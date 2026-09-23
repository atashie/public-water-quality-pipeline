#!/usr/bin/env python
"""QA/QC of the CyAN lake and tile shapefiles. Reads the local zips only. Contacts nothing.

Reports, for the lake file: feature count, distinct COMID count and duplicates, fields and
types, projection, geometry validity, area statistics from the file's own area field and from
the geometry in EPSG:5070, bounds, and the largest lakes. For the tile file: feature count,
fields, projection, and the tile rows. Writes qa-lakes-<stamp>.json and qa-lakes-<stamp>.md.
Never edit them by hand.

Usage:
  uv run python datasets/cyan_lakes/qaqc/qa_lakes.py
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

RAW = REPO / "data" / "cyan_lakes" / "raw"
OUT = REPO / "datasets" / "cyan_lakes" / "outputs"
AREA_FIELDS = ("AREASQKM", "AREA_SQKM", "AREA")
PIXEL_M2 = 300.0 * 300.0


def quantiles(s) -> dict:
    import numpy as np

    return {
        "min": round(float(s.min()), 4),
        "p10": round(float(np.percentile(s, 10)), 3),
        "median": round(float(s.median()), 3),
        "p90": round(float(np.percentile(s, 90)), 2),
        "max": round(float(s.max()), 1),
        "sum": round(float(s.sum()), 1),
    }


def describe_lakes(path: Path) -> dict:
    import geopandas as gpd
    import numpy as np

    g = gpd.read_file(f"zip://{path}")
    rec: dict = {
        "source": path.name,
        "layer": "updatedValidLakes",
        "features": int(len(g)),
        "crs": g.crs.to_string() if g.crs else None,
        "epsg": g.crs.to_epsg() if g.crs else None,
        "fields": {c: str(t) for c, t in g.dtypes.items() if c != "geometry"},
        "geometry_types": {k: int(v) for k, v in g.geometry.geom_type.value_counts().items()},
        "valid_geometries": int(g.geometry.is_valid.sum()),
        "empty_geometries": int(g.geometry.is_empty.sum()),
        "bounds": [round(float(v), 3) for v in g.total_bounds],
    }
    if "COMID" in g.columns:
        comid = g["COMID"].astype("int64")
        rec["comid"] = {
            "distinct": int(comid.nunique()),
            "null": int(g["COMID"].isna().sum()),
            "duplicated_rows": int(comid.duplicated().sum()),
            "min": int(comid.min()),
            "max": int(comid.max()),
        }
    g5070 = g.to_crs(5070) if g.crs and g.crs.to_epsg() != 5070 else g
    geom_km2 = g5070.geometry.area / 1e6
    rec["area_km2_from_geometry_epsg5070"] = quantiles(geom_km2)
    area_field = next((c for c in g.columns if c.upper() in AREA_FIELDS), None)
    if area_field:
        field_km2 = g[area_field].astype(float)
        ratio = geom_km2.values / field_km2.values
        rec["area_field"] = area_field
        rec["area_km2_from_field"] = quantiles(field_km2)
        rec["geometry_over_field_area"] = {
            "median": round(float(np.median(ratio)), 4),
            "p1": round(float(np.percentile(ratio, 1)), 4),
            "p99": round(float(np.percentile(ratio, 99)), 4),
        }
    pixels = geom_km2 * 1e6 / PIXEL_M2
    rec["pixels_300m_from_area"] = {
        "under_9": int((pixels < 9).sum()),
        "under_25": int((pixels < 25).sum()),
        "median": round(float(pixels.median()), 1),
    }
    name_field = next((c for c in g.columns if "NAME" in c.upper()), None)
    if name_field:
        blank = g[name_field].astype(str).str.strip() == ""
        rec["name_field"] = name_field
        rec["unnamed"] = int(g[name_field].isna().sum() + blank.sum())
        top = g5070.assign(_a=geom_km2).sort_values("_a", ascending=False).head(8)
        rec["largest"] = [
            {
                "name": str(r[name_field]),
                "comid": int(r["COMID"]) if "COMID" in g.columns else None,
                "km2": round(float(r["_a"]), 1),
            }
            for _, r in top.iterrows()
        ]
    return rec


def describe_tiles(path: Path) -> dict:
    import geopandas as gpd

    g = gpd.read_file(f"zip://{path}")
    return {
        "source": path.name,
        "features": int(len(g)),
        "crs": g.crs.to_string() if g.crs else None,
        "epsg": g.crs.to_epsg() if g.crs else None,
        "fields": {c: str(t) for c, t in g.dtypes.items() if c != "geometry"},
        "bounds": [round(float(v), 3) for v in g.total_bounds],
        "rows": [
            {c: str(r[c]) for c in g.columns if c != "geometry"} for _, r in g.head(60).iterrows()
        ],
    }


def write_report(summary: dict, path: Path) -> None:
    lk, tl, cm = summary["lakes"], summary["tiles"], summary["lakes"]["comid"]
    lines = [f"# CyAN lake and tile shapefiles, QA/QC, {summary['stamp']}\n", "## Lakes\n"]
    lines.append("| Check | Result |\n|---|---|")
    ids = f"{lk['features']}, {cm['distinct']}, {cm['duplicated_rows']}, {cm['null']}"
    lines.append(f"| Features, distinct COMID, duplicated rows, null COMID | {ids} |")
    lines.append(f"| Projection | EPSG {lk['epsg']}. Full text in the JSON result |")
    fields = ", ".join(f"{k} {v}" for k, v in lk["fields"].items())
    lines.append(f"| Fields | {fields} |")
    geom = f"{lk['geometry_types']}, {lk['valid_geometries']}, {lk['empty_geometries']}"
    lines.append(f"| Geometry types, valid, empty | {geom} |")
    lines.append(f"| Bounds in the file's projection | {lk['bounds']} |")
    lines.append(
        f"| Area km² from geometry in EPSG:5070 | {lk['area_km2_from_geometry_epsg5070']} |"
    )
    if "area_km2_from_field" in lk:
        lines.append(f"| Area km² from field `{lk['area_field']}` | {lk['area_km2_from_field']} |")
        lines.append(f"| Geometry area over field area | {lk['geometry_over_field_area']} |")
    px = lk["pixels_300m_from_area"]
    small = f"{px['under_9']}, {px['under_25']}. Median {px['median']} pixels"
    lines.append(f"| Lakes under 9 and under 25 native pixels by area | {small} |")
    if "largest" in lk:
        largest = ", ".join(f"{x['name']} {x['km2']} km²" for x in lk["largest"])
        lines.append(f"| Unnamed | {lk['unnamed']} |")
        lines.append(f"| Largest | {largest} |")
    lines.append("\n## Tiles\n")
    lines.append(f"{tl['features']} features, EPSG {tl['epsg']}, fields {list(tl['fields'])}.")
    lines.append(f"Bounds {tl['bounds']}. Projection text is in the JSON result.\n")
    lines.append(
        "Areas are of the polygons as drawn. A lake's pixel count on the CyAN grid depends on "
        "the mask rule, decided in step 1e."
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--raw", default=str(RAW))
    ap.add_argument("--outdir", default=str(OUT))
    args = ap.parse_args(argv)
    raw, out = Path(args.raw), Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)
    started = net.utc_now_iso()
    stamp = started.replace(":", "")[:15] + "Z"
    lakes_zip, tiles_zip = raw / "MERIS_OLCI_Lakes.zip", raw / "CONUS_tiles_shapefile.zip"
    manifest = {m["filename"]: m for m in net.read_manifest(raw / "manifest.jsonl")}
    summary = {
        "measured_at": started,
        "stamp": stamp,
        "lakes": describe_lakes(lakes_zip),
        "tiles": describe_tiles(tiles_zip),
        "manifest": {
            k: {kk: v[kk] for kk in ("url", "bytes", "sha256", "accessed_utc")}
            for k, v in manifest.items()
        },
        "integrity": {
            p.name: net.sha256_file(p) == manifest.get(p.name, {}).get("sha256")
            for p in (lakes_zip, tiles_zip)
        },
        "code": provenance.code_provenance(
            [Path(__file__)], [lakes_zip, tiles_zip, raw / "manifest.jsonl"]
        ),
    }
    (out / f"qa-lakes-{stamp}.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    write_report(summary, out / f"qa-lakes-{stamp}.md")
    lk = summary["lakes"]
    print(f"[qa] lakes {lk['features']} features, {lk['comid']['distinct']} distinct COMID")
    print(f"[qa] EPSG {lk['epsg']}, fields {list(lk['fields'])}")
    print(f"[qa] tiles {summary['tiles']['features']} features, integrity {summary['integrity']}")
    print(f"[qa] wrote qa-lakes-{stamp}.json and .md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
