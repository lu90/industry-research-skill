# Report Regression Tests

Use this maintenance-only reference after changing the skill. It is not required for normal report generation. The goal is to verify that changes do not cause reports to regress into quick briefs, self-created outlines, or shallow template fills.

## How To Use

Run at least the six prompts below after material changes to routing, templates, evidence rules, or depth rules.

For each prompt, check:

1. Route and template.
2. Opening rule.
3. Required sections.
4. Evidence discipline.
5. Depth rubric.
6. Forbidden failure patterns.

For generated Markdown reports, also run the deterministic checker when a profile applies:

```bash
python scripts/report_contract_check.py --self-test
python scripts/report_contract_check.py --self-test --json
python scripts/report_contract_check.py path/to/report.md --profile auto --json
python scripts/report_contract_check.py path/to/report.md --profile company-capital
python scripts/report_contract_check.py path/to/report.md --profile company-capital --json
python scripts/report_contract_check.py path/to/report.md --profile company
python scripts/report_contract_check.py path/to/report.md --profile overview
python scripts/report_contract_check.py path/to/report.md --profile specific
python scripts/report_contract_check.py path/to/report.md --profile prompt-builder
python scripts/report_contract_check.py path/to/report.md --profile short
python scripts/report_batch_check.py --self-test
python scripts/report_batch_check.py --self-test --json
python scripts/report_batch_check.py path/to/reports-dir --json
```

Run `--self-test` after changing either checker. Self-tests include both passing and failing `company-capital`, `overview`, and `specific` fixtures, including total report length, report-front density, macro/meso depth, micro depth, priority depth blocks, section `11` paragraph density, research trace density, compliance checklist content, pressure-test content, risk/opportunity content, and verification-appendix content. Use `--profile auto --json` for a single report when the report type is not already known. Use `report_batch_check.py` for a directory of generated regression reports. The checker catches structural failures only. Passing it does not prove source quality, fact accuracy, or investment reasoning quality.

Passing one prompt is not enough. A change is stable only if all relevant prompts pass.

## Forward-Agent Test Gate

After every material change to routing, templates, evidence rules, depth rules, or checker behavior, run at least one real forward-agent test in addition to deterministic self-tests.

Minimum required forward test:

1. Spawn a fresh independent agent without the maintenance iteration context.
2. Give it the real skill mention and user prompt:

```text
[$industry-research](G:\skills_repos\industry-research-skill\skills\industry-research\SKILL.md) 请帮助我分析一下小米公司的股价为什么下跌了这么多
```

3. Ask the agent to create the full Markdown report under `reports/`, using `YYYYMMDD_HHMMSS_主题.md`.
4. Run:

```bash
python -B skills/industry-research/scripts/report_contract_check.py reports/<generated-report>.md --profile company-capital
```

The forward test fails if the generated answer:

- is a short brief or market comment;
- says an existing report file already contains the full draft and then outputs only a condensed judgment, unless the user explicitly asked for a summary;
- starts with anything other than `## 0. 研报前置区`;
- omits `2.1-2.3`;
- omits independent `5.1-5.7`;
- omits `11.1-11.4`;
- omits `12` or `17`;
- fails the deterministic company-capital checker.

Do not claim that a change has stabilized the Xiaomi stock-price prompt unless this forward-agent test has been run and the saved artifact passes the checker. Deterministic self-tests are necessary but not sufficient.

Also run the same Xiaomi prompt once with an existing report artifact available in context, such as `planning/forward-test-v54-xiaomi-stock-drop.md`. The presence of the existing file must not change the answer into a short summary. Existing files may be used as context, but the output still must satisfy the company-capital checker unless the user explicitly asks to summarize or review the file.

For all standard or deep prompts, the expected runtime behavior is Workspace Report File when file writing is available: the full report is written under `reports/`, and the chat reply contains only the path, short summary, and compliance/checker status. A chat-only brief fails unless the user explicitly asked for short-answer mode or unsaved Prompt Builder Mode.

## Prompt 1: Listed-Company Capital-Market Report

Prompt:

```text
请帮助我调研一下小米公司为什么股价跌了这么多呢?
```

Expected route:

- Company/product analysis plus listed-company capital-market module.
- Use `assets/company-product-template.md`.
- Use Workspace Report File by default when file writing is available; the saved report starts with `## 0. 研报前置区`.

Must include:

- `0.1-0.4`.
- `0.1-0.4` are not empty or token sections.
- `0.3` includes a metrics table with columns `指标`, `行业读数`, `目标公司/产品读数`, `判断`, and `证据/来源`, covering market size, growth or penetration, competition, profitability, prosperity, and key risks.
- `0.4` lists at least 4 concrete exhibits, charts, tables, or placeholders.
- `2.1-2.3`.
- `4.0` for listed-company capital-market reports; if the target is genuinely single-business, `4.0` explains why no material split is needed.
- `4.0` includes business line or industry line, industry stage, competitive structure, key metrics or prosperity signals, and implication for the target company.
- `5.1-5.7` as independent subsections.
- `10`.
- `11.1-11.4`.
- `12`.
- `17`.

Depth checks:

- `5.4-5.7` are visibly deeper than non-priority modules.
- `5.1-5.7` each include `关键指标和后续验证`.
- The full listed-company capital-market report reaches the standard-report target range rather than only passing local section minimums.
- Section `11` is a substantive analysis chapter, not only a scenario table.
- `11.1-11.4` pass paragraph-density checks in `report_contract_check.py`.
- `11.1` covers price movement, time window, benchmark or sector comparison, catalysts, and evidence gaps.
- `11.2` covers revenue, profitability or margin, cash flow, orders/delivery/operating metrics, guidance or business mix, and fundamental versus expectation changes.
- `11.3` covers valuation anchor, expectation gap, prior priced-in assumptions, rerating or derating mechanism, and indicators that need to be proven again.
- `11.4` covers upside triggers, downside risks, scenarios, tracking indicators, and no-investment-advice framing.
- Report depth rubric threshold passes.
- A Mermaid industry map appears in the report.
- `3` and `4` are not empty or token background sections.
- `4.4` includes lifecycle stage, evidence, counter-evidence, confidence, and target implication.
- `6` covers business model, product/service, customers/channels, financial/operating indicators, and moat or competitive position.
- `13` separates risks from opportunities, and separates industry-structure drivers from target-company/product drivers.
- `16` is a concrete verification appendix with待验证问题, 为什么重要, 推荐来源, and 优先级.

Evidence checks:

- Primary or near-primary sources are attempted first.
- Media-supported quantitative claims are marked as secondary or pending verification.
- `2.2`, `2.3`, `10`, `15`, and `17` reflect source gaps consistently.
- `2.1`, `2.2`, `2.3`, `10`, and `15` are not empty or token sections.
- `2.3` states what is missing, which three-round closure sources were attempted, current status, why it matters, unresolved reason, next verification step, and the primary or near-primary source to check.
- `2.3` does not keep a high-impact gap as `仍未补齐` unless it states that the source is inaccessible, requires a paid database, requires login, public search produced no reliable result, or the available evidence has a period/geography/definition mismatch.
- `2.2` includes source type, report use, evidence tier/grade, retrieval or primary-source status, and limitation/gap handling.
- `10` includes fact/opinion/inference type, content, source/evidence, evidence tier, source status, and confidence.
- `17` includes checklist rows for skeleton, research brief, depth, layers, evidence, source status, fact/opinion/inference separation, and follow-up verification.
- `12` includes at least industry expert, investment researcher, policy/regulatory, and operator/entrepreneur pressure-test perspectives.
- `16` prioritizes primary or near-primary verification sources rather than only generic media follow-up.

Forbidden failures:

- Starts with `## 1. 直接结论`.
- Uses "why it fell / can it rise / what to watch" as the main structure.
- Collapses seven modules into one table.
- Gives investment advice, target price, or guaranteed return.

## Prompt 2: Normal Company/Product Report

Prompt:

```text
分析一下蜜雪冰城在东南亚市场的增长前景.
```

Expected route:

- Company/product analysis.
- Use `assets/company-product-template.md`.
- Use Workspace Report File by default when file writing is available; the saved report starts with `## 0. 研报前置区`.
- Do not add section `11` unless the prompt asks about stock price, valuation, market expectation, investability, or rise/fall potential.

Must include:

- Industry overview base before target-specific analysis.
- Industry map and target position.
- Lifecycle judgment.
- `5.1-5.7` independent subsections.
- Micro company/product analysis.
- Pressure test and final compliance checklist.

Depth checks:

- Seven modules include conclusion, evidence, mechanism, and target implication.
- Macro, meso, and micro sections pass the report depth rubric.

Forbidden failures:

- Treats the question as a generic Southeast Asia beverage industry overview without target analysis.
- Adds capital-market section without trigger.
- Uses SWOT as the whole report structure.

## Prompt 3: Pure Industry-Specific Question

Prompt:

```text
为什么中国新能源汽车行业最近价格战这么激烈?
```

Expected route:

- Pure industry-specific question.
- Use `assets/specific-question-template.md`.
- Use Workspace Report File by default when file writing is available; the saved report starts with `## 1. 直接回答`.
- Do not use company/product `## 0. 研报前置区`.

Must include:

- Substantive direct answer.
- Research plan, source matrix, and three-round retrieval closure results.
- Issue tree.
- Evidence chain with fact, opinion, inference, evidence tier, source status, and confidence.
- Industry map, lifecycle, seven modules, pressure test, and final checklist.

Depth checks:

- The full standard industry-specific question report reaches the standard-report target range rather than only passing local section minimums.
- Direct answer includes evidence and mechanism.
- A Mermaid industry map appears in the report.
- `7` includes lifecycle stage, evidence, counter-evidence, confidence, and question implication.
- `3.2` includes source type, report use, evidence tier, retrieval status, and limitation columns.
- `3.3` states what is missing, which three-round closure sources were attempted, current status, why it matters, unresolved reason, next verification step, and the primary or near-primary source to check.
- `3.3` does not keep a high-impact gap as `仍未补齐` unless it states that the source is inaccessible, requires a paid database, requires login, public search produced no reliable result, or the available evidence has a period/geography/definition mismatch.
- `6` includes subquestion, conclusion, fact, opinion, inference, evidence tier, source status, and confidence columns.
- `8.1-8.7` are independent blocks with conclusion, evidence, mechanism, and question implication.
- Evidence chain covers the main subquestions.

Forbidden failures:

- A short commentary answer only.
- Facts, opinions, and inferences merged into one paragraph.
- Seven modules reduced to a sentence.

## Prompt 4: Pure Industry Overview

Prompt:

```text
帮我做一份中国宠物食品行业研究.
```

Expected route:

- Industry overview.
- Use `assets/industry-overview-template.md`.
- Use Workspace Report File by default when file writing is available.
- May start with a report title.
- Do not force company/product `## 0. 研报前置区`.

Must include:

- `2.1-2.3`.
- Industry map.
- Lifecycle judgment.
- `5.1-5.7`.
- Fact/opinion/inference separation.
- Pressure test.
- Final compliance checklist.

Depth checks:

- The full standard industry overview report reaches the standard-report target range rather than only passing local section minimums.
- A Mermaid industry map appears in the report.
- `4` includes lifecycle stage, evidence, counter-evidence, confidence, and industry implication.
- `2.2` includes source type, report use, evidence tier, retrieval status, and limitation columns.
- `2.3` states what is missing, which three-round closure sources were attempted, current status, why it matters, unresolved reason, next verification step, and the primary or near-primary source to check.
- `2.3` does not keep a high-impact gap as `仍未补齐` unless it states that the source is inaccessible, requires a paid database, requires login, public search produced no reliable result, or the available evidence has a period/geography/definition mismatch.
- `8` includes fact/opinion/inference type, content, source/evidence, evidence tier, source status, and confidence columns.
- Seven modules include conclusion, evidence, mechanism, and industry implication.
- Trend projection has enough reasoning and triggers.
- Source matrix identifies primary and secondary evidence.

Forbidden failures:

- Market overview without industry map.
- Seven modules collapsed into a table.
- No evidence-quality or source-gap discussion.

## Prompt 5: Prompt Builder Mode

Prompt:

```text
先帮我把“小米为什么股价跌这么多”整理成一个可交给 industry-research agent 使用的完整 prompt.
```

Expected route:

- Prompt-builder mode.
- Output a reusable prompt, not the final research report.
- Use `assets/research-prompt-template.md`.

Must include:

- Inferred route: company/product plus listed-company capital-market module.
- Required template and references.
- Required sections.
- Depth contract.
- Target character range and section-level depth requirements.
- Evidence rules.
- Compliance requirements.
- Rewrite-before-output triggers.

Forbidden failures:

- Starts writing the Xiaomi report directly.
- Omits capital-market `11.1-11.4` requirement.
- Omits company/product report opening `0. 研报前置区`, `2.1-2.3`, independent `5.1-5.7`, micro company/product analysis, source and depth requirements, or final compliance checklist.

## Prompt 6: Explicit Short Answer Mode

Prompt:

```text
请简单说一下中国新能源汽车价格战为什么激烈, 一段话就好.
```

Expected route:

- Explicit Short Answer Mode.
- A concise answer is allowed.
- It does not need the full standard-report skeleton.

Must still include:

- Clear direct answer.
- No invented data.
- Clear uncertainty if evidence is limited.

Forbidden failures:

- Produces a full 8000+ character report despite explicit short-answer request.
- Gives unsupported exact figures.
