# The EPA forecast code deposit read for its bloom recipe, 2026-09-23

Probe by the parent agent, Claude Code, directed by the repository owner, during the preparation of step 1f. One public archive downloaded and read. No dashboard or data endpoint contacted. The reading is the parent agent's and is not independently checked. Step 2a's checking agent confirms or corrects it.

## The deposit

- `https://pasteur.epa.gov/uploads/10.23719/1529140/INLA_CONUS_forecast.zip`, resolved from DOI `10.23719/1529140`, returned 33,677 bytes, sha256 `126f7f3fd9f79bdb36083009f726ecbe2d9047b728b7ac95bb2498545cf84afb`. Preserved under `datasets/epa_cyanohab_forecast/reference/` with its extraction. `probe`
- Contents: twelve R scripts and a README, every file dated 2023-06-13 in the archive. No input data. The README says the repository "contains all code used in the INLA cyanobacteria study" and that input files are excluded for size. `probe`

| File | sha256 |
|---|---|
| `README.md` | `ef3a97ca414de68c9e6e7fae81558dc355512950260d86d1cb89cf2a606bf81f` |
| `cyan_processing_conus.R` | `4634000c0c0d503b6611c0ba32dee8b731e181ea1f40159ebfc93854cdf0ff30` |
| `parallel.step1plus2.R` | `82feaed2d70de9bdcc7ec2bdbc90cb5a913ca67d39ab4d2db14220d073082326` |
| `cyanoCONUS_ice_step3_adjusted.R` | `4c8dfbc426c1debd70c2c86d9f75788d54968c675420ae6c3f6b3f2c3820d2c0` |
| `cyanoCONUS_ice_step4_adjusted.R` | `1cc50ddbc7c7813922fa0ac55709d8d4798e8b23b64517d7fe3f95bb111d457a` |
| `compile_data.R` | `ffca3aac12b751e39b429a7b71b18c2e1573f67def40406234e942790d0a1288` |
| `conus_inla.R` | `f2556e46c979845c7003815c731e930ed4515304b0307a970dc9f4c12d437a08` |
| `generate_ice_tibble.R` | `d08260498c6e879419bcbc31f85490ed63803dec6789e65e8c716ef9804f71e1` |
| `generate_week_assignments_tibble.R` | `876c772bc3433c8d3fa6c51b3f957119b407384d1ecd9d7843a07b3cdaf5b1ea` |
| `lake_morpho_code.R` | `59d6ccc6195786db143286fa1579fe0d6fa0698b536a03f1ebaea15655a48657` |
| `prism_download.R` | `f1773957bdf4c434f578faaae7868b839a4e99a1da55a34067bf04219c1ccd86` |
| `prism_processing_conus.R` | `f73eba43da133e8329eae9d8c7ccfb8d1ceb16b9a344abe4ced2bac1f6babf60` |

## What the code does with the CyAN pixels

Line numbers are in the extracted files.

- `cyan_processing_conus.R` lines 105 to 108: `exact_extract(ci_brick,lake)[[1]] %>% filter(coverage_fraction == 1) %>% dplyr::select(-coverage_fraction) %>% apply(MARGIN = 2,FUN = metrics)`. Only pixels wholly inside the lake polygon enter the statistics. `probe`
- Lines 91 to 95: the metrics are `mean(x,na.rm = T)`, `median(x,na.rm = T)`, and `sd(x, na.rm = T)`. Missing pixels are dropped, not counted. `probe`
- Line 170: `bloom = ifelse(median>=130,T,F)) %>% # 97 for 3 ug/L, 130 for 12 ug/L, 151 for 24 ug/L - subbing u for mu, so ug = micrograms`. The bloom flag is a weekly lake median of 130 or more. The comment names the code-to-chlorophyll equivalents the authors used. `probe`
- `compile_data.R` line 32, comment: "we're actually using the median, not the mean. Both are recorded in the csv." Line 75 maps `Cyano = median`. `probe`
- `cyanoCONUS_ice_step4_adjusted.R` line 107: `data<-reclassify(data,c(253,Inf,NA))`. Under the `raster` package's default of right-closed intervals, codes above 253 become missing and 253 stays. So land, 254, and no data, 255, are dropped and code 0 stays as a measurement of zero. The reading of the package default is the parent agent's and is not checked here. `probe`

## What the code does that decision 0002 does not

- `parallel.step1plus2.R` lines 54 to 60 and 86: every weekly image is multiplied by a raster named `invalidMixed.tif`, and negative products become missing. The mask is not in the deposit. Its content is unknown. The name suggests mixed land and water pixels. `probe`
- `cyanoCONUS_ice_step3_adjusted.R` and `step4`: weekly ice masks are built from shapefiles and applied to the images. The ice inputs are not in the deposit. `probe`
- `compile_data.R` line 63: `mutate(bloom = ifelse(is.na(bloom) & masked == T, F, bloom))`. A missing weekly flag under ice becomes no bloom before training. `probe`
- `generate_week_assignments_tibble.R`: weeks are numbered from the first Sunday of each year to match the CyAN week numbers. This repository keys rows by file start date and needs no week number. `probe`

## What this changes in this repository

- The 130 threshold and the whole-pixel rule were `prior`, from the HAB_PoC repository's replication of the paper. They are now read from the official code and cited as `probe`. They become `documented` when step 2a's checking agent confirms the quotes.
- Decision 0002 stands. Its interior rule, 99.9 percent coverage from an oversampled rasterization, is a stand-in for `coverage_fraction == 1` and for the unknown mixed-pixel mask, and is not the same mask. The dashboard of step 1f states the differences.
- The 130 line on the dashboard is labelled as the EPA code's operationalization and is movable. It is not a claim about any lake.
