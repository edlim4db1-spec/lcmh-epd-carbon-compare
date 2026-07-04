"use client";

import { useMemo, useState } from "react";
import Link from "next/link";

type CardData = {
  key: string;
  epdId: string;
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
  epdOrdinal: number;
  epdSiblings: number;
};

export default function Catalog({ cards }: { cards: CardData[] }) {
  const [query, setQuery] = useState("");
  const [minMpa, setMinMpa] = useState("");
  const [maxMpa, setMaxMpa] = useState("");
  const [loc, setLoc] = useState("all");
  const [program, setProgram] = useState("all");
  const [selected, setSelected] = useState<string[]>([]);
  const [sort, setSort] = useState("mpa"); // default: compressive strength (per brief's filters)
  const [expanded, setExpanded] = useState<Set<string>>(new Set());

  const locations = useMemo(() => Array.from(new Set(cards.map((c) => c.location).filter(Boolean))).sort(), [cards]);
  const programs = useMemo(() => Array.from(new Set(cards.map((c) => c.program).filter(Boolean))).sort(), [cards]);

  const filterActive = query !== "" || loc !== "all" || program !== "all" || minMpa !== "" || maxMpa !== "";

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    let out = cards.filter((c) => {
      if (q && !`${c.name} ${c.manufacturer} ${c.epdId} ${c.location} ${c.strengthClass ?? ""}`.toLowerCase().includes(q)) return false;
      if (loc !== "all" && c.location !== loc) return false;
      if (program !== "all" && c.program !== program) return false;
      if (minMpa && (c.mpa == null || c.mpa < Number(minMpa))) return false;
      if (maxMpa && (c.mpa == null || c.mpa > Number(maxMpa))) return false;
      return true;
    });
    out = [...out].sort((a, b) => {
      if (sort === "mpa") {
        const d = (a.mpa ?? Infinity) - (b.mpa ?? Infinity);
        return d !== 0 ? d : (a.a13 ?? Infinity) - (b.a13 ?? Infinity); // then greenest first
      }
      if (sort === "a13") return (a.a13 ?? Infinity) - (b.a13 ?? Infinity);
      return a.name.localeCompare(b.name);
    });
    return out;
  }, [cards, query, loc, program, minMpa, maxMpa, sort]);

  // group filtered products by EPD, preserving sorted order (first appearance)
  const groups = useMemo(() => {
    const m = new Map<string, CardData[]>();
    for (const c of filtered) (m.get(c.pdf) ?? m.set(c.pdf, []).get(c.pdf)!).push(c);
    return Array.from(m.entries()).map(([pdf, cs]) => ({ pdf, cards: cs }));
  }, [filtered]);

  function toggle(key: string) {
    setSelected((s) => (s.includes(key) ? s.filter((k) => k !== key) : s.length < 4 ? [...s, key] : s));
  }
  function toggleExpand(pdf: string) {
    setExpanded((s) => {
      const n = new Set(s);
      n.has(pdf) ? n.delete(pdf) : n.add(pdf);
      return n;
    });
  }

  const compareHref = `/compare?keys=${encodeURIComponent(selected.join(","))}`;
  const fmt = (n: number) => n.toLocaleString(undefined, { maximumFractionDigits: 0 });

  function ProductCard({ c }: { c: CardData }) {
    return (
      <div className="card" key={c.key}>
        <div className="card-top">
          <div>
            <h4>
              <Link href={`/product?key=${encodeURIComponent(c.key)}`} title="View full extraction — every stage with provenance">
                {c.name}
              </Link>
            </h4>
            <div className="maker">{c.manufacturer || "—"}</div>
          </div>
          <div style={{ textAlign: "right" }}>
            {c.mpa != null ? <span className="chip">{c.mpa} MPa</span> : <span className="chip grey" title="Strength not stated in text">MPa ?</span>}
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
          <span>{c.location}</span>
          <span>{c.strengthClass ? `class ${c.strengthClass}` : "class —"}</span>
          <span>{c.declaredCount} stages declared</span>
        </div>
        <div className="card-actions">
          <label>
            <input type="checkbox" checked={selected.includes(c.key)} onChange={() => toggle(c.key)}
              disabled={!selected.includes(c.key) && selected.length >= 4} />
            Add to compare
          </label>
          <a className="prov" href={`/epds/${encodeURIComponent(c.pdf)}${c.a13Page ? `#page=${c.a13Page}` : ""}`} target="_blank" rel="noreferrer" style={{ marginLeft: "auto" }}>
            source EPD ↗
          </a>
        </div>
      </div>
    );
  }

  function GroupBlock({ pdf, cs }: { pdf: string; cs: CardData[] }) {
    const isOpen = expanded.has(pdf) || filterActive;
    const mpas = cs.map((c) => c.mpa).filter((v): v is number => v != null);
    const a13s = cs.map((c) => c.a13).filter((v): v is number => v != null);
    const plants = Array.from(new Set(cs.map((c) => c.location)));
    const title = cs[0].manufacturer || cs[0].epdId;

    if (!isOpen) {
      return (
        <div className="card group-card" onClick={() => toggleExpand(pdf)} role="button" tabIndex={0}>
          <div className="card-top">
            <div>
              <h4>{title}</h4>
              <div className="maker">{cs.length} products · {plants.length} plant{plants.length === 1 ? "" : "s"} · one EPD</div>
            </div>
            <div style={{ textAlign: "right" }}>
              {mpas.length ? <span className="chip">{Math.min(...mpas)}–{Math.max(...mpas)} MPa</span> : null}
            </div>
          </div>
          <div className="headline">
            {a13s.length ? (
              <>
                <span className="num">{fmt(Math.min(...a13s))}–{fmt(Math.max(...a13s))}</span>
                <span className="unit">kg CO₂e / m³ · A1–A3 range</span>
              </>
            ) : null}
          </div>
          <div className="meta-row"><span>{plants.join(" · ")}</span></div>
          <div className="card-actions">
            <button className="btn secondary" onClick={(e) => { e.stopPropagation(); toggleExpand(pdf); }}>
              Expand {cs.length} products ▾
            </button>
          </div>
        </div>
      );
    }

    // expanded: full-width, products sub-grouped by plant
    const byPlant = new Map<string, CardData[]>();
    for (const c of cs) (byPlant.get(c.location) ?? byPlant.set(c.location, []).get(c.location)!).push(c);
    return (
      <div className="group-expanded" style={{ gridColumn: "1 / -1" }}>
        <div className="group-head">
          <div>
            <strong>{title}</strong> · {cs.length} products across {plants.length} plant{plants.length === 1 ? "" : "s"} · one EPD
          </div>
          {!filterActive && (
            <button className="btn ghost" onClick={() => toggleExpand(pdf)}>Collapse ▴</button>
          )}
        </div>
        {Array.from(byPlant.entries()).map(([plant, pcs]) => {
          // within each plant, group variants under their mix family (first name token)
          const byFamily = new Map<string, CardData[]>();
          for (const c of pcs) {
            const fam = c.name.split(" ")[0];
            (byFamily.get(fam) ?? byFamily.set(fam, []).get(fam)!).push(c);
          }
          return (
            <div key={plant}>
              {plants.length > 1 && <div className="plant-subhead">{plant} <span className="small">({pcs.length})</span></div>}
              {Array.from(byFamily.entries()).map(([fam, fcs]) => (
                <div key={fam} className="mix-family">
                  <div className="mix-subhead">
                    {fam}
                    <span className="small">
                      {fcs[0].mpa != null ? ` · ${fcs[0].mpa} MPa` : ""} · {fcs.length} variant{fcs.length === 1 ? "" : "s"}
                    </span>
                  </div>
                  <div className="grid">
                    {fcs.map((c) => <ProductCard c={c} key={c.key} />)}
                  </div>
                </div>
              ))}
            </div>
          );
        })}
      </div>
    );
  }

  const totalProducts = filtered.length;

  return (
    <div className="layout">
      <aside className="panel panel-pad filters">
        <h3>Filter</h3>
        <div className="filter-group">
          <label>Search</label>
          <input type="text" placeholder="mix, supplier, plant…" value={query}
            onChange={(e) => setQuery(e.target.value)} aria-label="Search products" />
        </div>
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
            {locations.map((l) => <option key={l} value={l}>{l}</option>)}
          </select>
        </div>
        <div className="filter-group">
          <label>EPD programme</label>
          <select value={program} onChange={(e) => setProgram(e.target.value)}>
            <option value="all">All programmes</option>
            {programs.map((p) => <option key={p} value={p}>{p}</option>)}
          </select>
        </div>
        <div className="filter-group">
          <label>Sort by</label>
          <select value={sort} onChange={(e) => setSort(e.target.value)}>
            <option value="mpa">Compressive strength (then carbon)</option>
            <option value="a13">A1–A3 carbon (low → high)</option>
            <option value="name">Name</option>
          </select>
        </div>
        <div className="callout info" style={{ marginTop: 8 }}>
          A1–A3 (product stage) is only part of the story. Select products and open{" "}
          <strong>Compare</strong> to see every declared life-cycle stage side by side.
        </div>
      </aside>

      <section>
        <div className="results-bar">
          <div className="result-count">
            {groups.length} EPD{groups.length === 1 ? "" : "s"} · {totalProducts} product{totalProducts === 1 ? "" : "s"} · {selected.length} selected
          </div>
          <div className="actions">
            {selected.length > 0 && <button className="btn ghost" onClick={() => setSelected([])}>Clear</button>}
            <Link href={compareHref} className="btn"
              aria-disabled={selected.length < 2}
              style={selected.length < 2 ? { pointerEvents: "none", opacity: 0.5 } : {}}>
              Compare {selected.length > 1 ? `(${selected.length})` : ""}
            </Link>
          </div>
        </div>

        <div className="grid">
          {groups.map((g) =>
            g.cards.length === 1
              ? <ProductCard c={g.cards[0]} key={g.pdf} />
              : <GroupBlock pdf={g.pdf} cs={g.cards} key={g.pdf} />
          )}
        </div>
      </section>
    </div>
  );
}
