# Audit — EPD-IES-0014785:001

- **Source PDF:** `EPD-IES-0014785_Heidelberg_Woolworths-GE322LPF2.pdf` (24 pp)
- **Programme:** EPD International AB
- **PCR / standard:** CEN standard EN 15804:A2 (PCR 2019:14 Construction Products, Version 1.3.4) served as the core PCR; Environdec c-PCR-003 Concrete, concrete elements (EN 16757:2023) served as sub-PCR. · EN 15804:A2 (in accordance with ISO 14025, EN 16757:2023, Environdec c-PCR-003) · EF 3.0
- **Published / valid until:** 2024-11-19 / 2029-11-19
- **Extraction confidence:** high
- **Verified by / checked by:** epd-context-agent (Opus 4.8) / None

**Number traceability (cross_validate):** 75 declared cells checked, 0 problem(s). **Schema:** 0 error(s).

## System boundary (per module)

| A1 | A2 | A3 | A1-A3 | A4 | A5 | B1 | B2 | B3 | B4 | B5 | B6 | B7 | C1 | C2 | C3 | C4 | D |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ND | ND | ND | ✓ | ✓ | ✓ | ✓ | 0 | 0 | 0 | 0 | 0 | 0 | ✓ | ✓ | ✓ | ✓ | ✓ |

## Product 1: GE322LPF2 (Hutchinson Builders - Woolworths Doolandella)

- **Manufacturer:** Heidelberg Materials Australia Pty Ltd
- **Compressive strength:** 32 MPa (class None, status found) — p.17
- **Location:** Brisbane (AU)
- **Declared unit:** 1 m3 · mass 2355.5 kg

### GWP-total (kg CO₂e) — provenance per module

| Module | Value | Raw (verbatim) | Status | Page | Section |
|---|---|---|---|---|---|
| A1-A3 | 145.0 | `1.45E+02` | declared | 18 |  |
| A4 | 3.41 | `3.41E+00` | declared | 18 |  |
| A5 | 10.1 | `1.01E+01` | declared | 18 |  |
| B1 | -3.17 | `-3.17E+00` | declared | 18 |  |
| B2 | 0.0 | `0.00E+00` | declared_zero | 18 |  |
| B3 | 0.0 | `0.00E+00` | declared_zero | 18 |  |
| B4 | 0.0 | `0.00E+00` | declared_zero | 18 |  |
| B5 | 0.0 | `0.00E+00` | declared_zero | 18 |  |
| B6 | 0.0 | `0.00E+00` | declared_zero | 18 |  |
| B7 | 0.0 | `0.00E+00` | declared_zero | 18 |  |
| C1 | 8.99 | `8.99E+00` | declared | 18 |  |
| C2 | 9.03 | `9.03E+00` | declared | 18 |  |
| C3 | 5.19 | `5.19E+00` | declared | 18 |  |
| C4 | 2.85 | `2.85E+00` | declared | 18 |  |
| D | -14.1 | `-1.41E+01` | declared | 18 |  |

## Comparability notes
- GCCA Industry EPD Tool for Cement and Concrete (v4.2), International version, used to model results (page 17).
- Full cradle-to-grave scope A1-A3 + A4 + A5 + B1-B7 + C1-C4 + D — all modules declared; no ND/NR modules.
- GWP reported as GWP-tot per the GCCA tool using EF3.0-based EN15804+A2 methodology (page 15); GWP-GHG and GWP-tot are numerically identical here (page 18).
- Module D is negative (-14.1 kg CO2e), a net credit; page 15 discourages using A1-A3 results without also considering Module C.
- Project-specific EPD (Hutchinson Builders - Woolworths Doolandella project); values indicative of local material performance at time of publishing (page 20).
- EPDs from different programmes or that do not comply with EN 15804 may not be comparable (page 22).

## Warnings
- Candidate compressive_strength.value_mpa was null with class='32'; corrected to value_mpa=32 (stated numerically on pages 17 and 20 as MPa, not inferred from the GE322 code). GWP numbers unchanged.
