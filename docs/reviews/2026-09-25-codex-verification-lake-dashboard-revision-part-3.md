# Codex verification of the part 3 commit: an unqualified coverage claim, and the earlier fixes confirmed, 2026-09-25

Requested by the implementer, Claude Code, before the owner's decision on publishing. The request and the answer stay together in this file. The owner separately requested [an independent verification](2026-09-25-cyan-dashboard-part-3-independent-verification.md).

## Request

Run with `codex exec -s read-only` from the repository root on 2026-09-25, from 21:58 to 22:03 UTC. The request is verbatim.

```text
You are verifying committed work before it is published. Work read-only. Do not contact any website or data provider. Do not edit files.

Commit `31c3462` holds part 3 of the step 1f revision of the CyAN lake dashboard. Your earlier review of part 3 is in `docs/reviews/2026-09-25-codex-review-lake-dashboard-revision-part-3.md`. The implementer's dispositions of its nine findings are in `docs/reviews/2026-09-25-cyan-lake-dashboard-revision-part-3.md`, section "Codex review, 2026-09-25". The fixes were made after that review and before the commit, so no reviewer has seen them. Read `CLAUDE.md` and `.claude/rules/docs.md` first. Use `git show 31c3462` and `git diff e808d82 31c3462`.

1. For each of the nine findings, say whether the committed fix resolves it: resolved, partly resolved, or not resolved, with evidence from the committed files.
2. Look for regressions the fixes introduced in `docs/dashboards/cyan-lakes/index.html`. Cover the `level` and `abundance` helpers for codes 0, 0.5, 1, 41, 41.5, 42, 101.5, 186.5, 187, and 253. Cover every caller of those helpers, the renamed `earlyYears` and `AFTER_EARLY_YEARS`, the FAQ links with `href="#"` and their click handler, and the compare footnote.
3. Check the new wording of assumption A17 in `docs/assumptions.md` and its use in measurements 13 and 14. Does anything on the page or in a dataset use a pooled number that A17's new terms forbid?
4. Check that nothing committed carries a restrictive license, a local absolute path, a credential, or a personal name other than a citation.
5. Say whether anything you find blocks publishing the page. The page deploys to a public Vercel site when the owner pushes.

Put blocking problems first. Keep the answer under 700 words.
```

## Answer

Reviewer: Codex CLI 0.156.1, model `gpt-6-astra`, run read-only. The answer below is verbatim, except that local absolute links were made relative and their line suffixes dropped. The dispositions are in [the part 3 record](2026-09-25-cyan-lake-dashboard-revision-part-3.md#independent-verification-requested-by-the-owner-2026-09-25).

**Before publishing, fix the unqualified coverage claim** in the [year-plot note and compare footnote](../../docs/dashboards/cyan-lakes/index.html). Both omit “May to October.” The committed all-month results show 2016 at **87.48%** of lake-weeks with a value, versus **80.54%** in 2019. The FAQ correctly limits the comparison to May–October. Add that qualification to both notes.

A separate, pre-existing publication gate remains: the [dashboard README](../../docs/dashboards/cyan-lakes/README.md) explicitly leaves Esri’s public-site terms unresolved. This offline review cannot close that item.

I reviewed `31c3462` using `git show` and `git diff e808d82 31c3462`, excluding uncommitted review changes. No files were edited or websites contacted.

| Earlier finding | Verdict | Committed evidence |
|---|---|---|
| 1. Restrictive-license conflict | **Resolved** | Coffer 2020’s XML is absent. `cyan-abundance-research.json:58` records the conflicting license and omission. Thirteen source files remain. |
| 2. Unsupported satellite cutoff | **Partly resolved** | `index.html:293–296` now defines an early-calendar-years marker, and the FAQ acknowledges the unknown first contributing week. The unqualified coverage wording above remains misleading. |
| 3. Fractional medians | **Resolved** | `index.html:289–292` classifies the unrounded cell estimate and suppresses estimates below code 1. All requested boundary checks pass. |
| 4. Measurement 14 interpretation | **Resolved** | `measurements.md`, section 14, identifies shares, partial years, and equal weighting of lake-weeks. Its table agrees with the committed JSON. |
| 5. Overstated scientific claims | **Resolved** | `METADATA.md:100–103` restores the historical uncertainty and validation qualifications. D9 now says “Unresolved.” The FAQ removes the unsupported absence claim. |
| 6. SFEI treatment | **Resolved** | The probe’s code-0 row restores both footnote meanings. S8 requires a decision defining a new bloom. The introduction identifies S1, S2, and S4 as delivered. |
| 7. Keyboard FAQ links | **Resolved** | All five FAQ anchors have `href="#"`. The delegated handler prevents navigation and opens the requested entry. |
| 8. Diagnostic aggregation authorization | **Resolved** | A17 records the owner’s diagnostic exception. Measurements 13 and 14 explicitly identify pooled diagnostics. |
| 9. Document conventions | **Partly resolved** | Placeholders are replaced and the long METADATA class description is split. Repeated facts remain, expressly acknowledged by the disposition. Long new sentences remain, including the FAQ’s Mishra attribution. |

The committed helpers produce:

| Code | `level` | `abundance` estimate |
|---|---|---|
| 0 | below detection | none |
| 0.5 | near the detection limit | none |
| 1 | low | about 7,000 |
| 41, 41.5 | low | about 20,000 |
| 42 | moderate | about 20,000 |
| 101.5 | high | about 100,000 |
| 186.5 | high | about 1,000,000 |
| 187 | very high | about 1,000,000 |
| 253 | very high | about 6,000,000 |

Estimates are cells/mL. Rounding blurs boundaries, but classifications correctly use unrounded values.

I traced every caller: map popup, pixel readout, slider note, lake facts, and weekly/year hover data through `abundanceOf`. Nulls are guarded, and pixel codes 0/254/255 bypass conversion. `cells(0)` remains callable internally but does not reach those displays.

`earlyYears` and `AFTER_EARLY_YEARS` consistently control dotted traces, row asterisks, and footnote visibility. No stale names remain. Extracted-function checks preserve year-plot gaps, paired hover data, scalar/paired clicks, FAQ outside-click closing, and footnote clearing. No runtime regression was found.

A17’s diagnostic numbers feed neither the page nor dataset builders. Existing duration counts and retained per-lake summaries remain authorized by decision 0003.

The publication-content check is **not entirely clean**: the new [EPA factsheet](../../datasets/cyan/reference/abundance/epa-hh-rec-criteria-habs-factsheet-2019.txt) contains two named agency contacts, not citations. Older committed plan/QA files also contain local absolute paths. These sit outside the Vercel dashboard folder. I found no new credentials, local paths, or restrictively licensed full-text additions.

Two non-writing measurement tests and Ruff checks passed. Full `/check` and browser rendering were not run under the read-only constraints.
