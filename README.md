# Open water-quality data pipeline

**CyAN is characterized, pulled, checked, derived per lake, and served on a lake dashboard as of 2026-09-23. The dashboard is prepared for Vercel hosting. The AWS note, step 1g, is next.**

This repository ingests, checks, processes, and serves open water-quality data for lakes and reservoirs.
The first three datasets derive from or train on Sentinel-3 OLCI at 300 m:

| Dataset | Producer | What it gives us |
|---|---|---|
| CyAN cyanobacteria index (`CI_cyano`) | NASA Ocean Biology DAAC for the EPA CyAN program | Daily and weekly rasters of a cyanobacteria index over the contiguous United States and Alaska, 2016 onward |
| Lake Water Quality 300 m, version 2 | Copernicus Land Monitoring Service | Ten-day global composites of turbidity, chlorophyll-a, suspended matter, trophic state, a cyanobacteria index, reflectances, and flags for more than 4,000 lakes, 2024-09 onward, with a version 1 archive from 2002 |
| Experimental cyanoHAB forecast | US EPA Office of Research and Development | Weekly bloom probability for about 2,200 satellite-resolvable lakes, April to November |

The work serves two purposes. In the short term, each dataset that fits locally is pulled in full, checked, reviewed on a
generated dashboard, and served through a user-facing dashboard specified per case. In the long term, each dataset gets a
high-level AWS design for regular updates with storage and compute costs, written for the engineering team.
[docs/assumptions.md](docs/assumptions.md) records the scope. [Decision 0001](docs/decisions/0001-scope-conventions-and-dataset-order.md) records the choices.

Validation of facts comes first. Every claim carries a status. Every new dataset is reviewed by the owner on a dashboard
before it is used. Nothing is committed without the owner's authorization.

## Quick start

Python 3.12.13 and `uv.lock` pin the environment.

```sh
uv sync --locked
uv run pytest
```

The tests check documentation links, dated headings, and the shared download helper on fixtures. They contact nothing.
Provider pulls need credentials in `.env`. Copy `.env.example` and fill it in. Git ignores `.env`.

## Documents

| Read | For |
|---|---|
| [docs/work-plan.md](docs/work-plan.md) | The ordered steps, what is done, and what is open |
| [docs/assumptions.md](docs/assumptions.md) | Planning assumptions and where each came from |
| [docs/decisions/](docs/decisions/README.md) | Why something was decided |
| [docs/data-registry.md](docs/data-registry.md) | One row per dataset with its status |
| [docs/probes/](docs/probes/README.md) | Dated records of live checks against providers |
| [docs/measurements.md](docs/measurements.md) | What checked-in scripts measured, with the result file behind each number |
| [docs/reviews/](docs/reviews/README.md) | Dated review records, newest first |
| [docs/aws/](docs/aws/README.md) | What each dataset's AWS note will contain |
| [datasets/README.md](datasets/README.md) | The eight-step loop each dataset follows, and the folder layout |
| [CLAUDE.md](CLAUDE.md) | Conventions, workflow, and gotchas for AI coding agents. [AGENTS.md](AGENTS.md) points Codex here |

Code is MIT licensed. Upstream data keep their own licenses and attribution requirements.
This repository claims no production deployment.
