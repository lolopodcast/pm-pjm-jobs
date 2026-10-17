// Data loading and small shared helpers.
const BASE = import.meta.env.BASE_URL + "data/";

async function get(path) {
  const r = await fetch(BASE + path, { cache: "no-cache" });
  if (!r.ok) throw new Error(`${path}: HTTP ${r.status}`);
  return r.json();
}

export async function loadData() {
  const [db, ksa, task, major, index] = await Promise.all([
    get("data.json"), get("vocab/ksa_vocabulary.json"), get("vocab/task_vocabulary.json"),
    get("vocab/major_vocabulary.json"), get("index.json").catch(() => ({ archives: [] })),
  ]);
  const vocab = {};
  for (const it of ksa.items) vocab[it.id] = it;
  for (const it of task.items) vocab[it.id] = { ...it, category: "T" };
  const byCat = { K: [], S: [], A: [], T: [] };
  for (const it of Object.values(vocab)) byCat[it.category].push(it);
  const majors = Object.fromEntries(major.items.map((i) => [i.id, i]));
  return { db, vocab, byCat, majors, archives: index.archives || [] };
}

export const loadArchive = (year) => get(`history_archive_${year}.json`);

export const analysed = (jobs) => jobs.filter((j) => j.ai_status === "done");
export const openJobs = (jobs) => jobs.filter((j) => j.status === "open");
export const daysBetween = (a, b) => Math.round((new Date(b) - new Date(a)) / 86400000);
export const todayTPE = () => new Date(Date.now() + 8 * 3600e3).toISOString().slice(0, 10);

export const vname = (vocab, id, t) => (vocab[id] ? t.pick([vocab[id].zh, vocab[id].en]) : id);

/** Title shown in the current language, plus the original when it differs. */
export function titles(job, t) {
  const shown = t.lang === "en" ? job.title_en || job.title : job.title;
  return { shown, original: shown !== job.title ? job.title : null };
}
export const companyName = (job, t) => (t.lang === "en" && job.company_en ? job.company_en : job.company);

export function countBy(items, keysOf) {
  const m = new Map();
  for (const it of items) for (const k of keysOf(it) || []) m.set(k, (m.get(k) || 0) + 1);
  return [...m.entries()].sort((a, b) => b[1] - a[1]);
}

/** Tags from all four groups, used for search. */
export function tagText(job) {
  const k = job.ksa || {};
  return [...(k.knowledge || []), ...(k.skills || []), ...(k.attributes || []), ...(job.tasks || [])].flatMap((x) => [x.zh, x.en]);
}
