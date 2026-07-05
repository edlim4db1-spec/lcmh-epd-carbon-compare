import Link from "next/link";
import { loadEpds } from "@/lib/data";

export const dynamic = "force-static";

// Current-build phases (0–3 are the "happy path" lead-in; 4–7 rendered inline
// because they carry the gate checklist and the escalate/publish branch).
const LEAD_PHASES = [
  {
    n: "0",
    title: "Intake & triage",
    desc: "Classify the format, map physical vs printed pages, and lock the headline indicator to GWP-total EN 15804+A2 (not GWP-GHG, not the legacy +A1 table).",
    tool: "page_labels.py · §0 checklist",
  },
  {
    n: "1",
    title: "Inventory first",
    desc: "Enumerate every results table and give each an explicit disposition before extracting — so completeness is provable, not discovered page-by-page as a reviewer surfaces gaps.",
    tool: "table ledger · disposition per table",
  },
  {
    n: "2",
    title: "Deterministic extraction",
    desc: "Parse each cell with its status and verbatim provenance. The same discipline covers non-carbon facts — strength, location, unit — each clicking through to its exact source page.",
    tool: "extract.py · lib_parse · lib_tables",
  },
  {
    n: "3",
    title: "Derive — only if the EPD sanctions it",
    desc: "Where the document states a method for a value it does not print per product, apply that exact method and label the result estimated, citing the representative table and the method page.",
    tool: "R11 · density-scaled · never declared",
  },
];

const GATES = [
  ["schema", "structure + status enum legal — a not-declared cell can never carry a value"],
  ["cross_validate", "every stored raw value appears literally on the page it cites"],
  ["qa", "internal consistency — A1+A2+A3 ≈ A1–A3, boundary vs status, dates vs registry"],
  ["verify_independent + teamC", "2nd and 3rd engines re-extract, diffed cell-by-cell"],
  ["registry", "every family→variant label checked against the document's registry"],
  ["completeness", "Σ values on a sheet equals Σ mixes mapped from it (no dropped table)"],
];

const LOOP_POINTS = [
  ["Inventory consensus", "Several agents must agree on the table count and dispositions before extraction begins."],
  ["Ensemble extraction", "One table read by independent methods; a value ships only when they agree on the identical raw string."],
  ["Derived self-consistency", "Recompute each estimate until it reproduces the EPD's own worked example."],
  ["Verify → repair", "Feed every gate failure back to a fixer and re-run until all six are green."],
  ["Adversarial red-team", "A challenger tries to break each value — wrong page, wrong column, wrong label, totals — and anything it breaks re-enters the loop."],
];

const CONTRACT = [
  ["Independent evidence", "Agreement between different methods, never one parser trusted on its own."],
  ["Bounded", "A hard iteration cap — the loop can converge or stop, never spin forever."],
  ["Convergence test", "An explicit “agreed” criterion (identical raw, gate-green, example reproduced), not “looks done”."],
  ["Escalate, never guess", "Residuals become labelled gaps in needs_review — never an invented value."],
];

export default function Pipeline() {
  const docs = loadEpds();
  const products = docs.reduce((n, d) => n + d.products.length, 0);

  return (
    <div className="container pipeline" style={{ padding: "26px 0 60px" }}>
      <h1>How the extraction engine works</h1>
      <p className="small" style={{ maxWidth: 720, marginTop: 6, fontSize: 13.5 }}>
        What a new EPD PDF passes through, end to end — from intake to a published,
        source-traceable record. Every step preserves the same provenance chain, and nothing
        reaches the app until six independent checks pass.
      </p>

      <div className="metricstrip">
        <div className="m"><div className="n">{docs.length}</div><div className="l">EPDs · one JSON each</div></div>
        <div className="m"><div className="n">{products}</div><div className="l">products extracted</div></div>
        <div className="m"><div className="n">6</div><div className="l">verification gates</div></div>
        <div className="m"><div className="n">~760</div><div className="l">cells cross-checked · 0 mismatches</div></div>
      </div>

      <h3 style={{ marginBottom: 14 }}>Current build — end to end</h3>

      {LEAD_PHASES.map((p) => (
        <div className="pstep" key={p.n}>
          <div className="prail"><span className="pdot">{p.n}</span><span className="pline" /></div>
          <div className="pcard">
            <h3>{p.title}</h3>
            <p>{p.desc}</p>
            <span className="tool">{p.tool}</span>
          </div>
        </div>
      ))}

      {/* Phase 4 — the hard gate */}
      <div className="pstep">
        <div className="prail"><span className="pdot ok">4</span><span className="pline" /></div>
        <div className="pcard ok">
          <h3>Verify — six gates, zero tolerance</h3>
          <p>A JSON file does not reach the app unless all six pass on the real dataset.</p>
          <ul className="pgates">
            {GATES.map(([name, desc]) => (
              <li key={name}><span className="tick">✓</span><span><b>{name}</b> — {desc}</span></li>
            ))}
          </ul>
          <div className="pbranch">
            <span className="tag ok">all green → publish</span>
            <span className="tag warn">any cell unverified → flag, never guess</span>
          </div>
        </div>
      </div>

      {/* Phase 5 — escalate */}
      <div className="pstep">
        <div className="prail"><span className="pdot warn">5</span><span className="pline" /></div>
        <div className="pcard warn">
          <h3>Escalate the un-mappable</h3>
          <p>
            Anything a gate cannot verify goes to <span className="mono">needs_review</span> — surfaced in
            the app as a labelled gap, cited and in plain English. Never invented, never shown as a zero.
          </p>
          <span className="tool">honest gap · resumable from the inventory</span>
        </div>
      </div>

      {/* Phase 6 — publish */}
      <div className="pstep">
        <div className="prail"><span className="pdot ok">6</span><span className="pline" /></div>
        <div className="pcard ok">
          <h3>Publish &amp; render</h3>
          <p>
            The validated record renders with no per-EPD code: the{" "}
            <Link href="/">catalog</Link>, the product audit view (mirrors the source table, two
            totals), and the <Link href="/compare">comparison view</Link> — every figure clicking
            back to its source PDF and page.
          </p>
          <span className="tool">catalog · audit · compare</span>
        </div>
      </div>

      {/* Phase 7 — feedback */}
      <div className="pstep">
        <div className="prail"><span className="pdot">7</span></div>
        <div className="pcard">
          <h3>Feedback loop</h3>
          <p>
            Any new trap a document surfaces becomes a documented rule, a risk entry, and — where
            possible — an automated gate. The same mistake cannot recur; each pass starts from a
            larger map.
          </p>
          <span className="tool">field guide R# · RISKS.md · memory</span>
        </div>
      </div>

      {/* Next phase — agent-in-loop layer, clearly forward-looking */}
      <div style={{ marginTop: 40 }}>
        <span className="looptag">Next phase</span>
        <h3 style={{ margin: "12px 0 0" }}>Agent-in-loop accuracy layer</h3>
      </div>
      <div className="callout info" style={{ marginTop: 10 }}>
        <strong>Planned — built after the first review.</strong> This wraps an orchestration layer
        around the same six gates above; it is an additive upgrade, not a rewrite. The goal is to push
        accuracy toward no margin of error even on formats never seen before.
      </div>

      <p className="small" style={{ fontSize: 13.5, marginTop: 4 }}>
        The essence: extraction becomes <em>converge-or-escalate</em>. The document is read by several
        independent methods and reconciled cell-by-cell — a value ships only when the methods agree on
        the identical raw string and it traces to its source page. Anything they cannot agree on is
        re-worked within a bounded budget, and otherwise escalated to a labelled gap. Accuracy comes
        from requiring agreement between methods, not from trusting any single parser.
      </p>

      <h4 style={{ margin: "20px 0 0", fontSize: 14 }}>Where the loops sit</h4>
      <div className="loopgrid">
        {LOOP_POINTS.map(([t, d]) => (
          <div className="loopcard" key={t}><h4>{t}</h4><p>{d}</p></div>
        ))}
      </div>

      <h4 style={{ margin: "22px 0 0", fontSize: 14 }}>What keeps a loop safe (the contract)</h4>
      <div className="loopgrid">
        {CONTRACT.map(([t, d]) => (
          <div className="loopcard" key={t}><h4>{t}</h4><p>{d}</p></div>
        ))}
      </div>

      <p className="small" style={{ fontSize: 13.5, marginTop: 18 }}>
        The validators already in the current build become the loop&apos;s scoring functions — today
        they run once at the end; the loop runs them every iteration and steers by their output. So the
        core invariant is unchanged: no figure ships without independent agreement and full provenance.
      </p>

      <p style={{ marginTop: 22 }}>
        <Link href="/methodology" className="btn secondary">Read the methodology →</Link>
      </p>
    </div>
  );
}
