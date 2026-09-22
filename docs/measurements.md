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
