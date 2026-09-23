# Step 1f, CyAN lake dashboard: every lake's weekly state under a movable bloom line, a ranked list, a per-lake deep dive, and the companion attribute table, 2026-09-23

Implementer: Claude Code (AI coding agent), directed by the repository owner. Scope: step 1f of [the work plan](../work-plan.md). Two public archives were fetched, the EPA forecast code deposit and the USGS GNIS names file, and one USGS map service was queried read-only. No CyAN provider was contacted. Nothing is committed. The owner gave four rounds of feedback on 2026-09-23, dispositioned below. The third round also asked for a check of six assertions contrasting the EPA and Copernicus products, recorded in a separate probe.

## What the owner directed

The owner approved step 1e on 2026-09-23 and said to proceed. The work plan names the HAB_PoC "current active blooms" view as the reference for step 1f and leaves the specification to the owner. The companion per-lake table with centroids, windows, and interior cell indices was folded into this step on the 1e review. This record delivers a first version built on that reference and lists the choices the owner may want to change.

## What changed

| Area | Change |
|---|---|
| Evidence for the bloom line | The EPA forecast code deposit, DOI 10.23719/1529140, fetched and read. [Probe record](../probes/2026-09-23-epa-forecast-code-deposit.md). Preserved under `datasets/epa_cyanohab_forecast/reference/` with hashes. The 130 threshold and the whole-pixel rule move from `prior` to `probe`. Decision 0002 carries a dated note on the three things the EPA code does that the recipe does not |
| Builder | `datasets/cyan/viz/build_lake_dashboard.py` with 5 offline tests. Reads the per-lake table and the lake shapefile, computes nothing new from pixels. Writes the page data, the per-lake series files, the companion attribute table, and a stamped summary |
| Page | `docs/dashboards/cyan-lakes/index.html`, two tabs and a FAQ dropdown, offline, self-contained with its own `vendor/` copies, byte-identical to the review dashboard's. Names the file at fault at the top when one fails to load. [README](../dashboards/cyan-lakes/README.md) |
| Context and pixels | `datasets/cyan/viz/pull_basemap.py` pulls Natural Earth 1:50m countries and lakes, manifested, clipped to North America. The builder assigns each lake a state by centroid and writes the newest weekly file's pixels per lake as a coloured Web Mercator PNG plus a grey PNG of raw codes, loaded on demand. Registry row `natural_earth`. The page streams Esri World Imagery as an optional basemap, the only external request, with the service's own attribution |
| Mask check | `datasets/cyan/qaqc/check_lake_masks.py`, exact coverage fractions against the masks for a sample of lakes, stamped result under `datasets/cyan/outputs/`. Measurement 10 |
| Names | `datasets/cyan_lakes/access/pull_gnis.py` pulls the USGS GNIS national names file, manifested. `datasets/cyan_lakes/derive/build_name_crosswalk.py` names every lake from the shapefile or from the GNIS point inside its polygon, with 2 offline tests. Tracked CSV under `datasets/cyan_lakes/outputs/`. [Measurement 9](../measurements.md#9-names-for-every-lake-by-comid-from-the-shapefile-and-the-gnis-point-inside-the-polygon-2026-09-23). Assumption A22 |
| Companion table | `data/cyan/derived/cyan_lake_attributes-2026-09-23T1618Z.parquet`: per lake, the COMID, name and its source, area, centroid, EPSG:5070 bounds, pixel window, interior and touched counts, and the flat indices of the interior cells. Ignored by git |
| Documents | [Measurement 8](../measurements.md#8-the-lake-dashboard-data-2321-lakes-the-newest-104-weeks-on-one-page-2026-09-23) and 9. CyAN METADATA section 9, decision 0002 note, registry rows for `cyan` and `usgs_gnis`, assumption A22, work plan, probe and review indexes, outputs READMEs, `.gitignore` for the series files |

## What the page shows and does not show

- **Map tab.** Controls left, map in the middle, ranked list right. Every lake as a circle on its centroid, coloured by its state in the selected week: at or above the bloom line in four run-length buckets, below the line, or no data. Outlines from zoom 8, North American land and large lakes beneath. A slider over the newest 104 weeks. The bloom line defaults to a median code of 130 and is movable. A checkbox draws the newest week's pixels for the lakes in view past zoom 8. "More options" holds the coverage minimum and the run-bridging choice. The list ranks the lakes at or above the line by run length.
- **Lake tab.** Filters by state, by status in the newest week, and by name or COMID. Opens on the first lake alphabetically. Leads with the weekly median, 90th percentile, maximum, and coverage over the whole record, then the daily composites beside a small map of the lake's newest-week pixels, then the newest 16 weeks as a table, then the facts at the bottom.
- **FAQ.** A dropdown at the top right explains the data, the terms, the limits, and the sources in plain language. No decision, script, or hash is named on the page. Those stay in this record and in the stamped summaries.
- It does not show a forecast, a probability, a toxin level, a pixel value, or a validated value. The 130 line is labelled as the EPA code's operationalization, not as a fact about any lake.

## Build

46 seconds for 2,321 lakes with the pixel overlays and exact outlines. `data/lakes.js` 3.1 MB and `data/basemap_land.js` 0.6 MB are tracked. The 2,321 pixel files, 67 MB with the exact outlines, are ignored by git. The 2,321 series files, 73 MB, are ignored by git and regenerable. Earlier runs at 15:13Z and 15:22Z, before names, produced identical counts and stay under `datasets/cyan/outputs/`. The name crosswalk ran twice, at 16:13Z under recipe version 1 and at 16:15Z under version 2, and both results stay.

## Findings

1. **The newest week, 2026-09-13 to 2026-09-19, at the build line.** 566 lakes at or above a median of 130, 1,679 below, 76 without a valid pixel. An independent recount from the page data matches the page's own counts.
2. **Long runs are concentrated in Florida.** The three longest strict runs at 130, all above two years, are Hamilton, Lake, Howard, Lake, and Apopka, Lake, at 179, 154, and 147 weeks. 18 lakes have run a year or more. The map shows the cluster.
3. **455 of 2,321 lakes carry no GNIS name in the shapefile, and NHDPlus has none for them either.** The USGS waterbody service returns blank names for the same COMIDs, so no lookup by COMID alone can help. The GNIS point-in-polygon crosswalk names 364 of them, Lake Okeechobee, Lake Pontchartrain, Lake Champlain, and Lake Mead among them, and 91 stay unnamed. Where several GNIS features lie inside one polygon the choice is a heuristic, and two large picks look wrong to the implementer: Goose Lake for COMID 167267897 with Lake of the Ozarks as an alternative, and Agency Lake for COMID 120054054 with Upper Klamath Lake as an alternative. The page shows the alternatives. The EPA forecast's public lake names, step 2, are the better source for the lakes it covers.
4. **The EPA code confirms the recipe where they overlap and differs in three places.** Whole pixels only, median with missing dropped, code 0 kept, codes above 253 dropped, bloom at 130. The EPA code also applies a fixed mixed-pixel mask that is not in the deposit, masks ice, and fills ice-masked weeks with no bloom before training. The page's Limits section says so.
5. **The companion table closes the loop with measurement 7.** Its interior cell indices sum to 541,510, the same count the extraction used.

## Checks

| Check | Result |
|---|---|
| `uv run pytest -q` | 144 passed. No network |
| `uv run ruff check .` and `uv run ruff format --check .` | Pass |
| Headless render, Chrome for Testing | Both tabs render with no console error. The map tab's counts, week label, threshold readout, and 566 list rows read back from the DOM, and 13 FAQ entries are present. The Lake tab opens on Abamgamook Lake, Maine, with 3 plots, 16 table rows, and one pixel overlay. The pixel view at zoom 11 over central Florida draws 25 overlays, and the screenshots show them. A first version put the overlays in Leaflet's default pane, where the land canvas covered them, so they were in the DOM but invisible. They now sit in a pane above the land and below the outlines. The Apopka, Lake facts match the parquet row: median 176, 90th percentile 180, maximum 198, 1,284 valid of 1,284 interior pixels |
| Cross-check | One lake's page series, parquet rows, and attribute row agree. The builder's whole-record run for Apopka, Lake, 147 weeks, equals a recount from the parquet |

## Limits

- The page carries the newest 104 weeks for every lake and the whole record per lake on demand. A run that reaches the window's start shows as 104 or more on the map. The Lake tab shows the true run.
- The coverage control defaults to any valid pixel, which matches the EPA code, so a lake seen on one pixel gets a median from one pixel.
- The interior rule of decision 0002 discards every shoreline pixel. A bloom confined to a shore is invisible here, as in the table.
- No basemap tiles. The page is offline by design, like the review dashboard. State outlines are the only context.
- A fresh clone needs one run of the builder before the Lake tab works, because the series files are not tracked.
- A crosswalk name chosen among several candidates is a label, not a fact about the lake. COMID stays the key, assumption A22.

## Owner decisions requested

1. The defaults: bloom line 130, coverage any valid pixel, strict runs, four run buckets as in HAB_PoC, 104-week window. Any of these can change without a rebuild except the window.
2. Whether "detecting", a median under the line with some pixel above zero, deserves its own colour on the map. Today it is only visible in the median colouring and the popups.
3. Whether to overrule any crosswalk pick. The two named in finding 3 are the candidates. An override list is a small addition if wanted.
4. Whether the pixel overlays stay limited to the newest week. Every week would cost about 4 MB per week on disk and a rebuild rule.

## Owner feedback, first round, 2026-09-23

| Feedback | Disposition |
|---|---|
| "Name crosswalk by comid (it should be cheap and fast)" | fixed. A lookup by COMID alone returns the same blanks, so the crosswalk goes through the USGS GNIS names by point in polygon. 364 lakes newly named, 91 remain. Measurement 9, finding 3 |
| "The html is not populated with data (no maps or visuals display, only the framework and basic text)" | corrected with evidence, cause not confirmed. The headless render populates every tab, so the failure is in how the page was opened. The likeliest cause is the page's references to the sibling folder `../cyan/`, which a viewer that serves one folder cannot reach. The page is now self-contained, and when a file fails to load it names the file at the top. If the page still opens empty, the message at the top says which file is missing, and the implementer needs the browser's name and that message |

## Owner feedback, second round, 2026-09-23

| Feedback | Disposition |
|---|---|
| Remove the text naming scripts and decisions, and every reference to decisions | fixed. The page names no decision, script, or hash. The FAQ describes what is on the page in plain language |
| Remove the Provenance tab | fixed. Its plain-language parts moved into the FAQ. Build details stay in the stamped summary and this record |
| Simplify the left side of the map tab and put detailed and technical information into a FAQ at the top right, toggled off | fixed. Left panel: week, bloom line, colouring, pixel toggle, legend, counts, and a collapsed "More options" for coverage and bridging. FAQ button at the top right with 13 entries |
| Lake tab: filters by state and by in bloom or not, open on the first lake alphabetically | fixed. State by lake centroid against the Census outlines, status in the newest week at the current bloom line, plus a find box. Opens on Abamgamook Lake, Maine |
| Lake tab: metadata boxes at the bottom, lead with the weekly plot. What does "run at the line, newest week" mean | fixed. The facts sit at the bottom. The label now reads "Consecutive weeks at or above the bloom line, ending with the newest week", which is what it counts |
| Toggle a raster of index values within a lake, perhaps the most recent week only, served on demand | fixed. The newest weekly file's pixels per lake as a coloured image in Web Mercator, 4.4 MB for all lakes, loaded on demand. On the Map tab past zoom 8 with a checkbox, and always on the Lake tab's small map. Pixels wholly inside the outline at full strength, touched pixels faded |
| Move the ranked list to the far right, map in the middle | fixed. Three panels |
| Add outlines for the North American continent | fixed. Natural Earth 1:50m countries and large lakes, public domain, pulled and manifested, clipped to North America, beneath the state outlines, with water and land colours |

## Owner feedback, third round, 2026-09-23

| Feedback | Disposition |
|---|---|
| Pixels look fuzzy, they should be crisp | fixed. The overlay images render with no interpolation, so each 300 m pixel is a sharp square at every zoom |
| Add a hover to inspect values | fixed. Each pixel file now carries the raw codes as a grey image. Moving the mouse over a lake's pixels reads the lake, the code, the converted index, and whether the pixel is counted, into a box on the map and under the Lake tab's small map. A headless probe at a point inside Apopka, Lake read code 178, wholly inside, counted |
| Add a basemap, preferably earth imagery | fixed. Esri World Imagery as a tile layer beneath everything, on by default, with a checkbox to turn it off, land fills hidden while it shows, and an automatic fallback to outlines when a tile fails. Attribution as the service states it. Whether Esri's terms allow a public deployment without an API key is an open item in the page README |
| Lakes on the map are not clickable | fixed. The circles had moved to a canvas beneath the outlines' canvas when the panes were split for the pixels, so the upper canvas took the clicks. Circles and outlines now share one canvas above the pixels, and a click on either opens the same popup as a click on a row in the list |
| Check six assertions contrasting EPA CyAN and Copernicus Lake Water Quality | corrected with evidence. [Probe record](../probes/2026-09-23-cyan-vs-clms-assertions.md): two confirmed, four partly right. The main corrections: the index uses 665, 681, and 709 nm with a 620 nm phycocyanin test; Copernicus version 2 carries a floating cyanobacteria index; Lakes_cci version 3.0.0 adds a prototype phycocyanin concentration. Two manuals and one paper's full text preserved under `reference/` |

## Owner feedback, fourth round, 2026-09-23

| Feedback | Disposition |
|---|---|
| Many pixels look mislabelled against the lake polygon. Check whether the polygons are simplified. If so, drop them, or reassess the pixel classification | corrected with evidence. The drawn outlines were simplified to 300 m, one pixel, and sat a median 286 m and up to 428 m from the true shore. The classification is sound: a new check script compares the masks with exact coverage fractions on 70 lakes and finds no wholly inside cell missed and no cell touched without overlap, with under one percent of interior cells clipped by shore slivers thinner than the sub-grid. [Measurement 10](../measurements.md#10-the-pixel-masks-against-exact-polygon-geometry-and-the-displacement-of-simplified-outlines-2026-09-23). The page now draws only exact outlines, loaded per lake with the pixels from zoom 9, and the simplified outline file is gone. Decision 0002 carries a dated note on the precision of the rule |
| Move the basemap toggle out of the panel onto the map, top right | fixed. A Leaflet control at the top right of both maps, sharing one state |

## Owner feedback, fifth round, 2026-09-23

| Feedback | Disposition |
|---|---|
| Add column names to the ranked list on the Map tab: location, wks in bloom, value | fixed. A header row that stays at the top of the list while it scrolls. Hovering a column name explains it: weeks in bloom are the consecutive weeks at or above the bloom line ending with the selected week, and value is the median index code in that week |
| Change "not seen" to "no data" | fixed. Every place the page said "not seen" now says "no data": the legend, the counts, the Lake tab filter, the facts, the weekly table, and the FAQ. The class key in the served data and in the stamped summary is `no_data` instead of `not_seen`, and the data was rebuilt, summary `lake-dashboard-2026-09-23T1923Z.json`. Pixels that carry no value keep the words "no value" |
| Is the page standalone, or do the supplementary files travel with it? Asked while the commit was being prepared | corrected with evidence. Not standalone: the page loads `vendor/` and `data/` by relative path. Preparing the commit showed that the ignore rule `data/`, written for the root data folder, matched every folder named `data`, so no dashboard data file had ever been committed, for this page or for the step 1d page, although the step 1d record said they were tracked. That is the likely cause of the first-round report of an empty page, which a local render could not reproduce. The rule is now `/data/`, root only. The up-front files, `lakes.js` and the two basemaps here and `summary.js` and the states there, are committed. The per-lake series and pixel files stay out of git, 4,642 files and about 140 MB, rebuilt by the builder. The README lists what must travel with the page |
| Estimate how much larger the page would be with a year of pixel images per lake, or whether that would explode it | corrected with evidence. The page itself would not grow at all. The pixel images are separate files loaded one lake at a time, and the outline, not the images, is 98 percent of those files today. A year of images was measured, not estimated: all 2,321 lakes over the newest 52 weekly files cost 281 MB encoded as today, or 53 MB with the codes stacked into one image per lake and coloured in the browser, against 67 MB served today. Split into one file per lake per week, a lake's fetch stays what it is today, and the page and the up-front lake file do not grow. [Measurement 11](../measurements.md#11-a-year-of-per-lake-pixel-images-what-it-costs-in-bytes-2026-09-23). Whether to serve the year, and in which encoding, is an owner decision |

## Authorization

After the fourth round the owner approved the page and authorized commit and push. The commit was interrupted before it ran, and the owner then asked for the fifth round. On 2026-09-23 the owner approved the fifth round and authorized commit and push of the whole step.

## Proposed next step

Step 1g, the AWS note for CyAN. Before that, a Codex second-model check of the probe record on the six assertions, and the owner's decisions listed above.
