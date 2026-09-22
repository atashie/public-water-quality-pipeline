# cyan: CyAN cyanobacteria index

Status: characterized on 2026-09-22. Dry runs and the route comparison are measured. The pull awaits authorization. Step 1 of [the work plan](../../docs/work-plan.md). Read [METADATA.md](METADATA.md) first.

What it is: the NASA-produced `CI_cyano` Level-3 mapped product for the EPA Cyanobacteria Assessment Network. The Ocean Biology DAAC distributes it as 8-bit GeoTIFF tiles and whole-region mosaics at 300 m in EPSG:5070. Composites are daily and 7-day maximum.
[METADATA.md](METADATA.md) holds the characterization. Its 100 claims from 17 primary sources each carry a verbatim quote confirmed by a checking agent. Section 12 lists the open items.

## Run guide

Every command below contacts a provider and runs only when the owner invokes it. Downloads need `OB_DAAC_EDL_TOKEN` in `.env`.

```sh
# Plan without credentials. Contacts only the search endpoint.
uv run python datasets/cyan/access/pull_cyan.py --period weekly --tiles all --sdate 2016-01-01 --edate 2026-09-22 --dry-run
uv run python datasets/cyan/access/pull_cyan.py --period daily --tiles all --sdate 2026-07-28 --edate 2026-09-22 --dry-run

# Compare the cloud route with the archive. HEADs every listed file, downloads two samples twice.
uv run python datasets/cyan/access/compare_routes.py --sdate 2016-01-01 --edate 2026-09-22 --sample 2

# Pull, after authorization. Cached and manifested. --limit N for a sample.
uv run python datasets/cyan/access/pull_cyan.py --period weekly --tiles all --sdate 2016-01-01 --edate 2026-09-22
```

Files land under `data/cyan/raw/<period>_<region>_<scope>/` with `manifest.jsonl`. Evidence from the scripts lands under [outputs/](outputs/README.md).

## Plan for this folder

- Step 1a wrote `METADATA.md` with a research agent and a checking agent. Done 2026-09-22.
- Step 1b ported `cyan_api.py` and `pull_cyan.py` into `access/` with tests and added `compare_routes.py`. Part 1 done 2026-09-22. Part 2, the pull, awaits authorization.
- Step 1c ports `qa_cyan.py` into `qaqc/`.
- Step 1d builds the review dashboard data under `viz/`.
- Local scope is assumption A8: weekly whole-region mosaics from 2016 plus 8 weeks of dailies.

## Prior code to port

From the owner's HAB_PoC repository, `data-sources/cyan/`. `access/cyan_api.py` holds the encoding constants, filename parser, stream preference, and file search. `access/pull_cyan.py` holds the enumerate-plan-download flow. `qaqc/qa_cyan.py` and `viz/viz_cyan.py` follow. Its `METADATA.md` is input, not evidence.
