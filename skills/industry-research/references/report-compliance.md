# Report Compliance Gate

Use this file before producing any standard or deep report. For company/product analysis, this gate is mandatory.

## Industry Overview Report Gate

For standard or deep pure industry overview reports, apply `references/industry-overview-output-contract.md` before final output.

Verify:

- The report does not use company/product `## 0. 研报前置区` for a pure industry overview.
- The report includes `2.1 研究计划摘要`, `2.2 来源矩阵和证据质量`, and `2.3 二次检索缺口`.
- The industry map, lifecycle judgment, seven modules, trend projection, risk/opportunity, pressure test, and follow-up research suggestions are present.
- The seven modules are independent analytical subsections with conclusion, evidence or evidence gap, mechanism, and industry implication.
- Standard overview reports target 8000-12000 Chinese characters unless the user explicitly triggers Explicit Short Answer Mode.
- Standard overview seven-module subsections reach roughly 250-450 Chinese characters; deep overview subsections reach roughly 500-800 Chinese characters.
- The report includes a fact/opinion/inference section with evidence tier, source status, and confidence.
- The final `报告合规自检表` does not mark evidence separation as passed if the fact/opinion/inference section is missing.

If this gate fails, rewrite the missing sections before final output.

## Specific-Question Report Gate

For standard or deep pure industry-specific question reports, apply `references/specific-question-output-contract.md` before final output.

Verify:

- The report starts with `## 1. 直接回答`, not `## 0. 研报前置区`.
- The report includes `3.1 研究计划摘要`, `3.2 来源矩阵和证据质量`, and `3.3 二次检索缺口`.
- The evidence chain includes facts, opinions, inferences, evidence tier, source status, and confidence.
- The direct answer is substantive and includes evidence and mechanism, not only a quick take.
- The seven modules are independent analytical blocks with conclusion, evidence or evidence gap, mechanism, and implication for the question.
- Standard specific-question reports target 8000-12000 Chinese characters unless the user explicitly triggers Explicit Short Answer Mode.
- Standard specific-question seven-module blocks reach roughly 200-400 Chinese characters; deep reports reach roughly 400-700 Chinese characters.
- The industry map, lifecycle judgment, seven modules, pressure test, and follow-up verification list are present.
- The final `报告合规自检表` does not mark evidence separation as passed if facts, opinions, and inferences are merged.

If this gate fails, rewrite the missing sections before final output.

## Pre-Output Contract Gate

For standard or deep company/product reports, apply `references/company-product-output-contract.md` before final output.

The draft must be built from the heading skeleton in `assets/company-product-template.md`. Before final output, scan for the applicable required heading strings listed in `references/company-product-output-contract.md`.

If any applicable heading is missing, do not output the draft. Restore the missing heading, write the missing body, and rerun the gate.

## Research Brief Gate

Before producing any standard or deep report, verify that `references/research-brief-builder.md` was applied internally.

The internal research brief must lock:

- Original request and inferred intent.
- Report depth and delivery mode.
- Target, geography, time horizon, and boundary assumptions.
- Core research questions.
- Required layers.
- Required template and references.
- Conditional modules.
- Primary-source priority.
- Section-level depth contract.
- Rewrite triggers.

Do not output the internal brief unless the user explicitly asks for a prompt, research brief, requirement summary, or reusable instruction.

If the report route, template, conditional modules, or depth contract cannot be named before drafting, stop drafting, complete the internal brief, and then continue. A standard or deep report that skips this brief fails the gate.

## Report Depth Rubric Gate

Before final output, apply `references/report-depth-rubric.md` to the major analytical sections required by the report type.

Verify:

- Standard report major analytical sections score at least 7/10.
- Deep report major analytical sections score at least 8/10.
- Seven-module subsections meet the rubric threshold for the selected depth.
- Listed-company capital-market priority modules and section `11` score at least 8/10.
- Sections that are mostly tables, repeat generic claims, or mention evidence without mechanism are rewritten before final output.

Do not output the numeric score unless the user explicitly asks for quality scoring. The visible compliance checklist should state whether the depth rubric passed.

## Opening Heading Gate

The Markdown report body for a standard or deep company/product report must begin with:

```md
## 0. 研报前置区
```

Do not put a H1 title, template title, template metadata, output-contract notes, or internal compliance notes before `## 0. 研报前置区`.

If the report begins with `## 1. 直接结论`, or if it outputs template metadata before `## 0. 研报前置区`, the draft fails the gate even if later sections are detailed. Rewrite the report from the company/product template before final output.

## Rewrite Trigger List

Rewrite before final output when a standard or deep company/product report:

- Starts from `## 1. 直接结论`.
- Uses a self-created long-brief structure instead of the template skeleton.
- Uses "why it fell / can it rise / what to watch" as the main structure for a capital-market question.
- Omits `0. 研报前置区`, `0.1`, `0.2`, `0.3`, or `0.4`.
- Omits `2.1 研究计划摘要`, `2.2 来源矩阵和证据质量`, or `2.3 二次检索缺口`.
- Compresses `5.1-5.7` into one table, one paragraph, or a few bullet points.
- Omits `11.1-11.4` for stock price, valuation, expectation gap, investability, market-cap repair, or rise/fall questions.
- Omits `12. 多视角压力测试`.
- Omits `17. 报告合规自检表`.
- Uses media summaries as core evidence when primary company filings, official statistics, regulators, industry associations, exchange filings, or company IR sources are available.

Do not show a failing draft to the user. Rewrite the missing sections first.

## Company/Product Report Gate

Before final output, verify all items below:

- The report used `assets/company-product-template.md` as the section structure.
- The report follows the research brief gate.
- The report used `references/output-format.md` for length and prose-first rules.
- Standard company/product reports target 10000-15000 Chinese characters unless the user explicitly triggers Explicit Short Answer Mode.
- Listed-company capital-market reports target 12000-18000 Chinese characters unless the user explicitly triggers Explicit Short Answer Mode.
- The report meets both total-length expectations and section-level depth expectations; one cannot substitute for the other.
- The report includes research boundary.
- The report includes industry key indicators.
- `0.3 核心指标总览` is a metrics table with columns `指标`, `行业读数`, `目标公司/产品读数`, `判断`, and `证据/来源`; it covers market size, growth or penetration, competition, profitability, prosperity, and key risks.
- The report includes industry map details: vertical value chain, horizontal competition, production factors, production relations, key flows, and target position.
- The report includes lifecycle judgment.
- The seven core modules appear as 7 separate subsections.
- Each seven-module subsection keeps these four exact labels: `结论`, `依据`, `机制`, `对目标公司/产品的影响`.
- Tables support the reasoning but do not replace the main analysis.
- Facts, opinions, and inferences are separated when the distinction affects the conclusion.
- Weak evidence is marked as weak evidence or evidence gap.
- The report includes a multi-perspective pressure test section.
- Important company and industry claims follow the primary source gate.
- Important company and industry claims follow the source quality gate.
- The report follows the formal report style gate.
- The report follows the section-level depth gate.
- The report follows the report depth rubric gate.
- The report follows the Deep Research gate.
- The report follows the layer gate.
- The report follows the explicit short answer gate.
- The report follows the seven-module depth gate.
- The report follows the heading gate.
- The report follows the template skeleton gate.
- The report follows the compressed report gate.
- The report follows the research trace density gate.
- The report follows the visible compliance checklist gate.

## Template Skeleton Gate

For standard or deep company/product reports, verify the report preserves the required company/product template skeleton before final output.

Required core skeleton:

- `0. 研报前置区`
- `1. 直接结论`
- `2. 研究边界`
- `2.1 研究计划摘要`
- `2.2 来源矩阵和证据质量`
- `2.3 二次检索缺口`
- `3. 宏观环境分析`
- `4. 中观行业分析`
- `4.3 行业地图和目标位置`
- `4.4 生命周期判断`
- `5. 七个核心模块加权分析`
- `5.1 可行性`
- `5.2 规模性`
- `5.3 防守性`
- `5.4 盈利性`
- `5.5 估值`
- `5.6 外部因素`
- `5.7 景气度`
- `6. 微观公司/产品分析`
- `10. 事实, 观点和推断分层`
- `12. 多视角压力测试`
- `13. 风险和机会`
- `15. 方法论和数据来源说明`
- `16. 附录: 后续验证清单`
- `17. 报告合规自检表`

Conditional skeleton:

- Multi-business companies must include `4.0 多业务线中观拆分`.
- `4.0 多业务线中观拆分` must include business line or industry line, industry stage, competitive structure, key metrics or prosperity signals, and implication for the target company.
- Capital-market questions must include `11. 资本市场表现与估值预期变化` and `11.1-11.4`.
- Portfolio section `8. 业务/产品组合分析` is required only for portfolio questions.

If any required skeleton section is missing, rewrite the report before final output.

## Compressed Report Gate

A report is a compressed report failure if it is long but bypasses the required template structure.

For standard or deep company/product reports, do not replace the template skeleton with self-created structures such as:

- "Conclusion first / why it fell / what to watch".
- "Why it fell / can it rise / my judgment".
- "One-line attribution table" as the main body.
- A sequence of topical paragraphs without `2.1`, `2.2`, `2.3`, `5.1-5.7`, and required ending sections.

If this gate fails, rewrite using `assets/company-product-template.md`.

## Research Trace Density Gate

For standard or deep company/product reports, `2.1`, `2.2`, `2.3`, `10`, and `15` must contain substantive body content. A heading, a placeholder sentence, or an empty table is not enough.

Rewrite before final output if:

- `2.1` does not show the actual research plan or key subquestions.
- `2.2` does not distinguish source types, evidence quality, and primary-source status.
- `2.2` does not include source type, report use, evidence tier/grade, retrieval or primary-source status, and limitation or gap-handling columns.
- `2.3` does not name missing sources and next verification steps.
- `2.3` does not state what is missing, why it matters, what to verify next, and which primary or near-primary source to check.
- `2.3` does not show three-round closure attempts, current status, and the reason a gap remains unresolved.
- `2.3` keeps a gap as unresolved without explaining that the source is inaccessible, requires a paid database, requires login, public search produced no reliable result, or the available evidence has a mismatched period, geography, or definition.
- `10` does not separate facts, opinions, inferences, evidence tier, and confidence.
- `10` does not include fact/opinion/inference type, content, source/evidence, evidence tier, source status, and confidence columns.
- `15` does not explain methodology, data-source limits, and assumptions.

## Visible Compliance Checklist Gate

Standard and deep reports must end with a visible `报告合规自检表`. This is a reader-facing checklist, not a replacement for the analysis.

The checklist must include at least these rows:

- Template skeleton completeness.
- Research brief translation was completed before drafting.
- Explicit Short Answer Mode was not mis-triggered.
- Deep Research visible trace.
- Correct macro/meso/micro/capital-market layer selection.
- Multi-business meso split when applicable.
- Seven core modules are complete.
- Every seven-module subsection keeps `结论`, `依据`, `机制`, and `对目标公司/产品的影响`.
- Priority seven-module sections have enough depth.
- Macro, meso, micro, and capital-market sections meet the section-level depth contract when applicable.
- Report depth rubric threshold was met.
- Capital-market section appears when applicable.
- Source quality and evidence grading.
- Primary-source retrieval status and gaps.
- Fact/opinion/inference separation with evidence tier.
- Follow-up verification checklist.
- Markdown heading format.

If any row cannot be marked as passed, fix the missing report section before final output. A token checklist such as only "passed" is not enough. Do not output a failing standard or deep report.

Do not mark a row as "partially passed" in a final standard or deep report. If a requirement is only partially satisfied, fix the body first, then mark the checklist row as passed or not applicable.

## Deep Research Gate

For standard and deep reports, verify the report shows visible traces of Deep Research Engine:

- The report states the research boundary and selected layers.
- The report includes a research plan summary.
- The report includes a source/evidence matrix or methodology note.
- The report includes key evidence quality notes.
- The report includes three-round retrieval closure results or source-oriented follow-up verification.
- The report includes retrieval-gap closure results: round-by-round attempted sources, status, unresolved reason, and next source.
- Important claims have source type, evidence quality, or confidence markings.
- Key claims are cross-checked where possible, or evidence gaps are marked.
- Contradictory source definitions, dates, geographies, or scopes are explained instead of merged silently.
- Follow-up verification items are specific and source-oriented.

## Layer Gate

Before final output, verify layer selection:

- Industry overview reports include macro and meso layers; micro appears only when representative cases or players are needed.
- Industry-specific question reports include macro, meso, and issue-tree logic; micro appears only when the question involves a company, product, project, or player.
- Company/product reports include macro, meso, and micro layers.
- Capital-market layers appear only for stock price, valuation, market expectation, investability, market-cap repair, or rise/fall questions.
- Pure industry questions must not force a company-level micro section.
- Multi-business companies split the meso layer by relevant business lines.

## Explicit Short Answer Gate

Only skip standard report requirements when the user explicitly asks for a short, simple, quick, brief, one-paragraph, one-sentence, no-detail, or no-expansion answer.

If the user did not explicitly trigger this mode, verify:

- The report does not open with "quick take", "brief version", "first quick judgment", "simple view", or similar brief-only framing.
- The report uses the standard report structure.
- Company/product and capital-market questions do not collapse into a short comment.

If this gate fails, rewrite as a standard report.

## Seven-Module Depth Gate

For standard company/product reports, verify every seven-module subsection:

- Keeps the exact labels `结论`, `依据`, `机制`, and `对目标公司/产品的影响`.
- Also includes `关键指标和后续验证`, naming the metrics to track and the next primary or near-primary sources to verify.
- Reaches roughly 300-500 Chinese characters, unless the user explicitly requested a short answer.
- Includes at least 2 evidence points, data points, source pointers, or clearly marked evidence gaps.
- Explains causality in the mechanism, not just a generic business logic sentence.
- Links the implication to a concrete target company/product metric, business line, risk, or verification item.

For capital-market questions, profitability, valuation, external factors, and prosperity must be deeper than non-priority modules, but non-priority modules still need their own metric and verification block.

## Section-Level Depth Gate

For standard and deep reports, verify the report has analytical density inside major sections, not just correct headings.

For standard company/product reports:

- `3. 宏观环境分析` covers at least 2-3 relevant macro variables and states how they affect the industry and target.
- `4. 中观行业分析` includes industry definition, supply-demand or competitive structure, key indicators, industry map, and lifecycle judgment.
- Lifecycle judgment includes stage conclusion, evidence, counter-evidence, confidence, and implication for the industry, target, or question.
- `3` and `4` must contain substantive analysis; headings or generic background sentences are not enough.
- `5.1-5.7` follow the seven-module depth gate.
- `6. 微观公司/产品分析` links company facts to industry conclusions and target implications.
- `6` covers business model, product/service, customers/channels, financial or operating indicators, and moat or competitive position.
- `10. 事实, 观点和推断分层` includes evidence tier, source status, and confidence for important claims.
- `12. 多视角压力测试` includes at least 4 distinct perspectives unless Explicit Short Answer Mode is triggered.
- `13. 风险和机会` covers both risks and opportunities, and separates industry-structure drivers from target-company/product drivers.
- `16. 附录: 后续验证清单` lists concrete validation items, why each item matters, recommended sources, and priority.

For standard listed-company capital-market reports:

- Section `11` reaches roughly 1800-3000 Chinese characters across `11.1-11.4`.
- `11.1` separates price movement, timing, and likely catalysts.
- `11.2` separates fundamental changes from expectation changes.
- `11.3` explains valuation anchor, expectation gap, and the mechanism behind rerating or derating.
- `11.4` includes upside triggers, downside risks, and scenarios without investment advice.
- `11.1-11.4` cover the required capital-market concept groups, not only long generic paragraphs.

For deep reports:

- `5.1-5.7` reach roughly 600-1000 Chinese characters each.
- If capital-market analysis applies, section `11` reaches roughly 3000-5000 Chinese characters.

If a section is thin, generic, or only repeats a table, rewrite that section before final output. Evidence gaps count only when they name the missing source, why it matters, and the next verification step.

## Heading Gate

Formal reports must use Markdown headings:

- Use `##` for major sections.
- Use `###` for subsections.
- Do not use bold text such as `**1. Section**` as a substitute for headings.

If this gate fails, rewrite headings before final output.

## Formal Report Style Gate

For standard and deep company/product reports, verify formal report presentation before final output:

- The report includes a front section with report summary, key conclusions, core metrics overview, and exhibit list or exhibit placeholders.
- The report is not only a sequence of Markdown sections; it has a clear report-front, main-body, and report-back rhythm.
- `0.1-0.4` must contain substantive content, not only headings, empty tables, or placeholder sentences.
- `0.4 图表清单或图表占位` lists at least 4 concrete exhibits, charts, tables, or placeholders in standard company/product reports.
- Standard reports include a Mermaid industry map unless the active output surface cannot render Mermaid, in which case the report must still include the Mermaid code block as Markdown.
- The first half of the main body establishes industry context before target-specific analysis dominates.
- Major analytical chapters start with a paragraph-level conclusion before details.
- Tables and exhibits support the analysis with metrics, evidence chains, comparisons, or validation lists.
- The report ends with methodology and data source note, evidence quality summary, key assumptions, and follow-up verification appendix.

## Primary Source Gate

For company/product and listed-company capital-market reports, verify primary-source discipline before final output:

- Company financial and operating facts first attempted company filings, financial reports, IR releases, exchange filings, or regulatory filings.
- Stock price movement, market cap, valuation multiples, and benchmark comparisons first attempted exchange data or credible market databases.
- Industry size, penetration, policy, exports, and sales facts first attempted official statistics, regulators, industry associations, international organizations, or credible databases.
- Broker, consensus, media, interviews, and social media are marked as opinions, secondary evidence, supplementary signals, or weak evidence unless independently verified.
- `2.2 来源矩阵和证据质量` states the primary-source status: obtained, attempted but unavailable, or pending retrieval.
- `2.3 二次检索缺口` lists the exact primary sources to verify next.
- `2.3 二次检索缺口` lists only residual high-impact gaps after up to three closure rounds and explains why each remaining gap was not closed.
- `10. 事实, 观点和推断分层` includes evidence tier and primary-source status columns, and marks secondary-source quantitative claims as `待核验事实` or secondary evidence.
- `15. 方法论和数据来源说明`, and `17. 报告合规自检表` reflect primary-source limitations when primary evidence is unavailable.

If this gate fails, rewrite the source matrix, evidence notes, and affected claims before final output.

## Source Quality Gate

For company/product reports, verify source quality before final output:

- Company and financial facts should prioritize company announcements, financial reports, investor relations materials, exchange filings, and regulatory filings.
- Industry facts should prioritize official statistics, regulators, industry associations, international organizations, and credible databases.
- Media, financial websites, social media, and informal sources may be used as supplementary signals only.
- If a media or informal source is used as core evidence because no primary source is available, mark it as weak evidence or a verification need.
- Do not use media summaries to replace available primary company filings or official industry data.

## Pressure Test Gate

Standard and deep company/product reports must include a multi-perspective pressure test section. Use industry expert, investment researcher, policy/regulatory researcher, operator/entrepreneur, and devil's advocate perspectives unless the user asks for a short answer.

The section must contain substantive challenges and verification needs for at least industry expert, investment researcher, policy/regulatory, and operator/entrepreneur perspectives. A heading, one token sentence, or an empty table is not enough.

## Failure Handling

If any required item is missing, rewrite the missing section before final output. Do not apologize, do not mention internal compliance checks, and do not continue with a compressed report.

If evidence is insufficient, write the evidence gap and next verification step. Do not fill the section with generic claims.

## Explicit Short Answer Mode

Only skip the standard report gate when the user explicitly asks for a short, quick, brief, simple, one-paragraph, one-sentence, no-detail, or no-expansion answer. If the request is simply ambiguous, default to the standard report gate.





