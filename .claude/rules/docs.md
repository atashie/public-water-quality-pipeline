---
paths:
  - "docs/**"
  - "README.md"
  - "CLAUDE.md"
  - "AGENTS.md"
  - "datasets/**/*.md"
---

# Rules for documents

- Every claim about a data source, service, or tool carries `documented`, `measured`, `probe`, or `unverified`. Every planning assumption is a row in `docs/assumptions.md` with `sourced` or `unsourced`.
- `documented` needs a primary page, a verbatim quote, an access date, and a check by a second agent. `probe` is a live check the parent agent ran and recorded under `docs/probes/`. `measured` cites a result file written by a checked-in script.
- One fact has one home. Link to it. If you find a copy, remove the copy. Numbers live in the probe record, the result file, or the dataset METADATA, never in `CLAUDE.md`.
- Refer to colleagues by role. Never write a person's name. Do not name customers or vendors of the owner's employer.
- Dates are ISO 8601 with no relative dates. Dated documents put the date in the first heading.
- Plain English and American spelling. Descriptive sentences: 25 words maximum. Procedure steps: imperative, 20 words maximum. No semicolons. No "should". Quoted source text stays verbatim.
- Use relative links for repository files. External primary-source citations use HTTPS links. `tests/test_docs.py` checks that every relative link resolves.
- Decisions go in `docs/decisions/NNNN-<slug>.md` and the index. Reviews go in `docs/reviews/YYYY-MM-DD-<slug>.md` and the index. Probe records go in `docs/probes/YYYY-MM-DD-<slug>.md` and the index.
- AI-generated research, including prior repositories' METADATA files, is input, not evidence. Its claims stay `unverified` here until rechecked against a primary page.
- Credentials never appear in a document. Not even a masked one.
