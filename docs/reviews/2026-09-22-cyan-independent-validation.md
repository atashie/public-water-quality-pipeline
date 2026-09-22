# Independent validation of CyAN route measurements, 2026-09-22

Reviewer: Codex, with three independent `gpt-5.6-luna` subagents requested by the owner.
Assignments covered saved evidence, NASA primary sources, and measurement methods.

Scope: review [step 1b part 1](2026-09-22-cyan-route-comparison-and-dry-run.md) and [measurements](../measurements.md).
Acceptance checks: recompute material counts, check claim boundaries, consult NASA documentation, and run the repository check workflow.
The pull, implementation fixes, commit, and publication remain deferred.

## Findings requiring follow-up

### 1. Unexpected HTML becomes a successful empty search

Priority: high. Status: open, reproduced offline.

In [cyan_api.py](../../datasets/cyan/access/cyan_api.py), `parse_search_body` accepts any HTTP 200 body containing `<html` as an empty listing.
The parent reproduced this with `<html><body>Service temporarily unavailable</body></html>`.
The result was `[]`, allowing a provider failure to masquerade as an empty archive or successful zero-file pull.
Reject unexpected HTML and accept only explicit empty-result responses.
The saved nonempty listings do not demonstrate this failure occurred during the recorded measurements.

### 2. Identity and absence claims exceed the observations

Priority: medium. Status: open, evidence interpretation corrected here.

[Measurement 1](../measurements.md) calls the cloud copy byte-identical wherever present.
The comparison establishes byte identity only for its two samples.
The samples are the newest available pair, not a historical or randomized sample.
Matching date windows between `CYAN` and `CYANV6T` establish overlapping coverage, not interchangeable bytes or processing versions.
Replace “No data lost” with a statement about retained date coverage in the selected stream.

The endpoint's recorded 404s establish unavailable HTTPS paths at the observation time.
They do not enumerate S3 contents.
Likewise, measurement 2 establishes an absent search result, not physical absence from the archive.
Use endpoint-specific and listing-specific wording consistently in titles, findings, METADATA, and the AWS note.

### 3. The saved plans cannot reproduce the exact approved selection

Priority: medium. Status: open, code inspection.

[pull_cyan.py](../../datasets/cyan/access/pull_cyan.py) removes `files` before writing its plan JSON.
The daily artifact preserves counts and endpoints, but no individual filenames or URLs.
Its full date coverage cannot be independently recomputed from that artifact.
Execution repeats the live search without consuming an approved plan or detecting selection changes.
Preserve the complete selection and detect drift before a later pull.

The route comparison records `code_version: 9838942`.
That revision contains none of the access scripts used for the measurement.
Record the working-tree state and source hashes when measuring uncommitted code.
The current artifact identifies the base revision, not the executed implementation.

### 4. Recorded latency is age at access

Priority: medium. Status: open, reproduced offline.

In [pull_cyan.py](../../datasets/cyan/access/pull_cyan.py), `latency_days` subtracts the composite end date from the local access date.
For a historical composite ending 2016-04-30, access on 2026-09-22 produces 3,797 days.
That measures age at retrieval, not the provider's publication delay.
Name and document the field accordingly.
Provider latency remains `unverified` without first-availability observations or provider publication timestamps.

## Primary-source validation

The direct-S3 regional restriction is `documented` by NASA's [OB.DAAC staff response](https://forum.earthdata.nasa.gov/viewtopic.php?t=7701).
Accessed 2026-09-22, independently opened by the source-checking agent and parent.

> If the code is used from an IP that is outside of the AWS-specified IPs for us-west-2, those errors will be seen.

The recorded `AccessDenied` is consistent with that restriction, but does not independently diagnose its cause.
The measurement supports HTTPS access from the tested off-region laptop, not guaranteed access from every location or account.
The source checker also consulted NASA's [download guide](https://www.earthdata.nasa.gov/learn/tutorials/search-download-methods-data-archived-ob-daac).
The credentials README and collection record could not be rendered by the browser tool.

## Verification and limits

The evidence agent independently decoded every weekly filename using standard-library calendar arithmetic.
It confirmed the counts, date-window collapse, lag, older endpoint gaps, and missing archive-listing week in [measurements](../measurements.md).
The corrected expected series through the cloud cutoff contains 536 weekly starts, not 537. `measured`

The parent independently hashed the four existing local sample payloads with SHA-256.
Every hash and byte count matched the [comparison artifact](../../datasets/cyan/outputs/route-comparison-2026-09-22.json). `measured`
The evidence agent initially missed these ignored files. Explicit filesystem enumeration resolved that review error.

The daily count agrees with the reported calendar span.
Individual daily filenames remain unavailable in its summary artifact.
The size arithmetic is reasonable, but full-scope size remains `unverified`, as measurement 3 already states.
No fresh provider measurement was run, so this review validates saved observations rather than current availability.

Repository check workflow passed in its required order:

- `uv sync --locked`: passed.
- `uv run ruff check .`: passed.
- `uv run ruff format --check .`: passed.
- `uv run pytest -q`: 76 passed in 0.17 seconds.

Existing implementation changes and result files were preserved.
This follow-up adds only this review and its index entry.
No provider scripts, new dataset downloads, or credential reads were performed during this review.

## Dispositions and proposed next step

The previous review's sample identities remain supported within their stated sample scope.
Broader identity and physical-absence claims are corrected with evidence in finding 2.
The earlier correction of the expected weekly count is independently confirmed.
Implementation findings remain open for the implementer.

Next: address these findings and return the corrected step 1b part 1 for owner review.
This validation does not authorize the pull or advance the dataset workflow.
