// PRD 6 測項 8 (front end): the manual-collection notice shows only while collection_mode is "manual".
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { ManualNotice } from "./components.jsx";
import { makeT } from "./i18n.js";

const html = (db, lang = "zh") => renderToStaticMarkup(<ManualNotice db={db} t={makeT(lang)} />);

describe("ManualNotice", () => {
  it("shows with the last full crawl date in manual mode", () => {
    expect(html({ collection_mode: "manual", last_full_crawl: "2026-11-23" })).toContain("職缺下架狀態停在 2026-11-23");
    expect(html({ collection_mode: "manual", last_full_crawl: "2026-11-23" }, "en")).toContain("as of 2026-11-23");
  });
  it("is hidden in auto mode or when the field is missing", () => {
    expect(html({ collection_mode: "auto" })).toBe("");
    expect(html({})).toBe("");
  });
});
