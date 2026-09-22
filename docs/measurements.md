# Measurements

What checked-in scripts measured, with the result file behind each number and what the number does not show. Never edit a result file by hand. Rerun the script.

## CyAN

### 1. The cloud copy is a byte-identical but lagging and incomplete mirror, 2026-09-22

Script `datasets/cyan/access/compare_routes.py`. Result [route-comparison-2026-09-22.json](../datasets/cyan/outputs/route-comparison-2026-09-22.json). Run from the owner's laptop, outside us-west-2, with an Earthdata token. 2 minutes 32 seconds. `measured`

| Measure | Value |
|---|---|
| Weekly whole-region files the file search listed for 2016-01-01 to 2026-09-22 | 560, of which 542 in the `CYAN` stream and 18 `CYANV6T` duplicates of weeks in 2022 and 2023 |
| Files the cloud HTTPS endpoint served with HTTP 200 | 529, all `CYAN` stream |
| Files it answered with HTTP 404 | 31 |
| Of those, `CYANV6T` duplicates whose `CYAN` twin is present | 18. No data lost |
| Of those, weeks newer than the endpoint's newest file | 7, window starts 2026-08-02 through 2026-09-13 |
| Of those, `CYAN` files older than the newest yet absent | 6, window starts 2025-04-27, 2025-07-06, 2025-07-13, 2025-08-24, 2025-09-21, 2026-01-18 |
| Newest window end on the endpoint and in the cloud catalog | 2026-08-01, against 2026-09-19 in the file search |
| Cloud catalog granules matching the weekly whole-region pattern | 529, equal to the endpoint count |
| Temporary credentials endpoint | HTTP 200, credentials issued |
| Bucket listing with those credentials from outside us-west-2 | Refused, `AccessDenied` |
| Sample files downloaded through both routes and compared | 2 of 2 identical by sha256, 5,886,210 and 6,175,066 bytes |

What it shows. Where the cloud copy holds a file, the bytes equal the archive's. The copy trails the archive by 7 weeks and lacks 6 weekly files from the last 17 months. Listing the bucket needs compute inside us-west-2. The HTTPS endpoint answers from anywhere with a token.
What it does not show. Whether the bucket itself lacks the 6 files or only the endpoint's index does. Whether the lag is constant. Daily and tile files were not compared.

### 2. The archive itself lacks one weekly file, 2026-09-22

Same result file, and the plan file below. From 2016-04-24 to 2026-09-13 there are 543 weekly start dates. The file search lists 542 `CYAN` weeks. The week starting 2026-07-05 is absent from the archive listing. `measured`

### 3. Dry-run plans for the assumption A8 scope, 2026-09-22

Script `datasets/cyan/access/pull_cyan.py --dry-run`. Results [plan-weekly-mosaic-2026-09-22.json](../datasets/cyan/outputs/plan-weekly-mosaic-2026-09-22.json) and [plan-daily-mosaic-2026-09-22.json](../datasets/cyan/outputs/plan-daily-mosaic-2026-09-22.json). `measured`

| Scope | Files | First | Last | Streams |
|---|---|---|---|---|
| Weekly whole-region, 2016-01-01 to 2026-09-22 | 542 after collapsing 18 duplicates | 2016-04-24 to 2016-04-30 | 2026-09-13 to 2026-09-19 | `CYAN` only |
| Daily whole-region, 2026-07-28 to 2026-09-22 | 56 | 2026-07-28 | 2026-09-21 | `CYAN` only |

Size estimate: the two sampled weekly files were about 6 MB each, and the catalog probe gave 4.5 MB for a daily file. That makes about 3.3 GB weekly plus about 0.25 GB daily. Under the limit of assumption A16. `unverified` until the pull measures it.
