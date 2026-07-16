# Company/Product Output Contract

Use this file before writing any standard or deep company/product report. This is an output contract, not a style suggestion.

Select `output_language` through `references/report-language.md`. The headings and structured fields below are the Chinese contract. For English output, copy the exact company and product headings, table headers, row labels, bold labels, and retrieval-round markers from the language contract while preserving the same numbering, order, conditional sections, and obligations. Do not paraphrase contract fields.

## Contract Trigger

Apply this contract when the request is a standard or deep company/product report, including listed-company stock price, valuation, expectation gap, market-cap repair, investability, or rise/fall potential questions.

When a request is both a specific question and a company/product or listed-company capital-market question, this contract overrides the generic specific-question direct-answer rule. Keep the report front matter and use the language-matched opening.

If the user explicitly asks for a short, brief, quick, simple, one-paragraph, one-sentence, or no-detail answer, use Explicit Short Answer Mode instead.

## Build Order

Before drafting the report:

1. Classify the request and selected layers.
2. Build the internal research brief from `references/research-brief-builder.md`, including report type, output language, source plan, conditional modules, and depth contract.
3. Read `assets/company-product-template.md`.
4. Copy only the required language-matched Markdown heading skeleton from the dynamic H1 title onward.
5. Add conditional headings for multi-business or capital-market questions.
6. Fill the skeleton with evidence, analysis, source quality notes, and retrieval-gap closure results.
7. Run the heading scan, section-level depth gate, and compliance gate.
8. If any required heading is missing or any required section is thin, stop using the current draft and rewrite from the template skeleton.

Do not begin from a self-created outline.

## Opening Heading Rule

The first nonempty line must be exactly one dynamic H1 title, followed immediately by the company front matter:

```md
# {公司/产品名称}{研究主题}研究报告

## 0. 研报前置区
```

For English output, use a natural English H1 title followed immediately by `## 0. Research Front Matter`.

Do not start a standard or deep company/product report with:

```md
## 1. 直接结论
```

If the draft starts with `## 1. 直接结论`, it is a compressed report failure. Rewrite it before final output.

The final report body must begin with one dynamic H1 title and then the language-matched company front matter heading. Do not output template metadata, output-contract notes, internal compliance notes, or prose between them.

End the report with the exact language-matched disclaimer from `references/report-language.md`. Do not paraphrase it or repeat it elsewhere as a substitute for the fixed final line.

## Required Heading Scan

Before final output, scan the draft for the exact heading strings in the selected language. The Chinese strings are below; the English strings are defined in `references/report-language.md`:

```md
## 0. 研报前置区
### 0.1 报告摘要
### 0.2 关键结论
### 0.3 核心指标总览
### 0.4 图表清单或图表占位
## 1. 直接结论
## 2. 研究边界
### 2.1 研究计划摘要
### 2.2 来源矩阵和证据质量
### 2.3 二次检索缺口
## 3. 宏观环境分析
## 4. 中观行业分析
### 4.3 行业地图和目标位置
### 4.4 生命周期判断
## 5. 七个核心模块加权分析
### 5.1 可行性
### 5.2 规模性
### 5.3 防守性
### 5.4 盈利性
### 5.5 估值
### 5.6 外部因素
### 5.7 景气度
## 6. 微观公司/产品分析
## 10. 事实, 观点和推断分层
## 12. 多视角压力测试
## 13. 风险和机会
## 15. 方法论和数据来源说明
## 16. 附录: 后续验证清单
## 17. 报告合规自检表
```

For multi-business companies, also include:

```md
### 4.0 多业务线中观拆分
```

For listed-company capital-market questions, include `### 4.0 多业务线中观拆分` by default. If the target is genuinely single-business, keep `4.0` and state why no material business-line split is needed.

For capital-market questions, also include:

```md
## 11. 资本市场表现与估值预期变化
### 11.1 股价表现拆解
### 11.2 基本面变化
### 11.3 估值逻辑和市场预期差
### 11.4 上涨触发器, 下跌风险和情景分析
```

If any applicable heading is absent, do not output the draft. Restore the missing heading and its body, then rerun the scan.

Sections `13` and `16` are not optional end matter. `13. 风险和机会` must contain both risks and opportunities, and must distinguish industry-structure drivers from target-company/product drivers. `16. 附录: 后续验证清单` must include concrete validation questions, why each matters, recommended sources, and priority.

Section `2.3 二次检索缺口` is a residual gap closure section, not a first-pass missing-data list. Before final output, high-impact gaps must have up to three targeted closure rounds. The section must show the gap, round-by-round attempted sources, current status, why it matters, unresolved reason, and next source. Do not keep a gap as `仍未补齐` unless the active environment cannot access the source, the source requires a paid database or login, public search has no reliable result, or the available evidence has a mismatched period, geography, or definition.

## Seven-Module Body Rule

The seven-module section may include a summary matrix, but the matrix is never the body.

Each module must be an independent subsection:

- `### 5.1 可行性`
- `### 5.2 规模性`
- `### 5.3 防守性`
- `### 5.4 盈利性`
- `### 5.5 估值`
- `### 5.6 外部因素`
- `### 5.7 景气度`

Each subsection must keep these four labels:

- `结论`
- `依据`
- `机制`
- `对目标公司/产品的影响`

For capital-market questions, `5.4 盈利性`, `5.5 估值`, `5.6 外部因素`, and `5.7 景气度` are priority modules and must be more detailed than the non-priority modules.

## Rewrite Triggers

Rewrite before final output if the draft:

- Starts at `## 1. 直接结论`.
- Uses "why it fell / can it rise / what to watch" as the main structure.
- Omits `0. 研报前置区`.
- Omits `2.1`, `2.2`, or `2.3`.
- Collapses `5.1-5.7` into one table or paragraph.
- Omits `11.1-11.4` for a capital-market question.
- Omits `12. 多视角压力测试`.
- Omits `17. 报告合规自检表`.
- Uses media summaries as core evidence when primary company filings, official data, or industry association data are available.

## Workspace File Discipline

For standard or deep company/product reports, use Workspace Report File by default when file writing is available. Create the full Markdown report under `reports/`, then answer in chat with the file path, short summary, and compliance/checker status.

If file writing is unavailable or the user explicitly asks not to create files, Chat Report is still a full report. Do not shorten or reorder the contract because the output is in chat.

Correct headings are not enough. Apply the section-level depth contract in `references/output-format.md` and rewrite thin sections before final output.
