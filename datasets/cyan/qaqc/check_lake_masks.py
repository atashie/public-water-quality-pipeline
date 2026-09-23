#!/usr/bin/env python
"""Check the interior and touched pixel masks of decision 0002 against exact polygon geometry.

For a sample of lakes, every cell of the lake's pixel window gets its exact coverage fraction,
the area of the intersection between the cell square and the full-resolution polygon divided
by the cell area, computed with Shapely. The check compares that fraction with the classes the
8 by 8 oversampled rasterization assigned: interior when at least 99.9 percent, touched when
above zero. It also measures how far the simplified outlines drawn on earlier dashboards sit
from the exact outlines.

Reads local files only. Writes datasets/cyan/outputs/mask-check-<stamp>.json.

Usage:
  uv run python datasets/cyan/qaqc/check_lake_masks.py [--sample 60] [--seed 0]
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
from datasets.cyan.derive import build_lake_table as lt  # noqa: E402

LAKES_ZIP = REPO / "data" / "cyan_lakes" / "raw" / "MERIS_OLCI_Lakes.zip"
WEEKLY_RAW = REPO / "data" / "cyan" / "raw" / "weekly_conus_mosaic"
OUTPUTS = REPO / "datasets" / "cyan" / "outputs"
SIMPLIFY_M = 300.0


def exact_fractions(geom, window, transform) -> np.ndarray:
    """Exact coverage fraction of every cell in the window, shape (h, w)."""
    from shapely.geometry import box
    from shapely.prepared import prep

    col0, row0, w, h = window
    out = np.zeros((h, w), dtype=float)
    pixel_area = abs(transform.a * transform.e)
    prepared = prep(geom)
    for r in range(h):
        for c in range(w):
            x0, y0 = transform * (col0 + c, row0 + r)
            x1, y1 = transform * (col0 + c + 1, row0 + r + 1)
            cell = box(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))
            if prepared.contains(cell):
                out[r, c] = 1.0
            elif prepared.intersects(cell):
                out[r, c] = geom.intersection(cell).area / pixel_area
    return out


def check_lake(row, masks, transform, width) -> dict:
    m = masks[int(row.COMID)]
    col0, row0, w, h = m["window"]
    frac = exact_fractions(row.geometry, m["window"], transform)
    interior = np.zeros((h, w), bool)
    touched = np.zeros((h, w), bool)
    ri, ci = np.divmod(m["interior"], width)
    rt, ct = np.divmod(m["touched"], width)
    interior[ri - row0, ci - col0] = True
    touched[rt - row0, ct - col0] = True
    exact_interior = frac >= lt.RECIPE["interior_min_coverage"]
    exact_touched = frac > 0
    simplified = row.geometry.simplify(SIMPLIFY_M, preserve_topology=True)
    return {
        "comid": int(row.COMID),
        "name": None if row.GNIS_NAME is None or str(row.GNIS_NAME) == "nan" else row.GNIS_NAME,
        "area_sqkm": round(float(row.AREASQKM), 2),
        "window_cells": int(w * h),
        "n_interior": int(interior.sum()),
        "n_touched": int(touched.sum()),
        "interior_agree": int((interior == exact_interior).sum()),
        "interior_only_in_mask": int((interior & ~exact_interior).sum()),
        "interior_only_in_exact": int((~interior & exact_interior).sum()),
        "min_exact_fraction_of_mask_interior": round(float(frac[interior].min()), 4)
        if interior.any()
        else None,
        "touched_agree": int((touched == exact_touched).sum()),
        "touched_only_in_mask": int((touched & ~exact_touched).sum()),
        "touched_only_in_exact": int((~touched & exact_touched).sum()),
        "max_exact_fraction_outside_touched": round(float(frac[~touched].max()), 4)
        if (~touched).any()
        else None,
        "simplified_vertices": int(
            sum(len(g.exterior.coords) for g in getattr(simplified, "geoms", [simplified]))
        ),
        "exact_vertices": int(
            sum(len(g.exterior.coords) for g in getattr(row.geometry, "geoms", [row.geometry]))
        ),
        "hausdorff_simplified_m": round(float(row.geometry.hausdorff_distance(simplified)), 1),
    }


def build(args) -> dict:
    import geopandas as gpd
    import rasterio

    started = net.utc_now_iso()
    stamp = started.replace(":", "")[:15] + "Z"
    lakes = gpd.read_file(f"zip://{args.lakes}")
    lakes["COMID"] = lakes["COMID"].astype("int64")
    grid = sorted(Path(args.raw).glob("*.tif"))[0]
    with rasterio.open(grid) as ds:
        lakes = lakes.to_crs(ds.crs)
        transform, width, height = ds.transform, ds.width, ds.height
    rng = np.random.default_rng(args.seed)
    idx = list(rng.choice(len(lakes), size=min(args.sample, len(lakes)), replace=False))
    largest = list(lakes["AREASQKM"].nlargest(args.largest).index)
    chosen = lakes.loc[sorted(set(idx) | set(largest))]
    masks = lt.lake_masks(
        chosen, transform, width, height, lt.RECIPE["oversample"],
        lt.RECIPE["interior_min_coverage"],
    )  # fmt: skip
    results = [check_lake(r, masks, transform, width) for r in chosen.itertuples()]
    tot = {k: int(sum(r[k] for r in results)) for k in (
        "window_cells", "n_interior", "n_touched", "interior_agree", "interior_only_in_mask",
        "interior_only_in_exact", "touched_agree", "touched_only_in_mask",
        "touched_only_in_exact",
    )}  # fmt: skip
    summary = {
        "measured_at": started,
        "recipe": lt.RECIPE,
        "grid_file": grid.name,
        "sample": {"random": args.sample, "largest": args.largest, "seed": args.seed},
        "lakes_checked": len(results),
        "totals": tot,
        "interior_disagreement_share": round(
            (tot["interior_only_in_mask"] + tot["interior_only_in_exact"]) / tot["window_cells"], 6
        ),
        "touched_disagreement_share": round(
            (tot["touched_only_in_mask"] + tot["touched_only_in_exact"]) / tot["window_cells"], 6
        ),
        "min_exact_fraction_of_any_mask_interior_cell": min(
            r["min_exact_fraction_of_mask_interior"]
            for r in results
            if r["min_exact_fraction_of_mask_interior"] is not None
        ),
        "max_exact_fraction_of_any_cell_outside_touched": max(
            r["max_exact_fraction_outside_touched"]
            for r in results
            if r["max_exact_fraction_outside_touched"] is not None
        ),
        "simplified_outline_hausdorff_m": {
            "median": float(np.median([r["hausdorff_simplified_m"] for r in results])),
            "max": max(r["hausdorff_simplified_m"] for r in results),
        },
        "lakes": results,
        "code": provenance.code_provenance(
            [Path(__file__), Path(lt.__file__)], [Path(args.lakes), grid]
        ),
    }
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    out = OUTPUTS / f"mask-check-{stamp}.json"
    out.write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8")
    print(f"[mask-check] {len(results)} lakes, {tot['window_cells']:,} cells")
    print(
        f"[mask-check] interior disagreements {tot['interior_only_in_mask']} + "
        f"{tot['interior_only_in_exact']}, touched {tot['touched_only_in_mask']} + "
        f"{tot['touched_only_in_exact']}"
    )
    print(f"[mask-check] simplified outline Hausdorff {summary['simplified_outline_hausdorff_m']}")
    print(f"[mask-check] wrote {out.name}")
    return summary


def parse_args(argv=None):
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--lakes", default=str(LAKES_ZIP))
    ap.add_argument("--raw", default=str(WEEKLY_RAW))
    ap.add_argument("--sample", type=int, default=60)
    ap.add_argument("--largest", type=int, default=10)
    ap.add_argument("--seed", type=int, default=0)
    return ap.parse_args(argv)


def main(argv=None) -> int:
    build(parse_args(argv))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
