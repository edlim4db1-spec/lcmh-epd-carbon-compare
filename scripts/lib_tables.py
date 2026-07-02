"""
Coordinate-based extraction of the GWP impact-results table from an EPD page.
We reconstruct columns from word x-positions so a value is bound to the correct
module even when the flattened text order is ambiguous (RISKS.md P4).
"""
import fitz
from lib_parse import MODULE_SET, classify_cell

GWP_ROW_LABELS = {
    "gwp-total": "GWP_total", "gwp – total": "GWP_total", "gwp-tot": "GWP_total",
    "gwp - total": "GWP_total", "gwp-fossil": "GWP_fossil", "gwp – fossil": "GWP_fossil",
    "gwp-fos": "GWP_fossil", "gwp-biogenic": "GWP_biogenic", "gwp – biogenic": "GWP_biogenic",
    "gwp-bio": "GWP_biogenic", "gwp-luluc": "GWP_luluc", "gwp – luluc": "GWP_luluc",
    "gwp-luc": "GWP_luluc", "gwp-ghg": "GWP_GHG",
    "global warming pot.": "GWP_total_CML", "global warming potential": "GWP_total_CML",
}
# order longest-first so "gwp-total" beats "gwp-tot", "gwp-fossil" beats "gwp-fos"
_GWP_LABELS_SORTED = sorted(GWP_ROW_LABELS.items(), key=lambda kv: -len(kv[0]))


def _words_by_line(page, y_tol=3.0):
    """Group words into visual lines by y; return list of (y, [words sorted by x])."""
    words = page.get_text("words")  # x0,y0,x1,y1,text,block,line,word
    lines = []
    for w in sorted(words, key=lambda w: (round(w[1], 1), w[0])):
        y = (w[1] + w[3]) / 2
        placed = False
        for ln in lines:
            if abs(ln["y"] - y) <= y_tol:
                ln["words"].append(w)
                ln["y"] = (ln["y"] * ln["n"] + y) / (ln["n"] + 1)
                ln["n"] += 1
                placed = True
                break
        if not placed:
            lines.append({"y": y, "n": 1, "words": [w]})
    for ln in lines:
        ln["words"].sort(key=lambda w: w[0])
    lines.sort(key=lambda ln: ln["y"])
    return lines


def find_module_header(lines):
    """Find the header line carrying module labels; return {module: x_center} + line y."""
    best = None
    for ln in lines:
        cols = {}
        for w in ln["words"]:
            t = w[4].strip()
            if t in MODULE_SET:
                cols[t] = (w[0] + w[2]) / 2
        # accept >=3 modules incl at least one anchor; supports tables split across pages
        # (Boral HUB: A1-A5 on one page, C1-D on the next)
        anchors = {"A1", "A1-A3", "C1", "C2", "A4"}
        if len(cols) >= 3 and (anchors & set(cols)):
            if best is None or len(cols) > len(best[0]):
                best = (cols, ln["y"])
    return best


def extract_gwp_tables(pdf_path):
    """
    Return list of row dicts:
      {indicator, page(1-based), unit_raw, section, cells:{module:{raw,value,status}}}
    One entry per GWP row found across the document.
    """
    doc = fitz.open(pdf_path)
    results = []
    for pno in range(doc.page_count):
        page = doc[pno]
        lines = _words_by_line(page)
        header = find_module_header(lines)
        if not header:
            continue
        cols, header_y = header
        col_items = sorted(cols.items(), key=lambda kv: kv[1])  # (module, xcenter) L->R
        xcenters = [x for _, x in col_items]
        modules = [m for m, _ in col_items]
        # tolerance = ~half the min gap between columns
        gaps = [xcenters[i + 1] - xcenters[i] for i in range(len(xcenters) - 1)]
        tol = (min(gaps) / 2.0) if gaps else 25.0
        # nearest section heading above the header (best-effort)
        section = ""
        for ln in lines:
            if ln["y"] < header_y:
                txt = " ".join(w[4] for w in ln["words"]).strip()
                if txt.isupper() and len(txt) > 8:
                    section = txt
        # scan rows below header for GWP labels
        for ln in lines:
            if ln["y"] <= header_y + 1:
                continue
            label = " ".join(w[4] for w in ln["words"]).strip()
            low = label.lower().replace("–", "-").replace("  ", " ")
            indicator = None
            for key, name in _GWP_LABELS_SORTED:
                k = key.replace("–", "-")
                if low.startswith(k):
                    indicator = name
                    break
            if not indicator:
                continue
            # These EPD tables are strictly ordered left->right. Take value cells in
            # positional order and zip with header modules in order. Robust to edge
            # columns and split tables; avoids nearest-x tolerance drops.
            value_words = [w for w in ln["words"] if _is_value_cell(w[4])]
            value_words.sort(key=lambda w: w[0])
            cells = {}
            mapping_ok = (len(value_words) == len(modules))
            if mapping_ok:
                for mod, w in zip(modules, value_words):
                    val, status, raw = classify_cell(w[4])
                    cells[mod] = {"raw": raw, "value": val, "status": status}
            else:
                # fall back to nearest-column so we still capture something, but flag it
                for w in value_words:
                    xc = (w[0] + w[2]) / 2
                    j = min(range(len(xcenters)), key=lambda k: abs(xcenters[k] - xc))
                    mod = modules[j]
                    if mod in cells:
                        continue
                    val, status, raw = classify_cell(w[4])
                    cells[mod] = {"raw": raw, "value": val, "status": status}
            unit_raw = _guess_unit(ln, xcenters[0])
            results.append({
                "indicator": indicator, "page": pno + 1, "unit_raw": unit_raw,
                "section": section, "n_module_cols": len(modules),
                "modules_in_header": modules, "cells": cells,
                "mapping_ok": mapping_ok, "n_values": len(value_words),
            })
    doc.close()
    return results


def _looks_valueish(t):
    t = t.strip()
    if t in ("ND", "NR", "MND", "NA", "MNR"):
        return True
    return any(c.isdigit() for c in t)


def _is_value_cell(t):
    """True only for real data cells: a number, declared-zero, or ND/NR status.
    Excludes labels, units ('kg','CO2e'), and footnote markers ('1)','2)')."""
    _, status, _ = classify_cell(t)
    return status in ("declared", "declared_zero", "not_declared", "not_relevant")


def _guess_unit(ln, first_col_x):
    """Unit sits between the label and the first data column."""
    parts = [w[4] for w in ln["words"] if (w[0] + w[2]) / 2 < first_col_x]
    txt = " ".join(parts)
    for u in ["kg CO2 eq", "kg CO2e", "kg CO₂e", "kg CO2-eq", "kg CO2 e"]:
        if u.lower().replace(" ", "") in txt.lower().replace(" ", ""):
            return u
    return ""


if __name__ == "__main__":
    import sys, json
    rows = extract_gwp_tables(sys.argv[1])
    for r in rows:
        print(f"\n[p{r['page']}] {r['indicator']}  ({r['unit_raw']})  cols={r['modules_in_header']}")
        for m in r["modules_in_header"]:
            c = r["cells"].get(m)
            if c:
                print(f"   {m:6s} {c['raw']:>12s} -> {c['value']!s:>10}  [{c['status']}]")
            else:
                print(f"   {m:6s} {'(no cell found)':>12s}")
