import Catalog from "@/components/Catalog";
import { loadRows, gwpCell, locationLabel, moduleSignature } from "@/lib/data";
import { DISPLAY_MODULES } from "@/lib/types";

export const dynamic = "force-static";

export default function Home() {
  const rows = loadRows();
  const cards = rows.map((r) => {
    const a13 = gwpCell(r, "A1-A3");
    const declared = DISPLAY_MODULES.filter((m) => {
      const c = gwpCell(r, m);
      return c && (c.status === "declared" || c.status === "declared_zero");
    });
    return {
      key: r.key,
      name: r.product.name,
      manufacturer: r.product.manufacturer || "",
      mpa: r.product.compressive_strength?.value_mpa ?? null,
      strengthClass: r.product.compressive_strength?.class ?? null,
      strengthStatus: r.product.compressive_strength?.status ?? "missing",
      location: locationLabel(r),
      country: r.product.manufacturing_location?.country || "",
      program: r.epd.program_operator?.split(",")[0]?.replace(/®/g, "").trim() || "—",
      a13: typeof a13?.value === "number" && (a13.status === "declared" || a13.status === "declared_zero") ? a13.value : null,
      a13Page: a13?.provenance?.page ?? null,
      unit: `kg CO₂e / ${r.product.declared_unit?.unit || "m³"}`,
      pdf: r.epd.source_pdf,
      declaredModules: declared as string[],
      declaredCount: declared.length,
      confidence: r.confidence,
    };
  });

  return (
    <div className="container">
      <div className="hero">
        <h1>Compare concrete by embodied carbon — honestly</h1>
        <p>
          {rows.length} concrete products from verified EPDs. Compare across the full life
          cycle (not just one headline number), filter by strength and location, and trace
          every figure back to its source EPD page. Not-declared stages are shown as such —
          never assumed to be zero.
        </p>
      </div>
      <Catalog cards={cards} />
    </div>
  );
}
