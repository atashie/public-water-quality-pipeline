# Independent review of the CyAN pull and QA/QC, 2026-09-22

Reviewer: Codex, requested by the repository owner.

Scope: the [delivery record](2026-09-22-cyan-pull-and-qa.md), [QA report](../../datasets/cyan/outputs/qa-report-2026-09-22.md), implementation, saved results, and local raw files.
Acceptance checks: reconcile files and manifests, independently verify hashes and headers, sample pixel counts, challenge failure handling, and run the repository check workflow.
Implementation fixes, provider requests, and the next dataset step remain deferred.

The local ingest is supported by independent checks. The QA implementation and several conclusions need correction before accepting step 1c.
No corrupt downloaded file was found. The failure cases below used temporary synthetic files.

## Findings requiring follow-up

### 1. Mixed processing versions still report a consistent collection

Priority: P2, medium. Status: open, reproduced offline.

In [qa_cyan.py](../../datasets/cyan/qaqc/qa_cyan.py), `cross_file` lines 192–199 checks only CRS, dimensions, and transform.
`qa_one` requires a version tag but never checks an expected version or agreement across files.
A synthetic collection containing versions `6.0`, `7.0`, and `6.0` returns `consistent: true`, zero flagged files, and empty `flag_counts`.
Nodata conventions, band types, and stream membership also do not participate in the collection consistency verdict.

A partially reprocessed collection can therefore receive the same clean headline as this delivery.
Add explicit collection findings for incompatible versions and other required invariants.
Keep detailed observed values, and distinguish grid consistency from overall collection consistency.
Add a regression case containing mixed processing versions.

The current delivery's uniform `6.0` tags were independently confirmed. This finding concerns the QA's ability to detect future changes.

### 2. Completeness silently shrinks when endpoint files disappear

Priority: P2, medium. Status: open, reproduced offline.

`expected_dates`, lines 149–171, derives both expected endpoints from successfully inspected files.
It does not compare against a saved selection or an explicitly expected date range.
Read failures also discard the parsed filename, removing that date from the expected range when it lies at an endpoint.

Reproduction: create three consecutive daily files and their manifest, then remove the first TIFF.
The result reports two of two expected dates, no missing dates, and zero flagged files.
`manifest_only` contains the missing filename, but this discrepancy never becomes a collection flag.
If both the file and its manifest record are absent, even that indication disappears.

Reconcile the expected selection, manifest, and disk inventory independently.
Report catalog gaps, missing downloads, and unreadable files separately.
Use explicit coverage boundaries, with documented exceptions for provider availability, rather than assuming every requested date already exists.
Preserve filename-derived dates when pixel inspection fails.

This delivery has no manifest-only files. Independent calendar arithmetic confirms the reported internal weekly gap and complete daily span.
That does not establish physical absence from the provider archive.

### 3. A corrupt TIFF still produces a successful process exit

Priority: P2, medium. Status: open, reproduced offline.

`qa_directory` catches raster read failures and records `QA error`.
However, `main`, lines 358–360, always returns zero after writing reports.
Replacing a temporary TIFF with `not a tiff` produced one flagged file and exit code zero.
The existing `test_main_writes_dated_outputs` also expects zero with a known checksum mismatch.

A caller relying on process status cannot distinguish clean QA from unreadable or integrity-failing data.
Write the diagnostic artifacts, then return nonzero for fatal read errors and checksum failures.
Define how collection warnings affect status, and test the fatal cases explicitly.

### 4. The reported latency remains age at retrieval

Priority: P2, medium. Status: open, repeated from the [previous independent review](2026-09-22-cyan-independent-validation.md).

The new delivery record and measurement 4 again advertise three-day weekly latency and one-day daily latency.
The calculation uses the local access date minus the composite end date.
The oldest weekly file consequently reports 3,797 days, confirming that this measures age when downloaded.
Neither the manifests nor QA results record publication time or first observed availability.

Rename the metric to age at retrieval in code, reports, and headings.
Keep provider publication delay `unverified` until suitable observations exist.
The QA report's explanatory column heading helps, but does not justify the stronger delivery headline.

### 5. QA results do not identify the implementation that produced them

Priority: P2, medium. Status: open, code and artifact inspection.

`main`, line 349, assigns `code_version = None` unconditionally.
Both saved QA JSON files therefore lack an implementation identifier.
The implementation is uncommitted, so recording only the current Git revision would also fail to identify the executed code.

Record the base revision, working-tree state, relevant source hashes, and input manifest hashes with each run.
Preserve distinct run artifacts when rerunning QA, instead of replacing evidence solely by directory and calendar date.
This makes comparisons after code changes or provider reprocessing auditable.

## Corrections to the report's interpretation

- “Every pixel falls in the four classes” is an exhaustive partition of uint8 values, not independent validation of their meanings.
  The classes cover all 256 possible values. Describe this as composition under the documented encoding.
- “Exactly two metadata tags” describes the default dataset namespace read by `ds.tags()`.
  All six inspected samples also expose `IMAGE_STRUCTURE` and `DERIVED_SUBDATASETS` namespaces.
  The single-band finding is supported. The broader tag claim needs qualification.
- No separate flag band establishes no separately exposed flag raster. It does not establish that upstream snow or ice screening was absent.
- The missing week is absent from the saved listing and local selected collection. Physical archive absence remains unverified.
- Land-count variation proves the land classification changes, but does not measure the number or location of changed pixels.
  The count spread is not an upper bound on spatial mask differences.
  Polygon selection under assumption A9 still needs appropriate treatment of each image's land and no-data codes.
- Whole-canvas no-data percentages do not measure usable coverage within lakes or identify the causes of missingness.
  Defer those spatial claims until the relevant masks are inspected.

Two status documents also contradict the delivered state.
[CLAUDE.md](../../CLAUDE.md) still says no dataset has been pulled.
[The dataset README](../../datasets/cyan/README.md) still says the pull awaits authorization and QA runs after completion.

## Independent verification

The audit used `hashlib.file_digest`, Rasterio header reads, and standard-library date arithmetic independently of `qa_one`.
It reconciled every local TIFF against its manifest and saved per-file QA record.

| Check | Result |
|---|---|
| Inventory | 542 weekly and 56 daily TIFFs, with exact manifest and QA filename matches |
| SHA-256 and bytes | All 598 match both their manifests and QA records |
| Total bytes | 3,080,930,304 weekly and 271,020,420 daily |
| Headers | All 598 match the reported dimensions, transform, EPSG, resolution, dtype, bands, compression, blocks, nodata, and version |
| Filename dates | All agree with manifest and QA dates |
| Internal calendar coverage | Weekly gap at 2026-07-05, no daily gap, no duplicate manifest filenames |
| Pixel class counts | Exact matches for the first, middle, and last file of each collection |
| Saved class totals | Every saved per-file total equals the reported raster area |

The six fully decoded samples were:

- Weekly: windows starting 2016-04-24, 2021-07-04, and 2026-09-13.
- Daily: 2026-07-28, 2026-08-25, and 2026-09-21.

The independent audit did not repeat every pixel read across all 598 files.
It found no disagreement in the sampled pixel counts or the complete inventory, hash, header, and date checks.
Producer checksum verification, publication delay, scientific accuracy, and lake-level coverage remain outside what these checks establish.
The manifest's initial `integrity: unverified` is compatible with later local hash matches. It records the lack of a prior expected checksum.

## Prior findings and proposed next step

The previous independent review's HTML parsing, saved-selection, latency, and claim-boundary findings remain open.
The manifests now document what was fetched, but do not recover the exact earlier approved selection.
The new delivery's disposition table omits these prior findings. Add explicit dispositions rather than implying their resolution.

Retain the downloaded bytes. Correct the QA findings and report wording, add failure-case coverage, and return step 1c for review.
This review adds only this record and its index entry. Existing implementation changes and results are preserved.

## Repository checks

The repository check workflow passed in its required order:

- `uv sync --locked`: passed.
- `uv run ruff check .`: passed.
- `uv run ruff format --check .`: passed, 52 files already formatted.
- `uv run pytest -q`: 88 passed in 0.26 seconds, with 13 Rasterio pending-deprecation warnings.

Passing tests do not resolve the reproduced gaps. The existing tests do not assert the missing failure behavior.
