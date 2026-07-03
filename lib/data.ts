import fs from "fs";
import path from "path";
import type { EpdDoc, ProductRow, Cell, CellStatus } from "./types";
import { DISPLAY_MODULES, FULL_LIFECYCLE, B_MODULES } from "./types";

const DATA_DIR = path.join(process.cwd(), "data");

let _cache: EpdDoc[] | null = null;

export function loadEpds(): EpdDoc[] {
  if (_cache) return _cache;
  const files = fs
    .readdirSync(DATA_DIR)
    .filter((f) => f.endsWith(".json"))
    .sort();
  const docs: EpdDoc[] = [];
  for (const f of files) {
    try {
      const raw = fs.readFileSync(path.join(DATA_DIR, f), "utf8");
      docs.push(JSON.parse(raw) as EpdDoc);
    } catch {
      // skip malformed file rather than crash the whole app
    }
  }
  _cache = docs;
  return docs;
}

export function loadRows(): ProductRow[] {
  const docs = loadEpds();
  const rows: ProductRow[] = [];
  for (const d of docs) {
    d.products.forEach((p, i) => {
      rows.push({
        key: `${d.epd.source_pdf}#${i}`,
        epd: d.epd,
        product: p,
        systemBoundary: d.system_boundary,
        comparabilityNotes: d.comparability_notes || [],
        needsReview: d.extraction_meta?.needs_review || [],
        confidence: d.extraction_meta?.confidence || "unknown",
      });
    });
  }
  return rows;
}

export function getRow(key: string): ProductRow | undefined {
  return loadRows().find((r) => r.key === key);
}

// GWP-total cell for a module, honouring status (never fabricates a value).
export function gwpCell(row: ProductRow, module: string): Cell | undefined {
  const ind = row.product.indicators?.GWP_total;
  return ind?.modules?.[module];
}

export function moduleStatus(row: ProductRow, module: string): CellStatus {
  const c = gwpCell(row, module);
  if (c) return c.status;
  return row.systemBoundary?.[module] ?? "not_declared";
}

// Sum only DECLARED modules across the FULL lifecycle (incl. B-stages where an EPD
// declares them); report which were included so we never imply completeness.
// A not-declared stage is excluded, not treated as zero.
export function declaredTotal(row: ProductRow): {
  total: number | null;
  included: string[];
  excluded: string[];
} {
  const included: string[] = [];
  const excluded: string[] = [];
  let total = 0;
  let any = false;
  for (const m of FULL_LIFECYCLE) {
    const c = gwpCell(row, m);
    if (c && (c.status === "declared" || c.status === "declared_zero") && typeof c.value === "number") {
      // avoid double counting: A1-A3 is the aggregate; individual A1/A2/A3 not in FULL_LIFECYCLE
      total += c.value;
      included.push(m);
      any = true;
    } else {
      excluded.push(m);
    }
  }
  return { total: any ? Math.round(total * 100) / 100 : null, included, excluded };
}

// Compact a module list for display: collapse a full B1..B7 run into "B1–B7".
export function formatModuleList(mods: string[]): string {
  const allB = B_MODULES.every((b) => mods.includes(b));
  if (!allB) return mods.join(", ");
  const i = mods.indexOf("B1");
  const before = mods.slice(0, i).filter((m) => !m.startsWith("B"));
  const after = mods.slice(i).filter((m) => !m.startsWith("B"));
  return [...before, "B1–B7", ...after].join(", ");
}

// True when this product's EPD declares any use-stage (B) module.
export function hasDeclaredB(row: ProductRow): boolean {
  return B_MODULES.some((m) => {
    const c = gwpCell(row, m);
    return !!c && (c.status === "declared" || c.status === "declared_zero");
  });
}

export function pdfHref(row: ProductRow, page?: number | null): string {
  const base = `/epds/${encodeURIComponent(row.epd.source_pdf)}`;
  return page ? `${base}#page=${page}` : base;
}

// Printed folio label for a physical page, when the document numbers them differently
// (booklet spreads, unnumbered front matter). null when printed == physical.
export function printedLabel(row: ProductRow, page?: number | null): string | null {
  if (!page || !row.epd.page_labels) return null;
  return row.epd.page_labels[String(page)] ?? null;
}

// Distinct declared-module signature, to flag comparability differences.
export function moduleSignature(row: ProductRow): string {
  return DISPLAY_MODULES.filter((m) => {
    const s = moduleStatus(row, m);
    return s === "declared" || s === "declared_zero";
  }).join(",");
}

export function allLocations(rows: ProductRow[]): string[] {
  const set = new Set<string>();
  for (const r of rows) {
    const loc = locationLabel(r);
    if (loc) set.add(loc);
  }
  return Array.from(set).sort();
}

export function locationLabel(row: ProductRow): string {
  const l = row.product.manufacturing_location;
  return (
    l?.city ||
    l?.region ||
    l?.country ||
    (l?.raw ? l.raw.split(",").slice(-2).join(",").trim() : "") ||
    "Unknown"
  );
}
