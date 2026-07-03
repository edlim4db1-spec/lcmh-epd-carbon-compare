import type { Cell, CellStatus } from "@/lib/types";

function fmt(n: number): string {
  const a = Math.abs(n);
  if (a !== 0 && (a < 0.01 || a >= 100000)) return n.toExponential(2);
  return n.toLocaleString(undefined, { maximumFractionDigits: 2 });
}

export function statusBadge(status: CellStatus) {
  if (status === "not_declared") return <span className="badge nd" title="Not declared — this stage is outside the EPD's system boundary">ND</span>;
  if (status === "not_relevant") return <span className="badge nr" title="Module not relevant">NR</span>;
  if (status === "not_reported") return <span className="badge nrep" title="In scope per the EPD's system boundary, but no value was published for it — not zero">not reported</span>;
  if (status === "missing") return <span className="badge nd" title="Missing / could not extract">—</span>;
  if (status === "estimated") return <span className="badge zero" title="Estimated">est</span>;
  return null;
}

export default function StageValue({
  cell,
  href,
  printed,
}: {
  cell?: Cell;
  href?: string;
  printed?: string | null;
}) {
  if (!cell || (cell.status !== "declared" && cell.status !== "declared_zero")) {
    return <span>{statusBadge(cell?.status ?? "not_declared")}</span>;
  }
  const val = typeof cell.value === "number" ? fmt(cell.value) : "—";
  const page = cell.provenance?.page;
  const isImage = cell.provenance?.source_type === "image";
  return (
    <span>
      <span className="mono">{val}</span>
      {isImage ? (
        <span className="badge nd" style={{ marginLeft: 6 }} title="Read from a rasterised table image (no text layer); verified visually">img</span>
      ) : null}
      {cell.status === "declared_zero" ? (
        <span className="badge zero" style={{ marginLeft: 6 }} title="Declared as zero (not missing)">0</span>
      ) : null}
      {href && page ? (
        <>
          {" "}
          <a
            className="prov"
            href={href}
            target="_blank"
            rel="noreferrer"
            title={`Source: ${cell.provenance?.section || "results table"} — raw ${cell.raw}${printed ? ` — printed page ${printed} on PDF sheet ${page}` : ""}`}
          >
            p.{page}{printed ? <span className="small">&thinsp;({printed})</span> : null}
          </a>
        </>
      ) : null}
    </span>
  );
}
