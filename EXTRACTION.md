# EXTRACTION.md

## Overall strategy
The 20 EPDs come from at least **seven different templates** (EPD Hub / One Click LCA in two
layouts, the International EPD System, EPD Australasia, GCCA slide decks, a multi-product mix
matrix, and a transposed per-stage layout). They disagree on decimal separator, on which
life-cycle modules they declare, on where the results table lives, and even on orientation
(modules-as-columns vs modules-as-rows). So the core decision was: **split the problem by what
each method is actually good at.**

- **Numbers → deterministic parsing.** A GWP figure like `‐1,32E+01` is a landmine for an LLM:
  European decimal comma, a *Unicode* minus (U+2010, not ASCII), scientific notation, and easy
  column drift. I parse these with PyMuPDF word coordinates, binding each value to its module by
  position, and copy the **verbatim `raw` string** alongside the parsed value. No model transcribes
  a number, so no model can hallucinate one.
- **Context → agents.** Product name, compressive strength, manufacturing location, dates, and the
  two irregular templates need reading comprehension. Four agents verified/enriched these against
  the actual PDF pages and extracted the two matrix/per-stage EPDs a parser couldn't.

## Model and architecture
Deterministic layer: PyMuPDF (`get_text("words")`) + coordinate/order-bound table reconstruction,
with a status classifier that keeps `ND / NR / declared-zero / missing` distinct. Agent layer:
per-EPD verification with a strict corrections schema (agents may only touch contextual fields;
they cannot overwrite numbers, only flag them). I chose this over an off-the-shelf PDF-table library
or a pure vision-LLM because provenance had to be *per cell* and machine-verifiable, and because the
templates were too varied for one table extractor — but too numeric for an LLM to be trusted alone.

## Accuracy — how I know it's right
Three gates: **(1)** `cross_validate.py` re-opens each source PDF and asserts every stored `raw`
value appears literally on its cited page — traceability is machine-checked, not promised. **(2)** a
schema validator enforces the status enum and forbids a `not_declared` cell from carrying a value.
**(3)** independent agent review. The loop paid off: agents caught a mis-bound strength (P252080
read as 40 MPa; actually 25), C-module values pulled from the GWP-GHG (IPCC AR5) table instead of
core GWP-total on Dry Creek, and several wrong dates/locations — all fixed with provenance.

## What could go wrong / how it's handled
Column-to-module drift, decimal/minus dialects, and indicator confusion (GWP-total vs GWP-GHG vs
+A1/CML) are the main traps — addressed by positional binding + verbatim raws + using **GWP-total
EN 15804+A2** only. **A not-declared module is never 0**: it keeps its status and is excluded from
any total, which is labelled with the stages it covers. Genuinely hard cases (Dry Creek's S-series
and density-scaled end-of-life modules) are listed in `needs_review` rather than invented — honest
gaps beat false completeness, because someone makes a procurement decision on these numbers.
