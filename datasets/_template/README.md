# _template: copy-me skeleton for a new dataset

1. Create `../<name>/` with `reference/`, `access/`, `qaqc/`, `viz/`, `outputs/`, and `tests/`.
2. Copy `METADATA.template.md` to `../<name>/METADATA.md`. Fill every section from primary pages with quotes and access dates.
3. Write the access, QA, and dashboard-builder scripts. Reuse `../_common/net.py` for sessions, credentials, and manifested downloads.
4. Add offline tests on fixtures under `../<name>/tests/`.
5. Add the row to [../../docs/data-registry.md](../../docs/data-registry.md). Record decisions. Write the review record.

Keep raw and derived data out of git. Track the documents, code, QA report and JSON, and small proofs.
