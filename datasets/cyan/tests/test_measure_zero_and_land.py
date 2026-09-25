"""Offline tests for the zero-median and land-code measurement. No network."""

import json

import numpy as np
import pandas as pd

from datasets.cyan.qaqc import measure_zero_and_land as z


def frame():
    rows = []
    # Lake 1: 10 interior pixels, 3 always land, so coverage can reach 0.7 at most.
    for i, (valid, zero, med) in enumerate([(7, 7, 0.0), (5, 2, 40.0), (0, 0, np.nan)]):
        rows.append((1, "7D", f"2026-07-0{1 + i}", "Pond", 10, 3, 7 - valid, valid, zero, med))
    # Lake 2: land in one file only, so no ceiling.
    for i, land in enumerate([0, 1]):
        rows.append((2, "7D", f"2026-07-0{1 + i}", None, 4, land, 0, 4 - land, 4 - land, 0.0))
    rows.append((2, "DAY", "2026-07-01", None, 4, 0, 0, 4, 4, 0.0))
    return pd.DataFrame(rows, columns=z.COLUMNS)


def test_zero_shares_count_rows_with_a_value_only():
    weekly = frame()[lambda d: d["temporal"] == "7D"]
    s = z.zero_shares(weekly)
    assert s["weekly_rows"] == 5 and s["rows_with_a_value"] == 4
    assert s["median_zero"] == 3 and s["median_zero_share"] == 0.75
    assert s["every_valid_pixel_zero"] == 3
    # Only lake 2's first week has every interior pixel valid and zero.
    assert s["every_interior_pixel_zero"] == 1


def test_land_ceilings_use_the_smallest_land_count():
    weekly = frame()[lambda d: d["temporal"] == "7D"]
    c = z.land_ceilings(weekly)
    one = c[c["comid"] == 1].iloc[0]
    assert one["min_land"] == 3 and one["max_land"] == 3 and one["n_files"] == 3
    assert abs(one["ceiling"] - 0.7) < 1e-9 and one["max_valid"] == 7
    two = c[c["comid"] == 2].iloc[0]
    assert two["min_land"] == 0 and two["ceiling"] == 1.0
    s = z.summarize_land(c)
    assert s["lakes"] == 2 and s["lakes_with_land_in_every_file"] == 1
    assert s["lakes_with_a_constant_land_count"] == 1
    assert s["ceiling_under_0_9"] == 1 and s["ceiling_under_0_5"] == 0
    assert s["lakes_under_0_9"][0]["comid"] == 1 and s["lakes_under_0_9"][0]["gnis_name"] == "Pond"


def test_build_writes_a_stamped_result(tmp_path, monkeypatch):
    table = tmp_path / "cyan_lake_table-2026-07-20T0000Z.parquet"
    frame().to_parquet(table, index=False)
    monkeypatch.setattr(z, "OUTPUTS", tmp_path / "outputs")
    summary = z.build(z.parse_args(["--table", str(table)]))
    assert summary["rows"] == {"all": 6, "weekly": 5, "dropped_daily": 1}
    written = list((tmp_path / "outputs").glob("zero-and-land-*.json"))
    assert len(written) == 1
    assert json.loads(written[0].read_text())["land"]["ceiling_under_0_9"] == 1
