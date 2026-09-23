# cyan_lakes outputs

Evidence written by `../qaqc/qa_lakes.py` and `../derive/build_name_crosswalk.py`. Never edit a file here by hand. Rerun the script.

| File | What it holds |
|---|---|
| `qa-lakes-<stamp>.json` | Feature counts, COMID checks, fields, projection, geometry validity, area statistics, largest lakes, the tile rows, manifest digests, integrity, and code provenance |
| `qa-lakes-<stamp>.md` | The same as a report |
| `lake-names-<stamp>.csv` | One row per lake: COMID, the shapefile name, the chosen name, its source, the GNIS id, class, and state, the candidate count, the distance, and the other GNIS names inside the polygon. The dashboard builder reads the newest |
| `lake-names-<stamp>.json` | The run's recipe, counts by source, the agreement between shapefile names and GNIS points, the largest newly named lakes with their alternatives, the CSV's sha256, and code provenance |
