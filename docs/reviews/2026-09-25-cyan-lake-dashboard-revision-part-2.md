# Step 1f revision, part 2: a heat scale, a bloom line slider, states, coverage by class, years, and compared weeks on the lake dashboard, 2026-09-25

Implementer: Claude Code (AI coding agent), directed by the repository owner. Scope: part 2 of [the revision record](2026-09-25-cyan-lake-dashboard-scientist-feedback.md), which the owner authorized on 2026-09-25 with approval of part 1. The owner also chose option B for part 4 and directed that readers select the weeks of comparison. No provider was contacted. One headless render streamed Esri imagery tiles, as the page does by default. Nothing is committed.

## What changed

| Area | Change |
|---|---|
| Map coloring | The map opens colored by each lake's median index code on one warm hue, light orange to dark brown. A median of code 0, below detection, has its own pale color. A week with no data is a hollow dashed circle. "Bloom duration" is the other choice under "Color lakes by". `#color=duration` opens on it |
| Bloom line | A slider drawn over the index scale replaces the number box. "EPA 130" marks the default. The readout gives the code and the index as a decimal. Arrow keys move it one code at a time |
| States and sorting | A state selector on the Map tab zooms to the state and limits the counts and the list to its lakes. It also sets the Lake tab's state filter. The list gains a state column, and all four columns sort |
| Pixels | The page colors each lake's pixels itself from the raw code image, with one lookup table shared by circles, pixels, and the slider. No pixel file changed |
| Coverage | Each week's bar splits the interior pixels into those with a value, without a value, and coded land, on a 0 to 100 percent axis with a line at 100. The builder adds each file's no-value and land counts to the lake series |
| Years | A new plot draws each year's weekly medians on one calendar axis, older years lighter, the newest year in teal |
| Compared weeks | "Compare weeks" lists the weeks the reader picks by clicking either plot or from a list. "Same date in every year" adds the matching week of every year. Rows show existing weekly statistics. Nothing is averaged. [Decision 0003](../decisions/0003-comparisons-across-time.md) records the owner's direction |
| Terms | "Bloom duration" replaces "bloom state and how long", "run", and "wks in bloom". The FAQ has 17 entries, including colors, states and sorting, the land mask, and comparing weeks |
| Measurement | `datasets/cyan/qaqc/measure_zero_and_land.py` with 3 offline tests. [Measurement 13](../measurements.md#13-zero-medians-and-land-coded-lake-pixels-in-the-weekly-record-2026-09-25) |
| Documents | Decision 0003 and its index row, the page README, the outputs README, the work plan, the reviews index, and the owner's answers in the part 1 record |

## Colors

The colors follow the data-visualization method the implementer uses for charts. One hue carries magnitude, light to dark. Code 0, no value, and land are separate neutrals, because the rules keep below detection distinct from missing. The implementer ran that method's palette validator on 2026-09-25. Its output is not preserved in this repository, so these results are `unverified`.

- The index ramp, `#fdae6b` to `#7f2704`, falls steadily in lightness within one hue.
- Two colors pass the "normal-vision floor" when a reader with full color vision can tell them apart at a glance. Every pair among below detection, no value, land, and each ramp step passed.
- The "color-vision warning band" flags pairs that red-green color-blind readers may confuse. One pair falls in it: the darkest ramp step against land. The hover readout names land, which gives such a reader a second cue.
- The coverage colors, blue, gray, and dark gray, passed both tests for every pair.
- The ramp's light end is faint on white. The method allows that for a scale whose light end means "near the bottom".

## Acceptance checks

| Check | Result |
|---|---|
| Terms | No visible "run", "bloom state and how long", or "wks in bloom" remains. Code names are unchanged |
| Default coloring | Headless render: the map opens on "index, low to high" with the index legend. 566 at or above 130, 1,679 below, 76 without data, as in step 1f |
| Pixel files unchanged | 0 of 2,321 pixel files changed after the rebuild. Lake Henshaw's recolored image holds only the below-detection color, 179 pixels, land, 259, and no value, 17. It holds none of the old dark blue |
| Bloom line | A mouse drag moved the line to code 219 and the count to 29. Two presses of the left arrow key moved it to 217. At 180 the list reads 227 lakes |
| States | Florida: 43 at or above, 89 below, 1 without data. Every list row reads FL. The Lake tab's state filter follows |
| Sorting | A click on "state" sorts the list by state, with an arrow on the column name |
| Coverage | Lake Henshaw: three stacked series. The blue share peaks at 77.4 percent. The land share is 22.6 percent in every week. The axis reads 0 to 100 percent |
| Years | Lake Henshaw: one line for each year from 2016 to 2026, plus the compared weeks |
| Compared weeks | "Same date in every year" from the newest week added 11 weeks, 2016-09-11 to 2026-09-13. After a September week and then an August week were added, it added the Augusts. A compared week without data shows as a dotted line and an ×, never at code 0. Rows show the no-value and land shares |
| Gaps and bloom duration | Lake Henshaw's weekly lines break at the absent file of 2026-07-05. The Lake tab gives Lake Hamilton a bloom duration of 179 weeks over the whole record, as in step 1f |
| Filters | A stale find box no longer empties the Lake tab when a state is picked on the Map tab. When no lake matches, the tab says so and clears the old plots |
| Pixels and hover | Central Florida at zoom 11: 21 overlays. The probe inside Lake Apopka reads code 180, index 0.0083, wholly inside, counted, as in step 1f |
| Console | No console error or page error in nine headless page loads, Chrome for Testing through Playwright |

## Build

The builder ran in 39 seconds, summary `lake-dashboard-2026-09-25T1615Z.json`. The newest week's classes match step 1f. All 2,321 series files changed, 80 MB, because each gained the two count lists. `lakes.js` changed because its build time changed. The companion attribute table `cyan_lake_attributes-2026-09-25T1615Z.parquet` stays under the ignored `data/`.

## Limits

- The year plot is busy for lakes that swing between code 0 and high codes, such as Lake Henshaw. The legend hides a year on a click and isolates one on a double-click.
- Compared weeks do not survive a reload, and no deep link carries them.
- The builder still writes six summaries across weeks that the page does not display. Decision 0003 lists them, and the owner chose to keep them.
- The pixels are still the newest week only. The mid-August comparison of pixel maps waits for part 4.
- The page does not yet say that 2016 and 2017 come from one satellite and later years from two. Part 3 adds it, per decision 0003.
- A commit of this rebuild adds the 80 MB of series files to the history again.
- The checks ran headless. The owner's own browser check is pending.

## Codex review, 2026-09-25

Codex reviewed this part read-only the same day. [Request and answer](2026-09-25-codex-review-lake-dashboard-revision-part-2.md). It checked every series file, 1,387,958 rows, against the table and found the counts consistent. It confirmed that no pixel file changed and that measurement 13 reproduces.

| # | Codex finding | Disposition |
|---|---|---|
| 1 | A compared week without data sits at code 0 on both plots | fixed. Such a week shows as a dotted vertical line on the weekly plot and an × at the top of the year plot. Rings mark only weeks with a value |
| 2 | Decision 0003 misses counts across weeks: "weeks with a value", the coverage minimum, the 104-week window, and the builder's undisplayed summaries. The FAQ claims a full duration the Lake tab did not compute. The comparison omits the no-value and land shares | fixed. The Lake tab computes bloom duration over the whole record with the map's rules. Decision 0003 records every count and lists the six undisplayed summaries for the owner. The comparison rows show both shares |
| 3 | "Same date in every year" uses the latest date, not the last one added. Skipped years and the 24-week cap are silent | fixed. It starts from the week selected in the list, which adding or clicking a week sets. It reports skipped years and a full list |
| 4 | The weekly plot connects across the absent file of 2026-07-05 | fixed. The weekly lines break there |
| 5 | A stale find box plus a state picked on the Map tab leaves an empty selector with old plots | fixed. Picking a state clears the find box. An empty match clears the plots and says so |
| 6, 7 | Data, recoloring, and measurement 13 confirmed. Pooled lake-week shares do not show that "most lakes" were painted blue | corrected with evidence. Measurement 13 now speaks of lake-weeks |
| 8 | Drag, keys, layout, overlays, the probe, and clean loads rest on the headless render only | accepted. The owner's browser check remains the test |
| 9 | Palette claims lack statuses. Numbers recur across documents. One sentence in decision 0003 and one in measurement 13 exceed 25 words. Measurement 12 says "today" | fixed, except the recurring numbers. The palette results are `unverified` and their terms are explained. The two sentences are split. Measurement 12 gives a date. Reviews restate numbers with a link to their home, as earlier reviews do |

A bloom duration over the whole record differs from the rule Codex proposed in one respect. A weekly file absent from the pulled record is skipped, as the map skips it, rather than ending the duration. Decision 0003 records this.

## Dispositions

| Item | Disposition |
|---|---|
| F2, bloom duration | fixed |
| F3, a colored scale to set the line | fixed |
| F4, sort by state | fixed |
| F5, the coverage scale | fixed. The axis reads 0 to 100 percent with a line at 100, and each bar shows the land share. No per-lake ceiling is stated, per part 1 |
| F7, a heat-map scale for pixels | fixed for the newest week. Part 4 extends it to history |
| Long-term progress | fixed in the form decision 0003 allows: the year plot and compared weeks |
| Step 1f's Lake tab bloom duration, capped at 104 weeks | fixed, found by Codex |
| Owner direction on the baseline | fixed. Decision 0003. Part 5 is replaced |

## Checks

| Check | Result |
|---|---|
| `uv sync --locked`, `uv run ruff check .`, `uv run ruff format --check .` | Pass |
| `uv run pytest -q` | 167 passed in 2 seconds, 11 more than part 1. They are the measurement's 3 tests, the checks of the 2 new result files, and the documentation checks of the 3 new records. No network |

## Authorization

On 2026-09-25 the owner confirmed the wording of decision 0003 and chose to keep the six undisplayed summaries. The owner authorized a commit of parts 1 and 2, and part 3 to follow. Push was not part of the authorization.

## Proposed next step

Part 3: a research agent and a Codex check of what the index means in abundance terms, and the SFEI survey in a browser with the owner's go-ahead.
