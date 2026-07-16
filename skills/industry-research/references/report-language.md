# Report Language Contract

Use this file for every output mode, including formal reports, short answers, visible briefs, and Prompt Builder output. It is the single source of truth for output-language selection and translated report headings.

## Contents

- [Language Selection](#language-selection)
- [Translation Scope](#translation-scope)
- [Canonical Contract Fields](#canonical-contract-fields)
- [Template Use](#template-use)
- [Depth and Validation](#depth-and-validation)

## Language Selection

Only Chinese and English are supported. Apply this precedence:

1. If the user explicitly requests Chinese or English, use that language.
2. If the user explicitly requests another language, briefly state that only Chinese and English are supported, then use English.
3. Otherwise, use Chinese when Chinese is the dominant language of the user's current request; use English when English or any other language is dominant.
4. If the current request is genuinely balanced or language-neutral, use the most recent Chinese or English dominant language in the conversation.
5. If no supported language signal exists, use English.

Do not infer the report language from source documents, company names, quoted text, code, or the language of this Skill. Record the selected `output_language` in the internal research brief before choosing or translating the report skeleton.

## Translation Scope

Translate all reader-facing material into the selected language:

- report title and Markdown headings;
- prose, summaries, conclusions, labels, table headers, captions, notes, and compliance checklist;
- visible research brief or reusable prompt when the user requests one;
- filenames when a natural-language topic is used, unless the user provides an exact filename.

Keep these elements in their original or canonical form:

- `claim_id`, `source_id`, Schema fields, enums, paths, commands, code, URLs, and citation identifiers;
- official organization, product, dataset, standard, paper, and legal-document names when translation would reduce precision;
- short source quotations when exact wording matters. Explain them in the report language when necessary.

Do not mix Chinese and English contract headings in one report. Proper names and technical identifiers do not count as language mixing.

## Canonical Contract Fields

Copy contract-bearing table headers, row labels, bold labels, and retrieval-round markers exactly. Do not paraphrase them, change capitalization, remove hyphens, or replace `Target Company/Product` with a company or product name. Markdown table-cell whitespace is not significant. Put target names and report-specific content in table cells or prose.

### Common research trace

Industry overview and industry-specific source matrix:

```text
来源类型 | 本报告用途 | 证据层级 | 检索状态 | 限制
Source Type | Use in This Report | Evidence Tier | Retrieval Status | Limitations
```

Company and product source matrix:

```text
来源类型 | 本报告用途 | 证据等级 | 一手来源状态 | 缺口处理
Source Type | Use in This Report | Evidence Tier | Primary-Source Status | Gap Handling
```

All follow-up retrieval gap tables:

```text
缺口 | 三轮闭环已尝试 | 当前状态 | 为什么仍重要 | 未补齐原因 | 下一步来源
Gap | Three-Round Closure Attempts | Current Status | Why It Still Matters | Unresolved Reason | Next Source
```

Use `第1轮`, `第2轮`, and `第3轮` in Chinese. Use `Round 1`, `Round 2`, and `Round 3` in English. Do not abbreviate them as `R1`, `R2`, or `R3`.

### Industry overview fields

Fact, opinion, and inference table:

```text
类型 | 内容 | 来源/依据 | 证据层级 | 来源状态 | 置信度
Type | Content | Source/Basis | Evidence Tier | Source Status | Confidence
```

Use these exact lifecycle labels: `阶段结论` / `Lifecycle Phase`, `证据` / `Evidence`, `反证` / `Counterevidence`, `置信度` / `Confidence`, and `行业含义` / `Industry Implication`.

Use these exact seven-module labels: `结论` / `Conclusion`, `证据` / `Evidence`, `机制` / `Mechanism`, and `行业含义` / `Industry Implication`.

### Industry-specific question fields

Evidence chain table:

```text
子问题 | 结论 | 事实 | 观点 | 推断 | 证据层级 | 来源状态 | 置信度
Sub-question | Conclusion | Fact | Opinion | Inference | Evidence Tier | Source Status | Confidence
```

Use these exact lifecycle labels: `阶段结论` / `Lifecycle Phase`, `证据` / `Evidence`, `反证` / `Counterevidence`, `置信度` / `Confidence`, and `对该问题的含义` / `Implication for the Question`.

Use these exact seven-module labels: `结论` / `Conclusion`, `证据` / `Evidence`, `机制` / `Mechanism`, and `对该问题的含义` / `Implication for the Question`.

### Company and product fields

Core metrics table:

```text
指标 | 行业读数 | 目标公司/产品读数 | 判断 | 证据/来源
Metric | Industry Reading | Target Company/Product Reading | Judgment | Evidence/Source
```

Use these exact first-column metric labels: `市场规模` / `Market Size`, `增速/渗透率` / `Growth Rate/Penetration Rate`, `竞争强度` / `Competitive Intensity`, `盈利水平` / `Profitability Level`, `景气度` / `Prosperity`, and `关键风险` / `Key Risk`.

Multi-business table:

```text
业务线/行业线 | 行业阶段 | 竞争格局 | 关键指标/景气信号 | 对目标公司的含义
Business Line/Industry Line | Industry Stage | Competitive Landscape | Key Metrics/Prosperity Signal | Implication for the Target Company
```

Fact, opinion, and inference table:

```text
类型 | 内容 | 来源/依据 | 证据层级 | 一手来源状态 | 置信度
Type | Content | Source/Basis | Evidence Tier | Primary-Source Status | Confidence
```

Use these exact lifecycle labels: `阶段结论` / `Lifecycle Phase`, `证据` / `Evidence`, `反证` / `Counterevidence`, `置信度` / `Confidence`, and `对目标公司/产品的影响` / `Implication for Target Company/Product`.

Use these exact seven-module labels: `结论` / `Conclusion`, `依据` / `Basis`, `机制` / `Mechanism`, `对目标公司/产品的影响` / `Implication for Target Company/Product`, and `关键指标和后续验证` / `Key Metrics and Follow-up Verification`.

### Common supporting tables

Use `视角 | 质疑 | 影响 | 需要验证` / `Perspective | Challenge | Impact | Verification Needed` for industry overview and industry-specific pressure tests. Use `视角 | 质疑 | 为什么重要 | 需要验证` / `Perspective | Challenge | Why It Matters | Verification Needed` for company and product pressure tests.

Use `检查项 | 是否通过 | 说明` / `Check | Passed | Explanation` for report compliance tables. Company and product verification appendices use `待验证问题 | 为什么重要 | 推荐来源 | 优先级` / `Verification Item | Why It Matters | Recommended Source | Priority`.

## Report Shell Contract

Every standard or deep industry overview, industry-specific question, and company or product report must use exactly one dynamic H1 title as its first nonempty line. Do not leave template placeholders in the title. The next nonempty line must be the route opening: section `1` for industry overview and industry-specific reports, or section `0` for company and product reports. Short answers, Prompt Builder outputs, and visible research briefs do not use this shell contract.

End every standard or deep report with exactly one of these language-matched disclaimer lines. Copy it exactly and keep it as the final nonempty line.

- Chinese: `本报告仅供研究和信息参考, 不构成投资建议, 也不构成任何收益承诺.`
- English: `This report is for research and informational purposes only. It does not constitute investment advice or any guarantee of returns.`

## Template Use

The assets in `assets/` define the canonical structure and content obligations. Preserve their H1 position, numbering, order, conditional sections, tables, disclaimer, and analytical requirements. When the selected language is English, translate reader-facing placeholders and use the exact English headings, contract fields, and disclaimer in this file. When the selected language is Chinese, use the existing Chinese headings, exact contract fields, and disclaimer in the assets and output contracts.

Do not translate the report skeleton into a third language. `output_language` must be `zh` or `en`.

### Industry overview English headings

```md
## 1. One-Sentence Industry Definition
## 2. Research Scope
### 2.1 Research Plan Summary
### 2.2 Source Matrix and Evidence Quality
### 2.3 Follow-up Retrieval Gaps
## 3. Industry Map
## 4. Lifecycle Assessment
## 5. Seven Core Modules
### 5.1 Feasibility
### 5.2 Scalability
### 5.3 Defensibility
### 5.4 Profitability
### 5.5 Valuation
### 5.6 External Factors
### 5.7 Prosperity
## 6. Trend Outlook
## 7. Risks and Opportunities
## 8. Fact, Opinion, and Inference Layers
## 9. Multi-Perspective Pressure Test
## 10. Follow-up Research Recommendations
## 11. Report Compliance Checklist
```

### Industry-specific question English headings

```md
## 1. Direct Answer
## 2. Conclusion Summary
## 3. Research Scope
### 3.1 Research Plan Summary
### 3.2 Source Matrix and Evidence Quality
### 3.3 Follow-up Retrieval Gaps
## 4. Industry Map
## 5. Problem Decomposition and Issue Tree
## 6. Evidence Chain Analysis
## 7. Lifecycle Assessment
## 8. Seven Core Modules Analysis
### 8.1 Feasibility
### 8.2 Scalability
### 8.3 Defensibility
### 8.4 Profitability
### 8.5 Valuation
### 8.6 External Factors
### 8.7 Prosperity
## 9. Multi-Perspective Pressure Test
## 10. Risks and Uncertainties
## 11. Follow-up Verification Checklist
## 12. Report Compliance Checklist
```

### Company and product English headings

```md
## 0. Research Front Matter
### 0.1 Executive Summary
### 0.2 Key Conclusions
### 0.3 Core Metrics Overview
### 0.4 Exhibit List or Placeholders
## 1. Direct Conclusion
## 2. Research Scope
### 2.1 Research Plan Summary
### 2.2 Source Matrix and Evidence Quality
### 2.3 Follow-up Retrieval Gaps
## 3. Macro Environment Analysis
## 4. Meso Industry Analysis
### 4.0 Multi-Business Meso Breakdown
### 4.1 One-Sentence Industry Definition
### 4.2 Key Industry Metrics
### 4.3 Industry Map and Target Position
### 4.4 Lifecycle Assessment
## 5. Weighted Analysis of Seven Core Modules
### 5.1 Feasibility
### 5.2 Scalability
### 5.3 Defensibility
### 5.4 Profitability
### 5.5 Valuation
### 5.6 External Factors
### 5.7 Prosperity
## 6. Micro Company/Product Analysis
## 7. SWOT
## 8. Business/Product Portfolio Analysis
## 9. Competitor Comparison
## 10. Fact, Opinion, and Inference Layers
## 11. Capital-Market Performance and Valuation Expectation Changes
### 11.1 Share-Price Performance Breakdown
### 11.2 Fundamental Changes
### 11.3 Valuation Logic and Market Expectation Gap
### 11.4 Upside Catalysts, Downside Risks, and Scenario Analysis
## 12. Multi-Perspective Pressure Test
## 13. Risks and Opportunities
## 14. Recommended Next Actions
## 15. Methodology and Data Sources
## 16. Appendix: Follow-up Verification Checklist
## 17. Report Compliance Checklist
```

Use `4.0` and section `11` only when their existing route conditions apply. Every English formal report begins with one natural English H1 title. English company and product reports then use `## 0. Research Front Matter`; English specific-question reports then use `## 1. Direct Answer`; English overview reports then use `## 1. One-Sentence Industry Definition`.

## Depth and Validation

Character targets in existing references express analytical depth, not a requirement to write Chinese. For deterministic maintenance checks, Chinese uses CJK characters and English uses half of non-whitespace Latin content as a normalized approximation. Do not pad either language to satisfy a count.

Validate reports with:

```text
python -B scripts/report_contract_check.py <report.md> --profile <profile> --language auto
```

The checker accepts `auto`, `zh`, or `en`. It validates exact contract fields before language normalization, reports targeted field errors without downstream duplicates, rejects mixed contract headings, and then applies the same structure, evidence, depth, and compliance rules. Third-language report output is outside the supported contract.
