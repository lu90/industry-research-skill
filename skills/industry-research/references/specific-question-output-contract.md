# Specific-Question Output Contract

Use this file before writing a standard or deep industry-specific question report. This is a lightweight output contract for pure industry questions. It must not override the company/product output contract.

## Contract Trigger

Apply this contract when the user asks about an industry phenomenon, cause, trend, opportunity, risk, competition, price war, policy impact, profitability, lifecycle, or future direction, and no company/product is the target of analysis.

If the request targets a company, product, brand, business line, listed ticker, stock price, valuation, expectation gap, investability, market-cap repair, or rise/fall potential, use the company/product output contract instead.

## Opening Rule

Pure industry-specific question reports must start by answering the user question:

```md
## 1. 直接回答
```

Do not force `## 0. 研报前置区` for pure industry-specific questions. That opening belongs to standard or deep company/product reports.

## Required Heading Scan

Before final output, scan for these applicable headings:

```md
## 1. 直接回答
## 2. 结论摘要
## 3. 研究边界
### 3.1 研究计划摘要
### 3.2 来源矩阵和证据质量
### 3.3 二次检索缺口
## 4. 行业地图
## 5. 问题拆解和议题树
## 6. 证据链分析
## 7. 生命周期判断
## 8. 七个核心模块分析
## 9. 多视角压力测试
## 10. 风险和不确定性
## 11. 后续验证清单
## 12. 报告合规自检表
```

If any required heading is missing, restore it before final output.

## Evidence Chain Rule

`## 6. 证据链分析` must separate facts, opinions, and inferences. The table must include these columns:

```md
| 子问题 | 结论 | 事实 | 观点 | 推断 | 证据层级 | 来源状态 | 置信度 |
```

Rules:

- `事实` should cite official statistics, regulators, industry associations, credible databases, company filings, or clearly marked secondary evidence.
- `观点` should identify the source stance, such as regulator, company, broker, media, expert, consumer, or operator.
- `推断` should state the reasoning bridge from facts and opinions to the conclusion.
- `证据层级` should use primary, near-primary, secondary, or weak evidence.
- `来源状态` should state obtained, attempted but unavailable, pending retrieval, or secondary-only.
- Do not mark the compliance checklist as passed if facts, opinions, and inferences are merged into one column.

## Source Matrix Rule

`### 3.2 来源矩阵和证据质量` must show source type, report use, evidence tier, retrieval status, and limitation.

For industry-specific questions, official statistics, regulators, industry associations, customs, central banks, ministries, and credible databases should be preferred for market size, sales, exports, price, policy, and penetration claims. Media may be used for narrative and supplementary signals, but not as the only core proof when primary or near-primary sources are available.

`### 3.3 二次检索缺口` must contain residual high-impact gaps after up to three targeted closure rounds, not merely first-pass missing items. Show the gap, round-by-round attempted sources, current status, why it matters, unresolved reason, and next source. Keep a gap as unresolved only when the active environment cannot access the source, the source requires a paid database or login, public search returns no reliable result, or the available evidence has a mismatched period, geography, or definition.

## Seven-Module Rule

The seven modules may be shorter than company/product reports, but all seven must appear as independent subsections or clearly separated blocks. Do not replace the seven modules with a single summary sentence.

For standard industry-specific question reports:

- `## 1. 直接回答` should include 3-6 substantive paragraphs or a conclusion table plus explanatory paragraphs.
- `## 5. 问题拆解和议题树` should contain 3-5 verifiable subquestions.
- `## 6. 证据链分析` should include enough rows to cover the core subquestions. For complex questions, use at least 5 rows.
- Each seven-module block should reach roughly 200-400 Chinese characters.
- Each module should state conclusion, evidence or evidence gap, mechanism, and implication for the industry question.

For deep industry-specific question reports:

- Each seven-module block should reach roughly 400-700 Chinese characters.
- The evidence chain should explain conflicting evidence, source limitations, and confidence.

If the direct answer is only a short take, or if the seven modules are only labels, rewrite before final output.

## Rewrite Triggers

Rewrite before final output if the draft:

- Does not start with `## 1. 直接回答`.
- Uses the company/product `## 0. 研报前置区` opening for a pure industry-specific question.
- Omits research plan, source matrix, or three-round retrieval closure results.
- Omits the `观点` column in the evidence chain.
- Merges facts, opinions, and inferences into one undifferentiated paragraph.
- Gives a short-take direct answer without evidence and mechanism.
- Writes seven modules as labels or a single summary sentence.
- Omits industry map, lifecycle judgment, seven modules, pressure test, or final compliance checklist.
