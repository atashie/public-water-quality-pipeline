# CyAN cyanobacteria index: metadata

Short name: `cyan`. Product: `CI_cyano`, the Level-3 mapped cyanobacteria index from merged Sentinel-3A and Sentinel-3B OLCI, version 6.0, as daily and 7-day composites. Version documented: 6.0, release notes of 2025-02 with the known-issues update of 2025-08.
Compiled: 2026-09-22. Access date for every check below: 2026-09-22. Compiled by the parent agent, Claude Code, directed by the repository owner, with a research agent on Opus and a checking agent on Sonnet.

Every fact carries a status. `documented [cl-...]` cites a claim in [reference/cyan-research.json](reference/cyan-research.json) with a verbatim quote, confirmed or corrected in [reference/cyan-checks.json](reference/cyan-checks.json). `probe` cites a dated record under [docs/probes/](../../docs/probes/README.md). `prior` is a fact from the owner's HAB_PoC repository, access 2026-07-01, not yet rechecked here. `unverified` names the step that settles it. Ambiguities are flagged in section 12, not smoothed over.

## 0. Summary for the modeler

| Question | Answer | Status |
|---|---|---|
| What is it? | A satellite cyanobacteria index for lakes and reservoirs of the contiguous United States and Alaska, produced by NASA for the multi-agency CyAN program | documented [cl-cyan-identity-product-title] [cl-cyan-identity-agencies] |
| Native form and format | One 8-bit GeoTIFF per tile or whole region per period. The catalog record says netCDF-4. The files are `.tif` | documented [cl-cyan-encoding-geotiff-8bit] [cl-cyan-format-granule-tif], discrepancy D3 |
| Spatial resolution and extent | 300 m nominal. Albers Equal Area matched to the National Hydrography Dataset. A 9 by 6 tile grid over the contiguous United States and 4 by 3 over Alaska | documented [cl-cyan-spatial-300m] [cl-cyan-spatial-albers-nhd] [cl-cyan-spatial-conus-tiles] [cl-cyan-spatial-alaska-tiles] |
| Temporal span, cadence, gaps | MERIS 2002 to 2012, then OLCI from 2016-04-24 with an open end. Daily and 7-day maximum composites. No product between 2012-04-07 and 2016-04-24 | documented [cl-cyan-temporal-meris-envisat-span] [cl-cyan-temporal-olci-collection-start] [cl-cyan-temporal-daily-and-7day], gap and start are probe |
| The value in a cell | The maximum index over the period, encoded as an 8-bit digital number | documented [cl-cyan-temporal-maximum-composite] |
| Encoding | 0 below detection, 1 to 253 data, 254 land, 255 no data. Index equals 10 to the power of DN times 0.011714 minus 4.1870866 | documented [cl-cyan-encoding-dn-table] [cl-cyan-encoding-dn-formula] |
| Nodata, fill, detection limit | 255 is no data. 0 is below the detection limit and is a measurement. The catalog variable declares no fill value | documented [cl-cyan-encoding-dn-table] [cl-cyan-encoding-band1-int8] |
| Access | Search through the OB.DAAC `cyan_file_search` endpoint. Download with an Earthdata Login through `getfile`, or read in region from the Earthdata Cloud bucket with temporary credentials | documented [cl-cyan-access-file-search-endpoint] [cl-cyan-access-edl-required] [cl-cyan-access-s3-bucket] |
| Full-archive size and the subset, assumption A16 | Daily whole-region files are about 4.5 MB and weekly ones about 5.9 MB. The weekly whole-region record from 2016 is a few gigabytes. The daily record is over the local limit. Scope is assumption A8 | probe and `prior`, section 6 |
| Likely role | The observed bloom signal. Per-lake statistics keyed by COMID become the target and features. Never validate it against the EPA forecast, which derives from it | section 9 |

## 1. What it is

CyAN is a project of four federal agencies, EPA, NASA, NOAA, and USGS, joined by the U.S. Army Corps of Engineers in 2023 according to EPA. documented [cl-cyan-identity-agencies] [cl-cyan-identity-usace-2023]
NASA's principal role is the production, validation, and distribution of the satellite-derived index. documented [cl-cyan-identity-nasa-role]
NASA's Ocean Biology Processing Group at Goddard Space Flight Center generates the MERIS and OLCI files. documented [cl-cyan-identity-producer-obpg]

The distributed collection is "Merged Sentinel-3A and Sentinel-3B OLCI Regional Mapped Cyanobacteria Index (CI) Data, version 6.0". Its short name is `MERGED_S3_OLCI_L3m_CYAN`, its DOI `10.5067/MERGED-S3/OLCI/L3M/CYAN/CI/6.0`, its processing level 3, and its platforms Sentinel-3A and Sentinel-3B. documented [cl-cyan-identity-product-title] [cl-cyan-identity-short-name] [cl-cyan-identity-doi] [cl-cyan-identity-version] [cl-cyan-identity-processing-level] [cl-cyan-identity-platforms]
The one geophysical variable is `band1`, the digital-number-encoded index, unitless. documented [cl-cyan-identity-band1-variable]
A companion MERIS collection exists, `MERIS_L3m_CYAN` version 6.0, concept id `C3416412319-OB_CLOUD`. documented [cl-cyan-identity-meris-collection]

Maturity. The data are validated at Stage 2 of 4 on NASA's data maturity ranking. Stage 2 means accuracy is estimated from a significant but not full set of independent measurements from selected locations and periods. documented [cl-cyan-maturity-stage-2] [cl-cyan-maturity-stage-2-definition]
The release notes state that the data are preliminary and for evaluation purposes only. documented [cl-cyan-maturity-preliminary]
Validation has been published for Lake Erie and fifteen states. They are Florida, Ohio, Vermont, New Hampshire, Rhode Island, Connecticut, Massachusetts, Oregon, California, Indiana, New Jersey, New York, Utah, Maine, and Idaho. documented [cl-cyan-maturity-validation-locations]
EPA describes its own CyANWeb application over these data as experimental and provisional. That wording is about the application, not the NASA files. documented [cl-cyan-maturity-epa-experimental]

## 2. Temporal coverage, cadence, and gaps

| Sensor | Period | Cadence | Status |
|---|---|---|---|
| MERIS on Envisat | 2002 to 2012. The catalog extent is 2002-03-21 to 2012-05-09 | 14-day composites 2002 to 2007, when the instrument viewed the United States irregularly. 7-day composites and dailies 2008 to 2012 | documented [cl-cyan-temporal-meris-envisat-span] [cl-cyan-temporal-meris-14day] [cl-cyan-temporal-meris-collection-extent] [cl-cyan-temporal-meris-collection-end] |
| Gap | 2012-04-07 to 2016-04-24 | No file listed. The last MERIS weekly file ends 2012-04-07. A weekly search for 2013-01-01 to 2015-12-31 returns "Your query generated 0 file(s)." | probe, [record](../../docs/probes/2026-09-22-cyan-format-and-start.md) |
| OLCI on Sentinel-3A and 3B | Catalog extent starts 2016-04-25, open-ended. The earliest weekly file covers 2016-04-24 to 2016-04-30 and the earliest daily file 2016-04-25. See discrepancy D1 | Daily and 7-day composites at 300 m | documented [cl-cyan-temporal-olci-collection-start] [cl-cyan-temporal-daily-and-7day], probe [record](../../docs/probes/2026-09-22-cyan-format-and-start.md) |

The OLCI products are merged Sentinel-3A and 3B from 2018 onward. The merged value is the maximum for each pixel. documented [cl-cyan-temporal-merged-s3a-s3b-2018] [cl-cyan-temporal-merged-max-per-pixel]
Both the daily and the 7-day composite hold the maximum index over their period. documented [cl-cyan-temporal-maximum-composite]

Latency. No fetched page states when a new composite appears. On the pull of 2026-09-22 the newest weekly file was 3 days past its window end and the newest daily file 1 day. Those ages at retrieval bound the publication delay from above. The delay itself stays `unverified`. measured, [measurement 4](../../docs/measurements.md#4-the-assumption-a8-pull-598-files-335-gb-no-failure-newest-weekly-file-3-days-old-at-retrieval-2026-09-22)
On 2026-09-22 the file search listed the weekly composite for 2026-09-13 to 2026-09-19. That was 3 days after its window end. It also listed the daily composite for 2026-09-21, 1 day old. probe, [record](../../docs/probes/2026-09-22-cyan-catalogs.md)
On the same day the cloud HTTPS endpoint's newest file lagged the file search by 7 weeks. Six older weekly paths were unavailable through it. measured, [measurement 1](../../docs/measurements.md#1-the-cloud-https-endpoint-served-529-of-560-listed-weekly-files-7-weeks-behind-two-samples-byte-identical-2026-09-22)
The search listing lacks the week starting 2026-07-05. From 2016-04-24 to 2026-09-13 there are 543 weekly start dates and the file search lists 542. Physical absence from the archive is not established. measured, [measurement 2](../../docs/measurements.md#2-the-archive-listing-lacks-one-weekly-file-2026-09-22)

Reprocessing. The producer reprocesses and redistributes the whole MERIS and OLCI series every 10 to 16 months. EPA's page says annually. documented [cl-cyan-temporal-reprocessing-cadence], discrepancy D6
Version history: 4.0 in 2022-03, 5.0 in 2023-05, 6 in 2025-02, with a known-issues update in 2025-08. All current data are processing version 6. documented [cl-cyan-temporal-version-history] [cl-cyan-temporal-current-version]
Version 6 changed the vicarious calibration with minor adjustments at 681 nm and 709 nm, added a water vapor correction, and improved the turbid-water test. documented [cl-cyan-temporal-v6-changes]
Pixel values are therefore not frozen. Every pulled file records its version tag, section 10.

## 3. Spatial characteristics

- Nominal resolution 300 m. The Appendix A metadata of the upstream binned file says 289.894507 m. See discrepancy D4. documented [cl-cyan-spatial-300m] [cl-cyan-spatial-appendix-a-resolution]
- Projection: Albers Equal Area with area-weighted interpolation to match the National Hydrography Dataset projection. No page gives an EPSG code or parameters. documented [cl-cyan-spatial-albers-nhd]. Every one of the 598 pulled files declares EPSG:5070 at exactly 300.0 m. measured, [measurement 5](../../docs/measurements.md#5-qaqc-of-the-pulled-files-2026-09-22)
- Tiles: 9 by 6 over the contiguous United States and 4 by 3 over Alaska. Tile pixel dimensions are not on any page. The HAB_PoC repository measured 2,000 by 2,000 pixels, `prior`. No tile is in the pulled scope. documented [cl-cyan-spatial-conus-tiles] [cl-cyan-spatial-alaska-tiles]
- Whole-region files: the search parameter `areaids=all` retrieves all data. On 2026-09-22 the search returned whole-region file names without a tile suffix. Every pulled whole-region file is 26,328 by 15,138 pixels on one shared grid. The origin is easting −3,949,197.047 m and northing 3,791,526.267 m. Files are LZW compressed with one row per block. documented [cl-cyan-access-param-areaids], measured [measurement 5](../../docs/measurements.md#5-qaqc-of-the-pulled-files-2026-09-22)
- Land mask: the release notes say Shuttle Radar Topography Mission 60-meter data. The project page says a 50 m mask for the contiguous United States and a less refined 500 m mask for Alaska. The release notes name the Alaska file `landmask_GMT15ARC_AK_v2021.nc`. See discrepancy D2. documented [cl-cyan-spatial-srtm-landmask] [cl-cyan-spatial-project-landmasks] [cl-cyan-spatial-alaska-landmask-file]
- Minimum reliable water body: retrievals are considered more robust for lakes with a window width of at least 900 m. That width gives a minimum 3 by 3 pixel array. Smaller water bodies and rivers are not masked, and their data may be erroneous. documented [cl-cyan-spatial-900m-window] [cl-cyan-spatial-3x3-pixels] [cl-cyan-issues-small-waterbodies]

## 4. Encoding and quality flags, exact values

Each file is an 8-bit GeoTIFF. documented [cl-cyan-encoding-geotiff-8bit]. Every pulled file is one uint8 band with no nodata flag. The four classes below partition every uint8 value, so counting them describes a file without validating its codes. measured, [measurement 5](../../docs/measurements.md#5-qaqc-of-the-pulled-files-2026-09-22)

| Digital number | Meaning | Handling |
|---|---|---|
| 0 | Below the detection limit. Water was observed | A measurement, not missing. Keep it distinct from 255 |
| 1 to 253 | Data | Convert with the formula below |
| 254 | Land | Mask |
| 255 | No data, for example a cloudy pixel or ice cover | Missing |

documented [cl-cyan-encoding-dn-table]

Conversion for 1 to 253: index equals 10 to the power of the digital number times 0.011714 minus 4.1870866. documented [cl-cyan-encoding-dn-formula]
NASA's guide renders below-threshold pixels grey, land brown, and no data black. documented [cl-cyan-encoding-dn-guide-colors]
The catalog variable `Band1` is `int8` with no fill value, valid range, scale, or offset recorded. The semantics live in the release notes. documented [cl-cyan-encoding-band1-int8]

Look-alike product. NOAA's cyanobacteria index uses a different encoding. Its land value is 252, its invalid values are 251, 253, 254, and 255, and its valid range is 0 to 250. CyAN uses land 254, invalid 255, and a range of 0 to 253. Code written for the NOAA product is wrong for these files. documented [cl-cyan-encoding-noaa-flagging] [cl-cyan-encoding-noaa-valid-range]

Flags. The distributed GeoTIFF carries one band. Its default metadata namespace holds two tags, `AREA_OR_POINT` and `OBPG_version`, beside the `IMAGE_STRUCTURE` and `DERIVED_SUBDATASETS` namespaces. No separately exposed flag raster ships with it. Whether upstream snow and ice screening was applied is not visible in the file. measured, [measurement 5](../../docs/measurements.md#5-qaqc-of-the-pulled-files-2026-09-22)
The upstream binned file carries `CI_stumpf`, `CI_cyano`, `CI_noncyano`, `MCI_stumpf`, `chl_mph`, `flags_mph`, and `flags_habs`, and its binning used the Level-2 flags LAND, CLDICE, and HISATZEN. documented [cl-cyan-encoding-l3b-variables] [cl-cyan-encoding-l2-flags]
A snow and ice flag and a mixed-pixel flag have been applied but are not yet verified, section 5.
A separate lake biophysical water quality flag dataset is cited in the release notes. The notes do not say that it ships with these files. documented [cl-cyan-issues-biophysical-flag-dataset]

Cell counts. The project page says the digital-number range corresponds to roughly 10,000 to 7,000,000 cells per milliliter. It gives no conversion factor. The release notes give none either. documented [cl-cyan-encoding-cells-per-ml-range], `unverified` factor. Any cell-count statement in this repository names its own source and its uncertainty.

## 5. Known issues and limitations, from the producer

All from the release notes' Known Issues section of 2025-08. The list numbers 1 to 5 and 7 to 9. Item 6 is absent from the document.

1. A snow and ice flag has been applied but not verified. Ice can register as high index counts. Whether cyanobacteria under thin ice are detectable is unknown. documented [cl-cyan-issues-snow-ice-flag] [cl-cyan-issues-under-thin-ice]
2. The land mask may cover dry lakes and may exclude other lakes. An eroded mask is needed. documented [cl-cyan-issues-landmask-imperfect]
3. A mixed land and water pixel flag has been added but not verified. Caution at the shoreline. documented [cl-cyan-issues-mixed-pixels]
4. Undetected thin clouds can register as high index counts. documented [cl-cyan-issues-thin-clouds]
5. Retrievals are robust only at 900 m window width or more. Smaller water bodies and rivers are not masked. documented [cl-cyan-spatial-900m-window] [cl-cyan-issues-small-waterbodies]
7. Processing does not account for water level changes from drought and flood. documented [cl-cyan-issues-no-water-level-correction]
8. Validation is published for the locations in section 1. documented [cl-cyan-maturity-validation-locations]
9. The 7-day mapped maximum is occasionally lower than that week's daily maximum, because of the reprojection during mapping. The weekly file is not a strict upper bound on the dailies. documented [cl-cyan-issues-7day-less-than-daily]

Turbid water: version 6's improved test reduces false positives in turbid waters. It does not claim to remove them. documented [cl-cyan-issues-turbid-water]

Measured composition of the pulled whole-region files. The canvas is 33.2 percent land and 61 to 65 percent no data. The below-detection class is 1.4 to 5.1 percent and the data class 0.03 to 0.53 percent. The land count varies by up to 1,365 pixels between files. That is a lower bound on the pixels whose class differs, so no single file's land class is a mask. Canvas percentages say nothing about coverage inside a lake. measured, [measurement 5](../../docs/measurements.md#5-qaqc-of-the-pulled-files-2026-09-22)

Consequences for use. Cloud and ice gaps are seasonal and latitudinal, so missing values are not random. Below-detection values are frequent and meaningful. Small, narrow, and shoreline waters are under-served. Values change with each reprocessing.

## 6. Bulk or subset

Measured sizes from the catalog on 2026-09-22: a daily whole-region file 4.53 MB, a daily tile 0.13 MB, weekly whole-region files 5.6 to 5.9 MB. Two weekly files downloaded on 2026-09-22 were 5,886,210 and 6,175,066 bytes, measurement 1. The tile size is also a catalog claim. The catalog record gives the number without a unit. Megabytes is the catalog's documented convention. documented [cl-cyan-format-granule-size] The catalog held 3,742 daily and 529 weekly whole-region files through 2026-08-01. probe, [records](../../docs/probes/README.md)
The HAB_PoC repository pulled the full weekly whole-region record, MERIS and OLCI, as 752 files and 4.04 GB on 2026-07-01. `prior`

Measured on the pull of 2026-09-22, with the two unpulled scopes estimated from the same numbers:

| Scope | Files | Size |
|---|---|---|
| Weekly whole-region, OLCI 2016 onward, assumption A8 | 542, pulled 2026-09-22 | 3,080,930,304 bytes, [measurement 4](../../docs/measurements.md#4-the-assumption-a8-pull-598-files-335-gb-no-failure-newest-weekly-file-3-days-old-at-retrieval-2026-09-22) |
| Daily whole-region, most recent 8 weeks, assumption A8 | 56, pulled 2026-09-22 | 271,020,420 bytes, [measurement 4](../../docs/measurements.md#4-the-assumption-a8-pull-598-files-335-gb-no-failure-newest-weekly-file-3-days-old-at-retrieval-2026-09-22) |
| Daily whole-region, OLCI 2016 onward | about 3,800 | about 17 GB, over the limit of assumption A16 |
| Per-tile instead of whole-region | 54 tiles per date | many small files, no size saving |

Decision under assumption A8: the weekly whole-region record in full plus the recent dailies are pulled. The full daily record and the tiles are not.

## 7. Access, verified 2026-09-22

### 7.1 Search or enumerate

The search tool is at `https://oceandata.sci.gsfc.nasa.gov/api/cyan_file_search/`, reached from the NASA Earthdata tool page. documented [cl-cyan-access-file-search-endpoint]
Parameters, from the OB.DAAC page's bulk-download instructions. documented [cl-cyan-access-param-region-period-product] [cl-cyan-access-param-areaids] [cl-cyan-access-param-dates-and-flags]

| Parameter | Values |
|---|---|
| `region` | 0 Alaska, 1 contiguous United States |
| `period` | 1 weekly, 2 daily |
| `product` | 1 cyanobacteria index, 2 true color |
| `areaids` | `all`, one tile such as `1_1`, or tiles joined with `+` |
| `sdate`, `edate` | `YYYY-MM-DD` |
| `addurl` | 1 to include full URLs |
| `results_as_file` | 1 for a text listing |
| `wgetflag` | Always 1. Mandatory |
The page's wget example posts to a host without the `.sci.` label. documented [cl-cyan-access-wget-example]
A search without credentials returned a listing on 2026-09-22. probe. The HAB_PoC repository observed intermittent HTTP 502 from this endpoint and retried. `prior`

### 7.2 Download and authentication

Files download through `getfile` URLs on the OceanColor host. documented [cl-cyan-access-getfile-pattern]
The OB.DAAC requires an Earthdata Login to download any product. documented [cl-cyan-access-edl-required]
Three methods: a `.netrc` file for `urs.earthdata.nasa.gov`, an AppKey appended to the download URL, or a user token sent as a Bearer token. User tokens are valid for 60 days. documented [cl-cyan-access-netrc] [cl-cyan-access-appkey] [cl-cyan-access-bearer-token] [cl-cyan-access-token-lifetime]
Credentials live in the ignored `.env`, variables `OB_DAAC_EDL_TOKEN` or `OB_DAAC_APPKEY`. See [.env.example](../../.env.example).

### 7.3 Earthdata Cloud, in region

The granules live in the bucket `s3://ob-cumulus-prod-public/`. Each granule carries an `s3://` link and an HTTPS link under `https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/`. documented [cl-cyan-access-s3-bucket] [cl-cyan-access-granule-s3-href] [cl-cyan-access-tea-https-prefix]
Temporary credentials come from `https://obdaac-tea.earthdatacloud.nasa.gov/s3credentials`. They allow same-region, read-only, direct S3 access and last 1 hour. documented [cl-cyan-access-s3credentials-endpoint] [cl-cyan-access-s3-same-region-readonly] [cl-cyan-access-s3-credentials-1hour]
The collection's direct-distribution region is us-west-2. Two other NASA-related pages state the us-west-2 limit in general terms. documented [cl-cyan-access-region-us-west-2] [cl-cyan-access-us-west-2-limit] [cl-cyan-access-us-west-2-laads]
An unauthenticated HEAD on the HTTPS link redirected to a host naming `ob-cumulus-prod-public.s3.us-west-2.amazonaws.com`, which places the bucket in us-west-2. probe [record](../../docs/probes/2026-09-22-cyan-format-and-start.md)
On 2026-09-22 the cloud HTTPS endpoint served 529 of the 560 weekly whole-region files the file search listed. Its newest file ended 2026-08-01, 7 weeks behind. Beyond the lag, 6 weekly files from the last 17 months were absent, and the 18 `CYANV6T` duplicates were absent with their `CYAN` twins present. The two sampled files were byte-identical on both routes. Identity elsewhere is untested. Listing the bucket from outside us-west-2 was refused, which matches NASA staff guidance on the Earthdata forum. measured, [measurement 1](../../docs/measurements.md#1-the-cloud-https-endpoint-served-529-of-560-listed-weekly-files-7-weeks-behind-two-samples-byte-identical-2026-09-22). See [docs/aws/cyan.md](../../docs/aws/cyan.md).

### 7.4 Ancillary files

- Lake shapefile for MERIS and OLCI sensors: `https://www.earthdata.nasa.gov/s3fs-public/2026-01/MERIS_OLCI_Lakes.zip`. documented [cl-cyan-lakes-shapefile-link]. On 2026-09-22 the file was 32,822,913 bytes, last modified 2026-01-07. probe. The HAB_PoC repository read 2,321 valid lakes keyed by COMID from `updatedValidLakes.shp`, `prior`. No page states that the shapefile carries COMID. Step 1e verifies it.
- Tile-grid shapefile for the contiguous United States: `https://www.earthdata.nasa.gov/s3fs-public/2026-01/CONUS_tiles_shapefile.zip`. documented [cl-cyan-lakes-conus-tile-shapefile]
- The project page says the "CONUS Shapefile" comes from NHDPlus version 2.0. Which of the two shapefiles that sentence means is not clear from the page. documented [cl-cyan-lakes-nhdplus-source]
- NASA warns the shapefiles are not perfect and are occasionally updated. documented [cl-cyan-lakes-shapefiles-imperfect]
- EPA's CyANWeb serves the same data for over 2,000 of the largest lakes and reservoirs. documented [cl-cyan-lakes-epa-2000-lakes]

## 8. Sources, all accessed 2026-09-22

Full records with titles, publishers, and page dates are in [reference/cyan-research.json](reference/cyan-research.json).

1. Release notes for the NASA-produced MERIS and OLCI cyanobacteria index, version 6, 2025-02, known-issues update 2025-08. `https://oceancolor.gsfc.nasa.gov/images/cyan/version/6/CyAN_NASA_MERISOLCI_CI_release_notes_V6_Aug_2025.pdf`. Local copy and text extraction under [reference/](reference/README.md).
2. Earthdata collection page, `https://www.earthdata.nasa.gov/data/catalog/ob-cloud-merged-s3-olci-l3m-cyan-6.0`.
3. CMR collection records, `https://cmr.earthdata.nasa.gov/search/concepts/C3416412382-OB_CLOUD.json` and the `.umm_json` form, and the MERIS record `C3416412319-OB_CLOUD.json`.
4. CMR granule search for the newest granule of the collection.
5. EPA, Cyanobacteria Assessment Network, `https://www.epa.gov/water-research/cyanobacteria-assessment-network-cyan`.
6. EPA, CyAN application page, `https://www.epa.gov/water-research/cyanobacteria-assessment-network-application-cyan-app`.
7. NASA Earthdata CyAN project page, `https://www.earthdata.nasa.gov/data/projects/cyan`.
8. NASA Earthdata CyAN File Search tool page, `https://www.earthdata.nasa.gov/data/tools/cyan-file-search`.
9. OB.DAAC CyAN file search page, `https://oceandata.sci.gsfc.nasa.gov/api/cyan_file_search/`.
10. NASA Earthdata tutorial on OB.DAAC search and download methods, `https://www.earthdata.nasa.gov/learn/tutorials/search-download-methods-data-archived-ob-daac`.
11. OB.DAAC temporary credentials README, `https://obdaac-tea.earthdatacloud.nasa.gov/s3credentialsREADME`.
12. Earthdata Login user token documentation, `https://urs.earthdata.nasa.gov/documentation/for_users/user_token`.
13. NASA Earthdata open data policy, `https://www.earthdata.nasa.gov/engage/open-data-services-software-policies`.
14. NASA Openscapes Earthdata Cloud Clinic, community-maintained, and a LAADS DAAC page on direct S3 access. Corroboration only.

## 9. Role in this project

The index is the observed bloom signal for every lake in the universe of assumption A9. Per-lake statistics over the pixels inside a lake polygon become the target and the features of any model. That aggregation needs the recorded authorization of assumption A17 before step 1e computes it.
The EPA cyanoHAB forecast is built from this signal. Validating a model that uses this signal against that forecast is circular. Ground truth for bloom presence comes from independent in situ sources or from this index treated as an observation.
The index is not a toxin measurement and not a cell count. Any link from index to cells or toxins carries its own source and uncertainty.

## 10. Reproducibility and version pinning

- Read the processing version from each file's own metadata, never from the filename. No page documents the tag. Every one of the 598 files pulled on 2026-09-22 carries the tag `6.0`. measured, [measurement 4](../../docs/measurements.md#4-the-assumption-a8-pull-598-files-335-gb-no-failure-newest-weekly-file-3-days-old-at-retrieval-2026-09-22). The HAB_PoC repository read `6T` from files whose names carry `CYANV6T`, `prior`, none of which is in the pulled scope.
- Two name streams can coexist for one date, `CYAN` and `CYANV6T`. The dry run of 2026-09-22 found 18 `CYANV6T` duplicates, all in 2022 and 2023, each with a `CYAN` twin. The pull keeps `CYAN`, which spans the whole record. measured, [measurement 3](../../docs/measurements.md#3-dry-run-plans-for-the-assumption-a8-scope-2026-09-22)
- Every download goes through the cached, sha256-manifested helper in `datasets/_common/net.py`. A changed sha256 on re-fetch is a reprocessing event, recorded, never overwritten.
- File names follow `sensoryyyydddyyyyddd.datalevel_temporalresolution_product_version_resolution_region`, with a tile column and row suffix for tiles. A daily file carries one date stamp. Alaska files replace `CONUS` with `AK`. documented [cl-cyan-naming-convention-release-notes] [cl-cyan-naming-example-decomposition] [cl-cyan-naming-project-page-pattern] [cl-cyan-naming-granule-real-example] [cl-cyan-naming-alaska-difference]
- Access date for every check in this document: 2026-09-22.

## 11. License and attribution

NASA's Earth Science Data Systems program promotes full and open sharing of all data, metadata, documentation, and source code. Data generated under NASA sponsorship are available to all users, and citation is encouraged. documented [cl-cyan-terms-open-sharing] [cl-cyan-terms-data-use-guidance]
The collection is openly shared without restriction under the EOSDIS data use and citation guidance. The collection metadata carries no use-constraint element. documented [cl-cyan-terms-citation-requirement]
Recommended citation: "NASA Ocean Biology Processing Group. (2025). Merged Sentinel-3A and Sentinel-3B OLCI Regional Mapped Cyanobacteria Index (CI) Data, version 6.0 [Dataset]. NASA Ocean Biology Distributed Active Archive Center. https://doi.org/10.5067/MERGED-S3/OLCI/L3M/CYAN/CI/6.0". documented [cl-cyan-terms-citation-text]
The project page's citation form adds the access URL and date. documented [cl-cyan-terms-citation-project-page]
EPA's application page disclaims endorsement of any trade name, product, service, or enterprise. documented [cl-cyan-terms-epa-disclaimer]

## 12. Discrepancies and open items

The owner ruled on 2026-09-22 that O1 to O4 are unknowns to uncover when their step runs, not blockers. O2 and O4 were uncovered the same day. D7 feeds the AWS route decision.

| Id | Topic | What the sources say | Resolution |
|---|---|---|---|
| D1 | OLCI start | Catalog and collection page: 2016-04-25. EPA page and project page: 2016. Release notes: 2017. The search form labels weekly as "2007-Present" | Confirmed by probe on 2026-09-22. The earliest weekly OLCI file starts 2016-04-24 and the earliest daily file 2016-04-25. The release notes' 2017 describes the instrument era. The form's 2007 spans MERIS and OLCI together. [record](../../docs/probes/2026-09-22-cyan-format-and-start.md) |
| D2 | Land mask resolution | Release notes: SRTM 60-meter. Project page: 50 m for the contiguous United States, 500 m for Alaska | Unresolved on the pages. Recorded as two statements |
| D3 | File format | Collection page and metadata: netCDF-4 [cl-cyan-format-collection-netcdf4] [cl-cyan-format-umm-netcdf4]. Granules: `.tif` [cl-cyan-format-granule-tif]. Release notes: 8-bit GeoTIFF | Confirmed by probe on 2026-09-22. Granule-level metadata says Format TIFF and MimeType image/tiff. Every listed file ends in `.tif`. The netCDF-4 label matches the intermediate binned files in the release-notes appendices. The TIFF byte signature is checked in step 1b. [record](../../docs/probes/2026-09-22-cyan-format-and-start.md) |
| D4 | Pixel size | Release notes body: 300 m. Appendix A: 289.894507 m | Appendix A describes the binned grid. Step 1c reads the mapped pixel size from a file |
| D5 | DOI | Catalog: `L3M/CYAN/CI/6.0`. Release notes file metadata: `L3B/CYAN/CI/6T` | Two products, mapped and binned. Cite the catalog DOI for the distributed files |
| D6 | Reprocessing cadence | Release notes: every 10 to 16 months. EPA page: annually | Both recorded. Step 1g plans a version watch either way |
| D7 | Cloud copy completeness | Measured on 2026-09-22: two samples byte-identical, the endpoint's newest file 7 weeks behind, 6 older weekly paths unavailable through it, bucket listing refused from outside the region | A Discovery input to the AWS route choice, [docs/aws/cyan.md](../../docs/aws/cyan.md), [measurement 1](../../docs/measurements.md#1-the-cloud-https-endpoint-served-529-of-560-listed-weekly-files-7-weeks-behind-two-samples-byte-identical-2026-09-22). A listing from inside us-west-2 remains open |
| O1 | Weekly update timing | Not on any fetched page. Not needed now | Bounded from above by the age at retrieval of the newest pulled file, 3 days weekly and 1 day daily on 2026-09-22. The delay itself needs first-availability observations |
| O2 | EPSG code and tile pixel dimensions | Not on any page | Resolved for the whole-region files on 2026-09-22: EPSG:5070, 26,328 by 15,138 pixels, [measurement 5](../../docs/measurements.md#5-qaqc-of-the-pulled-files-2026-09-22). Tile dimensions stay `prior` until a tile is pulled |
| O3 | COMID in the lake shapefile | Not on any page. Not needed now | Step 1e opens the shapefile |
| O4 | Flag bands in the GeoTIFF | Not on any page. The catalog lists one band | Resolved on 2026-09-22: one band, two tags, no flag band, [measurement 5](../../docs/measurements.md#5-qaqc-of-the-pulled-files-2026-09-22) |
| O5 | Cells per milliliter factor | Range only, no factor, no citation | Any factor used later names its own source |
| O6 | Known Issues item 6 | Absent from the document | None. Recorded as published |
