"""
INDEPENDENT second extraction ("Team B") + cell-by-cell diff against /data ("Team A").

Team A extracted GWP numbers with PyMuPDF word coordinates. This script re-extracts
GWP-total/fossil/biogenic per module using a COMPLETELY different engine and method:
pdfplumber's table detection + per-line regex scanning. The two must agree on every
comparable cell. Any disagreement is a hard failure to investigate by eye.

This is deliberately independent: different library, different table logic, different
number normalisation code path.
"""
import re, json, os, glob, sys
import pdfplumber

ROOT = os.path.join(os.path.dirname(__file__), "..")
DATA = os.path.join(ROOT, "data")
EPDS = os.path.join(ROOT, "epds")

MODS = ["A1", "A2", "A3", "A1-A3", "A4", "A5", "B1", "B2", "B3", "B4", "B5", "B6", "B7",
        "C1", "C2", "C3", "C4", "D"]

NUMTOK = re.compile(r"^[-‐‑‒–−+]?\d+(?:[.,]\d+)?(?:[eE][-‐‑‒–−+]?\d+)?$")
STATTOK = {"ND", "NR", "MND", "MNR"}


def tonum(tok):
    t = tok
    for m in "‐‑‒–−":
        t = t.replace(m, "-")
    t = t.replace(",", ".")
    try:
        return float(t)
    except ValueError:
        return None


def row_values(line_tokens):
    """Return the ordered value tokens (numbers or ND/NR) from a token list."""
    out = []
    for t in line_tokens:
        t = t.strip()
        if not t:
            continue
        if t in STATTOK:
            out.append(("status", t))
        elif NUMTOK.match(t):
            out.append(("num", t))
    return out


LABELS = {
    "GWP_total": [r"^GWP\s*[-–]\s*total", r"^GWP-tot\b", r"^GWPt\b"],
    "GWP_fossil": [r"^GWP\s*[-–]\s*fossil", r"^GWP-fos\b"],
    "GWP_biogenic": [r"^GWP\s*[-–]\s*biogenic", r"^GWP-bio\b"],
}


def indicator_for(line):
    for name, pats in LABELS.items():
        for p in pats:
            if re.search(p, line, re.I):
                return name
    return None


def header_modules(lines, idx, back=12):
    """Look upward from a GWP row for the most recent module header sequence."""
    for j in range(idx - 1, max(-1, idx - back) - 1, -1):
        toks = lines[j].split()
        mods = [t for t in toks if t in MODS]
        if len(mods) >= 3:
            return mods
    return None


def extract_pdf(path):
    """Team B extraction: {indicator: {module: value}} + free-standing ND statuses."""
    found = {}
    with pdfplumber.open(path) as pdf:
        for pno, page in enumerate(pdf.pages, start=1):
            txt = page.extract_text() or ""
            if "GWP" not in txt:
                continue
            lines = txt.split("\n")
            for i, line in enumerate(lines):
                ind = indicator_for(line.strip())
                if not ind:
                    continue
                vals = row_values(line.replace(indicator_get_label(line), "", 1).split())
                mods = header_modules(lines, i)
                if not mods or not vals:
                    continue
                if len(vals) != len(mods):
                    # tolerate unit token stuck to row: try dropping leading non-numeric noise
                    if len(vals) == len(mods) + 1:
                        vals = vals[1:]
                    else:
                        continue
                d = found.setdefault(ind, {})
                for m, (kind, tok) in zip(mods, vals):
                    if m in d:
                        continue
                    d[m] = tok if kind == "status" else tonum(tok)
    return found


def indicator_get_label(line):
    # strip the label portion before values begin (first numeric/status token)
    toks = line.split()
    keep = []
    for t in toks:
        if NUMTOK.match(t) or t in STATTOK:
            break
        keep.append(t)
    return " ".join(keep)


def compare(file_json, teamB):
    d = json.load(open(file_json))
    diffs, agrees, uncovered = [], 0, 0
    for prod in d["products"]:
        for ind_name in ("GWP_total", "GWP_fossil", "GWP_biogenic"):
            ind = prod.get("indicators", {}).get(ind_name)
            if not ind:
                continue
            b = teamB.get(ind_name, {})
            for m, cell in ind.get("modules", {}).items():
                a_status = cell.get("status")
                a_val = cell.get("value")
                if m not in b:
                    # Team B didn't capture this cell (template it can't read) -> uncovered
                    if a_status in ("declared", "declared_zero"):
                        uncovered += 1
                    continue
                bv = b[m]
                if a_status in ("not_declared", "not_relevant"):
                    if isinstance(bv, str):  # B also saw ND/NR
                        agrees += 1
                    elif bv is None:
                        agrees += 1
                    else:
                        diffs.append(f"{ind_name}.{m}: A says {a_status}, B read value {bv}")
                elif a_status in ("declared", "declared_zero"):
                    if isinstance(bv, str):
                        diffs.append(f"{ind_name}.{m}: A={a_val}, B saw status {bv}")
                    elif bv is None:
                        uncovered += 1
                    else:
                        if a_val == 0 and bv == 0:
                            agrees += 1
                        elif a_val is not None and abs(bv - a_val) <= abs(a_val) * 1e-6 + 1e-9:
                            agrees += 1
                        else:
                            diffs.append(f"{ind_name}.{m}: A={a_val} vs B={bv}  MISMATCH")
    return agrees, uncovered, diffs


def main():
    total_a = total_u = total_d = 0
    rows = []
    for jf in sorted(glob.glob(os.path.join(DATA, "*.json"))):
        base = os.path.basename(jf).replace(".json", "")
        pdf = os.path.join(EPDS, base + ".pdf")
        if not os.path.exists(pdf):
            print("missing pdf for", base)
            continue
        teamB = extract_pdf(pdf)
        agrees, uncov, diffs = compare(jf, teamB)
        total_a += agrees; total_u += uncov; total_d += len(diffs)
        tag = "OK " if not diffs else "!!!"
        rows.append((tag, base, agrees, uncov, diffs))
        print(f"{tag} {base[:58]:58s} agree={agrees:3d} uncovered={uncov:2d} mismatches={len(diffs)}")
        for x in diffs:
            print("      -", x)
    print(f"\n===== TOTAL: {total_a} cells agree, {total_u} uncovered by Team B, {total_d} MISMATCHES =====")
    sys.exit(1 if total_d else 0)


if __name__ == "__main__":
    main()
