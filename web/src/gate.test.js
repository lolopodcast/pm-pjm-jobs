import { describe, expect, it } from "vitest";
import { checkCode, hashCode } from "./Gate.jsx";

// The real code is not written here: this repo is public. A sample code checks the same logic.
describe("access gate", async () => {
  const hash = await hashCode("sample-2026");
  it("accepts the code regardless of case and surrounding spaces", async () => {
    expect(await checkCode("sample-2026", hash)).toBe(true);
    expect(await checkCode("  SAMPLE-2026 ", hash)).toBe(true);
  });
  it("rejects anything else", async () => {
    expect(await checkCode("sample-2025", hash)).toBe(false);
    expect(await checkCode("", hash)).toBe(false);
    expect(await checkCode("sample-2026")).toBe(false);   // not the site's real code
  });
});
