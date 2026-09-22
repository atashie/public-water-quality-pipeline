# <Dataset name>: metadata

Short name: `<id>`. Product: <specific product and variables>. Version documented: <version and date>.
Compiled: <YYYY-MM-DD>. Access date for every check below: <YYYY-MM-DD>. Compiled by: <role>, with a research agent and a checking agent.
Every fact carries `documented`, `measured`, `probe`, or `unverified`. A `documented` fact has a verbatim quote, the page, and the access date. Ambiguities are flagged, not smoothed over.

## 0. Summary for the modeler

| Question | Answer | Status |
|---|---|---|
| What is it? | | |
| Native form and format | | |
| Spatial resolution and extent | | |
| Temporal span, cadence, gaps | | |
| The value in a cell or record | | |
| Encoding and how to read a value | | |
| Nodata, fill, detection limit | | |
| Access: search, download, authentication | | |
| Full-archive size and the subset decision, assumption A16 | | |
| Likely role: target, feature, mask, context | | |

## 1. What it is
<producer, algorithm lineage, maturity and validation status>

## 2. Temporal coverage, cadence, and gaps
<sources by period and cadence, refresh latency stated and observed, reprocessing and version history, known gaps>

## 3. Spatial characteristics
<resolution verified from a file, projection, grid or tiling, extent, minimum reliable unit>

## 4. Encoding and quality flags, exact values
<value scheme and units, nodata and fill, detection limits, every flag and its meaning, look-alike products with other encodings>

## 5. Known issues and limitations, from the producer
<the producer's own caveats, verbatim, and the biases that matter for use>

## 6. Bulk or subset
<order-of-magnitude size of the full archive, the chosen scope, and the justification under assumption A16>

## 7. Access, verified <date>
### 7.1 Search or enumerate
### 7.2 Download and authentication. Credentials live in `.env`
### 7.3 Alternative access, documented and secondary
### 7.4 Ancillary files, grids, shapefiles, DOIs

## 8. Sources, all accessed <date>
1. <primary source>, URL. Local copy: `reference/<file>`.

## 9. Role in this project
<target, feature, mask, or context. What it is not. Leakage and circularity warnings>

## 10. Reproducibility and version pinning
<how the version is read from the data, default stream or selection, cache and manifest, access dates>

## 11. License and attribution
<license, required citation text verbatim, redistribution terms>
