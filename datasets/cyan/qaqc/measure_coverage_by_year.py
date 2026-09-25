#!/usr/bin/env python
"""Measure how weekly lake coverage changes by year, for the single-satellite context.

From 2018 the CyAN files merge Sentinel-3A and 3B and keep the higher value per pixel. A second
satellite adds observations, so later years can have more weeks with a value. This counts, for
each calendar year of weekly files, the lake-weeks with at least one valid interior pixel and the
mean share of interior pixels that are valid. It does so over all months and over May to October,
which leaves out most ice and low sun.

The counts are measurements for the review record. The page shows no number made from them.
Weekly rows only. Every lake has a row in every weekly file, so each year pools the same lakes.
Reads the per-lake table of decision 0002. Contacts nothing.
Writes datasets/cyan/outputs/coverage-by-year-<stamp>.json.

Usage:
  uv run python datasets/cyan/qaqc/measure_coverage_by_year.py [--table <parquet>]
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
COLUMNS = ["comid", "temporal", "start_date", "n_interior", "n_valid"]
SEASON = (5, 10)


def newest_table() -> Path:
    tables = sorted(DERIVED.glob("cyan_lake_table-*.parquet"))
    if not tables:
        raise SystemExit("no per-lake table under data/cyan/derived. Run build_lake_table.py")
    return tables[-1]


def by_year(weekly) -> list[dict]:
    """Per calendar year of the file's start date: files, lake-weeks, and two coverage shares."""
    import pandas as pd

    w = weekly.assign(
        year=pd.to_datetime(weekly["start_date"]).dt.year,
        has_value=weekly["n_valid"] > 0,
        valid_share=weekly["n_valid"] / weekly["n_interior"],
    )
    g = w.groupby("year")
    out = g.agg(
        files=("start_date", "nunique"),
        lake_weeks=("comid", "size"),
        with_a_value=("has_value", "sum"),
        mean_valid_share=("valid_share", "mean"),
    ).reset_index()
    return [
        {
            "year": int(r.year),
            "files": int(r.files),
            "lake_weeks": int(r.lake_weeks),
            "with_a_value": int(r.with_a_value),
            "with_a_value_share": round(r.with_a_value / r.lake_weeks, 4),
            "mean_valid_share": round(float(r.mean_valid_share), 4),
        }
        for r in out.itertuples()
    ]


def in_season(weekly):
    import pandas as pd

    month = pd.to_datetime(weekly["start_date"]).dt.month
    return weekly[month.between(*SEASON)]


def build(args) -> dict:
    import pandas as pd

    started = net.utc_now_iso()
    stamp = started.replace(":", "")[:15] + "Z"
    table = Path(args.table) if args.table else newest_table()
    df = pd.read_parquet(table, columns=COLUMNS)
    weekly = df[(df["temporal"] == "7D") & (df["n_interior"] > 0)]
    summary = {
        "measured_at": started,
        "table": provenance.rel(table),
        "table_sha256": net.sha256_file(table),
        "rows": {"all": len(df), "weekly": len(weekly)},
        "season_months": list(SEASON),
        "all_months": by_year(weekly),
        "may_to_october": by_year(in_season(weekly)),
        "code": provenance.code_provenance([Path(__file__)], [table]),
    }
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    out = OUTPUTS / f"coverage-by-year-{stamp}.json"
    out.write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8")
    for r in summary["may_to_october"]:
        print(
            f"[coverage-by-year] {r['year']} May-Oct: {r['files']} files, "
            f"{r['with_a_value_share']:.3f} with a value, {r['mean_valid_share']:.3f} valid share"
        )
    print(f"[coverage-by-year] wrote {out.name}")
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
