"""
Generate the per-EPD audit report + a summary. For every GWP-total cell this prints
module / value / raw / status / page / section / unit so a human can trace each number
to the source EPD in seconds. Also records the machine cross-validation result.
"""
import json, os, glob, sys
sys.path.insert(0, os.path.dirname(__file__))
from cross_validate import validate_file
from schema import validate, MODULES

ROOT = os.path.join(os.path.dirname(__file__), "..")
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "docs", "audit")


def prov_line(cell):
    p = cell.get("provenance") or {}
    return (cell.get("raw"), cell.get("value"), cell.get("status"),
            p.get("page"), (p.get("section") or p.get("table") or "")[:46], p.get("unit_raw") or "")


def report_one(path):
    d = json.load(open(path))
    epd = d["epd"]
    lines = [f"# Audit — {epd['id']}", "",
             f"- **Source PDF:** `{epd['source_pdf']}` ({epd['pages']} pp)",
             f"- **Programme:** {epd.get('program_operator')}",
             f"- **PCR / standard:** {epd.get('pcr')} · {epd.get('reference_standard') or epd.get('en15804_version')} · {epd.get('characterisation') or ''}",
             f"- **Published / valid until:** {epd.get('published')} / {epd.get('valid_until')}",
             f"- **Extraction confidence:** {d['extraction_meta'].get('confidence')}",
             f"- **Verified by / checked by:** {d['extraction_meta'].get('verified_by')} / {d['extraction_meta'].get('checked_by')}",
             ""]

    probs, checked = validate_file(path, os.path.join(ROOT, "epds"))
    serrs = validate(d)
    lines += [f"**Number traceability (cross_validate):** {checked} declared cells checked, "
              f"{len(probs)} problem(s). **Schema:** {len(serrs)} error(s).", ""]
    for p in probs:
        lines.append(f"- ⚠ {p}")
    for e in serrs:
        lines.append(f"- ⚠ schema: {e}")
    if probs or serrs:
        lines.append("")

    lines += ["## System boundary (per module)", "",
              "| " + " | ".join(MODULES) + " |",
              "|" + "---|" * len(MODULES)]
    sb = d.get("system_boundary", {})
    lines.append("| " + " | ".join(_short(sb.get(m)) for m in MODULES) + " |")
    lines.append("")

    for pi, prod in enumerate(d["products"]):
        cs = prod.get("compressive_strength", {})
        loc = prod.get("manufacturing_location", {})
        du = prod.get("declared_unit", {})
        lines += [f"## Product {pi+1}: {prod.get('name')}", "",
                  f"- **Manufacturer:** {prod.get('manufacturer')}",
                  f"- **Compressive strength:** {cs.get('value_mpa')} MPa (class {cs.get('class')}, status {cs.get('status')})"
                  + (f" — p.{(cs.get('provenance') or {}).get('page')}" if cs.get('provenance') else ""),
                  f"- **Location:** {loc.get('city') or loc.get('raw')} ({loc.get('country')})",
                  f"- **Declared unit:** {du.get('amount')} {du.get('unit')} · mass {du.get('mass_kg')} kg", ""]
        gwp = prod.get("indicators", {}).get("GWP_total", {})
        lines += [f"### GWP-total ({gwp.get('unit_raw')}) — provenance per module", "",
                  "| Module | Value | Raw (verbatim) | Status | Page | Section |",
                  "|---|---|---|---|---|---|"]
        for m in MODULES:
            c = gwp.get("modules", {}).get(m)
            if not c:
                continue
            raw, val, st, pg, sec, _ = prov_line(c)
            lines.append(f"| {m} | {val} | `{raw}` | {st} | {pg} | {sec} |")
        lines.append("")

    notes = d.get("comparability_notes", [])
    warns = d["extraction_meta"].get("warnings", [])
    review = d["extraction_meta"].get("needs_review", [])
    if notes:
        lines += ["## Comparability notes"] + [f"- {n}" for n in notes] + [""]
    if warns:
        lines += ["## Warnings"] + [f"- {w}" for w in warns] + [""]
    if review:
        lines += ["## Needs review (honest gaps)"] + [f"- {r}" for r in review] + [""]

    return "\n".join(lines), len(probs), len(serrs), checked


def _short(s):
    return {"declared": "✓", "declared_zero": "0", "not_declared": "ND",
            "not_relevant": "NR", "not_reported": "—", None: "?"}.get(s, s or "?")


def main():
    os.makedirs(OUT, exist_ok=True)
    files = sorted(glob.glob(os.path.join(DATA, "*.json")))
    summary = ["# Audit summary", "",
               "| EPD | products | cells checked | trace probs | schema errs | confidence |",
               "|---|---|---|---|---|---|"]
    tot_p = tot_s = 0
    for f in files:
        md, np_, ns_, checked = report_one(f)
        d = json.load(open(f))
        base = os.path.basename(f).replace(".json", ".md")
        with open(os.path.join(OUT, base), "w") as fh:
            fh.write(md)
        tot_p += np_; tot_s += ns_
        summary.append(f"| {d['epd']['id']} | {len(d['products'])} | {checked} | {np_} | {ns_} | {d['extraction_meta'].get('confidence')} |")
    summary += ["", f"**Totals:** {tot_p} traceability problems, {tot_s} schema errors across {len(files)} EPDs."]
    with open(os.path.join(ROOT, "docs", "AUDIT_SUMMARY.md"), "w") as fh:
        fh.write("\n".join(summary))
    print(f"Wrote {len(files)} audit reports; {tot_p} trace problems, {tot_s} schema errors.")


if __name__ == "__main__":
    main()
