# Probe records

Dated records of live, read-only checks the parent agent ran against a provider's catalog, page, or endpoint.
A probe is evidence of what a provider returned on that date. It is not independently checked and not a measurement by a checked-in script.
A dataset METADATA claim may cite a probe as `probe`. It becomes `documented` only after a checking agent confirms it against the primary page.

| Date | Record | What it covers |
|---|---|---|
| 2026-09-22 | [Dataset facts checked before initialization](2026-09-22-dataset-facts.md) | CyAN catalogs and cloud bucket, Copernicus catalogue listing and manual, EPA forecast page and evaluation abstract |
| 2026-09-22 | [CyAN file format and OLCI start date confirmed by probes](2026-09-22-cyan-format-and-start.md) | Granule-level metadata, file search listings, unauthenticated HEAD requests, release-notes quotes, decoded earliest OLCI dates |
| 2026-09-23 | [Six assertions contrasting EPA CyAN and Copernicus Lake Water Quality, checked against primary sources](2026-09-23-cyan-vs-clms-assertions.md) | The CyAN index bands and the cells-per-millilitre conversion, the Copernicus version 2 variables including the floating cyanobacteria index, and the Lakes_cci variables through version 3.0.0 |
| 2026-09-23 | [The EPA forecast code deposit read for its bloom recipe](2026-09-23-epa-forecast-code-deposit.md) | The official R code: pixels wholly inside the polygon, median of 130 as the bloom flag, codes above 253 dropped, ice and mixed-pixel masks this repository does not apply |
| 2026-09-22 | [CyAN catalogs, cloud lag, and reference documents](2026-09-22-cyan-catalogs.md) | Release notes preserved, the Earthdata Cloud catalog 7 weeks behind the file search, neighboring collections, lake shapefile header |
