// Types mirror the Part-1 JSON schema (scripts/schema.py).
export type CellStatus =
  | "declared" | "declared_zero" | "not_declared" | "not_relevant"
  | "not_reported" | "estimated" | "missing";

export type FieldStatus = "declared" | "found" | "missing" | "not_declared" | "uncertain";

export const DISPLAY_MODULES = [
  "A1-A3", "A4", "A5", "C1", "C2", "C3", "C4", "D",
] as const;

// Use-stage modules: most concrete EPDs leave these ND, so the UI only shows them
// for products whose EPD actually declares them (e.g. GCCA EPDs declare B1 recarbonation).
export const B_MODULES = ["B1", "B2", "B3", "B4", "B5", "B6", "B7"] as const;

// Full lifecycle order used for totals and for tables when B stages are declared.
export const FULL_LIFECYCLE = [
  "A1-A3", "A4", "A5", ...B_MODULES, "C1", "C2", "C3", "C4", "D",
] as const;
export type Module = (typeof DISPLAY_MODULES)[number] | "A1" | "A2" | "A3"
  | "B1" | "B2" | "B3" | "B4" | "B5" | "B6" | "B7";

export interface Provenance {
  page?: number | null;
  section?: string | null;
  table?: string | null;
  module?: string | null;
  unit_raw?: string | null;
  snippet?: string | null;
  source_type?: string | null; // "image" => read visually from a rasterised table
  verification?: string | null;
  note?: string | null; // e.g. estimation method for density-scaled cells
}

export interface Cell {
  value: number | null;
  raw: string | null;
  status: CellStatus;
  provenance?: Provenance;
}

export interface Indicator {
  unit_raw?: string | null;
  unit_normalised?: string | null;
  header_modules?: string[];
  modules: Record<string, Cell>;
}

export interface Strength {
  value_mpa: number | null;
  class: string | null;
  at_days?: number | null;
  raw?: string | null;
  status: FieldStatus;
  provenance?: Provenance | null;
}

export interface Location {
  site?: string | null;
  city?: string | null;
  region?: string | null;
  country?: string | null;
  raw?: string | null;
  provenance?: Provenance | null;
}

export interface DeclaredUnit {
  amount: number;
  unit: string;
  description?: string | null;
  mass_kg?: number | null;
  provenance?: Provenance | null;
}

export interface Product {
  name: string;
  manufacturer?: string | null;
  concrete_type?: string | null;
  compressive_strength: Strength;
  manufacturing_location: Location;
  declared_unit: DeclaredUnit;
  indicators: Record<string, Indicator>;
}

export interface Epd {
  id: string;
  source_pdf: string;
  pages: number;
  // physical PDF page -> printed folio label, only for documents where they differ
  // (booklet spreads print two folios per sheet; some docs have unnumbered front matter)
  page_labels?: Record<string, string> | null;
  program_operator?: string | null;
  pcr?: string | null;
  reference_standard?: string | null;
  en15804_version?: string | null;
  characterisation?: string | null;
  published?: string | null;
  valid_until?: string | null;
  provenance?: Record<string, Provenance | null>;
}

export interface EpdDoc {
  schema_version: string;
  epd: Epd;
  products: Product[];
  system_boundary: Record<string, CellStatus>;
  comparability_notes: string[];
  extraction_meta: {
    method: string;
    numbers_validated?: string;
    verified_by?: string | null;
    checked_by?: string | null;
    confidence?: string;
    warnings?: string[];
    needs_review?: string[];
  };
}

// A single comparable row = one product from one EPD.
export interface ProductRow {
  key: string;
  epd: Epd;
  product: Product;
  systemBoundary: Record<string, CellStatus>;
  comparabilityNotes: string[];
  needsReview: string[];
  confidence: string;
}
