// PRD 6 測項 7: weekly age labels.
import { describe, expect, it } from "vitest";
import { jobAge, shortDate } from "./age.js";

const BASE = "2026-11-23";
const job = (over = {}) => ({ status: "open", first_seen_date: "2026-11-01", appear_date: null, ...over });
const levelAt = (date) => jobAge(job({ appear_date: date }), BASE).level;

describe("jobAge", () => {
  it("uses week boundaries 0-6 / 7-13 / 14-20 / 21-27 / 28+", () => {
    expect(levelAt("2026-11-23")).toBe("w1"); // 0 days
    expect(levelAt("2026-11-17")).toBe("w1"); // 6
    expect(levelAt("2026-11-16")).toBe("w2"); // 7
    expect(levelAt("2026-11-09")).toBe("w3"); // 14
    expect(levelAt("2026-10-27")).toBe("w4"); // 27
    expect(levelAt("2026-10-26")).toBe("w5"); // 28
  });

  it("prefers appear_date, falls back to first_seen_date", () => {
    expect(jobAge(job({ appear_date: "2026-11-20" }), BASE)).toMatchObject({ basis: "appear", date: "2026-11-20", days: 3, inDb: 22 });
    expect(jobAge(job(), BASE)).toMatchObject({ basis: "first", level: "w4", days: 22 });
  });

  it("marks launch-day rows without appear_date as before launch", () => {
    expect(jobAge(job({ first_seen_date: "2026-10-17" }), BASE)).toMatchObject({ level: "pre", days: null, inDb: 37 });
    expect(jobAge(job({ first_seen_date: "2026-10-17", appear_date: "2026-11-20" }), BASE).level).toBe("w1");
  });

  it("depends on the data date, not the clock", () => {
    expect(jobAge(job({ appear_date: "2026-11-20" }), "2026-11-23").level).toBe("w1");
    expect(jobAge(job({ appear_date: "2026-11-20" }), "2026-12-30").level).toBe("w5");
  });

  it("shows nothing for closed jobs or without a data date", () => {
    expect(jobAge(job({ status: "closed" }), BASE)).toBeNull();
    expect(jobAge(job(), null)).toBeNull();
  });

  it("formats short dates", () => {
    expect(shortDate("2026-11-05")).toBe("11/5");
  });
});
