"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import type { ProductRow } from "@/lib/types";

type CardData = {
  key: string;
  name: string;
  manufacturer: string;
  mpa: number | null;
  strengthClass: string | null;
  strengthStatus: string;
  location: string;
  country: string;
  program: string;
  a13: number | null;
  a13Page: number | null;
  unit: string;
  pdf: string;
  declaredModules: string[];
  declaredCount: number;
  confidence: string;
};

export default function Catalog({ cards }: { cards: CardData[] }) {
  const [minMpa, setMinMpa] = useState<string>("");
  const [maxMpa, setMaxMpa] = useState<string>("");
  const [loc, setLoc] = useState<string>("all");
  const [program, setProgram] = useState<string>("all");
  const [selected, setSelected] = useState<string[]>([]);
  const [sort, setSort] = useState<string>("a13");

  const locations = useMemo(
    () => Array.from(new Set(cards.map((c) => c.location).filter(Boolean))).sort(),
    [cards]
  );
  const programs = useMemo(
    () => Array.from(new Set(cards.map((c) => c.program).filter(Boolean))).sort(),
    [cards]
  );

  const filtered = useMemo(() => {
    let out = cards.filter((c) => {
      if (loc !== "all" && c.location !== loc) return false;
      if (program !== "all" && c.program !== program) return false;
      if (minMpa && (c.mpa == null || c.mpa < Number(minMpa))) return false;
      if (maxMpa && (c.mpa == null || c.mpa > Number(maxMpa))) return false;
      return true;
    });
    out = [...out].sort((a, b) => {
      if (sort === "a13") {
        if (a.a13 == null) return 1;
        if (b.a13 == null) return -1;
        return a.a13 - b.a13;
      }
      if (sort === "mpa") return (a.mpa ?? 0) - (b.mpa ?? 0);
      return a.name.localeCompare(b.name);
    });
    return out;
  }, [cards, loc, program, minMpa, maxMpa, sort]);

  function toggle(key: string) {
    setSelected((s) =>
      s.includes(key) ? s.filter((k) => k !== key) : s.length < 4 ? [...s, key] : s
    );
  }

  const compareHref = `/compare?keys=${encodeURIComponent(selected.join(","))}`;

  return (
    <div className="layout">
      <aside className="panel panel-pad filters">
        <h3>Filter</h3>
        <div className="filter-group">
          <label>Compressive strength (MPa)</label>
          <div className="range-row">
            <input type="number" placeholder="min" value={minMpa} onChange={(e) => setMinMpa(e.target.value)} />
            <span>to</span>
            <input type="number" placeholder="max" value={maxMpa} onChange={(e) => setMaxMpa(e.target.value)} />
          </div>
        </div>
        <div className="filter-group">
          <label>Manufacturing location</label>
          <select value={loc} onChange={(e) => setLoc(e.target.value)}>
            <option value="all">All locations</option>
            {locations.map((l) => (
              <option key={l} value={l}>{l}</option>
            ))}
          </select>
        </div>
        <div className="filter-group">
          <label>EPD programme</label>
          <select value={program} onChange={(e) => setProgram(e.target.value)}>
            <option value="all">All programmes</option>
            {programs.map((p) => (
              <option key={p} value={p}>{p}</option>
            ))}
          </select>
        </div>
        <div className="filter-group">
          <label>Sort by</label>
          <select value={sort} onChange={(e) => setSort(e.target.value)}>
            <option value="a13">A1–A3 carbon (low → high)</option>
            <option value="mpa">Strength (MPa)</option>
            <option value="name">Name</option>
          </select>
        </div>
        <div className="callout info" style={{ marginTop: 8 }}>
          A1–A3 (product stage) is only part of the story. Select products and open{" "}
          <strong>Compare</strong> to see every declared life-cycle stage side by side.
        </div>
      </aside>

      <section>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div className="result-count">
            {filtered.length} product{filtered.length === 1 ? "" : "s"} · {selected.length} selected
          </div>
          <div style={{ display: "flex", gap: 8 }}>
            {selected.length > 0 && (
              <button className="btn ghost" onClick={() => setSelected([])}>Clear</button>
            )}
            <Link
              href={compareHref}
              className="btn"
              aria-disabled={selected.length < 2}
              style={selected.length < 2 ? { pointerEvents: "none", opacity: 0.5 } : {}}
            >
              Compare {selected.length > 1 ? `(${selected.length})` : ""}
            </Link>
          </div>
        </div>

        <div className="grid">
          {filtered.map((c) => (
            <div className="card" key={c.key}>
              <div className="card-top">
                <div>
                  <h4>{c.name}</h4>
                  <div className="maker">{c.manufacturer || "—"}</div>
                </div>
                <div style={{ textAlign: "right" }}>
                  {c.mpa != null ? (
                    <span className="chip">{c.mpa} MPa</span>
                  ) : (
                    <span className="chip grey" title="Strength not stated in text">MPa ?</span>
                  )}
                </div>
              </div>

              <div className="headline">
                {c.a13 != null ? (
                  <>
                    <span className="num">{c.a13.toLocaleString(undefined, { maximumFractionDigits: 1 })}</span>
                    <span className="unit">{c.unit} · A1–A3</span>
                  </>
                ) : (
                  <span className="unit">A1–A3 not available</span>
                )}
              </div>

              <div className="meta-row">
                <span>📍 {c.location}</span>
                <span>🧱 {c.strengthClass || "—"}</span>
                <span>📄 {c.declaredCount} stages declared</span>
              </div>

              <div className="card-actions">
                <label>
                  <input
                    type="checkbox"
                    checked={selected.includes(c.key)}
                    onChange={() => toggle(c.key)}
                    disabled={!selected.includes(c.key) && selected.length >= 4}
                  />
                  Add to compare
                </label>
                <a className="prov" href={`/epds/${encodeURIComponent(c.pdf)}${c.a13Page ? `#page=${c.a13Page}` : ""}`} target="_blank" rel="noreferrer" style={{ marginLeft: "auto" }}>
                  source EPD ↗
                </a>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
