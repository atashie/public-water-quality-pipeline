# Step 1f revision, part 1: a scientist's feedback on the CyAN lake dashboard, the owner's answers, and the plan, 2026-09-25

Implementer: Claude Code (AI coding agent), directed by the repository owner. Scope: record the feedback, check what local data can show, answer the owner's hosting question, and propose the revision. The page and its data are unchanged. No provider was contacted. Four Vercel documentation pages were read. One fetch of the SFEI site was refused. Codex reviewed the plan the same day, and this record carries the corrections. Nothing is committed.

## What arrived

On 2026-09-25 the owner forwarded feedback from a scientist colleague, a limnologist, who explored the deployed lake dashboard. They download Sentinel-2 and Sentinel-3 data by hand. They find the CyAN data hard to reach in its current form. They see three uses for the page:

- Prospecting. The map of all lakes and the ranking already serve it.
- Long-term progress. Compare current conditions with the historical record to show how a lake changed after management began.
- Short-term treatment decisions. Use satellite data to set treatment doses and to judge how a lake responded.

Their requests, paraphrased. Words in quotation marks are theirs.

| # | Request |
|---|---|
| F1 | Make clear throughout the page what the CyAN index represents and how it relates to cyanobacteria abundance |
| F2 | "Bloom state and how long" is unintuitive to a limnologist. "Bloom duration" is the better term |
| F3 | A median code of 130 as the bloom line is unintuitive. Color the index from low to high on a scale, and set the line by dragging over that scale |
| F4 | Add the option to sort by state, for prospecting |
| F5 | Mark the top of the coverage plot's 0 to 1 scale. Lake Henshaw reads as 100 percent coverage when it is about 75 percent |
| F6 | Add left and right arrows to the Lake tab's pixel map to step through the whole record and see blooms change |
| F7 | The pixel map "shows only blue". A heat-map scale would show hotspots in a lake |
| F8 | Pull the mid-August pixel map for six different years and compare them on the heat-map scale |
| F9 | Look at the NOAA and SFEI harmful algal bloom map for California, [fhab.sfei.org](https://fhab.sfei.org/), and adopt what it does well, including how it accounts for satellite data gaps |

## What was checked on 2026-09-25

Findings 1 to 3 come from a one-off query of the per-lake table by the implementer. Codex reproduced every count with its own query the same day. They stay `unverified` until part 2 measures them with a checked-in script.

1. **Why the pixels look blue.** The color scale runs from dark blue at code 0 to dark red at code 253. Code 0 means below detection. Of 1,040,186 weekly lake rows with a value, 79 percent have a median of code 0. In 49 percent every valid pixel is code 0. The map's "median index code" coloring paints such a lake dark blue, and the pixel map paints every code-0 pixel dark blue. These shares explain the report. They do not measure what the newest week's pixel images show.
2. **Why Lake Henshaw never reaches full coverage.** COMID 20342929 has 53 interior pixels. Each of the 542 weekly files codes 12 of them as land, code 254. Its coverage therefore peaks at 41 of 53, 77 percent, reached in 304 weeks. The counts do not show that the same 12 pixels are land in every file. The CyAN release notes name this class of problem: the land mask may cover dry lakes, known issue 2 in [the CyAN METADATA](../../datasets/cyan/METADATA.md).
3. **How common a coverage ceiling is.** 517 of 2,321 lakes have at least one land-coded interior pixel in every weekly file. For 118 of them the smallest land count keeps coverage under 90 percent, and for 12 under 50 percent. No land code enters a statistic, because [decision 0002](../decisions/0002-per-lake-table-recipe.md) excludes code 254. The statistics then describe only the remaining pixels, which can represent the whole lake less well.
4. **The coverage plot.** The small plot fixes its axis at 0 to 1 and draws no line at 1. Lake Henshaw's bars at 0.77 are its tallest and read as full.
5. **The SFEI site.** The implementer's fetch tool received HTTP 403 from the site on 2026-09-25. A survey needs a browser session. Whether the site refuses every automated client is `unverified`.
6. **The cost of the whole record of pixel images.** The run of 2026-09-24 had never been recorded. It is now [measurement 12](../measurements.md#12-the-whole-weekly-record-of-per-lake-pixel-images-what-it-costs-in-bytes-2026-09-24). Codex checked every number in it against the result file.

## The owner's answers, 2026-09-25

1. Do the revision now, ahead of step 1g.
2. The map defaults to a continuous heat scale of the index. Bloom duration stays as a coloring the reader can switch to.
3. "State" means US state.
4. The page deploys to Vercel only. If Vercel cannot carry historical pixel images, the owner revisits whether to show them.
5. Explain the baseline question. The explanation follows below.

## Dispositions

| # | Disposition |
|---|---|
| F1 | accepted and deferred to part 3. The page already converts a code to the index. A link from the index to cells per milliliter needs `documented` sources first. The 10^8 factor is checked in [the assertions probe](../probes/2026-09-23-cyan-vs-clms-assertions.md) and awaits Codex. No category breakpoints, such as low, moderate, and high, are sourced in this repository |
| F2 | accepted and deferred to part 2. "Bloom duration" replaces "bloom state and how long", "run", and "wks in bloom" on both tabs and in the FAQ |
| F3 | accepted and deferred to part 2. A slider drawn over the color scale replaces the number box. The readout gives the code and the index. The EPA forecast's 130 stays the default and is marked on the scale. The map opens on the continuous scale, owner answer 2 |
| F4 | accepted and deferred to part 2. A state selector on the Map tab zooms the map and filters the list. The list's columns sort by name, state, bloom duration, and value |
| F5 | accepted and deferred to part 2. The axis becomes 0 to 100 percent with a line at 100. Each week's bar splits into pixels with a value, without a value, and coded land. Decision 0002 already authorizes these counts per file. A single ceiling per lake is a summary across weeks, so it waits for decision 0003 |
| F6 | accepted and deferred to part 4, in the form the hosting analysis below allows |
| F7 | accepted and deferred to part 2. Code 0 gets its own neutral color. Codes 1 to 253 get a sequential heat scale, fixed across lakes and weeks so that comparisons hold. The page colors the pixels itself from the code images it already loads, so no pixel file changes |
| F8 | accepted and deferred to part 4. A grid of the same mid-month week across years on one shared scale |
| F9 | accepted and deferred to part 3. A browser survey of the site, recorded as a probe. The owner then picks the features to adopt |
| Long-term progress | accepted and deferred to part 2 in a form that needs no authorization, a year-over-year plot. A baseline waits for the owner, see below |
| Treatment decisions | accepted and deferred to step 1g. They need a weekly refresh and a daily pixel history. The page is a static build of the pull of 2026-09-22. Local daily files cover 8 weeks, assumption A8 |

## Historical pixel images on Vercel

Vercel builds this page from git, so every served file is a committed file. GitHub recommends a repository "ideally less than 1 GB". That is a guideline, not a hard limit. The packed repository measured 59 MB with `du` on 2026-09-25, `measured`. The served image files are base64 text. How much git compression saves on them is not measured.

The quotes behind the next three points are in [the hosting note](../vercel-hosting.md), in its note of 2026-09-25.

- **Vercel's caps.** The limits page states size and file caps for CLI uploads only, and none for git deployments. `unverified` until a larger deployment succeeds. The largest live test is the 149 MB folder of 2026-09-23.
- **Deployment storage.** A Hobby team gets 10 GB of deployment storage. Each project keeps its 3 newest production deployments and its 3 newest of any type. Going over can block deploying. `unverified`. Under option B one deployment is about 310 MB, so six retained deployments hold about 1.9 GB. Under option A they hold about 4 GB. What the account's other projects already use is not known here.
- **Vercel Blob.** One upload per lake, 2,321, exceeds one month's Hobby allowance of advanced operations. Going over locks Blob for 30 days. Staging uploads across months, or packing lakes into shared files, would work around it. Storage, transfer, and read allowances also apply. `unverified`.

| Option | Bytes | Git | What the reader gets |
|---|---|---|---|
| A. The whole weekly record | 516 MB, [measurement 12](../measurements.md#12-the-whole-weekly-record-of-per-lake-pixel-images-what-it-costs-in-bytes-2026-09-24) | Under the 1 GB guideline once. Each full rebuild adds to the history | Every week since 2016-04-24 |
| B. The newest 52 weeks, then one week per month back to 2016 | about 160 MB, estimated | Room for several rebuilds | Weekly steps for a year, monthly steps before it, and every mid-August since 2016 |
| C. The newest 52 weeks only | 53 MB, [measurement 11](../measurements.md#11-a-year-of-per-lake-pixel-images-what-it-costs-in-bytes-2026-09-23) | Room for many rebuilds | Weekly steps for a year. No comparison across years |
| D. Vercel Blob | as A or B | Outside git | Needs staged uploads or shared files on Hobby |

The estimate for B. The week for a month is the weekly file whose seven days contain the 15th. That gives 125 weeks, one for every month from 2016-05 to 2026-09. 112 of them fall outside the newest 52, so B holds 164 distinct files. At the measured mean of 951,415 B per week stacked, the 112 weeks add about 107 MB to the 53 MB of C. The estimate leaves out the outlines and masks, which the page's pixel files already serve. Lake Okeechobee's file would be about 5 MB instead of 16 MB. The 11 mid-August weeks run from 2016-08-14 to 2026-08-09. Choosing one file per month is a selection, not an aggregation.

Recommendation: B. It answers F6 and F8 on Vercel alone and leaves room for rebuilds and retained deployments. Part 4 measures B with a checked-in script before building it. The owner checks the account's deployment storage in Vercel before the first deployment of part 4. A stays possible as a one-time choice.

## The baseline question

[Assumption A17](../assumptions.md) forbids spatial or temporal aggregation without a recorded owner authorization. Decision 0002 authorizes one spatial statistic per lake and file. It authorizes no temporal one.

There are two ways to show change over the record.

1. **Put single weeks side by side.** A year-over-year plot draws each year's weekly medians against the day of the year. The grid of F8 does the same for pixel images. Every value shown already exists, so no authorization is needed.
2. **Compute a baseline.** One example is a lake's typical mid-August median over 2016 to 2025. Others are a band of typical values for each week, or a summary before and after a management date. Each is a new number made from many weeks, so A17 requires a recorded decision first.

A baseline recipe must fix at least these choices. Each one moves the answer.

- **The period.** All earlier years, a fixed span, or the years before a lake's management date. The page has no management dates, so a reader would enter one.
- **The season.** Ice can register as high index counts, known issue 1 in the CyAN METADATA. How often winter weeks lack a value is not measured here.
- **The statistic.** Over codes 1 to 253 a code is linear in the logarithm of the index. A mean of those codes is therefore a geometric mean of the index. Code 0, below detection, needs its own rule. A median, or a count of weeks at or above the line, avoids the mean. The recipe also fixes its quantile convention.
- **Gaps and weights.** Years differ in how many weeks have a value, and some lakes have a coverage ceiling, finding 3. The recipe sets a minimum coverage, a minimum count of weeks per year, and a minimum count of years. It also says how a year with few weeks is weighted.
- **The sensors.** From 2018 the files merge Sentinel-3A and 3B and keep the higher value per pixel, per the CyAN METADATA. A maximum over more observations can only stay the same or rise. So 2016 and 2017 may read lower than later years for reasons unrelated to the lake. The size of the effect is not measured.
- **Interpretation.** A difference before and after a date is a change, not an effect of management. Weather and water level move the index too.

Bloom duration is itself a count across weeks. The owner approved it with the page in step 1f, but no decision records it. A single coverage ceiling per lake, finding 3, would be another summary across weeks. Decision 0003 can cover both.

Recommendation: part 2 builds the year-over-year plot. A baseline waits until the scientist has used that plot and names the comparison they need. Then decision 0003 records the recipe, Codex reviews it, and the owner confirms it.

## Proposed revision

Each part is one authorized unit with its own review record.

1. **This record.** Measurement 12, the hosting note's dated note, the work plan, and [the Codex review](2026-09-25-codex-review-lake-dashboard-feedback-plan.md).
2. **The page, with no new statistics and no new claims.** Acceptance checks:
   - Every "run", "bloom state and how long", and "wks in bloom" now reads "bloom duration".
   - The map opens on the continuous heat scale. Code 0 has its own color. Bloom duration is one click away.
   - The page colors pixels in the browser from the code images it already loads. The pixel files do not change.
   - Dragging over the scale moves the bloom line. The counts, the list, and the Lake tab's line follow.
   - A state selector filters the list and zooms the map. The list's column headers sort.
   - The coverage axis reads 0 to 100 percent with a line at 100. Each week's bar shows the shares with a value, without a value, and coded land.
   - The builder adds each file's land and no-value counts to the lake series. The series files are rebuilt and committed.
   - Lake Henshaw shows a land band of 12 of 53 pixels in every week.
   - The Lake tab plots each year's weekly medians against the day of the year of each week's start. Weeks without a value stay gaps. The newest year is highlighted.
   - A checked-in script measures findings 1 to 3.
   - Tests pass, `/check` passes, and a headless render shows no console error.
3. **What the index means.** A research agent and a Codex check of the 10^8 factor, the cells per milliliter range, and the category breakpoints that EPA and others use. A browser survey of the SFEI site, with the owner's go-ahead, recorded as a probe. Then the explainer, the tooltips, and legend labels in words.
4. **Historical pixel images**, the option the owner picks. Measure it, build per-lake stacks, and add arrows and arrow keys. Add a jump to the next week with a value, and a click on the weekly plot that opens that week. Add the same-month grid across years with a shared scale and each panel's coverage.
5. **A baseline**, only after decision 0003.

## Codex review, 2026-09-25

Codex reviewed this plan read-only the same day. [Request and answer](2026-09-25-codex-review-lake-dashboard-feedback-plan.md).

| # | Codex finding | Disposition |
|---|---|---|
| 1 | A coverage ceiling per lake is a summary across weeks and needs an authorization under A17. The series files lack the land count | fixed. Part 2 shows per-file counts for each week instead. A stated ceiling waits for decision 0003 |
| 2 | GitHub's 1 GB is a guideline. Packed growth is not measured. The plan missed Hobby's 10 GB deployment storage | fixed. The implementer read Vercel's changelog of 2026-09-16 and added the allowance to the hosting note and to the analysis |
| 3 | Blob is over one month's operations, not infeasible | fixed. Staged uploads and shared files are named as workarounds |
| 4 | Finding 1 said "every interior pixel" where the query counts valid pixels. "Most lakes solid dark blue", "the same 12 pixels", and "statistics unaffected" are unsupported. The counts reproduce | fixed. Wording corrected. The counts stay `unverified` until part 2 measures them |
| 5 | The geometric-mean statement ignores code 0. The recipe list misses weighting, minimum years, and quantiles. The winter statement is not quantified. The overlay needs rules for week numbering and gaps | fixed. The overlay uses the day of the year, which needs no week numbering, and keeps gaps |
| 6 | Measurement 12 confirmed. Measurement 11's "543 files" is stale | fixed. Measurement 2 counts 543 weekly periods and 542 listed files. Measurements 11 and 12 now say so |
| 7 | B confirmed as an estimate, 159.30 MB and 164 files. Masks and outlines add 62 MB | accepted. The page already serves the outlines. The estimate now says it leaves them out |
| 8 | Coloring pixels in the browser works from disk | confirmed. No change |
| 9 | One fact in several homes, missing statuses, "corrected with evidence" on unmeasured findings, one sentence over 25 words, and "today" | fixed. The Vercel quotes live only in the hosting note. Statuses added. F5 and F7 now read "accepted and deferred". The sentence is split, and "today" is gone |

## Deferred

- Treatment decisions, to step 1g: refresh cadence and a daily pixel history.
- The Esri imagery terms for a public site, still open from step 1f.
- The Codex check of the assertions probe. Part 3 now depends on it.

## Checks

| Check | Result |
|---|---|
| `uv sync --locked`, `uv run ruff check .`, `uv run ruff format --check .` | Pass |
| `uv run pytest -q` | 156 passed in 2 seconds, including the link and date checks over these documents. No network |

## Owner decisions requested

1. Historical pixel images: option B, A, or C.
2. The baseline: the year-over-year plot only for now, or a draft of decision 0003 now.
3. Approval of this record and authorization of part 2.

## Proposed next step

Part 2, the page changes that need no new statistics and no new claims.

## Owner decision, 2026-09-25

The owner approved this record and authorized part 2. The owner chose option B for historical pixel images in part 4. On the baseline, the owner directed that readers select the weeks of comparison, because natural variance defeats any generic rule. [Decision 0003](../decisions/0003-comparisons-across-time.md) records that direction, and part 5 is replaced by it. [Part 2](2026-09-25-cyan-lake-dashboard-revision-part-2.md) followed the same day.
