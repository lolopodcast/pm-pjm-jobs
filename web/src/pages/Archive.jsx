import { useEffect, useState } from "react";
import { ListingBadge, PageHead } from "../components.jsx";
import { companyName, loadArchive, titles, vname } from "../data.js";

export default function Archive({ t, data }) {
  const [year, setYear] = useState(data.archives[0] || "");
  const [rows, setRows] = useState(null);
  useEffect(() => {
    if (!year) return;
    setRows(null);
    loadArchive(year).then(setRows).catch(() => setRows([]));   // loaded only when this page is opened (PRD 5.4)
  }, [year]);
  return (
    <section className="page">
      <PageHead page="archive" t={t} lede={t("ar_lede")} />
      {!data.archives.length ? <div className="card mini">{t("ar_none")}</div> : (
        <>
          <div className="card">
            <div className="field" style={{ width: 140 }}><label htmlFor="ar-year">{t("ar_year")}</label>
              <select id="ar-year" value={year} onChange={(e) => setYear(e.target.value)}>{data.archives.map((y) => <option key={y}>{y}</option>)}</select></div>
          </div>
          <div className="card tbl-wrap">
            {!rows ? <span className="mini">{t("loading")}</span> : (
              <table className="tbl">
                <thead><tr>{[t("f_role"), t.lang === "zh" ? "職稱" : "Title", t.lang === "zh" ? "公司" : "Company", t("first_seen"), t("closed_on"), t("d_s")].map((h) => <th key={h}>{h}</th>)}</tr></thead>
                <tbody>
                  {rows.map((j) => (
                    <tr key={j.job_id}>
                      <td>{j.role_type || "—"}</td><td>{titles(j, t).shown}</td>
                      <td>{companyName(j, t)} <ListingBadge job={j} t={t} /></td>
                      <td>{j.first_seen_date}</td><td>{j.closed_date}</td>
                      <td>{(j.ksa_normalized?.skills || []).map((id) => vname(data.vocab, id, t)).join(t.sep)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </>
      )}
    </section>
  );
}
