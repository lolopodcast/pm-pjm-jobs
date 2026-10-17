# 產品需求文件 (PRD.md)
專案名稱：104 上市櫃 PM/PjM 新人職缺追蹤與雙語 KSA 自動分析系統 (PWA)

---

## 1. 專案目標與定位
本系統旨在每天定時自動爬取 104 人力銀行之特定新人職缺，經由 Google Gemini API 萃取並轉化為雙語職能需求（KSA），並以極簡靜態架構（GitHub Pages + PWA）呈現，提供求職者無負擔、高價值的最新與歷史職缺分析工具。

---

## 2. 業務邏輯與資料管線 (Pipeline)

### 步驟一：資料過濾與抓取
1. **上市櫃公司過濾：** 讀取台灣證券交易所 (TWSE) 與櫃買中心最新公開上市櫃公司名單，建立比對白名單。
2. **職缺爬取與模糊匹配：**
   * **職稱模糊匹配：** 職稱須同時包含 (PM, PjM, 產品, 專案, Project, Product) 中的任一項，且包含 (經理, 專員, 工程師, 助理, 管理師, Engineer, Specialist, Assistant) 中的任一項。
   * **年資限制：** 限定工作經驗要求在 `0-2 年`（含經驗不拘、1年以下、1-2年）。
   * **執行時間：** 台灣時間每日凌晨 **03:05** 執行（此時為 104 系統最低離峰期，且能確保早上 07:00 前更新上線）。
   * **頻率控制：** 點入個別職缺頁面時，強制設定 `time.sleep(3~5)` 秒，完全模擬真人行為。

### 步驟二：增量更新與雙語 KSA 萃取
1. **增量比對：** 讀取現有 `data.json`。若職缺 ID 已存在，保留原資料並跳過，嚴禁重複呼叫 AI API。
2. **雙語 KSA 萃取：** 若為新職缺，將 JD（工作內容）送交 `gemini-2.5-flash`。不論原始 JD 為中文或英文，Gemini 必須統一輸出「繁體中文（附帶英文專業術語）」的 K、S、A 陣列標籤。
3. **著作權合規（不存原文）：** 為避免整篇 JD 全文之著作權爭議，**JSON 檔案中嚴格禁止儲存原始工作內容全文**，僅保留結構化標籤與公司基本欄位。

### 步驟三：下架過濾與一個月自動歸檔
1. 當日爬蟲未抓取到之現存職缺，狀態一律改為 `status: "closed"` 並記錄當天為 `closed_date`。
2. 若職缺處於 `closed` 狀態**超過 30 天（1 個月）**，自動將其移出 `data.json`，並移入 `history_archive.json` 進行歷史歸檔，確保前端 PWA 載入不卡頓。

---

## 3. 異常處理與資安熔斷機制

1. **網頁改版防空跑警報（核心機制）：** 若爬蟲在 104 第一頁抓取到的總職缺筆數為 0，必須立刻觸發異常並強行中斷（`sys.exit(1)`），迫使 GitHub Actions 觸發失敗，以便系統自動向開發者發送改版 Email 警報。
2. **API 熔斷保護：** 單次排程中，若新職缺呼叫 Gemini API 的數量 **> 80 筆**（可能為爬蟲失控或大量異常資料），程式須立刻強制中編號斷，防範 API 額度爆增與 104 側風控。
3. **網路容錯重試（Retry）：** 網路請求與 API 呼叫遭遇瞬間異常時，須實施指數退避重試（最多重試 3 次，間隔分別為 2s, 4s, 8s）。
4. **金鑰資安：** `GEMINI_API_KEY` 嚴禁以明文硬編碼形式寫在程式碼中，必須由 **GitHub Secrets** 加密注入環境變數。
5. **手動補爬機制：** 工作流設定必須開啟 `workflow_dispatch`，容許自動執行因不可抗力失敗時，能透過 GitHub 網頁一鍵手動補爬更新。

---

## 4. 自動備份機制 (Backup Strategy)
* **自動版控備份：** GitHub Actions 在每次成功寫入並覆蓋 `data.json` 之前，須自動將前一日舊版檔案複製備份至專案的 `backup/` 目錄下，並以 `data_backup_YYYYMMDD.json` 命名。
* **歷史留存：** 備份目錄僅保留最近 30 天的備份檔，超過 30 天者由腳本自動刪除。

---

## 5. 測試與驗證段落 (Testing & Verification)
腳本必須內建一個**獨立測試模式 (`--test`)**，供本機及 CI 環境驗證以下三個核心測項：

* **驗證測項 1：爬蟲與模糊匹配測試 (`--test-crawl`)**
  * 驗證程式能否成功對接 TWSE 資料、成功抓取 104 前 5 筆職缺，且能正確識別如「專案工程師」或「Product Specialist」等複合型職稱。
* **驗證測項 2：Gemini 雙語格式測試 (`--test-llm`)**
  * 餵入一段全英文假 JD。驗證 Gemini 能否精準回傳標準 JSON，格式完美符合 K、S、A 分類，且文字呈現雙語形式（例如：需求管理 (Requirement Management)），不含任何 markdown 外包裝或雜質文字。
* **驗證測項 3：狀態流轉與歸檔測試 (`--test-archive`)**
  * 建立一組包含舊 ID 且下架超過 31 天的假資料庫，跑一次對比流程，驗證消失的 ID 是否順利轉為 `closed`，且過期資料是否精準移入 `history_archive.json`。

---

## 6. 資料結構定義 (`data.json` 範例)
```json
[
  {
    "job_id": "104_abc123",
    "industry": "電子零組件業",
    "company": "台灣積體電路製造股份有限公司",
    "department": "先進製程專案處",
    "title": "專案工程師 (Project Engineer)",
    "status": "open", 
    "published_date": "2026-10-16",
    "closed_date": null,
    "ksa": {
      "knowledge": ["半導體製程基礎 (Semiconductor Principles)", "專案管理實務理論 (Project Management Theory)"],
      "skills": ["MS Project 操作", "英文多益 750 分以上", "跨部門會議主持 (Cross-functional Facilitation)"],
      "attributes": ["高抗壓性 (Stress Tolerance)", "嚴謹細心 (Meticulousness)"]
    }
  }
]
```
