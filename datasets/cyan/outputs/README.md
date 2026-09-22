# CyAN outputs

Evidence written by scripts under `../access/` and, later, `../qaqc/`. Never edit a file here by hand. Rerun the script that wrote it. [docs/measurements.md](../../../docs/measurements.md) interprets these files.

| File | Written by | What it holds |
|---|---|---|
| `plan-weekly-mosaic-2026-09-22.json` | `pull_cyan.py --dry-run` | The weekly whole-region plan: counts, streams, first and last file, search time |
| `plan-daily-mosaic-2026-09-22.json` | `pull_cyan.py --dry-run` | The daily whole-region plan for the last 8 weeks |
| `route-comparison-2026-09-22.json` | `compare_routes.py` | Presence of every listed weekly file on the cloud endpoint, the catalog count, the credentials and listing test, and two byte comparisons |
