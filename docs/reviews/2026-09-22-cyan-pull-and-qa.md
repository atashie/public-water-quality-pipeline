# Step 1b part 2 and step 1c, CyAN pull and QA/QC: 598 files, 3.35 GB, every file version 6.0, structure read from the files, corrected after two independent reviews, 2026-09-22

Implementer: Claude Code (AI coding agent), directed by the repository owner. Scope: the pull authorized on 2026-09-22 and step 1c of [the work plan](../work-plan.md). Nothing committed.

## What the owner directed

After approving step 1b part 1, the owner authorized the full pull and step 1c on 2026-09-22. The owner then had Codex review the delivery and asked for every agreed correction to be applied, with disagreements explained. The dispositions are below.

## What changed

| Area | Change |
|---|---|
| Data | 542 weekly and 56 daily whole-region files under `data/cyan/raw/`, ignored by git, each in the manifest with sha256, bytes, version tag, and observed latency. [Measurement 4](../measurements.md#4-the-assumption-a8-pull-598-files-335-gb-no-failure-newest-weekly-file-3-days-old-at-retrieval-2026-09-22) |
| QA code | `datasets/cyan/qaqc/qa_cyan.py` with 10 offline tests on synthetic GeoTIFFs. Inventory reconciliation against the approved plan, integrity, structure, tag namespaces, composition under the encoding, collection invariants, plan-bound completeness, manifest statistics, provenance, and exit codes that fail on unreadable files, digest mismatches, missing planned files, and broken invariants |
| Access code | `parse_search_body` fails closed on unexpected HTML or empty bodies. Plans carry every filename and code provenance. `pull_cyan.py --plan` detects selection drift and refuses without `--accept-drift`. The manifest field `latency_days` is renamed `age_at_retrieval_days` for new pulls. `compare_routes.py` records provenance. A shared `provenance.py` helper with tests |
| Evidence | Plans regenerated with every filename at 2026-09-22T18:46Z and 18:47Z. They match the pulled manifests file for file. QA results `qa-weekly_conus_mosaic-2026-09-22T1850Z.json`, `qa-daily_conus_mosaic-2026-09-22T1850Z.json`, and `qa-report-2026-09-22T1850Z.md` under `datasets/cyan/outputs/`, stamped with the run time. [Measurement 5](../measurements.md#5-qaqc-of-the-pulled-files-2026-09-22) |
| METADATA | Sections 2, 3, 4, 6, 7.3, 10, and 12 carry values read from files, with the wording corrections below. Open items O2 and O4 resolved. O1 bounded |

## Findings

1. **Structure read from real files matches the documentation.** Every one of the 598 files is a single uint8 band in EPSG:5070 at exactly 300.0 m. All are 26,328 by 15,138 pixels on one shared grid, LZW compressed, without a nodata flag. Open item O2 is resolved for the whole-region files and discrepancies D3 and D4 are settled in favor of GeoTIFF at 300 m.
2. **Two default-namespace tags and no separately exposed flag raster.** The default namespace holds `AREA_OR_POINT` and `OBPG_version=6.0` in every file, beside the `IMAGE_STRUCTURE` and `DERIVED_SUBDATASETS` namespaces. Open item O4 is resolved. Whether upstream snow and ice screening was applied is not visible in the files.
3. **Integrity and invariants hold.** Every sha256 matches the manifest. Every collection invariant, grid, projection, type, band count, nodata flag, stream, and version, takes one value. Zero files and zero collections carry a flag. The four codes partition every uint8 value, so composition describes the files and validates no meaning.
4. **The land class differs between files.** The count varies from 132,508,772 to 132,510,137 pixels, a spread of 1,365. That spread is a lower bound on the pixels whose class differs. A per-lake mask must come from the lake polygons in step 1e and treat each file's land and no-data codes on its own.
5. **Composition of the whole canvas.** Weekly files are 33.2 percent land and 61 to 64 percent no data, because the canvas extends beyond the region. Below detection is 2.5 to 5.1 percent and data 0.03 to 0.53 percent. None of this measures coverage inside a lake. The top code 253 appears in 537 of 542 weekly files.
6. **Completeness against the approved plans.** Weekly 542 of 543 dates, the week starting 2026-07-05 absent from the search listing. Daily 56 of 56. Newest age at retrieval 3 days weekly and 1 day daily, which bound the publication delay from above.

## Dispositions of the independent validation of route measurements

| Finding | Disposition |
|---|---|
| 1. Unexpected HTML becomes a successful empty search | Fixed. `parse_search_body` accepts only the explicit empty markers. Other HTML and empty bodies fail after the retries. Regression test added |
| 2. Identity and absence claims exceed the observations | Fixed. Measurements 1 and 2, METADATA sections 2, 7.3, and 12, and the AWS note now say two samples byte-identical, unavailable paths rather than missing files, listing absence rather than archive absence, and date coverage retained rather than no data lost |
| 3. The saved plans cannot reproduce the exact approved selection | Fixed. Plans carry every filename and code provenance. Execution with `--plan` detects drift and refuses to download unless told to accept it. Both plans were regenerated and match the pulled manifests file for file. The route-comparison result stays as written. Measurement 1 notes that its script ran uncommitted and was committed unchanged in `5663c35` |
| 4. Recorded latency is age at access | Fixed. New pulls write `age_at_retrieval_days`. The QA reads both keys and labels the value age at retrieval. Measurement 4 and METADATA present the newest file's age as an upper bound on the publication delay, and the delay itself as `unverified` |
| Primary-source validation of the regional restriction | Accepted. The NASA staff forum response is cited as `documented` in measurement 1 and METADATA section 7.3 |

## Dispositions of the independent review of the pull and QA

| Finding | Disposition |
|---|---|
| 1. Mixed processing versions still report a consistent collection | Fixed. Collection invariants cover grid, projection, type, band count, nodata flag, stream, and version tag. `grid_consistent` and `collection_consistent` are separate. A mixed version is a collection flag and a nonzero exit. Regression test with versions 6.0, 7.0, 6.0 |
| 2. Completeness silently shrinks when endpoint files disappear | Fixed. Expected dates come from the approved plan's bounds. Planned, manifest, disk, and readable inventories are reconciled and every discrepancy is a collection flag. Unreadable files keep their filename dates and are listed. Regression test with a removed file and manifest record |
| 3. A corrupt TIFF still produces a successful process exit | Fixed. Exit 1 after writing the results when any file is unreadable, any digest differs, any planned file is missing, or any invariant breaks. Notes such as the land count do not change the status. Tests cover a clean run and a failing run |
| 4. The reported latency remains age at retrieval | Fixed as above. One framing kept on purpose: the newest file's age at retrieval is a measured upper bound on the publication delay and is reported as such |
| 5. QA results do not identify the implementation | Fixed. Each result records the base revision, the dirty flag, the sha256 of the QA script, the access module, and the download helper, and the sha256 of the manifest and plan it read. Results are stamped with the run's UTC time and never overwritten. The first run's files, produced by the superseded implementation and never committed, were deleted before this correction was applied. That deletion went against the finding and cannot be undone. A note at the old report path records it, and no result file is deleted from now on |
| Interpretation: partition of uint8, tag namespaces, flag raster, listing absence, land spread, canvas percentages | Fixed in measurement 5, METADATA sections 4 and 5, and the QA report footer |
| Stale status lines in CLAUDE.md and the dataset README | Fixed |
| Dispositions of the earlier review were omitted | Fixed by the table above |

## Checks

| Check | Result |
|---|---|
| Pull | 598 of 598 planned files fetched, 0 failures, 0 integrity events, 13 minutes 35 seconds in all. The regenerated plans match the manifests file for file |
| `uv run pytest -q` | 96 passed. No network |
| `uv run ruff check .` and `uv run ruff format --check .` | Pass |
| QA run | 598 files against both approved plans, exit 0. 0 files flagged, 0 collection flags, inventories agree at 598. Per-file numbers equal the first run's. 69 minutes of wall time against 10 for the first run, so wall time is not reported as throughput |
| Credential scan | No token in any tracked file |

## Limits

- The QA reads the whole record once and measures it on one day. A reprocessing changes every value.
- Sha256 recomputation confirms what was downloaded, not what the producer intended. No producer checksum exists to compare against.
- No pixel has been compared against a lake polygon or an in situ measurement. That is step 1e and later.

## Dispositions of prior findings

| Finding | Disposition |
|---|---|
| METADATA O1, weekly update timing | Bounded from above by the newest file's age at retrieval. The delay itself stays `unverified` |
| METADATA O2, EPSG code and tile dimensions not on any page | Fixed for whole-region files. EPSG:5070 and 26,328 by 15,138 pixels read from every file. Tile dimensions stay `prior` |
| METADATA O4, flag bands in the GeoTIFF | Fixed. One band, two tags, no flag band |
| Measurement 3, size estimate `unverified` | Fixed. Measured on the pull |

## Authorization

The owner reviewed the corrected record and dispositions on 2026-09-22, authorized commit and push, and authorized step 1d.

## Proposed next step

Owner review of this record, the dispositions, the QA report, and the METADATA changes. Then authorization to commit and push. Then step 1d, the review dashboard the owner explores.
