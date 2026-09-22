# CyAN catalogs, cloud lag, and reference documents, 2026-09-22

Probes by the parent agent, Claude Code, directed by the repository owner, at the start of step 1a. Read-only catalog queries. One documentary PDF downloaded. No data file pulled.

## Release notes preserved

- `https://oceancolor.gsfc.nasa.gov/images/cyan/version/6/CyAN_NASA_MERISOLCI_CI_release_notes_V6_Aug_2025.pdf` returned HTTP 200, `application/pdf`, 1,929,326 bytes, sha256 `e48b56a192215394c74cad3429d3dd3d07ca2cae714dffcc5f5b807edf154f99`. Identical to the HAB_PoC repository's copy of 2026-07-01. Preserved under `datasets/cyan/reference/` with a 31-page text extraction. `probe`

## The Earthdata Cloud catalog lags the OB.DAAC file search

All queries against the NASA Common Metadata Repository, collection `C3416412382-OB_CLOUD`, on 2026-09-22.

- Exact-name lookup for `L20262562026262.L3m_7D_CYAN_CI_cyano_CYAN_CONUS_300m.tif`, the newest weekly composite in the file search: 0 matches. `probe`
- Granules with a start date on or after 2026-08-02: `cmr-hits: 0`. `probe`
- Newest four weekly whole-region granules by start date: `L20262072026213` for 2026-07-26 to 2026-08-01 at 5.89 MB, then the weeks starting 2026-07-19, 2026-07-12, and 2026-06-28. The week starting 2026-07-05 is absent from that list. `probe`
- Earliest granules: `L2016116.L3m_DAY_...` daily items with start 2026-04-25, both the whole region and tile `1_1`. `probe`
- Counts by name pattern: 529 weekly whole-region granules, 3,742 daily whole-region granules. `probe`
- The OB.DAAC file search on the same day lists weekly composites through `L20262562026262`, 2026-09-13 to 2026-09-19, and daily composites through `L2026264`, 2026-09-21. `probe`
- Conclusion: on 2026-09-22 the cloud catalog's newest item is 7 weeks older than the file search's. The catalog holds 529 weekly whole-region files through 2026-08-01, where a complete weekly series from 2016-04-24 would hold 537. Whether the S3 bucket itself lags or only the catalog index lags is unknown without credentials. Step 1b checks the bucket with a token. `unverified`

## Neighboring collections in the same provider

Keyword search `CYAN` under provider `OB_CLOUD`:

- `C3416412319-OB_CLOUD`, `MERIS_L3m_CYAN` 6.0, "ENVISAT MERIS Regional Mapped Cyanobacteria Index (CI) Data, version 6.0". MERIS is a separate collection from the merged OLCI one. `probe`
- `C3416412386-OB_CLOUD` and `C3416412340-OB_CLOUD`, the true-color companions for OLCI and MERIS. `probe`
- Eleven Inland Waters collections, `ILW` 5.0, at levels 2, 3 binned, and 3 mapped, for OLCI-A, OLCI-B, merged, and MERIS. Not assessed. `probe`

## Lake shapefile

- `HEAD https://www.earthdata.nasa.gov/s3fs-public/2026-01/MERIS_OLCI_Lakes.zip`: HTTP 200, `application/zip`, 32,822,913 bytes, `last-modified` 2026-01-07T18:50:32Z. Not downloaded. Step 1e pulls it. `probe`
