# Section Depth Playbook

Use this file with `references/output-format.md` and `references/report-depth-rubric.md` for standard and deep reports. It tells the agent how to expand sections with analytical substance, not just meet a heading or character-count requirement.

## Core Rule

For every major analytical section, write depth through distinct reasoning blocks:

1. Conclusion block: state the section judgment in concrete terms.
2. Evidence block: provide facts, metrics, source-backed opinions, or named evidence gaps.
3. Mechanism block: explain why the evidence supports the judgment.
4. Implication block: explain the effect on the industry, target company, product, metric, risk, or decision.
5. Verification block: state uncertainty, confidence, and the next evidence to verify.

Do not merge all five blocks into one generic paragraph. Tables may summarize these blocks, but the prose must carry the reasoning.

## Minimum Expansion Pattern

For standard reports:

- Major chapters such as `3`, `4`, `6`, `10`, `12`, and `13` should contain at least 3 substantive paragraphs plus any useful table or exhibit.
- Seven-module subsections should contain at least 4 short paragraphs or clearly separated labeled blocks: `结论`, `依据`, `机制`, and `对目标公司/产品的影响`.
- Priority seven-module subsections should add a fifth block for `关键指标和后续验证`.
- Capital-market subsections `11.1-11.4` should each contain at least 3 substantive paragraphs or 2 paragraphs plus one evidence/scenario table.

For deep reports:

- Major chapters should contain at least 4-6 substantive paragraphs plus tables or exhibits where useful.
- Seven-module subsections should contain all five blocks and should not rely on one paragraph per label if the issue is strategically important.
- Section `11` should read as a full analytical chapter, not a market-comment insert.

## What Counts As A Substantive Paragraph

A paragraph counts toward depth only if it does at least one of these:

- connects a specific source, metric, event, or evidence gap to the section conclusion;
- explains a causal mechanism or tradeoff;
- compares the target with competitors, substitutes, or historical benchmarks;
- names a decision-relevant implication;
- names an uncertainty and the specific evidence needed to resolve it.

A paragraph does not count when it only repeats the heading, restates the same conclusion, uses generic phrases, or says "needs further verification" without naming the source to check.

## Seven-Module Expansion Pattern

Each seven-module subsection must follow this writing order:

1. `结论`: one specific judgment tied to the user question.
2. `依据`: at least two evidence points, source pointers, metrics, events, or named evidence gaps.
3. `机制`: one causal chain from evidence to conclusion.
4. `对目标公司/产品的影响`: one concrete effect on business line, growth, margin, valuation, competitive position, risk, or verification priority.
5. `关键指标和后续验证`: required for priority modules and recommended for all modules in deep reports.

For listed-company capital-market reports, priority modules are `5.4 盈利性`, `5.5 估值`, `5.6 外部因素`, and `5.7 景气度`. These modules must be visibly thicker than non-priority modules.

## Capital-Market Section 11 Pattern

For listed-company stock price, valuation, expectation gap, or rise/fall questions, section `11` must expand like this:

- `11.1 股价表现拆解`: define the time window, price movement, relative performance if available, event timeline, and catalyst confidence.
- `11.2 基本面变化`: separate reported fundamentals, forward-looking operating indicators, and market expectation changes.
- `11.3 估值逻辑和市场预期差`: identify valuation anchor, expectation embedded in the previous price, new information that changed the anchor, and why the market may have overreacted or underreacted.
- `11.4 上涨触发器, 下跌风险和情景分析`: separate upside triggers, downside risks, scenario assumptions, and tracking indicators. Do not give a buy/sell recommendation.

Each subsection should include at least one named evidence source or evidence gap. If no reliable market data is available, state the missing source, why it matters, and the next verification step.

## Anti-Thinness Gate

Rewrite a section before final output if any of these are true:

- The section has the correct heading but only one short paragraph.
- The section is mostly a table and has little causal explanation.
- The `依据` block has fewer than two evidence points or named evidence gaps.
- The `机制` block uses generic cause words but does not explain a concrete causal chain.
- The implication does not name the target, industry, metric, risk, or decision.
- The verification block says only "continue tracking" without naming what to track.

