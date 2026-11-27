// Industry filter: jobs with no industry (manual input, PRD 2.5) can be selected as "Other".
import { describe, expect, it } from "vitest";
import { DEFAULT_FILTERS } from "./data.js";
import { filterJobs, IND_NONE } from "./pages/Jobs.jsx";

const job = (id, industry) => ({ job_id: id, status: "open", industry, first_seen_date: "2026-11-27", company: id, title: "PM" });
const jobs = [job("a", "半導體製造業"), job("b", null), job("c", "電信相關業"), job("d", undefined)];
const ctx = { vocab: {}, fit: {}, me: {} };
const ids = (ind) => filterJobs(jobs, { ...DEFAULT_FILTERS, ind, sort: "co" }, ctx).map((j) => j.job_id);

describe("industry filter", () => {
  it("selects jobs without an industry", () => {
    expect(ids(IND_NONE)).toEqual(["b", "d"]);
  });
  it("keeps the normal choices working", () => {
    expect(ids("半導體製造業")).toEqual(["a"]);
    expect(ids("all")).toEqual(["a", "b", "c", "d"]);
  });
});
