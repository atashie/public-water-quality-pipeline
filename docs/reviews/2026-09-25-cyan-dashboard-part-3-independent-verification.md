# Independent verification of the CyAN dashboard revision, part 3, 2026-09-25

Reviewer: Codex, requested by the owner. This review checks the delivered corrections, beyond the earlier reviews preserved by the implementer.
The delivered changes were committed as `31c3462` by the other contributor during this review. Findings refer to that revision.
Scope: the [delivery record](2026-09-25-cyan-lake-dashboard-revision-part-3.md), [claim check](2026-09-25-codex-check-cyan-abundance-claims.md), and [implementation review](2026-09-25-codex-review-lake-dashboard-revision-part-3.md).
Acceptance checks cover scientific support, arithmetic, coverage reproducibility, browser behavior, and the repository check workflow.
Implementation fixes, publishing, and part 4 are deferred. No implementation file was edited by this reviewer.

The corrected scientific explanations are supported within their stated limits. Two implementation findings remain.

## Findings

### F1. P2: a repeated measurement can overwrite its evidence

Location: [measure_coverage_by_year.py](../../datasets/cyan/qaqc/measure_coverage_by_year.py), lines 85 and 100 to 101.

The filename keeps only the minute. `write_text` replaces an existing file without checking.
Two runs during the same minute therefore reuse a path, even when their inputs differ.
That violates the dataset rule that a rerun never overwrites an earlier result.

Verification: two synthetic builds used one fixed timestamp and changed the valid-pixel count between runs.
Only one result remained, and its bytes changed. All reproduction files stayed in a temporary directory.
The delivered measurement is reproducible. This finding concerns subsequent runs, not its existing values.

Recommendation: create output files exclusively and reject collisions, or generate unique filenames while retaining exclusive creation.

### F2. P3: fractional labels and chart boundaries disagree

Location: [index.html](../dashboards/cyan-lakes/index.html), `levelTable`, `levelShapes`, and `levelNotes`.

The corrected `level` function classifies fractional medians by estimated cells per mL.
The chart guides still use the first integer codes reaching each boundary.
Consequently, median 101.5 reads "high" while appearing below the guide marking "high" at 102.
The FAQ lists high as codes 102 to 186, without explaining that this column covers integer pixel codes only.

Verification: the page's helper returns approximately 100,435 cells per mL for 101.5.
The local table contains 185 weekly medians with that value, so this is an observed case.
The continuous boundaries are approximately 41.6695, 101.3391, and 186.7071.
The headless browser confirmed that the chart instead draws guides at 42, 102, and 187.

Recommendation: retain integer boundaries for the integer slider, and use continuous boundaries for plots containing fractional statistics.
Identify the FAQ's code column as integer pixel codes and explain how fractional medians are classified.
The numerical estimates and corrected hover labels themselves are accurate.

## Disposition of earlier findings

| Earlier issue | Independent disposition |
|---|---|
| Twofold uncertainty generalized to version 6 | fixed. The page confines that statement to earlier Lake Erie work |
| Mishra classes presented as WHO classes | fixed. The page calls them an adaptation and distinguishes the newer framework |
| Unsupported January 2019 satellite cutoff | fixed. The page distinguishes the unknown contribution date from the observed coverage period |
| Fractional labels and extrapolated estimates below code 1 | fixed in the helpers. F2 records the remaining presentation mismatch |
| California recommendation missing its qualification | fixed. Further validation is explicitly required |
| Restrictive Coffer source proposed for inclusion | fixed. The conflicting source is absent from the proposed preserved files |
| SFEI footnotes and new-bloom rule | fixed in the survey record |
| Keyboard access to FAQ links | fixed. Enter opened the sensor explanation and retained the lake deep link |
| Diagnostic pooling under A17 | corrected with evidence. The updated [A17](../assumptions.md) records the owner's diagnostic exception |

The A17 and owner-answer records changed during this review. Their final recorded wording resolves the earlier authorization finding.
The choice of level words remains an owner preference, as the delivery record states.

## Verification and scientific limits

- Recomputed both yearly result arrays from the local Parquet table. They exactly match [measurement 14's result](../../datasets/cyan/outputs/coverage-by-year-2026-09-25T1701Z.json).
- Verified the input and measurement-script hashes. Checked uniqueness of lake-week rows and the lake count against the measurement record.
- Verified all 50 files in the researcher's scratch manifest against their recorded hashes.
- Confirmed that all 51 preserved claim verdicts match the original checking-agent answer.
- Compared current explanations with the approved claim values and inspected the key preserved source passages.
- Revisited the primary [Mishra paper](https://www.nature.com/articles/s41598-019-54453-y) and [EPA recreational criteria page](https://www.epa.gov/habs/protecting-human-health-cyanotoxin-exposure-during-recreation).
- Confirmed the conversion factor and Mishra attribution. The paper does not establish nationwide version 6 accuracy.
- Confirmed that the EPA values describe toxin concentrations. They are not thresholds for the satellite index.
- Ran headless Chrome with external requests blocked. Verified slider levels, sample fractional estimates, year styles, comparison selection, and FAQ keyboard activation.
- Confirmed unchanged default map counts and no page errors during that browser run.

The SFEI survey remains a documentation survey. This review does not establish how its live map draws gaps.
Coverage differences do not identify their cause or quantify a second satellite's effect on the weekly maximum.
The abundance conversion remains approximate and does not measure toxins.
No additional scientific correction to the delivered explanations was identified.

## Repository checks and next step

The documented [check workflow](../../.claude/skills/check/SKILL.md) passed: synchronization, lint, formatting, and 183 tests in 0.95 seconds.
Verification includes this review record and its index entry. `git diff --check` also passed.

Proposed next step: address F1 and F2, then return the follow-up changes for review.
This reviewer made no commit, push, or deployment.
