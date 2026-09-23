"""Offline tests for the per-lake table recipe on a synthetic mosaic. No network."""

from pathlib import Path

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.transform import from_origin
from shapely.geometry import box

from datasets.cyan.derive import build_lake_table as b


def test_lake_masks_interior_and_touched():
    transform = from_origin(0.0, 3000.0, 300.0, 300.0)  # 10 x 10 cells, 300 m
    exact = box(600, 600, 1500, 1500)  # covers cells cols 2..4, rows 5..7 exactly: 9 interior
    partial = box(650, 650, 1150, 1150)  # 500 m wide, straddles four cells, covers none fully
    tiny = box(100, 100, 150, 150)  # smaller than one cell
    lakes = gpd.GeoDataFrame({"COMID": [1, 2, 3]}, geometry=[exact, partial, tiny], crs="EPSG:5070")
    masks = b.lake_masks(lakes, transform, 10, 10, 8, 0.999)
    assert masks[1]["interior"].size == 9 and masks[1]["touched"].size == 9
    assert masks[2]["interior"].size == 0 and masks[2]["touched"].size == 4
    assert masks[3]["interior"].size == 0 and masks[3]["touched"].size == 1
    rows, cols = np.divmod(masks[1]["interior"], 10)
    assert set(rows.tolist()) == {5, 6, 7} and set(cols.tolist()) == {2, 3, 4}


def test_lake_stats_follow_the_recipe():
    vals = np.array([0, 0, 10, 130, 253, 254, 255, 255], dtype=np.uint8)
    s = b.lake_stats(vals)
    assert s["n_interior"] == 8 and s["n_land"] == 1 and s["n_nodata"] == 2
    assert s["n_valid"] == 5 and s["n_zero"] == 2 and s["n_detect"] == 3
    assert s["valid_frac"] == 5 / 8
    assert s["dn_median"] == 10.0  # zeros included, as the EPA recipe does
    assert s["dn_mean"] == (0 + 0 + 10 + 130 + 253) / 5
    assert s["dn_max"] == 253 and s["ci_max"] > 0
    empty = b.lake_stats(np.array([254, 255], dtype=np.uint8))
    assert empty["n_valid"] == 0 and empty["dn_median"] is None and empty["valid_frac"] == 0.0


def test_build_on_synthetic_mosaic(tmp_path, monkeypatch):
    raw = tmp_path / "raw"
    raw.mkdir()
    arr = np.full((10, 10), 254, np.uint8)
    arr[5:8, 2:5] = 0
    arr[6, 3] = 200
    name = "L20261882026194.L3m_7D_CYAN_CI_cyano_CYAN_CONUS_300m.tif"
    transform = from_origin(0.0, 3000.0, 300.0, 300.0)
    with rasterio.open(
        raw / name, "w", driver="GTiff", height=10, width=10, count=1, dtype="uint8",
        crs="EPSG:5070", transform=transform,
    ) as ds:  # fmt: skip
        ds.write(arr, 1)
        ds.update_tags(OBPG_version="6.0")
    lakes = gpd.GeoDataFrame(
        {"COMID": [11, 12], "GNIS_NAME": ["Square Lake", "Pond"], "AREASQKM": [0.81, 0.0025]},
        geometry=[box(600, 600, 1500, 1500), box(100, 100, 150, 150)],
        crs="EPSG:5070",
    )
    zip_path = tmp_path / "lakes.zip"
    lakes.to_file(tmp_path / "lakes.shp")
    import zipfile

    with zipfile.ZipFile(zip_path, "w") as z:
        for p in tmp_path.glob("lakes.*"):
            z.write(p, p.name)
    (raw / "manifest.jsonl").write_text("{}\n", encoding="utf-8")
    monkeypatch.setattr(b, "DERIVED", tmp_path / "derived")
    monkeypatch.setattr(b, "OUT", tmp_path / "out")
    summary = b.build(b.parse_args(["--raw", str(raw), "--lakes", str(zip_path)]))
    assert summary["lakes"]["with_interior_pixel"] == 1 and summary["lakes"][
        "without_interior_pixel"
    ] == [12]
    assert summary["rows"] == 1 and summary["weekly_lake_weeks_with_valid_pixel"] == 1
    import pandas as pd

    df = pd.read_parquet(tmp_path / "derived" / Path(summary["output"]).name)
    r = df.iloc[0]
    assert r["comid"] == 11 and r["n_interior"] == 9 and r["n_valid"] == 9 and r["n_zero"] == 8
    assert r["n_detect"] == 1 and r["dn_max"] == 200 and r["dn_median"] == 0.0
    assert r["gnis_name"] == "Square Lake" and abs(r["area_sqkm"] - 0.81) < 1e-9
    assert "sources" in summary["code"] and summary["recipe"]["id"] == "decision-0002-v1"
