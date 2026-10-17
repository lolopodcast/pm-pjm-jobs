# 詞彙表審核（草稿 1.0-draft，2026-10-17）

來源：從 data.json 隨機抽 50 筆職缺，以 `gemini-3.1-flash-lite` 開放式分析，共 506 個原始標籤，歸類為以下標準詞彙（PRD 2.2 第 6 點）。
審核通過後版本改為 `1.0`，之後每筆職缺的標籤會對應到這些詞彙（`ksa_normalized`、`tasks_normalized`），統計圖表與配適度都以此計算。

**請在「調整意見」欄填寫**，或直接告訴我編號，例如「12 和 13 合併」「刪除 35」「27 改名為……」「新增……」。

構面欄是「我的構面輪廓」雷達圖的歸屬依據；「—」代表不歸入七大構面，例如外語、個人特質。

## 知識 Knowledge（20 項）

| # | 中文 | English | 構面 | 樣本中的原始標籤（節錄） | 調整意見 |
|---|---|---|---|---|---|
| 1 | 專案管理方法論 | Project management methodology | D7 創新管理 | 專案管理知識、專案管理方法論、專案管理架構 | |
| 2 | 敏捷開發方法 | Agile methods | D3 創新流程 | 敏捷式專案管理、敏捷開發方法 | |
| 3 | 產品開發流程 | Product development process | D3 創新流程 | 產品開發流程、電子產業開發流程、研發與製造基礎知識 | |
| 4 | 產品管理 | Product management | D2 產品線組合 | 軟體產品管理、產品定位與規格制訂 | |
| 5 | 行銷管理 | Marketing management | D5 市場研究 | STP 行銷理論、行銷規劃與廣告營運、金融商品行銷、數位廣告平台知識 | |
| 6 | 市場與競爭分析 | Market and competitive analysis | D5 市場研究 | 市場分析、市場與競爭分析 | |
| 7 | 財務與商業分析 | Finance and business analysis | D1 策略 | 商業運作與損益控管、財務數據理解、投資案件相關知識 | |
| 8 | 國際貿易與進出口 | International trade | — | 國際貿易基本概念、進出口業務 | |
| 9 | 製造與生產管理 | Manufacturing and production | D3 創新流程 | 工廠流程、工廠運作流程、生產管理知識、製造相關知識 | |
| 10 | 品質管理 | Quality management | D3 創新流程 | （樣本未出現，預留） | |
| 11 | 電子與電機產業 | Electronics industry | D4 設計開發工具 | 電子產業知識、電子製造業知識、ODM 產業知識、連接器與線纜知識 | |
| 12 | 半導體 | Semiconductors | D4 設計開發工具 | 半導體設備知識、半導體氣體配管 | |
| 13 | 機械與機構設計 | Mechanical engineering and design | D4 設計開發工具 | 機械工程知識、機構設計與分析 | |
| 14 | 資訊系統與軟體開發 | IT systems and software development | D4 設計開發工具 | 資訊相關知識、系統分析與設計、技術架構概念、ERP系統操作 | |
| 15 | 雲端與資訊安全 | Cloud and cybersecurity | D4 設計開發工具 | 雲端架構知識、雲端虛擬化技術、網路安全與通訊 | |
| 16 | 人工智慧技術與治理 | AI technology and governance | D4 設計開發工具 | AI技術知識、AI技術與應用場景、AI治理與風險管理 | |
| 17 | 金融科技與支付 | Fintech and payments | D4 設計開發工具 | 金融科技與支付知識、金融科技與數位金融、金流處理流程、支付應用整合 | |
| 18 | 生醫與製藥 | Biomedical and pharmaceutical | D4 設計開發工具 | ELISA技術、分子生物技術、蛋白質藥物知識、蛋白質體學技術 | |
| 19 | 法規與合規 | Regulations and compliance | D7 創新管理 | 醫材法規、政府標案履約、公共政策 | |
| 20 | 其他產業知識 | Other industry knowledge | — | 健康產業知識、產業應用知識、手機遊戲運營 | |

## 技能 Skills（32 項）

| # | 中文 | English | 構面 | 樣本中的原始標籤（節錄） | 調整意見 |
|---|---|---|---|---|---|
| 21 | 英文能力 | English | — | 英文溝通能力、英文精通、英文聽說讀寫、英文聽說讀寫精通 | |
| 22 | 日文能力 | Japanese | — | 日文溝通能力 | |
| 23 | 其他外語能力 | Other foreign languages | — | 西班牙文、西班牙文溝通能力 | |
| 24 | 口譯與翻譯 | Interpretation and translation | — | 中英口譯與翻譯 | |
| 25 | 辦公室軟體 | Office software | D4 設計開發工具 | 辦公室軟體、辦公室軟體應用、辦公軟體應用、Microsoft Office | |
| 26 | 專案管理工具 | Project management tools | D4 設計開發工具 | 專案管理工具、專案管理工具使用 | |
| 27 | 企業資源規劃系統（ERP／SAP） | ERP / SAP | D4 設計開發工具 | ERP系統操作、SAP系統操作、SAP與SFC系統、鼎基ERP | |
| 28 | 設計與原型工具 | Design and prototyping tools | D4 設計開發工具 | Figma 工具使用、原型製作工具、CAD繪圖軟體、繪圖軟體操作 | |
| 29 | 資料分析 | Data analysis | D5 市場研究 | 資料分析、數據分析工具、統計軟體操作、使用者行為分析 | |
| 30 | AI 工具應用 | AI tools | D4 設計開發工具 | AI 工具應用、生成式AI工具 | |
| 31 | 專案管理 | Project management | D7 創新管理 | 專案管理、專案管理技能、專案管理專業、專案管理能力 | |
| 32 | 時程與進度控管 | Schedule and progress control | D7 創新管理 | 專案時程控管、專案時程與資源管理、專案時程與進度控管、專案時間進度控管 | |
| 33 | 專案規劃與範疇管理 | Project planning and scope | D7 創新管理 | 專案規劃與執行、專案規劃與範圍管理 | |
| 34 | 成本與預算控管 | Cost and budget control | D7 創新管理 | 成本控制 | |
| 35 | 報價作業 | Quotation (RFQ) | D7 創新管理 | 報價作業 | |
| 36 | 供應商管理 | Supplier management | D7 創新管理 | 供應商管理 | |
| 37 | 工程變更管理 | Engineering change management | D3 創新流程 | 工程變更管理 | |
| 38 | 需求與規格文件撰寫 | Requirements and specification writing | D3 創新流程 | 需求文件撰寫、產品需求文件撰寫、產品規格撰寫、產品企劃撰寫 | |
| 39 | 測試規劃與驗證 | Test planning and validation | D3 創新流程 | 測試個案撰寫 | |
| 40 | 產品規劃 | Product planning | D2 產品線組合 | 產品規劃設計、數位產品規劃、產品管理、移動應用程式管理 | |
| 41 | 市場調查與分析 | Market research | D5 市場研究 | 市場調查分析、市場資料分析、市場趨勢分析、市場需求分析 | |
| 42 | 行銷企劃與推廣 | Marketing planning and promotion | D5 市場研究 | 數位行銷、行銷推廣、產品行銷規劃 | |
| 43 | 財務與營業分析 | Financial and business analysis | D1 策略 | 財務與營業分析 | |
| 44 | 文件與報表處理 | Documentation and reporting | — | 報表彙整與管理、文件處理能力、文書處理與排版、工程文件編撰 | |
| 45 | 簡報與提案 | Presentation and proposals | D6 團隊與領導 | 簡報製作、專案簡報製作、簡報與提案、簡報製作與溝通 | |
| 46 | 溝通協調 | Communication and coordination | D6 團隊與領導 | 溝通協調、跨部門溝通協調、會議協調與時程控管、會議規劃與紀錄 | |
| 47 | 談判協商 | Negotiation | D6 團隊與領導 | 英語溝通協商 | |
| 48 | 邏輯分析與問題拆解 | Analytical thinking | — | 邏輯分析、邏輯分析與問題拆解 | |
| 49 | 教育訓練 | Training delivery | D6 團隊與領導 | 教育訓練 | |
| 50 | 系統開發與維運 | System development and operations | D4 設計開發工具 | 系統開發、雲端平台管理、產品安裝與設定 | |
| 51 | 行政事務處理 | Administration | — | 行政事務處理 | |
| 52 | 影音製作 | Video production | — | 影片剪輯分鏡規劃 | |

## 特質 Attributes（20 項）

| # | 中文 | English | 構面 | 樣本中的原始標籤（節錄） | 調整意見 |
|---|---|---|---|---|---|
| 53 | 主動積極 | Proactive | — | 主動積極、積極主動、積極主動與溝通協調、積極細心抗壓 | |
| 54 | 抗壓性 | Stress tolerance | — | 抗壓性、抗壓性強、高抗壓性、抗壓性與韌性 | |
| 55 | 細心 | Attention to detail | — | 細心度、細心負責、熱情與細心、細心且重視數據結果 | |
| 56 | 責任感 | Responsibility | — | 責任心、責任感、工作熱忱與責任心 | |
| 57 | 當責 | Ownership | — | 產品責任感、積極主動與當責 | |
| 58 | 溝通能力 | Communication | D6 團隊與領導 | 溝通協調能力、溝通能力、良好溝通能力、擅長溝通 | |
| 59 | 團隊合作 | Teamwork | D6 團隊與領導 | 團隊合作、團隊合作精神、具備團隊合作精神、重視團隊合作 | |
| 60 | 領導力 | Leadership | D6 團隊與領導 | 領導力 | |
| 61 | 跨文化溝通 | Cross-cultural communication | D6 團隊與領導 | 跨文化溝通、跨文化溝通能力 | |
| 62 | 學習意願 | Willingness to learn | — | 具學習意願、學習意願與抗壓性、持續學習熱忱、好奇心與解決問題 | |
| 63 | 應變能力 | Adaptability | — | 應變能力 | |
| 64 | 問題分析與解決 | Problem solving | — | 問題分析能力、問題解決能力 | |
| 65 | 邏輯思考 | Logical thinking | — | 邏輯思考能力、邏輯清晰、邏輯與溝通能力、邏輯與組織能力 | |
| 66 | 時間管理 | Time management | D7 創新管理 | 時間管理能力、細心與時間管理 | |
| 67 | 自我管理 | Self-management | — | 自我管理能力 | |
| 68 | 熱忱 | Passion | — | 熱忱 | |
| 69 | 企圖心 | Ambition | — | 企圖心與挑戰精神 | |
| 70 | 服務熱誠 | Service orientation | — | 服務熱誠 | |
| 71 | 商業與產業敏銳度 | Business acumen | D1 策略 | 對數位金融具敏銳度 | |
| 72 | 出差或外派意願 | Willingness to travel or relocate | — | 外派意願、配合移動 | |

## 工作職責 Tasks（36 項）

| # | 中文 | English | 構面 | 樣本中的原始標籤（節錄） | 調整意見 |
|---|---|---|---|---|---|
| 73 | 產品策略與路線圖 | Product strategy and roadmap | D1 策略 | 定義產品願景與路線圖、擬訂產品發展策略與企劃、競品分析與策略制定、產品方向討論 | |
| 74 | 產品規劃與功能定義 | Product planning and feature definition | D2 產品線組合 | 產品功能規劃落地、商品規劃與執行、數據產品需求規劃、數據產品企劃提案 | |
| 75 | 產品生命週期管理 | Product lifecycle management | D2 產品線組合 | 產品生命週期管理、主導產品生命週期、上市後管理、產品版本與文件管理 | |
| 76 | 產品營運與成效分析 | Product operations and performance analysis | D2 產品線組合 | 分析運營成效並提出改進需求、制定運營計畫以提升使用者指標與收入、產品開發成效分析、金流產品規劃與維運 | |
| 77 | 市場與競品分析 | Market and competitor analysis | D5 市場研究 | 執行市場與競品分析、市場與競品分析、市場趨勢調查與研發建議、市場需求與競爭分析 | |
| 78 | 需求訪談與分析 | Requirement gathering and analysis | D5 市場研究 | 專案需求訪談與規劃、需求分析與文件撰寫、客戶需求管理、客戶需求變更處理 | |
| 79 | 規格定義 | Specification definition | D3 創新流程 | 規格定義與開發協作、與客戶及研發確認產品規格、產品規格與工程溝通、系統資料串接規格開立 | |
| 80 | 上市與行銷規劃 | Launch and marketing planning | D5 市場研究 | 上市規劃與經營、行銷推廣與上市規劃、產品開發與上市 | |
| 81 | 行銷推廣 | Marketing and promotion | D5 市場研究 | 行銷策略與宣傳規劃、執行行銷策略研究與推廣規劃、國際品牌推廣、數位健康產品活動規劃 | |
| 82 | 使用者與客戶體驗改善 | User and customer experience improvement | D4 設計開發工具 | 使用者體驗優化、客戶體驗優化、原型製作與客戶對焦 | |
| 83 | 敏捷開發與待辦事項管理 | Agile delivery and backlog management | D3 創新流程 | 執行敏捷專案管理、管理產品待辦事項與優先級 | |
| 84 | 專案規劃與資源分配 | Project planning and resourcing | D7 創新管理 | 制定專案計畫與資源分配、專案規劃、專案規劃與範疇定義、獨立進行專案規劃 | |
| 85 | 時程與進度控管 | Schedule and progress control | D7 創新管理 | 專案進度管控、專案執行時程追蹤管制、專案進度與里程碑追蹤、NPI階段里程碑追蹤 | |
| 86 | 跨部門溝通協調 | Cross-functional coordination | D6 團隊與領導 | 跨部門溝通協調、跨部門資源協調、跨部門協調與資源整合、跨部門專案推動 | |
| 87 | 客戶溝通與關係維護 | Customer communication and relationship | D6 團隊與領導 | 客戶溝通應對、客戶溝通與會議管理、主持客戶會議、管理關鍵客戶專案並維護客戶關係 | |
| 88 | 進度報告與簡報 | Progress reporting and presentations | D7 創新管理 | 專案進度定期彙整與報告、報表製作與簡報、製作會議相關資料、風險管理與成果簡報 | |
| 89 | 風險與異常管理 | Risk and issue management | D7 創新管理 | 專案風險管理與異常排除、專案問題追蹤處理、擔任專案問題升級窗口並推動緩解計畫、跨部門解決生產異常 | |
| 90 | 成本與預算控管 | Cost and budget control | D7 創新管理 | 成本預算管控、專案成本與風險控管、進行專案損益控管、協助年度預算編列 | |
| 91 | 報價與成本彙整 | Quotation (RFQ) and costing | D7 創新管理 | 報價與成本彙整、主導報價服務與內部成本收集、與研發團隊合作進行報價 | |
| 92 | 專案文件管理 | Project documentation | D7 創新管理 | 專案文件撰寫、專案文件管理、協助專案文件建立、產品文件製作 | |
| 93 | 新產品導入與試產 | New product introduction and pilot runs | D3 創新流程 | 新產品導入與驗證、規劃新產品導入時程、NPI專案場域主導、試產安排與量產維護 | |
| 94 | 量產與交付管理 | Mass production and delivery | D3 創新流程 | 新產品導入與量產管理、量產訂單排程與出貨管理、與工廠協調生產與交付、產品交付保障 | |
| 95 | 產能規劃與生產排程 | Capacity planning and production scheduling | D7 創新管理 | 產能規劃與生產排程、產能規劃與量產建置、產品量產規劃 | |
| 96 | 供應鏈與物料管理 | Supply chain and materials | D7 創新管理 | 供應鏈規劃、供應鏈與製造計劃管理、供應鏈物料準備狀態報告與風險提示、建立物料清單並追蹤除錯進度 | |
| 97 | 供應商與承包商管理 | Supplier and contractor management | D7 創新管理 | 供應商管理、承包商管理 | |
| 98 | 工程變更管理 | Engineering change management | D3 創新流程 | 執行工程變更需求、管理工程變更流程 | |
| 99 | 測試與驗證 | Testing and validation | D3 創新流程 | 與測試團隊制定測試計畫、客製化整合測試、產品測試與個案撰寫、執行結構分析與測試 | |
| 100 | 工程文件與圖面 | Engineering documents and drawings | D4 設計開發工具 | 編撰工程技術文件、繪製工程圖面、管理生產技術文件 | |
| 101 | 系統整合與串接 | System integration | D4 設計開發工具 | 外部系統串接窗口、系統維護與問題追蹤、規劃雲端平台功能與架構、執行移動應用程式開發管理 | |
| 102 | 技術移轉 | Technology transfer | D3 創新流程 | 跨國技轉主導 | |
| 103 | 數位轉型與 AI 專案 | Digital transformation and AI projects | D1 策略 | 規劃與推動數位轉型專案、推動AI與數據專案、發想AI產品與解決方案、數位平台創新 | |
| 104 | 治理、法規與補助案作業 | Governance, regulatory and grant work | D7 創新管理 | ESG與公司治理資料彙整、推動AI治理落地與日常管理、醫材法規送審、政府補助專案窗口 | |
| 105 | 投資評估與追蹤 | Investment evaluation and tracking | D1 策略 | 投資後追蹤與績效分析、協助投資交易流程 | |
| 106 | 教育訓練與產品介紹 | Training and product introduction | D6 團隊與領導 | 內部教育訓練、產品介紹與教育訓練、產品教育訓練、影音教材製作 | |
| 107 | 現場支援與安裝導入 | On-site support and installation | — | 現場營運支援、產品安裝與導入、臨床技術支援 | |
| 108 | 行政與交辦事項 | Administration and ad-hoc tasks | — | 主管交辦事項、執行主管交辦事項、行政作業協助、部門行政事務 | |
