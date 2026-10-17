import { describe, expect, it } from "vitest";
import { checkCode } from "./Gate.jsx";

describe("access gate", () => {
  it("accepts the code regardless of case and surrounding spaces", async () => {
    expect(await checkCode("pmj2026")).toBe(true);
    expect(await checkCode("  PMJ2026 ")).toBe(true);
  });
  it("rejects anything else", async () => {
    expect(await checkCode("pmj2025")).toBe(false);
    expect(await checkCode("")).toBe(false);
  });
});
