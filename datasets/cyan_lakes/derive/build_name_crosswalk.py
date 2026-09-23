#!/usr/bin/env python
"""Name every CyAN lake by COMID from the shapefile, else from a GNIS point inside its polygon.

Recipe, id gnis-crosswalk-v2:
  1. The shapefile's GNIS_NAME wins when present. Source "shapefile".
  2. Else the GNIS domestic-names features of class Lake or Reservoir, not marked historical,
     whose primary point lies inside the lake polygon are the candidates. With several, the one
     farthest from the shoreline wins, because a lake's own point sits in its open water and a
     bay's or pond's point sits near a shore. The others are listed. Source "gnis_inside".
  3. Else the nearest such feature within NEAR_M of the polygon wins. Source "gnis_near".
  4. Else the lake stays unnamed. Source "none".
  GNIS names are kept as published. The shapefile mixes "X, Lake" and "Lake X" itself.
  Version 1 of this recipe, run once on 2026-09-23, chose the candidate nearest the polygon's
  representative point, kept historical names, and inverted "Lake X" to "X, Lake".

Reads local files only. Writes a parquet under data/cyan_lakes/derived/, a CSV and a JSON summary
under datasets/cyan_lakes/outputs/. Stamped, never overwritten.

Usage:
  uv run python datasets/cyan_lakes/derive/build_name_crosswalk.py
"""

from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from datasets._common import net, provenance  # noqa: E402

RAW = REPO / "data" / "cyan_lakes" / "raw"
DERIVED = REPO / "data" / "cyan_lakes" / "derived"
OUTPUTS = REPO / "datasets" / "cyan_lakes" / "outputs"
LAKES_ZIP = RAW / "MERIS_OLCI_Lakes.zip"
GNIS_ZIP = RAW / "DomesticNames_National_Text.zip"
GNIS_MEMBER = "Text/DomesticNames_National.txt"
CLASSES = ("Lake", "Reservoir")
NEAR_M = 300.0
RECIPE = {
    "id": "gnis-crosswalk-v2",
    "classes": list(CLASSES),
    "near_m": NEAR_M,
    "excluded": "names containing (historical)",
    "tie_break": "farthest from the shoreline",
}
COLUMNS = [
    "comid",
    "gnis_name_shapefile",
    "name",
    "name_source",
    "gnis_id",
    "gnis_name_raw",
    "gnis_class",
    "gnis_state",
    "n_candidates",
    "distance_m",
    "alternatives",
]


def natural(name: str) -> str:
    """'Okeechobee, Lake' becomes 'lake okeechobee' for comparison. Case and style folded."""
    n = name.strip()
    if n.lower().endswith(", lake"):
        n = "Lake " + n[:-6]
    return n.lower()


def read_gnis(zip_path: Path):
    """Lake and Reservoir features as a GeoDataFrame in EPSG:5070."""
    import geopandas as gpd
    import pandas as pd

    with zipfile.ZipFile(zip_path) as z, z.open(GNIS_MEMBER) as f:
        df = pd.read_csv(
            f,
            sep="|",
            dtype=str,
            encoding="utf-8-sig",
            usecols=["feature_id", "feature_name", "feature_class", "state_name"]
            + ["prim_lat_dec", "prim_long_dec"],
        )
    df = df[df["feature_class"].isin(CLASSES)].copy()
    df["lat"] = df["prim_lat_dec"].astype(float)
    df["lon"] = df["prim_long_dec"].astype(float)
    g = gpd.GeoDataFrame(
        df[["feature_id", "feature_name", "feature_class", "state_name"]],
        geometry=gpd.points_from_xy(df["lon"], df["lat"]),
        crs="EPSG:4326",
    )
    return g.to_crs("EPSG:5070")


def crosswalk(lakes, gnis) -> list[dict]:
    """One record per lake. `lakes` and `gnis` share a projected CRS."""
    import geopandas as gpd

    lakes = lakes.copy()
    gnis = gnis[~gnis["feature_name"].str.contains("(historical)", regex=False, na=False)]
    inside = gpd.sjoin(
        gnis, lakes[["COMID", "geometry"]], how="inner", predicate="within"
    )  # fmt: skip
    by_comid = {k: v for k, v in inside.groupby("COMID")}
    out = []
    for row in lakes.itertuples():
        comid = int(row.COMID)
        shp = None if row.GNIS_NAME is None or str(row.GNIS_NAME) == "nan" else str(row.GNIS_NAME)
        rec = {
            "comid": comid,
            "gnis_name_shapefile": shp,
            "name": None,
            "name_source": "none",
            "gnis_id": None,
            "gnis_name_raw": None,
            "gnis_class": None,
            "gnis_state": None,
            "n_candidates": 0,
            "distance_m": None,
            "alternatives": None,
        }
        cands = by_comid.get(comid)
        if cands is not None and len(cands):
            d = cands.geometry.distance(row.geometry.boundary)
            order = d.sort_values(ascending=False).index
            best = cands.loc[order[0]]
            rec.update(
                gnis_id=str(best["feature_id"]),
                gnis_name_raw=str(best["feature_name"]),
                gnis_class=str(best["feature_class"]),
                gnis_state=str(best["state_name"]),
                n_candidates=int(len(cands)),
                distance_m=round(float(d.loc[order[0]]), 1),
                alternatives="; ".join(str(cands.loc[i, "feature_name"]) for i in order[1:4])
                or None,
            )
        if shp:
            rec["name"], rec["name_source"] = shp, "shapefile"
        elif rec["gnis_id"]:
            rec["name"], rec["name_source"] = rec["gnis_name_raw"], "gnis_inside"
        else:
            near = gnis[gnis.geometry.dwithin(row.geometry, NEAR_M)]
            if len(near):
                d = near.geometry.distance(row.geometry)
                i = d.idxmin()
                best = near.loc[i]
                rec.update(
                    name=str(best["feature_name"]),
                    name_source="gnis_near",
                    gnis_id=str(best["feature_id"]),
                    gnis_name_raw=str(best["feature_name"]),
                    gnis_class=str(best["feature_class"]),
                    gnis_state=str(best["state_name"]),
                    n_candidates=int(len(near)),
                    distance_m=round(float(d.loc[i]), 1),
                )
        out.append(rec)
    return out


def build(args) -> dict:
    import geopandas as gpd
    import pandas as pd

    started = net.utc_now_iso()
    stamp = started.replace(":", "")[:15] + "Z"
    lakes = gpd.read_file(f"zip://{args.lakes}")
    lakes["COMID"] = lakes["COMID"].astype("int64")
    gnis = read_gnis(Path(args.gnis))
    if lakes.crs != gnis.crs:
        lakes = lakes.to_crs(gnis.crs)
    rows = crosswalk(lakes, gnis)
    df = pd.DataFrame(rows, columns=COLUMNS)
    DERIVED.mkdir(parents=True, exist_ok=True)
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    parquet = DERIVED / f"lake_names-{stamp}.parquet"
    df.to_parquet(parquet, index=False)
    csv = OUTPUTS / f"lake-names-{stamp}.csv"
    df.to_csv(csv, index=False)
    sources = df["name_source"].value_counts().to_dict()
    agree = df[(df["name_source"] == "shapefile") & df["gnis_name_raw"].notna()]
    same = int(
        (agree["gnis_name_shapefile"].map(natural) == agree["gnis_name_raw"].map(natural)).sum()
    )
    newly = df[df["name_source"].str.startswith("gnis")].merge(
        lakes[["COMID", "AREASQKM"]].rename(columns={"COMID": "comid"}), on="comid"
    )
    largest = newly.sort_values("AREASQKM", ascending=False).head(12)
    summary = {
        "measured_at": started,
        "recipe": RECIPE,
        "lakes": int(len(df)),
        "name_sources": {k: int(v) for k, v in sources.items()},
        "shapefile_names_with_a_gnis_point_inside": int(len(agree)),
        "of_which_the_nearest_gnis_name_is_the_same": same,
        "gnis_features_of_the_classes": int(len(gnis)),
        "multiple_candidates_among_newly_named": int((newly["n_candidates"] > 1).sum()),
        "largest_newly_named": [
            {
                "comid": int(r.comid),
                "name": r.name,
                "source": r.name_source,
                "area_sqkm": round(float(r.AREASQKM), 1),
                "n_candidates": int(r.n_candidates),
                "alternatives": r.alternatives,
            }
            for r in largest.itertuples()
        ],
        "parquet": provenance.rel(parquet),
        "csv": provenance.rel(csv),
        "csv_sha256": net.sha256_file(csv),
        "code": provenance.code_provenance(
            [Path(__file__)], [Path(args.lakes), Path(args.gnis), RAW / "manifest.jsonl"]
        ),
    }
    (OUTPUTS / f"lake-names-{stamp}.json").write_text(json.dumps(summary, indent=1) + "\n")
    print(f"[names] {len(df)} lakes, sources {sources}")
    print(f"[names] wrote {csv.name}, {parquet.name}")
    return summary


def parse_args(argv=None):
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--lakes", default=str(LAKES_ZIP))
    ap.add_argument("--gnis", default=str(GNIS_ZIP))
    return ap.parse_args(argv)


def main(argv=None) -> int:
    build(parse_args(argv))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
