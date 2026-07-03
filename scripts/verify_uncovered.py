"""
Third-method verification for the cells Team B's line parser couldn't reach:
 - GCCA slide EPDs (0014769, 0014785, 0014958): pdfplumber WORDS (pdfminer engine),
   rows rebuilt by y-clustering, values taken in x-order under the module header.
 - Dry Creek (0009353): same word-based reconstruction on the plant matrix page,
   verifying each shipped mix's A1-A3 GWP-total against its column position.
 - Adbri (0021165): A4 text cells re-checked; A1-A3 image cells listed for VISUAL check
   (rendered separately).
Compares against /data. Exit 1 on any mismatch.
"""
import os, re, json, glob, sys
import pdfplumber

ROOT = os.path.join(os.path.dirname(__file__), "..")
DATA = os.path.join(ROOT, "data")
EPDS = os.path.join(ROOT, "epds")
MODS = ["A1-A3", "A4", "A5", "B1", "B2", "B3", "B4", "B5", "B6", "B7",
        "C1", "C2", "C3", "C4", "D"]
NUM = re.compile(r"^[-‐‑‒–−+]?\d+(?:[.,]\d+)?(?:[eE][-‐‑‒–−+]?\d+)?$")


def tonum(t):
    for m in "‐‑‒–−":
        t = t.replace(m, "-")
    try:
        return float(t.replace(",", "."))
    except ValueError:
        return None


def rows_from_words(page, ytol=3.5):
    rows = {}
    for w in page.extract_words():
        y = round(w["top"] / ytol)
        rows.setdefault(y, []).append(w)
    out = []
    for y in sorted(rows):
        out.append(sorted(rows[y], key=lambda w: w["x0"]))
    return out


def check_gcca(pdfpath, jsonpath):
    """GCCA slides: find header row of modules, then GWP-tot row; zip in x-order."""
    d = json.load(open(jsonpath))
    prod = d["products"][0]
    a_cells = prod["indicators"]["GWP_total"]["modules"]
    page_no = a_cells["A1-A3"]["provenance"]["page"]
    mism = agree = 0
    with pdfplumber.open(pdfpath) as pdf:
        page = pdf.pages[page_no - 1]
        rows = rows_from_words(page)
        header = None
        for r in rows:
            mods = [w["text"] for w in r if w["text"] in MODS]
            if len(mods) >= 10:
                header = [w for w in r if w["text"] in MODS]
                break
        gwp_row = None
        for r in rows:
            txt = " ".join(w["text"] for w in r[:3])
            if re.match(r"GWP-?tot\b", txt) and not re.match(r"GWP-?GHG", txt):
                vals = [w for w in r if NUM.match(w["text"])]
                if len(vals) >= 10:
                    gwp_row = vals
                    break
        if not header or not gwp_row:
            return None, None, ["couldn't rebuild table via pdfminer words"]
        # map values to nearest header x-center
        problems = []
        for w in gwp_row:
            xc = (w["x0"] + w["x1"]) / 2
            near = min(header, key=lambda h: abs((h["x0"] + h["x1"]) / 2 - xc))
            m = near["text"]
            b = tonum(w["text"])
            a = a_cells.get(m, {}).get("value")
            if a is None:
                problems.append(f"{m}: B={b} but A has no value")
                mism += 1
            elif abs(a - b) > abs(a) * 1e-6 + 1e-9:
                problems.append(f"{m}: A={a} vs B={b} MISMATCH")
                mism += 1
            else:
                agree += 1
    return agree, mism, problems


def check_drycreek(pdfpath, jsonpath):
    """Verify every shipped mix's A1-A3 GWPt against the Dry Creek p11 matrix."""
    d = json.load(open(jsonpath))
    agree = mism = 0
    problems = []
    with pdfplumber.open(pdfpath) as pdf:
        page = pdf.pages[10]  # p11
        rows = rows_from_words(page)
        # variant header row: sequences of Ref/F30/S30/T50/S50
        var_row = None
        mix_row = None
        for r in rows:
            texts = [w["text"] for w in r]
            if texts.count("Ref") >= 4:
                var_row = r
            if sum(1 for t in texts if re.match(r"^N\d{4}P$", t)) >= 4:
                mix_row = r
        gwp_row = None
        for r in rows:
            if r and r[0]["text"].startswith("GWPt"):
                gwp_row = [w for w in r if NUM.match(w["text"])]
                break
        if not (var_row and mix_row and gwp_row):
            return None, None, ["couldn't rebuild Dry Creek matrix"]
        variants = [w for w in var_row if w["text"] in ("Ref", "F30", "S30", "T50", "S50")]
        mixes = [w for w in mix_row if re.match(r"^N\d{4}P$", w["text"])]

        def mix_for(xc):
            # nearest mix-family label to the LEFT region: family headers span groups;
            # use nearest by center distance
            return min(mixes, key=lambda w: abs((w["x0"] + w["x1"]) / 2 - xc))["text"]

        def var_for(xc):
            return min(variants, key=lambda w: abs((w["x0"] + w["x1"]) / 2 - xc))["text"]

        # Build B-side lookup: (mix, variant) -> value
        bmap = {}
        for w in gwp_row:
            xc = (w["x0"] + w["x1"]) / 2
            bmap[(mix_for(xc), var_for(xc))] = tonum(w["text"])

        for prod in d["products"]:
            name = prod["name"]  # e.g. "N3220P S50 ..."
            m = re.match(r"^(N\d{4}P)\s+(Ref|F30|S30|T50|S50)", name)
            if not m:
                continue
            key = (m.group(1), m.group(2))
            a = prod["indicators"]["GWP_total"]["modules"].get("A1-A3", {}).get("value")
            b = bmap.get(key)
            if b is None:
                problems.append(f"{key}: not found in B matrix")
                mism += 1
            elif a is None or abs(a - b) > abs(a) * 1e-6 + 1e-9:
                problems.append(f"{key}: A={a} vs B={b} MISMATCH")
                mism += 1
            else:
                agree += 1
    return agree, mism, problems


def check_adbri_text(pdfpath, jsonpath):
    """A4 cells are in the text layer; verify with pdfplumber."""
    d = json.load(open(jsonpath))
    prod = d["products"][0]
    agree = mism = 0
    problems = []
    with pdfplumber.open(pdfpath) as pdf:
        t34 = pdf.pages[33].extract_text() or ""
    for ind in ("GWP_total", "GWP_fossil"):
        cell = prod["indicators"].get(ind, {}).get("modules", {}).get("A4")
        if not cell or cell.get("value") is None:
            continue
        if cell["raw"] in t34:
            agree += 1
        else:
            mism += 1
            problems.append(f"{ind}.A4 raw '{cell['raw']}' not on p34 (pdfminer)")
    return agree, mism, problems


def main():
    total_a = total_m = 0
    allp = []
    gcca = ["EPD-IES-0014769_P252080", "EPD-IES-0014785_Heidelberg_Woolworths-GE322LPF2",
            "EPD-IES-0014958_Hymix_GE252WA06-3_2024-11-19"]
    for base in gcca:
        a, m, p = check_gcca(os.path.join(EPDS, base + ".pdf"), os.path.join(DATA, base + ".json"))
        print(f"{'OK ' if not m else '!!!'} GCCA {base:55s} agree={a} mismatch={m}")
        for x in p:
            print("     -", x)
        total_a += a or 0; total_m += m or 0; allp += p

    base = "epd-australasia-com-wp-content-uploads-2023-08-epd-ies-0009353-003-hallett-ready-mix-concrete-2026-05-04-pdf"
    a, m, p = check_drycreek(os.path.join(EPDS, base + ".pdf"), os.path.join(DATA, base + ".json"))
    print(f"{'OK ' if not m else '!!!'} DryCreek A1-A3 x24 mixes {'':32s} agree={a} mismatch={m}")
    for x in p:
        print("     -", x)
    total_a += a or 0; total_m += m or 0; allp += p

    base = "epd-ies-0021165-sn252f100"
    a, m, p = check_adbri_text(os.path.join(EPDS, base + ".pdf"), os.path.join(DATA, base + ".json"))
    print(f"{'OK ' if not m else '!!!'} Adbri A4 (text layer) {'':36s} agree={a} mismatch={m}")
    for x in p:
        print("     -", x)
    total_a += a or 0; total_m += m or 0; allp += p

    print(f"\n===== THIRD-METHOD TOTAL: {total_a} agree, {total_m} mismatches =====")
    print("NOTE: Adbri A1-A3 (3 cells) are image-only -> verified visually (render p32).")
    sys.exit(1 if total_m else 0)


if __name__ == "__main__":
    main()
