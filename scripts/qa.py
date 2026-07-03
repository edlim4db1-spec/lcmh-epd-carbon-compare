"""
Full QA/QC sweep over /data. Beyond schema + traceability, this checks INTERNAL
CONSISTENCY and honesty invariants that a wrong extraction would violate:
 - A1-A3 aggregate ~= A1+A2+A3 when both are present
 - system_boundary vs module status agree (declared-in-boundary but value missing -> flag)
 - not_declared / not_relevant cells never carry a value (never 0)
 - dates present, plausible, published < valid_until
 - strength present or explicitly uncertain; unit sane; manufacturer + country present
 - GWP-total unit looks like kg CO2
Run alongside schema.py and cross_validate.py.
"""
import json, os, glob, sys, re, datetime
sys.path.insert(0, os.path.dirname(__file__))
from schema import validate, MODULES
from cross_validate import validate_file

ROOT = os.path.join(os.path.dirname(__file__), "..")
DATA = os.path.join(ROOT, "data")
EPDS = os.path.join(ROOT, "epds")


def parse_date(s):
    if not s or not isinstance(s, str):
        return None
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.datetime.strptime(s.strip()[:10], fmt).date()
        except ValueError:
            continue
    return None


def qa_file(path):
    d = json.load(open(path))
    issues, warns = [], []

    # 1. schema + traceability
    for e in validate(d):
        issues.append(f"schema: {e}")
    probs, _ = validate_file(path, EPDS)
    for p in probs:
        issues.append(f"trace: {p}")

    sb = d.get("system_boundary", {})

    for pi, prod in enumerate(d["products"]):
        tag = f"p{pi}:{(prod.get('name') or '?')[:20]}"
        gwp = prod.get("indicators", {}).get("GWP_total", {})
        mods = gwp.get("modules", {})

        # unit sanity
        u = (gwp.get("unit_raw") or "") + (gwp.get("unit_normalised") or "")
        if "co2" not in u.lower().replace(" ", ""):
            warns.append(f"{tag}: GWP unit looks off: {gwp.get('unit_raw')!r}")

        # A1-A3 == A1+A2+A3
        agg = mods.get("A1-A3", {})
        parts = [mods.get(m, {}) for m in ("A1", "A2", "A3")]
        if agg.get("status") == "declared" and all(p.get("status") == "declared" for p in parts):
            s = sum(p["value"] for p in parts)
            if agg["value"] and abs(s - agg["value"]) / abs(agg["value"]) > 0.02:
                issues.append(f"{tag}: A1+A2+A3={s:.3g} != A1-A3={agg['value']:.3g}")

        # not_declared/not_relevant never carry a value
        for m, c in mods.items():
            if c.get("status") in ("not_declared", "not_relevant", "not_reported") and c.get("value") is not None:
                issues.append(f"{tag}.{m}: status {c['status']} but value={c['value']} (must be null)")

        # boundary vs module-status coherence — only for headline display modules.
        # (Individual A1/A2/A3/B* are ignored: many EPDs report only the A1-A3 aggregate,
        # which is normal, not an error.)
        DISPLAY = ["A1-A3", "A4", "A5", "C1", "C2", "C3", "C4", "D"]
        for m in DISPLAY:
            bs = sb.get(m)
            cell = mods.get(m)
            cs = cell.get("status") if cell else None
            if bs == "declared" and cs in (None, "not_declared"):
                warns.append(f"{tag}.{m}: boundary=declared but GWP {cs or 'absent'} — expected not_reported")
            if bs in ("not_declared", "not_relevant") and cs in ("declared", "declared_zero"):
                issues.append(f"{tag}.{m}: boundary={bs} but GWP declared — contradiction")

        # strength
        cs = prod.get("compressive_strength", {})
        if cs.get("value_mpa") is None and cs.get("status") not in ("uncertain", "missing"):
            warns.append(f"{tag}: no MPa and status={cs.get('status')}")

        # context presence
        if not prod.get("manufacturer"):
            warns.append(f"{tag}: manufacturer missing")
        if not (prod.get("manufacturing_location") or {}).get("country"):
            warns.append(f"{tag}: location.country missing")
        du = prod.get("declared_unit", {})
        if du.get("unit") not in ("m3", "tonne", "m2", "kg"):
            warns.append(f"{tag}: declared_unit.unit={du.get('unit')!r}")

    # dates
    pub, val = parse_date(d["epd"].get("published")), parse_date(d["epd"].get("valid_until"))
    if d["epd"].get("published") and not pub:
        warns.append(f"published unparseable: {d['epd'].get('published')!r}")
    if d["epd"].get("valid_until") and not val:
        warns.append(f"valid_until unparseable: {d['epd'].get('valid_until')!r}")
    if pub and val and pub > val:
        issues.append(f"published {pub} after valid_until {val}")
    if not d["epd"].get("reference_standard") and not d["epd"].get("en15804_version"):
        warns.append("no reference_standard / en15804_version")

    return issues, warns


def main():
    files = sorted(glob.glob(os.path.join(DATA, "*.json")))
    ti = tw = 0
    for f in files:
        issues, warns = qa_file(f)
        ti += len(issues); tw += len(warns)
        tag = "OK  " if not issues else "!!  "
        print(f"{tag}{os.path.basename(f):58s} issues={len(issues)} warns={len(warns)}")
        for i in issues:
            print("     ✗", i)
        for w in warns:
            print("     ·", w)
    print(f"\n=== {len(files)} files: {ti} hard issues, {tw} warnings ===")
    sys.exit(1 if ti else 0)


if __name__ == "__main__":
    main()
