# 上市櫃 PM／PjM 新人職缺觀測站

每天自動整理 104 人力銀行上，上市、上櫃、興櫃公司（含子公司）的 PM／PjM 新人職缺，以 AI 分析職能需求（KSA）與工作內容，並以 GitHub Pages + PWA 呈現。教學用途，非 104 官方網站。

## 文件
- 產品需求文件：[docs/PRD.md](docs/PRD.md)
- UI 示意稿（虛構示意資料）：[docs/mockup/ui-mockup.html](docs/mockup/ui-mockup.html)

## 本機開發
1. 建立虛擬環境：`python -m venv .venv`，啟用：`.venv\Scripts\Activate.ps1`
2. 安裝套件：`pip install -r requirements.txt`
3. 複製 `.env.example` 為 `.env`，填入**測試用** Gemini 金鑰（見 PRD 11.5）

## 連線測試
`python tools/probe_104.py`：檢查能否連上 104、TWSE、TPEx。GitHub 上可在 Actions 頁面手動執行 `probe-104`。
