# Step 1d, CyAN review dashboard: native 300 m frames for eight windows, the national record, and provenance on one offline page, 2026-09-23

Implementer: Claude Code (AI coding agent), directed by the repository owner. Scope: step 1d of [the work plan](../work-plan.md), the page the owner explores before the data are used. Nothing committed. No provider contacted.

## What the owner directed

The owner authorized step 1d on 2026-09-22 after approving the pull and the corrected QA. The plan for the page was one static file with vendored libraries that opens from disk. It shows a selectable week at native 300 m over a chosen region, the composition over the full record, the QA table, and the gaps.

## What changed

| Area | Change |
|---|---|
| Builder | `datasets/cyan/viz/build_review_dashboard.py` with `regions.json` and 5 offline tests on a synthetic mosaic. It reads one native window per region from every pulled file, reprojects it to latitude and longitude with nearest neighbor so every pixel keeps its code, and writes each frame as a PNG inside a script file so the page can read pixels from a file:// URL |
| Page | `docs/dashboards/cyan/index.html` with three tabs. Map: region, cadence, date slider, play, class toggles, legend, the code and index under the cursor, and the window's composition. Record: four charts of the national record with the missing week shaded, and a sortable table of every file. Provenance: QA verdicts, manifests, and the hashes behind the page |
| Data | `data/summary.js` and `data/basemap_states.js` tracked. Note added 2026-09-23: they were not, because the ignore rule `data/` matched this folder too. The step 1f commit of 2026-09-23 fixed the rule and added them. 4,784 frames under `data/frames/`, 635 MB, ignored by git and rebuilt by the builder |
| Vendored | Leaflet 1.9.4 and Plotly.js 2.35.2 copied from the HAB_PoC repository, with the Census state outlines it derived |
| Environment | Pillow added to the pinned `datasets` group |

## What the page shows and does not show

- Every displayed pixel is one original code. Colors are assigned in the browser. Land, no data, and below detection can be hidden to see the data class alone.
- Window percentages describe the review window. Canvas percentages on the record tab describe the whole file, which extends beyond the region. Neither describes a lake. Lake polygons arrive in step 1e.
- The state outlines are context at 1:20,000,000, not a water mask.
- Nothing on the page validates a value. It lets the owner see the data as delivered.

## Build

The first build started 2026-09-22T16:31Z and finished 2026-09-23T13:03Z with the machine asleep for most of that time. Its frames showed the lake surfaces in the color of code 1 where the window composition said code 0.
A browser-equivalent decode of one frame matched Python's bytes exactly and put the fault in the builder, not the page. The reprojection passed a destination nodata value of 0, and GDAL nudges a valid output pixel that equals the destination nodata by one. Code 0 became code 1 in every frame.
The fix removes the destination nodata and takes coverage from the alpha band. A regression test asserts that an all-zero window stays zero. Every frame was rebuilt from 13:07:37Z to 13:23:00Z, 15 minutes 23 seconds for 598 files and 8 windows with the machine kept awake. The rebuilt frame for the week of 2026-09-13 over Lake Erie holds 707,521 pixels of code 0 and none of the spurious code 1.
The summary was regenerated at 2026-09-23T14:23Z with exact pixel counts per file after the owner's first feedback, reusing the rebuilt frames. The builder emits a Pillow deprecation warning for the `mode` argument. It is harmless and is left untouched so the source hash in the summary matches the code that ran.

## Findings

1. **The data are what the QA said.** The page renders every pulled file at native resolution. In the last weekly frame over Lake Erie, the lake surfaces are below detection and a bloom sits in the western basin and Sandusky Bay. The window is 82 percent land, 17 percent below detection, 0.8 percent data, and 0.4 percent no data.
2. **A display bug would have misread the data.** Without the browser check, the review page would have shown below-detection water as the lowest data code. The check is now part of the step.
3. **The frames are cheap.** A 600 km window at native 300 m reprojects in about 40 ms and stores as roughly 130 KB inside its script file. The full record for a new window costs about two minutes.

## Checks

| Check | Result |
|---|---|
| `uv run pytest -q` | 105 passed. No network |
| `uv run ruff check .` and `uv run ruff format --check .` | Pass |
| Page opened in a browser | The Chrome extension was not connected. Headless Chromium from the Playwright cache, build 1234, rendered all three tabs from a file:// URL. Dynamic text, the image overlay, 49 state outlines, four charts, and the file table were present. A frame decoded in the browser matched Python's bytes exactly, which found the code 0 fault |
| External requests | None. Every script, stylesheet, and data file is relative |

## Limits

- The eight windows are the implementer's choice. The owner's feedback sets the next ones.
- Frames are 600 km squares. A lake on a window edge needs a new window.
- The reprojection is for display. Any analysis reads the EPSG:5070 files.
- The daily record covers 8 weeks only, per assumption A8.
- The headless render checks structure and one frame's codes. The owner's exploration is the review of the data.

## Owner feedback

| Date | Feedback | Disposition |
|---|---|---|
| 2026-09-23 | Does the weekly record chart show sums across all locations in the 48 states? | Answered and fixed. Each point is one national file's counts over every pixel of its canvas, expressed as a share of the canvas. The canvas is the CyAN product extent for the contiguous United States, which includes whole lakes across the Canadian border and near-shore waters, plus empty margins coded as no data. The record tab now says so, and every point carries the exact pixel count on hover. The builder now writes the counts and the canvas size into the summary |
| 2026-09-23 | The dual-axis charts take time to read. Label the axes more clearly, perhaps by color | Fixed. Every axis title, tick, and line carries the color of its series, chart titles name which series sits on which axis, and the legend entries say left or right. The daily no-data series became a line on its own dark-gray axis so the two scales no longer compete as bars. Hover is unified per date |

## Authorization

The owner explored the page, gave the feedback above, approved the result on 2026-09-23, and authorized commit, push, and step 1e.

## Proposed next step

The owner explores the page and gives feedback. Then dispositions, any rebuild, and authorization to commit. Then step 1e, the resolvable-lakes shapefile and the per-lake table, with the aggregation recipe recorded in a decision.
