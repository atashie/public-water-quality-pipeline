# CyAN reference documents

Preserved primary documents for the CyAN characterization, with their provenance. Research and check records for the claims in `../METADATA.md` live here too.

| File | What | Provenance |
|---|---|---|
| `CyAN_NASA_MERISOLCI_CI_release_notes_V6_Aug_2025.pdf` | NASA OBPG release notes for the MERIS and OLCI cyanobacteria index product, version 6, with the known-issues update of 2025-08 | Downloaded 2026-09-22 from `https://oceancolor.gsfc.nasa.gov/images/cyan/version/6/CyAN_NASA_MERISOLCI_CI_release_notes_V6_Aug_2025.pdf`. 1,929,326 bytes. sha256 `e48b56a192215394c74cad3429d3dd3d07ca2cae714dffcc5f5b807edf154f99`. Byte-identical to the copy the HAB_PoC repository preserved on 2026-07-01 |
| `CyAN_NASA_MERISOLCI_CI_release_notes_V6_Aug_2025.txt` | Text extraction of the PDF, 31 pages, page markers inserted | Extracted 2026-09-22 with `pypdf`. Quotes in the research record cite this text. Tables and figures lose their layout in extraction |
| `mishra-2019-europepmc-PMC6892802.xml` | Full text of Mishra et al. (2019), Measurement of cyanobacterial bloom magnitude using satellite remote sensing, Scientific Reports 9, 18310, doi:10.1038/s41598-019-54453-y, open access | Downloaded 2026-09-23 from `https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6892802/fullTextXML`. 166,140 bytes. sha256 `51de85305becea2fc9406dc0617858f8520144048595eb8043dbe4bba9ecfd03`. Quoted in the [probe record of 2026-09-23](../../../docs/probes/2026-09-23-cyan-vs-clms-assertions.md) for the index bands and the cell conversion |
| `cyan-research.json` | Draft claims with verbatim quotes and locators, by the research agent | Written in step 1a. Format in [../../README.md](../../README.md) |
| `cyan-checks.json` | Independent verdicts on every draft claim, by a checking agent on a different model | Written in step 1a |
| `cyan-abundance-research.json` | 51 draft claims on the index as abundance: the cells per mL factor, its uncertainty and range, named levels, toxins, and Sentinel-3B dates. Each source records its URL, date, size, sha256, license, and any local copy | Written 2026-09-25 in part 3 of the step 1f revision by a research agent. The parent agent added 2 claims |
| `cyan-abundance-checks.json` | Codex's verdicts on all 51 claims, its extra checks, and its most serious findings | Written 2026-09-25. [Request and answer](../../../docs/reviews/2026-09-25-codex-check-cyan-abundance-claims.md) |
| `abundance/` | 13 sources of the abundance claims. All are US government works or open under CC BY 4.0 or CC0. For the EPA user guides and the NOAA bulletin only the text extraction is kept | Downloaded 2026-09-25 by the research agent. Sources under other licenses are cited by URL, size, and sha256 in `cyan-abundance-research.json` |

Documents here are input to `METADATA.md`. A fact becomes `documented` only when its check record says `confirmed` or `corrected`.
