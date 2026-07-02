"""
Full deterministic extractor -> candidate JSON per EPD.
Numbers come from lib_tables (coordinate-bound, no transcription).
Contextual fields are best-effort text scans that ALWAYS carry a page + raw snippet,
and are set to null (never guessed) when not confidently found, flagged for the agent.
"""
import fitz, re, json, sys, os, glob
sys.path.insert(0, os.path.dirname(__file__))
from lib_tables import extract_gwp_tables
from lib_parse import MODULE_ORDER, classify_cell

EPDS = os.path.join(os.path.dirname(__file__), "..", "epds")
OUT = os.path.join(os.path.dirname(__file__), "..", "extract_work", "candidates")


def page_texts(doc):
    return [doc[i].get_text() for i in range(doc.page_count)]


def find_field(pages, labels, max_lookahead=3):
    """Find a labelled field; return {value, page, snippet} or None. Never guesses."""
    for pno, txt in enumerate(pages):
        lines = [l.strip() for l in txt.split("\n")]
        for i, line in enumerate(lines):
            # skip all-caps section headers (e.g. "MANUFACTURER AND SITE") — they are
            # not label:value rows and cause false matches like manufacturer="AND SITE".
            if line and line.upper() == line and any(c.isalpha() for c in line) and len(line) > 3:
                continue
            low = line.lower()
            for lab in labels:
                if low == lab.lower() or low.startswith(lab.lower()):
                    # value may be on same line after colon, else next non-empty lines
                    same = line[len(lab):].lstrip(" :\t") if len(line) > len(lab) else ""
                    if same and same not in (":",):
                        return {"value": same.strip(), "page": pno + 1, "snippet": line.strip()}
                    for j in range(1, max_lookahead + 1):
                        if i + j < len(lines) and lines[i + j]:
                            return {"value": lines[i + j].strip(), "page": pno + 1,
                                    "snippet": f"{line.strip()} | {lines[i + j].strip()}"}
    return None


def find_regex(pages, pattern, flags=re.I):
    for pno, txt in enumerate(pages):
        m = re.search(pattern, txt, flags)
        if m:
            return {"value": m.group(1).strip(), "page": pno + 1, "snippet": m.group(0).strip()[:160]}
    return None


def extract_strength(pages, filename):
    """MPa + class, from characteristics/description/name. Records provenance; flags guesses."""
    # 1) explicit compressive strength class label
    cls = find_field(pages, ["Compressive strength class:", "Compressive strength class",
                             "Strength class", "Compressive strength"])
    # 2) explicit MPa number anywhere near 'strength'
    mpa = find_regex(pages, r"(\d{2,3})\s*MPa")
    result = {"value_mpa": None, "class": None, "at_days": None,
              "provenance": None, "confidence": "none", "note": None}
    if cls:
        result["class"] = cls["value"]
        result["provenance"] = {"page": cls["page"], "snippet": cls["snippet"]}
    if mpa:
        result["value_mpa"] = int(mpa["value"])
        result["confidence"] = "text"
        if not result["provenance"]:
            result["provenance"] = {"page": mpa["page"], "snippet": mpa["snippet"]}
    # characteristic-strength phrasing e.g. "characteristic strength of 32MPa"
    cs = find_regex(pages, r"characteristic strength of\s*(\d{2,3})\s*MPa")
    if cs:
        result["value_mpa"] = int(cs["value"])
        result["confidence"] = "text"
        result["provenance"] = {"page": cs["page"], "snippet": cs["snippet"]}
    if result["value_mpa"] is None:
        result["note"] = "MPa not found in text; agent must confirm (do NOT infer from product code)."
    return result


def system_boundary_status(indicators, pages):
    """Per-module declared status. Primary source: GWP-total results cells.
    Modules absent from results -> not_declared (agent confirms vs boundary table)."""
    gwp = indicators.get("GWP_total", {}).get("modules", {})
    status = {}
    for m in MODULE_ORDER:
        cell = gwp.get(m)
        if cell is None:
            status[m] = "not_declared"
        else:
            status[m] = cell["status"]
    return status


def build_indicators(pdf_path):
    rows = extract_gwp_tables(pdf_path)
    # Merge cells for the same indicator across pages (tables split across pages).
    indicators = {}
    conflicts = []
    for r in rows:
        name = r["indicator"]
        ind = indicators.setdefault(name, {"unit_raw": r["unit_raw"], "modules": {},
                                           "header_modules": [], "pages": []})
        if r["page"] not in ind["pages"]:
            ind["pages"].append(r["page"])
        for m in r["modules_in_header"]:
            if m not in ind["header_modules"]:
                ind["header_modules"].append(m)
        for m in MODULE_ORDER:
            c = r["cells"].get(m)
            if c is None:
                continue
            cell = {
                "value": c["value"], "raw": c["raw"], "status": c["status"],
                "provenance": {"page": r["page"], "section": r["section"],
                               "table": r["section"], "module": m, "unit_raw": r["unit_raw"]},
            }
            if m in ind["modules"]:
                prev = ind["modules"][m]
                if prev["raw"] != cell["raw"]:
                    conflicts.append(f"{name}.{m}: '{prev['raw']}' vs '{cell['raw']}'")
                continue  # keep first occurrence, record conflict
            ind["modules"][m] = cell
    return indicators, conflicts


def extract_one(pdf_path):
    doc = fitz.open(pdf_path)
    pages = page_texts(doc)
    npages = doc.page_count
    doc.close()
    fname = os.path.basename(pdf_path)

    idm = re.search(r"(EPD[-_](?:IES|HUB)[-_ ]?\d{3,6}|epd-ies-\d{3,6}|HUB-\d{3,6})", fname, re.I)
    epd_id = find_field(pages, ["Registration number", "EPD registration number",
                                "EPD number", "Declaration number"])
    indicators, conflicts = build_indicators(pdf_path)

    cand = {
        "epd": {
            "id": (epd_id["value"] if epd_id else (idm.group(1) if idm else fname)),
            "source_pdf": fname,
            "pdf_page_count": npages,
            "program_operator": _v(find_field(pages, ["Program operator", "Programme operator", "Programme Operator"])),
            "pcr": _v(find_field(pages, ["PCR", "Product category rules", "Product Category Rules"])),
            "reference_standard": _v(find_field(pages, ["Reference standard", "Reference Standard"])),
            "characterization": _v(find_regex(pages, r"(EF\s*3\.\d|CML|PEF)")),
            "published": _v(find_regex(pages, r"[Pp]ublished on\s*([0-9./\-]+)")),
            "valid_until": _v(find_regex(pages, r"[Vv]alid until\s*([0-9./\-]+)")),
        },
        "product": {
            "name": _v(find_field(pages, ["Product name", "Product Name", "Name of product"])),
            "manufacturer": _v(find_field(pages, ["Manufacturer", "Name of manufacturer"])),
            "concrete_type": _v(find_field(pages, ["Concrete type", "Product type"])),
            "compressive_strength": extract_strength(pages, fname),
            "manufacturing_location": _v(find_field(pages, ["Place of production", "Place of Production",
                                                            "Manufacturing site", "Address", "Plant"])),
        },
        "declared_unit": {
            "description": _v(find_field(pages, ["Declared unit", "Declared Unit", "Functional unit"])),
            "mass_kg": _v(find_field(pages, ["Declared unit mass, kg", "Mass per declared unit",
                                             "Declared unit mass"])),
        },
        "system_boundary": system_boundary_status(indicators, pages),
        "indicators": indicators,
        "comparability_notes": [],
        "extraction_meta": {
            "method": "deterministic coordinate-bound table parse + text field scan",
            "numbers_source": "lib_tables (x-position column binding, no transcription)",
            "needs_agent_verification": [
                "compressive_strength.value_mpa", "manufacturing_location",
                "system_boundary (cross-check vs boundary table)", "declared_unit.mass_kg",
            ],
            "warnings": [],
        },
    }
    # sanity warnings
    if "GWP_total" not in indicators:
        cand["extraction_meta"]["warnings"].append("No GWP-total results table found deterministically.")
    for c in conflicts:
        cand["extraction_meta"]["warnings"].append("Cell conflict across pages: " + c)
    return cand


def _v(field):
    return field  # keep {value,page,snippet} envelope so provenance survives


def main():
    os.makedirs(OUT, exist_ok=True)
    targets = sorted(glob.glob(os.path.join(EPDS, "*.pdf")))
    if len(sys.argv) > 1:
        targets = [t for t in targets if sys.argv[1] in t]
    for p in targets:
        cand = extract_one(p)
        out = os.path.join(OUT, os.path.basename(p).replace(".pdf", ".json"))
        with open(out, "w") as f:
            json.dump(cand, f, indent=2, ensure_ascii=False)
        gwp = cand["indicators"].get("GWP_total", {}).get("modules", {})
        declared = [m for m, c in gwp.items() if c["status"] in ("declared", "declared_zero")]
        print(f"OK {os.path.basename(p):55s} GWP-total modules declared: {declared}")


if __name__ == "__main__":
    main()
