# data 分支

本分支只由 GitHub Actions 每日排程寫入（PRD 11.3），請勿手動修改。

- `data.json`：開放中與近 30 天內關閉的職缺
- `history_archive_YYYY.json`：關閉超過 30 天的職缺（依關閉年份）
- `backup/`：最近 30 天的每日備份
- `unmatched_companies.json`：職稱符合但公司未比對成功的名單（供審核子公司對照表）
- `run_summary.json`：最近一次執行的統計
