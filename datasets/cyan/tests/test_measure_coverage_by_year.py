"""Offline tests for the coverage-by-year measurement. No network."""

import json

import pandas as pd
import pytest

from datasets.cyan.qaqc import measure_coverage_by_year as c


def frame():
    rows = [
        # 2017: one lake of 4 pixels, a July week with 2 valid and a January week with none.
        (1, "7D", "2017-07-02", 4, 2),
        (1, "7D", "2017-01-01", 4, 0),
        # 2019: the same lake, a July week fully valid and a December week with 1 valid.
        (1, "7D", "2019-07-07", 4, 4),
        (1, "7D", "2019-12-01", 4, 1),
        # A daily row and a lake without interior pixels are left out.
        (1, "DAY", "2019-07-08", 4, 4),
        (2, "7D", "2019-07-07", 0, 0),
    ]
    return pd.DataFrame(rows, columns=c.COLUMNS)


def weekly():
    df = frame()
    return df[(df["temporal"] == "7D") & (df["n_interior"] > 0)]


def test_by_year_counts_weeks_with_a_value_and_the_valid_share():
    rows = {r["year"]: r for r in c.by_year(weekly())}
    assert rows[2017] == {
        "year": 2017,
        "files": 2,
        "lake_weeks": 2,
        "with_a_value": 1,
        "with_a_value_share": 0.5,
        "mean_valid_share": 0.25,
    }
    assert rows[2019]["with_a_value"] == 2 and rows[2019]["mean_valid_share"] == 0.625


def test_in_season_keeps_may_to_october():
    kept = c.in_season(weekly())
    assert sorted(kept["start_date"]) == ["2017-07-02", "2019-07-07"]


def test_build_writes_a_stamped_result(tmp_path, monkeypatch):
    table = tmp_path / "cyan_lake_table-2026-07-20T0000Z.parquet"
    frame().to_parquet(table, index=False)
    monkeypatch.setattr(c, "OUTPUTS", tmp_path / "outputs")
    summary = c.build(c.parse_args(["--table", str(table)]))
    assert summary["rows"] == {"all": 6, "weekly": 4}
    written = list((tmp_path / "outputs").glob("coverage-by-year-*.json"))
    assert len(written) == 1
    season = json.loads(written[0].read_text())["may_to_october"]
    assert [r["with_a_value_share"] for r in season] == [1.0, 1.0]


def test_a_rerun_in_the_same_minute_does_not_overwrite(tmp_path, monkeypatch):
    table = tmp_path / "cyan_lake_table-2026-07-20T0000Z.parquet"
    frame().to_parquet(table, index=False)
    monkeypatch.setattr(c, "OUTPUTS", tmp_path / "outputs")
    monkeypatch.setattr(c.net, "utc_now_iso", lambda: "2026-09-25T17:01:30Z")
    c.build(c.parse_args(["--table", str(table)]))
    first = next((tmp_path / "outputs").glob("coverage-by-year-*.json")).read_bytes()
    with pytest.raises(FileExistsError):
        c.build(c.parse_args(["--table", str(table)]))
    assert next((tmp_path / "outputs").glob("coverage-by-year-*.json")).read_bytes() == first
