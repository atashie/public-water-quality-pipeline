# epa_cyanohab_forecast: EPA experimental cyanoHAB forecast

Status: planned. Step 2 of [the work plan](../../docs/work-plan.md). No snapshot taken.

What it is: a weekly probability, per satellite-resolvable lake, that the lake exceeds a bloom threshold in the coming week. The EPA Office of Research and Development publishes it inside three Qlik dashboards. There is no official API. The access path is unofficial, assumption A12.
Facts checked on 2026-09-22 are in the [probe record](../../docs/probes/2026-09-22-dataset-facts.md#epa-cyanohab-forecast). They are not yet `documented`.

## Plan for this folder

- Step 2a writes `METADATA.md` with a research agent and a checking agent. Its sources are the EPA pages, the 2024 method paper, the 2025 evaluation, and the official code deposit.
- Step 2b ports the HAB_PoC repository's Qlik engine client and snapshot script into `access/` with the offline fixture tests. It takes one snapshot after the owner authorizes it. Weekly snapshots start once verified, assumption A7.
- The dashboards keep about two seasons. Snapshots are append-only. A changed past value is a revision, never an overwrite.

## Prior code to port

From the owner's HAB_PoC repository, `data-sources/cyano-forecasts/`: `access/qlik_public.py`, `access/pull_forecasts.py`, `access/pull_official.py`, `qaqc/qa_forecasts.py`, `viz/viz_forecasts.py`, and `tests/test_qlik_public.py` with its fixture. Its `METADATA.md` is input, not evidence.
