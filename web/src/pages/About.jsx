import { PageHead } from "../components.jsx";
import { DOM_FULL, STG } from "../i18n.js";

const TEXT = {
  src: [
    ["職缺：104 人力銀行公開職缺，依職務類別（產品經理、產品管理師、產品企劃、專案經理、軟體專案管理師、其他專案管理師）查詢，僅含全職、年資 3 年以下；每日凌晨 03:05 更新。",
      "Jobs: public postings on 104 Job Bank, queried by job category (product and project management), full-time and up to 3 years of experience; refreshed daily at 03:05."],
    ["公司名單：臺灣證券交易所與證券櫃檯買賣中心公開資料（上市、上櫃、興櫃），子公司依人工審核的對照表比對。",
      "Companies: open data from TWSE and TPEx (listed, OTC, emerging), with subsidiaries matched through a manually reviewed list."],
    ["本站不保存職缺原文，只保存結構化標籤、AI 撰寫的摘要與 104 原始連結。", "We never store the original posting text, only structured tags, an AI-written summary and the link to 104."],
  ],
  ai: [
    ["以 Google Gemini（gemini-3.1-flash-lite）分析每份職缺，萃取知識、技能、特質（KSA）、工作職責、PM 七大構面、Stage-Gate 階段與職務情境，並對應到 108 項標準詞彙。",
      "Google Gemini (gemini-3.1-flash-lite) analyses each posting for knowledge, skills and attributes (KSA), tasks, the seven PM domains, Stage-Gate stages and work context, mapped to a 108-item vocabulary."],
    ["每個標籤都必須在職缺原文中找得到依據，找不到的會被捨棄；職缺內文中任何要求 AI 改變行為的文字都會被忽略。",
      "Every tag must be backed by text in the posting or it is dropped; any text in a posting that tries to instruct the AI is ignored."],
    ["可能違反《就業服務法》第 5 條的條件（性別、年齡、容貌等）不列入 KSA 與配適度，只做統計觀察。",
      "Conditions that may breach Article 5 of the Employment Service Act (gender, age, appearance and so on) are kept out of KSA and fit scores and only counted."],
    ["AI 可能出錯，請以 104 原始職缺為準；發現錯誤可在職缺卡片上回報。", "The AI can be wrong. Treat the 104 posting as authoritative and report errors from any job card."],
  ],
  disc: ["本站為教學用途，非 104 人力銀行官方網站。配適度僅供參考，不代表錄取機會。本站不使用 cookie，也不安裝任何流量統計或追蹤工具；「我的配適度」資料只存在你的瀏覽器。",
    "This is an educational project, not an official 104 Job Bank site. Fit scores are a guide only. The site uses no cookies and no analytics or tracking; your self-assessment stays in your browser."],
};

export default function About({ t }) {
  const p = (pair) => t.pick(pair);
  return (
    <section className="page">
      <PageHead page="about" t={t} />
      <div className="card prose"><h2 className="h2 mb-2">{t("ab_src")}</h2><ul>{TEXT.src.map((x) => <li key={x[1]}>{p(x)}</li>)}</ul></div>
      <div className="card prose"><h2 className="h2 mb-2">{t("ab_ai")}</h2><ul>{TEXT.ai.map((x) => <li key={x[1]}>{p(x)}</li>)}</ul></div>
      <div className="card prose">
        <h2 className="h2 mb-2">{t("ab_fw")}</h2>
        <p>{p(["工作內容依兩個架構分析：「PM 產品經理」的七大構面，以及「NPD Stage-Gate Model」新產品開發階段。",
          "Work content is mapped to two structures: the seven domains of product management and the NPD Stage-Gate Model."])}</p>
        <div className="grid2">
          <div className="tbl-wrap"><table className="tbl"><tbody>{Object.keys(DOM_FULL).map((k) => <tr key={k}><td>{k}</td><td>{p(DOM_FULL[k])}</td></tr>)}</tbody></table></div>
          <div className="tbl-wrap"><table className="tbl"><tbody>{Object.keys(STG).map((k) => <tr key={k}><td>{k}</td><td>{p(STG[k])}</td></tr>)}</tbody></table></div>
        </div>
      </div>
      <div className="card prose"><h2 className="h2 mb-2">{t("ab_disc")}</h2><p>{p(TEXT.disc)}</p></div>
    </section>
  );
}
