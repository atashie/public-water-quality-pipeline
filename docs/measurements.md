# Measurements

What checked-in scripts measured, with the result file behind each number and what the number does not show. Never edit a result file by hand. Rerun the script.

## CyAN

### 1. The cloud HTTPS endpoint served 529 of 560 listed weekly files, 7 weeks behind, two samples byte-identical, 2026-09-22

Script `datasets/cyan/access/compare_routes.py`. Result [route-comparison-2026-09-22.json](../datasets/cyan/outputs/route-comparison-2026-09-22.json). Run from the owner's laptop, outside us-west-2, with an Earthdata token. 2 minutes 32 seconds. `measured`
The result names base revision `9838942`. The script was uncommitted at run time and was committed unchanged in `5663c35`. Later results carry the working-tree state and source hashes.

| Measure | Value |
|---|---|
| Weekly whole-region files the file search listed for 2016-01-01 to 2026-09-22 | 560, of which 542 in the `CYAN` stream and 18 `CYANV6T` duplicates of weeks in 2022 and 2023 |
| Files the cloud HTTPS endpoint served with HTTP 200 | 529, all `CYAN` stream |
| Paths it answered with HTTP 404 at that time | 31. A 404 is an unavailable path, not a bucket listing |
| Of those, `CYANV6T` duplicates whose `CYAN` twin is present | 18. Date coverage is retained in the `CYAN` stream. Byte or version equivalence between the streams is untested |
| Of those, weeks newer than the endpoint's newest file | 7, window starts 2026-08-02 through 2026-09-13 |
| Of those, `CYAN` files older than the newest yet absent | 6, window starts 2025-04-27, 2025-07-06, 2025-07-13, 2025-08-24, 2025-09-21, 2026-01-18 |
| Newest window end on the endpoint and in the cloud catalog | 2026-08-01, against 2026-09-19 in the file search |
| Cloud catalog granules matching the weekly whole-region pattern | 529, equal to the endpoint count |
| Temporary credentials endpoint | HTTP 200, credentials issued |
| Bucket listing with those credentials from outside us-west-2 | Refused, `AccessDenied` |
| Sample files downloaded through both routes and compared | 2 of 2 identical by sha256, 5,886,210 and 6,175,066 bytes. The two newest files present on both routes, not a random sample |

What it shows. For the two sampled files, the bytes equal the archive's. The endpoint's newest file trails the archive listing by 7 weeks, and 6 older weekly paths were unavailable through it. Listing the bucket needs compute inside us-west-2, which NASA staff confirm on the Earthdata forum, `documented` in the [independent validation](reviews/2026-09-22-cyan-independent-validation.md). The HTTPS endpoint answered from the tested off-region laptop with a token.
What it does not show. Byte identity beyond the two samples. Whether the bucket itself lacks the 6 files or only the endpoint's index does. Whether the lag is constant. Daily and tile files were not compared.

### 2. The archive listing lacks one weekly file, 2026-09-22

Same result file, and the plan file below. From 2016-04-24 to 2026-09-13 there are 543 weekly start dates. The file search lists 542 `CYAN` weeks. The week starting 2026-07-05 is absent from the search listing on 2026-09-22. Physical absence from the archive is not established. `measured`

### 3. Dry-run plans for the assumption A8 scope, 2026-09-22

Script `datasets/cyan/access/pull_cyan.py --dry-run`. Results [plan-weekly-mosaic-2026-09-22.json](../datasets/cyan/outputs/plan-weekly-mosaic-2026-09-22.json) and [plan-daily-mosaic-2026-09-22.json](../datasets/cyan/outputs/plan-daily-mosaic-2026-09-22.json). `measured`

| Scope | Files | First | Last | Streams |
|---|---|---|---|---|
| Weekly whole-region, 2016-01-01 to 2026-09-22 | 542 after collapsing 18 duplicates | 2016-04-24 to 2016-04-30 | 2026-09-13 to 2026-09-19 | `CYAN` only |
| Daily whole-region, 2026-07-28 to 2026-09-22 | 56 | 2026-07-28 | 2026-09-21 | `CYAN` only |

Size estimate: the two sampled weekly files were about 6 MB each, and the catalog probe gave 4.5 MB for a daily file. That makes about 3.3 GB weekly plus about 0.25 GB daily. Under the limit of assumption A16. `unverified` until the pull measures it.

### 4. The assumption A8 pull: 598 files, 3.35 GB, no failure, newest weekly file 3 days old at retrieval, 2026-09-22

Script `datasets/cyan/access/pull_cyan.py` through the archive route, authorized by the owner on 2026-09-22. Manifests under `data/cyan/raw/<dir>/manifest.jsonl`, ignored by git. Their statistics are in the QA result files under `datasets/cyan/outputs/`. `measured`

| Measure | Weekly whole-region | Daily whole-region |
|---|---|---|
| Files planned and fetched | 542 of 542 | 56 of 56 |
| Failures and integrity events | 0 and 0 | 0 and 0 |
| Bytes | 3,080,930,304 | 271,020,420 |
| File size range | 4,215,264 to 8,408,906 | 4,422,996 to 5,231,522 |
| Version tag read from every file | `6.0` | `6.0` |
| Wall time | 11 minutes 54 seconds, 2026-09-22T16:15:40Z to 16:27:34Z | 1 minute 41 seconds |
| Newest file's age at retrieval, window end to access | 3 days, window 2026-09-13 to 2026-09-19 | 1 day, 2026-09-21 |

What it shows. The scope of assumption A8 fits under the limit of assumption A16 with room to spare. The archive route delivered every planned file on the first attempt at about 4.4 MB per second. Every file carries the version tag `6.0`. The newest file's age at retrieval bounds the provider's publication delay from above. The bound is 3 days for that weekly file and 1 day for that daily file.
What it does not show. The publication delay itself, which stays `unverified` until first-availability observations exist. Throughput on another day or from another network. The size of the daily record beyond 8 weeks. The manifests of this pull store the age under the key `latency_days`. Later pulls write `age_at_retrieval_days`. Both mean age at retrieval.

### 5. QA/QC of the pulled files, 2026-09-22

Script `datasets/cyan/qaqc/qa_cyan.py` over both raw directories against their approved plans. Results [qa-weekly_conus_mosaic-2026-09-22T1850Z.json](../datasets/cyan/outputs/qa-weekly_conus_mosaic-2026-09-22T1850Z.json), [qa-daily_conus_mosaic-2026-09-22T1850Z.json](../datasets/cyan/outputs/qa-daily_conus_mosaic-2026-09-22T1850Z.json), and the [report](../datasets/cyan/outputs/qa-report-2026-09-22T1850Z.md). Started 2026-09-22T18:50:06Z, finished 19:59:25Z, 69 minutes for 598 files. The first run took under 10 minutes on files fresh in the page cache. The rerun's wall time is not a throughput measurement. `measured`
A first run of the script, before the corrections of the [independent review](reviews/2026-09-22-cyan-pull-qa-independent-review.md), gave the same per-file numbers. Its result files were replaced by this run's.

| Measure | Value |
|---|---|
| Inventory | 598 planned, 598 in the manifests, 598 on disk, 598 readable. No file in one inventory and not another |
| Files flagged, collection flags | 0, none |
| sha256 against the manifest | 598 of 598 match |
| Band count and type | 1 band, uint8, in every file |
| Projection | EPSG:5070 in every file |
| Grid | 26,328 by 15,138 pixels, 300.0 m, one transform, origin easting −3,949,197.047 m and northing 3,791,526.267 m, in every file |
| Nodata flag, compression, blocks | None, LZW, one row per block, in every file |
| Metadata | Namespaces `IMAGE_STRUCTURE`, `DERIVED_SUBDATASETS`, and the default one. The default namespace holds `AREA_OR_POINT` and `OBPG_version`. `OBPG_version=6.0` in every file. No separately exposed flag raster |
| Composition under the documented encoding, whole canvas | Land, code 254: 33.247 to 33.248 percent. No data, code 255: 61.1 to 64.2 percent in weekly files, 63.7 to 65.2 in daily files. Below detection, code 0: 2.5 to 5.1 percent weekly, 1.4 to 2.9 daily. Data, codes 1 to 253: 0.03 to 0.53 percent weekly, 0.08 to 0.17 daily |
| Land count across files | 132,508,772 to 132,510,137 pixels, a spread of 1,365. The spread is a lower bound on the number of pixels whose class differs between files |
| Highest code | 253 in 537 of 542 weekly files and in all 56 daily files. The lowest per-file maximum is 251 |
| Completeness against the plan bounds | Weekly 542 of 543 dates from 2016-04-24 to 2026-09-13, the week starting 2026-07-05 without a file. Daily 56 of 56 from 2026-07-28 to 2026-09-21 |
| Age at retrieval of the newest file | 3 days weekly, 1 day daily |

What it shows. The files share one grid and one version tag, and their metadata matches the documented encoding. The four classes partition every uint8 value, so the composition describes the files and does not validate the meaning of any code. The land class differs between files. A per-lake mask must therefore come from the lake polygons and treat each file's land and no-data codes on its own.
What it does not show. Whether any value is right. Usable coverage inside any lake, or the causes of missing values. Whether upstream snow and ice screening was applied. Physical absence of the missing week from the archive.

### 6. The CyAN resolvable-lakes shapefile: 2,321 lakes keyed by COMID, 2026-09-23

Scripts `datasets/cyan_lakes/access/pull_lakes.py` and `datasets/cyan_lakes/qaqc/qa_lakes.py`. Results [qa-lakes-2026-09-23T1433Z.json](../datasets/cyan_lakes/outputs/qa-lakes-2026-09-23T1433Z.json) and the [report](../datasets/cyan_lakes/outputs/qa-lakes-2026-09-23T1433Z.md). `measured`

| Measure | Value |
|---|---|
| `MERIS_OLCI_Lakes.zip` | 32,822,913 bytes, sha256 `e3efe1f69a00...`, fetched 2026-09-23. Four members, `updatedValidLakes.shp` at 41,997,768 bytes |
| `CONUS_tiles_shapefile.zip` | 4,834 bytes, 54 tile features with row and column fields |
| Lake features, distinct COMID, null, duplicated | 2,321, 2,321, 0, 0 |
| Projection | Albers equal area on GRS80, read as EPSG:5070 |
| Geometry | 2,316 polygons and 5 multipolygons, 2,306 valid, 0 empty |
| Area from geometry, km² | 0.74 min, 7.28 median, 4,309.7 max, 67,370 in all. The `AREASQKM` field agrees within 0.02 percent |
| Lakes under 9 and under 25 native pixels by area | 1 and 177 |
| Unnamed features | 455 |
| Fields beyond NHDPlus | `shore_dist`, `max_window`, `new_flag`, `POINTID`, and `_1` duplicates, undocumented on the project page |

What it shows. The universe of assumption A9 exists, is keyed by COMID without gaps, and lands on the CyAN grid's projection. The count matches the HAB_PoC repository's access of 2026-07-02.
What it does not show. Which NHDPlus version the COMIDs follow, or whether the polygons match current shorelines. The 15 invalid geometries are counted, not repaired.

### 7. The per-lake table: 1,387,958 rows for 2,321 lakes under decision 0002, 2026-09-23

Script `datasets/cyan/derive/build_lake_table.py`, recipe `decision-0002-v1`. Table `data/cyan/derived/cyan_lake_table-2026-09-23T1436Z.parquet`, 32,581,188 bytes, ignored by git, with its provenance sidecar. Summary [lake-table-2026-09-23T1436Z.json](../datasets/cyan/outputs/lake-table-2026-09-23T1436Z.json). Built 2026-09-23T14:34:34Z to 14:36:01Z, 1 minute 27 seconds for 598 files, each read once in full. `measured`

| Measure | Value |
|---|---|
| Lakes in the shapefile, lakes with an interior pixel | 2,321, 2,321 |
| Interior pixels per lake | min 3, median 44, 90th percentile 354, max 46,186, 541,510 in all |
| Lakes under 9 and under 25 interior pixels | 51 and 688 |
| Touched pixels the interior rule discards, per lake | median 61 percent, 90th percentile 78 percent |
| Rows | 1,387,958, one per lake and file: 1,257,982 weekly and 129,976 daily |
| Weekly lake-weeks with at least one valid pixel | 1,040,186 of 1,257,982, 82.7 percent |
| Weekly lake-weeks with `valid_frac` of at least 0.5 | 947,460, 75.3 percent. Median `valid_frac` 0.933 |
| Mean weekly `valid_frac` by year | 0.73 in 2016, 0.64 in 2017, 0.64 in 2018, 0.70 in 2019, 0.75 in 2020, 0.74 in 2021, 0.72 in 2022, 0.69 in 2023, 0.78 in 2024, 0.74 in 2025, 0.74 in 2026 to date |
| Weekly lake-weeks whose median code is 130 or more | 124,104, which is 11.9 percent of those with a valid pixel. Reported as a distribution, not a bloom claim |

What it shows. The shapefile is already limited to lakes the sensor resolves, so every lake yields interior pixels. The strict interior rule keeps well under half of the pixels a lake polygon touches, and 688 lakes rest on fewer than 25 pixels. Cloud and ice leave one weekly lake-week in six without any valid pixel.
What it does not show. Whether any value is right. Whether the discarded shoreline pixels carry signal. The 130 threshold is the EPA forecast paper's operationalization and is reported here only to describe the table.

### 8. The lake dashboard data: 2,321 lakes, the newest 104 weeks on one page, 2026-09-23

Script `datasets/cyan/viz/build_lake_dashboard.py` over the table of measurement 7. Summary [lake-dashboard-2026-09-23T1846Z.json](../datasets/cyan/outputs/lake-dashboard-2026-09-23T1846Z.json). Built 2026-09-23T18:46:37Z in 46 seconds, with names, states, the newest week's pixel overlays carrying the raw codes, and each lake's exact outline. Earlier runs at 15:13Z, 15:22Z, 16:18Z, 16:38Z, and 17:02Z produced the same counts and their summaries stay in `datasets/cyan/outputs/`. `measured`

| Measure | Value |
|---|---|
| Lakes on the page | 2,321, every lake with a row in the table |
| Newest weekly file | 2026-09-13 to 2026-09-19 |
| Lakes in that week at the build line, median of 130 or more with any valid pixel | 566 at or above, 1,679 below (967 of them with some pixel above zero), 76 without a valid pixel |
| Consecutive weeks at or above 130 ending in that week, strict, whole record | 3 lakes at 104 or more and 18 at 52 or more. The longest: Hamilton, Lake, COMID 16793819, and Howard, Lake, COMID 16794057, and Apopka, Lake, COMID 16632086, all in Florida |
| Names | 1,866 from the shapefile, 345 from a GNIS point inside the polygon, 19 from a GNIS point within 300 m, 91 lakes unnamed and shown by COMID. Measurement 9 |
| `data/lakes.js`, `data/basemap_land.js` | 3,122,804 and 559,819 bytes, tracked. The simplified `outlines.js` of earlier builds is no longer written |
| States by centroid | 46 states, every lake assigned, 2 by nearest state. Minnesota 414, Maine 199, Texas 138, Michigan 137, Florida 133 |
| Pixel overlays from `L20262562026262`, 2026-09-13 to 2026-09-19 | 2,321 files, 66,755,331 bytes in all, ignored by git. Each is the lake's window warped to Web Mercator at twice the native resolution, once coloured and once as raw codes, plus the exact outline to 6 decimals, which is most of the bytes |
| Per-lake series files `data/lakes/<comid>.js` | 2,321 files, 73 MB, ignored by git |
| Companion attribute table `data/cyan/derived/cyan_lake_attributes-2026-09-23T1846Z.parquet` | 2,321 rows, 20 columns with the state, ignored by git. Interior cell indices sum to 541,510, equal to measurement 7 |
| Cross-check of one lake | Apopka, Lake: the page series, the parquet row, and the attribute row agree on the newest week's median 176, 90th percentile 180, maximum 198, 1,284 valid of 1,284 interior pixels, and a strict run of 147 weeks |

What it shows. The page reproduces the table without transformation, and an independent recount of the newest week's classes from the page data matches the page's own counts. What it does not show. Whether 130 is the right line for any use. The counts move with the line and the coverage control.

### 9. Names for every lake by COMID, from the shapefile and the GNIS point inside the polygon, 2026-09-23

Scripts `datasets/cyan_lakes/access/pull_gnis.py` and `datasets/cyan_lakes/derive/build_name_crosswalk.py`, recipe `gnis-crosswalk-v2`. Summary [lake-names-2026-09-23T1615Z.json](../datasets/cyan_lakes/outputs/lake-names-2026-09-23T1615Z.json), CSV [lake-names-2026-09-23T1615Z.csv](../datasets/cyan_lakes/outputs/lake-names-2026-09-23T1615Z.csv). A first run at 16:13Z under recipe version 1 kept historical names and chose the candidate nearest the polygon's representative point. It named a reservoir after a submerged historical lake and a bay, so version 2 excludes historical names and prefers the candidate farthest from the shoreline. Both runs stay in `datasets/cyan_lakes/outputs/`. `measured`

| Measure | Value |
|---|---|
| USGS NHDPlus waterbody layer, queried for the four largest unnamed lakes on 2026-09-23 | `gnis_name` blank for all four. The shapefile's blanks are NHDPlus blanks. `probe` |
| GNIS national file | `DomesticNames_National_Text.zip`, 38,581,543 bytes, published 2026-08-28, sha256 `e2dc959d762a…` in the manifest. 981,706 features, 143,334 of class Lake or Reservoir |
| Lakes named from the shapefile, from a GNIS point inside, from a GNIS point within 300 m, unnamed | 1,866, 345, 19, 91 |
| Shapefile names with a GNIS point inside, of which the chosen GNIS name is the same name | 1,789 and 1,579. The rest differ in spelling or choose a different feature, which bounds the heuristic's error near 12 percent |
| Newly named lakes with several candidates | 108 of 364. The alternatives travel with every row and show on the dashboard |
| Largest newly named | Lake Okeechobee, Lake Pontchartrain, Lake Champlain, Lake Mead, one candidate or a clear winner each. Two picks the owner may overrule: Goose Lake for COMID 167267897 where Lake of the Ozarks is an alternative, and Agency Lake for COMID 120054054 where Upper Klamath Lake is an alternative |
| Run time | 2 seconds |

What it shows. Names now exist for 2,230 of 2,321 lakes. What it does not show. Which of several GNIS features inside one polygon is the lake's own name. The chosen one is a heuristic, assumption A22.

### 10. The pixel masks against exact polygon geometry, and the displacement of simplified outlines, 2026-09-23

Script `datasets/cyan/qaqc/check_lake_masks.py`. Result [mask-check-2026-09-23T1842Z.json](../datasets/cyan/outputs/mask-check-2026-09-23T1842Z.json). 70 lakes: 60 drawn at random with seed 0 plus the 10 largest, 877,294 window cells, 55 seconds. For every cell the exact coverage fraction is the area of the cell's intersection with the full-resolution polygon over the cell area, computed with Shapely, and compared with the classes of the 8 by 8 oversampled rasterization of decision 0002. `measured`

| Measure | Value |
|---|---|
| Interior cells in the masks, of which the exact fraction is under 0.999 | 160,892 and 1,533, which is 0.95 percent. No cell with an exact fraction of 0.999 or more is missing from the masks |
| Lowest exact fraction of any cell the masks call interior | 0.9441, on Great Salt Lake. The median across lakes of that lowest fraction is 0.989 |
| Touched cells in the masks, and cells the exact polygon touches that the masks miss | 201,227 and 2,703, which is 1.3 percent of the touched count. The largest exact fraction of any missed cell is 0.0528. No mask cell is touched without exact overlap |
| Share of window cells where the two classifications disagree | 0.17 percent for interior, 0.31 percent for touched |
| Displacement of the 300 m simplified outlines drawn on the dashboard until this date | Hausdorff distance to the exact outline: median 286 m, maximum 428 m. Vertices per lake: median 311 exact, 15 simplified |

What it shows. The masks never miss a wholly inside cell and never touch a cell the polygon does not reach. The 8 by 8 sub-grid, which samples a cell at 64 points about 37 m apart, counts as interior a cell whose corner a sliver of shore clips by up to 5.6 percent of its area, and misses slivers thinner than one sample. The outlines the dashboard drew were displaced by about one pixel, which is what made the pixels look mislabelled. What it does not show. Whether the shapefile's shoreline is right. The check is against the polygon as published.


### 11. A year of per-lake pixel images: what it costs in bytes, 2026-09-23

Script `datasets/cyan/viz/estimate_pixel_history.py`. Result [pixel-history-2026-09-23T1952Z.json](../datasets/cyan/outputs/pixel-history-2026-09-23T1952Z.json). All 2,321 lakes, the newest 52 weekly files, 2025-09-14 through 2026-09-13, 13 minutes. For each file and each lake the script encodes the coloured PNG and the grey code PNG exactly as the dashboard builder does and counts the base64 data URLs as served. `measured`. A first run, `pixel-history-2026-09-23T1938.json`, counted the outlines at full coordinate precision instead of the 6 decimals the page serves, and is superseded.

| Measure | Value |
|---|---|
| Served today, all lakes: images for the newest week, and the exact outlines | 6,088,476 B of images and 60,993,186 B of outlines, 67,081,662 B together. The outlines are 91 percent. The served folder measures 66,755,331 B, within 0.5 percent: the script keeps trailing zeros in coordinates that the builder drops, and the served files add a wrapper |
| Images per weekly file, all lakes, over the 52 files | mean 5,408,993 B, from 4,606,496 B to 6,606,348 B. The grey code PNG alone: mean 1,701,555 B |
| 52 weeks of images as built, all lakes | 281,267,636 B, 46 times the newest week |
| 52 weeks of the grey code PNG alone, with the alpha mask sent once per lake | 88,480,904 B of codes and 1,381,350 B of masks |
| 52 weeks of the grey code PNG stacked into one PNG per lake | 52,743,014 B, 60 percent of the separate code PNGs |
| One lake, one week, as built | median 1,155 B, 90th percentile 4,611 B, largest 113,361 B on Lake Okeechobee |
| One lake, 52 weeks, as built, and as stacked codes | median 60,100 B and 5,522 B. 90th percentile 239,812 B and 44,326 B. Largest 5,894,796 B and 1,752,766 B, Lake Okeechobee |
| The page and the up-front lake file | unchanged by any of this: `index.html` 46,957 B, `lakes.js` 3,122,780 B |

What it shows. A year of pixels for every lake costs 281 MB as the page encodes them today, or 53 MB with the codes stacked per lake and coloured in the browser, against 67 MB served today, most of it outlines. Split into one file per lake per week, what the browser fetches for one lake and one week stays what it is today. The page and the up-front data do not grow at all. What it does not show. The bytes for daily composites, or for the whole weekly record since 2016, which is 543 files and about ten times the year.
