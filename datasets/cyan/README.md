# cyan: CyAN cyanobacteria index

Status: characterized on 2026-09-22, owner review pending. Step 1 of [the work plan](../../docs/work-plan.md). No file pulled. Read [METADATA.md](METADATA.md) first.

What it is: the NASA-produced `CI_cyano` Level-3 mapped product for the EPA Cyanobacteria Assessment Network. The Ocean Biology DAAC distributes it as 8-bit GeoTIFF tiles and whole-region mosaics at 300 m in EPSG:5070. Composites are daily and 7-day maximum.
[METADATA.md](METADATA.md) holds the characterization. Its 100 claims from 17 primary sources each carry a verbatim quote confirmed by a checking agent. Section 12 lists the open items.

## Plan for this folder

- Step 1a wrote `METADATA.md` with a research agent and a checking agent. Done 2026-09-22.
- Step 1b ports the HAB_PoC repository's `cyan_api.py` and `pull_cyan.py` into `access/` with tests. It adds an Earthdata Cloud S3 reader as a second access path to compare.
- Step 1c ports `qa_cyan.py` into `qaqc/`.
- Step 1d builds the review dashboard data under `viz/`.
- Local scope is assumption A8: weekly whole-region mosaics from 2016 plus 8 weeks of dailies.

## Prior code to port

From the owner's HAB_PoC repository, `data-sources/cyan/`. `access/cyan_api.py` holds the encoding constants, filename parser, stream preference, and file search. `access/pull_cyan.py` holds the enumerate-plan-download flow. `qaqc/qa_cyan.py` and `viz/viz_cyan.py` follow. Its `METADATA.md` is input, not evidence.
