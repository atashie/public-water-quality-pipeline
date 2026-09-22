# CyAN file format and OLCI start date confirmed by probes, 2026-09-22

Probes by a subagent of Claude Code, directed by the repository owner. Read-only requests without credentials. No data file downloaded.

## Fact A: the distributed files are GeoTIFF

- A1. CMR granule UMM-G for the three newest granules of C3416412382-OB_CLOUD lists ArchiveAndDistributionInformation with "Format":"TIFF" and "MimeType":"image/tiff" for every granule. probe
- A1. RelatedUrls give a GET DATA href like "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/L2026213.L3m_DAY_CYAN_CI_cyano_CYAN_CONUS_300m.tif" ending in .tif. probe
- A1. The weekly whole-region granule name-pattern search returned 529 hits, and the sampled granules also show "Format":"TIFF" and "MimeType":"image/tiff". probe
- A2. CMR collection UMM-C for C3416412382-OB_CLOUD gives "ArchiveAndDistributionInformation":{"FileDistributionInformation":[{"Format":"netCDF-4"}]}. probe
- A3. The OB.DAAC file search for weekly CONUS files, 2026-09-01 to 2026-09-22, returned only .tif filenames such as "L20262492026255.L3m_7D_CYAN_CI_cyano_CYAN_CONUS_300m.tif". probe
- A3. The same search for tile 1_1 also returned only .tif filenames, for example "L20262492026255.L3m_7D_CYAN_CI_cyano_CYAN_CONUS_300m_1_1.tif". probe
- A4. A HEAD request to the TEA HTTPS granule URL returned HTTP 303 with Location "https://dwgofd1fffpxv.cloudfront.net/head-60d27a6eaf8c854e8c64973f295212af/ob-cumulus-prod-public.s3.us-west-2.amazonaws.com/L2026213.L3m_DAY_CYAN_CI_cyano_CYAN_CONUS_300m.tif" (query string omitted). probe
- A4. A HEAD request to the getfile URL returned HTTP 302 with Location "https://oceandata.sci.gsfc.nasa.gov/getfile/urs/?next=http%3A%2F%2Flocalhost%3A5007%2Fgetfile%2FL20262492026255.L3m_7D_CYAN_CI_cyano_CYAN_CONUS_300m.tif". Byte-level confirmation of the TIFF magic number needs a token and is deferred to step 1b. probe
- A5. The release notes state "Each data file is stored in 8-bit GeoTIFF, where values of:" on PAGE 5. probe
- A5. They also state "The GeoTIFFs now include product version information in metadata" on PAGE 17, item 4 of the version history. probe
- A5. Appendices on PAGE 25, 26, 28, and 29 quote ":oformat = "netCDF4" ;" for an intermediate binned file, not the distributed image. probe
- Conclusion: granule, file search, and release-notes evidence show distributed CyAN images are GeoTIFF. The collection record's netCDF-4 tag names an intermediate binned format, not the shipped file. Byte-level confirmation of the TIFF signature is deferred to step 1b. probe

## Fact B: when the OLCI record starts

- B1. Weekly CONUS search (areaids=all) for 2016-01-01 to 2016-12-31 returned 36 files, earliest "L20161152016121.L3m_7D_CYAN_CI_cyano_CYAN_CONUS_300m.tif". Day-of-year decode gives a start of 2016-04-24 and an end of 2016-04-30. probe
- B1. The same search with period=2 (daily) returned 251 files, earliest "L2016116.L3m_DAY_CYAN_CI_cyano_CYAN_CONUS_300m.tif", which decodes to 2016-04-25. probe
- B1. The weekly search for tile 1_1 over the same year returned the same 36 dates, earliest "L20161152016121.L3m_7D_CYAN_CI_cyano_CYAN_CONUS_300m_1_1.tif". probe
- B2. Weekly CONUS search (areaids=all) for 2013-01-01 to 2015-12-31 returned an HTML page, not a plain file list. probe
- B2. The page states "Your query generated 0 file(s)." confirming no OLCI or MERIS files exist for that gap. probe
- B3. Weekly CONUS search for 2007-01-01 to 2008-12-31 returned 53 MERIS files, earliest "M20073642008005.L3m_7D_CYAN_CI_cyano_CYAN_CONUS_300m.tif". That file decodes to a start of 2007-12-30 and an end of 2008-01-05. probe
- B3. The same search for 2012-01-01 to 2012-12-31 returned 14 MERIS files, latest "M20120922012098.L3m_7D_CYAN_CI_cyano_CYAN_CONUS_300m.tif". That file decodes to a start of 2012-04-01 and an end of 2012-04-07. probe
- B4. The earliest granule of C3416412382-OB_CLOUD by start_date is "MERGED_S3_OLCI_L3m_CYAN_L2016116.L3m_DAY_CYAN_CI_cyano_CYAN_CONUS_300m_1_1.tif_6.0" with time_start "2016-04-25T00:00:00Z". probe
- B4. The latest granule of MERIS collection C3416412319-OB_CLOUD by start_date is "MERIS_L3m_CYAN_M2012098.L3m_DAY_CYAN_CI_cyano_CYAN_CONUS_300m_9_6.tif_6.0" with time_start "2012-04-07T00:00:00Z". probe
- B5. On PAGE 4 the release notes state NASA processes CI-cyano data from "Ocean Colour Land Imager onboard Sentinel-3A (OLCI; 2017-present) and Sentinel-3B (2018-present)". probe
- B5. The same sentence gives MERIS as "Envisat (MERIS; 2002-2012)", matching the last MERIS weekly file found for 2012. probe
- B6. The search form at /api/cyan_file_search/ labels the weekly option "Weekly [2007-Present]" and the 14-day option "14 Day [2002-2007]". probe
- Conclusion: file search and CMR data place the OLCI weekly and daily record's start at 2016-04-24 through 2016-04-25. This matches the collection's 2016-04-25 begin date, not the release notes' 2017 OLCI reference or the form's 2007-Present weekly label. The 2013-2015 empty result and the 2012-04-07 last MERIS file confirm a gap between MERIS and OLCI coverage. probe

## Raw responses

- Saved under /private/tmp/claude-501/-Users-arik-github-public-water-quality-pipeline/d9a1494e-04d3-48e2-af3e-7608b97ebebe/scratchpad/confirm/: A1_newest3_granules.json, A1b_weekly_whole_region.json, A2_collection_umm_c.json, A3_weekly_all_20260901_20260922.txt, A3_weekly_1_1_20260901_20260922.txt, A4_HEAD_tea.txt, A4_HEAD_getfile.txt, B1_weekly_all_2016.txt, B1_daily_all_2016.txt, B1_weekly_1_1_2016.txt, B2_weekly_all_2013_2015.txt, B2_weekly_all_2013_2015_retry.txt, B2_headers.txt, B3_weekly_all_2007_2008.txt, B3_weekly_all_2012.txt, B4_earliest_olci_granules.json, B4_latest_meris_granules.json, B6_form_page.html.
