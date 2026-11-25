// Weekly age label for open jobs (PRD 5.2 刊登週數標籤, 5.6 色票, 6 測項 7).
import { daysBetween } from "./data.js";

// Day of the first full crawl: jobs first seen that day were already on 104 before launch.
export const LAUNCH_DATE = "2026-10-17";
export const AGE_LEVELS = ["w1", "w2", "w3", "w4", "w5", "pre"];

/**
 * Age of one job, counted against the data date (`updated_at`), never the viewer's clock.
 * Returns null for closed jobs. `level` is w1…w5 (week 1…4, 4+ weeks) or "pre" (before launch).
 */
export function jobAge(job, baseDate) {
  if (job.status !== "open" || !baseDate) return null;
  const inDb = job.first_seen_date ? Math.max(0, daysBetween(job.first_seen_date, baseDate)) : null;
  if (!job.appear_date && job.first_seen_date === LAUNCH_DATE) return { level: "pre", basis: "first", date: job.first_seen_date, days: null, inDb };
  const basis = job.appear_date ? "appear" : "first";
  const date = job.appear_date || job.first_seen_date;
  if (!date) return null;
  const days = Math.max(0, daysBetween(date, baseDate));
  return { level: "w" + Math.min(5, Math.floor(days / 7) + 1), basis, date, days, inDb };
}

/** "2026-11-20" -> "11/20" */
export const shortDate = (d) => (d ? `${Number(d.slice(5, 7))}/${Number(d.slice(8, 10))}` : "");
