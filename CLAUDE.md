# public-water-quality-pipeline

Ingest, QA/QC, process, and serve open water-quality data. The first three datasets derive from or train on Sentinel-3 OLCI:
the EPA and NASA CyAN cyanobacteria index, the Copernicus Land Monitoring Service Lake Water Quality 300 m product version 2,
and the EPA experimental cyanoHAB forecast. Sentinel-2, other sensors, and in situ data may follow. They are not the current priority.
`README.md` is the human overview and the document index.

## Current phase

Step 0, initialization, committed 2026-09-22 with the owner's authorization. Step 1a, the CyAN characterization, is next.
No dataset has been pulled. Start with [docs/work-plan.md](docs/work-plan.md). The facts checked on 2026-09-22 are in
[docs/probes/2026-09-22-dataset-facts.md](docs/probes/2026-09-22-dataset-facts.md). They await independent checks before any dataset METADATA calls them `documented`.

## Workflow

The owner, Codex, and Claude Code review every step. Complete one authorized step, then stop.

1. Read this file, the applicable rules, the latest review, and the relevant decisions. Preserve other contributors' changes.
2. State the step, its acceptance checks, and what is deferred.
3. Implement it with tests and documentation. Run `/check`.
4. Write a dated record under `docs/reviews/`: what changed, evidence, limits, dispositions of prior findings
   (`fixed`, `accepted and deferred`, `corrected with evidence`), and the proposed next step without starting it.
5. Stop for review. Silence, passing tests, and an AI review are not owner approval.
   Never commit, push, publish, or start the next step without the owner's explicit authorization.

Research uses a research agent and a separate checking agent per claim. Only confirmed or corrected claims enter a dataset's METADATA as `documented`.
Scripts that contact a provider run only when the owner invokes them. Codex reads [AGENTS.md](AGENTS.md), which points here.

## The loop for each dataset

Every dataset goes through the same eight steps. Each step is one authorized unit with its own review record.

1. Characterize. Write `METADATA.md` from primary sources with quotes and access dates. Preserve the sources under `reference/`. List what stays unresolved.
2. Pull. Enumerate, print a dry-run plan, then download into `data/<dataset>/raw/` with a cached, sha256-manifested downloader.
3. QA/QC the bytes. Integrity, structure, encoding, version tags, and distributions. Emit `outputs/qa_report.md` and `outputs/qa_summary.json`.
4. Review dashboard. The agent builds one static HTML page. The owner explores it and gives feedback. The feedback and its dispositions become a dated review.
5. Derive. Per-lake tables keyed by COMID on the lake universe of assumption A9. Any aggregation cites its authorization.
6. Serve. A user-facing dashboard to the owner's specification for that dataset.
7. Specify for AWS. A note under `docs/aws/` with the storage layout, schedule, compute unit, provenance fields, and cost lines from dated pricing pages.
8. Register. Update `docs/data-registry.md`, record decisions, write the review, and stop.

## Commands

```sh
uv sync --locked                          # pinned environment, Python 3.12.13
uv run pytest                             # documentation and helper tests, no network
uv run ruff check . && uv run ruff format --check .
```

Dataset commands are added here as each dataset's scripts exist. Every provider-contacting command is listed with the step that authorized it.

## Layout

| Path | What it is |
|---|---|
| `docs/` | Assumptions, decisions, reviews, probe records, work plan, data registry, AWS notes. Later the review dashboards and the engineering handoff page |
| `docs/archive/` | Ignored by git. Superseded documents kept locally until deleted. Nothing links to it |
| `datasets/` | One folder per dataset, the shared helpers in `_common/`, and the copy-me `_template/`. See [datasets/README.md](datasets/README.md) |
| `data/` | Ignored by git. `data/<dataset>/raw/` and `data/<dataset>/derived/`. Everything here regenerates from checked-in code |
| `tests/` | Documentation link and date checks, shared helper tests. No network |
| `.claude/` | Rules per path, the `check` skill, and permissions |

## Conventions

- A claim about a data source, service, or tool carries one status: `documented`, `measured`, `probe`, or `unverified`. `.claude/rules/docs.md` defines them.
- A planning assumption carries `sourced` or `unsourced`. The list is `docs/assumptions.md`. Link to it. Do not restate it.
- One fact has one home. Numbers live in probe records, result files, or dataset METADATA, not here.
- A dataset is stored locally in full only when it fits under the limit in assumption A16. Otherwise subset by scope, never by resolution.
- No aggregation without a recorded authorization, assumption A17.
- Prior repositories' code and METADATA are input. Port the code with tests. Recheck the facts against primary pages before marking them `documented`.
- Refer to colleagues by role, never by name. Do not name customers or vendors. This repository can become public, assumption A15.
- Timestamps carry a UTC offset. Dates are ISO 8601. No relative dates in documents.
- Documents use plain English and American spelling. Descriptive sentences: 25 words maximum. Procedure steps: imperative, 20 words maximum. No semicolons. No "should".
- Python: ruff, line length 100, rules `E F I B UP`. Python 3.12 for development and CI. Never install the PyPI package `datasets`.
- Do not commit anything under `data/` or `.env`. Large artifacts belong in linked storage.

## Gotchas

Each gotcha points to its home. Numbers live there, not here.

- CyAN files now sit in NASA Earthdata Cloud S3 as well as behind the OB.DAAC download endpoint. In-region reads change the AWS design. Probe record, CyAN section.
- The two CyAN catalogs disagreed on the newest granule on 2026-09-22. Do not assume the S3 bucket holds the newest composite until checked. Probe record, CyAN section.
- CyAN pixels are 8-bit codes. Zero means below detection, not missing. Land and no-data are explicit codes. There is no nodata flag. Prior CyAN METADATA in the HAB_PoC repository, to be rechecked in step 1.
- The Copernicus product is delivered as one global file per dekad of several gigabytes. It never fits the local limit as delivered. Subsetting is step 3's discovery question. Probe record, CLMS section.
- Copernicus version 2 adds chlorophyll-a, suspended matter, the cyanobacteria index, uncertainties, and flags from 2024-09. Version 1 turbidity uses a different method. Treat the versions as separate streams, assumption A11.
- The EPA forecast has no official API. The dashboards keep about two seasons. Every week not snapshotted is lost. Assumption A12 and the probe record, EPA section.
- The Copernicus manual is marked draft and states two different grid spacings. Verify the grid from a file. Probe record, CLMS section.
