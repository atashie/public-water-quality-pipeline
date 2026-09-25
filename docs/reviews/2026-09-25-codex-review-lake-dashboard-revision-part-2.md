# Codex review of part 2 of the step 1f revision: data confirmed, five page defects, and an incomplete decision, 2026-09-25

Requested by the implementer, Claude Code, under the repository's rule that Codex is the preferred second model for adversarial reviews of work. The request and the answer stay together in this file.

## Request

You are reviewing delivered work. Work read-only. Do not contact any data provider. Do not edit files.

Read `CLAUDE.md`, `.claude/rules/docs.md`, `.claude/rules/datasets.md`, `docs/reviews/2026-09-25-cyan-lake-dashboard-revision-part-2.md`, and `docs/decisions/0003-comparisons-across-time.md`. Then read the changed code: `docs/dashboards/cyan-lakes/index.html`, `datasets/cyan/viz/build_lake_dashboard.py`, `datasets/cyan/qaqc/measure_zero_and_land.py`, and their tests. Use `git diff` and `git status` to see what changed since revision `e24d9eb`.

Check these, and report each as confirmed, wrong, or unsupported, with evidence:

1. Bugs in `index.html`. Look at the bloom line slider, the list sorting, the Map tab state selector and its sync with the Lake tab filter, the pixel recoloring from the code image and the alpha channel, the coverage bars, the year plot's gaps, the compared weeks and "same date in every year", and repeated Plotly click handlers. Consider a lake with no weekly rows, a lake with missing weeks, and fractional median codes.
2. The data. Confirm that no file under `docs/dashboards/cyan-lakes/data/pixels/` changed. For a sample of lakes, confirm that each series file's `n_valid`, `n_nodata`, and `n_land` sum to the lake's `ni` in `data/lakes.js` and match `data/cyan/derived/cyan_lake_table-2026-09-23T1436Z.parquet`.
3. Measurement 13 in `docs/measurements.md` against `datasets/cyan/outputs/zero-and-land-2026-09-25T1615Z.json`, and the script's logic.
4. Assumption A17. Does the page compute any number across weeks beyond what decision 0003 records? Is decision 0003 accurate about the page?
5. The legend and the FAQ against the code: do the colors and words match what the page draws?
6. The review record's acceptance checks. Which can you confirm from code or data, and which rest only on the implementer's headless render?
7. Repository rules in the new and changed documents: statuses, one fact in one home, no names, plain English, no semicolons, sentences of 25 words or fewer, no relative dates.

Put the most serious problems first. Keep the answer under 900 words.

## Answer

Reviewer: Codex CLI 0.156.1, model `gpt-6-astra`, run read-only with `codex exec -s read-only` on 2026-09-25. The answer below is verbatim, except that local absolute links were made relative and their line suffixes dropped. The dispositions are in [the part 2 record](2026-09-25-cyan-lake-dashboard-revision-part-2.md#codex-review-2026-09-25).

The delivery needs corrections. I reviewed the diff from `e24d9eb` and the working tree without editing files or contacting providers.

1. **Wrong: compared no-data weeks appear at code zero.** Both plots replace a selected week’s null median with `0`. That places its comparison ring at “below detection,” although the table correctly reports no data. Preserve missingness with a separate annotation or marker outside the value axis. [Weekly plot](../../docs/dashboards/cyan-lakes/index.html), [year plot](../../docs/dashboards/cyan-lakes/index.html).

2. **Wrong/incomplete: decision 0003 does not describe every temporal calculation.** The page computes and displays “Weeks with a value” across the entire record. This count needs its recipe recorded under A17. The builder also retains earlier temporal summaries, including `seen_share_52`, `above_weeks_52`, and `peak_median`, although the page does not display them.

   Bloom duration’s recorded recipe omits the minimum-coverage filter and 104-file limit. **Wrong:** the FAQ says the Lake tab shows the “full duration,” but it calls the same truncated `run(l,NW-1)`. Decision 0003 also promises each compared week’s no-value and land shares, which the comparison table omits. [Page calculations](../../docs/dashboards/cyan-lakes/index.html), [decision](../../docs/decisions/0003-comparisons-across-time.md).

3. **Wrong: “same date” does not use the last week added.** `addCmp()` sorts dates, and the helper takes the final sorted date. Add September, then August: it compares September across years, contrary to the FAQ. The currently selected dropdown week is also ignored until added. The midpoint containment rule itself matches decision 0003. Missing years are silently skipped, and the 24-week cap can silently prevent complete selection. [Comparison controls](../../docs/dashboards/cyan-lakes/index.html).

4. **Wrong: missing-file gaps remain connected in the weekly plot.** The year plot correctly inserts nulls for missing weekly files and preserves null medians. The weekly plot passes dates directly without inserting gaps. Henshaw therefore connects June 28 to July 12 across the missing July 5 file. This is inherited behavior, but contradicts the gap wording. [Weekly plot](../../docs/dashboards/cyan-lakes/index.html), [year gaps](../../docs/dashboards/cyan-lakes/index.html).

5. **Controls: mostly confirmed, with an empty-filter defect.** Slider bounds, integer steps, redraw wiring, four-column sorting, and Map-to-Lake state synchronization are present. Synchronization is one-way. Retaining a Lake search for Henshaw, then choosing Florida on Map, leaves no matching lakes. `ensureLake()` leaves the previous charts visible despite the empty selector. [State/filter handling](../../docs/dashboards/cyan-lakes/index.html).

   A lake lacking a `7D` series has a safe empty fallback and a guarded comparison helper. Fractional medians retain their values for thresholds and sorting. Colors round to integer codes, with positive fractions below one mapped to code one. Existing Plotly click listeners are removed before rebinding. No accumulating-handler defect is evident.

6. **Data and rendering formulas: confirmed.** No tracked pixel file differs from `e24d9eb`, and there are no untracked additions there. All **2,321** pixel files remain unchanged.

   I checked **every series**, exceeding the requested sample: **1,387,958 rows** match Parquet counts, and `n_valid + n_nodata + n_land == ni` throughout. Examples include Henshaw, Okeechobee, and Great Salt Lake.

   Recoloring reads the opaque grayscale code image and preserves the separate alpha channel. Henshaw contains 179 visible zero-code pixels, 259 land, and 17 no-value pixels. Coverage divides exact counts by `ni`, stacks three classes, and marks 100%. Legend colors match their drawing constants. [Recoloring](../../docs/dashboards/cyan-lakes/index.html).

7. **Measurement 13: numbers and logic confirmed.** Recomputing both summaries reproduces the JSON exactly. Script and input hashes match. Counts are 824,157 zero medians, 512,444 all-valid-zero rows, 174,009 all-interior-zero rows, and 517 persistently land-bearing lakes. The 497 constant counts and 118/12 coverage limits also match.

   **Unsupported interpretation:** pooled lake-week percentages do not establish that “most lakes” were painted dark blue. The script correctly avoids claiming identical land-pixel locations across weeks. [Measurement](../../docs/measurements.md).

8. **Acceptance checks: partly confirmed, partly unsupported independently.** Code/data confirm terminology, defaults, reported threshold and Florida counts, Henshaw coverage, eleven year traces, and eleven newest-reference comparison dates. Actual dragging, keyboard behavior, visual layout, 21 overlays, the geographic hover probe, and four error-free browser loads rest on the implementer’s headless account.

   Ruff lint and formatting passed. **107 selected read-only tests passed in 0.57 seconds.** I did not rerun environment synchronization or tests that write fixtures.

9. **Repository rules: violations confirmed.** Palette claims lack required statuses and linked validator results. Numerical facts recur across reviews, measurements, and READMEs. Decision 0003’s helper sentence and Measurement 13’s “22 percent” sentence exceed 25 words. Measurement 12 adds “today.” Prose is mostly plain, but palette terminology is unexplained. I found no colleague-name or prose-semicolon violations. Documentation tests check links and dates, not these editorial rules.
