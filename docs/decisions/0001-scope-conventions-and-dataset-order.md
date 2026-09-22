# 0001. Scope, conventions, dataset order, and the per-dataset loop, 2026-09-22

Status: active.

## Context

The owner started this repository on 2026-09-22 to ingest, QA/QC, process, and serve open water-quality data.
The GitHub remote already existed with one commit holding a one-line README.
Before initialization, the implementer reviewed the owner's HAB_PoC dashboard, its data-source layer, and the Sentinel-2 assessment repository's review workflow and presentation.
The implementer then ran read-only checks against the three providers and asked eleven questions, each with a recommended default.
The owner accepted every default on 2026-09-22 and confirmed that the credentials exist. Those answers are the authority for the `sourced` rows in [assumptions.md](../assumptions.md).

## Decision

- Scope is ingestion, QA/QC, processing, and serving of open water-quality data. The first three datasets are CyAN, the Copernicus Lake Water Quality 300 m product version 2, and the EPA experimental cyanoHAB forecast. Assumption A1.
- Validation of facts comes first. Claims carry a status. A research agent and a separate checking agent confirm each documented claim. Assumption A2.
- Every dataset is reviewed by the owner on a generated dashboard before use. Assumption A3.
- Each dataset serves two purposes. One is a local store with a user-facing dashboard when it fits. The other is a high-level AWS design with costs for the engineering team. Assumptions A4 and A16.
- Conventions mirror the Sentinel-2 and weather assessment repositories, including the owner-gated workflow, Codex participation, plain English, claim statuses, and pinned tooling. Assumption A5.
- Layout is one folder per dataset plus shared helpers and top-level tests. Assumption A6.
- Dataset order is CyAN, EPA forecast, Copernicus. Forecast snapshots start as soon as the forecast module is verified, because the dashboards keep about two seasons. Assumption A7.
- CyAN local scope is the weekly contiguous-United-States mosaic record from 2016 plus daily files for the most recent 8 weeks. MERIS is deferred. Assumption A8.
- The CyAN resolvable-lakes shapefile keyed by COMID is the lake universe for per-lake products. Assumption A9.
- Copernicus version 2 comes first. Version 1 is a separate stream with its method break documented. Assumption A11.
- The EPA forecast's unofficial Qlik extraction is reused locally as research-grade. The owner decides on requesting a supported feed before AWS automation. Assumption A12.
- Review dashboards are static HTML with vendored libraries, served from `docs/` on Vercel. Assumption A13.
- The AWS region is us-west-2. Assumption A14.
- The repository can become public. Assumption A15.
- Every dataset follows the eight-step loop in [CLAUDE.md](../../CLAUDE.md): characterize, pull, QA/QC, review dashboard, derive, serve, specify for AWS, register.
- The sequence of work is in [work-plan.md](../work-plan.md). Step 0 is this initialization.
- Recorded on the owner's answers of 2026-09-22 to the initialization review: no dated milestones, assumption A18. COMID is the master key with a spatial crosswalk for Copernicus lakes, assumption A20. Scope is the contiguous United States first, assumption A21.

## Consequences

- Code from the HAB_PoC repository is ported with tests, not copied blind. Its METADATA facts stay `unverified` here until rechecked against primary pages.
- The facts checked on 2026-09-22 live in one probe record. They are `probe`, not `documented`, until a second agent checks them.
- The Copernicus product cannot be stored locally as delivered. Its subsetting route is a discovery question with measured options before any bulk pull.
- No dashboard, deployment, or pull exists on 2026-09-22.

## Review triggers

- The owner changes the dataset list, the lake universe, the local storage limit, or the AWS region.
- Step 1 finds that the CyAN weekly record no longer fits under the local limit.
- Step 3 finds that no Copernicus subsetting route is practical.
- The EPA forecast access path breaks or an official feed appears.
- The owner extends the scope beyond the contiguous United States. COMID is a United States identifier, assumptions A20 and A21. A project-internal lake id with crosswalks becomes the candidate.
