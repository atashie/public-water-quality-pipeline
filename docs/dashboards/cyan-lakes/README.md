# CyAN lake dashboard

One static page that serves the per-lake table of [decision 0002](../../decisions/0002-per-lake-table-recipe.md), step 1f of [the work plan](../../work-plan.md). It opens from disk and uses its own vendored libraries. The folder is self-contained. The one external request is the optional satellite imagery basemap, Esri World Imagery, which the page streams when it has an internet connection and drops on the first failed tile. The HAB_PoC "current active blooms" view is the reference. This page shows observations only. Nothing on it is a forecast.

Open `index.html` in a browser after building the data.

## Build the data

```sh
uv run python datasets/cyan/viz/build_lake_dashboard.py
```

The builder takes the newest table under `data/cyan/derived/` by default, or `--table <path>`. It needs the lake shapefile zip under `data/cyan_lakes/raw/`, the pulled weekly mosaics for the grid and the newest week's pixels, the newest name crosswalk CSV, and the state outlines. `--no-pixels` skips the pixel overlays. Run `uv run python datasets/cyan/viz/pull_basemap.py` once for the Natural Earth context layer. It writes the page data, the companion attribute table `data/cyan/derived/cyan_lake_attributes-<stamp>.parquet`, and a summary under `datasets/cyan/outputs/`. 29 seconds on 2026-09-23 with the pixel overlays.

## What must travel with the page

The page is not a single file. It loads its libraries from `vendor/` and its data from `data/`, all by relative path, and works from a folder on disk or from any static host. Share or deploy the whole folder.

- Always needed: `index.html`, `vendor/`, `data/lakes.js`, `data/basemap_land.js`, and `data/basemap_states.js`. These are in git. Without `data/`, the page shows only its frame and names the missing file at the top.
- Needed for the Lake tab's plots and for the pixel overlays: `data/lakes/` and `data/pixels/`, 4,642 files and about 140 MB. The builder writes them in under a minute. They were committed once on 2026-09-23 so that Vercel can serve them, see [the hosting note](../../vercel-hosting.md).

## What the page shows

- **Map tab.** Three panels: controls on the left, the map in the middle, the ranked list on the right. Every lake is a circle on its centroid, scaled with area and coloured by its state in the selected week: at or above the bloom line in four run-length buckets, below, or no data. Exact lake outlines load from zoom 9. The week slider covers the newest 104 weekly files. The bloom line defaults to a median code of 130, the EPA forecast's own line, and the reader can move it. "Show the newest week's pixels" draws each lake's 300 m pixels from the newest weekly file once the map is zoomed past level 8, at most 80 lakes in view at a time, as crisp squares with no interpolation. Moving the mouse over a lake's pixels reads the pixel into the box at the bottom left of the map: the lake, the code, the index it converts to, and whether the pixel counts. A control at the top right of each map toggles the Esri World Imagery basemap, on by default, with the land fills turned off while it shows. Clicking a circle or an outline opens the same popup as clicking a row in the list. "More options" holds the minimum coverage and the run-bridging choice. The list ranks the lakes at or above the line by run length, in three columns: location, weeks in bloom, and value, the median code. North American land and large lakes from Natural Earth and the state outlines from the Census Bureau give context.
- **Lake tab.** Filters by state, by status in the newest week, and by name or COMID feed one lake selector, alphabetical. The tab opens on the first lake. It leads with the weekly median, 90th percentile, maximum, and coverage over the whole record, then the daily composites of the pulled window beside a small map of the lake's newest-week pixels and exact outline over the imagery, with the same hover readout under it, then the newest 16 weeks as a table, then the lake's facts at the bottom. The series and the pixels load on demand. Deep links `#lake=<comid>` and `#tab=lake`.
- **FAQ.** A button at the top right opens a dropdown that explains the data, the lake value, the index code, the bloom line, the colours, coverage, runs, the pixels, the names, currency, limits, and sources, in plain language. Build details such as file hashes are not on the page. They are in the stamped summary under `datasets/cyan/outputs/`.
- A view deep link `#view=<lat>,<lon>,<zoom>` opens the map at a place, and `&px=1` turns the pixels on.

## What it does not show

- A value for a pixel. Every number is a statistic over the interior pixels of one lake in one file.
- A forecast, a probability, or a toxin level.
- The EPA forecast's ice mask or its fixed mixed-pixel mask. The [probe record of 2026-09-23](../../probes/2026-09-23-epa-forecast-code-deposit.md) lists the differences.
- A validated value. No number here is checked against a field sample.

| File | What |
|---|---|
| `index.html` | The page. If a file fails to load it says which one at the top |
| `vendor/` | Leaflet 1.9.4, BSD 2-Clause, and Plotly.js 2.35.2, MIT, byte-identical to the review dashboard's copies |
| `data/lakes.js` | One record per lake: COMID, name and its source, state, area, centroid, interior and touched pixel counts, the newest week's state at the build line, and the median and coverage of the newest 104 weeks. Tracked, about 3 MB |
| `data/basemap_land.js` | Natural Earth 1:50m countries and lakes clipped to North America, written by `datasets/cyan/viz/pull_basemap.py`. Tracked, about 0.5 MB |
| `data/basemap_states.js` | State outlines, copied from the review dashboard |
| `data/lakes/<comid>.js` | The lake's full weekly and daily series. 2,321 files, ignored by git because they are large and regenerable |
| `data/pixels/<comid>.js` | The lake's pixels from the newest weekly file as a coloured PNG in Web Mercator with its bounds, a grey PNG whose value is the raw code for the hover readout, and the lake's exact outline in WGS84 to 6 decimals. Pixels wholly inside the outline at full opacity, touched pixels faded, land grey, no data light grey. 2,321 files, 67 MB, ignored by git |


Lake names come from the shapefile where it has one, else from the GNIS crosswalk of `datasets/cyan_lakes/derive/build_name_crosswalk.py`. The Lake tab names the source and lists the other GNIS names inside the polygon when there are several. 91 lakes show as `COMID <n>`. States come from the lake centroid against the Census 1:20,000,000 outlines, nearest state for the 2 centroids that fall outside every state.

The companion attribute table holds, per lake, the centroid, the EPSG:5070 bounds, the pixel window on the mosaic grid, and the flat indices of the interior cells of decision 0002, so any later extraction can reuse the masks without rasterizing again.

## Imagery attribution

The imagery basemap is the Esri World Imagery tile service. Its own metadata on 2026-09-23 gave the copyright text "Source: Esri, Vantor, Earthstar Geographics, and the GIS User Community", which the page shows in the map's attribution control and the footer. Whether Esri's terms allow this use without an API key in a public deployment is an open item for the owner to settle before the page is published. `unverified`

## Why the outlines are exact

Until 2026-09-23 the page drew every outline simplified to 300 m, about one pixel, so pixels near a shore looked mislabelled against the drawn line. [Measurement 10](../../measurements.md#10-the-pixel-masks-against-exact-polygon-geometry-and-the-displacement-of-simplified-outlines-2026-09-23) shows the classification itself agrees with exact geometry, and that the simplified lines sat up to 428 m from the true shore. The page now draws only exact outlines, loaded per lake with the pixels.
