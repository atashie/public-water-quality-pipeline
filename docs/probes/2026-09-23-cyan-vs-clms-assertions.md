# Six assertions contrasting EPA CyAN and Copernicus Lake Water Quality, checked against primary sources, 2026-09-23

The owner asked on 2026-09-23 for a check of six assertions that contrast the two Sentinel-3 OLCI water-quality products. A research agent, Claude Code, fetched the sources and drafted the quotes. The parent agent then re-fetched the five main sources and confirmed every quote drawn from them, marked `checked` below. Quotes marked `agent` come from the research agent alone and are not yet confirmed. Every quote is verbatim. Access date for every URL: 2026-09-23. A second-model check by Codex is the next step before any of this enters a dataset METADATA as `documented`.

## Summary

| Assertion | Verdict |
|---|---|
| A1. CyAN targets cyanobacteria, reports a Cyanobacteria Index, converts it to cells per millilitre | Confirmed. The files carry the index. The cell density is a downstream conversion by a factor of 10^8, "Microcystis-equivalent" |
| A2. The algorithm reads the spectral shape around 665 and 681 nm, responding to chlorophyll fluorescence and absorption, and uses a phycocyanin feature to separate cyanobacteria | Confirmed, with one omission. The shape is centered at 681 nm with 665 and 709 nm as the reference bands. The cyanobacteria test is a second shape at 620, 665, and 681 nm keyed to phycocyanin absorption at 620 nm |
| A3. A harmful-bloom indicator, not a general algae measure | Partly right. The delivered product is cyanobacteria-specific. "Harmful" is an inference: it measures cyanobacterial biomass, not toxins, and the archive also carries a non-cyanobacteria index |
| A4. Copernicus LWQ measures trophic state and clarity: a trophic state index from chlorophyll-a, turbidity, and in some versions reflectance | Partly right. Reflectance is in every version. Version 2 adds chlorophyll-a, total suspended matter, and a floating cyanobacteria index, so the assertion understates version 2 |
| A5. Chlorophyll-a counts all phytoplankton and does not separate cyanobacteria | Right for chlorophyll-a as a variable. Wrong as a statement about the product: version 2 carries `floating_cyanobacteria`, a 0 to 1 probability of a surface bloom from a Maximum Peak Height test, since 2024-09 |
| A6. Lakes_cci covers chlorophyll-a, turbidity, reflectance, surface temperature, ice cover, and water extent, with no cyanobacteria-specific index | Partly right and version-dependent. It also covers water level and ice thickness. Version 3.0.0 of 2025-12 replaces turbidity with suspended matter and adds a prototype phycocyanin concentration, a cyanobacteria pigment, as a concentration rather than an index |

## A1. CyAN targets cyanobacteria and converts the index to cells per millilitre

- "satellite remote sensing products using the cyanobacteria index (CI) algorithm to estimate cyanobacteria concentrations (CI_cyano) in lakes across the contiguous United States and Alaska (CONUS)". NASA Earthdata CyAN project page, `https://www.earthdata.nasa.gov/data/projects/cyan`. `checked`
- "To convert Digital Number (DN) to CI_cyano: CIcyano=10^(DN∗0.011714−4.1870866) That range is ~10,000 to 7,000,000 cells/ml." Same page. `checked`
- "CI-cyano can be converted to Microcystis-equivalent cells by multiplying by the factor 10 8 (cells mL −1 ) 11 , 15 , 41 , to provide a more intuitive biomass metric." Mishra, S. et al. (2019), Measurement of cyanobacterial bloom magnitude using satellite remote sensing, Scientific Reports 9, 18310, doi:10.1038/s41598-019-54453-y, Methods, full text from Europe PMC, `https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6892802/fullTextXML`. `checked`. Preserved as `datasets/cyan/reference/mishra-2019-europepmc-PMC6892802.xml`.
- "Results indicated that MERIS provided robust estimates for Low (10,000–109,000 cells/mL) and Very High (>1,000,000 cells/mL) cell enumeration ranges". Lunetta, R. S. et al. (2015), Evaluation of cyanobacteria cell count detection derived from MERIS imagery across the eastern USA, Remote Sensing of Environment 157, 24 to 34, doi:10.1016/j.rse.2014.06.008, abstract as shown on EPA Science Inventory record 304530, `https://cfpub.epa.gov/si/si_public_record_report.cfm?Lab=NERL&dirEntryId=304530`. `checked`
- "The data the Cyan system reports are cyanobacteria concentrations. The data products as delivered by USGS/NASA are CI_cyano and include chlorophyll-a and phycocyanin in the response of the OLCI satellite sensors". EPA, CyANWeb Website User's Guide, EPA/600/B-21/072, 2021-04, page 22. `agent`
- The files themselves carry the index as an 8-bit code with units of inverse steradians, `CI_cyano:sr^-1`, [release notes](../../datasets/cyan/reference/README.md) page 23. The cell density is a conversion made downstream, not a value in the files.

## A2. Spectral shape, fluorescence and absorption, and the phycocyanin feature

- "Cyanobacteria Index (CI) is calculated by centering the spectral shape at 681 nm and changing the sign of SS, or CI = −SS (681). The CI evaluates Chl- a absorption at 681 nm. At 681 nm, chlorophyll in eukaryotes typically fluoresces strongly, leading to increased apparent reflectance that obscures chlorophyll absorption." Mishra et al. 2019, Methods. `checked`
- "In cyanobacteria, however, chlorophyll fluorescence is much weaker, such that Chl-a absorption dominates the radiance signal from the water at 681 nm, causing the reflectance at 681 nm to decrease relative to 665 and 709 nm." Same. `agent`, the sentence sits next to the checked ones.
- "For more specific identification of cyanobacteria, a SS using 620, 665, and 681 nm was used to identify the presence of PC, a characteristic pigment in this taxonomic division". Same. `checked`
- "Inclusion of 620 nm, which is the absorption peak of PC, a characteristic photopigment in cyanobacteria, reduces the false detection issue." Same. `checked`
- "The CI product, when SS (665) is negative, is termed as CI- cyano and was used to estimate cyanobacteria biomass in this research." Same. `checked`
- "narrow spectral bands ... optimally oriented at phytoplankton pigment absorption features including phycocyanin at 620 nm." Lunetta et al. 2015, EPA record 304530. `checked`
- "A change in the spectral shape at 681 nm is used to distinguish blooms of cyanobacteria from blooms of other phytoplankton via MERIS satellite sensor imagery." Wynne, T. T. et al. (2008), Relating spectral shape to cyanobacterial blooms in the Laurentian Great Lakes, International Journal of Remote Sensing 29(12), 3665 to 3672, doi:10.1080/01431160802007640, abstract as indexed by OpenAlex. The publisher page returned HTTP 403. `agent`
- "minor adjustments to the 681 nm and 709 nm wavelengths". Release notes, page 8, version 6 changes. `checked`

What the assertion gets slightly wrong: the index is a three-band shape at 665, 681, and 709 nm, so "around 665 and 681" leaves out 709 nm. The cyanobacteria separation is a second three-band shape at 620, 665, and 681 nm.

## A3. A harmful-bloom indicator, not a general algae measure

- "providing a capability of detecting and quantifying cyanobacteria algal blooms." NASA Earthdata CyAN page. `checked`
- "In the case of cyanobacteria, SS (665) turns negative due to lower reflectance at 620 nm band and is used as an exclusion criterion to select only cyanobacteria." Mishra et al. 2019, Methods. `checked`
- The level-3 binned files list companions to the delivered product: `:units = "CI_stumpf:sr^-1,CI_cyano:sr^-1,CI_noncyano:sr^-1,MCI_stumpf:sr^-1,chl_mph:mg m^-3"`. Release notes, page 23. `checked`
- "Ice can potentially register as high CI counts" and "Undetected thin clouds can potentially register as high CI counts". Release notes, page 18, known issues. `agent`

What to keep in mind: the delivered `CI_cyano` is cyanobacteria-specific, so "not a general algae measure" holds. "Harmful" is an inference. The index measures near-surface cyanobacterial biomass, not toxin. The OBPG archive keeps a `CI_noncyano` companion, so the raw index without the 620 nm test responds to any chlorophyll absorption.

## A4. Copernicus Lake Water Quality: trophic state, clarity, and reflectance

- "Version 2 of the product contains six (sets of) variables: lake water-leaving reflectance (all wavebands describing water properties, after atmospheric correction), turbidity, total suspended matter concentration, chlorophyll-a concentration, a floating cyanobacteria index and a trophic state index (derived from phytoplankton biomass by proxy of chlorophyll-a)." Copernicus Land Monitoring Service, Product User Manual, Lake Waters 300M Product, Version 2.1.0, Issue I1.01, 2025-10-23, marked "draft – pending review", section 1.1, `https://land.copernicus.eu/en/technical-library/product-user-manual-lake-water-quality-300m-version-2.1/@@download/file`. `checked`. Preserved as `datasets/clms_lwq/reference/CLMS_LWQ300_PUM_v2.1.0_I1.01_2025-10-23.pdf`.
- "The 100m products contain three (sets) of parameters: lake water reflectance (all wavebands that are available after atmospheric correction), turbidity (derived directly or from suspended solids concentration estimates) and a trophic state index (derived from phytoplankton biomass by proxy of chlorophyll-a)." CLMS Product User Manual, Lake Waters 100M Product, Version 1.2.0, Issue I1.03, 2022-03-30, section 1.1. `agent`
- "They consist of three water quality parameters: (i) the turbidity of a lake ... (ii) the trophic state index that is an indicator of the productivity of a lake in terms of phytoplankton ... and (iii) the lake surface reflectances". CLMS product page for the 300 m version 2 product, `https://land.copernicus.eu/api/en/products/water-bodies/lake-water-quality-near-real-time-v2-0-300m`, whose description text still describes the version 1 variables. `agent`

What the assertion gets wrong: reflectance is in every version, not "some versions". Version 2 adds chlorophyll-a, suspended matter, and a cyanobacteria variable.

## A5. Chlorophyll-a and cyanobacteria in the Copernicus product

- "New variables added in v2 include Total Suspended Matter (TSM) concentration, chlorophyll-a concentration and a floating cyanobacteria index, and are in demonstration mode pending further review." CLMS PUM v2.1.0, section 1.2. `checked`
- "floating_cyanobacteria float Floating cyanobacteria index, with a range of values from 0 to 1 indicating probability of cyanobacteria presence – the closer the value is to 1, the higher the probability". CLMS PUM v2.1.0, variable table. `checked`
- "Detection of surface blooms by applying the Maximum Peak Height (MPH) algorithm (Mathews and Odermatt 2015) adapted to use top-of-atmosphere (TOA) reflectance instead of Bottom-of-Rayleigh reflectance (BRR)." CLMS PUM v2.1.0, section 3. `checked`
- "Chlorophyll-a concentration, derived from LWLR, as a proxy for phytoplankton (algae and cyanobacteria) biomass." ESA Lakes_cci Product User Guide, Issue 3.0.0, 2025-12-09, section 1.2. `agent`
- "the NRT dekadal Lake Water Quality (LWQ) v2.0 products have been launched as of September 2024" with "a floating cyanobacteria risk index and, in the case of the 300 m product, per-pixel uncertainty estimates for chlorophyll-a and TSM". CLMS news item of 2024-10-28, `https://land.copernicus.eu/en/news/lake-water-quality-global-products-version-2-release`. `agent`

What the assertion gets wrong: chlorophyll-a itself does not separate cyanobacteria, which is right, but the version 2 product carries a separate cyanobacteria variable. It is a surface-scum probability from a spectral peak test, in demonstration mode, not a biomass. This confirms the repository's earlier probe that version 2 adds chlorophyll-a, suspended matter, a cyanobacteria variable, and uncertainties from 2024-09.

## A6. Lakes_cci variables

- "The Lakes ECV covers: Lake Water Level, Lake Water Extent, Lake Surface Water temperature, Lake Ice Cover, Lake Ice Thickness and Lake Water-Leaving Reflectance." Lakes_cci Product User Guide, Issue 2.1.1, 2024-04-04, section 1.1, `https://climate.esa.int/media/documents/CCI-LAKES2-0021-PUG-v2.1.1.pdf`. `agent`. The words "cyanobacteria" and "phycocyanin" do not occur in that issue, per the research agent.
- "In addition to LWLR the CDRP V3.0 includes estimates of chlorophyll-a (mg m-3) and TSM (g m-3), aCDOM(440) (m-1), the vertical diffuse attenuation coefficient Kd (m-1), and phycocyanin (mg m-3) which are derived from the LWLR." Lakes_cci Product User Guide, Issue 3.0.0, 2025-12-09, section 3.6.2, `https://climate.esa.int/media/documents/Lakes_cci_PUG-v3.00_ST.pdf`. `checked`. Preserved as `datasets/clms_lwq/reference/Lakes_cci_PUG_v3.0.0_2025-12-09.pdf`.
- "The phycocyanin product may be considered a prototype CCI product, included for convenience to assist researchers with initial analysis of global trends in phytoplankton composition." Same. `checked`
- "In CRDP versions prior to v3.0.0, this product was expressed as Turbidity." Same, section 1.2, on the suspended matter product. `checked`
- Version 3.0 was published on 2026-03-18 at the Centre for Environmental Data Analysis, per the Lakes_cci data page `https://climate.esa.int/en/projects/lakes/data/`. `agent`

What the assertion gets wrong: it leaves out water level and ice thickness, "turbidity" became suspended matter in version 3.0.0, and version 3.0.0 adds a prototype phycocyanin concentration. "No cyanobacteria-specific index" is true for version 2.x and outdated for 3.0.0, with the caveat that a pigment concentration is not an index.

## Sources that did not load

The research agent reports HTTP 403 from the publisher pages of Wynne 2008, Wynne 2010, and Lunetta 2015, a login redirect from the Nature page of Mishra 2019, a DNS failure for `catalogue.ceda.ac.uk`, and 404 or 403 for guessed manual URLs. The quotes above come from the pages that did load.
