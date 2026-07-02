# LCMH — Concrete EPD Carbon Compare

A thin slice of a platform that makes the embodied carbon of concrete products
**comparable and honest**. Extracts structured carbon data from 20 real concrete EPDs
(Part 1) and serves a Next.js app to compare them stage-by-stage with full provenance
(Part 2).

- **Part 1 write-up:** [`EXTRACTION.md`](./EXTRACTION.md) — strategy, architecture, accuracy, assumptions.
- **Data:** [`/data/*.json`](./data) — one JSON per EPD (the app's data source).
- **Audit trail:** [`/docs/audit`](./docs/audit) — per-EPD provenance table for every carbon number, plus [`AUDIT_SUMMARY.md`](./docs/AUDIT_SUMMARY.md).
- **Pitfalls / rules the build watches:** [`RISKS.md`](./RISKS.md).

## The one hard rule
Every carbon figure is traceable to its source EPD: **PDF · page · table/section · module ·
unit · status · verbatim value**. A not-declared stage is shown as `ND`, never as `0`.

## How the data was made (hybrid, by design)
1. **Deterministic parse** (`scripts/lib_tables.py`, `extract.py`) reads GWP tables by word
   coordinates, binding each value to its module and keeping the verbatim `raw` string.
   Handles decimal-comma vs decimal-point, Unicode-minus, scientific notation, split and
   transposed tables. No model transcribes a number.
2. **Agent verification** filled contextual fields (name, strength, location, dates) and
   extracted the two irregular templates (a 24-mix matrix; a rasterised per-stage layout),
   then **independent checker agents** re-audited every file against the source PDF.
3. **Machine gates:** `scripts/cross_validate.py` asserts every stored value literally
   appears on its cited page (image-sourced cells are flagged `source_type: "image"`);
   `scripts/schema.py` enforces the status enum and forbids a not-declared cell from
   carrying a value.

Reproduce:
```bash
python3 -m pip install pymupdf pdfplumber
python3 scripts/extract.py        # PDFs -> candidate JSON (numbers)
python3 scripts/finalize.py       # + agent corrections -> /data
python3 scripts/schema.py         # structural validation (0 errors)
python3 scripts/cross_validate.py # number traceability (0 problems)
python3 scripts/audit_report.py   # /docs/audit/*.md
```

## The app
```bash
npm install
npm run dev      # http://localhost:3000
```
- **Products** — filter by compressive strength and manufacturing location; sort by A1–A3 carbon.
- **Compare** — pick 2–4 products; full life-cycle GWP-total table (A1–A3, A4, A5, C1–C4, D),
  each figure links to the source EPD page. Flags when products declare different stages or
  units (not directly comparable). Totals sum only declared stages and say which.
- **Methodology** — how to read the numbers.

Data is 20 EPDs / 43 products. `scripts/`, `epds/` (source PDFs, also served from
`/public/epds` for provenance) and `extract_work/` support the pipeline; `/data` and the app
are the deliverables.
