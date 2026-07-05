import Link from "next/link";
import { getRow, gwpCell, declaredTotal, pdfHref, locationLabel, formatModuleList, printedLabel } from "@/lib/data";
import { DISPLAY_MODULES, B_MODULES } from "@/lib/types";
import StageValue, { statusBadge } from "@/components/StageValue";

// Depends on ?key= selection, so must render per-request.
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

const clip = (s: string, n: number) => (s.length > n ? s.slice(0, n).trimEnd() + "…" : s);

const EXTRA_INDICATORS: [string, string][] = [
  ["GWP_fossil", "GWP-fossil"],
  ["GWP_biogenic", "GWP-biogenic"],
  ["GWP_GHG", "GWP-GHG (legacy indicator)"],
];

export default function ProductDetail({
  searchParams,
}: {
  searchParams: { key?: string };
}) {
  const key = decodeURIComponent(searchParams.key || "");
  const row = key ? getRow(key) : undefined;

  if (!row) {
    return (
      <div className="container" style={{ padding: "40px 0" }}>
        <h1>Product not found</h1>
        <p className="small">Go back to <Link href="/">Products</Link> and open a product from there.</p>
      </div>
    );
  }

  const p = row.product;
  const total = declaredTotal(row);
  const a13 = gwpCell(row, "A1-A3");

  return (
    <div className="container" style={{ padding: "26px 0 60px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", gap: 12, flexWrap: "wrap" }}>
        <div>
          <h1 style={{ margin: 0 }}>{p.name}</h1>
          <div className="small" style={{ marginTop: 4 }}>{p.manufacturer || "Manufacturer not stated"}</div>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <Link href="/" className="btn secondary">← All products</Link>
          <a href={pdfHref(row)} target="_blank" rel="noreferrer" className="btn">Open source EPD ↗</a>
        </div>
      </div>

      <div className="meta-row" style={{ marginTop: 12, fontSize: 13 }}>
        {p.compressive_strength?.value_mpa != null ? (
          <span className="chip">
            {p.compressive_strength.value_mpa} MPa{p.compressive_strength.class ? ` · ${p.compressive_strength.class}` : ""}
            {p.compressive_strength.provenance?.page ? (
              <a className="prov" href={pdfHref(row, p.compressive_strength.provenance.page)} target="_blank" rel="noreferrer" title={p.compressive_strength.provenance?.snippet || "Source page"} style={{ marginLeft: 6 }}>
                p.{p.compressive_strength.provenance.page}
                {printedLabel(row, p.compressive_strength.provenance.page) ? ` (${printedLabel(row, p.compressive_strength.provenance.page)})` : ""}
              </a>
            ) : null}
          </span>
        ) : (p.name.startsWith("CLSM") || p.name.startsWith("NO FINES")) ? (
          <span className="chip grey" title="Fill material — no compressive-strength grade (N/A in the EPD)">N/A</span>
        ) : (
          <span className="chip grey">strength not stated</span>
        )}
        <span className="chip grey">
          {locationLabel(row)}
          {p.manufacturing_location?.provenance?.page ? (
            <a className="prov" href={pdfHref(row, p.manufacturing_location.provenance.page)} target="_blank" rel="noreferrer" title={p.manufacturing_location.provenance?.snippet || "Source page"} style={{ marginLeft: 6 }}>
              p.{p.manufacturing_location.provenance.page}
              {printedLabel(row, p.manufacturing_location.provenance.page) ? ` (${printedLabel(row, p.manufacturing_location.provenance.page)})` : ""}
            </a>
          ) : null}
        </span>
        <span className="chip grey">
          unit: {p.declared_unit?.unit}{p.declared_unit?.mass_kg ? ` · ${p.declared_unit.mass_kg} kg` : ""}
          {p.declared_unit?.provenance?.page ? (
            <a className="prov" href={pdfHref(row, p.declared_unit.provenance.page)} target="_blank" rel="noreferrer" title="Source page" style={{ marginLeft: 6 }}>
              p.{p.declared_unit.provenance.page}
              {printedLabel(row, p.declared_unit.provenance.page) ? ` (${printedLabel(row, p.declared_unit.provenance.page)})` : ""}
            </a>
          ) : null}
        </span>
        <span className="chip grey">EPD: {row.epd.id}</span>
      </div>

      {/* headline */}
      <div className="headline" style={{ marginTop: 18 }}>
        {a13 && typeof a13.value === "number" ? (
          <>
            <span className="num">{a13.value.toLocaleString(undefined, { maximumFractionDigits: 1 })}</span>
            <span className="unit">kg CO₂e / {p.declared_unit?.unit} · A1–A3</span>
          </>
        ) : (
          <span className="unit">A1–A3 not available</span>
        )}
        {total.total != null && (
          <span className="unit" style={{ marginLeft: 14 }}>
            declared total {total.total.toLocaleString()} over {total.included.length} stage{total.included.length === 1 ? "" : "s"}
            {total.excluded.length ? ` (excl. ${formatModuleList(total.excluded)})` : ""}
            {total.estTotal != null ? (
              <>
                {" · "}
                <span title="Includes density-scaled estimated C1–C4 + D per the EPD's stated method">
                  {total.estTotal.toLocaleString()} incl. estimated {formatModuleList(total.estIncluded)}
                </span>
              </>
            ) : null}
          </span>
        )}
      </div>

      {/* full extraction table: GWP-total per stage with provenance */}
      <h3 style={{ marginTop: 22 }}>Life-cycle stages — GWP-total ({p.indicators?.GWP_total?.unit_raw || "kg CO₂e"})</h3>
      <div className="tablewrap" style={{ marginTop: 8 }}>
        <table className="data">
          <thead>
            <tr>
              <th style={{ minWidth: 230 }}>Stage</th>
              <th className="num">Value</th>
              <th>As printed (raw)</th>
              <th>Status</th>
              <th>Source</th>
            </tr>
          </thead>
          <tbody>
            {/* Audit view mirrors the source RESULTS table exactly: a stage row renders
                iff the PDF's results table addressed that module (a number, a printed 0,
                a printed ND, or an explicit not-reported caution). Modules whose columns
                the PDF omits appear only in the System boundary strip below — same
                structure as the EPD document itself. */}
            {["A1-A3", "A4", "A5", ...B_MODULES, "C1", "C2", "C3", "C4", "D"]
              .filter((m) => !!gwpCell(row, m))
              .map((m) => {
              const c = gwpCell(row, m);
              const prov = c?.provenance;
              return (
                <tr key={m}>
                  <td className="rowlabel">{STAGE_LABEL[m] || m}</td>
                  <td className="num"><StageValue cell={c} href={pdfHref(row, prov?.page)} printed={printedLabel(row, prov?.page)} /></td>
                  <td className="mono small">{c?.raw ?? "—"}</td>
                  <td>
                    {!c
                      ? statusBadge("not_declared")
                      : c.status === "declared"
                      ? "declared"
                      : c.status === "declared_zero"
                      ? "declared (zero)"
                      : statusBadge(c.status)}
                  </td>
                  <td className="small">
                    {c?.status === "estimated" ? (
                      <a href={pdfHref(row, prov?.page)} target="_blank" rel="noreferrer" title={(prov as any)?.note || "Density-scaled estimate — EPD's stated method (annex p.70)"}>
                        p.{prov?.page}{printedLabel(row, prov?.page) ? ` (${printedLabel(row, prov?.page)})` : ""} · density-scaled est
                      </a>
                    ) : prov?.page ? (
                      <a href={pdfHref(row, prov.page)} target="_blank" rel="noreferrer" title={prov.section || undefined}>
                        p.{prov.page}
                        {printedLabel(row, prov.page) ? ` · printed ${printedLabel(row, prov.page)}` : ""}
                        {prov.section ? ` · ${clip(String(prov.section), 40)}` : ""}
                      </a>
                    ) : (prov as any)?.note ? (
                      <span title={(prov as any).note}>see boundary note</span>
                    ) : (
                      "—"
                    )}
                  </td>
                </tr>
              );
            })}
            {total.total != null && (
              <tr className="stage-total">
                <td>Total (GWP-total)</td>
                <td className="num">{total.total.toLocaleString()}</td>
                <td className="small" style={{ fontWeight: 400 }}>declared</td>
                <td className="small" style={{ fontWeight: 400 }}>{total.included.length} declared stage{total.included.length === 1 ? "" : "s"}</td>
                <td className="small" style={{ fontWeight: 400 }}>
                  {total.estTotal != null
                    ? <>{total.estTotal.toLocaleString()} incl. <span className="badge est">est</span> {formatModuleList(total.estIncluded)}</>
                    : "—"}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* other extracted GWP indicators */}
      {EXTRA_INDICATORS.some(([k]) => p.indicators?.[k]) && (
        <>
          <h3 style={{ marginTop: 24 }}>Other extracted GWP indicators</h3>
          <div className="tablewrap" style={{ marginTop: 8 }}>
            <table className="data">
              <thead>
                <tr>
                  <th>Indicator</th>
                  {DISPLAY_MODULES.map((m) => <th key={m} className="num">{m}</th>)}
                </tr>
              </thead>
              <tbody>
                {EXTRA_INDICATORS.filter(([k]) => p.indicators?.[k]).map(([k, label]) => (
                  <tr key={k}>
                    <td className="rowlabel">{label}</td>
                    {DISPLAY_MODULES.map((m) => {
                      const c = p.indicators[k]?.modules?.[m];
                      return (
                        <td key={m} className="num">
                          <StageValue cell={c} href={pdfHref(row, c?.provenance?.page)} printed={printedLabel(row, c?.provenance?.page)} />
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      {/* system boundary */}
      <h3 style={{ marginTop: 24 }}>System boundary (as declared by the EPD)</h3>
      <div className="tablewrap" style={{ marginTop: 8 }}>
        <table className="data">
          <thead>
            <tr>{DISPLAY_MODULES.map((m) => <th key={m} className="num">{m}</th>)}</tr>
          </thead>
          <tbody>
            <tr>
              {DISPLAY_MODULES.map((m) => {
                const s = row.systemBoundary?.[m];
                return (
                  <td key={m} className="num">
                    {s === "declared" ? "✓" : statusBadge((s as any) ?? "not_declared") ?? "—"}
                  </td>
                );
              })}
            </tr>
          </tbody>
        </table>
      </div>

      {/* EPD metadata + notes */}
      <h3 style={{ marginTop: 24 }}>EPD record &amp; extraction notes</h3>
      <div className="panel panel-pad" style={{ marginTop: 8 }}>
        <div className="small">
          <div><strong>Source PDF:</strong> <a href={pdfHref(row)} target="_blank" rel="noreferrer">{row.epd.source_pdf}</a> ({row.epd.pages} pages)</div>
          <div><strong>Programme:</strong> {row.epd.program_operator || "—"}</div>
          <div><strong>PCR:</strong> {row.epd.pcr || "—"}</div>
          <div><strong>Standard:</strong> {row.epd.reference_standard || row.epd.en15804_version || "—"}{row.epd.characterisation ? ` · ${row.epd.characterisation}` : ""}</div>
          <div><strong>Published / valid until:</strong> {row.epd.published || "—"} / {row.epd.valid_until || "—"}</div>
          <div><strong>Extraction confidence:</strong> {row.confidence}</div>
        </div>
        {row.comparabilityNotes?.length ? (
          <>
            <div className="small" style={{ marginTop: 10 }}><strong>Comparability notes</strong></div>
            <ul className="small" style={{ margin: "4px 0 0 16px" }}>
              {row.comparabilityNotes.map((n, i) => <li key={i}>{n}</li>)}
            </ul>
          </>
        ) : null}
        {row.needsReview?.length ? (
          <>
            <div className="small" style={{ marginTop: 10 }}><strong>Known gaps (not extracted — honesty over completeness)</strong></div>
            <ul className="small" style={{ margin: "4px 0 0 16px" }}>
              {row.needsReview.map((n, i) => <li key={i}>{n}</li>)}
            </ul>
          </>
        ) : null}
      </div>

      <div className="legend" style={{ marginTop: 14 }}>
        <span><span className="badge nd">ND</span> not declared (≠ 0)</span>
        <span><span className="badge nrep">not reported</span> in scope but unpublished (≠ 0)</span>
        <span><span className="badge est">est</span> derived by the EPD&apos;s stated method (not measured)</span>
        <span><span className="badge zero">0</span> declared as zero</span>
        <span><span className="badge nd">img</span> read from rasterised table</span>
      </div>
    </div>
  );
}
