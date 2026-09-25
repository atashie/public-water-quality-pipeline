# Codex review of the plan for the step 1f revision: two scope errors, one missed hosting limit, and wording corrections, 2026-09-25

Requested by the implementer, Claude Code, under the repository's rule that Codex is the preferred second model for adversarial reviews of plans. The request and the answer stay together in this file.

## Request

You are reviewing a plan, not code. Work read-only. Do not contact any data provider. Do not edit files.

Read `CLAUDE.md`, `.claude/rules/docs.md`, `.claude/rules/datasets.md`, and `docs/reviews/2026-09-25-cyan-lake-dashboard-scientist-feedback.md`. Then read what that record cites: measurements 11 and 12 in `docs/measurements.md`, `docs/vercel-hosting.md`, decision 0002, assumption A17 in `docs/assumptions.md`, `datasets/cyan/METADATA.md`, and `docs/dashboards/cyan-lakes/index.html`.

Check these, and report each as confirmed, wrong, or unsupported, with evidence:

1. Findings 1 to 3 of the record. Recompute them from `data/cyan/derived/cyan_lake_table-2026-09-23T1436Z.parquet` with your own query. Use weekly rows only, `temporal == "7D"`. Check the share of rows with a value whose median is 0, the share whose every valid pixel is 0, and Lake Henshaw, COMID 20342929. Check the count of lakes with a land-coded interior pixel in every weekly file, and the counts capped under 90 and 50 percent coverage.
2. Measurement 12 against `datasets/cyan/outputs/pixel-history-2026-09-24T1126Z.json`. Check every number and the claim that the key `year_bytes` holds whole-record totals.
3. The estimate for option B: 125 mid-month weeks, 112 outside the newest 52, about 160 MB. Count the weeks from the file names under `data/cyan/raw/weekly_conus_mosaic/`.
4. The hosting analysis. Is the conclusion that git and GitHub's guidance, not Vercel, bind the size sound? Is anything missed that makes option B fail on a Vercel git deployment, or makes Vercel Blob workable on Hobby?
5. The baseline section. Is anything in part 2 actually a temporal aggregation under A17? Is the year-over-year plot free of aggregation? Is the claim about merged Sentinel-3A and 3B maxima supported by the METADATA? Is any listed recipe choice wrong or missing?
6. The dispositions. Does any part-2 change need a new claim that is not yet `documented`, `measured`, or `probe`? Does coloring pixels in the browser from the existing code images work when the page is opened from disk, given that the code images are data URLs?
7. Anything in the plan that breaks a repository rule: one fact in one home, statuses, no names, plain English, no semicolons, sentences of 25 words or fewer.

Put the most serious problems first. Keep the answer under 900 words.

## Answer

Reviewer: Codex CLI 0.156.1, model `gpt-6-astra`, run read-only with `codex exec -s read-only` on 2026-09-25. The answer below is verbatim, except that local absolute links were made relative and their line suffixes dropped. The dispositions are in [the revision record](2026-09-25-cyan-lake-dashboard-scientist-feedback.md#codex-review-2026-09-25).

The plan needs corrections before approval. I read the requested files and ran independent, read-only queries. No files changed or data providers were contacted.

1. **Wrong: part 2 needs “no new claims” or aggregation authorization.**  
   Displaying each lake’s historical coverage ceiling introduces a new summary across weeks. Whether calculated as maximum coverage or minimum land count, it needs a recipe and recorded authorization under A17. Decision 0002 authorizes only statistics within individual files.

   The ceiling also remains `unverified` until the proposed checked-in measurement produces evidence. Existing browser series lack `n_land`, so distinguishing a land-based ceiling from observed maximum coverage requires additional derived information.

   Renaming the already approved bloom count adds no aggregation. Recording its existing recipe would resolve the documentation gap. [Plan](2026-09-25-cyan-lake-dashboard-scientist-feedback.md)

2. **Unsupported: GitHub guidance alone binds deployment size.**  
   GitHub’s 1 GB figure is guidance, not a hard repository limit. Uncompressed image bytes also cannot establish packed Git growth across rebuilds. [GitHub documentation](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github)

   The cited upload caps do explicitly concern CLI deployments. I found no size rule that inherently disqualifies B through git. [Vercel limits](https://vercel.com/docs/limits)

   However, the plan misses Hobby’s **10 GB Deployment Storage allowance**, shared across retained deployments. Exhausting it can block deployment, including B. Available account capacity remains unknown. [Vercel’s September 16 announcement](https://vercel.com/changelog/hobby-projects-now-retain-fewer-deployments-to-free-up-storage)

3. **Wrong: Blob requires shared files to work on Hobby.**  
   **Confirmed:** 2,321 ordinary uploads exceed 2,000 advanced operations within one allowance window. **Unsupported:** this makes separate lake files permanently infeasible.

   Staging uploads across usage windows, or keeping some files in git, offers alternatives to bundling. This is an inference from the recurring allowance. Reserve operations for store creation, listing, and multipart uploads. Storage, 10 GB transfer, and 10,000 simple operations also constrain use. [Blob pricing](https://vercel.com/docs/vercel-blob/usage-and-pricing)

4. **Findings 1–3: counts confirmed, several interpretations wrong or unsupported.**  
   My Parquet query filtered `temporal == "7D"` and used `n_valid > 0` for percentage denominators.

   | Check | Independent result |
   |---|---:|
   | Weekly rows | 1,257,982 |
   | Rows with a value | 1,040,186 |
   | Median equals zero | 824,157, **79.2317%** |
   | Every valid pixel equals zero | 512,444, **49.2647%** |
   | Every interior pixel equals zero | 174,009, **16.7286%** of valued rows |

   Finding 1’s “every interior pixel” is **wrong**. Its 49 percent concerns valid pixels. “Most lakes … solid dark blue” is **unsupported**, particularly because displayed shoreline pixels are excluded from these statistics.

   Henshaw, COMID 20342929: **confirmed** 53 interior pixels, 12 land-coded pixels in each of 542 files, maximum coverage 41/53 = **77.3585%**, reached **304** times.

   Grouping lakes and calculating `1 − min(n_land)/n_interior` confirms **517** with land counts in every file, **118** below 90%, and **12** below 50%.

   Counts cannot establish that the **same pixels** remain land-coded throughout. “Statistics are unaffected” is also unsupported. Exclusion prevents code contamination but can change spatial representativeness. [Findings](2026-09-25-cyan-lake-dashboard-scientist-feedback.md)

5. **Baseline: partly confirmed, recipe incomplete.**  
   The year-over-year plot introduces **no new temporal aggregation** if it merely repositions existing weekly medians. Existing spatial aggregation remains. Preserve missing weeks and define week numbering, year boundaries, and week 53.

   The merged Sentinel-3A/3B maxima from 2018 are explicitly supported by METADATA section 2. Increasing a fixed observation set cannot decrease its maximum. That does not establish the actual historical effect.

   **Wrong without qualification:** the geometric-mean statement includes code zero implicitly. METADATA restricts conversion to codes 1–253. Below-detection handling needs an explicit choice. Also specify year weighting, minimum valid years, gap treatment, and quantile conventions. Winter weeks “mostly” missing remains unsupported as a quantified generalization. [METADATA](../../datasets/cyan/METADATA.md)

6. **Measurement 12: confirmed against its JSON.**  
   Every reported number matches, including totals, extrema, lake quantiles, largest-lake values, runtime, revision, and clean-tree flag. Weekly sums reproduce **2,852,768,760** and **899,061,756** bytes. Stacked bytes total **515,666,746**, averaging **951,414.6605** per file.

   `year_bytes` covers the whole run, confirmed by the script’s summation. September 19 is the final window’s end, while JSON records September 13 as its start. Measurement 11’s reference to **543 files** is stale. [Measurements](../../docs/measurements.md)

7. **Option B: confirmed as an estimate.**  
   Filenames yield **125** mid-month weeks, **112** outside the newest 52, and **164** distinct selected files. All **11** August selections match. The calculation gives **159.30 MB**. Actual compression remains unmeasured. Masks and outlines add **62.37 MB**, before other dashboard assets.

8. **Browser recoloring: confirmed technically.**  
   Existing `pixelSamples()` already reads both embedded PNG data URLs through canvas. Recoloring can preserve alpha and work from disk without pixel-file changes. Data URLs do not create the proposed cross-origin obstacle. [Code](../../docs/dashboards/cyan-lakes/index.html), [Fetch standard](https://fetch.spec.whatwg.org/#main-fetch)

9. **Repository rules: violations confirmed.**  
   Hosting facts and byte totals have multiple homes. Some assertions lack statuses. “Corrected with evidence” conflicts with findings still labeled `unverified`. The baseline examples sentence exceeds 25 words, and “today” violates the relative-date rule. No colleague-name, semicolon, or “should” violation appeared in the plan.
