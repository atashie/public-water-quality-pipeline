# Data registry

One row per dataset. Status reflects the furthest completed step of the loop in [CLAUDE.md](../CLAUDE.md): `planned`, `characterized`, `pulled`, `checked`, `reviewed`, `derived`, `served`, `specified`.
Facts in this table cite their home. Numbers live in the probe records and the dataset METADATA files.

| Id | Dataset | Producer | Native form | Cadence and coverage | Access | Local plan | Status | Docs |
|---|---|---|---|---|---|---|---|---|
| `cyan` | CyAN cyanobacteria index `CI_cyano`, version 6.0 | NASA Ocean Biology DAAC for the EPA CyAN program | 8-bit GeoTIFF tiles and whole-region mosaics, 300 m, EPSG:5070 | Daily and 7-day maximum composites, contiguous United States and Alaska, 2016 onward with MERIS 2008 to 2012 | OB.DAAC file search and download with an Earthdata token, and Earthdata Cloud S3 in region | Weekly mosaics in full plus 8 weeks of dailies, assumption A8 | derived. Per-lake table built 2026-09-23 under decision 0002, recipe confirmed | [datasets/cyan/](../datasets/cyan/README.md), [probe record](probes/2026-09-22-dataset-facts.md#cyan) |
| `clms_lwq` | Lake Water Quality 300 m, 10-daily, version 2 | Copernicus Land Monitoring Service, produced by Plymouth Marine Laboratory and Brockmann Consult | One global NetCDF per dekad, plus a cloud-optimized GeoTIFF variant, EPSG:4326 | Dekads from 2024-09 for version 2. Version 1 covers 2002 to 2012 and 2016 to 2024 | Copernicus Data Space Ecosystem OData and S3 with account credentials | Subset to lakes in the contiguous United States. Route decided in step 3 | planned | [datasets/clms_lwq/](../datasets/clms_lwq/README.md), [probe record](probes/2026-09-22-dataset-facts.md#copernicus-lake-water-quality-300-m) |
| `epa_cyanohab_forecast` | Experimental weekly cyanoHAB forecast | US EPA Office of Research and Development | Per-lake, per-week table inside three Qlik dashboards | Weekly, Sunday to Saturday, April to November, about 2,200 lakes. Dashboards keep about two seasons | Unofficial Qlik engine extraction, no official API, assumption A12 | Snapshot the whole table weekly | planned | [datasets/epa_cyanohab_forecast/](../datasets/epa_cyanohab_forecast/README.md), [probe record](probes/2026-09-22-dataset-facts.md#epa-cyanohab-forecast) |

| `cyan_lakes` | CyAN resolvable-lakes shapefile and tile grid | NASA Earthdata CyAN project page | Two zipped shapefiles, EPSG:5070 | Static. 2,321 lakes keyed by COMID, 54 tiles | Public URLs, no login | Pulled in full | checked. Pulled and QA'd 2026-09-23 | [datasets/cyan_lakes/](../datasets/cyan_lakes/README.md) |

The `cyan_lakes` row is the lake universe of assumption A9 and the COMID backbone of assumption A20.
