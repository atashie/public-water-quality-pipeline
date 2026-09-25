---
paths:
  - "datasets/**"
---

# Rules for dataset folders

- Each dataset folder holds `README.md`, `METADATA.md`, `reference/`, `access/`, `qaqc/`, `viz/`, `outputs/`, and `tests/`. Raw and derived data live under the repository's ignored `data/<dataset>/`.
- Scripts that contact a provider run only when the owner invokes them. Every such script has `--dry-run`, which contacts nothing beyond a catalog listing, and `--limit`.
- Never edit `data/` or a manifest by hand. Rerun the script that wrote it.
- Every download records the URL, bytes, sha256, and access time in UTC. It records the provider's version tag read from the file itself, never from the filename alone.
- Credentials come from `.env` through `datasets/_common/net.py`. Never print, log, or echo them.
- No spatial or temporal aggregation without a recorded owner authorization, assumption A17. A17 also sets the terms for diagnostic measurements that pool counts. Work at native resolution and the provider's own composites. When something is too heavy, reduce scope, not resolution.
- Keep measured absence distinct from missing. Never fold a below-detection code into no-data.
- When a script excludes files or records, log the counts kept and dropped and say why.
- Never add the PyPI package named `datasets`. It shadows this repository's `datasets` package.
- QA writes `outputs/qa-<dir>-<stamp>.json` and `outputs/qa-report-<stamp>.md`, stamped with the run's UTC time. A rerun never overwrites an earlier result. The review dashboard is one HTML page with vendored libraries that opens from disk and makes no external request.
- Tests under `datasets/<name>/tests/` and `tests/` contact nothing. Use fixtures.
