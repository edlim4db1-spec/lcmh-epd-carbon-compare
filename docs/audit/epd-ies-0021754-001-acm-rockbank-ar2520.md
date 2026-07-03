# Audit — EPD-IES-0021754:001

- **Source PDF:** `epd-ies-0021754-001-acm-rockbank-ar2520.pdf` (25 pp)
- **Programme:** EPD International AB (The International EPD System); Regional Programme: EPD Australasia Limited
- **PCR / standard:** PCR 2019:14 Construction Products, Version 2.0.1, 2025-06-05; c-PCR-003 (to 2019:14) Concrete and concrete elements, version 2025-04-08 · EN 15804:2012+A2:2019/AC:2021 (ISO 14025:2006) · EF 3.1
- **Published / valid until:** 2025-08-15 / 2030-08-15
- **Extraction confidence:** high
- **Verified by / checked by:** epd-context-agent (opus) / None

**Number traceability (cross_validate):** 30 declared cells checked, 0 problem(s). **Schema:** 0 error(s).

## System boundary (per module)

| A1 | A2 | A3 | A1-A3 | A4 | A5 | B1 | B2 | B3 | B4 | B5 | B6 | B7 | C1 | C2 | C3 | C4 | D |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ✓ | ✓ | ✓ | ✓ | ND | ND | ND | ND | ND | ND | ND | ND | ND | ✓ | ✓ | ✓ | ✓ | ✓ |

## Product 1: AR2520 pre-mixed concrete manufactured at Rockbank

- **Manufacturer:** Aurora Construction Materials Epping Pty Ltd (Aurora / ACM)
- **Compressive strength:** 25 MPa (class None, status found) — p.5
- **Location:** Rockbank (near Melbourne) (AU)
- **Declared unit:** 1 m3 · mass 2270 kg

### GWP-total (kg CO2-eq) — provenance per module

| Module | Value | Raw (verbatim) | Status | Page | Section |
|---|---|---|---|---|---|
| A1-A3 | 140.0 | `1.40E+02` | declared | 18 |  |
| C1 | 12.0 | `1.20E+01` | declared | 18 |  |
| C2 | 14.5 | `1.45E+01` | declared | 18 |  |
| C3 | 8.03 | `8.03E+00` | declared | 18 |  |
| C4 | 0.861 | `8.61E-01` | declared | 18 |  |
| D | -9.79 | `-9.79E+00` | declared | 18 |  |

## Comparability notes
- Cradle-to-gate + end-of-life: modules A1-A3, C1-C4, D declared. Construction (A4-A5) and use (B1-B7) NOT declared (ND) — no A4/A5 in this EPD, unlike the Holcim EPDs which include A4-A5.
- Single-product, single-location EPD (Rockbank plant only); individual EPD verification without a pre-verified LCA/EPD tool.
- GWP-total uses EF 3.1 / IPCC AR6 CFs (higher numeric values than AR5). Document also reports a separate 'GWP-GHG (IPCC AR5)' row (A1-A3=139, C1=12.0, C2=14.5, C3=7.83, C4=0.861, D=-9.8) aligned to Australian GHG reporting.
- Manufacturer Aurora uses GGBFS (treated as secondary material) and recycled aggregates — a lower-carbon 'ALTRA' style mix.
- Declared unit 1 m3; density/mass 2270 kg/m3.
- Version date 2025-08-15 / valid until 2030-08-15 confirmed from p1 (the 2030-04-07 seen elsewhere is the PCR's validity, not the EPD's).

## Warnings
- Cell conflict across pages: GWP_GHG.A1-A3: '1.39E+02' vs '139'
- Cell conflict across pages: GWP_GHG.C1: '1.20E+01' vs '12.0'
- Cell conflict across pages: GWP_GHG.C2: '1.45E+01' vs '14.5'
- Cell conflict across pages: GWP_GHG.C3: '7.83E+00' vs '7.83'
- Cell conflict across pages: GWP_GHG.C4: '8.61E-01' vs '0.861'
- Cell conflict across pages: GWP_GHG.D: '-9.79E+00' vs '-9.8'
- Candidate date fields were wrong: candidate published='20' (truncated, p24) and valid_until='2030-04-07' (that date is the PCR's validity, page 3, not the EPD's). Correct per page 1/3: Published 2025-08-15, Valid until 2030-08-15. Corrected here; GWP numbers unchanged.
- Candidate manufacturing_location='6 Cube Court' is the EPD Australasia regional programme operator address (Richmond, New Zealand), not the plant. Corrected to Rockbank, VIC.
- Candidate declared_unit description was garbled ('5'). Corrected to full text from page 7.
- Candidate extraction_meta 'cell conflicts' for GWP_GHG (e.g. '1.39E+02' vs '139') are the GWP-GHG row vs the GWP-GHG (IPCC AR5) row on the same page 18 — different indicators, not a data error.
