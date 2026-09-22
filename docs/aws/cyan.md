# AWS note for CyAN, Discovery stage, 2026-09-22

Status: Discovery input only. The design is step 1g of [the work plan](../work-plan.md). Nothing here is selected.

## Two access routes

| Route | What it is | Status on 2026-09-22 |
|---|---|---|
| A. OB.DAAC archive | Enumerate with `cyan_file_search`, download through `getfile` over HTTPS with an Earthdata token. Runs from any region and pays internet transfer | The route the HAB_PoC repository used. Newest weekly composite 2026-09-19, newest daily 2026-09-21. [Probe](../probes/2026-09-22-cyan-catalogs.md) |
| B. Earthdata Cloud S3 | Read `s3://ob-cumulus-prod-public/` in us-west-2 with one-hour temporary credentials. No download step, no transfer charge in region | The cloud catalog holds nothing newer than 2026-08-01 and 529 weekly whole-region files where a complete series holds 537. [Probe](../probes/2026-09-22-cyan-catalogs.md) |

## The owner's rule, 2026-09-22

Prefer route B if its data are identical to route A's. A bucket that lags or lacks files changes that preference. The finding above is therefore a Discovery input, recorded before any design.

## What decides it, step 1b

1. List the bucket with a token and compare the file set to the file search listing for the same period. Report missing files and the newest date on each side.
2. Compare the bytes of a sample of files present on both routes. Identical sha256 means identical data.
3. Repeat the newest-date comparison on a second date to separate a one-day lag from a standing one.
4. Record the outcome in a decision. Options: B alone, A alone, or A for the newest weeks with B for the archive.

## Measured on 2026-09-22

[Measurement 1](../measurements.md#1-the-cloud-copy-is-a-byte-identical-but-lagging-and-incomplete-mirror-2026-09-22) ran the comparison above from the owner's laptop.

- Bytes are identical where both routes hold a file. Two of two samples matched by sha256.
- Route B trails route A by 7 weeks and lacks 6 weekly files from the last 17 months. Route A itself lacks the week starting 2026-07-05.
- Route B holds only the `CYAN` name stream. The 18 `CYANV6T` duplicates are absent, with no data lost.
- Credentials are issued to any Earthdata user, but listing the bucket from outside us-west-2 is refused. The HTTPS endpoint of route B answers from anywhere with a token.

Consequence under the owner's rule: route B alone cannot be the source. It is not identical to route A. The candidates for step 1g are route A alone, or route A for freshness and gaps with route B for in-region bulk reads. A second measurement on a later date tells whether the 6 absent files ever arrive.

## Open questions for the design

- Whether the 6 absent files and the 7-week lag sit in the bucket or only in the endpoint's index. A listing from inside us-west-2 answers it.
- Whether the lag is constant. Repeat the comparison on a later date.
- How a reprocessing appears on each route, and how a version watch detects it.
