# cyan_lakes: the CyAN resolvable-lakes shapefile

Status: pulled and checked on 2026-09-23. The lake universe of assumption A9 and the COMID backbone of assumption A20.

What it is: `MERIS_OLCI_Lakes.zip` from the NASA Earthdata CyAN project page, holding `updatedValidLakes.shp`, plus the contiguous-United-States tile grid `CONUS_tiles_shapefile.zip`. Both are public, no login. Claims cl-cyan-lakes-shapefile-link and cl-cyan-lakes-conus-tile-shapefile in [the CyAN METADATA](../cyan/METADATA.md).

## Run guide

```sh
uv run python datasets/cyan_lakes/access/pull_lakes.py --dry-run   # plan
uv run python datasets/cyan_lakes/access/pull_lakes.py             # fetch both zips, manifested
uv run python datasets/cyan_lakes/qaqc/qa_lakes.py                 # local QA, writes outputs/
uv run python datasets/cyan_lakes/access/pull_gnis.py --dry-run    # plan the USGS GNIS names file
uv run python datasets/cyan_lakes/access/pull_gnis.py              # fetch it, manifested, 38 MB
uv run python datasets/cyan_lakes/derive/build_name_crosswalk.py   # name every lake, writes outputs/
```

Files land under `data/cyan_lakes/raw/` with `manifest.jsonl`. Evidence lands under [outputs/](outputs/README.md).

## What the QA found on 2026-09-23

2,321 features with 2,321 distinct COMID, no null, no duplicate. Projection reads as EPSG:5070. 2,316 polygons and 5 multipolygons, 2,306 valid geometries. Areas from 0.74 to 4,310 km², median 7.3 km², summing to 67,370 km². The file's `AREASQKM` field equals the geometry area within 0.02 percent. 455 features carry no name. The fields `shore_dist`, `max_window`, `new_flag`, and the `_1` duplicates are undocumented on the page. See [the QA report](outputs/README.md).

The shapefile carries COMID. That closes open item O3 of the CyAN METADATA. Which NHDPlus version the COMIDs follow is stated on the project page as version 2.0 for "the CONUS shapefile", which may mean either file.

## Names by COMID, 2026-09-23

455 lakes carry no `GNIS_NAME` in the shapefile, and the NHDPlus waterbody layer at the USGS returns the same blanks for them, so no crosswalk keyed by COMID alone can name them. `derive/build_name_crosswalk.py` names them from the USGS Geographic Names Information System instead: the domestic-names national file, class Lake or Reservoir, by the point inside each lake polygon. Recipe `gnis-crosswalk-v2` in the script's docstring. The shapefile name wins where it exists. The result is a tracked CSV under [outputs/](outputs/README.md), one row per lake with the name, its source, and the other GNIS names inside the polygon. [Measurement 9](../../docs/measurements.md#9-names-for-every-lake-by-comid-from-the-shapefile-and-the-gnis-point-inside-the-polygon-2026-09-23).

A GNIS name chosen among several candidates is a heuristic label, not an identifier. COMID stays the key, assumption A22. The EPA forecast's public lake names, step 2, are the planned better source for the lakes it covers.
