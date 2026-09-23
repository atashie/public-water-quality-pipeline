"""Offline tests for the GNIS name crosswalk on synthetic polygons and points. No network."""

import geopandas as gpd
from shapely.geometry import Point, box

from datasets.cyan_lakes.derive import build_name_crosswalk as x


def test_natural_folds_style_and_case():
    assert x.natural("Okeechobee, Lake") == "lake okeechobee"
    assert x.natural("Lake Okeechobee") == "lake okeechobee"
    assert x.natural("Utah Lake") == "utah lake"
    assert x.natural("Lake of the Woods") == "lake of the woods"


def gnis(rows):
    return gpd.GeoDataFrame(
        {
            "feature_id": [str(r[0]) for r in rows],
            "feature_name": [r[1] for r in rows],
            "feature_class": [r[2] for r in rows],
            "state_name": ["Nowhere"] * len(rows),
        },
        geometry=[Point(r[3], r[4]) for r in rows],
        crs="EPSG:5070",
    )


def test_crosswalk_rules():
    lakes = gpd.GeoDataFrame(
        {
            "COMID": [1, 2, 3, 4],
            "GNIS_NAME": ["Named Lake", None, None, None],
            "AREASQKM": [1.0, 1.0, 1.0, 1.0],
        },
        geometry=[
            box(0, 0, 1000, 1000),
            box(2000, 0, 3000, 1000),
            box(4000, 0, 5000, 1000),
            box(6000, 0, 7000, 1000),
        ],
        crs="EPSG:5070",
    )
    points = gnis(
        [
            (10, "Lake Named", "Lake", 500, 500),
            (20, "Lake Big", "Lake", 2500, 500),
            (21, "Small Pond", "Reservoir", 2050, 50),
            (22, "Old Lake (historical)", "Lake", 2500, 520),
            (30, "Lake Near", "Lake", 5100, 500),
            (40, "Lake Far", "Lake", 8000, 500),
        ]
    )
    rows = {r["comid"]: r for r in x.crosswalk(lakes, points)}
    assert rows[1]["name"] == "Named Lake" and rows[1]["name_source"] == "shapefile"
    assert rows[1]["gnis_name_raw"] == "Lake Named" and rows[1]["n_candidates"] == 1
    assert rows[2]["name"] == "Lake Big" and rows[2]["name_source"] == "gnis_inside"
    assert rows[2]["n_candidates"] == 2 and rows[2]["alternatives"] == "Small Pond"
    assert rows[2]["distance_m"] == 500.0
    assert rows[3]["name"] == "Lake Near" and rows[3]["name_source"] == "gnis_near"
    assert rows[3]["distance_m"] == 100.0
    assert rows[4]["name"] is None and rows[4]["name_source"] == "none"
