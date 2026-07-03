import Link from "next/link";
import { loadEpds } from "@/lib/data";

export const dynamic = "force-static";

export default function Methodology() {
  const docs = loadEpds();
  const total = docs.reduce((n, d) => n + d.products.length, 0);
  return (
    <div className="container" style={{ padding: "26px 0 60px", maxWidth: 820 }}>
      <h1>How to read these numbers</h1>
      <p className="small">
        {docs.length} EPDs · {total} products. Full reasoning is in{" "}
        <span className="mono">EXTRACTION.md</span> in the repository.
      </p>

      <h3>Provenance</h3>
      <p>
        Every carbon figure is traceable to its source EPD: PDF file, page, results-table
        section, life-cycle module, unit, and the verbatim value as printed. The numbers were
        extracted deterministically (coordinate/order-bound table parsing) and then
        machine-checked — each stored value must appear literally on the page it cites — so a
        figure can never be a transcription invented by a model.
      </p>

      <h3>Page citations</h3>
      <p>
        Cited pages (<span className="mono">p.N</span>) are <em>physical PDF sheets</em> — what your
        PDF viewer and our links target. Two documents number their printed pages differently
        (a booklet spread printing two folios per sheet, and one with unnumbered front matter);
        for those, citations also show the printed folio, e.g.{" "}
        <span className="mono">p.11 (20–21)</span>. The link always lands on the right sheet.
      </p>

      <h3>A not-declared stage is not zero</h3>
      <p>
        EPDs declare different life-cycle modules. Where a module (e.g. A4 transport, A5
        installation, or the C end-of-life stages) is not reported, it is shown as{" "}
        <span className="badge nd">ND</span> and excluded from any total — never silently
        treated as 0. A declared zero is shown distinctly as <span className="badge zero">0</span>.
      </p>

      <h3>Comparability</h3>
      <p>
        Two products are only directly comparable when they declare the same modules, on the
        same declared unit, under the same standard. The compare view flags when they don&apos;t.
        The headline A1–A3 number is the product stage only; use the full stage-by-stage table
        to make a real decision.
      </p>

      <h3>What we deliberately did not do</h3>
      <ul>
        <li>Fill missing modules with 0 to make totals look complete.</li>
        <li>Infer compressive strength from a product code — only from stated text.</li>
        <li>Mix GWP indicators (GWP-total EN 15804+A2 is used, not the legacy GWP-GHG or +A1/CML variants).</li>
      </ul>

      <p style={{ marginTop: 20 }}>
        <Link href="/" className="btn secondary">← Back to products</Link>
      </p>
    </div>
  );
}
