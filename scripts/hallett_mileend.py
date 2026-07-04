"""
Mile End plant — the hardest table (per docs/EPD_FIELD_GUIDE.md R3/R10/R13).
Sheet 19 (printed 36-37) reconciles exactly to 40 mixes via consume-known-variants order,
two-engine verified. Sheet 20 (S4020 16-variant E-series + CLSM/NO-FINES fill materials)
is documented in the inventory as the bounded remainder (value/variant counts not yet
reconciled without risk). Structural mixes only; fill materials flagged.
"""
import fitz, re, json, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from hallett_extend import lines_of, extract_densities, scale_cd, REP_DENSITY

ROOT = os.path.join(os.path.dirname(__file__), "..")
PDF = os.path.join(ROOT, "epds",
    "epd-australasia-com-wp-content-uploads-2023-08-epd-ies-0009353-003-hallett-ready-mix-concrete-2026-05-04-pdf.pdf")
CORR = os.path.join(ROOT, "extract_work", "corrections",
    "epd-australasia-com-wp-content-uploads-2023-08-epd-ies-0009353-003-hallett-ready-mix-concrete-2026-05-04-pdf.json")

ORDER = [("N2010P", "-"), ("N2010P", "100"),
    ("N2020P", "100"), ("N2020P", "120"), ("N2020P", "Ref"), ("N2020P", "F30"), ("N2020P", "S30"), ("N2020P", "S50"),
    ("N2520P", "Ref"), ("N2520P", "F30"), ("N2520P", "S30"), ("N2520P", "T50"), ("N2520P", "S50"),
    ("N3220P", "Ref"), ("N3220P", "F30"), ("N3220P", "S30"), ("N3220P", "T50"), ("N3220P", "S50"),
    ("N4020P", "Ref"), ("N4020P", "F30"), ("N4020P", "S30"), ("N4020P", "T50"), ("N4020P", "S50"),
    ("N5020P", "Ref"), ("N5020P", "F30"), ("N5020P", "S30"), ("N5020P", "T50"), ("N5020P", "S50"),
    ("S1020", "PLC1"), ("S1520", "PLC1120"), ("S1520", "PLC2120"), ("S2020P", "200"),
    ("S2520", "PLC1"), ("S2520", "E1100"),
    ("S3220", "PLC2"), ("S3220", "LSLC2"), ("S3220", "PLC2XYP"), ("S3220", "PLC2120"), ("S3220", "E1100"),
    ("S4010", "SCPH")]  # FIX: E1100 is an S3220 variant (Table 1), not S4010; S4010 has only SCPH
# Sheet 20 (printed 38-39) Table A CONT'D — reconciles exactly: S4020(16) + S5010(5) = 21.
ORDER_S20A = [("S4020", v) for v in ("E1100", "E1150H", "E2", "E2100", "E2120", "E2150", "E2150F",
    "E2200", "E3150", "E3150F", "PTLC2", "COLLC1", "COLLC2", "PLC1120", "PLC2120", "PLC2XYP")] + \
    [("S5010", v) for v in ("DW500D", "DW500D3", "E1150H", "SCPLC2", "SCPH")]
# Sheet 20 Table B (BOTTOM table on the same sheet, same +A2 CONT'D heading — must NOT be
# skipped). Structure from the source (visible family borders). CLSM / NO-FINES are
# non-structural FILL materials (R13): no MPa grade, distinct concrete_type.
ORDER_S20B = [("S5020", "E1200"), ("S5020", "METALDIT"), ("S6510", "SCPLC2"), ("S6510", "SCPEC2"),
    ("S6520", "PLC2120"), ("S6520", "E2150"), ("S8010", "COLSCLC2"), ("S8010", "SCPEC2"),
    ("CLSM", "PEB"), ("CLSM", "SB"), ("CLSM", "3"), ("CLSM", "4"), ("CLSM", "5"), ("CLSM", "15"),
    ("NO FINES", "-")]
GRADE_S20 = {"S4020": 40, "S5010": 50, "S5020": 50, "S6510": 65, "S6520": 65, "S8010": 80}
FILL_TYPE = {"CLSM": "Controlled low-strength material (CLSM / fill)", "NO FINES": "No-fines concrete"}
GRADE = {"N2010P": 20, "N2020P": 20, "N2520P": 25, "N3220P": 32, "N4020P": 40, "N5020P": 50,
         "S1020": 10, "S1520": 15, "S2020P": 20, "S2520": 25, "S3220": 32, "S4010": 40}


def gwp_rows_by_table(page):
    """Return {indicator: [[table-1 values], [table-2 values], ...]} — ONE list per table on
    the sheet (a sheet often holds multiple result tables under one heading; take them all)."""
    out = {"GWPt": [], "GWPf": [], "GWPb": []}
    for ln in lines_of(page):
        lab = ln["w"][0][4]
        if lab in out:
            out[lab].append([w[4] for w in ln["w"] if re.match(r"^-?\d+(\.\d+)?$", w[4])])
    return out


def main():
    write = "--write" in sys.argv
    doc = fitz.open(PDF)
    dens = extract_densities(doc)
    corr = json.load(open(CORR))
    corr["products"] = [p for p in corr["products"]
                        if (p.get("manufacturing_location") or {}).get("city") != "Mile End"]
    corr["needs_review"] = [n for n in corr.get("needs_review", []) if "Mile End sheet 20" not in n]
    rep = next(p for p in corr["products"] if p["indicators"]["GWP_total"]["modules"].get("C1", {}).get("value") is not None)
    rep_cd = {m: rep["indicators"]["GWP_total"]["modules"][m] for m in ("C1", "C2", "C3", "C4", "D")}

    # Sheet 19: two tables (23 + 17) -> concat = ORDER(40). Sheet 20: two tables (21 + 15).
    s19 = gwp_rows_by_table(doc[18])
    s20 = gwp_rows_by_table(doc[19])
    # RULE (R15): every table on a sheet must be consumed. Assert value count == mapped keys.
    assert sum(len(t) for t in s19["GWPt"]) == len(ORDER), "sheet19 GWPt count != ORDER"
    assert len(s20["GWPt"][0]) == len(ORDER_S20A) and len(s20["GWPt"][1]) == len(ORDER_S20B), \
        f"sheet20 tables {[len(t) for t in s20['GWPt']]} != {len(ORDER_S20A)}+{len(ORDER_S20B)}"

    def build(order, rows_by_ind, sheet, printed, grade_map):
        for i, (fam, var) in enumerate(order):
            dv = dens.get((fam, var))
            g = grade_map.get(fam)
            ctype = FILL_TYPE.get(fam, "Ready-mix concrete")
            prod = {
                "name": f"{fam} {var}".rstrip(" -"), "manufacturer": rep["manufacturer"], "concrete_type": ctype,
                "compressive_strength": {"value_mpa": g, "class": fam, "at_days": 28,
                    "raw": (str(g) if g else None), "status": ("found" if g else "uncertain"),
                    "provenance": {"page": 5, "snippet": (f"Table 1 grades ... {fam} ... {g}" if g
                                   else f"{fam} is non-structural fill — no MPa grade")}},
                "manufacturing_location": {"site": "Mile End batch plant", "city": "Mile End", "region": "South Australia",
                    "country": "AU", "raw": "Mile End, SA", "provenance": {"page": sheet, "snippet": f"MILE END | A1-A3 (printed {printed})"}},
                "declared_unit": {"amount": 1, "unit": "m3", "description": "1 m3 of product produced at Mile End batch plant",
                    "mass_kg": int(dv) if dv else None, "provenance": {"page": 5, "snippet": "Table 1 density"}},
                "indicators": {},
            }
            for ind, key in (("GWP_total", "GWPt"), ("GWP_fossil", "GWPf"), ("GWP_biogenic", "GWPb")):
                raw = rows_by_ind[key][i]
                prod["indicators"][ind] = {"unit_raw": "kg CO2-eq", "unit_normalised": "kg CO2e",
                    "modules": {"A1-A3": {"value": float(raw), "raw": raw, "status": "declared",
                        "provenance": {"page": sheet, "section": f"CORE ENVIRONMENTAL IMPACT INDICATORS | EN15804+A2 | MILE END | A1-A3 (printed {printed})",
                            "module": "A1-A3", "unit_raw": "kg CO2-eq"}}}}
            if dv:
                prod["indicators"]["GWP_total"]["modules"].update(scale_cd({k: rep_cd[k] for k in rep_cd}, dv / REP_DENSITY, sheet, f"density {int(dv)}"))
            corr["products"].append(prod)

    before = len(corr["products"])
    build(ORDER, {k: s19[k][0] + s19[k][1] for k in s19}, 19, "36-37", GRADE)         # sheet 19 both tables
    build(ORDER_S20A, {k: s20[k][0] for k in s20}, 20, "38-39", GRADE_S20)            # sheet 20 top
    build(ORDER_S20B, {k: s20[k][1] for k in s20}, 20, "38-39", GRADE_S20)            # sheet 20 bottom (FIX)
    added = len(corr["products"]) - before
    doc.close()
    print(f"added {added} Mile End products (sheet19 x2 + sheet20 x2 tables); total {len(corr['products'])}")
    if write:
        json.dump(corr, open(CORR, "w"), indent=2, ensure_ascii=False)
        print("WROTE.")


if __name__ == "__main__":
    main()
