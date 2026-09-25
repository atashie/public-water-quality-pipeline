# The SFEI harmful algal bloom map surveyed through its public documentation, 2026-09-25

A scientist's feedback of 2026-09-25 asked the lake dashboard to adopt features of `https://fhab.sfei.org/`, including how it accounts for data gaps. It is item F9 in [the revision record](../reviews/2026-09-25-cyan-lake-dashboard-scientist-feedback.md). The parent agent, Claude Code, ran this survey on 2026-09-25. It is a `probe`: what the pages said on that date, not checked by a second agent. Every quote is verbatim from a copy saved in the implementer's scratch folder. The copies are not committed. Their hashes are listed at the end.

## The map itself did not load

- The implementer's fetch tool received HTTP 403 from `https://fhab.sfei.org/` earlier on 2026-09-25.
- At 16:56 UTC headless Chrome for Testing 1.62 through Playwright received HTTP 403 and a page titled "Just a moment...". Its text read "Performing security verification" and named Cloudflare. The page stayed there for 12 seconds. The implementer did not try to get past the check.
- The Claude browser extension was not connected, so the owner's own Chrome was not available.

The survey therefore reads four public sources about the map. They describe what it does. They do not show its screens, its legend wording, or how its charts draw a week without data.

| Source | What it is |
|---|---|
| `https://fhab-api.sfei.org/` and its pages `/reference`, `/pixelvalues`, `/examples`, `/glossary`, `/howto` | The documentation of the application programming interface behind the map, by the San Francisco Estuary Institute. Not behind the bot check |
| `https://mywaterquality.ca.gov/habs/resources/satellite-map.html` | The California Water Quality Monitoring Council's page introducing the map |
| Smith, J. et al. (2025-03), Best Practices to Employ Satellite Remote Sensing to Assess Freshwater Harmful Algal Blooms in Inland Waters of California, Southern California Coastal Water Research Project, `https://www.waterboards.ca.gov/water_issues/programs/swamp/docs/2025/ca-satellite-tech-report-2025.pdf` | The state's best-practices report on the same satellite data. It describes the map and recommends processing steps |
| `https://www.sccwrp.org/web-based-tool-helps-analyze-visualize-inland-habs-satellite-monitoring-data/` | A news item of 2026-05-01 on a second, separate California tool. Noted, not surveyed |

## What the map serves

1. **A different processing of the same satellites.** The map shows NOAA's processing of Sentinel-3 OLCI and, for 2002 to 2012, MERIS. The report says "NOAA processes the satellite data with minor variations compared to the CyAN project, so CIcyano values from the two sources may have slight differences." The pixel codes differ too. The map's codes above 250 mean no data, and 252 means land. CyAN uses 254 for land and 255 for no data.
2. **255 waterbodies in California.** "Zonal statistics are then derived for 255 waterbodies being tracked across California (including a few in bordering states)".
3. **Composites over 1 and 10 days.** "The resultant rasters are further composited into pixel-maximum composites (1-day and 10-day) to smooth out general noise and variability and better assess large-scale trends." The interface also offers a running 7-day maximum and the uncomposited daily mosaics. CyAN's weekly file is a fixed 7-day maximum.
4. **Five statistics per waterbody and date, each with its pixel count.** The statistics are the minimum, maximum, mean, median, and 90th percentile. `pixel_count` is "The observed pixel count for the given waterbody at the requested date." For daily mosaics a second field gives the count per satellite.
5. **Values in four units.** Raw codes, the cyanobacteria index, a "modified" index, and chlorophyll-a. The modified index is "Pixel values converted to cyano index and a multiplier of 15,805.18, which adjusts the value range to 1-1,000." The map shows the modified index, "as given in the FHAB Web Map".
6. **A cell-count equivalent.** The index "can be related to estimated Microcystis sp. cell concentration (in cells/mL) by a multiplier of 100,000,000." The pixel table adds that "These conversions have not be field verified for water bodies in California and are provided only for reference."
7. **Named levels on the scale.** The pixel table marks rows with comments, quoted below without their footnote markers. The research record of part 3 checks them before this repository uses any of them.

   | Map code | Index | Cells per mL | Comment on the row |
   |---|---|---|---|
   | 0 | ≤6.310e-05 | ≤6,310 | Background Level / Non-Detect. The footnotes apply "Background Level" to the index and "Non-Detect" to chlorophyll-a |
   | 42 | 2.015e-04 | 20,147 | NOAA Minimum Risk Threshold / 'Moderate' Estimated Abundance Threshold |
   | 100 | 1.001e-03 | 100,111 | 'High' Estimated Abundance Threshold |
   | 130 | 2.294e-03 | 229,416 | FHAB Notification Threshold |
   | 184 | 1.021e-02 | 1,020,666 | 'Very High' Estimated Abundance Threshold |
   | 250 | >6.327e-02 | >6,327,038 | Maximum Detectable Level |

   The notification row's footnote reads "Threshold for this notification corresponds with the World Health Organization Alert Level 1 threshold." That row's chlorophyll-a value is 12.10 µg/L. The map's codes follow NOAA's scale. A level carries over to CyAN codes through the index, never through the code number.
8. **A color for each kind of missing value.** The pixel table colors no data, invalid, cloud, land, and adjacency to land in five different grays and white. CyAN's files mark only land and no data.
9. **Notifications.** "When a newly-formed bloom is identified by satellites, notifications are sent to staff at the SWRCB and regional water quality control boards".
10. **Long and short timelines, and paired charts.** The data "is also viewable in long and short timelines to show how concentrations vary over time." Charts for one waterbody "can be used to toggle between data types or view them paired under “comparison graphs” tab."
11. **A screening statement.** "No regulatory decisions, or health advisory postings, should occur based solely on information from the map." Also: "The map does not show any information about toxin concentrations and public health advisories."
12. **A data interface.** Every statistic, raster, pixel value, and waterbody outline downloads as JSON, CSV, GeoTIFF, GeoJSON, or KML.

## How the map and the report handle gaps

- **Longer composites.** A 10-day pixel maximum covers more overpasses than a 1-day one, so fewer waterbodies are empty on a given date. The report chose "7-day maximum composite images" because they smooth "potential data gaps from environmental conditions (e.g., clouds, ice, sun glint, etc.)".
- **A pixel count with every statistic.** A reader sees how many pixels stand behind each value.
- **A suitability class per waterbody.** The report classed 47 of 238 waterbodies as "Limited", with "1 – 2 pixels OR 51-90% of Weeks with 0 pixels" over 2017 to 2023. It left them out of statewide summaries and trends. The interface returns a `usetype`, for example "Limited", for each waterbody.
- **A wider outline, not a narrower one.** "waterbody boundaries are given a two-pixel buffer so as not to potentially exclude any valid pixels". This repository does the opposite: only pixels wholly inside the outline count, [decision 0002](../decisions/0002-per-lake-table-recipe.md). The report instead recommends removing the pixels along the outline.
- **Named gaps between sensors.** "There exists a significant data gap between 2012 and 2016, after contact was lost with Envisat and before Sentinel-3A become operational."
- **A warning about more satellites.** The report says "Sentinel-3B was launched in April 2018 and reached its nominal orbit on 23 November 2018 (Clerc et al., 2020)." It adds that maximum 7-day composites "can lead to observed increases in trends due to increased observational frequency through the addition of satellites to the constellation rather than true environmental change". It cites that finding as submitted work. [Measurement 14](../measurements.md#14-weekly-lake-coverage-by-year-before-and-after-the-second-satellite-2026-09-25) finds the matching step in this repository's own coverage between 2018 and 2019.

## Candidate features for the lake dashboard

Each row is a candidate for future work. "Fits" names what already allows each one. Part 3 builds S1, S2, and S4, because they answer the scientist's item F1 and decision 0003.

On 2026-09-25 the owner put the rest on hold. None is scheduled until a user asks for a specific feature. This table is their record.

| # | Feature | Fits | Note |
|---|---|---|---|
| S1 | Estimated cells per mL in every readout, with named levels in the legend | Part 3, once the research record's claims are checked | The page states the conversion is approximate and not field-checked |
| S2 | The screening statement and "no toxin information" near the top of the page | Part 3 | Wording only |
| S3 | The 90th percentile, maximum, and mean beside the median on the Lake tab | Decision 0002 already computes them for every lake and file | Display only. The map would stay colored by the median |
| S4 | A note on sensor periods, 2016 to 2018 with fewer weeks with a value | Part 3, per decision 0003 | Measurement 14 |
| S5 | A download of one lake's weekly rows as CSV | Nothing new is computed | The per-lake files already hold the rows |
| S6 | A suitability class per lake from its share of weeks without a value | Needs a new decision. It is a count across weeks | Useful for the scientist's prospecting use. The report's thresholds were set for California |
| S7 | A running 10-day maximum | Needs a new decision and daily files | This repository keeps 8 weeks of daily files, [assumption A8](../assumptions.md) |
| S8 | Alerts on a new bloom | Needs a weekly refresh, step 1g, and a decision on what counts as a new bloom | |
| S9 | Separate colors for cloud, invalid, and adjacency | Not possible. CyAN's files do not separate them | |

## Saved copies

Accessed 2026-09-25 between 16:57 and 17:00 UTC with `curl` and the user agent `public-water-quality-pipeline/0.1 (probe)`. The SFEI project page `https://www.sfei.org/projects/satellite-imaging-detect-cyanobacterial-blooms` returned HTTP 403.

| URL | Bytes | sha256 |
|---|---|---|
| `https://fhab-api.sfei.org/` | 14,269 | `bd75259ffa6c84b400933dc251e92be73b3c8eba97b3a1f280b00fed75446032` |
| `https://fhab-api.sfei.org/reference` | 62,485 | `ae9331c9568fcc411de4c3ec5e92e6f58f85a421e7d8009da933a8800ebdf82a` |
| `https://fhab-api.sfei.org/pixelvalues` | 98,721 | `fa6d4d243fd98c9b87d94cb1c644bbcccbd9f2c57781db710701bb9105f72029` |
| `https://fhab-api.sfei.org/examples` | 18,194 | `52a15219738a7c0fabae92f60b52a95739de5960a8b8a32db0f9a855b92d2a36` |
| `https://fhab-api.sfei.org/glossary` | 13,744 | `f63bd782e514b7d426de583ba8f83e1bb0a6cbbb7e1ee4233cd266bf32e545d0` |
| `https://fhab-api.sfei.org/howto` | 14,538 | `f8e28489a72d96ed5e825d506f5962c7f6b8eb3b2c4b8c952fcdce8792c0d299` |
| `https://mywaterquality.ca.gov/habs/resources/satellite-map.html` | 24,785 | `d44be336f593ab97d918302eb3eb9f9d2db1db5af427082421580be312b9b224` |
| `https://www.waterboards.ca.gov/water_issues/programs/swamp/docs/2025/ca-satellite-tech-report-2025.pdf` | 18,568,695 | `8c24faaabe2fcac91417b95d128da02c71d6aa0869f5c8d940fc9fbd061958e0` |
| `https://www.sccwrp.org/web-based-tool-helps-analyze-visualize-inland-habs-satellite-monitoring-data/` | 57,754 | `ec9cd10022f9578080e1fd375212bec7c94e2f20d2812c651d57aa03b5faf6b7` |
