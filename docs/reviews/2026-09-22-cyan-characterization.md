# Step 1a, CyAN characterization: release notes preserved, 100 claims researched and independently checked, METADATA bound to the checks, cloud catalog lag recorded, 2026-09-22

Implementer: Claude Code (AI coding agent), directed by the repository owner, with a research agent on Opus and a checking agent on Sonnet. Scope: step 1a of [the work plan](../work-plan.md). No data file pulled. Nothing committed.

## What the owner directed

The owner authorized step 1a after the initialization review on 2026-09-22 and answered assumptions A18 and A20 the same day. Those answers and the new A21 are recorded in [assumptions.md](../assumptions.md) and [decision 0001](../decisions/0001-scope-conventions-and-dataset-order.md).

## What changed

| Area | Change |
|---|---|
| Reference | The version 6 release notes PDF, 1,929,326 bytes, sha256 `e48b56a1...54f99`, byte-identical to the HAB_PoC copy, with a 31-page text extraction and a provenance README under `datasets/cyan/reference/` |
| Research | `cyan-research.json`: 17 primary sources, 100 claims with verbatim quotes and locators, 9 topics not found, 6 discrepancies, 10 limitations. Every quote was machine-verified by the researcher as a substring of the fetched source |
| Checks | `cyan-checks.json`: one verdict per claim by a checking agent on a different model, which re-fetched every source. Counts in the table below |
| METADATA | `datasets/cyan/METADATA.md`, twelve sections. Every documented fact cites a claim id. Prior HAB_PoC facts are labeled `prior`. Open items and discrepancies are in section 12 with the step that resolves each |
| Probes | [CyAN catalogs, cloud lag, and reference documents](../probes/2026-09-22-cyan-catalogs.md): the Earthdata Cloud catalog trails the OB.DAAC file search by 7 weeks and 8 weekly files, neighboring collections, lake shapefile header |
| Tests | `tests/test_dataset_claims.py`: research records are well formed, every claim has a check, checker and researcher differ by model, and every claim id cited in a METADATA has a confirmed or corrected check |
| Assumptions | A18 and A20 `sourced`. A21 added. Decision 0001 amended with the owner's answers and a global-scope review trigger |

## Findings worth the owner's attention

1. **Direct cloud access exists but its catalog lags.** The collection lives in `s3://ob-cumulus-prod-public/` with in-region temporary credentials. That could remove the download step from the AWS design. On 2026-09-22 the cloud catalog held nothing newer than 2026-08-01 while the file search listed 2026-09-19. Step 1b must list the bucket with a token before step 1g relies on it.
2. **The distributed files are GeoTIFF, whatever the catalog says.** The collection metadata declares netCDF-4. Granule-level metadata says TIFF, every listed file ends in `.tif`, and the release notes say 8-bit GeoTIFF. Confirmed by a separate probe at the owner's request. Discrepancy D3.
3. **Four different start years for OLCI.** The earliest weekly file starts 2016-04-24 and the earliest daily 2016-04-25. A separate probe confirmed both at the owner's request. The release notes' 2017 is the instrument era. The form's 2007 spans MERIS and OLCI. Discrepancy D1.
4. **Five facts are on no page.** Weekly update timing, the EPSG code, tile dimensions, COMID in the shapefile, and flag bands. Each is an open item in section 12 with a resolving step. The HAB_PoC values for them stay `prior`.
5. **Zero is a measurement.** The producer's encoding makes 0 "below threshold" and 255 "no data". The QA and the derived tables keep them apart.

## Owner direction on this record, 2026-09-22

| Direction | Disposition |
|---|---|
| Use Codex as the second model for adversarial reviews of work and plans, directly or through a prompt the owner runs | Fixed. Recorded in [CLAUDE.md](../../CLAUDE.md), assumption A5, and the dataset loop |
| Finding 1 matters for Discovery. The AWS route is preferred if the data are identical, and a lagging bucket changes that | Fixed. Recorded as a Discovery input in [docs/aws/cyan.md](../aws/cyan.md), with the step 1b comparison that decides |
| Confirm findings 2 and 3 with a subagent | Fixed. [Probe record](../probes/2026-09-22-cyan-format-and-start.md). Discrepancies D1 and D3 cite it |
| Finding 4 is an unknown to uncover later, not essential now | Fixed. O1 to O4 marked not needed now in METADATA section 12 |
| The agency-list finding is inconsequential | Fixed. Dropped from this record and from METADATA. The checker's note stays in the checks file as evidence |
| Commit and push step 1a with the A18 to A21 edits | Authorized 2026-09-22 |

## Checks

| Check | Result |
|---|---|
| Claim verdicts | 100 checked. 96 confirmed, 4 corrected, 0 not verifiable. The four corrections fix quote transcription only: curly apostrophes and quotation marks in three release-notes quotes, and the HTTPS prefix claim now quotes the link field instead of the title field. Values and notes unchanged |
| `uv run pytest -q` | 48 passed. Links, dates, helper, and the three claim-binding tests. No network |
| `uv run ruff check .` and `uv run ruff format --check .` | Pass |
| Name scan | No colleague's name. Cited authors appear only inside verbatim quotes |
| Credential scan | Clean. No `.env` read by any agent |
| Sentence audit | Prose sentences over 25 words reworded. Verbatim quotes exempt |

## Limits

- Nothing is verified against an actual file. Encoding, projection, tile geometry, and version tags are documentation claims until step 1c opens pulled files.
- The us-west-2 limit is stated for this collection in its own metadata record. The general statement comes from a community-maintained NASA Openscapes page and a LAADS DAAC page, not an OB.DAAC page.
- The two shapefile URLs and the HTTPS distribution prefix were verified from HTML attributes, not from visible text.
- The lag between the cloud catalog and the file search is measured on one day.
- The HAB_PoC METADATA was used only to know what to look for. None of its facts entered a claim.

## Dispositions of prior findings

| Finding | Disposition |
|---|---|
| Initialization review: the two CyAN catalogs disagreed on the newest granule | Corrected with evidence. The disagreement is a lag of the cloud catalog, measured at 7 weeks. Bucket contents remain to be listed, step 1b |
| Initialization review: assumptions A18 and A20 unsourced | Fixed. Owner answers recorded |
| Initialization review: HAB_PoC facts are `prior` | Accepted and deferred. Steps 1b, 1c, and 1e verify them from files |

## Proposed next step

Owner review of the METADATA, in particular section 12. Then authorization to commit this step together with the A18 to A21 edits. Then step 1b. It ports the search and pull scripts with tests, runs the dry run, and lists the cloud bucket with a token. The download of the assumption A8 scope needs its own authorization.
