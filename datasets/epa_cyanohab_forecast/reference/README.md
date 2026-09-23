# EPA cyanoHAB forecast reference documents

Preserved primary documents for the EPA forecast characterization, with their provenance. Step 2a writes the research and check records here.

| File | What | Provenance |
|---|---|---|
| `INLA_CONUS_forecast.zip` | The EPA Office of Research and Development code deposit for the INLA cyanobacteria forecast, DOI 10.23719/1529140. Twelve R scripts and a README. No input data | Downloaded 2026-09-23 by the parent agent. 33,677 bytes. sha256 `126f7f3fd9f79bdb36083009f726ecbe2d9047b728b7ac95bb2498545cf84afb`. [Probe record](../../../docs/probes/2026-09-23-epa-forecast-code-deposit.md) |
| `INLA_CONUS_forecast/INLA_CONUS_forecast/*.R`, `README.md` | The zip extracted as delivered. Every file is dated 2023-06-13 inside the archive | Extracted 2026-09-23. Per-file sha256 in the probe record |

The deposit is the primary source for the forecast's operationalization of a bloom: a weekly lake median of the CyAN code at or above 130 over pixels wholly inside the lake polygon. Decision 0002 in this repository was written before the deposit was read and matches it where the two overlap. The probe record lists the differences.
