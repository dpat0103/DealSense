"use client";

import { useMemo, useState } from "react";
import { searchListings, type SearchItem } from "../lib/api";

function money(n: number) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(n);
}

function badgeStyle(b: string) {
  if (b === "GREAT")
    return {
      background: "rgba(34,197,94,0.2)",
      border: "1px solid rgba(34,197,94,0.5)",
    };
  if (b === "FAIR")
    return {
      background: "rgba(250,204,21,0.2)",
      border: "1px solid rgba(250,204,21,0.5)",
    };
  return {
    background: "rgba(239,68,68,0.2)",
    border: "1px solid rgba(239,68,68,0.5)",
  };
}

export default function HomePage() {
  const [make, setMake] = useState("honda");
  const [model, setModel] = useState("civic");
  const [stateCode, setStateCode] = useState("");
  const [yearMin, setYearMin] = useState("2018");
  const [yearMax, setYearMax] = useState("2022");
  const [mileageMax, setMileageMax] = useState("90000");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<SearchItem[]>([]);
  const [error, setError] = useState<string | null>(null);

  const params = useMemo(() => {
    const p: Record<string, string> = {};
    if (make.trim()) p.make = make.trim().toLowerCase();
    if (model.trim()) p.model = model.trim().toLowerCase();
    if (stateCode.trim()) p.state = stateCode.trim().toLowerCase();
    if (yearMin.trim()) p.year_min = yearMin.trim();
    if (yearMax.trim()) p.year_max = yearMax.trim();
    if (mileageMax.trim()) p.mileage_max = mileageMax.trim();
    p.limit = "60";
    return p;
  }, [make, model, stateCode, yearMin, yearMax, mileageMax]);

  async function runSearch() {
    setLoading(true);
    setError(null);
    try {
      const data = await searchListings(params);
      setResults(data.results);
    } catch (e: any) {
      setError(e?.message ?? "Failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(6, 1fr)",
          gap: 10,
          padding: 14,
          borderRadius: 14,
          background: "#121826",
          border: "1px solid rgba(255,255,255,0.08)",
        }}
      >
        <label style={{ display: "grid", gap: 6 }}>
          <span style={{ opacity: 0.8, fontSize: 12 }}>Make</span>
          <input
            value={make}
            onChange={(e) => setMake(e.target.value)}
            style={inputStyle}
          />
        </label>

        <label style={{ display: "grid", gap: 6 }}>
          <span style={{ opacity: 0.8, fontSize: 12 }}>Model</span>
          <input
            value={model}
            onChange={(e) => setModel(e.target.value)}
            style={inputStyle}
          />
        </label>

        <label style={{ display: "grid", gap: 6 }}>
          <span style={{ opacity: 0.8, fontSize: 12 }}>State (optional)</span>
          <input
            value={stateCode}
            onChange={(e) => setStateCode(e.target.value)}
            placeholder="nj"
            style={inputStyle}
          />
        </label>

        <label style={{ display: "grid", gap: 6 }}>
          <span style={{ opacity: 0.8, fontSize: 12 }}>Year min</span>
          <input
            value={yearMin}
            onChange={(e) => setYearMin(e.target.value)}
            style={inputStyle}
          />
        </label>

        <label style={{ display: "grid", gap: 6 }}>
          <span style={{ opacity: 0.8, fontSize: 12 }}>Year max</span>
          <input
            value={yearMax}
            onChange={(e) => setYearMax(e.target.value)}
            style={inputStyle}
          />
        </label>

        <label style={{ display: "grid", gap: 6 }}>
          <span style={{ opacity: 0.8, fontSize: 12 }}>Mileage max</span>
          <input
            value={mileageMax}
            onChange={(e) => setMileageMax(e.target.value)}
            style={inputStyle}
          />
        </label>

        <button
          onClick={runSearch}
          disabled={loading}
          style={{
            gridColumn: "1 / -1",
            padding: "12px 14px",
            borderRadius: 12,
            background: loading ? "rgba(157,180,255,0.35)" : "#9db4ff",
            color: "#0b0d12",
            border: "none",
            fontWeight: 800,
            cursor: "pointer",
          }}
        >
          {loading ? "Searching..." : "Search & Score Deals"}
        </button>

        {error && (
          <div style={{ gridColumn: "1 / -1", color: "#ff8080" }}>{error}</div>
        )}
      </div>

      <div style={{ marginTop: 16, opacity: 0.8 }}>
        Showing <b>{results.length}</b> results (sorted by best deal score).
      </div>

      <div style={{ marginTop: 12, display: "grid", gap: 10 }}>
        {results.map((r) => {
          const l = r.listing;
          const title = `${l.year} ${cap(l.make)} ${cap(l.model)}${l.trim ? ` ${cap(l.trim)}` : ""}`;
          const loc = [l.city, l.state].filter(Boolean).join(", ");
          return (
            <a
              key={l.id}
              href={`/listing/${l.id}`}
              style={{
                textDecoration: "none",
                color: "inherit",
                padding: 14,
                borderRadius: 14,
                background: "#121826",
                border: "1px solid rgba(255,255,255,0.08)",
                display: "grid",
                gridTemplateColumns: "2fr 1fr 1fr 1fr 0.8fr",
                gap: 12,
                alignItems: "center",
              }}
            >
              <div>
                <div style={{ fontWeight: 900 }}>{title}</div>
                <div style={{ opacity: 0.75, fontSize: 12 }}>
                  {l.mileage.toLocaleString()} miles{loc ? ` • ${loc}` : ""}
                </div>
              </div>

              <div>
                <div style={{ opacity: 0.7, fontSize: 12 }}>Listed</div>
                <div style={{ fontWeight: 800 }}>{money(l.price)}</div>
              </div>

              <div>
                <div style={{ opacity: 0.7, fontSize: 12 }}>Fair price</div>
                <div style={{ fontWeight: 800 }}>
                  {money(r.predicted_price)}
                </div>
              </div>

              <div>
                <div style={{ opacity: 0.7, fontSize: 12 }}>Difference</div>
                <div style={{ fontWeight: 800 }}>
                  {r.diff < 0 ? "-" : "+"}
                  {money(Math.abs(r.diff))}
                  <span style={{ opacity: 0.7, fontSize: 12 }}>
                    {" "}
                    ({(r.diff_pct * 100).toFixed(1)}%)
                  </span>
                </div>
              </div>

              <div style={{ display: "grid", justifyItems: "end", gap: 8 }}>
                <div
                  style={{
                    padding: "6px 10px",
                    borderRadius: 999,
                    fontSize: 12,
                    fontWeight: 900,
                    textAlign: "center",
                    ...badgeStyle(r.badge),
                  }}
                >
                  {r.badge}
                </div>
                <div style={{ opacity: 0.8, fontSize: 12 }}>
                  Score <b>{r.deal_score}</b>/100
                </div>
              </div>
            </a>
          );
        })}
      </div>
    </div>
  );
}

const inputStyle: React.CSSProperties = {
  padding: "10px 12px",
  borderRadius: 10,
  border: "1px solid rgba(255,255,255,0.12)",
  background: "#0b0d12",
  color: "#e9eefc",
  outline: "none",
};

function cap(s: string) {
  const t = (s ?? "").toLowerCase();
  return t ? t[0].toUpperCase() + t.slice(1) : t;
}
