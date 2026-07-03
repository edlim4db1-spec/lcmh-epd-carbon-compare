"""
Team C verification (pypdf engine — independent of PyMuPDF and pdfminer) for the files
Team B couldn't decode:
 - 3 GCCA slide EPDs: verify GWP-tot / GWP-fos / GWP-bio rows (15 modules each).
 - Dry Creek: verify GWPt+GWPf+GWPb A1-A3 for all 24 shipped mixes (p11 matrix rows) and
   the representative mix's C1-C4 + D (p35).
 - Adbri: verify A4 cells (p34 text).
Every stored declared cell in these files must be matched. Exit 1 on any mismatch.
"""
import os, re, json, sys
from pypdf import PdfReader

ROOT = os.path.join(os.path.dirname(__file__), "..")
DATA = os.path.join(ROOT, "data")
EPDS = os.path.join(ROOT, "epds")
GCCA_MODS = ["A1-A3", "A4", "A5", "B1", "B2", "B3", "B4", "B5", "B6", "B7",
             "C1", "C2", "C3", "C4", "D"]
SCI = re.compile(r"[-‐‑‒–−]?\d+\.\d+E[+-]\d+")


def norm_minus(s):
    for m in "‐‑‒–−":
        s = s.replace(m, "-")
    return s


def check_gcca(base, row_labels):
    jf = json.load(open(os.path.join(DATA, base + ".json")))
    prod = jf["products"][0]
    page_no = prod["indicators"]["GWP_total"]["modules"]["A1-A3"]["provenance"]["page"]
    r = PdfReader(os.path.join(EPDS, base + ".pdf"))
    t = norm_minus(r.pages[page_no - 1].extract_text() or "")
    agree = mism = 0
    problems = []
    for label, ind_name in row_labels.items():
        m = re.search(re.escape(label) + r"\s+kg CO₂ eq\.\s+((?:[-]?\d+\.\d+E[+-]\d+\s*){15})", t)
        if not m:
            problems.append(f"{ind_name}: row '{label}' not found via pypdf")
            mism += 1
            continue
        vals = [float(x) for x in SCI.findall(m.group(1))]
        cells = jf["products"][0]["indicators"].get(ind_name, {}).get("modules", {})
        for mod, b in zip(GCCA_MODS, vals):
            a = cells.get(mod, {}).get("value")
            if a is None and cells.get(mod, {}).get("status") == "declared_zero":
                a = 0.0
            if a is None:
                problems.append(f"{ind_name}.{mod}: B={b}, A missing")
                mism += 1
            elif abs(a - b) > abs(a) * 1e-6 + 1e-9:
                problems.append(f"{ind_name}.{mod}: A={a} vs B={b} MISMATCH")
                mism += 1
            else:
                agree += 1
    return agree, mism, problems


def check_drycreek():
    base = ("epd-australasia-com-wp-content-uploads-2023-08-epd-ies-0009353-003-"
            "hallett-ready-mix-concrete-2026-05-04-pdf")
    jf = json.load(open(os.path.join(DATA, base + ".json")))
    r = PdfReader(os.path.join(EPDS, base + ".pdf"))
    t11 = norm_minus(r.pages[10].extract_text() or "")
    agree = mism = 0
    problems = []
    # p11 rows: 'GWPt kg CO2 eq. <25 values>' etc. 25 columns = 5 families x 5 variants,
    # but N2020P family has only 4 variants -> actually 24 shipped. Parse the three rows.
    rows = {}
    for lab, ind in (("GWPt", "GWP_total"), ("GWPf", "GWP_fossil"), ("GWPb", "GWP_biogenic")):
        m = re.search(lab + r"\s+kg CO2\s*(?:eq\.?|eq)\s+((?:[-]?\d+\.?\d*E?[+-]?\d*\s+){20,30})", t11)
        if not m:
            # numbers may be plain decimals not sci notation on this page
            m = re.search(lab + r"[^\n]*?((?:\s+[-]?\d+(?:\.\d+)?(?:E[+-]\d+)?){20,30})", t11)
        if not m:
            problems.append(f"{ind}: row {lab} not found on p11 via pypdf")
            mism += 1
            continue
        toks = re.findall(r"[-]?\d+(?:\.\d+)?(?:E[+-]\d+)?", m.group(1))
        rows[ind] = [float(x) for x in toks]

    # column order on p11 (from the agent's verified mapping): N2020P Ref,F30,S30,S50;
    # then N2520P/N3220P/N4020P/N5020P each Ref,F30,S30,T50,S50 = 4+20 = 24 columns.
    order = [("N2020P", v) for v in ("Ref", "F30", "S30", "S50")]
    for fam in ("N2520P", "N3220P", "N4020P", "N5020P"):
        order += [(fam, v) for v in ("Ref", "F30", "S30", "T50", "S50")]

    byname = {}
    for p in jf["products"]:
        m = re.match(r"^(N\d{4}P)\s+(Ref|F30|S30|T50|S50)", p["name"])
        if m:
            byname[(m.group(1), m.group(2))] = p

    for ind, vals in rows.items():
        if len(vals) != len(order):
            problems.append(f"{ind}: p11 row has {len(vals)} values, expected {len(order)}")
            mism += 1
            continue
        for key, b in zip(order, vals):
            p = byname.get(key)
            if not p:
                continue
            a = p["indicators"].get(ind, {}).get("modules", {}).get("A1-A3", {}).get("value")
            if a is None:
                problems.append(f"{ind} {key}: A missing, B={b}")
                mism += 1
            elif abs(a - b) > abs(a) * 5e-3 + 1e-9:  # matrix prints 3 s.f.
                problems.append(f"{ind} {key}: A={a} vs B={b} MISMATCH")
                mism += 1
            else:
                agree += 1

    # representative mix C1-C4 + D on p35
    t35 = norm_minus(r.pages[34].extract_text() or "")
    rep = next((p for p in jf["products"] if "representative" in p["name"].lower()
                or (p["indicators"]["GWP_total"]["modules"].get("C1", {}).get("value") is not None)), None)
    if rep:
        for mod in ("C1", "C2", "C3", "C4", "D"):
            cell = rep["indicators"]["GWP_total"]["modules"].get(mod, {})
            if cell.get("value") is None:
                continue
            if cell["raw"] and norm_minus(cell["raw"]) in t35:
                agree += 1
            else:
                problems.append(f"rep-mix {mod}: raw '{cell.get('raw')}' not on p35 via pypdf")
                mism += 1
    return agree, mism, problems


def check_adbri():
    base = "epd-ies-0021165-sn252f100"
    jf = json.load(open(os.path.join(DATA, base + ".json")))
    prod = jf["products"][0]
    r = PdfReader(os.path.join(EPDS, base + ".pdf"))
    t34 = norm_minus(r.pages[33].extract_text() or "")
    agree = mism = 0
    problems = []
    for ind in ("GWP_total", "GWP_fossil", "GWP_biogenic"):
        cell = prod["indicators"].get(ind, {}).get("modules", {}).get("A4")
        if not cell or cell.get("value") is None:
            continue
        if cell["raw"] and norm_minus(cell["raw"]) in t34:
            agree += 1
        else:
            problems.append(f"{ind}.A4 raw '{cell.get('raw')}' not on p34 via pypdf")
            mism += 1
    return agree, mism, problems


def main():
    ta = tm = 0
    for base in ("EPD-IES-0014769_P252080",
                 "EPD-IES-0014785_Heidelberg_Woolworths-GE322LPF2",
                 "EPD-IES-0014958_Hymix_GE252WA06-3_2024-11-19"):
        a, m, p = check_gcca(base, {"GWP-tot": "GWP_total", "GWP-fos": "GWP_fossil",
                                    "GWP-bio": "GWP_biogenic"})
        print(f"{'OK ' if not m else '!!!'} GCCA {base[:52]:52s} agree={a} mismatch={m}")
        for x in p:
            print("     -", x)
        ta += a; tm += m
    a, m, p = check_drycreek()
    print(f"{'OK ' if not m else '!!!'} DryCreek (GWPt/f/b x mixes + rep C/D) {'':18s} agree={a} mismatch={m}")
    for x in p:
        print("     -", x)
    ta += a; tm += m
    a, m, p = check_adbri()
    print(f"{'OK ' if not m else '!!!'} Adbri A4 {'':48s} agree={a} mismatch={m}")
    for x in p:
        print("     -", x)
    ta += a; tm += m
    print(f"\n===== TEAM C TOTAL: {ta} agree, {tm} mismatches =====")
    sys.exit(1 if tm else 0)


if __name__ == "__main__":
    main()
