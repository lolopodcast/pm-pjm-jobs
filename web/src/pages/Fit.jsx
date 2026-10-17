import { useMemo, useRef, useState } from "react";
import { Bars, Legend, Radar } from "../charts.jsx";
import { PageHead } from "../components.jsx";
import { analysed, companyName, openJobs, titles, todayTPE, vname } from "../data.js";
import { download, fileName, printPdf } from "../exporting.js";
import { fitLevel, fitScore, gaps, hasProfile, requirements } from "../fit.js";
import { DOM, OPT } from "../i18n.js";

const GROUPS = [["S", "fit_s"], ["K", "fit_k"], ["T", "fit_t"], ["A", "fit_a"]];
const LEVELS = [[0, "lv0"], [0.5, "lv1"], [1, "lv2"]];

export default function Fit({ t, data, fit, setFit, me, setMe, go, setFilters, flash }) {
  const [q, setQ] = useState("");
  const [armed, setArmed] = useState(false);
  const fileRef = useRef(null);
  const done = useMemo(() => analysed(openJobs(data.db.jobs)), [data]);
  const freq = useMemo(() => {
    const m = {};
    for (const j of done) { const r = requirements(j); for (const id of [...r.K, ...r.S, ...r.A, ...r.T]) m[id] = (m[id] || 0) + 1; }
    return m;
  }, [done]);
  const setLevel = (id, v) => { const n = { ...fit }; if (v) n[id] = v; else delete n[id]; setFit(n); setArmed(false); };
  const ranked = done.map((j) => ({ j, v: fitScore(j, fit, me) })).filter((x) => x.v != null).sort((a, b) => b.v - a.v);
  const gapRows = gaps(done, fit).map(([id, n]) => ({ key: id, label: vname(data.vocab, id, t), n }));
  const avgDm = Object.keys(DOM).map((d) => (done.length ? Math.round(done.reduce((a, j) => a + (j.pm_domains?.[d] || 0), 0) / done.length) : 0));
  const mine = (() => {
    const sums = Object.fromEntries(Object.keys(DOM).map((d) => [d, 0]));
    for (const [id, w] of Object.entries(fit)) { const d = data.vocab[id]?.domain; if (d) sums[d] += w; }
    const tot = Object.values(sums).reduce((a, b) => a + b, 0) || 1;
    return Object.keys(DOM).map((d) => Math.round((sums[d] / tot) * 100));
  })();
  const profile = hasProfile(fit, me);
  const today = todayTPE();
  const ql = q.trim().toLowerCase();

  const exportJson = () => download(fileName("my_fit", "json", today), "application/json", JSON.stringify({ app: "pmj", version: 1, exported: today, me, items: fit }, null, 2));
  const importJson = async (e) => {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (!file) return;
    try {
      const d = JSON.parse(await file.text());
      if (d.app !== "pmj" || typeof d.items !== "object") throw new Error("bad");
      const items = Object.fromEntries(Object.entries(d.items).filter(([id, v]) => data.vocab[id] && [0.5, 1].includes(v)));
      const majors = (d.me?.majors || []).filter((m) => data.majors[m]);
      setFit(items);
      setMe({ edu: OPT.myedu[d.me?.edu] ? d.me.edu : "", majors });
      flash(t("imp_ok"));
    } catch { flash(t("imp_bad")); }
  };
  const clear = () => {
    if (!armed) { setArmed(true); return; }
    setFit({}); setMe({ edu: "", majors: [] }); setArmed(false); flash(t("cleared"));
  };

  return (
    <section className="page">
      <PageHead page="fit" t={t} lede={t("fit_lede")} />
      <div className="fit-layout">
        <div className="card">
          <div className="sec-h">
            <h2 className="h2">{t("fit_my")}</h2>
            <div className="flex flex-wrap gap-2 noprint">
              <button className="btn" onClick={exportJson}>{t("exp")}</button>
              <button className="btn" onClick={() => fileRef.current.click()}>{t("imp")}</button>
              <input ref={fileRef} type="file" accept="application/json,.json" hidden onChange={importJson} />
              <button className={"btn danger" + (armed ? " armed" : "")} onClick={clear}>{armed ? t("clr2") : t("clr")}</button>
            </div>
          </div>
          <div className="field mb-2"><label htmlFor="fit-q">{t("fit_search")}</label>
            <input id="fit-q" type="search" value={q} onChange={(e) => setQ(e.target.value)} /></div>
          {GROUPS.map(([cat, key]) => {
            const items = data.byCat[cat].filter((it) => !ql || it.zh.toLowerCase().includes(ql) || it.en.toLowerCase().includes(ql))
              .sort((a, b) => (freq[b.id] || 0) - (freq[a.id] || 0));
            const ticked = data.byCat[cat].filter((it) => fit[it.id]).length;
            return (
              <details key={cat} className="fit-group flex flex-col gap-1" open={cat === "S" || !!ql}>
                <summary><span className="eyebrow">{t(key)}{ticked ? ` · ${ticked}` : ""}</span></summary>
                {cat === "K" && !ql && (
                  <div className="flex flex-col gap-2.5 py-2 border-b border-dashed" style={{ borderColor: "var(--line)" }}>
                    <div className="field" style={{ maxWidth: "16em" }}><label htmlFor="my-edu">{t("my_edu")}</label>
                      <select id="my-edu" value={me.edu} onChange={(e) => setMe({ ...me, edu: e.target.value })}>
                        <option value="">{t("choose")}</option>
                        {Object.keys(OPT.myedu).map((k) => <option key={k} value={k}>{t.pick(OPT.myedu[k])}</option>)}
                      </select></div>
                    <div className="field"><span className="lbl">{t("my_maj")}</span>
                      <div className="maj-grid">
                        {Object.values(data.majors).filter((m) => m.id !== "MAJ_SCI_ENG").map((m) => (
                          <label key={m.id} className="flex gap-1.5 items-center">
                            <input type="checkbox" checked={me.majors.includes(m.id)}
                              onChange={(e) => setMe({ ...me, majors: e.target.checked ? [...me.majors, m.id] : me.majors.filter((x) => x !== m.id) })} />
                            {t.pick([m.zh, m.en])}
                          </label>
                        ))}
                      </div></div>
                  </div>
                )}
                {items.map((it) => (
                  <div key={it.id} className="skill-row">
                    <div className="min-w-0"><div>{t.pick([it.zh, it.en])}</div><div className="mini">{t("appear", { n: freq[it.id] || 0 })}</div></div>
                    <div className="lv" role="group" aria-label={t.pick([it.zh, it.en])}>
                      {LEVELS.map(([v, k]) => (
                        <button key={k} className={(fit[it.id] || 0) === v ? "on" : ""} aria-pressed={(fit[it.id] || 0) === v} onClick={() => setLevel(it.id, v)}>{t(k)}</button>
                      ))}
                    </div>
                  </div>
                ))}
              </details>
            );
          })}
        </div>
        <div className="flex flex-col gap-4 min-w-0">
          {!profile ? <div className="card mini">{t("fit_empty")}</div> : (
            <>
              <div className="card">
                <div className="sec-h">
                  <h2 className="h2">{t("fit_res")}</h2>
                  <button className="btn solid noprint" onClick={() => printPdf()}>{t("x_report_pdf")}</button>
                </div>
                <p className="mini mb-2">≥70% {t("hi")} · 40–69% {t("mid")} · &lt;40% {t("lo")}</p>
                {ranked.slice(0, 8).map(({ j, v }) => (
                  <div className="match" key={j.job_id}>
                    <div className="min-w-0"><div className="font-semibold">{titles(j, t).shown}</div><div className="mini">{companyName(j, t)} · {j.role_type}</div></div>
                    <span className={"fit " + fitLevel(v)}>{v}%</span>
                  </div>
                ))}
                <p className="chart-note">{t("fit_disc")}</p>
              </div>
              <div className="card">
                <h2 className="h2 mb-3">{t("fit_gap")}</h2>
                <Bars rows={gapRows} color="var(--c5)" onPick={(r) => { setFilters((f) => ({ ...f, tag: r.key, status: "open" })); go("jobs"); }} />
              </div>
              <div className="card">
                <h2 className="h2 mb-3">{t("fit_radar")}</h2>
                <Radar t={t} size={300} series={[{ label: "avg", v: avgDm, color: "var(--c3)" }, { label: "me", v: mine, color: "var(--c1)" }]} />
                <Legend items={[[t("me"), "var(--c1)"], [t("avg"), "var(--c3)"]]} />
              </div>
            </>
          )}
        </div>
      </div>
    </section>
  );
}
