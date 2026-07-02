"""
Final JSON schema + structural validator. One JSON per EPD.
Every GWP module cell MUST carry {value, raw, status, provenance{page,section,module,unit_raw}}.
status is a closed enum so "not declared" can never masquerade as 0.
"""
MODULES = ["A1", "A2", "A3", "A1-A3", "A4", "A5",
           "B1", "B2", "B3", "B4", "B5", "B6", "B7",
           "C1", "C2", "C3", "C4", "D"]
CELL_STATUS = {"declared", "declared_zero", "not_declared", "not_relevant",
               "not_reported", "estimated", "missing"}
FIELD_STATUS = {"declared", "found", "missing", "not_declared", "uncertain"}


def _err(errs, cond, msg):
    if not cond:
        errs.append(msg)


def validate(d):
    errs = []
    _err(errs, isinstance(d, dict), "root not an object")
    if not isinstance(d, dict):
        return errs
    _err(errs, "epd" in d and isinstance(d["epd"], dict), "missing epd{}")
    epd = d.get("epd", {})
    for k in ("id", "source_pdf", "pages"):
        _err(errs, epd.get(k) not in (None, ""), f"epd.{k} empty")
    _err(errs, isinstance(d.get("products"), list) and d["products"], "products[] missing/empty")
    _err(errs, isinstance(d.get("system_boundary"), dict), "system_boundary missing")

    sb = d.get("system_boundary", {})
    for m in MODULES:
        st = sb.get(m)
        _err(errs, st in CELL_STATUS or st is None, f"system_boundary.{m} bad status '{st}'")

    for pi, p in enumerate(d.get("products", [])):
        tag = f"products[{pi}]"
        _err(errs, p.get("name") not in (None, ""), f"{tag}.name empty")
        cs = p.get("compressive_strength", {})
        _err(errs, isinstance(cs, dict), f"{tag}.compressive_strength missing")
        _err(errs, cs.get("status") in FIELD_STATUS, f"{tag}.compressive_strength.status bad")
        if cs.get("value_mpa") is not None:
            _err(errs, isinstance(cs["value_mpa"], (int, float)), f"{tag}.value_mpa not numeric")
            _err(errs, _has_prov(cs), f"{tag}.compressive_strength needs provenance when value present")
        du = p.get("declared_unit", {})
        _err(errs, du.get("unit") not in (None, ""), f"{tag}.declared_unit.unit empty")
        inds = p.get("indicators", {})
        _err(errs, "GWP_total" in inds, f"{tag}.indicators.GWP_total missing")
        for ind_name, ind in inds.items():
            for m, cell in ind.get("modules", {}).items():
                ct = f"{tag}.{ind_name}.{m}"
                _err(errs, m in MODULES, f"{ct} unknown module")
                _err(errs, isinstance(cell, dict), f"{ct} not object")
                _err(errs, cell.get("status") in CELL_STATUS, f"{ct} bad status '{cell.get('status')}'")
                if cell.get("status") in ("declared", "declared_zero"):
                    _err(errs, cell.get("raw") not in (None, ""), f"{ct} declared but no raw string")
                    _err(errs, isinstance(cell.get("value"), (int, float)), f"{ct} declared but value non-numeric")
                    prov = cell.get("provenance", {})
                    _err(errs, prov.get("page"), f"{ct} declared but no provenance.page")
                if cell.get("status") in ("not_declared", "not_relevant"):
                    _err(errs, cell.get("value") is None, f"{ct} {cell.get('status')} must have null value (never 0)")
    return errs


def _has_prov(obj):
    p = obj.get("provenance")
    return isinstance(p, dict) and p.get("page")


if __name__ == "__main__":
    import json, glob, os, sys
    root = os.path.join(os.path.dirname(__file__), "..")
    files = sorted(glob.glob(os.path.join(root, "data", "*.json")))
    total = 0
    for f in files:
        errs = validate(json.load(open(f)))
        total += len(errs)
        print(("OK  " if not errs else "!!  ") + os.path.basename(f) + (f"  ({len(errs)} errors)" if errs else ""))
        for e in errs[:12]:
            print("      -", e)
    print(f"\n{len(files)} files, {total} schema errors")
    sys.exit(1 if total else 0)
