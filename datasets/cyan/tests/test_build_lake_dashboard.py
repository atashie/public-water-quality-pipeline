"""Offline tests for the lake dashboard builder. No network."""

import json
import zipfile

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.transform import from_origin
from shapely.geometry import box

from datasets.cyan.viz import build_lake_dashboard as b


def test_run_length_and_weeks_since():
    assert b.run_length_at_end(np.array([True, False, True, True])) == 2
    assert b.run_length_at_end(np.array([False, False])) == 0
    assert b.run_length_at_end(np.array([True] * 5)) == 5
    assert b.weeks_since_last(np.array([True, False, False])) == 2
    assert b.weeks_since_last(np.array([False, True])) == 0
    assert b.weeks_since_last(np.array([False, False])) is None


def weekly_frame(medians, n_valid=None):
    n = len(medians)
    n_valid = n_valid if n_valid is not None else [10] * n
    starts = [f"2026-0{1 + i // 4}-{1 + 7 * (i % 4):02d}" for i in range(n)]
    return pd.DataFrame(
        {
            "comid": [7] * n,
            "temporal": ["7D"] * n,
            "start_date": starts,
            "end_date": starts,
            "n_interior": [10] * n,
            "n_valid": n_valid,
            "n_nodata": [10 - v for v in n_valid],
            "n_land": [0] * n,
            "n_detect": [5 if v else 0 for v in n_valid],
            "valid_frac": [v / 10 for v in n_valid],
            "dn_median": [np.nan if v == 0 else m for m, v in zip(medians, n_valid, strict=True)],
            "dn_p90": medians,
            "dn_max": medians,
        }
    )


def test_lake_state_classes_and_runs():
    w = weekly_frame([0, 140, 150, 131], [10, 10, 10, 10])
    s = b.lake_state(w, 130)
    assert s["class"] == "above" and s["run_above"] == 3 and s["run_seen"] == 4
    assert s["above_weeks_52"] == 3 and s["peak_median"] == 150.0 and s["weeks_since_seen"] == 0
    w = weekly_frame([140, 140, 0, 0], [10, 10, 10, 0])
    s = b.lake_state(w, 130)
    assert s["class"] == "no_data" and s["run_above"] == 0 and s["weeks_since_seen"] == 1
    assert s["median"] is None and s["seen_share_52"] == 0.75
    w = weekly_frame([140, 20, 20, 20])
    s = b.lake_state(w, 130)
    assert s["class"] == "detecting" and s["run_above"] == 0
    w = weekly_frame([140, 0, 0, 0])
    w["n_detect"] = 0
    assert b.lake_state(w, 130)["class"] == "below"


def test_recent_window_aligns_on_shared_weeks():
    w = weekly_frame([100, 200, 50], [10, 0, 10])
    out = b.recent_window(w, ["2025-12-28"] + w["start_date"].tolist())
    assert out["m"] == [None, 100.0, None, 50.0]
    assert out["v"] == [0.0, 1.0, 0.0, 1.0]


def test_lake_series_keeps_gaps_as_null():
    w = weekly_frame([100, 200], [10, 0])
    out = b.lake_series(w)
    assert out["7D"]["median"] == [100.0, None] and out["7D"]["detect_frac"] == [0.5, None]
    assert out["7D"]["n_land"] == [0, 0] and out["7D"]["n_nodata"] == [0, 10]
    assert "DAY" not in out


def test_build_on_synthetic_table(tmp_path, monkeypatch):
    name = "L20261882026194.L3m_7D_CYAN_CI_cyano_CYAN_CONUS_300m.tif"
    transform = from_origin(0.0, 3000.0, 300.0, 300.0)
    with rasterio.open(
        tmp_path / name, "w", driver="GTiff", height=10, width=10, count=1, dtype="uint8",
        crs="EPSG:5070", transform=transform,
    ) as ds:  # fmt: skip
        ds.write(np.zeros((10, 10), np.uint8), 1)
    lakes = gpd.GeoDataFrame(
        {"COMID": [11, 12], "GNIS_NAME": [None, None], "AREASQKM": [0.81, 0.36]},
        geometry=[box(600, 600, 1500, 1500), box(1800, 1800, 2400, 2400)],
        crs="EPSG:5070",
    )
    lakes.to_file(tmp_path / "lakes.shp")
    zip_path = tmp_path / "lakes.zip"
    with zipfile.ZipFile(zip_path, "w") as z:
        for p in tmp_path.glob("lakes.*"):
            z.write(p, p.name)
    rows = []
    for i, (med, nv) in enumerate([(10, 9), (140, 9), (150, 9)]):
        rows.append(
            {
                "comid": 11,
                "file": name,
                "temporal": "7D",
                "start_date": f"2026-07-{5 + 7 * i:02d}",
                "end_date": f"2026-07-{11 + 7 * i:02d}",
                "n_interior": 9,
                "n_touched": 16,
                "n_land": 0,
                "n_nodata": 9 - nv,
                "n_valid": nv,
                "n_zero": 0,
                "n_detect": nv,
                "valid_frac": nv / 9,
                "dn_mean": float(med),
                "dn_median": float(med),
                "dn_sd": 0.0,
                "dn_p90": float(med),
                "dn_max": float(med),
                "ci_max": 1.0,
                "gnis_name": "Square Lake",
                "area_sqkm": 0.81,
            }  # fmt: skip
        )
    rows.append(
        {**rows[0], "temporal": "DAY", "start_date": "2026-07-19", "end_date": "2026-07-19"}
    )
    table = tmp_path / "cyan_lake_table-2026-07-20T0000Z.parquet"
    pd.DataFrame(rows).to_parquet(table, index=False)
    derived = tmp_path / "derived"
    derived.mkdir()
    monkeypatch.setattr(b, "DERIVED", derived)
    monkeypatch.setattr(b.lt, "REPO", tmp_path)
    monkeypatch.setattr(b, "REPO", tmp_path)
    (tmp_path / "datasets" / "cyan" / "outputs").mkdir(parents=True)
    out = tmp_path / "out"
    names = tmp_path / "lake-names-2026-07-20T0000Z.csv"
    names.write_text(
        "comid,name,name_source,alternatives\n11,Square Lake,gnis_inside,Round Pond\n12,,none,\n"
    )
    args = b.parse_args(
        ["--table", str(table), "--lakes", str(zip_path), "--names", str(names)]
        + ["--grid-file", str(tmp_path / name), "--out", str(out)]
        + ["--newest-file", str(tmp_path / name)]
    )
    summary = b.build(args)
    assert summary["n_lakes"] == 1 and summary["newest_week"] == "2026-07-19"
    assert summary["classes_newest_week"] == {"above": 1}
    text = (out / "data" / "lakes.js").read_text(encoding="utf-8")
    payload = json.loads(text[len("window.CYAN_LAKES = ") : -2])
    lake = payload["lakes"][0]
    assert lake["c"] == 11 and lake["n"] == "Square Lake" and lake["ni"] == 9 and lake["nt"] == 9
    assert lake["ns"] == "gnis_inside" and summary["name_sources"] == {"gnis_inside": 1}
    assert lake["na"] == "Round Pond"
    assert lake["m"] == [10.0, 140.0, 150.0] and lake["s"]["run_above"] == 2
    assert 0 < lake["y"] < 90 and -180 < lake["x"] < 0
    assert lake["st"] is not None and len(lake["st"]) == 2
    pixels = (out / "data" / "pixels" / "11.js").read_text(encoding="utf-8")
    assert pixels.startswith("CYAN_PIXELS(11, ") and pixels.count("data:image/png;base64,") == 2
    assert '"codes":' in pixels
    assert summary["pixels"]["n_files"] == 1 and summary["pixels"]["start"] == "2026-07-07"
    series = (out / "data" / "lakes" / "11.js").read_text(encoding="utf-8")
    assert series.startswith("CYAN_LAKE(11, ") and '"DAY"' in series
    assert '"n_land":[0,0,0]' in series and '"n_nodata":[0,0,0]' in series
    assert not (out / "data" / "outlines.js").exists()
    assert '"outline":{"type":"Polygon"' in pixels
    attrs = pd.read_parquet(derived / summary["attributes"].split("/")[-1])
    assert list(attrs["comid"]) == [11] and attrs.iloc[0]["n_interior"] == 9
    assert len(attrs.iloc[0]["interior_cells"]) == 9 and attrs.iloc[0]["window_width"] > 0
    assert "sources" in summary["code"] and summary["threshold"] == 130
