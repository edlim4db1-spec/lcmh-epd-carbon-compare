# RISKS & PRIORITIES — living tracker (read before every EPD)

This is the "constant reminder" doc. Every extraction agent and every checker agent must
re-read this before touching a file. It encodes the ways this task goes wrong.

## THE ONE HARD RULE
Every carbon number must trace to: **source PDF filename · physical page · printed page ·
section/table heading · lifecycle module (A1–A3, A4, A5, C1–C4, D…) · unit · status**
(declared / declared_zero / not_declared / not_relevant / estimated / missing).
A number without provenance is WORSE than no number.

## MUST-HAVES (non-negotiable)
1. 20 JSON files in /data, one per EPD, all validating against the shared schema.
2. Every GWP cell carries full provenance + a `raw` string copied verbatim from the PDF.
3. `not_declared` / `not_relevant` are NEVER stored or displayed as 0.
4. Full lifecycle captured (A1–A3, A4, A5, B*, C1–C4, D) — not just the A1–A3 headline.
5. EXTRACTION.md explains strategy, model/architecture, accuracy method, assumptions, failure modes.
6. App shows per-stage breakdown, missing-data honestly, provenance visible, filters (strength, location).

## PARSING TRAPS (numeric)
- P1. Decimal separator VARIES: EPD HUB uses comma `2,32E+02`; IES/Australasia uses point `1.34E+02`. Detect per-doc.
- P2. NEGATIVE values (module D credits) use a Unicode minus `‐` (U+2010), not ASCII `-`. `float()` will break or drop the sign.
- P3. Scientific E-notation everywhere: `2,32E+02` = 232. Exponent minus may also be Unicode: `E‐01`.
- P4. Column→module mapping is the #1 silent error. An off-by-one column puts A4's value under A5. Verify against the header row every time.
- P5. `ND`, `NR`, `MND`, `-`, blank, and `0.00E+00` are DIFFERENT. 0.00E+00 = declared-zero; ND = not declared; NR = not relevant.
- P6. Some tables omit whole modules as COLUMNS (IES greencrete shows only A1-A3, C1-C4, D — A4/A5 absent because ND). Absent column ≠ 0.
- P7. Mass "2352" vs European "2,352" — don't misread mass/decimal.

## SEMANTIC / MODULE TRAPS
- S1. Multiple GWP rows: GWP-total, GWP-fossil, GWP-biogenic, GWP-LULUC, GWP-GHG. Headline = **GWP-total (EN 15804+A2)**. Keep fossil + biogenic. GWP-GHG is a separate legacy indicator.
- S2. Some EPDs print BOTH an EN 15804+A2 (EF 3.1) table AND an +A1 (CML) table — different numbers. Use +A2 as primary; do not mix.
- S3. A1-A3 may be given only as an aggregate, or as A1/A2/A3 + aggregate. Don't double-count, don't invent splits.
- S4. Module D is legitimately negative. Never clamp to 0 or flag as error.
- S5. C may be C1/C2/C3/C4 separate or aggregated. Capture what's declared.
- S6. GWP-biogenic in A1-A3 can be negative (uptake).

## UNIT / FUNCTIONAL-UNIT TRAPS
- U1. Declared unit usually 1 m³ but confirm (could be 1 tonne / "1 m³ supplied to client").
- U2. Units "kg CO2e" vs "kg CO2 eq" = same; normalize but keep raw.
- U3. Record mass per declared unit (kg/m³) — needed to reconcile m³ vs tonne comparisons.
- U4. Compressive strength: extract numeric MPa + class. May live in product name code (S32, GE322, AR2520), product characteristics, OR description. VERIFY from text — do not guess MPa from a product code.

## PROVENANCE TRAPS
- V1. PyMuPDF page index is 0-based; store physical page (index+1) AND the printed page number (cover offset differs).
- V2. Cite the authoritative results table, not the p2 summary duplicate (note both).
- V3. Table/section heading must be copied exactly.

## HONESTY TRAPS (the "don't fake completeness" list)
- H1. No blanket missing→0.
- H2. No A1-A3-only display hiding full lifecycle.
- H3. No fabricated page numbers.
- H4. No claiming comparability across EPDs with different declared module sets.
- H5. Schema must be deep enough to hold status + provenance per cell, not just a number.

## MULTI-TABLE DOCUMENT TRAP (root-cause rule)
- M1. **Inventory before extraction.** For any EPD with more than one result table (multi-plant,
  multi-mix, +A1/+A2 dual, split/CONT'D tables), enumerate EVERY table FIRST and give each an
  explicit disposition: EXTRACT (+A2 carbon) / DERIVE (EPD-provided method, mark `estimated`) /
  EXCLUDE:+A1 (not comparable per EN 15804) / EXCLUDE:noncarbon. Commit the inventory
  (see docs/hallett_table_inventory.md). Completeness must be PROVABLE from the inventory,
  never discovered page-by-page as a reviewer surfaces gaps.
- M2. **CONT'D tables are one logical table** — merge sheet pairs before parsing columns.
- M3. **Per-mix values the EPD derives by a stated method** (e.g. C1-C4+D by density scaling)
  are `estimated` with provenance to the method table — not `not_reported`, not `0`.

## UI DISPLAY TRAPS (found in review — check after every UI change)
- D1. EVERY status enum value must render a visible label/badge in EVERY view that shows
  status (declared, declared_zero, not_declared, not_relevant, not_reported, estimated,
  missing). A blank cell is indistinguishable from a bug. (Caught live: declared_zero
  rendered no STATUS label on the product page.)
- D2. The product detail page is the AUDIT view: it must mirror the source table 1:1 —
  all 15 modules always, ND shown as ND. Compare is the DECISION view: adaptive rows are
  fine there, but exclusions must be stated on totals. (Caught live: PDF printed B1-B7 'ND'
  columns; detail page hid the rows entirely.)

## COMPARABILITY TRAPS (app must surface)
- C1. Different EPDs declare different modules → cradle-to-grave totals not directly comparable. Flag it.
- C2. Different PCR / EN15804 version / EF version / geography / data period → note per EPD.
- C3. Filters must handle strength class variants (N vs S vs numeric-only) and missing strength.

## PROCESS TRAPS
- Pr1. Detect image-only/scanned pages (get_text empty) → OCR fallback needed.
- Pr2. Multi-column layouts can scramble text order.
- Pr3. One EPD may cover multiple products/strengths — identify which.
- Pr4. Agent hallucination: checker must confirm every stored value string appears in the source page text.

## STATUS LOG (update as we go)
- [ ] Deterministic extractor validated on 2 formats
- [ ] 20/20 extracted
- [ ] 20/20 checked by independent audit
- [ ] Schema validation passing
- [ ] App built + verified locally
- [ ] (final) GitHub + Vercel — ONLY after local verification
