# Codex check of 51 claims on what the CyAN index means in abundance terms: 35 confirmed, 16 corrected, 2026-09-25

Requested by the implementer, Claude Code, under the repository's rule that research uses a separate checking agent on a different model. The request and the answer stay together here. The per-claim verdicts are in [cyan-abundance-checks.json](../../datasets/cyan/reference/cyan-abundance-checks.json), beside the draft claims in [cyan-abundance-research.json](../../datasets/cyan/reference/cyan-abundance-research.json). The dispositions are in [the part 3 record](2026-09-25-cyan-lake-dashboard-revision-part-3.md).

## Request

Run with `codex exec -s read-only` from the repository root on 2026-09-25, from 17:30:58 to 17:44:18 UTC. `<scratch>` stands for the implementer's scratch folder, which held the draft and the saved sources. The request is otherwise verbatim.

```text
You are the checking agent for draft research claims. A research agent on a different model drafted them. Work read-only. Do not edit files. Do not contact any website or data provider. Check every claim against the saved copy of its source, which is local.

Files:
- The draft claims: <scratch>/abundance-sources/cyan-research-abundance.json. 51 claims. Each has an id, a value, a note, source_ids, a verbatim quote, a locator, and a proposed status.
- The saved sources: the other files in <scratch>/abundance-sources/. Each source in the JSON names its `local_copy`. `sources-manifest.json` gives each file's URL, access time, sha256, and license. For PDFs, a `.txt` extraction sits next to the PDF. You may also run `pdftotext <pdf> -` yourself. For HTML, a `.stripped.txt` sits next to some files.
- The format to follow: datasets/cyan/reference/cyan-checks.json in the repository, key `checks`.
- Context: datasets/cyan/METADATA.md, sections 4 and 12, and docs/probes/2026-09-23-cyan-vs-clms-assertions.md, section A1.

For each claim:
1. Confirm the quote occurs in the saved copy. Normalize whitespace. The research agent kept `<sup>` and `<sub>` tags literally in XML quotes, and " ... " joins two segments from the same locator. Say how you matched.
2. Confirm the locator leads to the quote.
3. Judge whether the quote supports the value and the note as written. Look for overstatement, a value the quote does not state, arithmetic added by the researcher, a secondary source presented as primary, and a claim that holds for MERIS, NOAA's product, or another processing version but is stated as if it holds for CyAN version 6.
4. Give a verdict: `confirmed`, `corrected` (give the corrected value), or `rejected`. For the two claims proposed as `probe`, say whether `probe` is the right status.

Also check these, and report each as confirmed, wrong, or unsupported:
A. The discrepancy on NASA's range. With CI = 10^(0.011714 × code − 4.1870866) and cells = CI × 10^8, compute the cells for codes 1 and 253, and the code where 10,000 and 7,000,000 cells/mL fall.
B. The first CyAN code whose estimate reaches 20,000, 100,000, and 1,000,000 cells/mL. The implementer computes 42, 102, and 187. Confirm or correct.
C. Whether the claims support these statements, which the implementer intends to put on the dashboard:
   1. "Multiplied by 100,000,000, the index gives an estimate in cells per mL, counted as the equivalent of Microcystis cells."
   2. The estimate "was fitted to Microcystis in western Lake Erie" and "can be off by a factor of two or more".
   3. Four named levels, low up to 20,000, moderate from 20,000, high above 100,000, and very high above 1,000,000 cells/mL, attributed to Mishra et al. 2019, whose first three classes follow the WHO's cell-count guidance, which WHO replaced in 2021 with biovolume and chlorophyll-a levels.
   4. "The EPA's recommended values for swimming are toxin concentrations, 8 micrograms per liter of microcystins and 15 of cylindrospermopsin."
   5. "Sentinel-3B launched on 2018-04-25. Its first OLCI data after commissioning were released on 2018-12-12. The CyAN files merge both satellites from 2018 and keep the higher value per pixel."
   6. "The satellite sees the top layer of the water only, about a meter in clear water."

Reply with a JSON object only, no prose outside it, with these keys:
- "checker": {"agent": "Codex CLI", "model": <your model>, "checked_on": "2026-09-25"}
- "method": one paragraph on how you matched quotes and judged support.
- "checks": one object per claim, in the order of the draft, with keys id ("chk-" + claim id), claim_id, verdict, approved_value, approved_unit, approved_note, source_ids, quote, reason, checked_on. For a rejected claim, approved_value is null.
- "extra_checks": one object each for A, B, C1 to C6, with keys item, verdict, evidence.
- "most_serious": up to five one-sentence findings, most serious first.
```

## Answer

Checker: Codex CLI 0.156.1, model `gpt-6-astra`, which reported itself as GPT-6. The answer was one JSON object. Its `checks` array, 51 verdicts, is stored as returned in the checks file: 35 confirmed and 16 corrected. The rest of the answer is reproduced here verbatim.

### Method

I worked locally and read-only, made no network requests, and verified all 50 manifest-listed files against their SHA-256 hashes. I independently extracted PDF text, decoded HTML/XML entities, normalized whitespace, preserved literal sup/sub tags, and matched each ellipsis-separated quote segment separately. For inline HTML links, I also checked concatenated text nodes. I checked XML paragraph identifiers, section headings, PDF page numbers, surrounding qualifications, and relevant supplementary passages. I visually inspected the app screenshots, WHO's 2003 units and table, and WHO's 2021 summary and framework. Verdicts distinguish a source's own methods or recommendations from its reports of earlier research, identify researcher-added arithmetic, and restrict historical MERIS, NOAA, app, and processing-version findings to their supported scope. The draft actually contains three probe proposals: two screenshot readings and one catalog observation.

### Extra checks

| Item | Verdict | Evidence |
|---|---|---|
| A | confirmed | Independent arithmetic confirms the discrepancy. cells(code) = 10^(0.011714 × code + 3.8129134). Code 1 gives CI 0.0000667770762348 and 6,677.707623 cells/mL; code 253 gives CI 0.0597799297025 and 5,977,992.970248 cells/mL. The inverse is code = (log10(cells/10^8) + 4.1870866)/0.011714. Thus 10,000 cells/mL falls at code 15.9711968585, with code 16 giving 10,007.771941; 7,000,000 falls at code 258.8513436925, outside valid data codes 1–253. NASA's saved range statement is authentic but does not equal these formula endpoints. No saved source resolves the discrepancy. |
| B | confirmed | The first valid integer codes reaching the thresholds are 42, 102, and 187. Code 41 gives 19,642.076583 cells/mL and 42 gives 20,179.081761; code 101 gives 99,089.445928 and 102 gives 101,798.504987; code 186 gives 981,109.317082 and 187 gives 1,007,932.386473. These are derived arithmetic thresholds, not independently observed biological boundaries. Apply the formula only to data codes 1–253. |
| C1 | confirmed | Mishra 2019 Par18 and the paragraph after Equation 2 explicitly support multiplying decoded CI_cyano by 100,000,000 to obtain estimated Microcystis-equivalent cells/mL. Prefer 'expressed as Microcystis-equivalent cells' to 'counted': this is an empirical estimate, not an actual enumeration. The multiplier applies to decoded CI, not the stored 8-bit code. The sources document use of this conversion but do not independently validate it for version 6. |
| C2 | unsupported | The western Lake Erie Microcystis origin is explicitly reported by Coffer 2021a P13, although the original calibration paper is absent. The proposed 'factor of two or more' statement is not established for CyAN version 6: Stumpf 2012 says 'about two-fold' uncertainty and potential underestimation 'as much as a factor of 2' in its Lake Erie context. Mishra's two-orders-of-magnitude passage describes spatial biomass variability, not a conversion-error estimate. Supported wording is: 'The conversion was developed from Microcystis observations in western Lake Erie; earlier Lake Erie work reported roughly twofold conversion uncertainty.' |
| C3 | wrong | The four numerical levels are supported as Mishra 2019's classification, with Very High its addition. Calling the first three WHO's classes without qualification misrepresents the saved primary guidance: WHO 2003 Table 8.3 associates 20,000 cells/mL with relatively low probability, 100,000 with moderate probability, and scum with high probability. Describe the dashboard categories as adapted from Mishra, who based thresholds on earlier WHO guidance. Mishra overlaps Low and Moderate at exactly 20,000 and nests Very High within High, so a mutually exclusive dashboard needs an explicit boundary convention. WHO 2021 explicitly replaces the earlier framework with biomass and visual indicators, while still allowing locally calibrated cell counts. Its framework is more than a direct replacement of cell-count bins with chlorophyll bins. |
| C4 | confirmed | The saved EPA 2019 fact sheet, PDF page 2, gives 8 µg/L microcystins and 15 µg/L cylindrospermopsin. The EPA recreation page explicitly identifies these as recommended cyanotoxin concentrations. The proposed sentence accurately states the magnitudes; they are not satellite-cell thresholds, and the full criteria/advisories include application-specific duration and frequency provisions. |
| C5 | confirmed | SentiWiki and NASA LAADS agree on the 2018-04-25 launch. The archived EUMETSAT announcement identifies 2018-12-12 as availability of the first post-commissioning OLCI Level-1 release. Version 6 release notes page 6 state merged Sentinel-3A/3B products from 2018 onward, and page 16 states maximum value per pixel. These facts do not identify the exact first Sentinel-3B observation used by CyAN, imply coverage throughout all of 2018, or make December 12 the first acquisition date. |
| C6 | confirmed | Mishra Par38, Coffer 2021a P22, and Seegers P5 support near-surface sensitivity. Stumpf 2012 Methods > Satellite states that CI bands detect no light from deeper than one meter in clear water and penetrate less with more particles. More precise wording is: 'The index sees only near-surface water—up to about a meter in clear water, and less in turbid water.' The one-meter statement comes from MERIS-era work, not a separate version 6 depth validation. |

### Most serious

- The saved evidence does not establish 'a factor of two or more' as a CyAN version 6 error range; the twofold statements concern earlier Lake Erie work.
- Mishra's category labels are not identical to WHO's primary three-tier table, so the dashboard must attribute them as an adaptation rather than WHO's exact classes.
- NASA's stated 10,000–7,000,000 cells/mL range conflicts with the specified equation and multiplier, which yield approximately 6,678–5,977,993 for valid codes 1–253.
- SFEI's raw codes and product-specific footnotes cannot be transferred to CyAN, including its raw-zero Non-Detect label, which applies to chlorophyll rather than CI.
- The app figures document historical displayed settings rather than verified defaults, and the Android Very High boundary does not exactly match Lunetta's.
