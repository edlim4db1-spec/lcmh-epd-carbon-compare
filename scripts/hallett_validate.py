"""
Mitigation for family->variant mislabels (the S3220/E1100 class of bug).
Builds the authoritative mix registry from Table 1 (page 5) — {family: set(variants)} — and
checks every Hallett product's (family, variant) against it. Any product whose (family,variant)
is not a real Table-1 mix is flagged as a likely column-mapping error.
Run after any Hallett extraction; wire into qa if desired.
"""
import fitz, re, json, os, sys

ROOT = os.path.join(os.path.dirname(__file__), "..")
PDF = os.path.join(ROOT, "epds",
    "epd-australasia-com-wp-content-uploads-2023-08-epd-ies-0009353-003-hallett-ready-mix-concrete-2026-05-04-pdf.pdf")
DATA = os.path.join(ROOT, "data",
    "epd-australasia-com-wp-content-uploads-2023-08-epd-ies-0009353-003-hallett-ready-mix-concrete-2026-05-04-pdf.json")

VARTOK = re.compile(r'^(PLC\d+|LSLC\d+|PLC\dXYP|PTLC\d+|COLLC\d+|SCPLC\d+|SCPEC\d+|LC\d+|'
                    r'COLSCLC\d+|SCPH|METALDIT|DW\d+[A-Z]?\d?|E\d+[A-Z]?|Ref|F30|S30|T50|S50|100|120|200|-)$')
FAMTOK = re.compile(r'^([NS]\d{4})P?$')


def registry():
    """{family: set(variant)} from Table 1 raw-text reading order (page 5)."""
    toks = re.split(r'\s+', fitz.open(PDF)[4].get_text())
    reg, fam = {}, None
    for i, t in enumerate(toks):
        fm = FAMTOK.match(t)
        if fm:
            fam = fm.group(1) + ("P" if t.endswith("P") else "")
        elif fam and VARTOK.match(t):
            # a real mix row is followed by a density (2xxx) within a few tokens
            if any(re.fullmatch(r'2\d{3}', toks[j]) or (toks[j] == '2' and re.fullmatch(r'\d{3}', toks[j+1]))
                   for j in range(i+1, min(i+4, len(toks)-1))):
                reg.setdefault(fam, set()).add(t)
    return reg


def main():
    reg = registry()
    print("Table-1 registry (family: variants):")
    for f in sorted(reg):
        print(f"  {f}: {sorted(reg[f])}")
    d = json.load(open(DATA))
    problems = []
    for p in d["products"]:
        m = re.match(r'^([NS]\d{4}P?)\s+(\S+)', p["name"])
        if not m:
            continue
        fam, var = m.group(1), m.group(2)
        base = fam[:-1] if fam.endswith("P") else fam
        key = base + ("P" if fam.endswith("P") else "")
        if var not in reg.get(key, set()) and var not in reg.get(fam, set()):
            problems.append(f"{p['name']}  ({p['manufacturing_location'].get('city')}) — variant '{var}' not in Table-1 {fam} {sorted(reg.get(fam,set()) or reg.get(key,set()))}")
    print(f"\n{len(problems)} mislabel(s):")
    for pr in problems:
        print("  ✗", pr)
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
