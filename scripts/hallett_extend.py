"""
Complete the Dry Creek plant extraction for the Hallett EPD (per docs/hallett_table_inventory.md):
  A) S-series A1-A3 GWP (total/fossil/biogenic) from sheet 11 (printed 20-21), coordinate-mapped.
  B) Per-mix density from Table 1 (sheet 5, printed 8-9).
  C) Density-scaled C1-C4+D as `estimated` for every Dry Creek mix, per the EPD's own method
     (annex, printed 70): value_mix = value_representative * (density_mix / 2332).

Dry-run (default) prints everything for verification. `--write` merges into the corrections file.
Any mix whose density can't be confidently read keeps C/D = not_reported (never guessed).
"""
import fitz, re, json, sys, os

ROOT = os.path.join(os.path.dirname(__file__), "..")
PDF = os.path.join(ROOT, "epds",
    "epd-australasia-com-wp-content-uploads-2023-08-epd-ies-0009353-003-hallett-ready-mix-concrete-2026-05-04-pdf.pdf")
CORR = os.path.join(ROOT, "extract_work", "corrections",
    "epd-australasia-com-wp-content-uploads-2023-08-epd-ies-0009353-003-hallett-ready-mix-concrete-2026-05-04-pdf.json")
REP_DENSITY = 2332.0

VAR = re.compile(r"^(PLC\d+|LSLC\d+|PLC\dXYP|PTLC\d+|COLLC\d+|SCPLC\d+|SCPEC\d+|LC\d+|COLSCLC\d+)$")
SFAM = re.compile(r"^S\d{4}$")


def lines_of(page, tol=4.0):
    words = sorted(page.get_text("words"), key=lambda w: (w[1], w[0]))
    L = []
    for w in words:
        yc = (w[1] + w[3]) / 2
        for ln in L:
            if abs(ln["y"] - yc) <= tol:
                ln["w"].append(w); ln["y"] = (ln["y"] * ln["n"] + yc) / (ln["n"] + 1); ln["n"] += 1; break
        else:
            L.append({"y": yc, "n": 1, "w": [w]})
    for ln in L:
        ln["w"].sort(key=lambda w: w[0])
    return sorted(L, key=lambda ln: ln["y"])


def xc(w): return (w[0] + w[2]) / 2


# Authoritative L->R (family, variant) order for the Dry Creek S-series block, taken from
# the document's OWN version history (printed 71, v002 product list). Ground truth for
# labelling — avoids fragile coordinate family-assignment (RISKS.md P4). Count = 20.
S_ORDER = [("S1020", "PLC1"), ("S1520", "PLC1120"), ("S1520", "PLC2120"), ("S2520", "PLC1"),
           ("S3220", "PLC2"), ("S3220", "LSLC2"), ("S3220", "PLC2XYP"), ("S3220", "PLC2120"),
           ("S4020", "PTLC2"), ("S4020", "COLLC1"), ("S4020", "COLLC2"), ("S4020", "PLC1120"),
           ("S4020", "PLC2120"), ("S4020", "PLC2XYP"), ("S5010", "SCPLC2"), ("S6510", "SCPLC2"),
           ("S6510", "SCPEC2"), ("S6520", "PLC2120"), ("S8010", "COLSCLC2"), ("S8010", "SCPEC2")]


def extract_s_series(doc):
    """Extract the S-series GWP rows L->R and zip to the authoritative order."""
    page = doc[10]
    L = lines_of(page)
    s_fam_row = next(ln for ln in L if sum(1 for w in ln["w"] if SFAM.match(w[4])) >= 5)
    rows = {"GWPt": "GWP_total", "GWPf": "GWP_fossil", "GWPb": "GWP_biogenic"}
    out = {mk: {} for mk in S_ORDER}
    for ln in L:
        if ln["y"] <= s_fam_row["y"]:
            continue
        lab = ln["w"][0][4]
        if lab not in rows:
            continue
        vals = [w[4] for w in ln["w"] if re.match(r"^-?\d+(\.\d+)?(E[+-]?\d+)?$", w[4])]
        vals = vals[-len(S_ORDER):]
        if len(vals) != len(S_ORDER):
            raise SystemExit(f"S-series {lab}: got {len(vals)} values, expected {len(S_ORDER)}")
        for mk, v in zip(S_ORDER, vals):
            out[mk][rows[lab]] = v
        if lab == "GWPb":
            break
    return out, S_ORDER


def extract_densities(doc):
    """Sequential raw-text parse of Table 1 (sheet 5): track family, pair each variant token
    with the immediately following '2 xxx' density. Robust for both N- and S-series."""
    toks = re.split(r"\s+", doc[4].get_text())
    FAMRE = re.compile(r"^([NS]\d{4})P?$")
    VNAMES = {"Ref", "F30", "S30", "T50", "S50"}
    dens = {}
    fam = None
    i = 0
    while i < len(toks):
        t = toks[i]
        fm = FAMRE.match(t)
        if fm:
            fam = fm.group(1) + ("P" if t.endswith("P") else "")
        if fam and (VAR.match(t) or t in VNAMES):
            # next density token: '2' then a 3-digit group (may be split '2' '332')
            for j in range(i + 1, min(i + 4, len(toks))):
                if re.fullmatch(r"2\d{3}", toks[j]):
                    dens[(fam, t)] = float(toks[j]); break
                if toks[j] == "2" and j + 1 < len(toks) and re.fullmatch(r"\d{3}", toks[j + 1]):
                    dens[(fam, t)] = float("2" + toks[j + 1]); break
        i += 1
    return dens


def scale_cd(rep_modules, factor, dens_page, dens_snip):
    """Estimated C1-C4+D from representative * factor, with provenance to the method."""
    out = {}
    for m in ("C1", "C2", "C3", "C4", "D"):
        rc = rep_modules.get(m)
        if not rc or rc.get("value") is None:
            continue
        est = round(rc["value"] * factor, 4)
        out[m] = {
            "value": est, "raw": None, "status": "estimated",
            "provenance": {"page": 35, "section": "Density-scaled from representative mix (Table 43, printed 68-69) "
                           "by the EPD's stated method (Table 48/annex, printed 70): value x density/2332",
                           "module": m, "unit_raw": "kg CO2-eq",
                           "note": f"estimate = {rc['value']} x {factor:.4f}; density from Table 1 p.5 ({dens_snip})"},
        }
    return out


def main():
    write = "--write" in sys.argv
    doc = fitz.open(PDF)
    sdata, mixkeys = extract_s_series(doc)
    dens = extract_densities(doc)
    doc.close()

    print(f"=== S-series A1-A3 ({len(sdata)} mixes) ===")
    for mk in mixkeys:
        print(f"  {mk[0]} {mk[1]:10s} GWPt={sdata[mk].get('GWP_total')} GWPf={sdata[mk].get('GWP_fossil')} "
              f"GWPb={sdata[mk].get('GWP_biogenic')}  density={dens.get(mk)}")
    print(f"\n=== density map: {len(dens)} entries ===")
    miss = [mk for mk in mixkeys if mk not in dens]
    print("  S-series missing density (C/D stays not_reported):", miss)

    corr = json.load(open(CORR))
    # representative C/D (real, printed) — find it on an existing N3220P S50 product
    rep = next((p for p in corr["products"]
                if p["indicators"]["GWP_total"]["modules"].get("C1", {}).get("value") is not None), None)
    rep_cd = {m: rep["indicators"]["GWP_total"]["modules"][m] for m in ("C1", "C2", "C3", "C4", "D")}
    print(f"\nrepresentative C/D source: {rep['name']}  C1={rep_cd['C1']['value']} D={rep_cd['D']['value']}")

    def dens_of(name):
        m = re.match(r"^([NS]\d{4}P?)\s+(\S+)", name)
        return dens.get((m.group(1), m.group(2))) if m else None

    # B) add density-scaled C/D to existing N-series products (except representative)
    scaled_n = 0
    for p in corr["products"]:
        if p is rep:
            p["declared_unit"]["mass_kg"] = int(REP_DENSITY)
            continue
        dv = dens_of(p["name"])
        if dv:
            p["declared_unit"]["mass_kg"] = int(dv)
            cd = scale_cd({k: rep_cd[k] for k in rep_cd},
                          dv / REP_DENSITY, 5, f"density {int(dv)} kg/m3")
            p["indicators"]["GWP_total"]["modules"].update(cd)
            scaled_n += 1

    # A) build S-series products
    from copy import deepcopy
    tmpl = deepcopy(corr["products"][0])
    grade = {"S1020": 10, "S1520": 15, "S2520": 25, "S3220": 32, "S4020": 40,
             "S5010": 50, "S6510": 65, "S6520": 65, "S8010": 80}
    new = []
    for mk in mixkeys:
        fam, var = mk
        vals = sdata[mk]
        dv = dens.get(mk)
        prod = {
            "name": f"{fam} {var}", "manufacturer": corr["products"][0]["manufacturer"],
            "concrete_type": "Ready-mix concrete (special class)",
            "compressive_strength": {"value_mpa": grade.get(fam), "class": fam, "at_days": 28,
                "raw": f"{grade.get(fam)}", "status": "found",
                "provenance": {"page": 5, "snippet": f"Table 1. Concrete mix names, grades ... {fam} ... Grade (MPa) {grade.get(fam)}"}},
            "manufacturing_location": deepcopy(corr["products"][0]["manufacturing_location"]),
            "declared_unit": {"amount": 1, "unit": "m3", "description": "1 m3 of product produced at Dry Creek batch plant",
                "mass_kg": int(dv) if dv else None,
                "provenance": {"page": 5, "snippet": "Table 1 density (kg/m3)"}},
            "indicators": {},
        }
        mods_t = {}
        for ind_name in ("GWP_total", "GWP_fossil", "GWP_biogenic"):
            raw = vals.get(ind_name)
            if raw is None:
                continue
            prod["indicators"][ind_name] = {"unit_raw": "kg CO2-eq", "unit_normalised": "kg CO2e",
                "modules": {"A1-A3": {"value": float(raw), "raw": raw, "status": "declared",
                    "provenance": {"page": 11, "section": "CORE ENVIRONMENTAL IMPACT INDICATORS | EN15804+A2 (Table 13, S-series)",
                                   "module": "A1-A3", "unit_raw": "kg CO2-eq"}}}}
        # scaled C/D on GWP_total
        if dv:
            prod["indicators"]["GWP_total"]["modules"].update(
                scale_cd({k: rep_cd[k] for k in rep_cd}, dv / REP_DENSITY, 5, f"density {int(dv)} kg/m3"))
        new.append(prod)

    print(f"\nwould add {len(new)} S-series products; density-scaled C/D added to {scaled_n} N-series")
    corr["products"].extend(new)
    corr.setdefault("comparability_notes", []).append(
        "Dry Creek complete: N-series + S-series (special class) A1-A3 from Table 13 (printed 20-21). "
        "C1-C4+D are density-scaled 'estimated' values per the EPD's stated method (annex, printed 70) "
        "from the representative mix; only the representative carries printed C/D.")
    corr.setdefault("needs_review", [])
    corr["needs_review"] = [n for n in corr["needs_review"] if "S-series" not in n]
    corr["needs_review"].append(
        "Other 4 plants (Elizabeth, Mile End, McLaren Vale, Osborne) declare the same mixes with "
        "per-plant A1-A3 (±1-2%); documented in docs/hallett_table_inventory.md, not loaded.")

    if write:
        json.dump(corr, open(CORR, "w"), indent=2, ensure_ascii=False)
        print(f"\nWROTE {CORR}: now {len(corr['products'])} products")
    else:
        print(f"\n(dry run) total would be {len(corr['products'])} products. Re-run with --write to apply.")


if __name__ == "__main__":
    main()
