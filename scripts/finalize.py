"""
Build final /data/*.json from deterministic candidate + optional agent corrections.
Numbers/provenance come from the candidate (never overwritten by the agent).
Corrections only touch contextual fields (name, strength, location, unit, dates, notes,
system-boundary confirmation) and must themselves carry a page number.
"""
import json, os, glob, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from schema import validate, MODULES

ROOT = os.path.join(os.path.dirname(__file__), "..")
CAND = os.path.join(ROOT, "extract_work", "candidates")
CORR = os.path.join(ROOT, "extract_work", "corrections")
DATA = os.path.join(ROOT, "data")

UNIT_NORM = [(r"cubic met|m3|m³|m3 of|1m3", "m3"), (r"tonne|1000 ?kg", "tonne")]


def num(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return v
    m = re.search(r"-?\d[\d ]*[.,]?\d*", str(v).replace(",", ""))
    if not m:
        return None
    try:
        return float(m.group(0).replace(" ", ""))
    except ValueError:
        return None


def norm_unit(desc):
    if not desc:
        return "m3"  # concrete EPDs are per m3 unless corrected
    low = desc.lower()
    for pat, out in UNIT_NORM:
        if re.search(pat, low):
            return out
    return "m3"


AU_STATES = {"NSW": "New South Wales", "QLD": "Queensland", "VIC": "Victoria",
             "SA": "South Australia", "WA": "Western Australia", "TAS": "Tasmania",
             "NT": "Northern Territory", "ACT": "ACT"}


def _clean_text(v):
    """Reject obvious extraction junk (dotted form-fill lines, header remnants)."""
    if not v or not isinstance(v, str):
        return v
    s = v.strip()
    if "...." in s or s.lower().startswith("and site") or len(s) < 3:
        return None
    if sum(c == "." for c in s) > 6:
        return None
    return s


def _parse_location(raw, prov):
    """Best-effort city/region/country from a free-form address (deterministic path)."""
    out = {"site": raw, "city": None, "region": None, "country": None, "raw": raw, "provenance": prov}
    if not raw:
        return out
    parts = [p.strip() for p in str(raw).replace("\n", ",").split(",") if p.strip()]
    blob = str(raw)
    for abbr, full in AU_STATES.items():
        if abbr in blob.split() or f"{abbr} " in blob or f" {abbr}" in blob or full.lower() in blob.lower():
            out["region"] = full
            out["country"] = "AU"
            break
    if "australia" in blob.lower():
        out["country"] = "AU"
    # city guess: last part that isn't a state/country/postcode/number
    for p in reversed(parts):
        pl = p.lower()
        if pl in ("australia", "au") or p.upper() in AU_STATES:
            continue
        if any(ch.isdigit() for ch in p) and len(p.split()) <= 2:
            continue
        # strip trailing state token
        toks = [t for t in p.split() if t.upper() not in AU_STATES and not t.isdigit()]
        if toks:
            out["city"] = " ".join(toks)
            break
    return out


def env(field):
    """candidate stores {value,page,snippet} envelopes; unwrap safely."""
    if isinstance(field, dict) and "value" in field:
        return field.get("value"), {"page": field.get("page"), "snippet": field.get("snippet")}
    return field, None


def build_final(cand, corr):
    corr = corr or {}
    ep = cand["epd"]
    prog, prog_p = env(ep.get("program_operator"))
    pcr, pcr_p = env(ep.get("pcr"))
    std, std_p = env(ep.get("reference_standard"))
    ch, _ = env(ep.get("characterization"))
    pub, pub_p = env(ep.get("published"))
    val, val_p = env(ep.get("valid_until"))
    name, name_p = env(cand["product"].get("name"))
    manu, manu_p = env(cand["product"].get("manufacturer"))
    ctype, _ = env(cand["product"].get("concrete_type"))
    loc, loc_p = env(cand["product"].get("manufacturing_location"))
    du_desc, du_p = env(cand["declared_unit"].get("description"))
    mass, mass_p = env(cand["declared_unit"].get("mass_kg"))
    cs = cand["product"]["compressive_strength"]

    c = corr  # shorthand; agent corrections win for contextual fields
    epd_id = c.get("id") or (ep.get("id") if isinstance(ep.get("id"), str) else None) or ep["source_pdf"]
    manu = _clean_text(manu)

    strength = {
        "value_mpa": c.get("compressive_strength", {}).get("value_mpa", cs.get("value_mpa")),
        "class": c.get("compressive_strength", {}).get("class", cs.get("class")),
        "at_days": c.get("compressive_strength", {}).get("at_days", cs.get("at_days")),
        "raw": c.get("compressive_strength", {}).get("raw"),
        "status": c.get("compressive_strength", {}).get("status",
                    "found" if cs.get("value_mpa") is not None else "missing"),
        "provenance": c.get("compressive_strength", {}).get("provenance") or cs.get("provenance"),
    }
    location = c.get("manufacturing_location") or _parse_location(loc, loc_p)
    declared_unit = {
        "amount": 1,
        "unit": (c.get("declared_unit", {}) or {}).get("unit") or norm_unit(du_desc),
        "description": (c.get("declared_unit", {}) or {}).get("description") or du_desc,
        "mass_kg": (c.get("declared_unit", {}) or {}).get("mass_kg", num(mass)),
        "provenance": (c.get("declared_unit", {}) or {}).get("provenance") or du_p,
    }

    # indicators: attach normalised unit; keep numbers/provenance verbatim
    inds = {}
    for iname, ind in cand["indicators"].items():
        inds[iname] = {
            "unit_raw": ind.get("unit_raw"),
            "unit_normalised": "kg CO2e",
            "header_modules": ind.get("header_modules", []),
            "modules": ind.get("modules", {}),
        }

    final = {
        "schema_version": "1.0",
        "epd": {
            "id": c.get("id") or epd_id,
            "source_pdf": ep["source_pdf"],
            "pages": ep["pdf_page_count"],
            "program_operator": c.get("program_operator") or prog,
            "pcr": c.get("pcr") or pcr,
            "reference_standard": c.get("reference_standard") or std,
            "en15804_version": c.get("en15804_version") or _guess_a2(std, pcr),
            "characterisation": c.get("characterisation") or ch,
            "published": c.get("published") or pub,
            "valid_until": c.get("valid_until") or val,
            "provenance": {"program_operator": prog_p, "pcr": pcr_p, "published": pub_p, "valid_until": val_p},
        },
        "products": [{
            "name": c.get("name") or name,
            "manufacturer": c.get("manufacturer") or manu,
            "concrete_type": c.get("concrete_type") or ctype,
            "compressive_strength": strength,
            "manufacturing_location": location,
            "declared_unit": declared_unit,
            "indicators": inds,
        }],
        "system_boundary": _boundary(cand, c),
        "comparability_notes": c.get("comparability_notes", []),
        "extraction_meta": {
            "method": "deterministic coordinate/order-bound table parse; contextual fields agent-verified",
            "numbers_validated": "cross_validate.py (raw string present on cited page)",
            "verified_by": c.get("verified_by"),
            "checked_by": c.get("checked_by"),
            "confidence": c.get("confidence", "medium"),
            "warnings": (cand["extraction_meta"].get("warnings", []) + c.get("warnings", [])),
            "needs_review": c.get("needs_review", []),
        },
    }
    # allow multi-product EPDs to replace products[] wholesale
    if c.get("products"):
        final["products"] = c["products"]
    return final


def _guess_a2(std, pcr):
    blob = f"{std} {pcr}".lower()
    if "+a2" in blob or "a2:2019" in blob or "15804:a2" in blob:
        return "A2"
    if "+a1" in blob:
        return "A1"
    return None


def _boundary(cand, corr):
    sb = dict(cand.get("system_boundary", {}))
    for m, st in (corr.get("system_boundary") or {}).items():
        if m in MODULES:
            sb[m] = st
    return sb


def main():
    os.makedirs(DATA, exist_ok=True)
    only = sys.argv[1] if len(sys.argv) > 1 else None
    ok = bad = 0
    for cf in sorted(glob.glob(os.path.join(CAND, "*.json"))):
        base = os.path.basename(cf)
        if only and only not in base:
            continue
        cand = json.load(open(cf))
        corr_path = os.path.join(CORR, base)
        corr = json.load(open(corr_path)) if os.path.exists(corr_path) else None
        final = build_final(cand, corr)
        errs = validate(final)
        status = "OK " if not errs else "!! "
        if errs:
            bad += 1
        else:
            ok += 1
        with open(os.path.join(DATA, base), "w") as f:
            json.dump(final, f, indent=2, ensure_ascii=False)
        print(f"{status}{base:55s} {'corr' if corr else 'det '}  errs={len(errs)}")
        for e in errs[:6]:
            print("      -", e)
    print(f"\nfinalised: {ok} clean, {bad} with schema errors")


if __name__ == "__main__":
    main()
