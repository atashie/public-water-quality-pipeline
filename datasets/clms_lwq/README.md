# clms_lwq: Copernicus Lake Water Quality 300 m, version 2

Status: planned. Step 3 of [the work plan](../../docs/work-plan.md). No file pulled.

What it is: ten-day composites for more than 4,000 lakes worldwide, from Sentinel-3 OLCI. The variables are turbidity, chlorophyll-a, suspended matter, trophic state, a floating cyanobacteria index, water-leaving reflectances, uncertainties, and quality flags. The Copernicus Land Monitoring Service produces it and the Copernicus Data Space Ecosystem distributes it.
Facts checked on 2026-09-22 are in the [probe record](../../docs/probes/2026-09-22-dataset-facts.md#copernicus-lake-water-quality-300-m). They are not yet `documented`.

## Why this dataset needs discovery first

Each dekad is delivered as one global file of several gigabytes, in a NetCDF variant and a cloud-optimized GeoTIFF variant. The full record does not fit the local limit of assumption A16.
Step 3b measures the subsetting routes on one dekad before any bulk pull. The routes are a full NetCDF download with a local crop, and range reads of the cloud-optimized variant over S3. Any server-side subsetting the platform offers is a third route.
Version 2 begins 2024-09. Version 1 covers 2002 to 2012 and 2016 to 2024 with a different turbidity method and without chlorophyll-a, suspended matter, the cyanobacteria index, or uncertainties. Version 1 is a separate stream, assumption A11.

## Plan for this folder

- Step 3a writes `METADATA.md` with a research agent and a checking agent. Its sources are the product user manual, the product pages, the release news, the catalog attributes, and a file opened locally. It preserves the manual under `reference/`.
- Step 3b writes the route comparison under `access/` with a result file and a dated review.
- Later steps follow the loop.

No prior code exists for this dataset.
