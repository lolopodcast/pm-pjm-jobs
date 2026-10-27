import { describe, expect, it } from "vitest";
import { checkCode, hashCode, normalizeCode, sha256Fallback } from "./Gate.jsx";

// The real code is not written here: this repo is public. A sample code checks the same logic.
describe("access gate", async () => {
  const hash = await hashCode("sample2026");
  it("accepts the code regardless of case and surrounding spaces", async () => {
    expect(await checkCode("sample2026", hash)).toBe(true);
    expect(await checkCode("  SAMPLE2026 ", hash)).toBe(true);
  });
  it("accepts what phones and Chinese input methods actually send", async () => {
    expect(await checkCode("ｓａｍｐｌｅ２０２６", hash)).toBe(true);          // full-width input mode
    expect(await checkCode("sample 2026", hash)).toBe(true);                   // stray inner space
    expect(await checkCode("sample2026​", hash)).toBe(true);              // invisible char pasted from chat apps
    expect(await checkCode(" Sample2026\n", hash)).toBe(true);
  });
  it("rejects anything else", async () => {
    expect(await checkCode("sample2025", hash)).toBe(false);
    expect(await checkCode("", hash)).toBe(false);
    expect(await checkCode("sample2026")).toBe(false);   // not the site's real code
  });
  it("keeps the stored hash valid: the plain code normalizes to itself", () => {
    expect(normalizeCode("sample2026")).toBe("sample2026");
  });
  it("fallback SHA-256 matches the browser one (for phones without crypto.subtle)", async () => {
    for (const text of ["", "abc", "pmj-gate:sample2026", "中文", "x".repeat(200)]) {
      const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text));
      const ref = [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
      expect(sha256Fallback(text)).toBe(ref);
    }
  });
});
