# Step 1e, CyAN lake universe and per-lake table: 2,321 lakes keyed by COMID, the recipe of decision 0002, and one row per lake and file, 2026-09-23

Implementer: Claude Code (AI coding agent), directed by the repository owner. Scope: step 1e of [the work plan](../work-plan.md). Two public shapefile zips were fetched. No other provider was contacted. The lake shapefiles and the extraction code were committed in `6c7321f` at the owner's direction before the table was built.

## What the owner directed

The owner approved step 1d and authorized step 1e on 2026-09-23. Assumption A17 requires a recorded recipe and authorization before any aggregation of pixels. [Decision 0002](../decisions/0002-per-lake-table-recipe.md) records the recipe the implementer proposed under that authorization. The owner confirms or amends it on this review.

## What changed

| Area | Change |
|---|---|
| Lake universe | `datasets/cyan_lakes/` with a manifested pull of `MERIS_OLCI_Lakes.zip` and `CONUS_tiles_shapefile.zip` and a QA script with stamped results. [Measurement 6](../measurements.md#6-the-cyan-resolvable-lakes-shapefile-2321-lakes-keyed-by-comid-2026-09-23) |
| Recipe | [Decision 0002](../decisions/0002-per-lake-table-recipe.md): interior pixels at 99.9 percent coverage from an 8 by 8 oversampled rasterization, statistics over codes 0 to 253 with zero included, land and no data excluded, no temporal aggregation |
| Extraction | `datasets/cyan/derive/build_lake_table.py` with 3 offline tests. Masks computed once per lake as flat pixel indices. Each file read once in full and every lake sliced from memory |
| Table | `data/cyan/derived/cyan_lake_table-2026-09-23T1436Z.parquet`, 1,387,958 rows and 21 columns for 2,321 lakes and 598 files, 32.6 MB, ignored by git, with a provenance sidecar. Summary under `datasets/cyan/outputs/`. [measurement 7](../measurements.md#7-the-per-lake-table-1387958-rows-for-2321-lakes-under-decision-0002-2026-09-23) |
| Documents | Open item O3 closed in the CyAN METADATA. Registry row for `cyan_lakes`. Work plan, commands, and dataset index updated |

## Findings

1. **Every lake in the universe yields interior pixels.** The shapefile is already the sensor-resolvable set. The smallest lake rests on 3 interior pixels, the median on 44, the largest on 46,186.
2. **The interior rule is strict.** It discards a median 61 percent of the pixels a lake polygon touches, and 78 percent at the 90th percentile. 688 lakes rest on fewer than 25 pixels and 51 on fewer than 9. This is the recipe of the EPA forecast paper, and it is the first thing the owner may want to amend. A looser rule, majority coverage for example, is a one-line change and a rebuild of 90 seconds.
3. **Coverage.** 82.7 percent of weekly lake-weeks have at least one valid pixel and 75.3 percent have half or more. The mean valid fraction moves with the seasons and the years, from 0.64 in 2017 to 0.78 in 2024.
4. **The table is cheap to rebuild.** 87 seconds for the whole record, so recipe changes cost nothing but a review.
5. **Distribution under the EPA threshold, for orientation only.** 11.9 percent of weekly lake-weeks with a valid pixel have a median code of 130 or more. That is near the base rate the EPA forecast paper reports and is not a bloom claim.

## Checks

| Check | Result |
|---|---|
| `uv run pytest -q` | 113 passed. No network |
| `uv run ruff check .` and `uv run ruff format --check .` | Pass |
| Build | 598 files in 1 minute 27 seconds, exit 0. Weekly rows equal lakes times files exactly. Every row's `n_valid` plus `n_land` plus `n_nodata` equals `n_interior` by construction |
| Provenance | The table's sidecar names the recipe id, the base revision, the dirty flag, the hashes of the extraction code and access module, and the hashes of the lake zip and both manifests |

## Limits

- The recipe is the EPA forecast paper's as replicated in the HAB_PoC repository. Whether it is the right one for this project's uses is the owner's call on this review.
- Interior pixels exclude every shoreline cell. A bloom confined to a shore is invisible to the table. The touched count per lake shows how much of a lake the rule discards.
- No value in the table is validated against a field observation. That is later work.
- The shapefile's polygons are as published in 2026-01. Shorelines move.

## Owner decisions requested

1. Confirm or amend the recipe in decision 0002. Any change renames the recipe id and rebuilds the table.
2. Whether the interior rule stays at 99.9 percent coverage or moves to a looser rule such as majority coverage. It discards a median 61 percent of touched pixels. Both rules can be carried as two tables if the owner wants the comparison.

## Authorization

The owner walked through the data folders and the recipe on 2026-09-23, confirmed decision 0002 as written, and authorized commit, push, and step 1f. A companion per-lake table with centroids, windows, and interior cell indices was offered and is folded into step 1f, which needs the geometries anyway.

## Proposed next step

Owner review of the recipe and of this record. Then authorization to commit the table's evidence and this record. Then step 1f, the user-facing dashboard to the owner's specification, for which the per-lake table is the source.
