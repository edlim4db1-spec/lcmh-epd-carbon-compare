"use client";

import { useState } from "react";

// Animated end-to-end view of the scaled extraction engine: LLM routing by
// difficulty, per-stage cost, verification gates, and the feedback flywheel.
// Costs are illustrative estimates of a routed + cached pipeline, not quotes.

const LANE_STD = "#059669"; // teal — standard lane (Sonnet)
const LANE_HARD = "#7c5cd6"; // violet — hard lane (Opus)
const LANE_FLY = "#b45309"; // amber — flywheel / review

function money(v: number): string {
  if (v >= 1000) return "$" + (v / 1000).toFixed(v >= 10000 ? 0 : 1) + "k";
  if (v >= 100) return "$" + Math.round(v);
  return "$" + v.toFixed(2);
}

export default function EngineFlow() {
  const [n, setN] = useState(100);
  const [hPct, setHPct] = useState(20);
  const h = hPct / 100;
  const lo = n * ((1 - h) * 0.15 + h * 0.6);
  const hi = n * ((1 - h) * 0.35 + h * 1.2);
  const mLo = n * 80;
  const mHi = n * 450;

  return (
    <div>
      <svg width="100%" viewBox="0 0 680 610" role="img" style={{ display: "block", marginTop: 8 }}>
        <title>EPD extraction engine — animated flow</title>
        <desc>
          PDFs flow from intake through Haiku triage, route to a Sonnet or Opus lane by
          difficulty, reconcile cell-by-cell, pass six gates, then publish or escalate;
          a flywheel returns lessons to the start.
        </desc>
        <defs>
          <marker id="engine-ah" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto">
            <path d="M1,1 L7,4 L1,7" fill="none" stroke="#9aa8a0" strokeWidth="1.6" />
          </marker>
        </defs>

        <line className="engine-flowline" x1="146" y1="62" x2="200" y2="62" markerEnd="url(#engine-ah)" />
        <line className="engine-flowline" x1="376" y1="62" x2="430" y2="62" markerEnd="url(#engine-ah)" />
        <path className="engine-flowline" d="M511,94 C511,132 485,128 485,158" markerEnd="url(#engine-ah)" />
        <path className="engine-flowline" d="M511,94 C511,132 200,118 200,158" markerEnd="url(#engine-ah)" />
        <path className="engine-flowline" d="M485,234 C485,262 340,252 340,278" markerEnd="url(#engine-ah)" />
        <path className="engine-flowline" d="M200,234 C200,262 340,252 340,278" markerEnd="url(#engine-ah)" />
        <line className="engine-flowline" x1="340" y1="344" x2="340" y2="368" markerEnd="url(#engine-ah)" />
        <path className="engine-flowline" d="M340,444 C340,482 540,472 540,508" markerEnd="url(#engine-ah)" />
        <path className="engine-flowline" d="M340,444 C340,482 140,472 140,508" markerEnd="url(#engine-ah)" />
        <path d="M36,510 C6,400 6,140 200,64" fill="none" stroke={LANE_FLY} strokeWidth="1.3" strokeDasharray="3 5" opacity="0.75" />

        <rect x="16" y="30" width="130" height="64" rx="10" fill="#fff" stroke="#d5ded8" />
        <text x="81" y="56" textAnchor="middle" fontSize="13" fontWeight="700" fill="#212121">EPD PDF in</text>
        <text x="81" y="74" textAnchor="middle" fontSize="11" fill="#5c6b63">any format · any layout</text>

        <rect x="206" y="30" width="170" height="64" rx="10" fill="#fff" stroke="#d5ded8" />
        <text x="291" y="50" textAnchor="middle" fontSize="13" fontWeight="700" fill="#212121">Triage</text>
        <text x="291" y="66" textAnchor="middle" fontSize="11" fill={LANE_FLY}>Haiku 4.5 · $1/$5 per 1M</text>
        <text x="291" y="82" textAnchor="middle" fontSize="11" fill="#5c6b63">≈ $0.01–0.03 per EPD</text>

        <rect x="436" y="30" width="150" height="64" rx="10" fill="#fff" stroke="#d5ded8" />
        <text x="511" y="56" textAnchor="middle" fontSize="13" fontWeight="700" fill="#212121">Route by difficulty</text>
        <text x="511" y="74" textAnchor="middle" fontSize="11" fill="#5c6b63">template · text vs image</text>

        <text x="468" y="130" fontSize="11" fill={LANE_STD}>≈80%</text>
        <text x="292" y="118" fontSize="11" fill={LANE_HARD}>≈20%</text>

        <rect x="370" y="158" width="230" height="76" rx="10" fill="#fff" stroke={LANE_STD} />
        <text x="485" y="180" textAnchor="middle" fontSize="13" fontWeight="700" fill="#212121">Standard extraction</text>
        <text x="485" y="197" textAnchor="middle" fontSize="11" fill={LANE_STD}>Sonnet 5 · $3/$15 (intro $2/$10)</text>
        <text x="485" y="214" textAnchor="middle" fontSize="11" fill="#5c6b63">clean text layer · ≈ $0.10–0.30</text>

        <rect x="80" y="158" width="240" height="76" rx="10" fill="#fff" stroke={LANE_HARD} />
        <text x="200" y="180" textAnchor="middle" fontSize="13" fontWeight="700" fill="#212121">Hard cases</text>
        <text x="200" y="197" textAnchor="middle" fontSize="11" fill={LANE_HARD}>Opus 4.8 · $5/$25 per 1M</text>
        <text x="200" y="214" textAnchor="middle" fontSize="11" fill="#5c6b63">image tables · multi-plant · ≈ $0.30–0.90</text>

        <rect x="215" y="278" width="250" height="66" rx="10" fill="#fff" stroke="#d5ded8" />
        <text x="340" y="300" textAnchor="middle" fontSize="13" fontWeight="700" fill="#212121">Reconcile — agree or retry</text>
        <text x="340" y="317" textAnchor="middle" fontSize="11" fill="#5c6b63">independent engines must produce the</text>
        <text x="340" y="331" textAnchor="middle" fontSize="11" fill="#5c6b63">identical raw string, cell by cell</text>

        <rect x="215" y="368" width="250" height="76" rx="10" fill="var(--teal-50)" stroke="var(--teal-100)" />
        <text x="340" y="390" textAnchor="middle" fontSize="13" fontWeight="700" fill="var(--teal-900)">Six zero-tolerance gates</text>
        <text x="340" y="407" textAnchor="middle" fontSize="11" fill="var(--teal-700)">provenance · schema · QA · engines</text>
        <text x="340" y="421" textAnchor="middle" fontSize="11" fill="var(--teal-700)">registry · completeness — run free (Python)</text>
        <text x="340" y="437" textAnchor="middle" fontSize="11" fill="var(--teal-700)">all green → ship · anything else → flag</text>

        <rect x="430" y="508" width="220" height="66" rx="10" fill="var(--teal-50)" stroke="var(--teal-100)" />
        <text x="540" y="532" textAnchor="middle" fontSize="13" fontWeight="700" fill="var(--teal-900)">Published</text>
        <text x="540" y="549" textAnchor="middle" fontSize="11" fill="var(--teal-700)">every figure traceable to its page</text>

        <rect x="30" y="508" width="220" height="66" rx="10" fill="var(--warn-bg)" stroke="var(--warn-line)" />
        <text x="140" y="532" textAnchor="middle" fontSize="13" fontWeight="700" fill="var(--warn-ink)">needs_review</text>
        <text x="140" y="549" textAnchor="middle" fontSize="11" fill="var(--warn-ink)">flagged honestly — never guessed</text>

        <text x="20" y="300" fontSize="11" fill={LANE_FLY} transform="rotate(-90 20 300)">flywheel: trap → rule + gate</text>

        <circle r="5" fill={LANE_STD}>
          <animateMotion dur="9s" begin="0s" repeatCount="indefinite" path="M20,62 L511,62 C511,132 485,128 485,196 C485,262 340,252 340,310 L340,406 C340,482 540,472 540,541" />
        </circle>
        <circle r="5" fill={LANE_STD}>
          <animateMotion dur="9s" begin="-3s" repeatCount="indefinite" path="M20,62 L511,62 C511,132 485,128 485,196 C485,262 340,252 340,310 L340,406 C340,482 540,472 540,541" />
        </circle>
        <circle r="5" fill={LANE_STD}>
          <animateMotion dur="9s" begin="-6s" repeatCount="indefinite" path="M20,62 L511,62 C511,132 485,128 485,196 C485,262 340,252 340,310 L340,406 C340,482 540,472 540,541" />
        </circle>
        <circle r="5" fill={LANE_HARD}>
          <animateMotion dur="10s" begin="-1.5s" repeatCount="indefinite" path="M20,62 L511,62 C511,132 200,118 200,196 C200,262 340,252 340,310 L340,406 C340,482 140,472 140,541" />
        </circle>
        <circle r="5" fill={LANE_HARD}>
          <animateMotion dur="10s" begin="-6.5s" repeatCount="indefinite" path="M20,62 L511,62 C511,132 200,118 200,196 C200,262 340,252 340,310 L340,406 C340,482 140,472 140,541" />
        </circle>
        <circle r="4" fill={LANE_FLY}>
          <animateMotion dur="12s" begin="-4s" repeatCount="indefinite" path="M36,510 C6,400 6,140 200,64" />
        </circle>
      </svg>

      <div className="engine-legend">
        <span className="engine-chip">Haiku 4.5 — $1/$5 · triage</span>
        <span className="engine-chip">Sonnet 5 — $3/$15 · standard</span>
        <span className="engine-chip">Opus 4.8 — $5/$25 · hard + red-team</span>
        <span className="engine-chip">Frontier models — only where evals prove the gain</span>
        <span className="engine-chip">cached playbook: reads ≈0.1×</span>
      </div>

      <div className="costcards">
        <div className="costcard">
          <h4>Clean text EPD (≈80%)</h4>
          <ul>
            <li><span>Triage — Haiku</span><b>$0.01–0.03</b></li>
            <li><span>Extract — Sonnet ×2 passes</span><b>$0.10–0.25</b></li>
            <li><span>Cross-check + gates</span><b>$0.04–0.07</b></li>
            <li className="tot"><span>Per EPD</span><b>$0.15–0.35</b></li>
          </ul>
        </div>
        <div className="costcard">
          <h4>Hard EPD (≈20%)</h4>
          <ul>
            <li><span>Triage — Haiku</span><b>$0.01–0.03</b></li>
            <li><span>Extract — Sonnet</span><b>$0.10–0.30</b></li>
            <li><span>Opus reconcile + vision</span><b>$0.30–0.90</b></li>
            <li className="tot"><span>Per EPD</span><b>$0.60–1.20</b></li>
          </ul>
        </div>
        <div className="costcard">
          <h4>Blended at volume</h4>
          <ul>
            <li><span>Routed + cached</span><b>&lt; $1 / EPD</b></li>
            <li><span>Known template, marginal</span><b>$0.10–0.50</b></li>
            <li><span>Extracted cells (code)</span><b>≈ $0</b></li>
            <li className="tot"><span>Manual assessment</span><b>$80–450 / EPD</b></li>
          </ul>
        </div>
      </div>

      <div className="engine-calc">
        <h4>Cost calculator (illustrative)</h4>
        <div className="row">
          <label>
            EPDs per month: {n}
            <input type="range" min={10} max={1000} step={10} value={n} onChange={(e) => setN(Number(e.target.value))} />
          </label>
          <label>
            Hard-case share: {hPct}%
            <input type="range" min={0} max={60} step={5} value={hPct} onChange={(e) => setHPct(Number(e.target.value))} />
          </label>
        </div>
        <div className="engine-res">
          <div className="r"><div className="n">{money(lo)}–{money(hi)}</div><div className="l">AI pipeline / month</div></div>
          <div className="r"><div className="n">${(lo / n).toFixed(2)}–{(hi / n).toFixed(2)}</div><div className="l">blended per EPD</div></div>
          <div className="r"><div className="n">{money(mLo)}–{money(mHi)}</div><div className="l">manual assessment / month</div></div>
          <div className="r"><div className="n">×{Math.round(mLo / hi)}–{Math.round(mHi / lo)}</div><div className="l">cheaper — with stronger provenance</div></div>
        </div>
      </div>
    </div>
  );
}
