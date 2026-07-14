# Industry Overview Output Contract

Use this file before writing a standard or deep industry overview report. This is a lightweight output contract for broad industry research. It must not override the company/product output contract or the specific-question output contract.

## Contract Trigger

Apply this contract when the user asks for an industry overview, market overview, sector research, track research, opportunity-space research, or a general industry report without targeting a specific company/product and without asking a specific cause/trend question.

If the user asks a specific industry question, use `references/specific-question-output-contract.md`. If the user targets a company/product or listed-company capital-market issue, use `references/company-product-output-contract.md`.

## Opening Rule

Industry overview reports may start with a report title:

```md
# {行业名称}行业研究报告
```

Do not force `## 0. 研报前置区` for pure industry overview reports. That opening belongs to standard or deep company/product reports.

## Required Heading Scan

Before final output, scan for these applicable headings:

```md
## 1. 行业一句话定义
## 2. 研究边界
### 2.1 研究计划摘要
### 2.2 来源矩阵和证据质量
### 2.3 二次检索缺口
## 3. 行业地图
## 4. 生命周期判断
## 5. 七个核心模块
## 6. 趋势推演
## 7. 风险和机会
## 8. 事实, 观点和推断分层
## 9. 多视角压力测试
## 10. 后续研究建议
## 11. 报告合规自检表
```

If any required heading is missing, restore it before final output.

## Evidence Discipline

Industry overview reports must not present a market narrative as if it were verified fact. Include:

- A source matrix with evidence tier and retrieval status.
- A three-round retrieval closure table that shows attempted sources by round, current status, unresolved reason, and next source.
- A fact/opinion/inference table with source type, evidence tier, source status, and confidence.

Use `待核验事实` when market size, growth, penetration, export, price, or profitability claims rely on media summaries, broker reports, consulting reports, or republished data.

Section `2.3 二次检索缺口` must contain residual high-impact gaps after up to three targeted closure rounds, not merely first-pass missing items. Keep a gap as unresolved only when the active environment cannot access the source, the source requires a paid database or login, public search returns no reliable result, or the available evidence has a mismatched period, geography, or definition.

## Seven-Module Rule

All seven modules must appear as independent subsections or clearly separated blocks. Tables may summarize the seven modules, but they cannot replace the module analysis.

For standard industry overview reports:

- Each seven-module subsection should reach roughly 250-450 Chinese characters.
- Each subsection must include a clear conclusion, evidence or evidence gap, mechanism, and industry implication.
- If evidence is insufficient, name the missing source and next verification step.

For deep industry overview reports:

- Each seven-module subsection should reach roughly 500-800 Chinese characters.
- Trend projection should include base, upside, and downside paths.
- Lifecycle judgment should include evidence, counter-evidence, and confidence.

Do not treat a single seven-module summary table as the body. If the module only contains a label or one sentence, rewrite it before final output.

## Rewrite Triggers

Rewrite before final output if the draft:

- Uses company/product `## 0. 研报前置区` for a pure industry overview.
- Omits research plan, source matrix, or three-round retrieval closure results.
- Omits industry map or lifecycle judgment.
- Collapses the seven modules into one paragraph.
- Writes seven modules as thin labels without conclusion, evidence, mechanism, and industry implication.
- Claims fact/opinion/inference separation in the checklist without an actual fact/opinion/inference section.
- Omits pressure test or final compliance checklist.
