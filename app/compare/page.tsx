import Link from "next/link";
import { getRow, gwpCell, declaredTotal, pdfHref, moduleStatus, locationLabel, loadRows, hasDeclaredB, formatModuleList } from "@/lib/data";
import { DISPLAY_MODULES, B_MODULES, FULL_LIFECYCLE, type ProductRow } from "@/lib/types";
import StageValue, { statusBadge } from "@/components/StageValue";

// Depends on ?keys= selection, so must render per-request (not statically cached).
export const dynamic = "force-dynamic";

const STAGE_LABEL: Record<string, string> = {
  "A1-A3": "A1–A3 Product (cradle-to-gate)",
  A4: "A4 Transport to site",
  A5: "A5 Installation",
  B1: "B1 Use (incl. carbonation)",
  B2: "B2 Maintenance",
  B3: "B3 Repair",
  B4: "B4 Replacement",
  B5: "B5 Refurbishment",
  B6: "B6 Operational energy",
  B7: "B7 Operational water",
  C1: "C1 Deconstruction",
  C2: "C2 Transport (EoL)",
  C3: "C3 Waste processing",
  C4: "C4 Disposal",
  D: "D Beyond system (reuse/recovery)",
};

export default function Compare({
  searchParams,
}: {
  searchParams: { keys?: string };
}) {
  const keys = (searchParams.keys || "").split(",").map((k) => decodeURIComponent(k)).filter(Boolean);
  let rows = keys.map((k) => getRow(k)).filter(Boolean) as ProductRow[];

  // Nothing selected (e.g. "Compare" clicked straight from the nav): show a curated
  // example instead of a dead end — three 32 MPa products from different suppliers,
  // clearly labelled as an example. Same strength class = a fair comparison basis.
  let isExample = false;
  if (rows.length < 1) {
    const all = loadRows();
    const seen = new Set<string>();
    const candidates = all
      .filter((r) => r.product.compressive_strength?.value_mpa === 32)
      .filter((r) => {
        const id = r.epd.source_pdf;
        if (seen.has(id)) return false;
        seen.add(id);
        return true;
      })
      .sort((a, b) => (gwpCell(a, "A1-A3")?.value ?? Infinity) - (gwpCell(b, "A1-A3")?.value ?? Infinity));
    rows = candidates.slice(0, 3);
    isExample = rows.length >= 2;
    if (!isExample) {
      return (
        <div className="container" style={{ padding: "40px 0" }}>
          <h1>Compare</h1>
          <p className="small">No products selected. Go to <Link href="/">Products</Link> and add 2–4 to compare.</p>
        </div>
      );
    }
  }

  // Comparability signals (full lifecycle incl. B stages)
  const signatures = rows.map((r) =>
    FULL_LIFECYCLE.filter((m) => ["declared", "declared_zero"].includes(moduleStatus(r, m))).join(",")
  );
  const differentModules = new Set(signatures).size > 1;
  const units = new Set(rows.map((r) => r.product.declared_unit?.unit || "m3"));
  const differentUnits = units.size > 1;
  const mpas = rows.map((r) => r.product.compressive_strength?.value_mpa).filter((v) => v != null);
  const differentStrengths = new Set(mpas).size > 1;
  const indicators = new Set(
    rows.map((r) => (r.product.indicators?.GWP_total?.unit_raw || "").replace(/\s/g, ""))
  );

  return (
    <div className="container" style={{ padding: "26px 0 60px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
        <h1 style={{ margin: 0 }}>Life-cycle carbon comparison</h1>
        <Link href="/" className="btn secondary">← Edit selection</Link>
      </div>
      <p className="small" style={{ marginTop: 6 }}>
        GWP-total, kg CO₂e per declared unit. Click <span className="mono">p.N</span> on any figure to open the source EPD at that page.
      </p>

      {isExample && (
        <div className="callout info">
          <strong>Example comparison.</strong> You haven&apos;t selected anything yet, so we&apos;re
          showing three 32&nbsp;MPa products from different suppliers — the same strength class,
          so the comparison basis is fair. Go to <Link href="/">Products</Link> to filter and
          pick your own (2–4 products).
        </div>
      )}

      {differentModules && (
        <div className="callout">
          <strong>Not directly comparable.</strong> These products declare different life-cycle
          stages. A blank/ND stage is <em>not</em> zero — it means the EPD did not report it. Compare
          stage-by-stage; treat any total as covering only the declared stages listed per product.
        </div>
      )}
      {differentUnits && (
        <div className="callout">
          <strong>Different declared units</strong> ({Array.from(units).join(", ")}). Per-unit figures
          are not on the same basis — check mass per unit before comparing.
        </div>
      )}
      {differentStrengths && (
        <div className="callout">
          <strong>Different strength classes</strong> ({Array.from(new Set(mpas)).join(" vs ")} MPa).
          A stronger mix usually carries more cement and more carbon — comparing carbon across
          strength classes is misleading unless the application allows either strength.
        </div>
      )}

      <div className="tablewrap" style={{ marginTop: 14 }}>
        <table className="data">
          <thead>
            <tr>
              <th style={{ minWidth: 220 }}>Life-cycle stage</th>
              {rows.map((r) => (
                <th key={r.key} className="num" style={{ minWidth: 150 }}>
                  {r.product.name}
                  <div className="small" style={{ fontWeight: 400, textTransform: "none", letterSpacing: 0 }}>
                    {r.product.manufacturer}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {/* context rows */}
            <tr>
              <td className="rowlabel">Compressive strength</td>
              {rows.map((r) => (
                <td key={r.key} className="num">
                  {r.product.compressive_strength?.value_mpa != null ? (
                    <span className="chip">{r.product.compressive_strength.value_mpa} MPa</span>
                  ) : (
                    <span className="chip grey" title="Strength not stated in the EPD text">MPa ?</span>
                  )}
                  {r.product.compressive_strength?.class ? (
                    <div className="small">class {r.product.compressive_strength.class}</div>
                  ) : null}
                </td>
              ))}
            </tr>
            <tr>
              <td className="rowlabel">Manufacturing location</td>
              {rows.map((r) => (
                <td key={r.key} className="num">{locationLabel(r)}</td>
              ))}
            </tr>
            <tr>
              <td className="rowlabel">Declared unit</td>
              {rows.map((r) => (
                <td key={r.key} className="num">
                  {r.product.declared_unit?.unit}
                  {r.product.declared_unit?.mass_kg ? (
                    <div className="small">{r.product.declared_unit.mass_kg} kg/unit</div>
                  ) : null}
                </td>
              ))}
            </tr>

            {/* stage rows — B stages appear only when a selected product declares them */}
            {(rows.some(hasDeclaredB)
              ? ["A1-A3", "A4", "A5", ...B_MODULES, "C1", "C2", "C3", "C4", "D"]
              : [...DISPLAY_MODULES]
            ).map((m) => (
              <tr key={m}>
                <td className="rowlabel">{STAGE_LABEL[m] || m}</td>
                {rows.map((r) => (
                  <td key={r.key} className="num">
                    <StageValue cell={gwpCell(r, m)} href={pdfHref(r, gwpCell(r, m)?.provenance?.page)} />
                  </td>
                ))}
              </tr>
            ))}

            {/* declared total */}
            <tr className="stage-total">
              <td>Declared total (sum of declared stages)</td>
              {rows.map((r) => {
                const t = declaredTotal(r);
                return (
                  <td key={r.key} className="num">
                    {t.total != null ? (
                      <>
                        <span className="mono">{t.total.toLocaleString()}</span>
                        <div className="small" style={{ fontWeight: 400 }}>
                          {t.included.length} stage{t.included.length === 1 ? "" : "s"}
                          {t.excluded.length ? ` · excl. ${formatModuleList(t.excluded)}` : ""}
                        </div>
                      </>
                    ) : (
                      statusBadge("missing")
                    )}
                  </td>
                );
              })}
            </tr>
          </tbody>
        </table>
      </div>

      <div className="legend">
        <span><span className="badge nd">ND</span> not declared (≠ 0)</span>
        <span><span className="badge nrep">not reported</span> in scope but unpublished (≠ 0)</span>
        <span><span className="badge nr">NR</span> not relevant</span>
        <span><span className="badge zero">0</span> declared as zero</span>
        <span><span className="badge nd">img</span> read from rasterised table (verified visually ×2)</span>
        <span><span className="mono">p.N</span> → source EPD page</span>
      </div>

      {/* provenance / metadata per product */}
      <h3 style={{ marginTop: 28 }}>Sources &amp; caveats</h3>
      <div className="grid" style={{ marginTop: 10 }}>
        {rows.map((r) => (
          <div className="panel panel-pad" key={r.key}>
            <h4 style={{ margin: "0 0 6px" }}>{r.product.name}</h4>
            <div className="small">
              <div><strong>EPD:</strong> {r.epd.id}</div>
              <div><strong>Programme:</strong> {r.epd.program_operator || "—"}</div>
              <div><strong>PCR:</strong> {r.epd.pcr || "—"}</div>
              <div><strong>Standard:</strong> {r.epd.reference_standard || r.epd.en15804_version || "—"} {r.epd.characterisation ? `· ${r.epd.characterisation}` : ""}</div>
              <div><strong>Valid until:</strong> {r.epd.valid_until || "—"}</div>
              <div><strong>Extraction confidence:</strong> {r.confidence}</div>
            </div>
            {r.comparabilityNotes?.length ? (
              <ul className="small" style={{ margin: "8px 0 0 16px" }}>
                {r.comparabilityNotes.map((n, i) => <li key={i}>{n}</li>)}
              </ul>
            ) : null}
            {r.needsReview?.length ? (
              <div className="small" style={{ marginTop: 8 }}>
                <strong>Known gaps (not extracted):</strong>
                <ul style={{ margin: "4px 0 0 16px" }}>
                  {r.needsReview.map((n, i) => <li key={i}>{n}</li>)}
                </ul>
              </div>
            ) : null}
            <div className="provbar">
              <a href={pdfHref(r)} target="_blank" rel="noreferrer">Open full source EPD ({r.epd.source_pdf}) ↗</a>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
