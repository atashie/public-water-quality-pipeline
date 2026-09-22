# Step 1b part 1, CyAN access code, dry runs, and the cloud route measured: identical bytes, a 7-week lag, 6 absent weeks, listing refused off region, 2026-09-22

Implementer: Claude Code (AI coding agent), directed by the repository owner. Scope: step 1b of [the work plan](../work-plan.md) up to the pull. Two sample files were downloaded twice for the byte comparison. No other data file was pulled. Nothing committed.

## What the owner directed

The owner authorized step 1b on 2026-09-22 and supplied the Earthdata token for the ignored `.env`. The download of the assumption A8 scope waits for a separate authorization after the dry-run plan.

## What changed

| Area | Change |
|---|---|
| Access code | `datasets/cyan/access/cyan_api.py`: encoding constants, index conversion, filename parsing with calendar-checked day-of-year, stream collapse, file search with retry, version tag reader, cloud helpers. `pull_cyan.py`: dry run, plan summary, two routes, manifest with version tag and observed latency. `compare_routes.py`: the route comparison |
| Tests | 16 offline tests under `datasets/cyan/tests/`, including the leap-year decode, the search response forms, the plan collapse, and the presence summary. `pytest` now collects `datasets/` too |
| Evidence | Three result files under `datasets/cyan/outputs/`, described in its README. [Measurements](../measurements.md) interprets them |
| Documents | METADATA sections 2, 6, 7.3, 10, and 12 carry the measured numbers. The AWS note gains a measured section and a consequence. Run guide in the dataset README. Commands in CLAUDE.md |
| Credentials | `.env` exists with owner-only permissions and is ignored by git. No agent read it. The token expiry was decoded from its public payload: 2026-10-25 |

## Findings

1. **Route B is a byte-identical but incomplete mirror.** 529 of 560 listed weekly files are served, all in the `CYAN` stream. The two samples matched the archive by sha256. The newest served file ends 2026-08-01, 7 weeks behind. Six weekly files from the last 17 months are absent beyond the lag. Under the owner's rule, route B alone cannot be the source. [Measurement 1](../measurements.md#1-the-cloud-copy-is-a-byte-identical-but-lagging-and-incomplete-mirror-2026-09-22).
2. **Credentials are issued but listing is refused off region.** The HTTPS endpoint answers from anywhere with a token. A bucket listing needs compute inside us-west-2. That is a design constraint for step 1g.
3. **The archive lacks one week too.** The week starting 2026-07-05 is absent from the file search. Every other week from 2016-04-24 to 2026-09-13 is present. [Measurement 2](../measurements.md#2-the-archive-itself-lacks-one-weekly-file-2026-09-22).
4. **The pull plan is 542 weekly and 56 daily files, about 3.5 GB.** All in the `CYAN` stream. The 18 `CYANV6T` duplicates collapse onto their `CYAN` twins. [Measurement 3](../measurements.md#3-dry-run-plans-for-the-assumption-a8-scope-2026-09-22).

## Checks

| Check | Result |
|---|---|
| `uv run pytest -q` | 67 passed. No network |
| `uv run ruff check .` and `uv run ruff format --check .` | Pass |
| Dry runs | Weekly 560 URLs to 542 files. Daily 56 files. Zero per-satellite or other exclusions |
| Route comparison | 560 HEADs in 2 minutes 32 seconds with 8 workers. Two byte comparisons identical |
| Credential scan | No token in any tracked file or document |

## Limits

- One day of measurement. The lag and the absent files can change. A second run on a later date is planned in the AWS note.
- The presence test is a HEAD through the HTTPS endpoint. Whether the bucket lacks the files or only the endpoint's index does needs an in-region listing.
- Daily and tile files were not compared.
- No file has been opened for its encoding, projection, or version tag. That is step 1c.

## Dispositions of prior findings

| Finding | Disposition |
|---|---|
| Step 1a review, finding 1: cloud catalog lag, 8 weekly files short | Corrected with evidence. A complete series through 2026-07-26 holds 536 start dates, not 537. The archive lacks 1 and the cloud copy lacks 6 more. The probe record carries a correction line |
| Step 1a review, finding 2 and 3 | No change. The comparison used only `.tif` names and the dry run's first file starts 2016-04-24 |
| METADATA section 10, stream choice `prior` | Fixed. Measured on the dry run |

## Authorization

The owner reviewed and approved this record and the measurements on 2026-09-22, authorized commit and push, and authorized the full pull followed by step 1c.

## Proposed next step

Owner review. Then authorization to commit and push this part. Then authorization of the pull: 542 weekly and 56 daily whole-region files through the archive route into `data/cyan/raw/`, about 3.5 GB. The manifest records latency, bytes, and version tags. Then step 1c, QA/QC on the pulled files.
