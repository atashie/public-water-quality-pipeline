# cyan_lakes: the CyAN resolvable-lakes shapefile

Status: pulled and checked on 2026-09-23. The lake universe of assumption A9 and the COMID backbone of assumption A20.

What it is: `MERIS_OLCI_Lakes.zip` from the NASA Earthdata CyAN project page, holding `updatedValidLakes.shp`, plus the contiguous-United-States tile grid `CONUS_tiles_shapefile.zip`. Both are public, no login. Claims cl-cyan-lakes-shapefile-link and cl-cyan-lakes-conus-tile-shapefile in [the CyAN METADATA](../cyan/METADATA.md).

## Run guide

```sh
uv run python datasets/cyan_lakes/access/pull_lakes.py --dry-run   # plan
uv run python datasets/cyan_lakes/access/pull_lakes.py             # fetch both zips, manifested
uv run python datasets/cyan_lakes/qaqc/qa_lakes.py                 # local QA, writes outputs/
```

Files land under `data/cyan_lakes/raw/` with `manifest.jsonl`. Evidence lands under [outputs/](outputs/README.md).

## What the QA found on 2026-09-23

2,321 features with 2,321 distinct COMID, no null, no duplicate. Projection reads as EPSG:5070. 2,316 polygons and 5 multipolygons, 2,306 valid geometries. Areas from 0.74 to 4,310 km², median 7.3 km², summing to 67,370 km². The file's `AREASQKM` field equals the geometry area within 0.02 percent. 455 features carry no name. The fields `shore_dist`, `max_window`, `new_flag`, and the `_1` duplicates are undocumented on the page. See [the QA report](outputs/README.md).

The shapefile carries COMID. That closes open item O3 of the CyAN METADATA. Which NHDPlus version the COMIDs follow is stated on the project page as version 2.0 for "the CONUS shapefile", which may mean either file.
