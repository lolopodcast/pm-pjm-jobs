// Interface text. Every entry holds [中文, English] so both languages always stay in step (PRD 5.6).
// Taiwan Traditional Chinese only.
export const T = {
  title: ["上市櫃 PM／PjM 新人職缺觀測站", "PM/PjM Entry-Level Job Observatory"],
  p_overview: ["總覽", "Overview"], p_jobs: ["職缺列表", "Jobs"], p_insights: ["統計儀表板", "Insights"],
  p_fit: ["我的配適度", "My Fit"], p_archive: ["歷史職缺", "Archive"], p_about: ["關於與方法", "About"],
  loading: ["資料載入中…", "Loading data…"], load_fail: ["資料載入失敗，請稍後重新整理。", "Could not load data. Please refresh later."],
  stale: ["資料已超過 36 小時未更新，可能是每日排程暫停，內容僅供參考。", "Data has not been updated for over 36 hours; the daily job may be paused."],
  offline: ["目前離線，顯示的是上次儲存的資料。", "You are offline; showing the last saved data."],
  update_ready: ["網站有新版本。", "A new version is available."], reload: ["重新整理", "Reload"],
  ov_lede: ["每天凌晨自動整理 104 人力銀行上市、上櫃、興櫃公司（含子公司）的 PM／PjM 新人職缺，並以 AI 分析職能需求與工作內容。",
    "Every night we collect entry-level PM/PjM openings on 104 Job Bank at listed, OTC and emerging-market companies (and their subsidiaries), then use AI to analyse the skills and work each one asks for."],
  st_open: ["開放中職缺", "Open jobs"], st_new: ["近 7 天新增", "New in 7 days"], st_split: ["PM／PjM 比例", "PM / PjM split"], st_upd: ["資料更新時間", "Last updated"],
  st_pending: ["其中 {n} 筆 AI 分析中", "{n} still being analysed"], st_fresh: ["每日凌晨 03:05 更新", "Refreshed daily at 03:05"],
  ov_new: ["最新職缺", "Newest jobs"], ov_all: ["看全部職缺 →", "See all jobs →"],
  ov_top: ["最常被要求的技能", "Most-requested skills"], ov_more: ["看統計儀表板 →", "Open insights →"],
  f_q: ["搜尋公司、職稱、技能（中英皆可）", "Search company, title or skill"], f_search: ["搜尋", "Search"],
  f_role: ["職務類型", "Role"], f_listing: ["上市別", "Market"], f_ind: ["產業", "Industry"], f_status: ["狀態", "Status"], f_sort: ["排序", "Sort"],
  all: ["全部", "All"], s_new: ["最新出現", "Newest"], s_co: ["公司名稱", "Company"], s_fit: ["配適度", "Fit"],
  n_jobs: ["共 {n} 筆職缺", "{n} jobs"], none: ["沒有符合條件的職缺，試著放寬篩選條件。", "No jobs match. Try loosening the filters."],
  tagf: ["標籤", "Tag"], clear_filters: ["清除篩選", "Clear filters"],
  reset_title: ["重設網站", "Reset this site"],
  reset_desc: ["清除這台裝置上本站保存的所有設定：語言、深淺主題、配適度勾選與進入碼狀態，回到第一次進入的畫面。不影響其他網站。",
    "Clears everything this site keeps on this device (language, theme, your fit answers and the access code) and starts over as on a first visit. Other sites are not affected."],
  reset_btn: ["重設網站", "Reset site"], reset_confirm: ["再按一次確認重設", "Click again to reset"],
  role_pending: ["職務類型與配適度由 AI 判定。目前還有 {n} 筆職缺分析中，不會出現在這個篩選或排序中，分析完成後會自動加入。",
    "Role type and fit come from the AI analysis. {n} jobs are still being analysed and are left out of this filter or sort until they are done."],
  fit_no_ai: ["配適度要和「已完成 AI 分析」的職缺比對，目前還沒有分析完成的職缺。你可以先勾選能力，分析完成後結果會自動出現。",
    "Fit is calculated against jobs with finished AI analysis, and none are ready yet. You can tick your abilities now; results appear once analysis is done."], show_more: ["再顯示 {n} 筆", "Show {n} more"],
  open: ["開放中", "Open"], closed: ["已關閉", "Closed"], analysing: ["分析中", "Analysing"],
  first_seen: ["首次出現", "First seen"], closed_on: ["關閉於", "Closed"], orig_title: ["原文職稱", "Original title"], parent: ["母公司", "Parent"],
  more: ["展開分析", "Show analysis"], less: ["收合", "Hide"], to104: ["前往 104 原始職缺 ↗", "Open on 104 ↗"],
  report: ["回報錯誤 ↗", "Report an error ↗"],
  ai: ["AI 產生", "AI-generated"], ai_note: ["可能有誤，以 104 原始職缺為準。", "May contain errors; the 104 posting is authoritative."],
  pending_note: ["AI 分析排隊中，基本資料可先參考。", "AI analysis is queued; basic details are shown meanwhile."],
  d_sum: ["職缺摘要", "Summary"], d_k: ["知識 Knowledge", "Knowledge"], d_s: ["技能 Skills", "Skills"], d_a: ["特質 Attributes", "Attributes"],
  d_t: ["工作職責", "Main tasks"], d_dom: ["PM 七大構面", "Seven PM domains"], d_stage: ["參與的 Stage-Gate 階段", "Stage-Gate stages involved"],
  d_ctx: ["職務情境", "Work context"], c_collab: ["主要協作單位", "Works with"], c_prod: ["產品類型", "Product type"], c_mkt: ["市場", "Market"],
  c_travel: ["出差", "Travel"], c_eng: ["英文使用", "English use"], c_lang: ["JD 原文語言", "JD language"],
  edu_lbl: ["學歷", "Degree"], maj_lbl: ["科系", "Major"], maj_any: ["科系不拘", "Any major"], req: ["必要", "required"], pref: ["尤佳", "preferred"],
  flag_note: ["此職缺含可能不符《就業服務法》第 5 條之條件：{f}。此條件未列入任何統計與配適度計算。",
    "This posting includes conditions that may conflict with Article 5 of the Employment Service Act: {f}. They are excluded from all statistics and fit scores."],
  law: ["查看法條 ↗", "Read the law ↗"],
  in_lede: ["所有圖表以「已完成 AI 分析」的開放中職缺計算。點選圖上的標籤可直接篩選職缺。", "Charts count open jobs with finished AI analysis. Click a label to filter the job list."],
  in_range: ["時間範圍", "Period"], r30: ["近 30 天", "30 days"], r90: ["近 90 天", "90 days"], rall: ["全部", "All time"],
  jobs_unit: ["筆", "jobs"],
  ch_ksa: ["KSA 出現次數 Top 20", "Top 20 KSA tags"], tab_k: ["知識 K", "Knowledge"], tab_s: ["技能 S", "Skills"], tab_a: ["特質 A", "Attributes"],
  ch_task: ["新人最常做的工作 Top 20", "Top 20 tasks for newcomers"],
  ch_radar: ["PM 七大構面平均比重", "Average weight of the seven PM domains"],
  ch_heat: ["Stage-Gate 參與熱度", "Stage-Gate involvement"], heat_note: ["格內數字為參與該階段的職缺比例。", "Each cell shows the share of jobs involved in that stage."],
  ch_collab: ["進公司後主要跟誰共事", "Who you will work with"], ch_ctx: ["職務情境分布", "Work context mix"],
  ch_edu: ["學歷與科系要求", "Degree and major requirements"], edu_dist: ["最低學歷", "Minimum degree"], maj_top: ["最常被要求的科系群組", "Most-requested fields of study"],
  maj_any_share: ["科系不拘的職缺占 {p}%", "{p}% of jobs accept any major"], maj_sfx: ["（必要 {r}）", " ({r} required)"],
  ch_comp: ["職缺合規觀察", "Posting compliance watch"],
  comp_lede: ["含可能不符《就業服務法》第 5 條條件的職缺比例。只呈現統計，不列出公司排行。", "Share of postings with conditions that may conflict with Article 5 of the Employment Service Act. Statistics only, no company ranking."],
  comp_any: ["含任一類條件", "Any condition"], not_stated: ["未提及", "Not stated"], no_ai_yet: ["還沒有完成 AI 分析的職缺，明天再來看看。", "No analysed jobs yet. Check back tomorrow."],
  fit_lede: ["勾選你具備的知識、技能、特質與做過的工作，系統會即時算出你和每個職缺的配適度。資料只存在你的瀏覽器，不會上傳。",
    "Tick the knowledge, skills, traits and tasks you already have. Fit scores update instantly. Your choices stay in this browser and are never uploaded."],
  lv0: ["無", "No"], lv1: ["略懂", "Some"], lv2: ["熟悉", "Strong"],
  fit_my: ["我的能力", "My abilities"], fit_k: ["知識", "Knowledge"], fit_s: ["技能", "Skills"], fit_a: ["特質", "Attributes"], fit_t: ["做過的工作", "Tasks I have done"],
  my_edu: ["我的最高學歷", "My highest degree"], my_maj: ["我的科系（可複選，含雙主修、輔系）", "My field(s) of study (double majors and minors count)"], choose: ["請選擇", "Select"],
  appear: ["{n} 筆職缺要求", "in {n} jobs"], fit_search: ["搜尋項目", "Search items"],
  fit_res: ["配適度最高的職缺", "Best-matching jobs"], fit_gap: ["補強方向：最常被要求但你還沒勾的項目", "What to build next: most-requested items you have not ticked"],
  fit_radar: ["我的構面輪廓 vs 職缺平均", "My domain profile vs the job average"], me: ["我", "Me"], avg: ["職缺平均", "Job average"],
  hi: ["高度符合", "Strong fit"], mid: ["部分符合", "Partial fit"], lo: ["差距較大", "Large gap"],
  fit_disc: ["配適度僅依自評與職缺標籤計算，供參考，不代表錄取機會。", "Fit is based only on your self-assessment and the job tags. It is a guide, not a prediction of being hired."],
  fit_empty: ["先在左側勾選你的能力，這裡就會出現結果。", "Tick your abilities on the left to see results here."],
  exp: ["匯出 JSON", "Export JSON"], imp: ["匯入 JSON", "Import JSON"], clr: ["清除我的資料", "Clear my data"], clr2: ["再按一次確認清除", "Click again to clear"],
  imp_ok: ["已匯入自評資料。", "Imported."], imp_bad: ["檔案格式不正確，請選擇先前從本站匯出的 JSON 檔。", "That file is not a valid export from this site."],
  cleared: ["已清除，學歷、科系與所有項目都已重設。", "Cleared. Degree, majors and every item have been reset."],
  have: ["已具備", "You have"], lack: ["尚缺", "Missing"],
  edu_have: ["學歷符合", "Degree met"], edu_lack: ["學歷未達", "Degree not met"], maj_have: ["科系符合", "Major matches"], maj_lack: ["科系不符", "Major does not match"],
  ar_lede: ["關閉超過 30 天的職缺會移到這裡，依年份保存。", "Jobs closed for more than 30 days move here, filed by year."],
  ar_year: ["年份", "Year"], ar_none: ["目前還沒有歸檔的職缺。", "Nothing has been archived yet."],
  x_csv_jobs: ["匯出 CSV（{n} 筆）", "Export CSV ({n} jobs)"], x_pdf: ["存成 PDF", "Save as PDF"], x_page_pdf: ["整頁存成 PDF", "Save page as PDF"],
  x_report_pdf: ["配適度報告存成 PDF", "Save fit report as PDF"],
  src_line: ["資料來源：104 人力銀行、TWSE／TPEx；本站整理於 {d}；AI 分析可能有誤，以 104 原始職缺為準。",
    "Sources: 104 Job Bank, TWSE/TPEx; compiled {d}; AI analysis may contain errors, the 104 posting is authoritative."],
  ab_src: ["資料來源", "Data sources"], ab_ai: ["AI 分析方式與限制", "How the AI analysis works, and its limits"], ab_fw: ["分析架構", "Analytical structure"], ab_disc: ["聲明", "Disclaimer"],
  gate_lede: ["網站目前開放測試中，請輸入進入碼。", "This site is open for testing. Please enter the access code."],
  gate_label: ["進入碼", "Access code"], gate_enter: ["進入網站", "Enter"],
  gate_hint: ["輸入一次後，這台裝置會記住，下次不用再輸入。", "This device will remember it, so you only need to enter it once."],
  gate_wrong: ["進入碼不正確，請再試一次。", "That code is not correct. Please try again."],
  gate_lock: ["鎖定", "Lock"],
  copyright: ["網站設計與分析 © Prof. Shihmin Lo · 職缺資料來源：104 人力銀行 · 僅供教學使用",
    "Site design and analysis © Prof. Shihmin Lo · Job data: 104 Job Bank · For educational use only"],
  theme_l: ["切換為淺色", "Switch to light"], theme_d: ["切換為深色", "Switch to dark"], menu: ["選單", "Menu"], home: ["首頁", "Home"],
};

export const DOM = { D1: ["策略", "Strategy"], D2: ["組合", "Portfolio"], D3: ["流程", "Process"], D4: ["工具", "Tools"], D5: ["市場", "Market"], D6: ["團隊", "Teams"], D7: ["管理", "Mgmt"] };
export const DOM_FULL = { D1: ["策略", "Strategy"], D2: ["產品線組合管理", "Portfolio Management"], D3: ["產品創新流程", "PI Process"], D4: ["產品設計開發工具", "PDD Tools"],
  D5: ["市場研究", "Market Research in PI"], D6: ["文化、團隊與領導", "Culture, Teams & Leadership"], D7: ["產品創新管理", "PI Management"] };
export const STG = { S1: ["行銷", "Marketing"], S2: ["可行性", "Feasibility"], S3: ["產品設計", "Design"], S4: ["模具", "Tooling"], S5: ["工程", "Engineering"], S6: ["上市", "Launch"], EOL: ["終止", "EOL"] };
export const COL = { RD: ["研發", "R&D"], MKT: ["行銷", "Marketing"], SA: ["業務", "Sales"], DQA: ["設計品保", "Design QA"], TE: ["研技", "Test eng."], QA: ["品保", "QA"],
  PE: ["生技", "Process eng."], PUR: ["採購", "Purchasing"], PC: ["生管", "Production control"], MC: ["物管", "Materials"], MFG: ["生產", "Manufacturing"], QC: ["品管", "QC"],
  FAE: ["應用工程", "FAE"], CS: ["客服", "Customer service"], GM: ["總經理室", "GM office"] };
export const OPT = {
  listing: { "上市": ["上市", "TWSE listed"], "上櫃": ["上櫃", "TPEx OTC"], "興櫃": ["興櫃", "Emerging"] },
  product: { hardware: ["硬體", "Hardware"], software: ["軟體", "Software"], service: ["服務", "Service"], mixed: ["綜合", "Mixed"] },
  market: { B2B: ["B2B", "B2B"], B2C: ["B2C", "B2C"], both: ["兩者皆有", "Both"] },
  travel: { none: ["不需出差", "None"], occasional: ["偶爾出差", "Occasional"], frequent: ["經常出差", "Frequent"], overseas: ["需外派", "Overseas posting"] },
  english: { none: ["不需要", "Not required"], reading: ["閱讀文件", "Reading"], daily: ["日常溝通", "Daily use"], primary: ["主要工作語言", "Main language"] },
  jdlang: { zh: ["中文", "Chinese"], en: ["英文", "English"], mixed: ["中英夾雜", "Mixed"] },
  flag: { GENDER: ["性別", "Gender"], AGE: ["年齡", "Age"], APPEARANCE: ["容貌", "Appearance"], MILITARY_SERVICE: ["役畢", "Military service"],
    MARITAL: ["婚姻", "Marital status"], ORIGIN: ["籍貫", "Place of origin"], OTHER: ["其他", "Other"] },
  edu: { none: ["學歷不拘", "Any degree"], hs: ["高中職以上", "High school+"], as: ["專科以上", "Associate+"], ba: ["大學以上", "Bachelor's+"], ma: ["碩士以上", "Master's+"], phd: ["博士", "PhD"] },
  myedu: { hs: ["高中職", "High school"], as: ["專科", "Associate"], ba: ["大學", "Bachelor's"], ma: ["碩士", "Master's"], phd: ["博士", "PhD"] },
};
export const EDU_RANK = { none: 0, hs: 1, as: 2, ba: 3, ma: 4, phd: 5 };

// County names for English mode (location strings from 104 start with the county).
const COUNTY = { "台北市": "Taipei", "新北市": "New Taipei", "基隆市": "Keelung", "宜蘭縣": "Yilan", "桃園市": "Taoyuan", "新竹市": "Hsinchu City",
  "新竹縣": "Hsinchu County", "苗栗縣": "Miaoli", "台中市": "Taichung", "彰化縣": "Changhua", "南投縣": "Nantou", "雲林縣": "Yunlin", "嘉義市": "Chiayi City",
  "嘉義縣": "Chiayi County", "台南市": "Tainan", "高雄市": "Kaohsiung", "屏東縣": "Pingtung", "台東縣": "Taitung", "花蓮縣": "Hualien", "澎湖縣": "Penghu",
  "金門縣": "Kinmen", "連江縣": "Lienchiang" };

export function makeT(lang) {
  const i = lang === "zh" ? 0 : 1;
  const t = (k, vars) => {
    let s = (T[k] || [k, k])[i];
    if (vars) for (const [a, b] of Object.entries(vars)) s = s.replace(`{${a}}`, b);
    return s;
  };
  t.lang = lang;
  t.pick = (pair) => (pair ? pair[i] : "");
  t.sep = lang === "zh" ? "、" : ", ";
  t.colon = lang === "zh" ? "：" : ": ";
  t.location = (s) => {
    if (!s || lang === "zh") return s || "";
    const k = Object.keys(COUNTY).find((c) => s.startsWith(c));
    return k ? COUNTY[k] : s;
  };
  t.salary = (s) => {
    if (!s || lang === "zh") return s || "";
    if (s.includes("面議")) return "Negotiable";
    const unit = s.startsWith("月薪") ? " / month" : s.startsWith("年薪") ? " / year" : s.startsWith("時薪") ? " / hour" : s.startsWith("日薪") ? " / day" : "";
    const nums = s.match(/[\d,]+/g) || [];
    if (!nums.length) return s;
    const range = nums.length > 1 ? `NT$${nums[0]}–${nums[1]}` : `NT$${nums[0]}${s.includes("以上") ? "+" : ""}`;
    return range + unit;
  };
  return t;
}
