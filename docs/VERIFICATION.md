# Verification matrix — how every number reached "verified"

Goal: no carbon figure ships unless it is confirmed by **at least two independent methods**.
"Independent" means a different PDF engine or a different pair of eyes — not the same code
run twice.

## Methods
| ID | Method | Engine |
|----|--------|--------|
| A  | Primary extraction: coordinate/order-bound table parse | PyMuPDF (MuPDF) |
| B  | Independent re-extraction + cell diff (`verify_independent.py`) | pdfplumber (pdfminer.six) |
| C  | Independent re-extraction + cell diff (`verify_teamC.py`) | pypdf |
| V  | Visual read of rendered page at high zoom (rasterised tables) | human/agent eyes ×2 |
| T  | Traceability gate: stored raw string literally on cited page (`cross_validate.py`) | PyMuPDF text search |
| G  | Agent audit vs source PDF (extraction agent + independent checker agent) | LLM read |

## Results (all 20 EPDs, 43 products)
| File group | Declared GWP cells | Verified by | Mismatches |
|---|---|---|---|
| 10 × EPD HUB (both layouts) | 447 | A + B + T (+G on 6 files) | 0 |
| 4 × IES/Australasia (Holcim, ACM, GreenCrete) | 128 | A + B + T + G | 0 |
| 3 × GCCA slides (Hanson, Heidelberg, Hymix) | 135 | A + C + T + G | 0 |
| Dry Creek multi-product (24 mixes) | 77 | A(agent) + B(24 A1-A3) + C(72 GWPt/f/b + rep C/D) + T | 0 |
| Adbri per-stage — text cells (A4) | 3 | A(agent) + C + T | 0 |
| Adbri per-stage — image cells (A1-A3) | 3 | V ×2 (agent read + main-agent re-render) | 0 |
| **Total** | **~793** | **≥2 independent methods each** | **0** |

## Contextual fields
- 83 machine checks (strength MPa, valid-until year, manufacturer present in source text): all pass.
  Two initial regex misses (P252080 25 MPa, GE322LPF2 32 MPa) resolved by direct page
  inspection — values are printed on p20/p17 respectively.
- 9 files fully agent-audited (extraction agent + independent checker); errors found and
  fixed along the way: strength 40→25 MPa (P252080), C-modules taken from the wrong
  indicator table (Dry Creek), wrong valid-until (GreenCrete boilerplate date, ACM PCR
  date), garbage manufacturer/location strings (Boral/Tandy/Entire files, verified against
  p2/p3 of each source), Adbri A5/C/D reclassified `not_reported` (in scope, unpublished).

## Honesty invariants (machine-enforced, `schema.py` + `qa.py`)
- `not_declared` / `not_relevant` / `not_reported` cells must have `value: null` — a missing
  stage can never appear as 0.
- Declared cells must carry `raw` + `provenance.page`.
- A1+A2+A3 must reconcile with the A1-A3 aggregate where both are printed (2% tolerance).
- Boundary-vs-results contradictions are hard failures.

## Current gate status
`schema.py` 0 errors · `cross_validate.py` 0 problems · `qa.py` 0 issues 0 warnings ·
`verify_independent.py` 0 mismatches · `verify_teamC.py` 0 mismatches.
