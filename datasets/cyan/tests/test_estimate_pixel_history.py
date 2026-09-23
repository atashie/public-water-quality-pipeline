"""Offline test for the pixel history measurement on two synthetic weekly files. No network."""

import json
import zipfile

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.transform import from_origin
from shapely.geometry import box

from datasets.cyan.viz import estimate_pixel_history as e


def test_measures_two_weeks_on_one_lake(tmp_path):
    transform = from_origin(0.0, 3000.0, 300.0, 300.0)
    raw = tmp_path / "raw"
    raw.mkdir()
    for i, fill in enumerate([0, 200]):
        name = f"L2026{188 + 7 * i}2026{194 + 7 * i}.L3m_7D_CYAN_CI_cyano_CYAN_CONUS_300m.tif"
        with rasterio.open(
            raw / name, "w", driver="GTiff", height=10, width=10, count=1, dtype="uint8",
            crs="EPSG:5070", transform=transform,
        ) as ds:  # fmt: skip
            ds.write(np.full((10, 10), fill, np.uint8), 1)
    lakes = gpd.GeoDataFrame(
        {"COMID": [11], "GNIS_NAME": [None], "AREASQKM": [0.81]},
        geometry=[box(600, 600, 1500, 1500)],
        crs="EPSG:5070",
    )
    lakes.to_file(tmp_path / "lakes.shp")
    zip_path = tmp_path / "lakes.zip"
    with zipfile.ZipFile(zip_path, "w") as z:
        for p in tmp_path.glob("lakes.*"):
            z.write(p, p.name)
    out = tmp_path / "result.json"
    args = e.parse_args(
        ["--raw", str(raw), "--lakes", str(zip_path), "--weeks", "2", "--out", str(out)]
    )
    s = e.build(args)
    saved = json.loads(out.read_text())
    assert s["files"] == {"n": 2, "first": "2026-07-07", "last": "2026-07-14"}
    assert s["lakes"]["n"] == 1 and s["lakes"]["window_cells"] == 25
    y = s["year_bytes"]
    assert y["as_built"] == sum(w["as_built"] for w in s["weekly"]) > y["codes_only"] > 0
    assert 0 < y["codes_strip"] < y["codes_only"] + 200 and y["mask_once"] > 0
    assert y["outline_once"] == saved["year_bytes"]["outline_once"] > 20
    assert s["served_today_bytes"] == s["newest_week_bytes"]["as_built"] + y["outline_once"]
    assert s["per_lake_bytes"]["year_as_built"]["max"] == y["as_built"]
    assert s["largest"][0]["comid"] == 11
    assert out.name.endswith(".json") and s["output"].endswith("result.json")
