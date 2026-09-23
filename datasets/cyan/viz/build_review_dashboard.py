#!/usr/bin/env python
"""Build the CyAN review dashboard: native-resolution frames per region and the page summary.

Reads local files only. Contacts nothing. For every region in regions.json and every pulled
whole-region file, it reads one window of the mosaic at native 300 m, reprojects it to
EPSG:4326 with nearest neighbor so every pixel keeps its code, and writes the frame as a
PNG inside a small JavaScript file. The page loads frames with script tags, which works
from a file:// URL where image pixel reads do not. Alpha marks pixels outside the source
window. Nothing is aggregated: the counts per frame come from the source window.

The summary JavaScript carries the regions, the frame index with per-window class counts,
the national record from the QA results, the manifest statistics, and provenance.

Outputs under docs/dashboards/cyan/: data/summary.js, data/basemap_states.js, and
data/frames/<region>/<date>_<temporal>.js. Frames are ignored by git and rebuilt here.

Usage:
  uv run python datasets/cyan/viz/build_review_dashboard.py \\
      --raw data/cyan/raw/weekly_conus_mosaic --raw data/cyan/raw/daily_conus_mosaic \\
      --qa datasets/cyan/outputs/qa-weekly_conus_mosaic-<stamp>.json \\
      --qa datasets/cyan/outputs/qa-daily_conus_mosaic-<stamp>.json
"""

from __future__ import annotations

import argparse
import base64
import io
import json
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from datasets._common import net, provenance  # noqa: E402
from datasets.cyan.access import cyan_api as c  # noqa: E402

DEFAULT_OUT = REPO / "docs" / "dashboards" / "cyan"
DEFAULT_REGIONS = Path(__file__).resolve().parent / "regions.json"
DEFAULT_BASEMAP = DEFAULT_OUT / "data" / "basemap_states.geojson"
RECORD_KEYS = (
    "collection_flags",
    "notes",
    "version_tags",
    "grid_consistent",
    "collection_consistent",
)


def snap_window(transform, width: int, height: int, lon: float, lat: float, size: int) -> dict:
    """The square pixel window of ``size`` centered on a point, clamped to the mosaic."""
    from pyproj import Transformer

    x, y = Transformer.from_crs("EPSG:4326", "EPSG:5070", always_xy=True).transform(lon, lat)
    col, row = ~transform * (x, y)
    col0 = min(max(int(col) - size // 2, 0), max(width - size, 0))
    row0 = min(max(int(row) - size // 2, 0), max(height - size, 0))
    return {"col": col0, "row": row0, "width": min(size, width), "height": min(size, height)}


def class_counts(arr: np.ndarray) -> dict:
    counts = np.bincount(arr.ravel(), minlength=256)
    valid = counts[c.DN_VALID_MIN : c.DN_VALID_MAX + 1]
    dn_max = int(np.nonzero(valid)[0].max() + c.DN_VALID_MIN) if valid.any() else None
    return {
        "below_detection": int(counts[c.DN_BELOW_DETECTION]),
        "valid": int(valid.sum()),
        "land": int(counts[c.DN_LAND]),
        "nodata": int(counts[c.DN_NODATA]),
        "dn_max": dn_max,
    }


def reproject_window(arr: np.ndarray, window_transform):
    """Nearest-neighbor reprojection of a code array to EPSG:4326.

    Returns the code array, an alpha array that is 255 inside the source window and 0
    outside, the destination transform, and the lat/lon bounds.
    """
    from rasterio.transform import array_bounds
    from rasterio.warp import Resampling, calculate_default_transform, reproject

    h, w = arr.shape
    bounds = array_bounds(h, w, window_transform)
    dst_transform, dw, dh = calculate_default_transform("EPSG:5070", "EPSG:4326", w, h, *bounds)
    # No destination nodata value. GDAL nudges a valid output pixel that equals the
    # destination nodata by one, which turned code 0 into code 1 in the first build of
    # 2026-09-23. Coverage comes from the alpha band instead.
    dst = np.zeros((dh, dw), dtype=np.uint8)
    alpha = np.zeros((dh, dw), dtype=np.uint8)
    kwargs = {
        "src_transform": window_transform,
        "src_crs": "EPSG:5070",
        "dst_transform": dst_transform,
        "dst_crs": "EPSG:4326",
        "resampling": Resampling.nearest,
        "src_nodata": None,
        "dst_nodata": None,
        "init_dest_nodata": False,
    }
    reproject(arr, dst, **kwargs)
    reproject(np.full(arr.shape, 255, np.uint8), alpha, **kwargs)
    west, south, east, north = array_bounds(dh, dw, dst_transform)
    return dst, alpha, dst_transform, {"west": west, "south": south, "east": east, "north": north}


def png_data_url(gray: np.ndarray, alpha: np.ndarray) -> str:
    from PIL import Image

    img = Image.fromarray(np.dstack([gray, alpha]), mode="LA")
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def frame_js(region_id: str, key: str, data_url: str) -> str:
    return f"CYAN_FRAME({json.dumps(region_id)}, {json.dumps(key)}, {json.dumps(data_url)});\n"


def national_record(qa_path: Path) -> dict:
    """The per-file record the page charts, extracted from a QA result."""
    s = json.loads(qa_path.read_text(encoding="utf-8"))
    rows = []
    for r in s["per_file"]:
        p = r.get("parsed") or {}
        pct = r.get("class_pct") or {}
        counts = r.get("class_counts") or {}
        rows.append(
            {
                "file": r["filename"],
                "total": r.get("total_pixels"),
                "counts": [counts.get(k) for k in ("valid", "below_detection", "land", "nodata")],
                "start": p.get("start_date"),
                "end": p.get("end_date"),
                "temporal": p.get("temporal"),
                "stream": p.get("stream"),
                "pct": [pct.get(k) for k in ("valid", "below_detection", "land", "nodata")],
                "dn_max": (r.get("dn_valid") or {}).get("max"),
                "version": r.get("processing_version_tag"),
                "flags": r.get("flags", []),
            }
        )
    return {
        "raw_dir": s["raw_dir"],
        "qa_file": qa_path.name,
        "measured_at": s.get("measured_at"),
        "fatal": s.get("fatal"),
        "n_files": s["n_files"],
        "collection": {k: s["collection"].get(k) for k in RECORD_KEYS},
        "completeness": dict(s["completeness"]),
        "manifest": s.get("manifest"),
        "code": s.get("code"),
        "rows": rows,
    }


def select_files(raw_dirs: list[str], frames: str) -> list:
    files = []
    for raw in raw_dirs:
        raw_path = Path(raw) if Path(raw).is_absolute() else REPO / raw
        for t in sorted(raw_path.glob("*.tif")):
            f = c.parse_cyan_filename(t.name)
            if f and f.is_mosaic:
                files.append((t, f))
    files.sort(key=lambda x: (x[1].temporal, x[1].start_date))
    if frames.startswith("last:"):
        n = int(frames.split(":")[1])
        by_t: dict[str, list] = {}
        for item in files:
            by_t.setdefault(item[1].temporal, []).append(item)
        files = [item for lst in by_t.values() for item in lst[-n:]]
    return files


def build(args) -> dict:
    import rasterio
    from rasterio.windows import Window
    from rasterio.windows import transform as win_transform

    out = Path(args.out)
    (out / "data" / "frames").mkdir(parents=True, exist_ok=True)
    cfg = json.loads(Path(args.regions).read_text(encoding="utf-8"))
    size = args.size or cfg.get("default_size_px", 2000)
    files = select_files(args.raw, args.frames)
    print(f"[build] {len(files)} files, {len(cfg['regions'])} regions, window {size} px")

    regions, windows = [], {}
    with rasterio.open(files[0][0]) as ds:
        base_transform, width, height = ds.transform, ds.width, ds.height
    for reg in cfg["regions"]:
        win = snap_window(base_transform, width, height, reg["lon"], reg["lat"], size)
        window = Window(win["col"], win["row"], win["width"], win["height"])
        wt = win_transform(window, base_transform)
        probe = np.zeros((win["height"], win["width"]), np.uint8)
        _, _, _, geo = reproject_window(probe, wt)
        windows[reg["id"]] = (window, wt)
        regions.append({**reg, "window": win, "bounds": geo, "frames": []})
        (out / "data" / "frames" / reg["id"]).mkdir(parents=True, exist_ok=True)

    for i, (path, f) in enumerate(files, 1):
        key = f"{f.start_date}_{f.temporal}"
        with rasterio.open(path) as ds:
            for reg in regions:
                window, wt = windows[reg["id"]]
                arr = ds.read(1, window=window)
                dst, alpha, _, _ = reproject_window(arr, wt)
                js_path = out / "data" / "frames" / reg["id"] / f"{key}.js"
                if not js_path.exists() or args.overwrite:
                    js_path.write_text(frame_js(reg["id"], key, png_data_url(dst, alpha)))
                reg["frames"].append(
                    {
                        "key": key,
                        "file": f.filename,
                        "start": f.start_date,
                        "end": f.end_date,
                        "temporal": f.temporal,
                        "counts": class_counts(arr),
                        "pixels": int(arr.size),
                        "shape": [int(dst.shape[1]), int(dst.shape[0])],
                    }
                )
        if i % 25 == 0:
            print(f"  [{i}/{len(files)}] {f.filename}")

    qa_paths = [Path(q) if Path(q).is_absolute() else REPO / q for q in args.qa]
    summary = {
        "built_at": net.utc_now_iso(),
        "window_px": size,
        "pixel_m": 300,
        "n_files": len(files),
        "regions": regions,
        "record": [national_record(q) for q in qa_paths],
        "code": provenance.code_provenance(
            [Path(__file__), Path(c.__file__), Path(args.regions)], qa_paths
        ),
        "encoding": {
            "below_detection": c.DN_BELOW_DETECTION,
            "valid": [c.DN_VALID_MIN, c.DN_VALID_MAX],
            "land": c.DN_LAND,
            "nodata": c.DN_NODATA,
            "ci_slope": c.CI_SLOPE,
            "ci_intercept": c.CI_INTERCEPT,
        },
    }
    (out / "data" / "summary.js").write_text(
        "window.CYAN_REVIEW = " + json.dumps(summary, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    basemap = Path(args.basemap)
    if basemap.is_file():
        (out / "data" / "basemap_states.js").write_text(
            "window.CYAN_STATES = " + basemap.read_text(encoding="utf-8").strip() + ";\n",
            encoding="utf-8",
        )
    n_frames = sum(len(r["frames"]) for r in regions)
    print(f"[build] wrote data/summary.js and {n_frames} frame entries under {out}")
    return summary


def parse_args(argv=None):
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--raw", action="append", required=True)
    ap.add_argument("--qa", action="append", default=[], help="QA result JSON for the record tab")
    ap.add_argument("--regions", default=str(DEFAULT_REGIONS))
    ap.add_argument("--basemap", default=str(DEFAULT_BASEMAP))
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--size", type=int, default=None, help="window size in pixels")
    ap.add_argument("--frames", default="all", help="'all' or 'last:N' per cadence")
    ap.add_argument("--overwrite", action="store_true", help="rewrite frames that exist")
    return ap.parse_args(argv)


def main(argv=None) -> int:
    build(parse_args(argv))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
