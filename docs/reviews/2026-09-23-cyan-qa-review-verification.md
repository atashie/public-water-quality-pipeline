# Verification of the dispositions of the independent review of the CyAN pull and QA/QC: two gaps closed, one suggestion declined, 2026-09-23

Implementer: Claude Code (AI coding agent), directed by the repository owner. Scope: the [independent review](2026-09-22-cyan-pull-qa-independent-review.md) by Codex on 2026-09-22 and the dispositions recorded in the [delivery record](2026-09-22-cyan-pull-and-qa.md). Nothing committed. No provider contacted. No result file written or deleted.

## What the owner directed

The owner asked for the review to be read again, for every suggestion still worth taking to be integrated, and for each disagreement to be explained.

## Method

Each finding was checked against the code committed in `56ad456` and the current documents, not against the delivery record's own claims. The failure cases were exercised on synthetic GeoTIFFs in the tests. The inventory and completeness functions were run on the real plans, manifests, and disk listing without opening a raster.

## Dispositions verified

| Finding | Delivery record said | Verified state |
|---|---|---|
| 1. Mixed processing versions | Fixed | Verified. `collection_checks` flags a mixed version tag, data type, band count, nodata flag, or stream. `grid_consistent` is separate from `collection_consistent`. The regression test with versions 6.0, 7.0, and 6.0 passes. Observed values are kept under `values`. The review's expected-version check is declined below |
| 2. Completeness silently shrinks | Fixed | Partly. Plan bounds, the reconciled inventories, and unreadable files keeping their dates are verified. Two gaps found and closed below |
| 3. Corrupt TIFF exits zero | Fixed | Verified. `main` returns 1 after writing the results when a file is unreadable, a digest differs, an inventory differs, or an invariant breaks. Notes never change the status. One passing and one failing run are tested |
| 4. Latency is age at retrieval | Fixed, upper-bound framing kept | Verified and agreed. The manifest key, the QA report, the heading of measurement 4, and METADATA say age at retrieval. The publication delay stays `unverified`. One stale word in the `pull_cyan.py` docstring corrected |
| 5. Results do not identify the implementation | Fixed | Verified. Each result carries the base revision, the dirty flag, and the sha256 of three source files and two inputs. Results are stamped and never overwritten. Three convention documents still prescribed fixed output names, corrected below |
| Interpretation corrections | Fixed | Verified in measurement 5, METADATA sections 4 and 5, and the report footer. The land-count spread is stated as a lower bound on differing pixels, which holds by counting |
| Stale status lines | Fixed | `CLAUDE.md` verified. The dataset README still said the pull awaits authorization and the QA runs once the pull completes. Corrected below |
| Prior dispositions omitted | Fixed | Verified. The delivery record carries a table for the earlier review |

## Gaps closed

| Gap | Change |
|---|---|
| An unplanned file on disk was reconciled but never flagged, so a directory holding more than the approved selection passed with exit 0. The delivery record claimed every discrepancy is a collection flag | `on_disk_not_planned` is a collection flag and fails the run. Test `test_unplanned_file_on_disk_is_a_collection_flag` |
| One `missing` list mixed dates the plan never listed with planned files absent or unreadable. The review asked for catalog gaps, missing downloads, and unreadable files to be reported separately | `completeness` now carries `missing_not_planned`, gaps in the search listing, and `missing_planned`, files the plan holds and the disk does not deliver. The report row shows both. The note names which kind it counts. On the real inventory the weekly week starting 2026-07-05 is `missing_not_planned` and both `missing_planned` lists are empty |
| A run without a plan takes its bounds from the filenames on disk and said so only in a JSON field | A collection note states that an absent first or last date cannot be detected. Test `test_without_a_plan_the_bounds_come_from_disk_and_the_notes_say_so` |
| `.claude/rules/datasets.md`, `CLAUDE.md`, and `datasets/README.md` told the next dataset to write `qa_report.md` and `qa_summary.json`, which a rerun overwrites | The three now name the stamped files and forbid overwriting |
| The dataset README status lines | Now say the pull and the QA are done and link the delivery record |
| `pull_cyan.py` docstring and one test name still said latency | Renamed to age at retrieval |

## Suggestions declined

Finding 1 asks the QA to check the files against an expected processing version. Not added. The version is a fact read from each file and recorded in the manifest and in every QA result. A configured expectation would be a second home for that fact and would need editing at every reprocessing. Agreement across files plus the reported value shows any change, and a file changed in place fails the sha256 check first.

Finding 4 asks that the latency be reported only as age at retrieval. The delivery record kept the newest file's age as an upper bound on the publication delay. Agreed. A file retrieved 3 days after its window end was published no later than 3 days after its window end. That holds for that one file and says nothing about the typical delay.

## Observed and left for the owner

- Per-file structural flags, projection, pixel size, band count, and type, do not fail the run when every file shares the same wrong value. The docstring states the contract. Making them fatal is a contract change.
- Every committed QA result records GDAL's `DERIVED_SUBDATASETS` tag values. They contain the absolute local path of each file, including the owner's home directory, 598 times in all. GDAL synthesizes these tags. They are not stored in the file. Assumption A15 says this repository can become public. Results are never edited by hand, so the options are to stop recording those values and to rerun.
- The judging criterion `Latency` in [the work plan](../work-plan.md) is defined as window end to local availability. That is the age at retrieval under another name.

## Checks

| Check | Result |
|---|---|
| `uv run ruff check .` and `uv run ruff format --check .` | Pass |
| `uv run pytest -q` | 142 passed. No network |
| Real inventory, no pixel read | Weekly 542 planned, in the manifest, and on disk, 543 expected dates, 542 present, `missing_not_planned` 2026-07-05. Daily 56 of 56 on every count |

## Proposed next step

Owner review of these changes together with the uncommitted step 1f work already in the tree. A QA rerun over the 598 files under the corrected code would take about 70 minutes and write new stamped results with the split fields. It was not run. Then commit with the owner's authorization.
