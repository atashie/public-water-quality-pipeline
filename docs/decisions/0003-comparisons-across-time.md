# 0003. Comparisons across time: weeks the reader chooses, shown as observed, 2026-09-25

Status: active. It records the owner's direction of 2026-09-25, given in answer to the baseline question of [the step 1f revision record](../reviews/2026-09-25-cyan-lake-dashboard-scientist-feedback.md#the-baseline-question). The implementer worded it, and the owner confirmed the wording on 2026-09-25.

## Context

A scientist asked to compare a lake's current conditions with its historical record, to show how the lake changed after management began. [Assumption A17](../assumptions.md) forbids temporal aggregation without a recorded owner authorization. [Decision 0002](0002-per-lake-table-recipe.md) authorizes one spatial statistic per lake and file and no temporal one. The revision record listed the choices a baseline would have to fix: the period, the season, the statistic, gaps and weights, the sensors, and how to read a difference.

The owner judged that natural variance between lakes is too large for any generic baseline rule to hold in every case.

## Decision

- No generic baseline. The page computes no number across weeks for a comparison.
- The reader chooses the weeks to compare. The page shows each chosen week's existing statistics from decision 0002 side by side, as observed. Each row also shows the week's shares of interior pixels with a value, without a value, and coded land.
- Helpers choose weeks and never combine them. "Same date in every year" starts from the week selected in the list, which a click on a plot also selects.
- For each year, that helper adds the weekly file whose seven days cover the middle date of the selected week. It reports the years that have no such file.
- The year-over-year plot places each existing weekly median at the calendar date its week starts. It combines no values.

## Counts across weeks that the page already shows

These count weeks and combine no values. They date from step 1f, which the owner approved, and are recorded here unchanged.

- Bloom duration counts the consecutive weekly files, ending with the selected week, whose lake median is at or above the bloom line.
- A week counts as having a value when its coverage meets the reader's minimum, any valid pixel by default. A week without a value ends a bloom duration, unless the reader turns on bridging, which skips it.
- A weekly file absent from the pulled record is skipped, not counted. One such file exists, the week of 2026-07-05, [measurement 2](../measurements.md#2-the-archive-listing-lacks-one-weekly-file-2026-09-22).
- The map counts within the newest 104 weekly files and shows 104 or more as "104+". The Lake tab counts over the whole record.
- The Lake tab's "weeks with a value" counts the lake's weekly files with at least one valid interior pixel.

The builder also writes six per-lake summaries across weeks into `data/lakes.js` that the page does not display. They are `run_above`, `run_seen`, `weeks_since_seen`, `seen_share_52`, `above_weeks_52`, and `peak_median`, the highest weekly median. The last one combines values. They date from step 1f. The owner chose on 2026-09-25 to keep them.

## Consequences

- Any number computed across weeks needs a new decision with its recipe. Examples are a mean, a median of medians, a band of typical values, or a difference before and after a date.
- The comparison serves the long-term use without a rule that would fail some lakes. The reader judges each week with its coverage, no-value, and land shares in view.
- From 2018 the files merge Sentinel-3A and 3B and keep the higher value per pixel, per the [CyAN METADATA](../../datasets/cyan/METADATA.md). A reader comparing 2016 or 2017 with later years needs that context. Part 3 of the revision adds it to the page.

## Review triggers

- The owner or a user asks for a summary number across weeks.
- A per-lake reference from another source becomes available, such as the EPA forecast's history in step 2.
