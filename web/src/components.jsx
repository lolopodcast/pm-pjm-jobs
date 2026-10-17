import { OPT } from "./i18n.js";

const PATHS = {
  menu: "M4 6h16M4 12h16M4 18h16",
  home: "M3 11l9-7 9 7v9a1 1 0 0 1-1 1h-5v-6h-6v6H4a1 1 0 0 1-1-1z",
  sun: "M12 4V2M12 22v-2M4.9 4.9 3.5 3.5M20.5 20.5l-1.4-1.4M4 12H2M22 12h-2M4.9 19.1l-1.4 1.4M20.5 3.5l-1.4 1.4M12 7a5 5 0 1 0 0 10 5 5 0 0 0 0-10z",
  moon: "M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z",
  overview: "M4 4h7v7H4zM13 4h7v4h-7zM13 10h7v10h-7zM4 13h7v7H4z",
  jobs: "M4 7h16v12H4zM9 7V5h6v2M4 12h16",
  insights: "M4 20V10M10 20V4M16 20v-7M22 20H2",
  fit: "M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm0 5a5 5 0 1 0 0 10 5 5 0 0 0 0-10zm0 4a1 1 0 1 0 0 2 1 1 0 0 0 0-2z",
  archive: "M3 5h18v4H3zM5 9v10h14V9M10 13h4",
  about: "M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zM12 11v6M12 7h.01",
  download: "M12 3v12M7 10l5 5 5-5M5 20h14",
};

export function Icon({ name, size = 20 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d={PATHS[name]} />
    </svg>
  );
}

export const PAGES = ["overview", "jobs", "insights", "fit", "archive", "about"];

export function PageHead({ page, t, lede }) {
  return (
    <div className="flex flex-col gap-2">
      <h1 className="h1"><span className="n">{PAGES.indexOf(page)}.</span><span>{t("p_" + page)}</span></h1>
      {lede && <p className="lede">{lede}</p>}
    </div>
  );
}

export function StatusChip({ job, t }) {
  if (job.status === "open" && job.ai_status !== "done") return <span className="st pending">{t("analysing")}</span>;
  return <span className={"st " + job.status}>{t(job.status)}</span>;
}

export const ListingBadge = ({ job, t }) => <span className="badge listed">{t.pick(OPT.listing[job.listing_type]) || job.listing_type}</span>;

export function TagChips({ tags, cls, t }) {
  return (
    <div className="chips">
      {(tags || []).map((x) => (
        <span key={x.zh} className={"chip " + (cls || "")} title={x.en}>
          {t.lang === "en" ? x.en : <>{x.zh}{x.en && x.en !== x.zh && <small>{x.en}</small>}</>}
        </span>
      ))}
    </div>
  );
}

export function Seg({ value, options, onChange }) {
  return (
    <div className="seg">
      {options.map(([v, l]) => <button key={v} className={value === v ? "on" : ""} aria-pressed={value === v} onClick={() => onChange(v)}>{l}</button>)}
    </div>
  );
}
