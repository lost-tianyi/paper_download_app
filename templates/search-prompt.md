# 标准化文献检索提示词

把尖括号内容替换为你的综述需求后，粘贴给已安装 Skills 的编码助手。
（安装向导结束页会生成更短的「启动说明」；日常由 `$literature-review-workflow` 在对话里逐步引导。）

```text
$academic-search
You are a rigorous academic literature researcher. Search for and organise real publications on <research topic>.
Scope: years <start-end>; journals <unrestricted / specified list / ranking range>; document types <articles / reviews / conference papers>.
Keywords: <core terms>; synonyms and related terms: <terms>; exclusions: <terms>; target number: <number, without lowering standards to fill quotas>.
Include only studies meeting the requirements for <scenario, research object, method, and outcomes>, and state why each study is included.
Verify every publication using an official publisher page and at least one authoritative source such as DOI/Crossref, IEEE Xplore, PubMed, Scopus, or Web of Science.
Do not invent or infer titles, authors, years, journals, DOIs, methods, or findings; mark unverified information as "Not verified".
Prefer final journal versions, identify duplicate preprint/conference/journal versions, and record explicit exclusion reasons.
Output fields: <Reference, Topic, Journal, Scenario, Model/Method, Data, Objective, Metrics, Findings, Limitations, DOI/URL>.
Separate results into Core Literature, Background Literature, and Pending Verification, and report search strings, search date, sources, and verification statistics.
```

输出分组：

| 分组 | 含义 |
|------|------|
| Core Literature | 直接回答研究问题，且已充分核验，可进入主证据表 |
| Background Literature | 提供理论、定义、模型、方法或背景，但不直接回答主问题 |
| Pending Verification | 看起来相关，但出版信息、全文、版本或发现仍需核实 |

# 标准化下载提示词

先人工审阅 Excel：核对 DOI/官网元数据、去重、调整分类/子节，增加 `Approved = Yes/No`，再执行：

```text
$sciencedirect-live-session-fetcher
Please process the attached Excel file. Only process records marked Approved = Yes.
Download PDFs that I can lawfully access, organise them by the category or subsection recorded in the spreadsheet, and prepare or import the approved records into Zotero.
Do not bypass paywalls or access controls. Record any unavailable, failed, or unmatched items instead of substituting another paper.
```

机构订阅场景：先在浏览器自行登录，再告诉助手“我已登录”。不要把密码交给助手。

# 最终质检（下载与入库后）

对照「已批准 Excel / PDF 文件夹 / Zotero」：

- 每条 Approved 记录都有对应 PDF，或明确的不可用/失败说明
- Zotero 题名、作者、年份、期刊、DOI 与表格一致
- 重复条目已合并或删除；分类文件夹与表格一致
- 开始精读/综述前备份 Excel 与 Zotero

完整路径：`Search → Verify → Review → Approve → Download → Organise → Final check`
