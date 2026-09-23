#!/usr/bin/env python
"""Measure what a year of per-lake pixel images costs in bytes.

The dashboard serves one week of pixels per lake, encoded by build_lake_dashboard.py as a
coloured PNG and a grey code PNG in Web Mercator, both as base64 data URLs. This script encodes
the same images for the newest N weekly files and every lake, and sums the bytes as served.
It also measures two cheaper encodings: the grey code PNG alone, with the alpha mask sent once
per lake, and all weeks of the grey code PNG stacked into one PNG per lake.

Reads local files only. Contacts nothing. Writes datasets/cyan/outputs/pixel-history-<stamp>.json.

Usage:
  uv run python datasets/cyan/viz/estimate_pixel_history.py --weeks 52
"""

from __future__ import annotations

import argparse
import base64
import io
import json
import re
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from datasets._common import provenance  # noqa: E402
from datasets.cyan.access import cyan_api as c  # noqa: E402
from datasets.cyan.derive import build_lake_table as lt  # noqa: E402
from datasets.cyan.viz import build_lake_dashboard as b  # noqa: E402

OUTPUTS = REPO / "datasets" / "cyan" / "outputs"


def decode_png(url: str) -> np.ndarray:
    from PIL import Image

    raw = base64.b64decode(url.split(",", 1)[1])
    return np.asarray(Image.open(io.BytesIO(raw)))


def strip_url(frames: list[np.ndarray]) -> str:
    from PIL import Image

    return b.png_url(Image.fromarray(np.vstack(frames)))


def mask_url(interior: np.ndarray, touched: np.ndarray, window_transform) -> str:
    """The alpha mask alone, warped like the pixels, as one grey PNG per lake."""
    zeros = np.zeros(interior.shape, np.uint8)
    url, _, _ = b.pixel_overlay(zeros, interior, touched, window_transform)
    alpha = decode_png(url)[:, :, 3]
    from PIL import Image

    return b.png_url(Image.fromarray(alpha))


def quantiles(values: list[int]) -> dict:
    a = np.asarray(sorted(values))
    if a.size == 0:
        return {"median": 0, "p90": 0, "max": 0}
    return {
        "median": int(np.median(a)),
        "p90": int(a[min(a.size - 1, int(0.9 * a.size))]),
        "max": int(a.max()),
    }


def build(args) -> dict:
    import geopandas as gpd
    import rasterio
    from rasterio.windows import Window
    from rasterio.windows import transform as win_transform

    t0 = time.time()
    files = sorted(Path(args.raw).glob("*.tif"))[-args.weeks :]
    lakes = gpd.read_file(f"zip://{args.lakes}")
    lakes["COMID"] = lakes["COMID"].astype("int64")
    with rasterio.open(files[-1]) as ds:
        lakes5070 = lakes.to_crs(ds.crs)
        transform, width, height = ds.transform, ds.width, ds.height
    masks = lt.lake_masks(
        lakes5070,
        transform,
        width,
        height,
        lt.RECIPE["oversample"],
        lt.RECIPE["interior_min_coverage"],
    )
    comids = [int(x) for x in lakes["COMID"] if masks[int(x)]["window"]]
    if args.sample and args.sample < len(comids):
        rng = np.random.default_rng(args.seed)
        comids = sorted(int(x) for x in rng.choice(comids, args.sample, replace=False))
    per_lake = {k: {"as_built": 0, "codes": 0, "frames": []} for k in comids}
    mask_once, outline_once = {}, {}
    win_cells = 0
    for k in comids:
        col0, row0, ww, hh = masks[k]["window"]
        win_cells += ww * hh
    weekly = []
    for f in files:
        with rasterio.open(f) as ds:
            codes_all = ds.read(1)
        wk = {"file": f.name, "as_built": 0, "codes": 0}
        for k in comids:
            m = masks[k]
            col0, row0, ww, hh = m["window"]
            win = codes_all[row0 : row0 + hh, col0 : col0 + ww]
            interior = np.zeros(win.shape, bool)
            touched = np.zeros(win.shape, bool)
            ri, ci = np.divmod(m["interior"], width)
            rt, ct = np.divmod(m["touched"], width)
            interior[ri - row0, ci - col0] = True
            touched[rt - row0, ct - col0] = True
            wtr = win_transform(Window(col0, row0, ww, hh), transform)
            url, codes_url, _ = b.pixel_overlay(win, interior, touched, wtr)
            n_built, n_codes = len(url) + len(codes_url), len(codes_url)
            wk["as_built"] += n_built
            wk["codes"] += n_codes
            per_lake[k]["as_built"] += n_built
            per_lake[k]["codes"] += n_codes
            per_lake[k]["frames"].append(codes_url)
            if k not in mask_once:
                mask_once[k] = len(mask_url(interior, touched, wtr))
        weekly.append(wk)
    idx = {int(x): i for i, x in enumerate(lakes["COMID"])}
    wgs = lakes5070.geometry.to_crs(4326)
    for k in comids:
        geo = json.dumps(wgs.iloc[idx[k]].__geo_interface__, separators=(",", ":"))
        outline_once[k] = len(re.sub(r"(\d+\.\d{6})\d+", r"\1", geo))
        frames = [decode_png(u) for u in per_lake[k]["frames"]]
        per_lake[k]["strip"] = len(strip_url(frames))
        per_lake[k]["frames"] = None
    n = len(files)
    parsed = [c.parse_cyan_filename(f.name) for f in files]
    year = {
        "as_built": sum(v["as_built"] for v in per_lake.values()),
        "codes_only": sum(v["codes"] for v in per_lake.values()),
        "codes_strip": sum(v["strip"] for v in per_lake.values()),
        "mask_once": sum(mask_once.values()),
        "outline_once": sum(outline_once.values()),
    }
    newest = weekly[-1]
    largest = sorted(comids, key=lambda k: per_lake[k]["as_built"], reverse=True)[:5]
    summary = {
        "measured_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "recipe": (
            "for each weekly file and each lake, the coloured RGBA PNG and the grey code PNG "
            "exactly as build_lake_dashboard.py encodes them, counted as base64 data URLs. "
            "Outlines at the 6 decimals the page serves"
        ),
        "files": {"n": n, "first": parsed[0].start_date, "last": parsed[-1].start_date},
        "lakes": {
            "n": len(comids),
            "of": len(lakes),
            "sample": args.sample,
            "window_cells": win_cells,
        },
        "newest_week_bytes": {"as_built": newest["as_built"], "codes_only": newest["codes"]},
        "per_week_bytes": {
            "as_built": {
                "mean": int(np.mean([w["as_built"] for w in weekly])),
                "min": min(w["as_built"] for w in weekly),
                "max": max(w["as_built"] for w in weekly),
            },
            "codes_only": {
                "mean": int(np.mean([w["codes"] for w in weekly])),
                "min": min(w["codes"] for w in weekly),
                "max": max(w["codes"] for w in weekly),
            },
        },
        "year_bytes": year,
        "served_today_bytes": newest["as_built"] + year["outline_once"],
        "per_lake_bytes": {
            "one_week_as_built": quantiles([v["as_built"] // n for v in per_lake.values()]),
            "year_as_built": quantiles([v["as_built"] for v in per_lake.values()]),
            "year_codes_strip": quantiles([v["strip"] for v in per_lake.values()]),
            "outline": quantiles(list(outline_once.values())),
        },
        "largest": [
            {
                "comid": k,
                "year_as_built": per_lake[k]["as_built"],
                "year_codes_strip": per_lake[k]["strip"],
                "outline": outline_once[k],
            }
            for k in largest
        ],
        "weekly": weekly,
        "seconds": round(time.time() - t0, 1),
        "code": provenance.code_provenance([Path(__file__), Path(b.__file__), Path(lt.__file__)]),
    }
    stamp = summary["measured_at"][:16].replace(":", "") + "Z"
    out = Path(args.out) if args.out else OUTPUTS / f"pixel-history-{stamp}.json"
    out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    summary["output"] = provenance.rel(out)
    return summary


def parse_args(argv=None):
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--raw", default=str(b.WEEKLY_RAW))
    ap.add_argument("--lakes", default=str(b.LAKES_ZIP))
    ap.add_argument("--weeks", type=int, default=52, help="newest weekly files to encode")
    ap.add_argument("--sample", type=int, default=0, help="lakes to draw at random, 0 for all")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default=None)
    return ap.parse_args(argv)


def main(argv=None) -> int:
    s = build(parse_args(argv))
    y = s["year_bytes"]
    print(f"{s['files']['n']} files, {s['lakes']['n']} lakes, {s['seconds']} s -> {s['output']}")
    print(f"newest week as built {s['newest_week_bytes']['as_built']:,} B")
    print(f"year as built {y['as_built']:,} B, codes only {y['codes_only']:,} B")
    print(f"year codes strip {y['codes_strip']:,} B")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
