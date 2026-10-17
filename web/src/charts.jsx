// SVG charts (PRD 5.3, 5.7 第 4 點: drawn as SVG so they can be exported as PNG).
import { useRef } from "react";
import { DOM } from "./i18n.js";
import { download, fileName, svgToPng, toCSV } from "./exporting.js";

const FONT = "Inter, 'Microsoft JhengHei', 'PingFang TC', sans-serif";
export const PALETTE = ["var(--c1)", "var(--c2)", "var(--c3)", "var(--c4)", "var(--c5)"];

const clip = (s, max) => (s.length > max ? s.slice(0, max - 1) + "…" : s);
const textWidth = (s) => [...s].reduce((w, ch) => w + (ch.charCodeAt(0) > 255 ? 1 : 0.55), 0);

export function Radar({ series, t, size = 280 }) {
  const c = size / 2, r = size / 2 - 42, keys = Object.keys(DOM);
  const max = Math.max(40, Math.ceil(Math.max(0, ...series.flatMap((s) => s.v)) / 10) * 10);
  const pt = (i, val) => {
    const a = -Math.PI / 2 + (i * 2 * Math.PI) / keys.length;
    return [c + Math.cos(a) * r * (val / max), c + Math.sin(a) * r * (val / max)];
  };
  return (
    <svg className="svgchart" viewBox={`0 0 ${size} ${size}`} role="img" aria-label={t("d_dom")} style={{ maxWidth: size, margin: "0 auto" }}>
      <rect width={size} height={size} fill="var(--card)" />
      {[0.25, 0.5, 0.75, 1].map((f) => (
        <polygon key={f} points={keys.map((_, i) => pt(i, max * f).join(",")).join(" ")} fill="none" stroke="var(--line)" />
      ))}
      {keys.map((k, i) => {
        const [x, y] = pt(i, max);
        const [lx, ly] = pt(i, max * 1.2);
        return (
          <g key={k}>
            <line x1={c} y1={c} x2={x} y2={y} stroke="var(--line)" />
            <text x={lx} y={ly} fontSize="11" fontFamily={FONT} fill="var(--muted)" dominantBaseline="middle"
              textAnchor={Math.abs(lx - c) < 6 ? "middle" : lx > c ? "start" : "end"}>{t.pick(DOM[k])}</text>
          </g>
        );
      })}
      <text x={c + 3} y={c - r - 2} fontSize="9" fill="var(--muted)" fontFamily={FONT}>{max}</text>
      {series.map((s) => (
        <g key={s.label}>
          <polygon points={s.v.map((v, i) => pt(i, v).join(",")).join(" ")} fill={s.color} fillOpacity="0.16" stroke={s.color} strokeWidth="2" strokeLinejoin="round" />
          {s.v.map((v, i) => { const [x, y] = pt(i, v); return <circle key={i} cx={x} cy={y} r="2.6" fill={s.color} />; })}
        </g>
      ))}
    </svg>
  );
}

/** Horizontal bars. rows: [{key, label, n, suffix?}] */
export function Bars({ rows, color, onPick, valueChars = 4 }) {
  if (!rows.length) return null;
  // A narrow design width keeps text readable when the SVG shrinks to phone width.
  const W = 400, rowH = 24, labelW = 140, valW = Math.max(34, valueChars * 8), barW = W - labelW - valW - 10;
  const max = Math.max(1, ...rows.map((r) => r.n));
  return (
    <svg className="svgchart" viewBox={`0 0 ${W} ${rows.length * rowH + 4}`} role="img">
      <rect width={W} height={rows.length * rowH + 4} fill="var(--card)" />
      {rows.map((r, i) => {
        const y = i * rowH + 4;
        const label = textWidth(r.label) > 10 ? clip(r.label, 10) : r.label;
        return (
          <g key={r.key || r.label} className={onPick ? "click" : undefined} onClick={onPick ? () => onPick(r) : undefined}
            role={onPick ? "button" : undefined} tabIndex={onPick ? 0 : undefined}
            onKeyDown={onPick ? (e) => (e.key === "Enter" || e.key === " ") && onPick(r) : undefined}>
            <title>{r.label}</title>
            <text x="0" y={y + 13} fontSize="13" fontFamily={FONT} fill="var(--fg)" dominantBaseline="middle">{label}</text>
            <rect x={labelW} y={y + 6} width={barW} height="12" rx="6" fill="var(--soft)" />
            <rect x={labelW} y={y + 6} width={Math.max(2, (r.n / max) * barW)} height="12" rx="6" fill={color} />
            <text x={W} y={y + 13} fontSize="12" fontFamily={FONT} fill="var(--muted)" textAnchor="end" dominantBaseline="middle">{r.suffix ?? r.n}</text>
          </g>
        );
      })}
    </svg>
  );
}

/** rows: [{label, values: {col: percent}}] */
export function Heat({ rows, cols, colLabel }) {
  const W = 400, rowH = 40, headH = 22, labelW = 40, cw = (W - labelW) / cols.length;
  const H = headH + rows.length * rowH;
  return (
    <svg className="svgchart" viewBox={`0 0 ${W} ${H}`} role="img">
      <rect width={W} height={H} fill="var(--card)" />
      {cols.map((c, i) => (
        <text key={c} x={labelW + i * cw + cw / 2} y="12" fontSize="12" fontWeight="600" fontFamily={FONT} fill="var(--muted)" textAnchor="middle">
          <title>{colLabel(c)}</title>{c}
        </text>
      ))}
      {rows.map((r, ri) => (
        <g key={r.label}>
          <text x="0" y={headH + ri * rowH + rowH / 2} fontSize="12" fontWeight="700" fontFamily={FONT} fill="var(--muted)" dominantBaseline="middle">{r.label}</text>
          {cols.map((c, i) => {
            const p = r.values[c] || 0;
            const x = labelW + i * cw + 2, y = headH + ri * rowH + 2;
            return (
              <g key={c}>
                <title>{`${r.label} · ${colLabel(c)} · ${p}%`}</title>
                <rect x={x} y={y} width={cw - 4} height={rowH - 4} rx="6" fill="var(--soft)" />
                <rect x={x} y={y} width={cw - 4} height={rowH - 4} rx="6" fill="var(--c1)" opacity={(p / 100) * 0.85} />
                <text x={x + (cw - 4) / 2} y={y + (rowH - 4) / 2} fontSize="12" fontWeight="600" fontFamily={FONT} textAnchor="middle" dominantBaseline="middle"
                  fill={p >= 55 ? "var(--on-primary)" : "var(--fg)"}>{p}%</text>
              </g>
            );
          })}
        </g>
      ))}
    </svg>
  );
}

/** One 100% stacked bar. parts: [{label, n, color}] */
export function Stack({ parts, total }) {
  const W = 400, H = 14;
  let x = 0;
  return (
    <>
      <svg className="svgchart" viewBox={`0 0 ${W} ${H}`} role="img">
        <rect width={W} height={H} rx="6" fill="var(--soft)" />
        {parts.map((p) => {
          const w = total ? (p.n / total) * W : 0;
          const el = w > 0 ? <rect key={p.label} x={x} y="0" width={w} height={H} fill={p.color}><title>{`${p.label} ${p.n}`}</title></rect> : null;
          x += w;
          return el;
        })}
      </svg>
      <Legend items={parts.map((p) => [`${p.label} ${total ? Math.round((p.n / total) * 100) : 0}%`, p.color])} />
    </>
  );
}

export function Legend({ items }) {
  return (
    <div className="legend">
      {items.map(([label, color]) => <span key={label}><i style={{ background: color }} />{label}</span>)}
    </div>
  );
}

/** Card with PNG / CSV export buttons (PRD 5.7). */
export function ChartCard({ t, title, name, csv, extra, children, wide, today }) {
  const ref = useRef(null);
  const src = t("src_line", { d: today });
  const png = () => {
    const svg = ref.current?.querySelector("svg.svgchart");
    if (svg) svgToPng(svg, fileName(name, "png", today), src);
  };
  return (
    <div className="card" style={wide ? { gridColumn: "1 / -1" } : undefined}>
      <div className="sec-h">
        <h2 className="h2">{title}</h2>
        <div className="flex gap-1.5 flex-wrap items-center noprint">
          {extra}
          <button className="tool" onClick={png}>PNG</button>
          {csv && <button className="tool" onClick={() => download(fileName(name, "csv", today), "text/csv;charset=utf-8", toCSV(csv(), src))}>CSV</button>}
        </div>
      </div>
      <div ref={ref}>{children}</div>
    </div>
  );
}
