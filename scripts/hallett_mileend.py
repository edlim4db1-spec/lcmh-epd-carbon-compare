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
    ("S3220", "PLC2"), ("S3220", "LSLC2"), ("S3220", "PLC2XYP"), ("S3220", "PLC2120"),
    ("S4010", "E1100"), ("S4010", "SCPH")]
GRADE = {"N2010P": 20, "N2020P": 20, "N2520P": 25, "N3220P": 32, "N4020P": 40, "N5020P": 50,
         "S1020": 10, "S1520": 15, "S2020P": 20, "S2520": 25, "S3220": 32, "S4010": 40}


def gwp_rows(page):
    rows = {"GWPt": [], "GWPf": [], "GWPb": []}
    for ln in lines_of(page):
        lab = ln["w"][0][4]
        if lab in rows:
            rows[lab] += [w[4] for w in ln["w"] if re.match(r"^-?\d+(\.\d+)?$", w[4])]
    return rows


def main():
    write = "--write" in sys.argv
    doc = fitz.open(PDF)
    r = gwp_rows(doc[18])
    dens = extract_densities(doc)
    for k in r:
        assert len(r[k]) == len(ORDER), f"{k}: {len(r[k])} != {len(ORDER)}"
    corr = json.load(open(CORR))
    rep = next(p for p in corr["products"] if p["indicators"]["GWP_total"]["modules"].get("C1", {}).get("value") is not None)
    rep_cd = {m: rep["indicators"]["GWP_total"]["modules"][m] for m in ("C1", "C2", "C3", "C4", "D")}
    import copy
    added = 0
    for i, (fam, var) in enumerate(ORDER):
        dv = dens.get((fam, var))
        prod = {
            "name": f"{fam} {var}", "manufacturer": rep["manufacturer"], "concrete_type": "Ready-mix concrete",
            "compressive_strength": {"value_mpa": GRADE[fam], "class": fam, "at_days": 28, "raw": str(GRADE[fam]),
                "status": "found", "provenance": {"page": 5, "snippet": f"Table 1 grades ... {fam} ... {GRADE[fam]}"}},
            "manufacturing_location": {"site": "Mile End batch plant", "city": "Mile End", "region": "South Australia",
                "country": "AU", "raw": "Mile End, SA", "provenance": {"page": 19, "snippet": "MILE END | A1-A3 (printed 36-37)"}},
            "declared_unit": {"amount": 1, "unit": "m3", "description": "1 m3 of product produced at Mile End batch plant",
                "mass_kg": int(dv) if dv else None, "provenance": {"page": 5, "snippet": "Table 1 density"}},
            "indicators": {},
        }
        for ind in ("GWP_total", "GWP_fossil", "GWP_biogenic"):
            key = {"GWP_total": "GWPt", "GWP_fossil": "GWPf", "GWP_biogenic": "GWPb"}[ind]
            raw = r[key][i]
            prod["indicators"][ind] = {"unit_raw": "kg CO2-eq", "unit_normalised": "kg CO2e",
                "modules": {"A1-A3": {"value": float(raw), "raw": raw, "status": "declared",
                    "provenance": {"page": 19, "section": "CORE ENVIRONMENTAL IMPACT INDICATORS | EN15804+A2 | MILE END | A1-A3",
                        "module": "A1-A3", "unit_raw": "kg CO2-eq"}}}}
        if dv:
            prod["indicators"]["GWP_total"]["modules"].update(scale_cd({k: rep_cd[k] for k in rep_cd}, dv / REP_DENSITY, 19, f"density {int(dv)}"))
        corr["products"].append(prod)
        added += 1
    doc.close()
    corr.setdefault("needs_review", []).append(
        "Mile End sheet 20 (printed 38-39): S4020 16-variant E-series + S5010/S5020/S6510/S6520/S8010 "
        "+ CLSM & NO-FINES fill materials (~36 columns) not yet loaded — value/variant counts need the "
        "full E-series order built + fill materials handled. Structure documented in hallett_table_inventory.md.")
    print(f"added {added} Mile End (sheet 19) products; total {len(corr['products'])}")
    if write:
        json.dump(corr, open(CORR, "w"), indent=2, ensure_ascii=False)
        print("WROTE.")


if __name__ == "__main__":
    main()
