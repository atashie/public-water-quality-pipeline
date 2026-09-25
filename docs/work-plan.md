# Work plan

No dated milestones exist, assumption A18 in [assumptions.md](assumptions.md). Steps run in order under the workflow in [CLAUDE.md](../CLAUDE.md).
A checked box means the work exists in this repository with evidence. Every step ends with a dated review record and an owner decision.

## Next session

Step 1f approved and committed 2026-09-23 after five rounds of feedback, and deployed on Vercel the same day, [hosting note](vercel-hosting.md). On 2026-09-25 a scientist's feedback led the owner to put a revision of 1f ahead of 1g. Part 1, the record and plan, is approved, [record](reviews/2026-09-25-cyan-lake-dashboard-scientist-feedback.md). Part 2, the page changes, is committed, [record](reviews/2026-09-25-cyan-lake-dashboard-revision-part-2.md). Part 3, what the index means and the SFEI survey, is committed, [record](reviews/2026-09-25-cyan-lake-dashboard-revision-part-3.md). The owner authorized a push of parts 2 and 3 on 2026-09-25, which redeploys the Vercel site. Part 4 awaits the owner's authorization. Then 1g, the AWS note for CyAN, and a Codex check of the probe record on the EPA and Copernicus assertions. Step 1b needs an Earthdata Login token in `.env` before any download. The dry run needs none.

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

- [x] 1a. Characterize, delivered 2026-09-22, owner review pending. 100 claims from 17 primary sources, researched and independently checked. Release notes preserved. The catalog disagreement is a measured 7-week lag of the cloud catalog. [Record](reviews/2026-09-22-cyan-characterization.md), [METADATA](../datasets/cyan/METADATA.md).
- [x] 1b, part 1, delivered and approved 2026-09-22. `cyan_api.py`, `pull_cyan.py`, and `compare_routes.py` ported or written with 16 offline tests. Dry runs: 542 weekly and 56 daily files. Route comparison measured, [measurements](measurements.md). [Record](reviews/2026-09-22-cyan-route-comparison-and-dry-run.md).
- [x] 1b, part 2, done 2026-09-22. 542 weekly and 56 daily whole-region files pulled through the archive route, 3.35 GB, no failure. [Measurement 4](measurements.md#4-the-assumption-a8-pull-598-files-335-gb-no-failure-newest-weekly-file-3-days-old-at-retrieval-2026-09-22).
- [x] 1c, delivered 2026-09-22, corrected after two independent Codex reviews the same day, approved by the owner. `qa_cyan.py` with tests, run on all 598 files against the approved plans. [Record](reviews/2026-09-22-cyan-pull-and-qa.md).
- [x] 1d, delivered and approved 2026-09-23 after the owner's exploration and two rounds of feedback. One offline page: native 300 m frames for eight review windows over every pulled file, the national record, the QA table, and provenance. [Record](reviews/2026-09-23-cyan-review-dashboard.md), [page README](dashboards/cyan/README.md).
- [x] 1e part 1, done 2026-09-23. Lake and tile shapefiles pulled and checked: 2,321 lakes, 2,321 distinct COMID. [Measurement 6](measurements.md#6-the-cyan-resolvable-lakes-shapefile-2321-lakes-keyed-by-comid-2026-09-23). Recipe recorded in [decision 0002](decisions/0002-per-lake-table-recipe.md), owner confirmation pending.
- [x] 1e part 2, delivered and approved 2026-09-23. Recipe confirmed. 1,387,958 rows for 2,321 lakes in 87 seconds. [measurement 7](measurements.md#7-the-per-lake-table-1387958-rows-for-2321-lakes-under-decision-0002-2026-09-23). [Record](reviews/2026-09-23-cyan-lake-table.md).
- [x] 1f, delivered, approved, and committed 2026-09-23 after five rounds of feedback. One offline page over the per-lake table: a map of every lake's state in any of the newest 104 weeks with a movable bloom line and coverage control, a ranked list, a per-lake deep dive over the whole record, and provenance. The companion attribute table with centroids, windows, and interior cell indices. Names for 2,230 of 2,321 lakes by a GNIS crosswalk after the owner's first feedback. After the second round: FAQ dropdown, three-panel map with continent outlines, filters by state and status, newest-week pixel overlays, no provenance tab. [Record](reviews/2026-09-23-cyan-lake-dashboard.md), [page README](dashboards/cyan-lakes/README.md), [measurement 8](measurements.md#8-the-lake-dashboard-data-2321-lakes-the-newest-104-weeks-on-one-page-2026-09-23).
- [x] Hosting, 2026-09-23. The per-lake files committed once, a `vercel.json`, and the [hosting note](vercel-hosting.md) with the owner's steps. [Record](reviews/2026-09-23-cyan-lakes-hosting.md).
- [ ] 1f revision, after a scientist's feedback of 2026-09-25. Each part is one authorized unit. [Record](reviews/2026-09-25-cyan-lake-dashboard-scientist-feedback.md).
  - [x] Part 1, delivered 2026-09-25, corrected after a Codex review, and approved the same day. Feedback, dispositions, the hosting analysis for historical pixels, the baseline question, [measurement 12](measurements.md#12-the-whole-weekly-record-of-per-lake-pixel-images-what-it-costs-in-bytes-2026-09-24), and a Codex review request.
  - [x] Part 2, delivered 2026-09-25, corrected after a Codex review, and committed on the owner's authorization the same day. Bloom duration, the heat scale by default, a slider for the bloom line, US states and sorting, coverage per week by class, a year-over-year plot, and weeks the reader compares. [Record](reviews/2026-09-25-cyan-lake-dashboard-revision-part-2.md), [decision 0003](decisions/0003-comparisons-across-time.md), [measurement 13](measurements.md#13-zero-medians-and-land-coded-lake-pixels-in-the-weekly-record-2026-09-25).
  - [x] Part 3, delivered 2026-09-25, corrected after two Codex passes and two verifications of the commit, committed and pushed on the owner's authorization the same day. What the index means, researched by an agent and checked by Codex, estimates and named levels on the page, the single-satellite years, and a survey of the SFEI map through its documentation. [Record](reviews/2026-09-25-cyan-lake-dashboard-revision-part-3.md), [probe record](probes/2026-09-25-sfei-fhab-survey.md), [measurement 14](measurements.md#14-weekly-lake-coverage-by-year-before-and-after-the-second-satellite-2026-09-25).
  - [ ] Part 4. Historical pixel images on Vercel, option B chosen by the owner on 2026-09-25: the newest 52 weeks and one week per month back to 2016. Stepping through time, and the compared weeks as pixel maps.
  - [x] Part 5, a baseline, replaced on 2026-09-25 by decision 0003: the reader chooses the weeks, and nothing is computed across them.
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

- [ ] 3a. Characterize. Product user manual, product pages, release news, and the catalog listing, with a research agent and a checking agent. Resolve the grid spacing from a file. Count the lakes inside the contiguous United States.
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

## Candidates, not scheduled

Ideas the owner has put on hold. Each waits for a specific request from a user.

- Lake dashboard features S3 and S5 to S9 from the survey of the SFEI map, held on 2026-09-25. The list, with what each would need, is in [the probe record](probes/2026-09-25-sfei-fhab-survey.md#candidate-features-for-the-lake-dashboard).
