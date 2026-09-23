# Dataset facts checked before initialization, 2026-09-22

Probes by the parent agent, Claude Code, directed by the repository owner. Read-only requests to public catalogs and pages. No file downloaded, except the Copernicus product user manual PDF.
Every item carries `probe` unless marked `documented`. Independent checks are step 1a, 2a, and 3a work.
Prior facts from the owner's HAB_PoC repository are marked `prior`. They are input, not evidence, until rechecked.

## CyAN

### Catalog and cloud hosting

- NASA Common Metadata Repository, collection `C3416412382-OB_CLOUD`, queried with `page_size=1`. Header `cmr-hits: 290636`. `probe`
- The three newest granules by start date were daily items for 2026-08-01: `L2026213.L3m_DAY_CYAN_CI_cyano_CYAN_CONUS_300m_1_1.tif`, `..._1_3.tif`, and the whole-region file `L2026213.L3m_DAY_CYAN_CI_cyano_CYAN_CONUS_300m.tif`. `probe`
- Granule sizes from the same query: whole-region daily mosaic 4.53 MB, tile `1_1` 0.135 MB, tile `1_3` 0.126 MB. `probe`
- Each granule carries two data links: `https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/<file>` and `s3://ob-cumulus-prod-public/<file>`. `probe`
- The Earthdata catalog page for the collection lists the title "Merged Sentinel-3A and Sentinel-3B OLCI Regional Mapped Cyanobacteria Index (CI) Data, version 6.0". It lists short name `MERGED_S3_OLCI_L3m_CYAN` and DOI `10.5067/MERGED-S3/OLCI/L3M/CYAN/CI/6.0`. It lists the temporal range "2016-04-25 to Present", processing level 3, and file format "netCDF-4". The granule links end in `.tif`. The format statement and the links disagree. `probe`
- The OB.DAAC credentials README is at `https://obdaac-tea.earthdatacloud.nasa.gov/s3credentialsREADME`. It states: "The credentials dispensed from the `/s3credentials` endpoint are valid for **1 hour**." It describes "temporary credentials for same-region, read-only, direct S3 access." The page does not name the region. `probe`
- NASA's general Earthdata Cloud guidance, as summarized by the NSIDC access guide, restricts direct S3 access to us-west-2. `unverified` for the OB.DAAC bucket until read from an OB.DAAC page or tested.

### File search endpoint

- `POST https://oceandata.sci.gsfc.nasa.gov/api/cyan_file_search` with `region=1&period=1&product=1&areaids=all&sdate=2026-08-01&edate=2026-09-22&addurl=1&results_as_file=1&wgetflag=1` returned seven weekly whole-region files. The newest is `L20262562026262.L3m_7D_CYAN_CI_cyano_CYAN_CONUS_300m.tif`, days 256 to 262 of 2026, which is 2026-09-13 to 2026-09-19. `probe`
- On 2026-09-22 that is 3 days after the window end. `probe`
- The catalog's newest granule, 2026-08-01, is 7 weeks older than the file search's newest composite. Which store the S3 bucket reflects is unresolved. Step 1a resolves it. `unverified`

### Prior facts from the HAB_PoC repository, access 2026-07-01

All `prior`. Recheck in step 1a.

- Pixel codes: 0 below detection, 1 to 253 valid, 254 land, 255 no data. No nodata flag in the GeoTIFF. Index formula `CI = 10 ** (DN * 0.011714 - 4.1870866)`.
- Distributed tiles are 300.0 m in EPSG:5070. A contiguous-United-States tile is 2,000 by 2,000 pixels. The whole-region mosaic is 26,328 by 15,138 pixels.
- The full weekly whole-region record covers MERIS 2008 to 2012 and OLCI 2016-04-24 onward. On 2026-07-01 it was 752 files and 4.04 GB, with per-file sizes of 3.7 to 8.4 MB.
- Both `CYAN` and `CYANV6T` streams appear. The `OBPG_version` tag read from the file was `6.0` for `CYAN` and `6T` for `CYANV6T`. The whole record is version 6.
- The producer reprocesses the record every 10 to 16 months.
- Downloads from the OB.DAAC need an Earthdata Login token or AppKey. Search needs no login.
- Resolvable-lakes shapefile: `https://www.earthdata.nasa.gov/s3fs-public/2026-01/MERIS_OLCI_Lakes.zip`, file `updatedValidLakes.shp`, 2,321 valid lakes in the contiguous United States, keyed by COMID, accessed 2026-07-02.

## Copernicus Lake Water Quality 300 m

### Catalog listing

Copernicus Data Space Ecosystem OData catalog, filter `contains(Name,'LWQ300') and Collection/Name eq 'CLMS'`, paged in full on 2026-09-22.

- 1,472 products in all: 736 dekads, each as a `_nc` product and a `_cog` product. `probe`
- Version spans and median product sizes, decimal gigabytes: `probe`

| Name suffix | Products | First dekad | Last dekad | Median NetCDF | Median COG |
|---|---|---|---|---|---|
| MERIS, no version token, `V1.3.0` in the name | 356 per variant | 2002-05-11 | 2012-04-01 | 1.42 GB | 2.52 GB |
| `OLCI_V1.3.0` | 133 per variant | 2016-04-21 | 2019-12-21 | 4.20 GB | 4.00 GB |
| `OLCI_V1.4.0` | 174 per variant | 2020-01-01 | 2024-10-21 | 2.95 GB | 4.20 GB |
| `OLCI_V2.0.0` | 17 per variant | 2024-09-01 | 2025-02-11 | 2.04 GB | 7.97 GB |
| `OLCI_V2.0.1` | 37 per variant | 2025-02-21 | 2026-02-21 | 2.90 GB | 4.12 GB |
| `OLCI_V2.1.1` | 19 per variant | 2026-03-01 | 2026-09-01 | 3.17 GB | 4.21 GB |

- Versions 1.4.0 and 2.0.0 overlap from 2024-09-01 to 2024-10-21. `probe`
- Newest product: `c_gls_LWQ300_202609010000_GLOBE_OLCI_V2.1.1`, dekad 2026-09-01 to 2026-09-10. NetCDF 3,677,632,115 bytes. COG 4,634,663,026 bytes. Attribute `productDeliveryDate` 2026-09-17T10:54:50Z, 7 days after the dekad end. `probe`
- S3 path pattern: `/eodata/CLMS/bio-geophysical/lake_water_quality/lwq-nrt_global_300m_10daily_v2/2026/09/01/<name>`. `probe`
- Attributes on the newest COG product: `processingCenter` "Plymouth Marine Laboratory", `platformShortName` "SENTINEL3A,SENTINEL3B", `datasetIdentifier` `lwq-nrt_global_300m_10daily_v2`, `productVersion` `v2.1.1`, `gridLabel` `300m`, footprint the whole globe. `probe`
- Listing the files inside a product with the `Nodes` endpoint returned HTTP 301 without credentials. The inner layout of the NetCDF and COG variants is unknown. Step 3b records it. `unverified`
- A 100 m product from Sentinel-2 MSI exists beside it, `c_gls_LWQ100_..._GLOBAL_MSI_V2.2.2`, NetCDF 1.64 GB and COG 8.69 GB for the same dekad. Out of scope, assumption A1. `probe`

### Product pages and release note

- Version 2 product page, DOI `https://doi.org/10.2909/801137b8-9575-43ef-a073-140b663cc61c`. Title "Lake Water Quality 2024-present (raster 300 m), global, 10-daily – version 2". Sensor Sentinel-3 OLCI, projection EPSG:4326. Latency "Within 3 days after the end of the synthesis period". Access through the Copernicus Browser, the OData API, S3, and a CSV file list. `probe`
- Version 1 product page, DOI `https://doi.org/10.2909/b8e48c8d-f44e-40eb-9583-4a3254c2bbb3`: "Lake Water Quality 2016-2024 (raster 300 m), global, 10-daily – version 1". `probe`
- Release news of the version 2 launch: "the NRT dekadal Lake Water Quality (LWQ) v2.0 products have been launched as of September 2024". "The NRT LWQ v2.0 products contain additional new bands to previous versions, namely, chlorophyll-a concentrations, total suspended matter (TSM) concentrations, a floating cyanobacteria risk index and, in the case of the 300 m product, per-pixel uncertainty estimates for chlorophyll-a and TSM." "in v2.0, turbidity is no longer derived via suspended particulate matter but by direct calculation from water leaving reflectance bands." "The NRT LWQ-300m v1.4 and NRT LWQ-100m v1.5 products shall be discontinued from November 2024 onwards." `probe`
- Data Space S3 documentation: endpoint `https://eodata.dataspace.copernicus.eu/`, keys from the S3 keys manager after registration, examples for access "from an external infrastructure". No quota stated on that page. `probe`

### Product user manual, version 2.0.0, issue I1.01, 2024-07-24

Downloaded from the technical library on 2026-09-22 and text-extracted. The title page reads "draft – pending review". To be preserved under `datasets/clms_lwq/reference/` in step 3a. `probe`

- "provides an optical characterisation of more than 4200 inland waterbodies". "Since version 1.3.0 of the processing chain, the set of lakes has been extended to 4,265 waterbodies to a total of 2,166,023 km2. The included waterbodies span a surface size range of 0.11 to 379,446 km2."
- Dekads: "periods of nominally ten and varying from eight to eleven days, defined to start on days 1, 11 and 21 of each month".
- Grid: "pixel size at 300m: 0.25/112°", "global grid size at 300m: 161280 columns, 80640 lines", and "0.0022° (nominally 300m)". Section 4.5.1 instead says "mapped to a global 0.0026° grid". The two statements disagree. Verify from a file.
- File naming: `c_gls_<Acronym>_<YYYYMMDDHHmm>_<AREA>_<SENSOR>_<Version>.<EXTENSION>`, example `c_gls_LWQ300_200504010000_GLOBE_OLCI_V2.0.nc`. Format "netCDF CF1.8". Collection identifier `clms_global_lwq_300m_v2_10daily-nrt_netcdf`. The catalog names above carry a `_nc` or `_cog` suffix instead of an extension.
- Observation bands: `num_obs`, `first_obs`, `last_obs`. Constituent bands: `turbidity_mean`, `chla_mean`, `chla_uncertainty`, `tsm_mean`, `tsm_uncertainty`. Reflectance bands: `Rw400_rep` through `Rw1020_rep` at 17 wavelengths, `Rw_relative_uncertainty`, `Rw_relative_uncertainty_unbiased`, `RwDayNum_rep`. Index bands: `trophic_state_index`, `floating_cyanobacteria`. Coordinates and flags: `lat`, `lon`, `time`, `crs`, `quality_flags`.
- `floating_cyanobacteria`: "range of values from 0 to 1 indicating probability of cyanobacteria presence".
- `trophic_state_index`: values 0 to 100 in steps of 10 after Carlson 1977. 60 to 80 eutrophic, 80 to 100 hypereutrophic.
- Quality flags: `bright_pixels`, `cloud`, `snow_ice`, `l1_invalid`, `land`, `land_contaminated`, `atmospheric_correction_failure`, `turbidity_invalid`, `chla_invalid`, `tsm_invalid`, `floating_cyanobacteria`, `floating_macrophytes_or_mixed_pixel`. "Flags raised in this variable do not indicate a degradation in the quality of the final aggregated pixel, but a reduction in the number of input observations".
- Aggregation: "Mean values (arithmetic averages) in each spatiotemporal bin", reflectance is the "most representative spectrum" by lowest root-mean-square difference to the median.
- Version compatibility. "reflectance and trophic state products found in Copernicus products v1.4.0 and v2.0 are fully compatible." "Turbidity equivalent to v1.4.0 can be obtained in v2.0 by applying the following scaling factor to TSM: Turbidity = TSM * 1.17."
- Processing chain Calimnos version 2.0. Polymer 4.14 for atmospheric correction. IdePix 7.0.5 for pixel identification. 13 optical water types plus 2 for land adjacency. Maximum Peak Height for floating cyanobacteria.
- Limitations quoted: "systematic underestimation of water-leaving reflectance is apparent in the current product version, particularly for highly turbid lakes". "Users interested in lake averages rather than maps are advised to mask a buffer of one or more pixels from shorelines".
- Latency. "The products from the NRT service are available 3 days after the last acquisition of the respective dekad period." The catalog's delivery date above shows 7 days for the newest dekad.
- Citation requirement: "Copernicus Service information [Year]" or "Contains modified Copernicus Service information [Year]", plus the Calimnos credit sentence in section 4.5.4.
- Planned: "A future version 3.0 is anticipated for 2025". The catalog holds no version 3 product on 2026-09-22.

## EPA cyanoHAB forecast

- `https://www.epa.gov/habs/hab-forecasts` fetched on 2026-09-22. "Last updated on April 14, 2026". Three iframes to `https://awsedap.epa.gov/public/single/` with application ids `c98935c5-a660-41b9-b1c0-abe31e649bf7` titled "Forecast Map", `9727f5d1-11d5-4522-9a59-1835a1885159` titled "Forecast Table", and `c00e1007-19bc-48c1-9a93-2c6f54569778` titled "Forecast Trends". No CSV, API, or file link on the page. `probe`
- The same three application ids were recorded in the HAB_PoC repository on 2026-07-02. `prior`
- Research page `https://www.epa.gov/water-research/cyanobacterial-harmful-algal-blooms-forecasting-research`, last update 2026-04-03: bloom is "median lake chlorophyll a ≥12 ug/L with cyanobacteria dominance". Forecasts are valid for a "seven-day period extending Sunday through Saturday". They become available Tuesday or Wednesday. They are "typically generated from the beginning of April through November", for 2,192 lakes. "the model overpredicts positive events". `probe`
- Meyers K, Schaeffer B, Cronin-Golomb O, Salls W, Benkendorf D, Serenbetz G, Coffer M. 2025. "National forecasting of cyanobacterial harmful algal bloom events: a 3-year model evaluation". Lake and Reservoir Management 41(4). DOI `10.1080/10402381.2025.2551961`. Published 2025-09-26. Abstract via the Europe PMC API: "The 2021-2023 predictions from this model were evaluated to determine occurrence of false negative and false positive predictions to update model interpretation. In total, 331,049 events were analyzed, of which false negatives represented 1.34% and false positives 8.06% of forecasts." `probe`
- Schaeffer et al. 2024, Journal of Environmental Management 349:119518, DOI `10.1016/j.jenvman.2023.119518`, is the method paper. Official model code DOI `10.23719/1529140`. `prior`
- Prior facts from the HAB_PoC repository, access 2026-07-02, all `prior`. The canonical table `AllWeeks_CyanForecasts` has ten fields. It held 105,168 rows for 2,191 lakes and 48 weeks. The dashboards keep about two seasons. Extraction runs over the Qlik engine WebSocket with an anonymous session. That path is undocumented and not supported by EPA.

## Local machine

- The HAB_PoC repository's raw CyAN archive, forecast snapshots, and derived lake tables are not present on this machine. Only code and documents are. `probe`
- Available tooling: `uv` 0.12.3 with Python 3.12.13, `git`. No `gh` and no `aws` command line. `probe`
- The GitHub remote held one commit, an initial README of one line, before initialization. `probe`
