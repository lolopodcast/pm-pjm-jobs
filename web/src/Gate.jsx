import { useState } from "react";
import { Icon } from "./components.jsx";

// Soft gate (kept in production): keeps casual visitors out, not a security control.
// The site is static, so anyone determined can bypass it or fetch the data files directly.
// Only a salted SHA-256 of the code is stored here.
const CODE_HASH = "d542f486735b23bc72f61e96cf54381bff64e9f3eef7487ac45994f881939776";

const hex = (bytes) => [...bytes].map((b) => b.toString(16).padStart(2, "0")).join("");

// Plain-JS SHA-256 for browsers without crypto.subtle (some older phones and in-app browsers).
export function sha256Fallback(text) {
  const K = [], H = [];
  for (let n = 2, found = 0; found < 64; n++) {
    let prime = true;
    for (let d = 2; d * d <= n; d++) if (n % d === 0) { prime = false; break; }
    if (!prime) continue;
    if (found < 8) H.push((Math.pow(n, 1 / 2) % 1) * 2 ** 32 | 0);
    K.push((Math.pow(n, 1 / 3) % 1) * 2 ** 32 | 0);
    found++;
  }
  const bytes = [...new TextEncoder().encode(text)], bitLen = bytes.length * 8;
  bytes.push(0x80);
  while (bytes.length % 64 !== 56) bytes.push(0);
  for (let i = 7; i >= 0; i--) bytes.push(i >= 4 ? 0 : (bitLen >>> (i * 8)) & 0xff);
  const rotr = (x, n) => (x >>> n) | (x << (32 - n));
  for (let off = 0; off < bytes.length; off += 64) {
    const w = new Array(64);
    for (let i = 0; i < 16; i++) w[i] = (bytes[off + i * 4] << 24) | (bytes[off + i * 4 + 1] << 16) | (bytes[off + i * 4 + 2] << 8) | bytes[off + i * 4 + 3];
    for (let i = 16; i < 64; i++) {
      const s0 = rotr(w[i - 15], 7) ^ rotr(w[i - 15], 18) ^ (w[i - 15] >>> 3);
      const s1 = rotr(w[i - 2], 17) ^ rotr(w[i - 2], 19) ^ (w[i - 2] >>> 10);
      w[i] = (w[i - 16] + s0 + w[i - 7] + s1) | 0;
    }
    let [a, b, c, d, e, f, g, h] = H;
    for (let i = 0; i < 64; i++) {
      const t1 = (h + (rotr(e, 6) ^ rotr(e, 11) ^ rotr(e, 25)) + ((e & f) ^ (~e & g)) + K[i] + w[i]) | 0;
      const t2 = ((rotr(a, 2) ^ rotr(a, 13) ^ rotr(a, 22)) + ((a & b) ^ (a & c) ^ (b & c))) | 0;
      [h, g, f, e, d, c, b, a] = [g, f, e, (d + t1) | 0, c, b, a, (t1 + t2) | 0];
    }
    [a, b, c, d, e, f, g, h].forEach((v, i) => { H[i] = (H[i] + v) | 0; });
  }
  return hex(H.flatMap((v) => [v >>> 24, (v >>> 16) & 0xff, (v >>> 8) & 0xff, v & 0xff]));
}

async function sha256(text) {
  if (!globalThis.crypto?.subtle) return sha256Fallback(text);
  return hex(new Uint8Array(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text))));
}

// Forgiving input: full-width characters from Chinese input methods become ASCII (NFKC), and spaces or
// invisible characters pasted from chat apps are dropped. Case does not matter.
export const normalizeCode = (code) => code.normalize("NFKC").replace(/[\s\u200B-\u200D\u2060\uFEFF]/g, "").toLowerCase();

export const hashCode = (code) => sha256("pmj-gate:" + normalizeCode(code));

export async function checkCode(input, hash = CODE_HASH) {
  return (await hashCode(input)) === hash;
}

export default function Gate({ t, onUnlock, toggleLang, toggleTheme, isDark }) {
  const [code, setCode] = useState("");
  const [wrong, setWrong] = useState(false);
  const [busy, setBusy] = useState(false);
  const submit = async (e) => {
    e.preventDefault();
    if (!code.trim()) return;
    setBusy(true);
    let ok = false;
    try { ok = await checkCode(code); } catch { /* treat as wrong rather than leave the button stuck */ }
    setBusy(false);
    if (ok) onUnlock();
    else setWrong(true);
  };
  return (
    <div className="gate">
      <div className="gate-bar">
        <button className="pill-btn" onClick={toggleLang}>{t.lang === "zh" ? "EN" : "中"}</button>
        <button className="ib" onClick={toggleTheme} aria-label={isDark ? t("theme_l") : t("theme_d")} title={isDark ? t("theme_l") : t("theme_d")}>
          <Icon name={isDark ? "sun" : "moon"} size={19} />
        </button>
      </div>
      <form className="gate-card" onSubmit={submit}>
        <div className="gate-logo" aria-hidden="true">PMJ</div>
        <h1 className="gate-title">{t("title")}</h1>
        <p className="lede">{t("gate_lede")}</p>
        <div className="field">
          <label htmlFor="gate-code">{t("gate_label")}</label>
          <input id="gate-code" type="text" autoComplete="off" autoCapitalize="none" autoCorrect="off" spellCheck="false" autoFocus
            value={code} onChange={(e) => { setCode(e.target.value); setWrong(false); }} aria-invalid={wrong} aria-describedby="gate-msg" />
        </div>
        <p id="gate-msg" className={"gate-msg" + (wrong ? " bad" : "")} role="status">{wrong ? t("gate_wrong") : t("gate_hint")}</p>
        <button className="btn solid gate-btn" type="submit" disabled={busy || !code.trim()}>{t("gate_enter")}</button>
        <p className="mini text-center">For Educational Use Only · {t.lang === "zh" ? "非 104 人力銀行官方網站" : "Not an official 104 Job Bank site"}</p>
      </form>
    </div>
  );
}
