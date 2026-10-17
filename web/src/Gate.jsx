import { useState } from "react";
import { Icon } from "./components.jsx";

// Soft gate for the test-sharing period: keeps casual visitors out, not a security control.
// The site is static, so anyone determined can bypass it or fetch the data files directly.
// Only a salted SHA-256 of the code is stored here.
const CODE_HASH = "d542f486735b23bc72f61e96cf54381bff64e9f3eef7487ac45994f881939776";

async function sha256(text) {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text));
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

export async function checkCode(input) {
  return (await sha256("pmj-gate:" + input.trim().toLowerCase())) === CODE_HASH;
}

export default function Gate({ t, onUnlock, toggleLang, toggleTheme, isDark }) {
  const [code, setCode] = useState("");
  const [wrong, setWrong] = useState(false);
  const [busy, setBusy] = useState(false);
  const submit = async (e) => {
    e.preventDefault();
    if (!code.trim()) return;
    setBusy(true);
    const ok = await checkCode(code);
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
          <input id="gate-code" type="password" autoComplete="off" autoCapitalize="none" spellCheck="false" autoFocus
            value={code} onChange={(e) => { setCode(e.target.value); setWrong(false); }} aria-invalid={wrong} aria-describedby="gate-msg" />
        </div>
        <p id="gate-msg" className={"gate-msg" + (wrong ? " bad" : "")} role="status">{wrong ? t("gate_wrong") : t("gate_hint")}</p>
        <button className="btn solid gate-btn" type="submit" disabled={busy || !code.trim()}>{t("gate_enter")}</button>
        <p className="mini text-center">For Educational Use Only · {t.lang === "zh" ? "非 104 人力銀行官方網站" : "Not an official 104 Job Bank site"}</p>
      </form>
    </div>
  );
}
