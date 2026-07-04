# Hallett Group EPD (EPD-IES-0009353:003) — complete table inventory & disposition

This is a **multi-table document** (37 sheets, ~48 tables, 5 batch plants, two EN 15804
methods). To guarantee nothing is silently missed, every carbon-relevant table is listed
here with an explicit disposition **before** extraction. Citations show `sheet (printed folio)`.

## Disposition rules
- **EXTRACT** — EN 15804**+A2** GWP results (core impact indicators). Our headline standard.
- **DERIVE** — values the EPD does not print per-mix but provides an official method for
  (density scaling), stored as `estimated` with provenance to the method.
- **EXCLUDE:+A1** — EN 15804**+A1** (older method). The EPD itself states +A1 results "are not
  comparable with +A2 studies" (printed 69) → never mixed with +A2.
- **EXCLUDE:noncarbon** — resource-use, waste, biogenic-content, and additional (ODP/AP/…)
  indicators — outside an embodied-carbon comparison.

## Carbon (+A2) tables — the extract set
| Sheet | Printed | Plant | Module | Table | Mixes | Disposition | Status |
|---|---|---|---|---|---|---|---|
| 11 | 20–21 | Dry Creek | A1–A3 | T13 | 24 | EXTRACT | ✅ done (N-series) |
| 11 | 20–21 | Dry Creek | A1–A3 | T13 (2nd block) | ~20 | EXTRACT | ⛔ S-series pending |
| 16 | 30–31 | Elizabeth | A1–A3 | T19 | 24 (N-series) | EXTRACT | ✅ done |
| 19 | 36–37 | Mile End | A1–A3 | T25 (2 sub-tables) | 40 | EXTRACT | ✅ done (two-engine verified) |
| 20 | 38–39 | Mile End | A1–A3 | T25 CONT'D Table A (top) | 21 | EXTRACT | ✅ done (S4020+S5010, two-engine verified) |
| 20 | 38–39 | Mile End | A1–A3 | T25 CONT'D Table B (bottom) | 15 | EXTRACT | ✅ done (S5020/6510/6520/8010 structural + CLSM/NO-FINES fill labelled; two-engine verified) |
| 29 | 56–57 | McLaren Vale | A1–A3 | T31 | 24 (N-series) | EXTRACT | ✅ done |
| 32 | 62–63 | Osborne | A1–A3 | T37 | 24 (N-series) | EXTRACT | ✅ done |

### Mile End detail (why deferred)
Unlike the other plants' clean 24-mix N-series, Mile End is **4 sub-tables across 2 sheets**,
76 columns, with extra families (N2010P, S2020P, S4010, S5020) and **non-structural products**
(CLSM = controlled low-strength material; NO FINES = no-fines concrete). Variant counts differ
per family (e.g. N2020P has 6 variants here: -, 100, 120, Ref, F30, S30, S50). Reliable
extraction requires building a full authoritative (family,variant) order for all 76 columns
from Table 1 — doable, but the highest column-mapping risk in the document for the lowest
marginal value (same mixes as the other plants, ±1-2%). Deferred pending an explicit decision.
| 35 | 68–69 | (all) | C1–C4+D | T43 | 1 (representative) | EXTRACT-rep | ✅ done |
| 36 | 70–71 | (all) | C1–C4+D | T48 | — | DERIVE (× density/2332) | ⛔ pending |

## Excluded, with reason
| Sheets (printed) | Tables | Reason |
|---|---|---|
| 15, 18, 27–28, 31, 34, 35 | T18, T24, T30, T36, T42, T47 | EN 15804**+A1** — EPD says not comparable with +A2 |
| 12–14, 17, 22–26, 30, 31, 33, 34, 35 | resource / waste / biogenic / additional | non-carbon indicators |

## Full +A2 carbon scope (what "complete" means)
- **A1–A3 across 5 plants:** 24 (Dry Creek N) + ~20 (Dry Creek S) + 24 + ~38 + 24 + 24 ≈ **~134 mix×plant products**.
- **C1–C4+D:** one printed representative + density-scaled `estimated` for every mix.
- **Currently loaded:** Dry Creek N-series (24) + representative C/D = the shipped 24 products.

## Governance rule (applies to every complex EPD, not just this one)
For any document with multiple result tables: build this inventory FIRST, give every table a
disposition, commit it, and extract against it. Completeness is then *provable* from the
inventory — not discovered page by page. (Added to RISKS.md.)
