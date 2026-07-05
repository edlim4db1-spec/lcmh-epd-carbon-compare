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
- **R10 CONT'D tables.** Detect: "… CONT'D" heading — this is the SAME +A2 table continued onto
  the next sheet(s), not a new section. Tackle: treat the "…CONT'D" page(s) as part of the same
  logical table and extract them too (a common miss is taking only the first page and dropping the
  continuation, losing products). Merge the sheet run into one logical table before mapping columns.
  Verify: merged column count matches the mix list; confirm each continued page still reads
  "+A2 CONT'D" (not a switch to +A1 — see R15).
- **R11 Derived values (method stated by the EPD) — GENERAL.** This is not Hallett-specific. An
  EPD may print a result for one representative item and give a **documented method** to obtain it
  for the rest — and the method, the module, and the driver differ per document (Hallett: C1-C4+D
  by *density*, `value × density/2332`; another EPD might derive A4 transport by *distance*, or a
  module by *mass*, *SCM %*, etc.). Detect: look for an annex / "calculation steps" / "results for
  other mixes can be determined by…" statement. Tackle: apply the EPD's exact formula, store
  `status:"estimated"`, provenance → the representative table + the method page + the driver value
  and its source; **never** label it declared, and **never** sum it into the declared total (show a
  separate "incl. estimated"). Verify: recompute the EPD's own worked example if it gives one
  (Hallett matched 14.8×2410/2332 = 15.3). UI: one consistent `est` badge + a Methodology note, so a
  reviewer sees the assumption without opening a cell.
- **R12 Compressive strength.** Detect: strength encoded in a product code (N32, AR2520, S32).
  Tackle: take the MPa from stated text only (caught P252080: code implied 40, text said 25).
  Verify: the MPa appears verbatim near "strength/grade" in the source.
- **R15 Multiple tables per sheet (caught TWICE — hard rule).** One PDF sheet often holds
  **more than one result table** stacked top+bottom under a single heading (e.g. Mile End
  printed 38-39: S4020+S5010 on top, S5020/S6510/S6520/S8010+CLSM+NO-FINES below — both
  EN15804+A2). There is no new page heading between them, so it's easy to grab only the top.
  Detect: **count the GWPt rows on the sheet** — each result table has exactly one. Tackle:
  extract EVERY table on the sheet (never a `first_only` shortcut). Verify (completeness gate):
  Σ(values across all GWPt rows on the sheet) == Σ(mixes mapped from that sheet). A shortcut
  that skips the bottom table passes value-verification on what it *did* take, so this count
  gate is the only thing that catches under-extraction.
  **Standard/indicator consistency (critical):** a sheet may stack tables of DIFFERENT kinds.
  Only extract/merge tables under the SAME heading you're collecting — **EN 15804+A2 core GWP**.
  Before taking a table, confirm its heading hasn't swapped to **+A1** (exclude, R5) or to a
  different indicator block (resource use / waste / biogenic-content / additional — exclude,
  non-carbon). Number of tables per sheet varies (some sheets show one, some two); take the ones
  that qualify, skip the ones that don't — and record the disposition per table in the inventory.
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

## 5b. UI display rules (the interface must not lie either)
The extraction can be honest and the UI still mislead. Enforce, and re-check after every UI change:
- **Every status enum renders a visible label** in every view that shows status (declared /
  declared_zero → "declared (zero)" / not_declared → ND / not_relevant → NR / not_reported /
  estimated → est / image). A blank cell is indistinguishable from a bug. (Caught live:
  declared_zero rendered no status label; estimated used two different colours.)
- **One consistent badge per state** — same glyph and colour everywhere it appears (value column,
  status column, legend). Add every state used to the on-screen legend.
- **Mirror the source's own labels.** If the EPD prints "N/A" for a field (e.g. fill materials
  CLSM / no-fines have no compressive-strength grade), show "N/A", not a "?" placeholder.
- **Provenance is uniform across ALL displayed facts**, not just carbon: strength, location,
  declared unit and mass each click through to their exact source page too.
- **Stage table mirrors the source RESULTS table column-for-column** (R4-style): show a stage row
  only when the document's results table addressed that module (a number, a printed 0, or a
  printed ND); omit modules whose columns the PDF omits (they live in the system-boundary strip).
  Product page = audit view (1:1 with source). Compare = decision view (adaptive rows, but state
  exclusions on totals).
- **Show totals, and keep declared vs estimated separate.** A per-stage table needs a total; the
  declared total sums only declared/declared_zero; any estimated contribution is shown as a
  separate "incl. estimated" figure, never blended into the declared number. Render them as **two
  distinct total rows on BOTH the audit (product) and decision (compare) views** — a "Declared
  total" (measured only) and a secondary "Total incl. estimated" (declared + density-scaled est,
  badged). The second row appears only when a product actually has estimated modules; on compare,
  products without estimated modules show "—" there (their declared total already covers their full
  extracted lifecycle). The declared number is the auditable figure; the incl.-estimated number is
  the full-lifecycle comparison — a builder reads both.
- **Citations: physical page for the link, printed folio for the reader.** Links target the
  physical PDF sheet (so they land); display both when they differ, e.g. `p.19 (36–37)`.
- **Long provenance/section labels truncate cleanly** (ellipsis, full text in tooltip) — never a
  mid-word cut.

## 6. Escalation
Defer only what is genuinely un-mappable without guessing — and when you defer, **document the
exact structure and reason in the inventory** so it is a recorded, resumable item, never a silent
gap. Deferral for *risk* (can't map safely yet) is legitimate; deferral for *value* is not.
Do **not** overlook a table because a plant/sheet isn't structurally identical to an easy one, or
because it isn't a single clean table — PDFs vary; a harder layout is a reason to slow down and map
it, not to drop it. Every EN 15804+A2 table that exists is in scope; record the disposition of each.
