# Company/Product Few-Shot

Use this file for standard or deep company/product reports. The examples are fragments, not full reports.

## Bad: One-Sentence Module

Do not write this:

```md
**Feasibility:** Feasible. China smart EV demand has been proven, but profit is the main issue.
```

Why it fails: it collapses conclusion, evidence, mechanism, and target implication into one sentence. It reads like a quick comment, not a research report.

## Good: Seven-Module Subsection

Write this shape instead:

```md
### 5.1 可行性

**Conclusion:** The industry-level demand for smart EVs is already validated, but the feasible business model is shifting from "selling EV units" to "selling differentiated mobility products with software, charging, service, and cost-control advantages".

**Evidence:** Use official registrations, penetration rate, delivery data, company filings, user adoption, or clearly marked evidence gaps. If only media reports are available, mark them as supplementary signals rather than core proof.

**Mechanism:** Explain why verified demand does not automatically mean every player is feasible. In a high-penetration and price-war stage, feasibility depends on whether the company can convert demand into repeatable gross margin, stable product cycles, and lower unit cost.

**Target implication:** For the target company/product, state whether its product definition, channel, cost structure, technology, or customer segment gives it a better or worse chance of turning industry demand into sustainable revenue and profit.
```

## Bad: Thin Four-Label Module

Do not write this even though it keeps the four labels:

```md
### 5.4 Profitability

**Conclusion:** Profitability is under pressure.

**Evidence:** Gross margin declined and competition is intense.

**Mechanism:** Price war and cost pressure hurt margins.

**Target implication:** The target must improve margins.
```

Why it fails: it satisfies the label format but not the research depth requirement. It lacks concrete data, source pointers, multiple evidence points, causal detail, and target-specific metrics.

## Good: Dense Seven-Module Fragment

```md
### 5.4 Profitability

**Conclusion:** The profitability issue is not only whether the target can sell more units, but whether scale can offset price pressure, component cost volatility, and new-business investment. For a capital-market question, this module should be treated as a priority module because it directly affects valuation repair.

**Evidence:** Use at least two evidence points: company-reported gross margin or operating margin, segment revenue or loss, management guidance, cost drivers such as battery or memory prices, or a clearly marked evidence gap. If only media reports are available, mark them as supplementary and specify the next filing or industry source to verify.

**Mechanism:** Explain the causal chain. For example, higher deliveries may increase revenue but still fail to improve profit if ASP falls, warranty/service costs rise, or R&D and channel costs grow faster than gross profit. Conversely, stable ASP and falling unit cost can turn volume growth into margin recovery.

**Target implication:** Tie the conclusion to target-specific indicators: segment gross margin, operating loss, free cash flow, inventory turnover, ASP, subsidy/discount level, or business-line profit mix. State which indicator would support the thesis and which would falsify it.
```

## Bad: Thin Industry Base

Do not write this:

```md
China NEV is in late growth stage. Competition is intense, so the target must compete on price and technology.
```

Why it fails: it lacks market indicators, value-chain structure, lifecycle evidence, and implication for the target.

## Good: Industry Base Fragment

```md
### Industry Key Indicators

Use a compact metric table first, then explain the mechanism in prose. Include market size or proxy, growth/penetration, supply-demand, price/cost, policy/regulation, and regional/export variables. For each indicator, state what it means for the target.

After the table, add 1-3 paragraphs explaining the pattern: what is improving, what is deteriorating, where the bottleneck is, and which indicators should be tracked next.
```

## Evidence Gap Pattern

Use this when data is unavailable:

```md
**Evidence:** Public data is not enough to confirm channel inventory by model. This is an evidence gap. The next verification step is to check dealer quotes, terminal discounts, inventory days, and monthly delivery split by model.
```

## Fact / Opinion / Inference Pattern

```md
| Type | Content | Source/Basis | Confidence |
|---|---|---|---|
| Fact | The company reported X deliveries and Y gross margin. | Company filing or announcement. | High |
| Opinion | Analysts argue the industry is entering a price-war stage. | Broker or consulting report; note the source standpoint. | Medium |
| Inference | The target's valuation should depend more on gross-margin durability than delivery volume alone. | Based on lifecycle stage, price pressure, and company margin trend. | Medium |
```

## Bad: Weak Source Use

Do not write this:

```md
**Evidence:** A media article says the industry is huge and the company is profitable.
```

Why it fails: media can be useful context, but it should not replace available company filings, official statistics, industry association data, or regulatory sources for core facts.

## Good: Source Quality Pattern

```md
**Evidence:** For company revenue, margin, deliveries, and cash position, use company filings, financial reports, IR announcements, or exchange filings first. For industry sales, penetration, exports, and policy, use official statistics, regulators, industry associations, international organizations, or credible databases first. Use media only as supplementary signal, and mark it as weak evidence when it cannot be independently verified.
```

## Pressure Test Pattern

```md
| Perspective | Challenge | Why it matters | Needed verification |
|---|---|---|---|
| Industry expert | The value-chain profit pool may not actually shift toward the target's link. | This would weaken the profitability conclusion. | Compare gross margin, bargaining power, and capacity utilization across value-chain links. |
| Investment researcher | The valuation thesis may rely on temporary margin improvement. | This affects whether the company deserves a higher multiple. | Verify recurring gross margin, free cash flow, and non-recurring revenue. |
| Devil's advocate | The core conclusion may be driven by narrative rather than financial evidence. | This is the main risk to the recommendation. | Identify evidence that would falsify the thesis. |
```

## Bad: Stock Quick Comment

Do not write this for stock price, valuation, or rise/fall questions:

```md
The stock fell because Q1 profit missed expectations and EV growth slowed. It may rise if deliveries improve.
```

Why it fails: it treats a capital-market question as a quick comment. It skips macro conditions, meso industry context, micro company facts, valuation logic, expectation gap, evidence quality, and scenario indicators.

## Bad: Starts From Section 1

Do not write this as the final report:

```md
## 1. 目标公司/产品综合判断

The stock fell because valuation expectations weakened and business fundamentals need more proof.

## 2. 为什么下跌
...
```

Why it fails: a standard or deep company/product report must start with `## 0. 研报前置区`. Starting from `## 1. 目标公司/产品综合判断` usually means the report skipped report summary, key conclusions, core metrics overview, exhibit list, research plan, source matrix, and evidence gaps.

## Bad: Seven Modules As One Table

Do not use one table as the body of the seven-module analysis:

```md
## 5. 七个核心模块分析

| 模块 | 判断 |
|---|---|
| 可行性 | 需求仍在 |
| 规模性 | 空间较大 |
| 防守性 | 竞争激烈 |
| 盈利性 | 毛利承压 |
| 估值 | 预期下修 |
| 外部因素 | 风险偏好下降 |
| 景气度 | 短期偏弱 |
```

Why it fails: a summary table can appear as an exhibit, but the body must contain `### 5.1` through `### 5.7`, and each subsection must include conclusion, evidence, mechanism, and target implication.

## Bad: Long Brief Without Template Skeleton

Do not write this as the final report even if it is long:

```md
## Conclusion First
...
## Why the stock fell
...
## What to watch next
...
## My judgment
...
```

Why it fails: length does not make it a standard company/product report. It misses the locked skeleton: research plan summary, source matrix, three-round retrieval closure results, seven modules `5.1-5.7`, micro analysis, fact/opinion/inference separation, pressure test, methodology, and appendix.

## Good: Template Skeleton Fragment

Use this skeleton shape before filling content:

```md
## 0. 研报前置区

### 0.1 报告摘要

### 0.2 关键结论

### 0.3 核心指标总览

### 0.4 图表清单或图表占位

## 1. 目标公司/产品综合判断

## 2. 研究边界

### 2.1 研究计划摘要

### 2.2 来源矩阵和证据质量

### 2.3 检索缺口闭环结果

## 5. 七个核心模块分析

### 5.1 可行性
### 5.2 规模性
### 5.3 防守性
### 5.4 盈利性
### 5.5 估值
### 5.6 外部因素
### 5.7 景气度

## 11. 资本市场表现与估值预期变化

### 11.1 股价表现拆解
### 11.2 基本面变化
### 11.3 估值逻辑和市场预期差
### 11.4 上涨触发器, 下跌风险和情景分析

## 12. 多视角压力测试

## 17. 报告合规自检表
```

Why it works: it preserves the mandatory report skeleton and prevents the model from collapsing the answer into a long quick comment.

## Good: Seven-Module Summary Plus Body

Use a summary matrix only before the independent subsections:

```md
## 5. 七个核心模块分析

| 模块 | 初步判断 | 证据质量 |
|---|---|---|
| 可行性 | {摘要} | {高/中/低} |
| 规模性 | {摘要} | {高/中/低} |

### 5.1 可行性

**结论:** {具体判断}

**依据:** {至少两个证据点, 来源指向或证据缺口}

**机制:** {因果链}

**研究含义:** {落到目标指标, 业务线, 风险或验证项}

### 5.2 规模性

**结论:** {具体判断}

**依据:** {至少两个证据点, 来源指向或证据缺口}

**机制:** {因果链}

**研究含义:** {落到目标指标, 业务线, 风险或验证项}
```

Why it works: the table helps the reader scan, while the independent subsections carry the actual research reasoning.

## Good: Capital-Market Research Fragment

```md
### Capital Market Performance and Valuation Expectation Change

**Conclusion:** The stock move should be decomposed into company fundamentals, sector beta, valuation expectation, and liquidity/risk appetite. Do not explain the move with one earnings number.

**Evidence:** Use company filings for revenue, margin, deliveries, cash flow, and buybacks. Use exchange or credible market data for stock movement and valuation. Use broker or media views only as opinions or supplementary signals.

**Mechanism:** A listed company can fall even when long-term strategy remains intact if the market had priced in faster growth, higher margin, or lower execution risk. The report must identify which assumption changed.

**Target implication:** State the measurable repair triggers, such as delivery recovery, margin stabilization, cash-flow improvement, valuation multiple repair, or sector risk appetite recovery. Also state what would falsify the recovery thesis.
```
