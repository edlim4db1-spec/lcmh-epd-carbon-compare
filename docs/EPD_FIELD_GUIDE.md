# EPD Extraction Field Guide — agent playbook

Purpose: a **repeatable map** for extracting carbon data from *any* concrete EPD. Every
scenario below was hit on a real document in this project; each entry says how to **detect**
it, how to **tackle** it, and how to **verify** the result. Follow the intake checklist for
every new EPD *before* extracting — completeness and correctness then become repeatable, not
rediscovered page-by-page.

Companion files: `RISKS.md` (condensed rules), `docs/hallett_table_inventory.md` (worked
multi-table inventory), `docs/VERIFICATION.md` (gate results), `scripts/` (the tools below).

---

## 0. Intake checklist — run for EVERY new EPD, in order
1. **Text vs image?** `page.get_text()` empty on the results page → rasterised table → must be
   read visually and each cell flagged `provenance.source_type:"image"` (can't be text-verified).
2. **Numeric dialect.** Decimal comma vs point; minus is often Unicode U+2010 `‐`, not ASCII.
3. **Pagination map.** Run `scripts/page_labels.py`. Physical sheet ≠ printed folio when the
   doc is a **booklet spread** (one sheet prints two folios, e.g. sheet 11 = "20–21") or has
   **unnumbered front matter** (constant offset). Store physical→printed; links target physical.
4. **Table inventory.** List EVERY results table with a disposition (extract / derive /
   exclude-A1 / exclude-noncarbon) BEFORE extracting. See §3.
5. **Indicator.** Headline = **GWP-total, EN 15804+A2**. NOT GWP-GHG, NOT the +A1/CML duplicate.
6. **Shape.** Single vs multi-product; single vs multi-plant; modules-as-columns vs
   modules-as-rows (transposed) vs mix-matrix.
7. **Boundary table.** Read it — it declares which modules are in scope (X / ND / NR).

---

## 1. Template taxonomy (seen so far)
| Family | Traits | Gotchas |
|---|---|---|
| EPD HUB / One Click LCA (13p) | modules as columns, decimal comma, Unicode minus | GWP table ~p9 |
| EPD HUB "Boral" (20p) | results **split across two pages** (A-modules \| C-modules) | ASCII minus + point decimals here |
| International EPD System / Australasia | modules as columns, reduced set (A4/A5 often ND) | point decimals, "kg CO2 eq" |
| GCCA slide deck | landscape, `GWP-tot`/`GWP-GHG` rows, B1–B7 declared | B1 = carbonation credit; 0.00E+00 = declared-zero |
| Adbri per-stage | **transposed** (indicators=columns), one table per stage, **image A1-A3** | boundary declares C/D but no results → `not_reported` |
| Hallett multi-product matrix | mixes=columns, families×variants, multi-plant, +A1 & +A2 both | see §2 R3/R8/R9/R11 |

---

## 2. Risk map — detect → tackle → verify
- **R1 Decimal separator.** Detect: comma vs point in E-notation. Tackle: treat separator-before-E
  as decimal. Verify: parsed value round-trips to the raw string.
- **R2 Unicode minus.** Detect: `‐‑–−` on module-D credits. Tackle: normalise to `-` before float.
  Verify: negative D survives; never clamp to 0.
- **R3 Column→module (and family→variant) mapping — THE big one.** Detect: any table where a
  header spans a group (family headers centred over variant groups). Tackle: DO NOT assign by
  nearest-x coordinate — it mislabels (bit us: "S3220 PLC2" tagged as "S2520"). Use an
  **authoritative order** (the document's own version-history / registry list), or positional
  zip of values L→R against a known ordered key list. Verify: value count == key count; second
  engine (pypdf/pdfplumber) reproduces the same L→R values. **AND validate every (family,variant)
  against the registry table** (`scripts/hallett_validate.py`): a value can zip to the correct
  *position* but the wrong *label* when a family's variant count is off by one — the S3220/S4010
  bug (E1100 was an S3220 variant, mislabelled S4010) passed value-verification but failed
  registry-validation. Build/consume counts from the registry, never from assumption.
- **R5b +A1 vs +A2 on spot-checks.** A reviewer zooming a PDF may land on the +A1 table (numbers
  differ ~2-3% from +A2). Before trusting a reported mismatch, find which page the crop is from
  (searching the value revealed page 27 = the +A1 table, not the +A2 we ship).
- **R4 Status semantics.** `declared` (value) / `declared_zero` (printed 0.00E+00) / `not_declared`
  (ND, out of boundary) / `not_relevant` (NR) / `not_reported` (in boundary but no value) / absent.
  Never collapse to 0. Verify: schema forbids a value on not_declared/not_relevant.
- **R5 Indicator confusion.** Detect: multiple GWP rows + a second (+A1/CML) table with different
  numbers. Tackle: take +A2 GWP-total only; the doc itself says +A1 "is not comparable with +A2".
  Verify: A1+A2+A3 reconcile with the A1-A3 aggregate.
- **R6 Pagination (sheet vs folio).** Detect: `page_labels.py` fit — identity / spread (2N-2|2N-1)
  / offset. Tackle: link to physical sheet, display both ("p.11 (20–21)"). Verify: fit score ≥0.5.
- **R7 Image tables.** Detect: text layer empty, page has images. Tackle: render at high zoom,
  read visually, cross-check ×2, mark `source_type:"image"`. Verify: two independent readings agree.
- **R8 Multi-product.** Detect: one PDF, many mixes/columns. Tackle: `products[]` array, one per
  mix, each with its own strength + provenance. Verify: one JSON file still = one EPD.
- **R9 Multi-plant.** Detect: same mixes re-tabulated per plant. Tackle: one product per (mix,plant);
  A1-A3 per plant; `location.city` = plant (so the location filter is a plant selector); mass-only
  modules (C1-C4/D) are plant-independent → reuse. Verify: per-plant values differ ±1-2% as expected.
- **R10 CONT'D tables.** Detect: "… CONT'D" heading. Tackle: merge the sheet pair into one logical
  table before mapping columns. Verify: merged column count matches the mix list.
- **R11 Derived values (method stated by the EPD).** Detect: EPD gives a formula for values it
  doesn't print per-mix (e.g. C/D by density: `value × density/2332`). Tackle: compute, store as
  `estimated`, provenance → the method table; never as declared. Verify: recompute the EPD's own
  worked example (matched 14.8×2410/2332 = 15.3).
- **R12 Compressive strength.** Detect: strength encoded in a product code (N32, AR2520, S32).
  Tackle: take the MPa from stated text only (caught P252080: code implied 40, text said 25).
  Verify: the MPa appears verbatim near "strength/grade" in the source.
- **R13 Non-structural products.** Detect: CLSM (controlled low-strength fill), NO FINES, flowable
  fill. Tackle: extract if completeness requires, but label `concrete_type` clearly and keep them
  out of default structural comparisons. Verify: flagged, not silently mixed with structural mixes.

---

## 3. Inventory-first methodology (root cause of "missed tables")
Gaps surface page-by-page only when there's no plan. For any multi-table doc: enumerate EVERY
results table with a disposition first, commit the inventory, extract against it. Completeness is
then *provable from the inventory*. See `docs/hallett_table_inventory.md`.

## 4. Verification gates (all must pass)
`schema.py` (structure + status enum) · `cross_validate.py` (every declared `raw` literally on its
cited page) · `qa.py` (internal consistency: A1+A2+A3≈A1-A3, boundary vs status, dates) ·
`verify_independent.py` + `verify_teamC.py` (second/third engine cell-diff, 0 mismatches).

## 5. Honesty invariants
Every figure: source PDF · physical page (+ printed folio) · section · module · unit · status ·
verbatim raw. ND / not_reported / NR are never 0. Estimated values are badged and cite their
method. Genuinely un-extractable items go in `needs_review`, not invented.

## 6. Escalation
Defer only what is genuinely un-mappable without guessing — and when you defer, **document the
exact structure and reason in the inventory** so it is a recorded, resumable item, never a silent
gap. Deferral for *risk* (can't map safely yet) is legitimate; deferral for *value* is not.
