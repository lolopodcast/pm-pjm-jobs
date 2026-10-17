import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { registerSW } from "virtual:pwa-register";
import { makeT } from "./i18n.js";
import { DEFAULT_FILTERS, loadData } from "./data.js";
import { Icon, PAGES } from "./components.jsx";
import Overview from "./pages/Overview.jsx";
import Jobs from "./pages/Jobs.jsx";
import Insights from "./pages/Insights.jsx";
import Fit from "./pages/Fit.jsx";
import Archive from "./pages/Archive.jsx";
import About from "./pages/About.jsx";
import Gate from "./Gate.jsx";
import { InstallButton, IOSHelp, useInstall } from "./Install.jsx";

// Per-viewer conveniences only; every read/write tolerates blocked storage.
const store = {
  get(k, fb) { try { const v = localStorage.getItem("pmj_" + k); return v == null ? fb : JSON.parse(v); } catch { return fb; } },
  set(k, v) { try { localStorage.setItem("pmj_" + k, JSON.stringify(v)); } catch { /* storage unavailable */ } },
};
const ICON = { overview: "overview", jobs: "jobs", insights: "insights", fit: "fit", archive: "archive", about: "about" };
const pageFromHash = () => (PAGES.includes(location.hash.slice(1)) ? location.hash.slice(1) : "overview");

/** Clear everything this site keeps on the device and start over at the access-code screen. */
function resetSite() {
  try { Object.keys(localStorage).filter((k) => k.startsWith("pmj_")).forEach((k) => localStorage.removeItem(k)); } catch { /* storage unavailable */ }
  location.replace(location.pathname);
}

export default function App() {
  const [lang, setLang] = useState(() => store.get("lang", (navigator.language || "").toLowerCase().startsWith("zh") ? "zh" : "en"));
  const [theme, setTheme] = useState(() => store.get("theme", null));
  const [page, setPage] = useState(pageFromHash);
  const [unlocked, setUnlocked] = useState(() => store.get("gate", 0) === 1);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [menuOpen, setMenuOpen] = useState(false);
  const [toast, setToast] = useState("");
  const [online, setOnline] = useState(navigator.onLine);
  const [updateSW, setUpdateSW] = useState(null);
  const [fit, setFitState] = useState(() => store.get("fit", {}));
  const [me, setMeState] = useState(() => store.get("me", { edu: "", majors: [] }));
  const [filters, setFilters] = useState(DEFAULT_FILTERS);
  const menuRef = useRef(null);
  const { mode: installMode, install } = useInstall();
  const [iosHelp, setIosHelp] = useState(false);
  const t = useMemo(() => makeT(lang), [lang]);

  useEffect(() => { if (unlocked && !data) loadData().then(setData).catch((e) => setError(String(e))); }, [unlocked, data]);
  useEffect(() => {
    const sw = registerSW({ onNeedRefresh: () => setUpdateSW(() => () => sw(true)) });
  }, []);
  useEffect(() => {
    const on = () => setOnline(true), off = () => setOnline(false);
    addEventListener("online", on); addEventListener("offline", off);
    return () => { removeEventListener("online", on); removeEventListener("offline", off); };
  }, []);
  useEffect(() => { document.documentElement.lang = lang === "zh" ? "zh-Hant-TW" : "en"; document.title = t("title"); }, [lang, t]);
  useEffect(() => {
    if (theme) document.documentElement.setAttribute("data-theme", theme);
    else document.documentElement.removeAttribute("data-theme");
  }, [theme]);
  useEffect(() => {
    const h = () => setPage(pageFromHash());
    addEventListener("hashchange", h);
    return () => removeEventListener("hashchange", h);
  }, []);
  useEffect(() => {
    const close = (e) => { if (menuRef.current && !menuRef.current.contains(e.target)) setMenuOpen(false); };
    const esc = (e) => e.key === "Escape" && setMenuOpen(false);
    addEventListener("click", close); addEventListener("keydown", esc);
    return () => { removeEventListener("click", close); removeEventListener("keydown", esc); };
  }, []);

  // "Smart" copyright reminder (PRD 5.6): blocks only where nobody needs the browser menu.
  // Selected text, links and form fields keep the normal menu; printing and Save As stay allowed.
  // A courtesy, not protection: code and data are public on GitHub.
  useEffect(() => {
    const remind = () => flash(t("copyright"));
    const onMenu = (e) => {
      if (String(getSelection()).trim()) return;
      if (e.target.closest?.("a, input, textarea, select, [contenteditable]")) return;
      e.preventDefault();
      remind();
    };
    const onKey = (e) => {
      const k = e.key.toLowerCase();
      const ctrl = e.ctrlKey || e.metaKey;
      if (k === "f12" || (ctrl && k === "u") || (ctrl && (e.shiftKey || e.altKey) && ["i", "j", "c"].includes(k))) {
        e.preventDefault();
        remind();
      }
    };
    const onDrag = (e) => { if (e.target.closest?.("svg, img")) e.preventDefault(); };
    addEventListener("contextmenu", onMenu);
    addEventListener("keydown", onKey);
    addEventListener("dragstart", onDrag);
    return () => { removeEventListener("contextmenu", onMenu); removeEventListener("keydown", onKey); removeEventListener("dragstart", onDrag); };
  }, [t]); // eslint-disable-line react-hooks/exhaustive-deps

  const go = useCallback((p) => {
    setPage(p); setMenuOpen(false);
    history.replaceState(null, "", "#" + p);
    scrollTo({ top: 0, behavior: "smooth" });
  }, []);
  const flash = useCallback((msg) => { setToast(msg); clearTimeout(flash.timer); flash.timer = setTimeout(() => setToast(""), 4000); }, []);
  const setFit = (f) => { setFitState(f); store.set("fit", f); };
  const setMe = (m) => { setMeState(m); store.set("me", m); };
  const isDark = theme ? theme === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
  const toggleTheme = () => { const n = isDark ? "light" : "dark"; setTheme(n); store.set("theme", n); };
  const toggleLang = () => { const n = lang === "zh" ? "en" : "zh"; setLang(n); store.set("lang", n); };

  const updatedAt = data?.db?.updated_at;
  const stale = updatedAt && Date.now() - new Date(updatedAt).getTime() > 36 * 3600e3;
  const nav = (cls) => PAGES.map((p, i) => (
    <button key={p} className={page === p ? "on" : ""} aria-current={page === p ? "page" : undefined} onClick={() => go(p)}>
      <span className="num">{i}</span><Icon name={ICON[p]} size={18} /><span>{t("p_" + p)}</span>
    </button>
  ));
  const props = { t, data, go, flash, fit, setFit, me, setMe, filters, setFilters, resetSite };
  const Page = { overview: Overview, jobs: Jobs, insights: Insights, fit: Fit, archive: Archive, about: About }[page];
  const unlock = () => { store.set("gate", 1); setUnlocked(true); };
  const lock = () => { store.set("gate", 0); setUnlocked(false); scrollTo({ top: 0 }); };

  if (!unlocked) {
    return (
      <>
        <Gate t={t} onUnlock={unlock} toggleLang={toggleLang} toggleTheme={toggleTheme} isDark={isDark} />
        {toast && <div className="toast" role="status">{toast}</div>}
      </>
    );
  }

  return (
    <>
      <header className="hdr">
        <div className="hdr-in">
          <div className="flex items-center gap-1 min-w-0">
            <div className="relative" ref={menuRef}>
              <button className="ib" aria-label={t("menu")} aria-expanded={menuOpen} onClick={() => setMenuOpen(!menuOpen)}><Icon name="menu" size={22} /></button>
              {menuOpen && <div className="menu">{nav()}</div>}
            </div>
            <button className="ib" aria-label={t("home")} onClick={() => go("overview")}><Icon name="home" size={19} /></button>
            <button className="brand" onClick={() => scrollTo({ top: 0, behavior: "smooth" })}><b>PMJ</b><span>{t("title")}</span></button>
          </div>
          <div className="flex items-center gap-1">
            <InstallButton t={t} mode={installMode} install={install} onIOS={() => setIosHelp(true)} />
            <button className="pill-btn" onClick={toggleLang}>{lang === "zh" ? "EN" : "中"}</button>
            <button className="ib" onClick={toggleTheme} aria-label={isDark ? t("theme_l") : t("theme_d")} title={isDark ? t("theme_l") : t("theme_d")}>
              <Icon name={isDark ? "sun" : "moon"} size={19} />
            </button>
          </div>
        </div>
      </header>

      <div className="shell">
        <nav className="rail" aria-label="Pages">{nav()}</nav>
        <main className="min-w-0 flex flex-col gap-4">
          {!online && <div className="notice" role="status"><span>{t("offline")}</span></div>}
          {stale && <div className="notice" role="status"><span>{t("stale")}</span></div>}
          {updateSW && <div className="notice" role="status"><span>{t("update_ready")}</span><button className="btn" onClick={updateSW}>{t("reload")}</button></div>}
          {error ? <div className="card">{t("load_fail")}</div> : !data ? <div className="card mini">{t("loading")}</div> : <Page key={page} {...props} />}
        </main>
      </div>

      <footer className="ftr">
        <div className="ftr-in">
          <span>
            v{__APP_VERSION__}{updatedAt ? ` · ${t("data_date")} ${updatedAt.slice(0, 10)}` : ""} · For Educational Use Only · {t.lang === "zh" ? "非 104 人力銀行官方網站" : "Not an official 104 Job Bank site"}
          </span>
          <span className="flex gap-3.5 items-center">
            <span>Architect:&nbsp;<a href="https://www.ibs.ncnu.edu.tw/index.php/faculty/tenured-professor/299-smlo" target="_blank" rel="noopener noreferrer">Prof. Shihmin Lo</a></span>
            <button onClick={lock}>{t("gate_lock")}</button>
            <button onClick={() => scrollTo({ top: 0, behavior: "smooth" })}>Top ↑</button>
          </span>
        </div>
      </footer>
      {toast && <div className="toast" role="status">{toast}</div>}
      {iosHelp && <IOSHelp t={t} onClose={() => setIosHelp(false)} />}
    </>
  );
}
