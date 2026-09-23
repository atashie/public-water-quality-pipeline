# CyAN review dashboard

One static page for the owner's review of the pulled CyAN files, step 1d of [the work plan](../../work-plan.md). It opens from disk, uses vendored libraries, and requests nothing external.

Open `index.html` in a browser after building the data. The page shows native 300 m pixels of the whole-region files inside eight review windows, one week or day at a time. It reports the code under the cursor. It also charts the national composition of every pulled file and shows the QA verdicts and provenance.

## Build the data

```sh
uv run python datasets/cyan/viz/build_review_dashboard.py \
  --raw data/cyan/raw/weekly_conus_mosaic --raw data/cyan/raw/daily_conus_mosaic \
  --qa datasets/cyan/outputs/qa-weekly_conus_mosaic-2026-09-22T1850Z.json \
  --qa datasets/cyan/outputs/qa-daily_conus_mosaic-2026-09-22T1850Z.json
```

Local only. The regions are in `datasets/cyan/viz/regions.json`. Edit them and rebuild to look elsewhere. Frames under `data/frames/` are ignored by git because they are large and regenerable. `data/summary.js` and `data/basemap_states.js` are tracked.

## What the page shows and does not show

- Every pixel is one native 300 m code, reprojected to latitude and longitude with nearest neighbor for display. No value is averaged or resampled.
- Percentages on the map tab are of the review window. Percentages on the record tab are of the whole canvas, which extends beyond the region. Neither is coverage inside any lake.
- The state outlines come from the Census cartographic boundary file at 1:20,000,000, copied from the HAB_PoC repository. They are context, not a water mask.
- Lake polygons are not on the page yet. They arrive in step 1e.

| File | What |
|---|---|
| `index.html` | The page |
| `vendor/` | Leaflet 1.9.4, BSD 2-Clause, and Plotly.js 2.35.2, MIT, copied from the HAB_PoC repository |
| `data/summary.js` | Regions, frame index with per-window counts, the national record from the QA results, provenance |
| `data/basemap_states.js` | State outlines as a script for file:// loading |
| `data/frames/<region>/<date>_<temporal>.js` | One frame per file and region, a PNG in a script. Ignored by git |
