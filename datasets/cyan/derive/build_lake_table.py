#!/usr/bin/env python
"""Build the per-lake table from the pulled CyAN files under the recipe of decision 0002.

Reads local files only. Contacts nothing. The recipe:
  * Lake universe: the CyAN resolvable-lakes shapefile, keyed by COMID, assumption A9.
  * Interior pixels: native 300 m cells whose area lies at least 99.9 percent inside the lake
    polygon, from an 8 by 8 oversampled rasterization on the mosaic grid. Computed once.
  * Touched pixels: cells with any polygon coverage. Counted for reference, not used in stats.
  * Per lake and file: counts of interior pixels by code class, and statistics over the
    valid codes 0 to 253 with code 0 included as a measurement of zero, which is the recipe
    of the EPA forecast paper as replicated in the HAB_PoC repository. Land and no data are
    excluded. Nothing is aggregated in time.

Each file is read once in full and every lake is sliced from memory. Output is one Parquet
table, a provenance sidecar, and a summary under datasets/cyan/outputs/. Never edit them by
hand.

Usage:
  uv run python datasets/cyan/derive/build_lake_table.py \\
      --raw data/cyan/raw/weekly_conus_mosaic --raw data/cyan/raw/daily_conus_mosaic
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from datasets._common import net, provenance  # noqa: E402
from datasets.cyan.access import cyan_api as c  # noqa: E402

LAKES_ZIP = REPO / "data" / "cyan_lakes" / "raw" / "MERIS_OLCI_Lakes.zip"
DERIVED = REPO / "data" / "cyan" / "derived"
OUT = REPO / "datasets" / "cyan" / "outputs"
RECIPE = {
    "id": "decision-0002-v1",
    "oversample": 8,
    "interior_min_coverage": 0.999,
    "valid_codes": [c.DN_VALID_MIN - 1, c.DN_VALID_MAX],
    "statistics_over": "interior pixels with codes 0 to 253, code 0 included",
    "excluded_codes": [c.DN_LAND, c.DN_NODATA],
    "temporal_aggregation": "none",
}
COLUMNS = [
    "comid",
    "file",
    "temporal",
    "start_date",
    "end_date",
    "n_interior",
    "n_touched",
    "n_land",
    "n_nodata",
    "n_valid",
    "n_zero",
    "n_detect",
    "valid_frac",
    "dn_mean",
    "dn_median",
    "dn_sd",
    "dn_p90",
    "dn_max",
    "ci_max",
]


def lake_masks(lakes, transform, width: int, height: int, oversample: int, cover_min: float):
    """Flat pixel indices of interior and touched cells per lake, computed once from geometry.

    Returns {comid: {"interior": int64 array, "touched": int64 array, "window": [c, r, w, h]}}.
    A lake whose polygon covers no cell to the threshold has an empty interior array.
    """
    from rasterio.features import rasterize
    from rasterio.windows import Window, from_bounds
    from rasterio.windows import transform as win_transform

    masks = {}
    for row in lakes.itertuples():
        geom = row.geometry
        minx, miny, maxx, maxy = geom.bounds
        win = from_bounds(minx, miny, maxx, maxy, transform=transform)
        col0 = max(0, int(np.floor(win.col_off)) - 1)
        row0 = max(0, int(np.floor(win.row_off)) - 1)
        col1 = min(width, int(np.ceil(win.col_off + win.width)) + 1)
        row1 = min(height, int(np.ceil(win.row_off + win.height)) + 1)
        if col1 <= col0 or row1 <= row0:
            masks[int(row.COMID)] = {
                "interior": np.zeros(0, np.int64),
                "touched": np.zeros(0, np.int64),
                "window": None,
            }
            continue
        w, h = col1 - col0, row1 - row0
        wtr = win_transform(Window(col0, row0, w, h), transform)
        fine_tr = wtr * wtr.scale(1.0 / oversample, 1.0 / oversample)
        fine = rasterize(
            [(geom, 1)],
            out_shape=(h * oversample, w * oversample),
            transform=fine_tr,
            fill=0,
            dtype="uint8",
        )
        cover = fine.reshape(h, oversample, w, oversample).mean(axis=(1, 3))
        rows, cols = np.nonzero(cover >= cover_min)
        trows, tcols = np.nonzero(cover > 0)
        masks[int(row.COMID)] = {
            "interior": ((rows + row0).astype(np.int64) * width + (cols + col0)),
            "touched": ((trows + row0).astype(np.int64) * width + (tcols + col0)),
            "window": [col0, row0, w, h],
        }
    return masks


def lake_stats(vals: np.ndarray) -> dict:
    """Counts and statistics for one lake's interior codes under the recipe."""
    n = int(vals.size)
    n_land = int((vals == c.DN_LAND).sum())
    n_nodata = int((vals == c.DN_NODATA).sum())
    valid = vals[vals <= c.DN_VALID_MAX]
    n_valid = int(valid.size)
    n_zero = int((valid == 0).sum())
    rec = {
        "n_interior": n,
        "n_land": n_land,
        "n_nodata": n_nodata,
        "n_valid": n_valid,
        "n_zero": n_zero,
        "n_detect": n_valid - n_zero,
        "valid_frac": (n_valid / n) if n else None,
    }
    if n_valid:
        v = valid.astype(np.float64)
        dn_max = int(valid.max())
        rec.update(
            {
                "dn_mean": float(v.mean()),
                "dn_median": float(np.median(v)),
                "dn_sd": float(v.std(ddof=1)) if n_valid > 1 else None,
                "dn_p90": float(np.percentile(v, 90)),
                "dn_max": dn_max,
                "ci_max": float(c.dn_to_ci(np.array([dn_max]))[0]) if dn_max >= 1 else None,
            }
        )
    else:
        rec.update(
            {k: None for k in ("dn_mean", "dn_median", "dn_sd", "dn_p90", "dn_max", "ci_max")}
        )
    return rec


def select_files(raw_dirs: list[str]) -> list:
    files = []
    for raw in raw_dirs:
        raw_path = Path(raw) if Path(raw).is_absolute() else REPO / raw
        for t in sorted(raw_path.glob("*.tif")):
            f = c.parse_cyan_filename(t.name)
            if f and f.is_mosaic:
                files.append((t, f))
    files.sort(key=lambda x: (x[1].temporal, x[1].start_date))
    return files


def build(args) -> dict:
    import geopandas as gpd
    import pandas as pd
    import rasterio

    files = select_files(args.raw)
    if args.limit:
        files = files[: args.limit]
    lakes = gpd.read_file(f"zip://{args.lakes}")
    lakes["COMID"] = lakes["COMID"].astype("int64")
    with rasterio.open(files[0][0]) as ds:
        lakes = lakes.to_crs(ds.crs)
        transform, width, height = ds.transform, ds.width, ds.height
    print(f"[lake-table] {len(lakes)} lakes, {len(files)} files, recipe {RECIPE['id']}")
    masks = lake_masks(
        lakes, transform, width, height, RECIPE["oversample"], RECIPE["interior_min_coverage"]
    )
    n_int = {k: int(v["interior"].size) for k, v in masks.items()}
    no_interior = sorted(k for k, n in n_int.items() if n == 0)
    n_with = len(masks) - len(no_interior)
    print(f"[lake-table] lakes with an interior pixel: {n_with} of {len(masks)}")

    rows = []
    for i, (path, f) in enumerate(files, 1):
        with rasterio.open(path) as ds:
            flat = ds.read(1).ravel()
        for comid, m in masks.items():
            if m["interior"].size == 0:
                continue
            rec = lake_stats(flat[m["interior"]])
            rec.update(
                {
                    "comid": comid,
                    "file": f.filename,
                    "temporal": f.temporal,
                    "start_date": f.start_date,
                    "end_date": f.end_date,
                    "n_touched": int(m["touched"].size),
                }
            )
            rows.append(rec)
        if i % 25 == 0 or i == len(files):
            print(f"  [{i}/{len(files)}] {f.filename}")

    df = pd.DataFrame(rows, columns=COLUMNS)
    attrs = lakes.set_index("COMID")
    df["gnis_name"] = df["comid"].map(attrs["GNIS_NAME"]) if "GNIS_NAME" in attrs else None
    df["area_sqkm"] = df["comid"].map(attrs["AREASQKM"]) if "AREASQKM" in attrs else None
    started = net.utc_now_iso()
    stamp = started.replace(":", "")[:15] + "Z"
    DERIVED.mkdir(parents=True, exist_ok=True)
    out_parquet = DERIVED / f"cyan_lake_table-{stamp}.parquet"
    df.to_parquet(out_parquet, index=False)
    interior_sizes = np.array([n for n in n_int.values() if n > 0])
    weekly = df[df["temporal"] == "7D"]
    summary = {
        "measured_at": started,
        "stamp": stamp,
        "recipe": RECIPE,
        "lakes": {
            "in_file": int(len(lakes)),
            "with_interior_pixel": int(len(lakes) - len(no_interior)),
            "without_interior_pixel": no_interior,
            "interior_pixels": {
                "min": int(interior_sizes.min()),
                "median": float(np.median(interior_sizes)),
                "p90": float(np.percentile(interior_sizes, 90)),
                "max": int(interior_sizes.max()),
                "sum": int(interior_sizes.sum()),
            },
        },
        "files": len(files),
        "rows": int(len(df)),
        "weekly_rows": int(len(weekly)),
        "weekly_lake_weeks_with_valid_pixel": int((weekly["n_valid"] > 0).sum()),
        "weekly_lake_weeks_valid_frac_at_least_half": int((weekly["valid_frac"] >= 0.5).sum()),
        "weekly_lake_weeks_median_at_least_130": int((weekly["dn_median"] >= 130).sum()),
        "output": provenance.rel(out_parquet),
        "output_sha256": net.sha256_file(out_parquet),
        "output_bytes": out_parquet.stat().st_size,
        "code": provenance.code_provenance(
            [Path(__file__), Path(c.__file__)],
            [Path(args.lakes)]
            + [
                (REPO / r if not Path(r).is_absolute() else Path(r)) / "manifest.jsonl"
                for r in args.raw
            ],
        ),
    }
    (DERIVED / f"cyan_lake_table-{stamp}.provenance.json").write_text(
        json.dumps(summary, indent=1), encoding="utf-8"
    )
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"lake-table-{stamp}.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    print(f"[lake-table] {len(df):,} rows for {df['comid'].nunique()} lakes -> {out_parquet.name}")
    return summary


def parse_args(argv=None):
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--raw", action="append", required=True)
    ap.add_argument("--lakes", default=str(LAKES_ZIP))
    ap.add_argument("--limit", type=int, default=0, help="first N files, for a trial")
    return ap.parse_args(argv)


def main(argv=None) -> int:
    build(parse_args(argv))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
