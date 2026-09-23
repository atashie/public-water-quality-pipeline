# 0002. The per-lake table: lake universe, pixel rule, and statistics, 2026-09-23

Status: active, proposed by the implementer under the owner's authorization of step 1e on 2026-09-23. The owner confirms or amends the recipe on review of the step 1e record.

## Context

Assumption A17 forbids spatial or temporal aggregation of CyAN pixels without a recorded authorization and recipe. Assumption A9 names the CyAN resolvable-lakes shapefile as the lake universe and A20 names COMID as the key.
The owner authorized step 1e, the per-lake table, on 2026-09-23. The HAB_PoC repository replicated the recipe of the EPA forecast paper for Florida. This decision records the recipe for the whole universe so that the table is reproducible and its limits are explicit.

## Decision

- Lake universe: `updatedValidLakes.shp` from the NASA Earthdata CyAN project page, 2,321 features with 2,321 distinct COMID, pulled and checked on 2026-09-23. Every lake keeps its COMID, name, and area from the file.
- Grid: the whole-region mosaic grid, EPSG:5070 at 300 m. Polygons are reprojected to the file's projection before rasterization.
- Interior pixel: a native cell whose area lies at least 99.9 percent inside the polygon, from an 8 by 8 oversampled rasterization. Computed once per lake. Touched pixels, any coverage above zero, are counted for reference and used in no statistic.
- Statistics per lake and file, over interior pixels only: counts by code class, and over the valid codes 0 to 253 the mean, median, sample standard deviation, 90th percentile, and maximum, with the derived index of the maximum. Code 0 counts as a measurement of zero, as in the EPA forecast recipe. Codes 254 and 255 are excluded and counted.
- A lake with no interior pixel produces no row. Its COMID is listed in the provenance sidecar.
- No temporal aggregation. One row per lake and file. Daily and weekly files stay apart.
- Every table carries a provenance sidecar with the recipe id, the code hashes, and the input hashes, and a summary under `datasets/cyan/outputs/`. Tables are stamped and never overwritten.

## Consequences

- The table matches the EPA forecast's operationalization where the two overlap, so a later comparison with the forecast is like for like.
- Small lakes drop out. The QA of the shapefile counts 1 lake under 9 native pixels by area and 177 under 25. How many have no interior pixel is a measured result of step 1e.
- Edge and mixed pixels are excluded by construction. A bloom confined to a shoreline is invisible to the table. The touched count shows how much of a lake the rule discards.
- The median with zeros included is a coverage-sensitive statistic. `valid_frac` travels with every row so a consumer can filter.

## Review triggers

- The owner amends any rule above. The recipe id changes and the table is rebuilt.
- Step 3 brings Copernicus lakes, which need their own polygons and a crosswalk, assumption A20.
- A lake polygon revision arrives from NASA. The shapefile is re-pulled and the masks rebuilt.
