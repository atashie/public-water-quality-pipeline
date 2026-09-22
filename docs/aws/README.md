# AWS notes

One note per dataset, written in the loop's step 7. Each note is a high-level design for the engineering team, not a production build.
The region is us-west-2, assumption A14. Costs come only from measurements or dated pricing pages, assumption A19.

Notes: [cyan.md](cyan.md) holds the Discovery input on the two access routes. `epa-cyanohab-forecast.md` and `clms-lwq.md` do not exist yet.

## What every note contains

1. Source and access path, with the official or unofficial status of the path.
2. Trigger and schedule, as an EventBridge rule tied to the provider's cadence and observed latency.
3. Unit of work, idempotent and keyed by the provider's product identifier and version. Retry and backfill behavior.
4. Compute unit, Lambda or Fargate, with the measured input size, memory, and time from the local pull.
5. Storage layout in one bucket: `raw/<dataset>/...` immutable and versioned, `derived/<dataset>/...`, `manifests/<dataset>/...`.
6. Provenance fields on every record: source URL, bytes, sha256, provider version tag, ingested time, available time.
7. Reprocessing detection: how a changed provider version is noticed and what is re-pulled.
8. Monitoring: a missing-object alarm per cadence and a failed-run alarm.
9. Cost lines: compute, storage, requests, transfer, and engineering effort, backfill separate from steady state, with the page and date behind each price.
10. Open questions and risks.

## Cross-cutting points to settle in step 4

- Whether NASA Earthdata Cloud in-region reads remove the CyAN download step entirely.
- Whether the Copernicus route is a full NetCDF pull per dekad or range reads of the cloud-optimized variant.
- Whether the EPA forecast is automated on the unofficial path, exported by hand, or fed by a supported feed, assumption A12.
- A shared catalog and query layer over the derived Parquet tables, if the dashboards need one.
