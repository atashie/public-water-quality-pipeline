# Codex review of part 3 of the step 1f revision: a license conflict, an unsupported satellite cutoff, and half-code medians, 2026-09-25

Requested by the implementer, Claude Code, under the repository's rule that Codex is the preferred second model for adversarial reviews of work. The request and the answer stay together in this file.

## Request

Run with `codex exec -s read-only` from the repository root on 2026-09-25, from 17:49:27 to 17:55:06 UTC. `<scratch>` stands for the implementer's scratch folder. The request is otherwise verbatim.

```text
You are reviewing delivered work. Work read-only. Do not contact any website or data provider. Do not edit files.

Read `CLAUDE.md`, `.claude/rules/docs.md`, `.claude/rules/datasets.md`, `docs/reviews/2026-09-25-cyan-lake-dashboard-revision-part-3.md`, `docs/decisions/0003-comparisons-across-time.md`, and `docs/assumptions.md` for A17. Use `git status` and `git diff` to see what changed since revision `e808d82`. The changed and new files include `docs/dashboards/cyan-lakes/index.html`, `datasets/cyan/METADATA.md`, `datasets/cyan/reference/cyan-abundance-research.json`, `datasets/cyan/reference/cyan-abundance-checks.json`, `datasets/cyan/reference/abundance/`, `docs/probes/2026-09-25-sfei-fhab-survey.md`, `datasets/cyan/qaqc/measure_coverage_by_year.py` with its test, `datasets/cyan/outputs/coverage-by-year-2026-09-25T1701Z.json`, and measurement 14 in `docs/measurements.md`.

The saved copies behind the SFEI probe record are in `<scratch>/sfei/`. The saved copies behind the abundance claims are in `<scratch>/abundance-sources/`.

Check these, and report each as confirmed, wrong, or unsupported, with evidence:

1. Bugs in `index.html`: the `cells`, `firstCode`, `LEVELS`, `level`, and `abundance` helpers, including fractional median codes such as 223.5 and code 0; the level band's positions against the slider's coordinates; the pixel readout for codes 0, 254, and 255; the FAQ links and the click handler that closes the FAQ; the year plot's new `customdata` pairs, its hover, its gap handling, and its click handler; the compare footnote; and the dotted 2016 to 2018 lines.
2. Every statement the page makes about abundance, levels, toxins, depth, and Sentinel-3B, in the FAQ, the notes, and the code comments. Is each supported by an approved value in `cyan-abundance-checks.json`? Flag overstatement.
3. `datasets/cyan/METADATA.md`: does each new sentence match the approved value of the claims it tags, not the draft value? Are D8 to D12 accurate against the research record's discrepancies?
4. Measurement 14 against the result file and the script's logic.
5. The SFEI probe record: its quotes against the saved copies, and its candidate features S1 to S9 against decisions 0002 and 0003.
6. Assumption A17 and decision 0003: does the page now show or compute any number across weeks or lakes that no decision records?
7. The licenses: is it defensible to commit the 14 files under `datasets/cyan/reference/abundance/`, given the licenses in `cyan-abundance-research.json`? Is anything committed that has a restrictive license?
8. Repository rules in the new and changed documents: statuses, one fact in one home, no personal names beyond citations, plain English, no semicolons, sentences of 25 words or fewer, no relative dates.

Put the most serious problems first. Keep the answer under 900 words.
```

## Answer

Reviewer: Codex CLI 0.156.1, model `gpt-6-astra`, run read-only. The answer below is verbatim, except that local absolute links were made relative and their line suffixes dropped. The link to the Coffer et al. 2020 file is shown as a path, because the file was removed after this review. The dispositions are in [the part 3 record](2026-09-25-cyan-lake-dashboard-revision-part-3.md#codex-review-2026-09-25).

Reviewed locally against `e808d82`, including untracked files and saved sources. No files were edited and no external sources were contacted.

1. **Wrong: the unrestricted-license claim.** Coffer 2020’s XML (`datasets/cyan/reference/abundance/coffer-2020-PMC8318153.xml`) displays “CC BY” but links to `creativecommons.org/licenses/by-nc/4.0/`. The research record overlooks that conflict. Committing all 14 files as unrestricted is **unsupported** until this is resolved. The other files match their recorded federal-work, CC BY, or CC0 provenance. All 14 are currently untracked, so this is proposed inclusion, not an existing commit.

2. **Unsupported: January 2019 as a satellite cutoff.** The [page’s constant, comments, limits, and compare footnote](../../docs/dashboards/cyan-lakes/index.html) treat every earlier week as having fewer passes. Approved sensor claims establish merging from 2018, but explicitly leave the first contributing week unknown. Measurement 14 measures coverage, not passes or causation. The dotted 2016–2018 traces are implemented correctly, but should identify the observed coverage period rather than assert a satellite boundary.

3. **Wrong: fractional-median cell-range labels.** [The helpers](../../docs/dashboards/cyan-lakes/index.html) label code **101.5 “moderate”**, although its estimate is **100,435 cells/mL**, within the FAQ’s “high” cell range. The table contains 185 such weekly medians. Integer thresholds applied to fractional medians cause this mismatch.

   **Confirmed:** `firstCode` returns 42, 102, and 187. Code 223.5 produces approximately 2.70 million, displayed as “very high, about 3,000,000.” `abundance(0)` correctly says below detection. However, `cells(0)` returns 6,500 internally, and 259 medians of 0.5 receive extrapolated estimates below the checked formula’s domain. That treatment is **unsupported**.

4. **Confirmed calculations; wrong interpretation in Measurement 14.** I reproduced both yearly result arrays from the local Parquet file. Input and script hashes match. There are 1,257,982 weekly rows, with 2,321 distinct lakes per file and no duplicate lake-weeks.

   [“Makes years comparable”](../../docs/measurements.md) overstates the seasonal filter: 2026 excludes October and part of September. “Fewer lake-weeks with a value” is also **wrong as a count**: 2016 has 57,910 versus 2026’s 42,508. The supported finding concerns **shares**. The mean valid share weights lake-weeks equally, not pixels.

5. **Mostly confirmed: page claims and METADATA.** The approved values support the conversion, Microcystis equivalence, historical Lake Erie uncertainty, Mishra adaptation, WHO framework change, toxin distinction, EPA concentrations, and qualified near-surface depth explanation. Launch and release dates are supported. Coverage comparisons come from Measurement 14, not the abundance checks.

   Exceptions: [California’s recommendation](../../datasets/cyan/METADATA.md) loses “without additional validation and study” in both METADATA and the FAQ. That blanket wording overstates the approved value. “The product defines none” lacks an approved absence claim. D8–D12 otherwise accurately summarize the discrepancies, but D9’s “likely” sign-convention explanation remains **unsupported**. The review’s unqualified “uncertainty is about a factor of two” repeats an already-corrected overstatement.

6. **Confirmed quotes; wrong SFEI footnote treatment.** All nine saved-source hashes match. The substantive quotations match after whitespace normalization. But [row 0](../../docs/probes/2026-09-25-sfei-fhab-survey.md) removes essential footnotes: “Background Level” applies to CI, while “Non-Detect” applies to chlorophyll.

   S1–S5 fit the existing display/statistic scope. S6–S7 correctly require new decisions. S9 correctly identifies unavailable classes. S8 is **unsupported as merely a refresh task**: neither decision defines a new-bloom alert rule. “None is built” is **wrong**, given delivered S1, S2, and S4.

7. **Confirmed interaction logic, with limitations.** Extracted-function checks confirmed pixel handling for 0/254/255, FAQ mouse opening and outside-click closing, year-plot paired `customdata`, hover indexing, missing-file gaps, and clicks on both paired and scalar data. Compare-footnote visibility works. FAQ anchors lack `href` or keyboard activation: **wrong for keyboard access**. The band uses the intended `(code−1)/252` coordinates and four-pixel inset; exact browser alignment remains **unsupported by this review**.

8. **Confirmed: no new pooled number on the page.** New estimates transform individual existing statistics. Comparisons and duration counts retain decision 0003’s recipes. Measurement 14 itself pools weeks and lakes outside the page; no decision records that new diagnostic recipe under A17.

9. **Wrong: complete document-rule compliance.** Facts repeat across METADATA, README, and review prose. New sentences exceed 25 words, including METADATA’s Mishra-class sentence. The review uses relative wording such as “now” and retains `CHECK_LINT`/`CHECK_TESTS` placeholders. I found no new noncitation personal names or unquoted Markdown semicolons.

Read-only verification: **95 tests passed**, one writing test excluded. Ruff checks passed. Full `/check` was not run because synchronization and writing tests conflict with your read-only instruction.
