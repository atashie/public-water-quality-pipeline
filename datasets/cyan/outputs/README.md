# CyAN outputs

Evidence written by scripts under `../access/` and, later, `../qaqc/`. Never edit a file here by hand. Rerun the script that wrote it. [docs/measurements.md](../../../docs/measurements.md) interprets these files.

| File | Written by | What it holds |
|---|---|---|
| `plan-weekly-mosaic-2026-09-22.json` | `pull_cyan.py --dry-run` | The approved weekly whole-region selection: every filename, counts, streams, search time, code provenance |
| `plan-daily-mosaic-2026-09-22.json` | `pull_cyan.py --dry-run` | The approved daily whole-region selection for the last 8 weeks |
| `lake-table-<stamp>.json` | `build_lake_table.py` | Summary of one per-lake table build: recipe, lakes with and without interior pixels, row counts, coverage counts, the table's path and sha256, and provenance |
| `lake-dashboard-<stamp>.json` | `build_lake_dashboard.py` | Summary of one lake dashboard build: the table it served and its sha256, the companion attribute table, the recipe, the bloom line and its source, the weeks covered, the newest week's class counts, and provenance |
| `pixel-history-<stamp>.json` | `viz/estimate_pixel_history.py` | Bytes of the per-lake pixel images for the newest 52 weekly files, as the dashboard encodes them, per week, per lake, and in total, with two cheaper encodings measured beside them |
| `mask-check-<stamp>.json` | `qaqc/check_lake_masks.py` | Exact coverage fractions against the interior and touched masks for a sample of lakes, per lake and in total, plus the displacement of 300 m simplified outlines |
| `qa-<dir>-<stamp>.json`, `qa-report-<stamp>.md` | `qa_cyan.py` | One result per raw directory per run, stamped with the run's UTC time, plus the report. Earlier runs are never overwritten |
| `route-comparison-2026-09-22.json` | `compare_routes.py` | Presence of every listed weekly file on the cloud endpoint, the catalog count, the credentials and listing test, and two byte comparisons |
