# Audit — EPD-IES-0014327:002

- **Source PDF:** `epd-australasia-com-wp-content-uploads-2024-12-epd-ies-0014327-002-holcim-qld-seq-geostone-qx25mor-2026-04-02-pdf.pdf` (21 pp)
- **Programme:** EPD International AB (International EPD System); Regional Programme: EPD Australasia
- **PCR / standard:** PCR 2019:14 Construction Products, Version 2.0.1, 2025-06-05; c-PCR-003 Concrete and Concrete Elements, 2025-04-08 · EN 15804:2012+A2:2019/AC:2021 (ISO 14025) · EF 3.1
- **Published / valid until:** 2026-04-02 / 2031-04-02
- **Extraction confidence:** high
- **Verified by / checked by:** epd-context-agent (opus) / None

**Number traceability (cross_validate):** 40 declared cells checked, 0 problem(s). **Schema:** 0 error(s).

## System boundary (per module)

| A1 | A2 | A3 | A1-A3 | A4 | A5 | B1 | B2 | B3 | B4 | B5 | B6 | B7 | C1 | C2 | C3 | C4 | D |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ND | ND | ND | ND | ND | ND | ND | ✓ | ✓ | ✓ | ✓ | ✓ |

## Product 1: QLD - SEQ - GEOStone - QX25MOR - S25 MORETON GEOSTONE - Decorative

- **Manufacturer:** Holcim (Australia) Pty Ltd
- **Compressive strength:** 25 MPa (class S25, status found) — p.10
- **Location:** Brisbane City (plus Acacia Ridge, Beaudesert, Beenleigh, Geebung, Wacol, etc.) (AU)
- **Declared unit:** 1 m3 · mass 2361 kg

### GWP-total (kg CO2 eq) — provenance per module

| Module | Value | Raw (verbatim) | Status | Page | Section |
|---|---|---|---|---|---|
| A1-A3 | 237.0 | `237` | declared | 16 |  |
| A4 | 2.63 | `2.63` | declared | 16 |  |
| A5 | 15.6 | `15.6` | declared | 16 |  |
| C1 | 0.522 | `0.522` | declared | 16 |  |
| C2 | 4.39 | `4.39` | declared | 16 |  |
| C3 | 10.5 | `10.5` | declared | 16 |  |
| C4 | 0.0 | `0` | declared_zero | 16 |  |
| D | -18.8 | `-18.8` | declared | 16 |  |

## Comparability notes
- Cradle-to-gate (A1-A3) with options A4-A5, full C1-C4 and module D declared; use stage B1-B7 not declared (ND).
- C4 = 0 is a printed declared value (inert waste landfill mass allocated to C3=1.9E3 kg, C4=4.8E2 kg but GWP prints 0), status declared not not_declared.
- Multi-plant SEQ EPD produced under Holcim's certified EPD Process (process certification, no pre-verified LCA/EPD tool).
- GWP-GHG table (page 17) shows minor rounding differences vs GWP-Total (page 16): A1-A3 237 vs 242, A5 15.6 vs 15.8, C1 0.522 vs 0.523, C3 10.5 vs 10.6 — flagged, numbers not changed.
- Declared unit 1 m3; product mass 2361 kg/m3.

## Warnings
- Cell conflict across pages: GWP_GHG.A1-A3: '237' vs '242'
- Cell conflict across pages: GWP_GHG.A5: '15.6' vs '15.8'
- Cell conflict across pages: GWP_GHG.C1: '0.522' vs '0.523'
- Cell conflict across pages: GWP_GHG.C3: '10.5' vs '10.6'
- GWP-GHG (page 17) vs GWP-Total (page 16) rounding conflicts present in candidate extraction_meta (A1-A3 237/242, A5 15.6/15.8, C1 0.522/0.523, C3 10.5/10.6). Not resolved here; GWP-Total values on page 16 confirmed correct.
