# Step 1f revision, part 3: what the index means, the SFEI survey, and the single-satellite years on the lake dashboard, 2026-09-25

Implementer: Claude Code (AI coding agent), directed by the repository owner. Scope: part 3 of [the revision record](2026-09-25-cyan-lake-dashboard-scientist-feedback.md), which the owner authorized on 2026-09-25 when approving parts 1 and 2. It answers the scientist's items F1 and F9 and the consequence of [decision 0003](../decisions/0003-comparisons-across-time.md) on sensor periods. No data provider was contacted. The research agent and the implementer fetched public pages and reports, listed below. The owner authorized the commit on 2026-09-25.

## What changed

| Area | Change |
|---|---|
| Research | A research agent drafted 49 claims from 26 sources on the index as abundance, named levels, toxins, and Sentinel-3B. The implementer added 2 claims from a preserved paper. Codex checked all 51 against the saved copies. `datasets/cyan/reference/cyan-abundance-research.json` and `cyan-abundance-checks.json` |
| Preserved sources | 13 files under `datasets/cyan/reference/abundance/`, US government works and papers under CC BY 4.0 or CC0 only. The rest are cited by URL and hash |
| CyAN METADATA | Section 4 gains what the index reads, the cell conversion with its origin and uncertainty, and the named level schemes. Section 9 gains toxins and depth, and section 2 the Sentinel-3B dates. Five new discrepancies, D8 to D12. Open item O5, the missing factor, is resolved |
| SFEI survey | [Probe record](../probes/2026-09-25-sfei-fhab-survey.md). The map sits behind a bot check. The survey reads its interface documentation, the state's page on it, and the state's best-practices report. It lists nine candidate features, S1 to S9 |
| Measurement | `datasets/cyan/qaqc/measure_coverage_by_year.py` with 3 offline tests. [Measurement 14](../measurements.md#14-weekly-lake-coverage-by-year-before-and-after-the-second-satellite-2026-09-25) |
| Page, explainer | The banner names the index as observed cyanobacteria near the surface. It says the index is not a forecast and not a toxin measurement, and links to a new FAQ entry. That entry says what the index reads, how it converts to cells per mL, how uncertain that is, and where the level words come from. A second new entry says the index is not a toxin measurement |
| Page, words on the scale | A band under the bloom line slider names four levels of estimated abundance: low, moderate, high, and very high. They adapt the classes of Mishra et al. 2019 at 20,000, 100,000, and 1,000,000 cells per mL. On the scale each starts at the first code whose estimate reaches the boundary: 42, 102, and 187. The weekly, daily, and year plots carry faint dotted lines and labels at the same codes |
| Page, estimates | Six places give the level and the estimate in cells per mL, to one significant figure. They are the slider note, the map popup, the pixel readout, the Lake tab's facts, and the hovers of the weekly and year plots. The words follow the estimate, so a half-code median gets the level its estimate falls in. A median below code 1 reads "near the detection limit" without an estimate. Code 0 reads "below detection" without an index value, which the pixel readout printed before |
| Page, single-satellite years | The year plot draws 2016 to 2018 dotted. Compared weeks from those years carry an asterisk and a note. Both say that Sentinel-3B joined during 2018 and that those years have a smaller share of weeks with a value. A new FAQ entry explains the sensor periods. It states measurement 14's finding in words. No number pooled across weeks appears on the page, per decision 0003 |
| Documents | The page README, the outputs README, the probes index, the reviews index, the work plan |

## Acceptance checks

| Check | Result |
|---|---|
| Claims checked by a second model before METADATA uses them | Codex confirmed 35 and corrected 16 of 51, rejecting none. [Request and answer](2026-09-25-codex-check-cyan-abundance-claims.md). METADATA cites only confirmed or corrected claims, in their corrected form |
| Every METADATA claim tag names a confirmed or corrected check | `tests/test_dataset_claims.py` passes |
| The level codes | 42, 102, and 187 in the page. Codex recomputed them: code 41 gives 19,642 cells per mL and code 42 gives 20,179 |
| Explainer and links | Headless render: the banner link and the words "estimated abundance" open the FAQ at "What does the index mean?". The asterisk note opens "Why do 2016 to 2018 differ?" |
| Level band | Four segments on the slider's own coordinates: low 1 to 41, moderate 42 to 101, high 102 to 186, very high 187 to 253 |
| Estimates | At the EPA line the slider note reads "high, about 200,000 cells/mL". At 187 it reads "very high, about 1,000,000 cells/mL". The probe inside Lake Apopka reads code 180, index 0.0083, "high, about 800,000 cells/mL" |
| Single-satellite years | Lake Henshaw: 2016, 2017, and 2018 dotted, 2019 on solid. "Same date in every year" from 2026-08-30 added 11 weeks. The rows for 2016, 2017, and 2018 carry an asterisk, and the note appears |
| Half codes and code 0 | The page's own helpers ran in headless Chrome. 101 reads moderate, and 101.5 and 102 read high. 186.5 reads high, and 187 very high. 0.5 reads "near the detection limit", and 0 reads "below detection" |
| Keyboard | Tab to the banner link and press Enter: the FAQ opens at "What does the index mean?" and the address keeps its deep link |
| Nothing else moved | The map counts at the EPA line stay 566, 1,679, and 76 |
| Console | No console error or page error in four headless page loads, Chrome for Testing through Playwright |

## The claim check

A research agent on Claude Opus 5.5 fetched 26 sources and drafted 49 claims. A script matched every quote against the saved copy. The implementer added 2 claims from the preserved Mishra et al. 2019 paper. Codex, on a different model, checked all 51 read-only against the saved copies and hashes. It also read the app screenshots and the WHO tables as images.

| # | Codex's most serious findings | Disposition |
|---|---|---|
| 1 | "A factor of two or more" is not established for version 6. The twofold statements concern earlier Lake Erie work | fixed. The page and METADATA say that earlier Lake Erie work put the uncertainty at about twofold |
| 2 | Mishra's labels are not WHO's three-tier table. The page must attribute them as an adaptation | fixed. The page says the words adapt Mishra's classes, which based two boundaries on earlier WHO guidance. It names very high as Mishra's addition and states the boundary rule |
| 3 | NASA's stated range conflicts with the formula and the factor | fixed. Discrepancy D8. The page uses the formula |
| 4 | SFEI's raw codes and footnotes do not carry over to CyAN | fixed. The page's codes come from the index. METADATA says SFEI's codes do not carry over |
| 5 | The app figures show displayed settings, not verified defaults. The Android very high boundary differs from Lunetta's | fixed. Discrepancy D10 says so |

Codex also asked for "expressed as" rather than "counted as" Microcystis-equivalent cells, and for "less in turbid water" beside the one-meter depth. Both are fixed. It judged the two screenshot readings `documented`, not `probe`, because a second agent checked a published figure. METADATA cites them as `documented`. The research record keeps the researcher's proposal and the check record holds the verdict.

## Codex review, 2026-09-25

Codex reviewed this part read-only the same day. [Request and answer](2026-09-25-codex-review-lake-dashboard-revision-part-3.md). It reproduced measurement 14 from the table, matched the SFEI quotes and hashes, and confirmed the level codes and the interaction logic.

| # | Codex finding | Disposition |
|---|---|---|
| 1 | Coffer et al. 2020's XML shows "CC BY" but links to CC BY-NC 4.0 | fixed. The file is not preserved. The research record says why. 13 files remain |
| 2 | January 2019 is not a documented satellite boundary. Measurement 14 measures coverage, not passes | fixed. The page, the README, and this record describe 2016 to 2018 by what is documented and measured. Sentinel-3A alone through 2017, Sentinel-3B joining during 2018, and a smaller share of weeks with a value |
| 3 | A half-code median such as 101.5 gets the word of the code below it. Medians of 0.5 get estimates outside the formula's domain | fixed. The words follow the estimate. Below code 1 the page gives no estimate |
| 4 | Measurement 14 says "fewer lake-weeks" where it means a smaller share, and "makes years comparable" overstates the filter | corrected with evidence. The measurement speaks of shares, names the partial first and last years, and says how the mean is weighted |
| 5 | California's recommendation lost "without additional validation and study". "The product defines none" lacks a claim. D9's "likely" is unsupported. This record's "about a factor of two" repeats the corrected overstatement | fixed in METADATA, the page, and this record |
| 6 | The SFEI record drops footnotes that split "Background Level" from "Non-Detect". S8 needs a rule for a new bloom. "None is built" is wrong | fixed |
| 7 | The FAQ links lack an address, so a keyboard cannot reach them | fixed. Each link has `href="#"`. A headless check opened the FAQ with the Enter key |
| 8 | The page shows no new pooled number. Measurement 14 pools weeks and lakes outside the page, and no decision records that recipe under A17 | fixed. On 2026-09-25 the owner added terms for diagnostic measurements to assumption A17. Measurements 13 and 14 meet them and say so |
| 9 | Facts repeat across METADATA, the README, and review prose. One METADATA sentence exceeds 25 words. This record held placeholders and "now" | fixed, except the restatements in review prose, which link to their homes as earlier reviews do. The README points to METADATA for the level boundaries |

## Limits

- The SFEI map itself was not seen. Its legend wording, time controls, and chart gaps are unknown. The owner's own browser with the Claude extension connected would allow a survey of the screens.
- The cell estimate is rough. Earlier Lake Erie work put its uncertainty at about twofold. California's program advises against cell counts from these satellites without further validation. The page says both and rounds to one significant figure.
- One significant figure blurs the edges of the levels. Code 41 reads "low, about 20,000" and code 186 "high, about 1,000,000". The FAQ's table gives the exact ranges.
- The level words come from one study. The EPA's CyAN app uses other defaults, and the WHO replaced its cell-count guidance in 2021. The owner may prefer another scheme or none.
- No source dates the week when Sentinel-3B data enter the CyAN files. The page marks 2016 to 2018 by calendar year. Measurement 14 places the step in coverage between 2018 and 2019. It does not show how much a second satellite raises a weekly maximum.
- The checks ran headless. The owner's browser check is pending.

## Dispositions

| Item | Disposition |
|---|---|
| F1, explain the index and how it relates to abundance | fixed |
| F9, the SFEI site's features and its handling of gaps | fixed as a survey through documentation. S1, S2, and S4 are built here because they answer F1 and decision 0003. The owner put the rest on hold on 2026-09-25, see below |
| Decision 0003, context on 2016 and 2017 | fixed. The context covers 2016 to 2018, because measurement 14 shows 2018 with the earlier years |
| The pixel readout's index for code 0 | fixed |
| The Codex check of the assertions probe, A1 | fixed in part. Its A1 quotes on the factor and the range are checked claims in this part. A2 to A6 wait, as before |

## Checks

| Check | Result |
|---|---|
| `uv sync --locked`, `uv run ruff check .`, `uv run ruff format --check .` | Pass |
| `uv run pytest -q` | 181 passed in 2 seconds, 14 more than part 2. The new ones cover the measurement script and the checks of the new records, result file, and documents. No network |

## The owner's answers, 2026-09-25

- Assumption A17: option 3. Diagnostic measurements may pool counts across lakes and weeks if they stay in the measurements document, say they are pooled, and never feed a dataset. The page may state their findings in words, never their numbers. [Assumption A17](../assumptions.md) holds the text.
- Commit: the owner authorized a commit of part 3. Push was not part of the authorization.
- The level words were not discussed. The page keeps the classes of Mishra et al. 2019 as delivered, and the question stays open.
- Features from the SFEI survey: none is scheduled until a user asks for a specific feature. S3 and S5 to S9 stay documented in [the probe record](../probes/2026-09-25-sfei-fhab-survey.md#candidate-features-for-the-lake-dashboard) and are listed in [the work plan](../work-plan.md#candidates-not-scheduled).

## Open for the owner

1. The level words: keep the four classes of Mishra et al. 2019, switch to another scheme, or show estimates without words.
2. Push, which redeploys the Vercel site with parts 2 and 3.

## Proposed next step

Part 4: historical pixel images under option B, stepping through time, and the compared weeks as pixel maps.
