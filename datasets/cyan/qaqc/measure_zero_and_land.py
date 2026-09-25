#!/usr/bin/env python
"""Measure how often weekly lake medians sit at code 0, and which lakes carry land-coded pixels.

Two questions from the scientist's feedback of 2026-09-25. Why does the pixel map look blue:
how many weekly lake rows with a value have a median of code 0, below detection, and how many
have every valid pixel at code 0. Why does Lake Henshaw never reach full coverage: which lakes
have interior pixels coded land, 254, in every weekly file, and how far that caps coverage.

The counts are measurements for the review record. The page shows no number made from them.
Weekly rows only. Reads the per-lake table of decision 0002. Contacts nothing.
Writes datasets/cyan/outputs/zero-and-land-<stamp>.json.

Usage:
  uv run python datasets/cyan/qaqc/measure_zero_and_land.py [--table <parquet>]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from datasets._common import net, provenance  # noqa: E402

DERIVED = REPO / "data" / "cyan" / "derived"
OUTPUTS = REPO / "datasets" / "cyan" / "outputs"
COLUMNS = [
    "comid", "temporal", "start_date", "gnis_name", "n_interior", "n_land", "n_nodata",
    "n_valid", "n_zero", "dn_median",
]  # fmt: skip


def newest_table() -> Path:
    tables = sorted(DERIVED.glob("cyan_lake_table-*.parquet"))
    if not tables:
        raise SystemExit("no per-lake table under data/cyan/derived. Run build_lake_table.py")
    return tables[-1]


def zero_shares(weekly) -> dict:
    """Counts of weekly rows with a value whose median is 0, or whose pixels are all 0."""
    valued = weekly[weekly["n_valid"] > 0]
    n = len(valued)
    median_zero = int((valued["dn_median"] == 0).sum())
    valid_all_zero = int((valued["n_zero"] == valued["n_valid"]).sum())
    interior_all_zero = int((valued["n_zero"] == valued["n_interior"]).sum())
    return {
        "weekly_rows": len(weekly),
        "rows_with_a_value": n,
        "median_zero": median_zero,
        "median_zero_share": round(median_zero / n, 4) if n else None,
        "every_valid_pixel_zero": valid_all_zero,
        "every_valid_pixel_zero_share": round(valid_all_zero / n, 4) if n else None,
        "every_interior_pixel_zero": interior_all_zero,
        "every_interior_pixel_zero_share": round(interior_all_zero / n, 4) if n else None,
    }


def land_ceilings(weekly):
    """Per lake: interior count, files, the smallest and largest land count, and the ceiling.

    The ceiling is the highest coverage the smallest land count allows. It is a measurement for
    the record, not a statistic the page serves.
    """
    g = weekly.groupby("comid")
    out = g.agg(
        gnis_name=("gnis_name", "first"),
        n_interior=("n_interior", "first"),
        n_files=("start_date", "size"),
        min_land=("n_land", "min"),
        max_land=("n_land", "max"),
        max_valid=("n_valid", "max"),
    ).reset_index()
    out["ceiling"] = 1 - out["min_land"] / out["n_interior"]
    return out.sort_values(["ceiling", "comid"]).reset_index(drop=True)


def summarize_land(ceilings) -> dict:
    land = ceilings[ceilings["min_land"] > 0]
    capped = land[land["ceiling"] < 0.9]
    return {
        "lakes": len(ceilings),
        "lakes_with_land_in_every_file": len(land),
        "lakes_with_a_constant_land_count": int((land["min_land"] == land["max_land"]).sum()),
        "ceiling_under_0_9": len(capped),
        "ceiling_under_0_5": int((land["ceiling"] < 0.5).sum()),
        "lakes_under_0_9": [
            {
                "comid": int(r.comid),
                "gnis_name": None if r.gnis_name != r.gnis_name else r.gnis_name,
                "n_interior": int(r.n_interior),
                "min_land": int(r.min_land),
                "max_land": int(r.max_land),
                "max_valid": int(r.max_valid),
                "ceiling": round(float(r.ceiling), 4),
            }
            for r in capped.itertuples()
        ],
    }


def build(args) -> dict:
    import pandas as pd

    started = net.utc_now_iso()
    stamp = started.replace(":", "")[:15] + "Z"
    table = Path(args.table) if args.table else newest_table()
    df = pd.read_parquet(table, columns=COLUMNS)
    weekly = df[df["temporal"] == "7D"]
    summary = {
        "measured_at": started,
        "table": provenance.rel(table),
        "table_sha256": net.sha256_file(table),
        "rows": {"all": len(df), "weekly": len(weekly), "dropped_daily": len(df) - len(weekly)},
        "zero": zero_shares(weekly),
        "land": summarize_land(land_ceilings(weekly)),
        "code": provenance.code_provenance([Path(__file__)], [table]),
    }
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    out = OUTPUTS / f"zero-and-land-{stamp}.json"
    out.write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8")
    z, land = summary["zero"], summary["land"]
    print(f"[zero-and-land] {z['rows_with_a_value']:,} weekly rows with a value")
    print(
        f"[zero-and-land] median 0: {z['median_zero']:,}, "
        f"all valid 0: {z['every_valid_pixel_zero']:,}"
    )
    print(
        f"[zero-and-land] {land['lakes_with_land_in_every_file']} lakes with land in every file, "
        f"{land['ceiling_under_0_9']} under 0.9, {land['ceiling_under_0_5']} under 0.5"
    )
    print(f"[zero-and-land] wrote {out.name}")
    return summary


def parse_args(argv=None):
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--table", default=None, help="per-lake table, default the newest")
    return ap.parse_args(argv)


def main(argv=None) -> int:
    build(parse_args(argv))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
