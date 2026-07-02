# Audit — EPD-IES-20602:001

- **Source PDF:** `epd-ies-20602-001-holcim-vic-melbourne-metro-ecopact-ve322eamf-epd.pdf` (20 pp)
- **Programme:** EPD International AB (The International EPD System); Regional Programme: EPD Australasia
- **PCR / standard:** PCR 2019:14 Construction Products, Version 1.3.4, 2024-04-30; c-PCR-003 Concrete and Concrete Elements, 2024-04-30 · EN 15804:2012+A2:2019/AC:2021 (ISO 14025) · EF 3.1
- **Published / valid until:** 2025-04-15 / 2030-04-15
- **Extraction confidence:** high
- **Verified by / checked by:** epd-context-agent (opus) / None

**Number traceability (cross_validate):** 40 declared cells checked, 0 problem(s). **Schema:** 0 error(s).

## System boundary (per module)

| A1 | A2 | A3 | A1-A3 | A4 | A5 | B1 | B2 | B3 | B4 | B5 | B6 | B7 | C1 | C2 | C3 | C4 | D |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ND | ND | ND | ND | ND | ND | ND | ✓ | ✓ | ✓ | ✓ | ✓ |

## Product 1: VIC - Melbourne Metro - ECOPact - VE322EAMF (S32@56D 20mm 120SL ECOPactMAX FIB CONC)

- **Manufacturer:** Holcim (Australia) Pty Ltd
- **Compressive strength:** 32 MPa (class S32, status found) — p.10
- **Location:** Melbourne (Laverton, Truganina, Footscray, Epping, Keilor, Preston, etc.) (AU)
- **Declared unit:** 1 m3 · mass 2400 kg

### GWP-total (kg CO2 eq) — provenance per module

| Module | Value | Raw (verbatim) | Status | Page | Section |
|---|---|---|---|---|---|
| A1-A3 | 105.0 | `105` | declared | 15 |  |
| A4 | 2.05 | `2.05` | declared | 15 |  |
| A5 | 8.81 | `8.81` | declared | 15 |  |
| C1 | 0.532 | `0.532` | declared | 15 |  |
| C2 | 3.99 | `3.99` | declared | 15 |  |
| C3 | 7.61 | `7.61` | declared | 15 |  |
| C4 | 1.28 | `1.28` | declared | 15 |  |
| D | -15.7 | `-15.7` | declared | 15 |  |

## Comparability notes
- Cradle-to-gate (A1-A3) with options A4-A5, full C1-C4 and module D declared; use stage B1-B7 not declared (ND).
- C4 = 1.28 kg CO2e is a positive declared value here (unlike the QLD Holcim EPDs where C4 GWP prints 0).
- PCR version differs from the other Holcim files: this EPD uses PCR 2019:14 v1.3.4 (2024-04-30) + c-PCR-003 2024-04-30, whereas the SEQ/Brisbane files use PCR v2.0.1 (2025). Only compare EPDs on the same PCR first-digit version.
- Strength declared at 56 days (S32@56D), a later age than the typical 28-day basis — relevant when comparing strength-normalised carbon.
- GWP-GHG (AR5) row on page 16 (A1-A3=110, D=-15.2) is a separate AR5-based indicator, not an error vs GWP-Total (105).
- Declared unit 1 m3; product mass 2,400 kg/m3.

## Warnings
- Cell conflict across pages: GWP_GHG.A1-A3: '105' vs '110'
- Cell conflict across pages: GWP_GHG.A4: '2.05' vs '2.02'
- Cell conflict across pages: GWP_GHG.A5: '8.81' vs '8.65'
- Cell conflict across pages: GWP_GHG.C1: '0.532' vs '0.521'
- Cell conflict across pages: GWP_GHG.C2: '3.99' vs '3.95'
- Cell conflict across pages: GWP_GHG.C3: '7.61' vs '7.56'
- Cell conflict across pages: GWP_GHG.C4: '1.28' vs '1.25'
- Cell conflict across pages: GWP_GHG.D: '-15.7' vs '-15.2'
- Candidate extraction_meta 'cell conflicts' for GWP_GHG (e.g. A1-A3 '105' vs '110') compare the GWP-GHG row against the GWP-GHG (AR5) row on page 16 — different indicators, not a data error. GWP-Total values on page 15 confirmed correct.
