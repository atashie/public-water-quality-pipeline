# Datasets

One folder per dataset, the shared helpers in `_common/`, and the copy-me `_template/`. Layout follows assumption A6 in [../docs/assumptions.md](../docs/assumptions.md).
The rules for these folders are in [.claude/rules/datasets.md](../.claude/rules/datasets.md).

| Folder | Dataset | Status |
|---|---|---|
| [cyan/](cyan/README.md) | CyAN cyanobacteria index | reviewed 2026-09-23, per-lake table in progress |
| [epa_cyanohab_forecast/](epa_cyanohab_forecast/README.md) | EPA experimental cyanoHAB forecast | planned |
| [clms_lwq/](clms_lwq/README.md) | Copernicus Lake Water Quality 300 m, version 2 | planned |
| `_common/` | Shared helpers: retrying HTTP session, credential resolution, cached and manifested downloads | ported with tests |
| [_template/](_template/README.md) | Skeleton to copy for a new dataset | ready |

## The loop, in order

Every dataset follows the eight steps in [CLAUDE.md](../CLAUDE.md). Each step is one authorized unit with its own review record. This is how each step is done.

### 1. Characterize before you pull

Write `METADATA.md` from the template. Every fact carries a status and, when `documented`, a verbatim quote, the page, and the access date.
A research agent drafts. A separate checking agent on a different model confirms or corrects against the page. Codex is the preferred checker, per the owner's direction of 2026-09-22 in [CLAUDE.md](../CLAUDE.md). Only confirmed or corrected facts become `documented`.
Preserve the primary documents under `reference/`, as the PDF and a text extraction, so the trail survives link rot.
Answer at least these questions. What does each variable mean? What are the coverage, cadence, and gaps? What is the exact encoding, with nodata and below-detection codes? How is it accessed and authenticated? How large is the full archive, and what subset does assumption A16 allow? What are the producer's own caveats? How do versions and reprocessing behave? What are the license and attribution terms?

### 2. Pull with a plan

Enumerate first. Print the dry-run plan: files, dates, versions, bytes when known. Then download into `data/<dataset>/raw/` through `_common/net.py`.
Every file lands in the manifest with URL, bytes, sha256, access time, and the version tag read from the file.
Log what the enumeration returned and what the script excluded, with counts. Record the observed latency against the provider's stated latency.

### 3. QA/QC the bytes

Recompute sha256 against the manifest. Check structure against the documented specification: type, bands or variables, projection, grid, bounds.
Report the composition of codes and flags per file. Keep measured absence separate from missing. Check consistency across files. Report version tags.
Write `outputs/qa_report.md` and `outputs/qa_summary.json`. A clean report still lists what was checked.

### 4. Build the review dashboard, then stop

One static HTML page under `docs/dashboards/<dataset>/`, vendored libraries, opens from disk, requests nothing external, data as a precomputed local file.
Show native resolution. Show the composition over time. Show the QA results. Show a representative case a domain reader can judge.
The owner explores it and gives feedback. Record the feedback and each disposition in a dated review before changing anything.

### 5. Derive per-lake products

Join to the lake universe of assumption A9 by COMID. Record the recipe and the owner's authorization for the aggregation in a decision before computing.
Keep the raw pixels. Write derived tables to `data/<dataset>/derived/` as Parquet with provenance columns.

### 6. Serve

Build the user-facing dashboard to the owner's specification for that dataset. Every number on it traces to a derived table and the script that built it.

### 7. Specify for AWS

Write `docs/aws/<dataset>.md` with the contents listed in [../docs/aws/README.md](../docs/aws/README.md).

### 8. Register

Update the row in [../docs/data-registry.md](../docs/data-registry.md). Record decisions. Write the review record. Stop for owner review.

## Folder layout

```
datasets/<name>/
  README.md        run guide and status
  METADATA.md      the characterization, from _template/METADATA.template.md
  reference/       preserved primary documents and their text extractions
  access/          enumerate and pull scripts, each with --dry-run and --limit
  qaqc/            QA scripts writing outputs/qa_report.md and outputs/qa_summary.json
  viz/             review dashboard data builder
  outputs/         QA report and JSON, small PNG proofs. Tracked
  tests/           offline tests on fixtures
data/<name>/raw/      as downloaded, with manifest.jsonl. Ignored by git
data/<name>/derived/  derived tables. Ignored by git
```
