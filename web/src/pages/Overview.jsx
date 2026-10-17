import { Bars } from "../charts.jsx";
import { PageHead, StatusChip } from "../components.jsx";
import { analysed, companyName, countBy, daysBetween, openJobs, titles, todayTPE, vname } from "../data.js";

export default function Overview({ t, data, go, setFilters }) {
  const jobs = data.db.jobs;
  const open = openJobs(jobs);
  const done = analysed(open);
  const today = todayTPE();
  const fresh = open.filter((j) => daysBetween(j.first_seen_date, today) <= 7);
  const pm = done.filter((j) => j.role_type === "PM").length, pj = done.filter((j) => j.role_type === "PjM").length;
  const pending = open.length - done.length;
  const skills = countBy(done, (j) => j.ksa_normalized?.skills).slice(0, 6).map(([id, n]) => ({ key: id, label: vname(data.vocab, id, t), n }));
  const newest = [...open].sort((a, b) => b.first_seen_date.localeCompare(a.first_seen_date) || a.job_id.localeCompare(b.job_id)).slice(0, 5);
  const upd = data.db.updated_at ? data.db.updated_at.slice(5, 16).replace("T", " ") : "—";
  const Stat = ({ k, v, s, small }) => (
    <div className="card stat"><div className="k">{k}</div><div className="v" style={small ? { fontSize: 22, paddingBlock: 4 } : undefined}>{v}</div>{s && <div className="s">{s}</div>}</div>
  );
  const pct = (a) => (pm + pj ? Math.round((a / (pm + pj)) * 100) : 0);
  return (
    <section className="page">
      <PageHead page="overview" t={t} lede={t("ov_lede")} />
      <div className="grid4">
        <Stat k={t("st_open")} v={open.length} s={pending ? t("st_pending", { n: pending }) : null} />
        <Stat k={t("st_new")} v={fresh.length} />
        <Stat k={t("st_split")} v={pm + pj ? `${pm} : ${pj}` : "—"} s={pm + pj ? `PM ${pct(pm)}% · PjM ${pct(pj)}%` : t("analysing")} />
        <Stat k={t("st_upd")} v={upd} s={t("st_fresh")} small />
      </div>
      <div className="grid2">
        <div className="card">
          <div className="sec-h"><h2 className="h2">{t("ov_new")}</h2><button className="link-btn" onClick={() => go("jobs")}>{t("ov_all")}</button></div>
          {newest.map((j) => (
            <div className="match" key={j.job_id}>
              <div className="min-w-0"><div className="font-semibold">{titles(j, t).shown}</div><div className="mini">{companyName(j, t)} · {j.first_seen_date}</div></div>
              <StatusChip job={j} t={t} />
            </div>
          ))}
        </div>
        <div className="card">
          <div className="sec-h"><h2 className="h2">{t("ov_top")}</h2><button className="link-btn" onClick={() => go("insights")}>{t("ov_more")}</button></div>
          {skills.length ? (
            <Bars rows={skills} color="var(--c2)" onPick={(r) => { setFilters((f) => ({ ...f, tag: r.key, status: "open" })); go("jobs"); }} />
          ) : <p className="mini">{t("no_ai_yet")}</p>}
        </div>
      </div>
    </section>
  );
}
