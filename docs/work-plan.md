# Work plan

No dated milestones exist, assumption A18 in [assumptions.md](assumptions.md). Steps run in order under the workflow in [CLAUDE.md](../CLAUDE.md).
A checked box means the work exists in this repository with evidence. Every step ends with a dated review record and an owner decision.

## Next session

The owner's answers on assumptions A18 and A20. Then step 1a. Step 1b needs an Earthdata Login token in `.env` before any download. The dry run needs none.

## How a dataset is judged

Every dataset step reports against the same criteria. The registry row summarizes them.

| Criterion | What to record |
|---|---|
| Correctness | Encoding, units, nodata and below-detection codes, projection and grid, version tag read from the file |
| Completeness | Expected, present, and missing files or records per period, and why |
| Latency | Time from the provider's window end to local availability, measured on a dated pull |
| Size | Bytes per file, files per year, total for the chosen scope, against the local limit of assumption A16 |
| Cost | Compute, storage, requests, transfer, and engineering effort for the AWS design, from measurements or dated pricing pages, assumption A19 |
| Operability | Idempotent units, retry, backfill, reprocessing detection, provider version changes |
| Terms | License, attribution, redistribution, and whether the access path is official |

## Step 0: initialize, delivered and committed 2026-09-22

- [x] Repository cloned from the existing remote. Conventions, rules, check workflow, CI, pinned environment.
- [x] Assumptions with provenance. [Decision 0001](decisions/0001-scope-conventions-and-dataset-order.md).
- [x] Probe record of the live checks run on 2026-09-22. [Record](probes/2026-09-22-dataset-facts.md).
- [x] Data registry with three planned rows. Dataset folder skeletons. Shared download helper ported from the HAB_PoC repository with offline tests.
- [x] Initialization review. [Record](reviews/2026-09-22-initialization.md).
- [x] Owner review and commit authorization, 2026-09-22.

## Step 1: CyAN

Each sub-step is one authorized unit.

- [ ] 1a. Characterize. Recheck the HAB_PoC CyAN METADATA and the probe record against primary pages with a research agent and a checking agent. Preserve the version 6 release notes under `reference/`. Resolve the catalog disagreement on the newest granule.
- [ ] 1b. Pull. Port `cyan_api.py` and `pull_cyan.py` with tests. Dry run, then pull the weekly contiguous-United-States mosaic record from 2016 and the daily files for the last 8 weeks, assumption A8. Record latency and bytes.
- [ ] 1c. QA/QC. Port `qa_cyan.py`. Integrity against the manifest, grid and projection consistency, version tags, code composition per file.
- [ ] 1d. Review dashboard. One page: national map of a selected week at native resolution, composition over time, and per-file QA. Owner review recorded.
- [ ] 1e. Derive. Pull the resolvable-lakes shapefile, verify its count, and build the per-lake weekly table with the recorded recipe. Authorization for the aggregation recorded in a decision.
- [ ] 1f. Serve. User-facing dashboard to the owner's specification. The HAB_PoC "current active blooms" view is the reference.
- [ ] 1g. AWS note. In-region read from the Earthdata Cloud bucket, weekly schedule, Lambda unit, provenance, backfill, reprocessing watch, costs from dated pages.
- [ ] 1h. Register and review.

## Step 2: EPA cyanoHAB forecast

- [ ] 2a. Characterize. Recheck the HAB_PoC forecast METADATA. Confirm the three dashboard applications and their identifiers. Preserve the 2024 paper's method summary and the 2025 evaluation abstract under `reference/`.
- [ ] 2b. Pull. Port the Qlik extraction client and the snapshot script with the offline fixture tests. Dry run, then one full snapshot. Start weekly snapshots once verified, assumption A7.
- [ ] 2c. QA/QC. Row count against the reported size, Saturday cadence, lake count, value range, revisions between snapshots.
- [ ] 2d. Review dashboard. Per-lake map of the current week and a sentinel-lake time series. Owner review recorded.
- [ ] 2e. Derive. Current view and revision log keyed by COMID and week.
- [ ] 2f. Serve. To the owner's specification.
- [ ] 2g. AWS note. Weekly schedule, the unofficial-access risk stated, the manual export alternative, and the owner's decision on requesting a supported feed, assumption A12.
- [ ] 2h. Register and review.

## Step 3: Copernicus Lake Water Quality 300 m

- [ ] 3a. Characterize. Product user manual, product pages, release news, and the catalogue listing, with a research agent and a checking agent. Resolve the grid spacing from a file. Count the lakes inside the contiguous United States.
- [ ] 3b. Discovery of access routes, measured on one dekad. Compare a full NetCDF download with a local crop, range reads from the cloud-optimized variant over S3, and any server-side subsetting the platform offers. Report bytes, requests, time, and completeness. Record the inner file layout of both product variants.
- [ ] 3c. Decision on the subsetting route and the local scope. Version 2 first, assumption A11.
- [ ] 3d. Pull, QA/QC, review dashboard, derive, serve, AWS note, register. Same pattern as step 1.
- [ ] 3e. Version 1 archive as a separate stream, with the method break documented and the 2024-09 to 2024-10 overlap compared.

## Step 4: engineering handoff

- [ ] Inventory JSON of the three AWS notes with claim bindings. A checked-in renderer with a `--check` mode renders it to one HTML page.
- [ ] Cost model per dataset with backfill and steady state separated. Prices only from dated pages, assumption A19.
- [ ] Vercel configuration for `docs/` and a hosting note, following the Sentinel-2 repository's pattern. First deployment after owner authorization.
- [ ] Engineering review with the platform team.

Later datasets, Sentinel-2 and in situ sources, are out of scope until the owner adds them, assumption A1.
