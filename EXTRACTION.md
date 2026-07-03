# EXTRACTION.md

## Overall strategy
The 20 EPDs come from at least **seven different templates** (EPD Hub / One Click LCA in two
layouts, the International EPD System, EPD Australasia, GCCA slide decks, a multi-product mix
matrix, and a transposed per-stage layout). They disagree on decimal separator, on which
life-cycle modules they declare, and even on table orientation. So the core decision was:
**split the problem by what each method is actually good at.** Numbers go through
deterministic parsing — a figure like `‐1,32E+01` is a landmine for an LLM (European decimal
comma, *Unicode* minus U+2010, scientific notation, easy column drift). Context (product name,
strength, location, dates) and the two irregular templates go through agent verification
against the actual PDF pages, because that part is reading comprehension.

## Model and architecture
Deterministic layer: PyMuPDF word coordinates with order-bound column mapping, storing the
**verbatim `raw` string** beside every parsed value. Agent layer: per-EPD verification with a
strict corrections schema — agents may only touch contextual fields, never overwrite numbers.
I chose this over an off-the-shelf table library or a pure vision-LLM because provenance had
to be per-cell and machine-checkable, and the templates were too varied for one extractor —
but too numeric to trust a model's transcription.

## Accuracy — what could go wrong, and how I know it's right
The main failure modes are column→module drift, decimal/minus dialects, and indicator
confusion (GWP-total vs GWP-GHG vs the +A1/CML duplicate table). Three machine gates guard
them: a validator asserting every stored raw value appears **literally on its cited page**; a
schema forbidding a not-declared cell from carrying a value (**ND is never 0**); and a full
re-extraction with two independent engines (pdfplumber, pypdf) diffed cell-by-cell against
the shipped data — **~760 cells, zero mismatches**. Genuinely un-extractable items (Dry
Creek's S-series variants) are listed in `needs_review`, not invented.

## Research and process
I assumed two formats and found seven — each "empty" parser result was investigated, not
patched. Pure nearest-x column binding silently dropped edge columns on split tables; I
questioned it and switched to positional zip with a count guard. I questioned whether product
codes imply strength — they don't reliably: P252080 was mis-bound as 40 MPa; the PDF states
25 (p.20). Independent checking caught the parser reading Dry Creek's C-modules from the
GWP-GHG (IPCC AR5) table instead of core GWP-total, and a boilerplate "valid until" date on
GreenCrete. Adbri's A1–A3 table turned out to be a rotated raster image with no text layer —
read visually at high zoom, verified twice, and flagged `source_type: "image"` rather than
passing silently. Its boundary declares A5/C/D in scope yet publishes no values — recorded as
`not_reported`, a distinct state from `not_declared`, because both honesty and comparability
depend on the difference.
