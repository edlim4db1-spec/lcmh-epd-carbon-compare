"""
Detect PRINTED page labels per physical PDF sheet, for dual citation (RISKS.md V1).

Some documents (Hallett/Dry Creek) are booklet spreads: one PDF sheet carries two
printed folios ("20" bottom-left, "21" top-right on physical sheet 11). Links must
target physical sheets (#page=N), but citations should also show the printed folio.

Strategy: collect standalone small integers near the sheet corners/edges, then fit a
DOCUMENT-LEVEL pattern (identity / spread formula) rather than trusting noisy
per-page hits. Only documents with a confidently-fitted non-identity pattern get a
physical->printed map; everything else keeps plain physical citations.
Output: extract_work/page_labels_map.json  {source_pdf: {physical_page_str: "label"}}
"""
import fitz, glob, os, json, re

ROOT = os.path.join(os.path.dirname(__file__), "..")
EPDS = os.path.join(ROOT, "epds")
OUT = os.path.join(ROOT, "extract_work", "page_labels_map.json")

EDGE = 90  # pt band from page edges considered "corner/footer/header"
# (Hallett's A3 spread prints its top folio at y=52 — a 50pt band missed it.)


def corner_numbers(page):
    """Standalone 1-3 digit integers in the edge bands of a page."""
    W, H = page.rect.width, page.rect.height
    nums = set()
    for x0, y0, x1, y1, txt, *_ in page.get_text("words"):
        t = txt.strip()
        if not re.fullmatch(r"\d{1,3}", t):
            continue
        v = int(t)
        if not (1 <= v <= 400):
            continue
        in_band = (y0 < EDGE) or (y1 > H - EDGE)
        if in_band:
            nums.add(v)
    return nums


def fit_patterns(per_page):
    """per_page: {physical(1-based): set(ints)} ->
    ('identity'|'spread'|('offset', k)|None, details)"""
    from collections import Counter
    id_hits = spread_hits = scorable = 0
    offsets = Counter()
    for p, nums in per_page.items():
        if not nums:
            continue
        scorable += 1
        if p in nums:
            id_hits += 1
        if p >= 2 and (2 * p - 2 in nums or 2 * p - 1 in nums):
            spread_hits += 1
        for v in nums:
            offsets[p - v] += 1
    if scorable == 0:
        return None, "no corner numbers found"
    id_score = id_hits / scorable
    spread_score = spread_hits / scorable
    best_off, off_hits = (offsets.most_common(1)[0] if offsets else (0, 0))
    off_score = off_hits / scorable
    detail = f"id={id_score:.2f} spread={spread_score:.2f} offset({best_off})={off_score:.2f} ({scorable} scorable)"
    if id_score >= 0.5 and id_score >= spread_score:
        return "identity", detail
    if spread_score >= 0.5:
        return "spread", detail
    if off_score >= 0.5 and best_off != 0:
        return ("offset", best_off), detail
    return None, detail


def main():
    result = {}
    for pdf in sorted(glob.glob(os.path.join(EPDS, "*.pdf"))):
        doc = fitz.open(pdf)
        per_page = {i + 1: corner_numbers(doc[i]) for i in range(doc.page_count)}
        pattern, note = fit_patterns(per_page)
        base = os.path.basename(pdf)
        if pattern == "spread":
            # formula-based map for every sheet after the cover
            labels = {str(p): f"{2*p-2}–{2*p-1}" for p in range(2, doc.page_count + 1)}
            result[base] = labels
        elif isinstance(pattern, tuple) and pattern[0] == "offset":
            k = pattern[1]
            labels = {str(p): str(p - k) for p in range(k + 1, doc.page_count + 1)}
            result[base] = labels
        tag = pattern if isinstance(pattern, str) else (f"offset{pattern[1]:+d}" if pattern else "none")
        print(f"{tag:9s} {base[:58]:58s} {note}")
        doc.close()
    with open(OUT, "w") as f:
        json.dump(result, f, indent=1)
    print(f"\nwrote {OUT}: {len(result)} document(s) need printed-page maps")


if __name__ == "__main__":
    main()
