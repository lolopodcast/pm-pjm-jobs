import { useMemo, useRef, useState } from "react";
import { Radar } from "../charts.jsx";
import { ListingBadge, PageHead, StatusChip, TagChips } from "../components.jsx";
import { companyName, tagText, titles, todayTPE, vname } from "../data.js";
import { download, fileName, printPdf, toCSV } from "../exporting.js";
import { eduItems, fitLevel, fitScore, hasProfile, requirements } from "../fit.js";
import { COL, DOM, OPT, STG } from "../i18n.js";
import { INDUSTRY_EN } from "../industries.js";
import { DEFAULT_FILTERS } from "../data.js";

const PAGE_SIZE = 30;
const REPO = "https://github.com/lolopodcast/pm-pjm-jobs";

function majorsText(job, data, t) {
  const e = job.education_req || {};
  if (!e.majors?.length) return t("maj_any");
  const names = e.majors.map((m) => t.pick([data.majors[m]?.zh, data.majors[m]?.en])).join(t.sep);
  return `${names}${t.lang === "zh" ? "（" : " ("}${t(e.major_required ? "req" : "pref")}${t.lang === "zh" ? "）" : ")"}`;
}

// Defined at module level so the <select> is not re-created on every render (stable on mobile browsers).
function Sel({ id, label, value, opts, onChange }) {
  return (
    <div className="field"><label htmlFor={id}>{label}</label>
      <select id={id} value={value} onChange={(e) => onChange(e.target.value)}>{opts.map(([v, l]) => <option key={v} value={v}>{l}</option>)}</select>
    </div>
  );
}

export function filterJobs(jobs, f, ctx) {
  const q = f.q.trim().toLowerCase();
  const list = jobs.filter((j) => {
    if (f.status !== "all" && j.status !== f.status) return false;
    if (f.role !== "all" && j.role_type !== f.role) return false;
    if (f.lst !== "all" && j.listing_type !== f.lst) return false;
    if (f.ind !== "all" && j.industry !== f.ind) return false;
    if (f.tag) {
      const r = requirements(j);
      if (![...r.K, ...r.S, ...r.A, ...r.T].includes(f.tag)) return false;
    }
    if (q) {
      const r = requirements(j);
      const vocabNames = [...r.K, ...r.S, ...r.A, ...r.T].flatMap((id) => [ctx.vocab[id]?.zh, ctx.vocab[id]?.en]);
      const hay = [j.title, j.title_zh, j.title_en, j.company, j.company_en, j.parent_company, j.industry, INDUSTRY_EN[j.industry], ...tagText(j), ...vocabNames]
        .filter(Boolean).join(" ").toLowerCase();
      if (!hay.includes(q)) return false;
    }
    return true;
  });
  if (f.sort === "new") list.sort((a, b) => b.first_seen_date.localeCompare(a.first_seen_date) || a.job_id.localeCompare(b.job_id));
  if (f.sort === "co") list.sort((a, b) => a.company.localeCompare(b.company, "zh-Hant-TW"));
  if (f.sort === "fit") list.sort((a, b) => (fitScore(b, ctx.fit, ctx.me) ?? -1) - (fitScore(a, ctx.fit, ctx.me) ?? -1));
  return list;
}

function jobsCSV(list, ctx, t, today) {
  const names = (ids) => (ids || []).map((id) => vname(ctx.vocab, id, t)).join("; ");
  const zh = t.lang === "zh";
  const head = ["job_id", zh ? "公司" : "Company", "Company (EN)", t("f_listing"), t("parent"), t("orig_title"), zh ? "職稱（中）" : "Title (ZH)",
    zh ? "職稱（英）" : "Title (EN)", t("f_role"), t("f_ind"), zh ? "地區" : "Location", t("edu_lbl"), t("maj_lbl"), zh ? "薪資" : "Salary",
    t("first_seen"), t("f_status"), t("closed_on"), "K", "S", "A", t("d_t"), ...Object.keys(DOM).map((d) => `${d} ${t.pick(DOM[d])}`), "Stage-Gate", t("d_sum"), "104 URL"];
  const withFit = hasProfile(ctx.fit, ctx.me);
  if (withFit) head.push(t("s_fit"));
  // compliance_flags are deliberately not exported per job (PRD 5.7 第 7 點, 8.4).
  const rows = list.map((j) => {
    const n = j.ksa_normalized || {};
    const r = [j.job_id, j.company, j.company_en || "", t.pick(OPT.listing[j.listing_type]), j.parent_company || "", j.title, j.title_zh || "", j.title_en || "",
      j.role_type || "", t.industry(j.industry), t.location(j.location), t.pick(OPT.edu[j.education_req?.level || "none"]), majorsText(j, ctx, t), t.salary(j.salary_desc),
      j.first_seen_date, t(j.status), j.closed_date || "", names(n.knowledge), names(n.skills), names(n.attributes), names(j.tasks_normalized),
      ...Object.keys(DOM).map((d) => j.pm_domains?.[d] ?? ""), (j.stage_gate || []).join("; "), j.jd_summary ? t.pick([j.jd_summary.zh, j.jd_summary.en]) : "", j.url];
    if (withFit) { const f = fitScore(j, ctx.fit, ctx.me); r.push(f == null ? "" : f + "%"); }
    return r;
  });
  return toCSV([head, ...rows], t("src_line", { d: today }));
}

function JobDetail({ job, t, ctx }) {
  const n = job.ksa_normalized || {};
  const showFit = hasProfile(ctx.fit, ctx.me);
  const fs = showFit ? fitScore(job, ctx.fit, ctx.me) : null;
  const req = requirements(job);
  const reqIds = [...req.K, ...req.S, ...req.A, ...req.T];
  const edu = eduItems(job, ctx.me);
  const eduHave = edu.filter((i) => i.score === 1).map((i) => t(i.kind === "edu" ? "edu_have" : "maj_have"));
  const eduLack = edu.filter((i) => i.score < 1).map((i) => t(i.kind === "edu" ? "edu_lack" : "maj_lack"));
  const c = job.context || {};
  const Row = ({ k, v }) => <><dt>{t(k)}</dt><dd>{v || "—"}</dd></>;
  const cardRef = useRef(null);
  return (
    <div className="job-detail" ref={cardRef}>
      <div className="dl">
        <div>
          <h4>{t("d_sum")} <span className="ai">{t("ai")}</span></h4>
          <p className="summary">{t.pick([job.jd_summary?.zh, job.jd_summary?.en])}</p>
          <div className="mini mt-1">{t("ai_note")}</div>
        </div>
        <div>
          <h4>{t("d_k")}</h4>
          <div className="chips mb-1.5">
            <span className="chip k">{t("edu_lbl")}{t.colon}{t.pick(OPT.edu[job.education_req?.level || "none"])}</span>
            <span className="chip k">{t("maj_lbl")}{t.colon}{majorsText(job, ctx, t)}</span>
          </div>
          <TagChips tags={job.ksa?.knowledge} cls="k" t={t} />
        </div>
        <div><h4>{t("d_s")}</h4><TagChips tags={job.ksa?.skills} cls="s" t={t} /></div>
        <div><h4>{t("d_a")}</h4><TagChips tags={job.ksa?.attributes} cls="a" t={t} /></div>
        <div><h4>{t("d_t")}</h4><TagChips tags={job.tasks} t={t} /></div>
        {fs != null && (
          <div>
            <h4>{t("s_fit")} {fs}%</h4>
            <div className="mini">{t("have")}{t.colon}{[...eduHave, ...reqIds.filter((id) => ctx.fit[id]).map((id) => vname(ctx.vocab, id, t))].join(t.sep) || "—"}</div>
            <div className="mini">{t("lack")}{t.colon}{[...eduLack, ...reqIds.filter((id) => !ctx.fit[id]).map((id) => vname(ctx.vocab, id, t))].join(t.sep) || "—"}</div>
          </div>
        )}
        {job.compliance_flags?.length > 0 && (
          <div className="flagnote">
            {t("flag_note", { f: job.compliance_flags.map((f) => t.pick(OPT.flag[f])).join(t.sep) })}{" "}
            <a href="https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=N0090001&flno=5" target="_blank" rel="noopener noreferrer">{t("law")}</a>
          </div>
        )}
      </div>
      <div className="dl">
        <div>
          <h4>{t("d_dom")} <span className="ai">{t("ai")}</span></h4>
          {job.pm_domains && <Radar t={t} size={240} series={[{ label: "job", v: Object.keys(DOM).map((d) => job.pm_domains[d] || 0), color: "var(--c1)" }]} />}
        </div>
        <div>
          <h4>{t("d_stage")}</h4>
          <div className="flex gap-1 flex-wrap">
            {Object.keys(STG).map((k) => <span key={k} className={"stg" + (job.stage_gate?.includes(k) ? " on" : "")}>{k} {t.pick(STG[k])}</span>)}
          </div>
        </div>
        <div>
          <h4>{t("d_ctx")}</h4>
          <dl className="kv">
            <Row k="c_collab" v={(c.collaborators || []).map((x) => t.pick(COL[x])).join(t.sep)} />
            <Row k="c_prod" v={t.pick(OPT.product[c.product_type])} />
            <Row k="c_mkt" v={t.pick(OPT.market[c.market])} />
            <Row k="c_travel" v={t.pick(OPT.travel[c.travel])} />
            <Row k="c_eng" v={t.pick(OPT.english[c.english_level])} />
            <Row k="c_lang" v={t.pick(OPT.jdlang[job.jd_lang])} />
          </dl>
        </div>
        <div className="flex gap-3 flex-wrap items-center noprint">
          <button className="tool" onClick={() => printPdf(cardRef.current.closest("article"))}>{t("x_pdf")}</button>
          {/* Only the job ID goes to the report form (PRD 8.5). */}
          <a className="text-[13px] font-semibold" target="_blank" rel="noopener noreferrer"
            href={`${REPO}/issues/new?title=${encodeURIComponent(`[回報] ${job.job_id}`)}`}>{t("report")}</a>
        </div>
      </div>
    </div>
  );
}

function JobCard({ job, t, ctx, open, toggle }) {
  const { shown, original } = titles(job, t);
  const fs = hasProfile(ctx.fit, ctx.me) ? fitScore(job, ctx.fit, ctx.me) : null;
  return (
    <article className="card job">
      <div className="job-top">
        <div className="min-w-0">
          <p className="job-title">{shown}</p>
          {original && <div className="mini">{t("orig_title")}{t.colon}{original}</div>}
          <div className="job-co">
            <span>{companyName(job, t)}</span><ListingBadge job={job} t={t} />
            {job.parent_company && <span className="mini">{t("parent")}{t.colon}{job.parent_company}</span>}
          </div>
          <div className="job-meta">
            <span>{t.industry(job.industry)}</span><span>{t.location(job.location)}</span>
            <span>{t.pick(OPT.edu[job.education_req?.level || "none"])}</span><span>{t.salary(job.salary_desc)}</span>
            <span>{t("first_seen")} {job.first_seen_date}</span>{job.closed_date && <span>{t("closed_on")} {job.closed_date}</span>}
          </div>
        </div>
        <div className="job-side">
          <StatusChip job={job} t={t} />
          {job.role_type && <span className="badge">{job.role_type}</span>}
          {fs != null && <span className={"fit " + fitLevel(fs)} title={t(fitLevel(fs))}>{t("s_fit")} {fs}%</span>}
        </div>
      </div>
      <div className="job-actions">
        {job.ai_status === "done"
          ? <button className="link-btn text-[13px]" aria-expanded={open} onClick={toggle}>{open ? t("less") + " ▴" : t("more") + " ▾"}</button>
          : <span className="mini">{t("pending_note")}</span>}
        <a className="text-[13px] font-semibold" href={job.url} target="_blank" rel="noopener noreferrer">{t("to104")}</a>
      </div>
      {open && <JobDetail job={job} t={t} ctx={ctx} />}
    </article>
  );
}

export default function Jobs({ t, data, fit, me, filters: f, setFilters, flash }) {
  const [openIds, setOpenIds] = useState(() => new Set());
  const [shown, setShown] = useState(PAGE_SIZE);
  const ctx = { vocab: data.vocab, majors: data.majors, fit, me };
  const list = useMemo(() => filterJobs(data.db.jobs, f, ctx), [data, f, fit, me]); // eslint-disable-line react-hooks/exhaustive-deps
  // Industry options follow the other filters and show how many jobs each would give.
  const industries = useMemo(() => {
    const counts = new Map();
    for (const j of filterJobs(data.db.jobs, { ...f, ind: "all", sort: "none" }, ctx)) if (j.industry) counts.set(j.industry, (counts.get(j.industry) || 0) + 1);
    if (f.ind !== "all" && !counts.has(f.ind)) counts.set(f.ind, 0);
    return [...counts.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0], "zh-Hant-TW"));
  }, [data, f, fit, me]); // eslint-disable-line react-hooks/exhaustive-deps
  const set = (k) => (v) => { setFilters({ ...f, [k]: v }); setShown(PAGE_SIZE); };
  const setQ = (e) => { setFilters({ ...f, q: e.target.value }); setShown(PAGE_SIZE); };
  const today = todayTPE();
  const pendingCount = data.db.jobs.filter((j) => (f.status === "all" || j.status === f.status) && j.ai_status !== "done").length;
  const exportCsv = () => {
    download(fileName(t.lang === "zh" ? "職缺總表" : "jobs", "csv", today), "text/csv;charset=utf-8", jobsCSV(list, ctx, t, today));
    flash(t("x_csv_jobs", { n: list.length }));
  };
  return (
    <section className="page">
      <PageHead page="jobs" t={t} />
      <div className="card controls">
        <div className="field q"><label htmlFor="f-q">{t("f_search")}</label>
          <input id="f-q" type="search" placeholder={t("f_q")} value={f.q} onChange={setQ} /></div>
        <Sel id="f-role" label={t("f_role")} value={f.role} onChange={set("role")} opts={[["all", t("all")], ["PM", "PM"], ["PjM", "PjM"], ["Other", "Other"]]} />
        <Sel id="f-lst" label={t("f_listing")} value={f.lst} onChange={set("lst")} opts={[["all", t("all")], ...Object.keys(OPT.listing).map((k) => [k, t.pick(OPT.listing[k])])]} />
        <Sel id="f-ind" label={t("f_ind")} value={f.ind} onChange={set("ind")} opts={[["all", t("all")], ...industries.map(([i, n]) => [i, t.lang === "zh" ? `${i}（${n}）` : `${t.industry(i)} (${n})`])]} />
        <Sel id="f-status" label={t("f_status")} value={f.status} onChange={set("status")} opts={[["all", t("all")], ["open", t("open")], ["closed", t("closed")]]} />
        <Sel id="f-sort" label={t("f_sort")} value={f.sort} onChange={set("sort")} opts={[["new", t("s_new")], ["co", t("s_co")], ["fit", t("s_fit")]]} />
      </div>
      {(f.role !== "all" || f.sort === "fit") && pendingCount > 0 && (
        <div className="notice" role="note"><span>{t("role_pending", { n: pendingCount })}</span></div>
      )}
      <div className="flex gap-2.5 items-center flex-wrap">
        <span className="mini">{t("n_jobs", { n: list.length })}</span>
        {f.tag && <button className="tagfilter" onClick={() => setFilters({ ...f, tag: null })}>{t("tagf")}{t.colon}{vname(data.vocab, f.tag, t)} ✕</button>}
        {JSON.stringify(f) !== JSON.stringify(DEFAULT_FILTERS) && (
          <button className="link-btn text-[13px]" onClick={() => { setFilters(DEFAULT_FILTERS); setShown(PAGE_SIZE); setOpenIds(new Set()); }}>{t("clear_filters")}</button>
        )}
        <button className="btn ml-auto" onClick={exportCsv}>{t("x_csv_jobs", { n: list.length })}</button>
      </div>
      <div className="jobs flex flex-col gap-3">
        {list.length === 0 && <div className="card text-center mini">{t("none")}</div>}
        {list.slice(0, shown).map((j) => (
          <JobCard key={j.job_id} job={j} t={t} ctx={ctx} open={openIds.has(j.job_id)}
            toggle={() => setOpenIds((s) => { const n = new Set(s); n.has(j.job_id) ? n.delete(j.job_id) : n.add(j.job_id); return n; })} />
        ))}
      </div>
      {list.length > shown && (
        <button className="btn self-center" onClick={() => setShown(shown + PAGE_SIZE)}>{t("show_more", { n: Math.min(PAGE_SIZE, list.length - shown) })}</button>
      )}
    </section>
  );
}
