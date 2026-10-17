// Fit scoring (PRD 5.5). Pure functions so they can be unit tested (PRD 6 測項 4).
import { EDU_RANK } from "./i18n.js";

export const WEIGHTS = { S: 0.35, K: 0.25, T: 0.25, A: 0.15 };
const SCI_ENG = ["MAJ_CS", "MAJ_EE", "MAJ_IE", "MAJ_ME", "MAJ_CHEM", "MAJ_MAT", "MAJ_BIO", "MAJ_CIVIL", "MAJ_SCI", "MAJ_SCI_ENG"];

export function requirements(job) {
  const n = job.ksa_normalized || {};
  return { K: n.knowledge || [], S: n.skills || [], A: n.attributes || [], T: job.tasks_normalized || [] };
}

const majorMatch = (mine, req) => mine.includes(req) || (req === "MAJ_SCI_ENG" && mine.some((m) => SCI_ENG.includes(m)));

/** Degree and major count as extra K items (PRD 5.5 第 3 點). */
export function eduItems(job, me) {
  const e = job.education_req || {};
  const items = [];
  if (e.level && e.level !== "none") {
    items.push({ kind: "edu", score: me.edu && EDU_RANK[me.edu] >= EDU_RANK[e.level] ? 1 : 0 });
  }
  if (e.majors && e.majors.length) {
    const ok = e.majors.some((r) => majorMatch(me.majors || [], r));
    items.push({ kind: "maj", score: ok ? 1 : e.major_required ? 0 : 0.5 });
  }
  return items;
}

/** 0–100, or null when the job has no AI analysis yet. Compliance flags never take part. */
export function fitScore(job, fit, me) {
  if (job.ai_status !== "done") return null;
  const req = requirements(job);
  let total = 0, wsum = 0;
  for (const [cat, w] of Object.entries(WEIGHTS)) {
    const scores = req[cat].map((id) => fit[id] || 0);
    if (cat === "K") eduItems(job, me).forEach((it) => scores.push(it.score));
    if (!scores.length) continue;
    total += w * (scores.reduce((a, b) => a + b, 0) / scores.length);
    wsum += w;
  }
  return wsum ? Math.round((total / wsum) * 100) : null;
}

export const fitLevel = (v) => (v >= 70 ? "hi" : v >= 40 ? "mid" : "lo");
export const hasProfile = (fit, me) => Object.values(fit).some((v) => v > 0) || !!me.edu || (me.majors || []).length > 0;

/** Most-requested vocabulary items the user has not ticked (degree and major are excluded). */
export function gaps(jobs, fit, limit = 10) {
  const c = new Map();
  for (const j of jobs) {
    const r = requirements(j);
    for (const id of [...r.K, ...r.S, ...r.A, ...r.T]) if (!fit[id]) c.set(id, (c.get(id) || 0) + 1);
  }
  return [...c.entries()].sort((a, b) => b[1] - a[1]).slice(0, limit);
}

/** Share of the user's ticked weight in each PM domain, summing to 100. */
export function domainProfile(fit, vocabById) {
  const keys = ["D1", "D2", "D3", "D4", "D5", "D6", "D7"];
  const sums = Object.fromEntries(keys.map((k) => [k, 0]));
  for (const [id, w] of Object.entries(fit)) {
    const d = vocabById[id]?.domain;
    if (d && w) sums[d] += w;
  }
  const tot = Object.values(sums).reduce((a, b) => a + b, 0) || 1;
  return keys.map((k) => Math.round((sums[k] / tot) * 100));
}
