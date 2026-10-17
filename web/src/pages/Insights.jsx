import { useState } from "react";
import { Bars, ChartCard, Heat, Legend, PALETTE, Radar, Stack } from "../charts.jsx";
import { PageHead, Seg } from "../components.jsx";
import { analysed, countBy, daysBetween, openJobs, todayTPE, vname } from "../data.js";
import { printPdf } from "../exporting.js";
import { COL, DOM, DOM_FULL, OPT, STG } from "../i18n.js";

export default function Insights({ t, data, go, setFilters }) {
  const [role, setRole] = useState("all");
  const [range, setRange] = useState("all");
  const [ksaTab, setKsaTab] = useState("skills");
  const today = todayTPE();
  const base = analysed(openJobs(data.db.jobs))
    .filter((j) => role === "all" || j.role_type === role)
    .filter((j) => range === "all" || daysBetween(j.first_seen_date, today) <= Number(range));
  const N = base.length || 1;
  const toJobs = (r) => { setFilters((f) => ({ ...f, tag: r.key, status: "open" })); go("jobs"); };
  const named = (pairs) => pairs.map(([id, n]) => ({ key: id, label: vname(data.vocab, id, t), n }));

  const ksaRows = named(countBy(base, (j) => j.ksa_normalized?.[ksaTab]).slice(0, 20));
  const taskRows = named(countBy(base, (j) => j.tasks_normalized).slice(0, 20));
  const avg = (list) => Object.keys(DOM).map((d) => (list.length ? Math.round(list.reduce((a, j) => a + (j.pm_domains?.[d] || 0), 0) / list.length) : 0));
  const pmL = base.filter((j) => j.role_type === "PM"), pjL = base.filter((j) => j.role_type === "PjM");
  const radar = [pmL.length && { label: "PM", v: avg(pmL), color: "var(--c1)" }, pjL.length && { label: "PjM", v: avg(pjL), color: "var(--c3)" }].filter(Boolean);
  const heatRows = [["PM", pmL], ["PjM", pjL]].filter(([, l]) => l.length).map(([label, l]) => ({
    label, values: Object.fromEntries(Object.keys(STG).map((k) => [k, Math.round((l.filter((j) => j.stage_gate?.includes(k)).length / l.length) * 100)])),
  }));
  const collabRows = countBy(base, (j) => j.context?.collaborators).slice(0, 10).map(([c, n]) => ({ key: c, label: t.pick(COL[c]) || c, n }));
  const dist = (opt, get) => {
    const parts = Object.keys(OPT[opt]).map((k, i) => ({ key: k, label: t.pick(OPT[opt][k]), n: base.filter((j) => get(j) === k).length, color: PALETTE[i % 5] }));
    const unstated = base.length - parts.reduce((a, p) => a + p.n, 0);   // the AI returns null when the JD does not say
    return unstated ? [...parts, { key: "null", label: t("not_stated"), n: unstated, color: "var(--line)" }] : parts;
  };
  const ctxBlocks = [["c_prod", dist("product", (j) => j.context?.product_type)], ["c_mkt", dist("market", (j) => j.context?.market)],
    ["c_travel", dist("travel", (j) => j.context?.travel)], ["c_eng", dist("english", (j) => j.context?.english_level)], ["c_lang", dist("jdlang", (j) => j.jd_lang)]];
  const eduParts = ["none", "hs", "as", "ba", "ma", "phd"].map((k, i) => ({ key: k, label: t.pick(OPT.edu[k]), n: base.filter((j) => (j.education_req?.level || "none") === k).length, color: PALETTE[i % 5] }))
    .filter((p) => p.n);
  const majRows = countBy(base, (j) => j.education_req?.majors).slice(0, 10).map(([m, n]) => {
    const r = base.filter((j) => j.education_req?.major_required && j.education_req.majors.includes(m)).length;
    return { key: m, label: t.pick([data.majors[m]?.zh, data.majors[m]?.en]), n, suffix: n + (r ? t("maj_sfx", { r }) : "") };
  });
  const anyMaj = Math.round((base.filter((j) => !j.education_req?.majors?.length).length / N) * 100);
  const anyFlag = base.filter((j) => j.compliance_flags?.length).length;
  const compRows = [{ key: "any", label: t("comp_any"), n: anyFlag, suffix: Math.round((anyFlag / N) * 100) + "%" },
    ...Object.keys(OPT.flag).map((f) => { const n = base.filter((j) => j.compliance_flags?.includes(f)).length; return { key: f, label: t.pick(OPT.flag[f]), n, suffix: Math.round((n / N) * 100) + "%" }; })];
  const card = { t, today };

  return (
    <section className="page">
      <PageHead page="insights" t={t} lede={t("in_lede")} />
      <div className="card flex gap-4 flex-wrap items-center">
        <span className="mini">{t("f_role")}</span>
        <Seg value={role} onChange={setRole} options={[["all", t("all")], ["PM", "PM"], ["PjM", "PjM"]]} />
        <span className="mini">{t("in_range")}</span>
        <Seg value={range} onChange={setRange} options={[["30", t("r30")], ["90", t("r90")], ["all", t("rall")]]} />
        <span className="mini">{base.length} {t("jobs_unit")}</span>
        <button className="btn ml-auto" onClick={() => printPdf()}>{t("x_page_pdf")}</button>
      </div>
      {!base.length ? <div className="card mini">{t("no_ai_yet")}</div> : (
        <>
          <div className="grid2">
            <ChartCard {...card} title={t("ch_ksa")} name={`KSA_Top20_${ksaTab}`} csv={() => [["ID", "Tag", "n"], ...ksaRows.map((r) => [r.key, r.label, r.n])]}>
              <div className="mb-3"><Seg value={ksaTab} onChange={setKsaTab} options={[["knowledge", t("tab_k")], ["skills", t("tab_s")], ["attributes", t("tab_a")]]} /></div>
              <Bars rows={ksaRows} color={{ knowledge: "var(--c1)", skills: "var(--c2)", attributes: "var(--c3)" }[ksaTab]} onPick={toJobs} />
            </ChartCard>
            <ChartCard {...card} title={t("ch_task")} name="Tasks_Top20" csv={() => [["ID", "Task", "n"], ...taskRows.map((r) => [r.key, r.label, r.n])]}>
              <Bars rows={taskRows} color="var(--c3)" onPick={toJobs} />
            </ChartCard>
            <ChartCard {...card} title={t("ch_radar")} name="PM_domains"
              csv={() => [["Domain", ...radar.map((s) => s.label)], ...Object.keys(DOM).map((d, i) => [`${d} ${t.pick(DOM_FULL[d])}`, ...radar.map((s) => s.v[i])])]}>
              <Radar t={t} series={radar} size={300} />
              <Legend items={radar.map((s) => [s.label, s.color])} />
            </ChartCard>
            <ChartCard {...card} title={t("ch_heat")} name="StageGate"
              csv={() => [["Role", ...Object.keys(STG)], ...heatRows.map((r) => [r.label, ...Object.keys(STG).map((k) => r.values[k] + "%")])]}>
              <Heat rows={heatRows} cols={Object.keys(STG)} colLabel={(c) => t.pick(STG[c])} />
              <p className="chart-note">{t("heat_note")} {Object.keys(STG).map((k) => `${k} ${t.pick(STG[k])}`).join(" · ")}</p>
            </ChartCard>
            <ChartCard {...card} title={t("ch_collab")} name="Collaborators" csv={() => [["Unit", "n"], ...collabRows.map((r) => [r.label, r.n])]}>
              <Bars rows={collabRows} color="var(--c4)" />
            </ChartCard>
            <ChartCard {...card} title={t("ch_ctx")} name="Context"
              csv={() => ctxBlocks.flatMap(([k, parts]) => [[t(k)], ...parts.map((p) => [p.label, p.n]), []])}>
              <div className="flex flex-col gap-3.5">
                {ctxBlocks.map(([k, parts]) => <div key={k}><h5 className="text-[13px] font-semibold mb-1">{t(k)}</h5><Stack parts={parts} total={N} /></div>)}
              </div>
            </ChartCard>
            <ChartCard {...card} wide title={t("ch_edu")} name="Degree_Major" extra={<span className="mini">{t("maj_any_share", { p: anyMaj })}</span>}
              csv={() => [[t("edu_dist"), "n"], ...eduParts.map((p) => [p.label, p.n]), [], [t("maj_top"), "n", t("req")], ...majRows.map((r) => [r.label, r.n, r.suffix])]}>
              <div className="grid2">
                <div><h5 className="text-[13px] font-semibold mb-1">{t("edu_dist")}</h5><Stack parts={eduParts} total={N} /></div>
                <div><h5 className="text-[13px] font-semibold mb-1">{t("maj_top")}</h5><Bars rows={majRows} color="var(--c1)" valueChars={9} /></div>
              </div>
            </ChartCard>
          </div>
          <ChartCard {...card} title={t("ch_comp")} name="Compliance" csv={() => [["Condition", "n", "%"], ...compRows.map((r) => [r.label, r.n, r.suffix])]}>
            <p className="lede mb-3 text-[13.5px]">{t("comp_lede")}</p>
            <Bars rows={compRows} color="var(--bad)" />
          </ChartCard>
        </>
      )}
    </section>
  );
}
