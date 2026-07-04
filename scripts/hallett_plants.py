"""
Extend the Hallett EPD with the other batch plants' EN15804+A2 A1-A3 core tables
(per docs/hallett_table_inventory.md). Plants share mix designs; A1-A3 differs per plant
(local grid/transport). C1-C4+D depend only on mass -> reuse the same density-scaled
`estimated` values. Sets location.city = plant so the location filter is a plant selector.

This pass: the 3 clean N-series plants (Elizabeth, McLaren Vale, Osborne), each 24 mixes
in the authoritative N-series order. Mile End (larger/irregular) handled separately.
Dry-run prints for verification; --write merges into corrections.
"""
import fitz, re, json, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from hallett_extend import lines_of, extract_densities, scale_cd, REP_DENSITY

ROOT = os.path.join(os.path.dirname(__file__), "..")
PDF = os.path.join(ROOT, "epds",
    "epd-australasia-com-wp-content-uploads-2023-08-epd-ies-0009353-003-hallett-ready-mix-concrete-2026-05-04-pdf.pdf")
CORR = os.path.join(ROOT, "extract_work", "corrections",
    "epd-australasia-com-wp-content-uploads-2023-08-epd-ies-0009353-003-hallett-ready-mix-concrete-2026-05-04-pdf.json")

# authoritative N-series (family, variant) order (from verified Dry Creek data)
N_ORDER = [("N2020P", v) for v in ("Ref", "F30", "S30", "S50")] + \
          [(f, v) for f in ("N2520P", "N3220P", "N4020P", "N5020P")
           for v in ("Ref", "F30", "S30", "T50", "S50")]

# plant -> (physical sheet index 0-based, printed folio, city)
PLANTS = {
    "Elizabeth": (15, "30-31", "Elizabeth"),
    "McLaren Vale": (28, "56-57", "McLaren Vale"),
    "Osborne": (31, "62-63", "Osborne"),
}
GRADE = {"N2020P": 20, "N2520P": 25, "N3220P": 32, "N4020P": 40, "N5020P": 50}


def plant_nseries(doc, sheet_idx):
    """Return {(fam,var): {GWP_total,GWP_fossil,GWP_biogenic: raw}} for a plant N-series table."""
    page = doc[sheet_idx]
    L = lines_of(page)
    rows = {"GWPt": "GWP_total", "GWPf": "GWP_fossil", "GWPb": "GWP_biogenic"}
    out = {mk: {} for mk in N_ORDER}
    for ln in L:
        lab = ln["w"][0][4]
        if lab not in rows:
            continue
        vals = [w[4] for w in ln["w"] if re.match(r"^-?\d+(\.\d+)?(E[+-]?\d+)?$", w[4])]
        if len(vals) < len(N_ORDER):
            continue
        vals = vals[:len(N_ORDER)]
        for mk, v in zip(N_ORDER, vals):
            out[mk][rows[lab]] = v
        if lab == "GWPb":
            break
    return out


def main():
    write = "--write" in sys.argv
    doc = fitz.open(PDF)
    dens = extract_densities(doc)
    corr = json.load(open(CORR))
    rep = next(p for p in corr["products"]
               if p["indicators"]["GWP_total"]["modules"].get("C1", {}).get("value") is not None)
    rep_cd = {m: rep["indicators"]["GWP_total"]["modules"][m] for m in ("C1", "C2", "C3", "C4", "D")}

    # tag existing (Dry Creek) products with their plant city
    for p in corr["products"]:
        p["manufacturing_location"]["city"] = "Dry Creek"

    import copy
    added = 0
    for plant, (idx, printed, city) in PLANTS.items():
        data = plant_nseries(doc, idx)
        vals = [data[mk].get("GWP_total") for mk in N_ORDER]
        print(f"\n{plant} (printed {printed}): {sum(v is not None for v in vals)}/24 GWPt -> {[v for v in vals]}")
        for mk in N_ORDER:
            fam, var = mk
            dv = dens.get(mk)
            prod = {
                "name": f"{fam} {var}", "manufacturer": rep["manufacturer"],
                "concrete_type": "Ready-mix concrete",
                "compressive_strength": {"value_mpa": GRADE[fam], "class": f"N{GRADE[fam]}", "at_days": 28,
                    "raw": str(GRADE[fam]), "status": "found",
                    "provenance": {"page": 5, "snippet": f"Table 1 grades ... {fam} ... Grade (MPa) {GRADE[fam]}"}},
                "manufacturing_location": {"site": f"{city} batch plant", "city": city,
                    "region": "South Australia", "country": "AU", "raw": f"{city}, SA",
                    "provenance": {"page": idx + 1, "snippet": f"{plant.upper()} | A1-A3 (printed {printed})"}},
                "declared_unit": {"amount": 1, "unit": "m3",
                    "description": f"1 m3 of product produced at {city} batch plant",
                    "mass_kg": int(dv) if dv else None,
                    "provenance": {"page": 5, "snippet": "Table 1 density"}},
                "indicators": {},
            }
            for ind, key in (("GWP_total", "GWP_total"), ("GWP_fossil", "GWP_fossil"), ("GWP_biogenic", "GWP_biogenic")):
                raw = data[mk].get(ind)
                if raw is None:
                    continue
                prod["indicators"][ind] = {"unit_raw": "kg CO2-eq", "unit_normalised": "kg CO2e",
                    "modules": {"A1-A3": {"value": float(raw), "raw": raw, "status": "declared",
                        "provenance": {"page": idx + 1,
                            "section": f"CORE ENVIRONMENTAL IMPACT INDICATORS | EN15804+A2 | {plant.upper()} | A1-A3",
                            "module": "A1-A3", "unit_raw": "kg CO2-eq"}}}}
            if dv:
                prod["indicators"]["GWP_total"]["modules"].update(
                    scale_cd({k: rep_cd[k] for k in rep_cd}, dv / REP_DENSITY, idx + 1, f"density {int(dv)} kg/m3"))
            corr["products"].append(prod)
            added += 1
    doc.close()

    corr.setdefault("comparability_notes", []).append(
        "Multi-plant: A1-A3 declared per batch plant (Dry Creek / Elizabeth / McLaren Vale / Osborne); "
        "location filter selects the plant. C1-C4+D are mass-only, so the same density-scaled estimate "
        "applies at every plant.")
    print(f"\nadded {added} products across {len(PLANTS)} plants; total now {len(corr['products'])}")
    if write:
        json.dump(corr, open(CORR, "w"), indent=2, ensure_ascii=False)
        print("WROTE corrections.")
    else:
        print("(dry run) re-run with --write")


if __name__ == "__main__":
    main()
