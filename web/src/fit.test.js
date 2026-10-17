// PRD 6 測項 4 (fit) and 測項 6 (CSV export safety).
import { describe, expect, it } from "vitest";
import { domainProfile, fitScore, gaps } from "./fit.js";
import { csvCell, toCSV } from "./exporting.js";

const job = (over = {}) => ({
  ai_status: "done",
  ksa_normalized: { knowledge: ["K1"], skills: ["S1", "S2"], attributes: ["A1"] },
  tasks_normalized: ["T1"],
  education_req: { level: "none", majors: [], major_required: false },
  ...over,
});
const none = { edu: "", majors: [] };

describe("fitScore", () => {
  it("is 100 when everything is held and 0 when nothing is", () => {
    expect(fitScore(job(), { K1: 1, S1: 1, S2: 1, A1: 1, T1: 1 }, none)).toBe(100);
    expect(fitScore(job(), {}, none)).toBe(0);
  });
  it("counts 略懂 as half", () => {
    expect(fitScore(job(), { K1: 0.5, S1: 0.5, S2: 0.5, A1: 0.5, T1: 0.5 }, none)).toBe(50);
  });
  it("re-weights when a category has no requirement", () => {
    const j = job({ ksa_normalized: { knowledge: [], skills: ["S1"], attributes: [] }, tasks_normalized: [] });
    expect(fitScore(j, { S1: 1 }, none)).toBe(100);
  });
  it("returns null for jobs without analysis", () => {
    expect(fitScore(job({ ai_status: "pending" }), {}, none)).toBeNull();
  });
  it("adds degree and major as knowledge items", () => {
    const j = job({ ksa_normalized: { knowledge: [], skills: [], attributes: [] }, tasks_normalized: [],
      education_req: { level: "ma", majors: ["MAJ_EE"], major_required: false } });
    expect(fitScore(j, {}, { edu: "ma", majors: ["MAJ_EE"] })).toBe(100);
    expect(fitScore(j, {}, { edu: "ba", majors: ["MAJ_EE"] })).toBe(50);          // degree not met
    expect(fitScore(j, {}, { edu: "ma", majors: ["MAJ_BUS"] })).toBe(75);         // preferred major: 0.5
    const strict = { ...j, education_req: { ...j.education_req, major_required: true } };
    expect(fitScore(strict, {}, { edu: "ma", majors: ["MAJ_BUS"] })).toBe(50);    // required major: 0
    expect(fitScore(j, {}, { edu: "ma", majors: ["MAJ_CS"] })).toBe(75);          // CS does not satisfy EE
  });
});

describe("gaps and profile", () => {
  it("lists unticked items by frequency", () => {
    expect(gaps([job(), job()], { S1: 1 }, 2)).toEqual([["K1", 2], ["S2", 2]]);
  });
  it("profile sums to about 100", () => {
    const v = { S1: { domain: "D7" }, S2: { domain: "D6" } };
    const p = domainProfile({ S1: 1, S2: 0.5 }, v);
    expect(p[6]).toBe(67);
    expect(p[5]).toBe(33);
  });
});

describe("CSV export", () => {
  it("neutralises formulas and quotes", () => {
    expect(csvCell('=HYPERLINK("x")')).toBe(`"'=HYPERLINK(""x"")"`);
    expect(csvCell("-1")).toBe("'-1");
    expect(csvCell("專案經理")).toBe("專案經理");
  });
  it("starts with a BOM and ends with the source line", () => {
    const s = toCSV([["a", "b"]], "來源");
    expect(s.charCodeAt(0)).toBe(0xfeff);
    expect(s.endsWith("\r\n來源")).toBe(true);
  });
});
