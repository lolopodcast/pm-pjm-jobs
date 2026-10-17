// Export helpers (PRD 5.7). Everything is generated in the browser; nothing is uploaded.

/** Quote a CSV cell and neutralise spreadsheet formulas (CSV injection, PRD 5.7 第 8 點). */
export function csvCell(v) {
  let s = v == null ? "" : String(v);
  if (/^[=+\-@]/.test(s)) s = "'" + s;
  return /[",\r\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
}

/** UTF-8 BOM so Excel opens Chinese correctly; a blank line then the source note at the end. */
export function toCSV(rows, sourceLine) {
  return "﻿" + [...rows, [], [sourceLine]].map((r) => r.map(csvCell).join(",")).join("\r\n");
}

export const fileName = (what, ext, date) => `PMJ_${what}_${date.replace(/-/g, "")}.${ext}`;

export function download(name, mime, content) {
  const url = URL.createObjectURL(content instanceof Blob ? content : new Blob([content], { type: mime }));
  const a = document.createElement("a");
  a.href = url;
  a.download = name;
  document.body.append(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 2000);
}

/** Render an on-screen SVG chart to a 2x PNG with the current theme's colours and a source line. */
export function svgToPng(svg, name, sourceLine) {
  const css = getComputedStyle(document.documentElement);
  const resolve = (s) => s.replace(/var\((--[\w-]+)\)/g, (_, v) => css.getPropertyValue(v).trim() || "#888");
  const vb = svg.viewBox.baseVal;
  const w = vb.width, h = vb.height, foot = 28, scale = 2;
  const clone = svg.cloneNode(true);
  clone.setAttribute("width", w);
  clone.setAttribute("height", h);
  const xml = resolve(new XMLSerializer().serializeToString(clone));
  const img = new Image();
  img.onload = () => {
    const c = document.createElement("canvas");
    c.width = w * scale;
    c.height = (h + foot) * scale;
    const g = c.getContext("2d");
    g.scale(scale, scale);
    g.fillStyle = resolve("var(--card)");
    g.fillRect(0, 0, w, h + foot);
    g.drawImage(img, 0, 0, w, h);
    g.fillStyle = resolve("var(--muted)");
    g.font = "9px Inter, 'Microsoft JhengHei', sans-serif";
    g.fillText(sourceLine, 8, h + 18, w - 16);
    c.toBlob((b) => b && download(name, "image/png", b), "image/png");
  };
  img.src = "data:image/svg+xml;charset=utf-8," + encodeURIComponent(xml);
}

/** Browser print → "Save as PDF". With a target element, only that element is printed. */
export function printPdf(target) {
  if (target) {
    document.body.classList.add("print-one");
    target.classList.add("print-target");
  }
  const cleanup = () => {
    document.body.classList.remove("print-one");
    target?.classList.remove("print-target");
  };
  window.addEventListener("afterprint", cleanup, { once: true });
  window.print();
}
