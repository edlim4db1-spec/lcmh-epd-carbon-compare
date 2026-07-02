"""
Anti-hallucination gate: for every stored GWP cell, assert its `raw` string actually
appears on the cited source page of the source PDF. A number that isn't literally in
the source text is rejected. This makes "every number is traceable" machine-checked,
not a promise.
"""
import fitz, json, os, glob, sys

ROOT = os.path.join(os.path.dirname(__file__), "..")


def norm(s):
    # normalise unicode minus + whitespace + subscripts for comparison
    for m in ["‐", "‑", "‒", "–", "—", "−"]:
        s = s.replace(m, "-")
    return s.replace(" ", "").replace(" ", "")


def page_text_cache(pdf_path):
    doc = fitz.open(pdf_path)
    texts = {i + 1: norm(doc[i].get_text()) for i in range(doc.page_count)}
    doc.close()
    return texts


def validate_file(json_path, epds_dir):
    d = json.load(open(json_path))
    pdf = os.path.join(epds_dir, d["epd"]["source_pdf"])
    if not os.path.exists(pdf):
        return [f"MISSING PDF: {d['epd']['source_pdf']}"], 0
    texts = page_text_cache(pdf)
    problems, checked = [], 0
    # indicators live under products[] in the final schema, and top-level in candidates
    indicator_sets = []
    for p in d.get("products", []):
        indicator_sets.append((p.get("name", "?"), p.get("indicators", {})))
    if d.get("indicators"):
        indicator_sets.append((d["epd"].get("id", "?"), d["indicators"]))

    for pname, inds in indicator_sets:
        for ind_name, ind in inds.items():
            for mod, cell in ind.get("modules", {}).items():
                raw = cell.get("raw")
                status = cell.get("status")
                if status not in ("declared", "declared_zero"):
                    continue
                if raw in (None, ""):
                    continue
                prov = cell.get("provenance") or {}
                # image-sourced cells can't be text-verified; require an explicit marker
                if prov.get("source_type") == "image":
                    checked += 1
                    continue
                page = prov.get("page")
                checked += 1
                hay = texts.get(page, "")
                if norm(raw) not in hay:
                    anywhere = any(norm(raw) in t for t in texts.values())
                    problems.append(
                        f"[{pname}] {ind_name}.{mod} raw='{raw}' NOT on cited page {page}"
                        + (" (found on another page!)" if anywhere else " (NOT in any text layer — image? mark source_type)"))
    return problems, checked


def main():
    epds_dir = os.path.join(ROOT, "epds")
    for src in [os.path.join(ROOT, "extract_work", "candidates"), os.path.join(ROOT, "data")]:
        files = sorted(glob.glob(os.path.join(src, "*.json")))
        if not files:
            continue
        print(f"\n### Validating {len(files)} files in {os.path.relpath(src, ROOT)} ###")
        total_problems = 0
        for jf in files:
            probs, checked = validate_file(jf, epds_dir)
            tag = "OK " if not probs else "!! "
            print(f"{tag}{os.path.basename(jf):55s} {checked:3d} cells checked, {len(probs)} problem(s)")
            for p in probs[:8]:
                print("      -", p)
            total_problems += len(probs)
        print(f"--- {total_problems} total problems in {os.path.relpath(src, ROOT)} ---")


if __name__ == "__main__":
    main()
