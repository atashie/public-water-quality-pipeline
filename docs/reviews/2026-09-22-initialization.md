# Initialization: conventions, assumptions, decision 0001, probe record, dataset skeletons, shared helper with tests, 2026-09-22

Implementer: Claude Code (AI coding agent), directed by the repository owner. Scope: step 0 of [the work plan](../work-plan.md). Nothing was committed or pushed.

## What the owner directed

The owner's brief of 2026-09-22 set three guidelines. Validation of facts comes first. The owner reviews every new dataset on a generated dashboard. Each dataset serves local use and a high-level AWS design.
The implementer reviewed the HAB_PoC dashboard and data-source layer and the Sentinel-2 assessment repository. It ran read-only probes against the three providers. It asked eleven questions with defaults.
The owner accepted every default and confirmed that the credentials exist. [Decision 0001](../decisions/0001-scope-conventions-and-dataset-order.md) and [assumptions.md](../assumptions.md) record the result.

## What changed

| Area | Change |
|---|---|
| Repository | Cloned from the existing remote, which held one commit with a one-line README |
| Tooling | `pyproject.toml` with a `dev` group and a `datasets` group, `uv.lock`, Python 3.12.13, ruff, pytest, CI workflow, `.gitignore`, `.env.example`, MIT license |
| Agent guidance | `CLAUDE.md`, `AGENTS.md`, rules for documents and dataset folders, the `check` skill, permissions that deny reading `.env` |
| Documents | Assumptions A1 to A20, decision 0001, work plan, data registry with three planned rows, probe record of 2026-09-22, AWS note outline, this review |
| Datasets | `datasets/README.md` with the eight-step loop, `_template/`, three dataset skeletons with a README each, `_common/net.py` ported from the HAB_PoC repository |
| Tests | Relative links resolve, dated documents carry their date, and the shared helper's dotenv, hashing, manifest, and cached download paths on a fake HTTP adapter |

## Evidence

- The probe record lists every live check with its endpoint, parameters, and result. It marks each item `probe`, `prior`, or `unverified`.
- The shared helper keeps the HAB_PoC behavior: cached downloads, sha256 manifests, integrity states `verified`, `refetched_stale_cache`, `mismatch`, and `unverified`, and credential resolution from `.env`.
- Check results are in the section below.

## Limits

- No dataset METADATA exists yet. The probe facts await a checking agent before any of them becomes `documented`.
- The two CyAN catalogs disagreed on the newest granule. Which one the S3 bucket reflects is unresolved.
- The inner file layout of the Copernicus products is unknown without credentials.
- The count of resolvable lakes and every other HAB_PoC fact is `prior` until rechecked.
- Assumptions A18 and A20 are `unsourced`.
- No Vercel configuration, dashboard, or pull exists.

## Checks

| Check | Result |
|---|---|
| `uv lock` and `uv sync --locked` | Pass. 37 packages resolved on Python 3.12.13. The geospatial imports load |
| `uv run ruff check .` and `uv run ruff format --check .` | Pass. 27 files formatted |
| `uv run pytest -q` | 39 passed in 0.17 s. Link, date, and helper tests. No network |
| Sentence audit | Prose sentences over 25 words reworded. Quoted source text in the probe record stays verbatim and is exempt |
| Forbidden words | No "should" outside the rule that bans it. No semicolon in prose |
| Name scan | No person's name in any document. Roles only |
| Credential scan | No credential value in any tracked file. `.env` is ignored and denied |

## Authorization

The owner reviewed this record and authorized commit and push on 2026-09-22. The owner answered on A18 and A20 the same day. Both are `sourced`. A21 records the contiguous-United-States scope. The answers are in the working tree and await the next authorized commit.

## Proposed next step

Owner review of this record and the documents. Then authorization to commit and push the initialization. Then step 1a, the CyAN characterization with a research agent and a checking agent. No provider pull before the owner authorizes step 1b.
