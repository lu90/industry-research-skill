# Report Language Contract

Select `output_language` before drafting:

- Use `zh` when the user explicitly requests Chinese or writes primarily in Chinese.
- Use `en` when the user explicitly requests English or writes primarily in English.
- Map unsupported languages to English unless the user provides a required translation.

Apply one language consistently to every reader-facing heading, label, table header, caption, paragraph, visible brief, and Prompt Builder output. Do not mix Chinese and English contract headings or fields.

This file owns language selection and exact translation only. It does not decide whether a section is required. Shared requiredness is defined by `references/common-report-section-contract.md`; route requiredness is defined by the selected route output contract.

## Report Shell

Formal reports start with exactly one dynamic H1 followed immediately by the language-matched route opening. They end with exactly one fixed disclaimer as the final nonempty line.

Chinese disclaimer:

```text
本报告仅供研究和信息参考, 不构成投资建议, 也不构成任何收益承诺.
```

English disclaimer:

```text
This report is for research and informational purposes only. It does not constitute investment advice or any guarantee of returns.
```

## Route Openings

| Route | Chinese | English |
|---|---|---|
| overview | `行业一句话定义` | `One-Sentence Industry Definition` |
| specific | `直接回答` | `Direct Answer` |
| company and company-capital | `研报前置区` | `Research Front Matter` |

## Shared Heading Dictionary

| `section_id` | Chinese | English |
|---|---|---|
| `research_scope` | `研究边界` | `Research Scope` |
| `research_plan` | `研究计划摘要` | `Research Plan Summary` |
| `source_matrix` | `来源矩阵和证据质量` | `Source Matrix and Evidence Quality` |
| `retrieval_gap_closure` | `检索缺口闭环结果` | `Retrieval Gap Closure Results` |
| `industry_definition` | `行业一句话定义` | `One-Sentence Industry Definition` |
| `industry_map` | `行业地图` | `Industry Map` |
| `lifecycle` | `生命周期判断` | `Lifecycle Assessment` |
| `seven_modules` | `七个核心模块分析` | `Seven Core Modules Analysis` |
| `evidence_classification` | `事实, 观点和推断分层` | `Fact, Opinion, and Inference Layers` |
| `pressure_test` | `多视角压力测试` | `Multi-Perspective Pressure Test` |
| `risk_uncertainty` | `风险, 机会和不确定性` | `Risks, Opportunities, and Uncertainties` |
| `verification_checklist` | `后续验证清单` | `Follow-up Verification Checklist` |
| `compliance_checklist` | `报告合规自检表` | `Report Compliance Checklist` |

## Shared Field Dictionary

### Source Matrix

| Chinese | English |
|---|---|
| `关键 Claim` | `Key Claim` |
| `来源类型` | `Source Type` |
| `本报告用途` | `Use in This Report` |
| `证据层级` | `Evidence Tier` |
| `证据质量` | `Evidence Quality` |
| `来源状态` | `Source Status` |
| `独立验证状态` | `Independent Verification Status` |
| `限制和缺口处理` | `Limitations and Gap Handling` |

### Retrieval Gap Closure

| Chinese | English |
|---|---|
| `缺口` | `Gap` |
| `已尝试轮次和来源` | `Attempted Rounds and Sources` |
| `当前状态` | `Current Status` |
| `为什么仍重要` | `Why It Still Matters` |
| `未补齐原因` | `Unresolved Reason` |
| `下一步来源` | `Next Source` |

### Lifecycle And Seven Modules

| Chinese | English |
|---|---|
| `阶段结论` | `Lifecycle Phase` |
| `证据` | `Evidence` |
| `反证` | `Counterevidence` |
| `置信度` | `Confidence` |
| `结论` | `Conclusion` |
| `机制` | `Mechanism` |
| `研究含义` | `Research Implication` |
| `关键指标和后续验证` | `Key Metrics and Follow-up Verification` |

### Evidence Classification And Evidence Chain

| Chinese | English |
|---|---|
| `类型` | `Type` |
| `内容` | `Content` |
| `来源/依据` | `Source/Basis` |
| `子问题` | `Sub-question` |
| `事实` | `Fact` |
| `观点` | `Opinion` |
| `推断` | `Inference` |

Evidence tier, evidence quality, source status, and confidence use the translations above.

### Pressure Test And Verification

| Chinese | English |
|---|---|
| `质疑 ID` | `Challenge ID` |
| `视角` | `Perspective` |
| `目标 Claim/章节` | `Target Claim/Section` |
| `重要性` | `Materiality` |
| `核心质疑` | `Core Challenge` |
| `裁决` | `Resolution` |
| `证据/Gap` | `Evidence/Gap` |
| `报告改动` | `Report Change` |
| `复核状态` | `Reviewer Status` |
| `待验证问题` | `Verification Item` |
| `当前证据状态` | `Current Evidence Status` |
| `推荐来源` | `Recommended Source` |
| `优先级` | `Priority` |

## Route-Specific Heading Dictionary

Company research-plan summary fields use `项目 / Item`, `内容 / Content`, and `条件模块 / Conditional Modules`. Conditional module identifiers and `enabled` or `disabled` values remain unchanged in both languages.

| Chinese | English |
|---|---|
| `结论摘要` | `Conclusion Summary` |
| `问题拆解和议题树` | `Problem Decomposition and Issue Tree` |
| `证据链分析` | `Evidence Chain Analysis` |
| `趋势推演` | `Trend Outlook` |
| `报告摘要` | `Executive Summary` |
| `关键结论` | `Key Conclusions` |
| `核心指标总览` | `Core Metrics Overview` |
| `图表清单或图表占位` | `Exhibit List or Placeholders` |
| `目标公司/产品综合判断` | `Target Company/Product Overall Assessment` |
| `宏观环境分析` | `Macro Environment Analysis` |
| `中观行业分析` | `Meso Industry Analysis` |
| `多业务线中观拆分` | `Multi-Business Meso Breakdown` |
| `行业关键指标` | `Key Industry Metrics` |
| `微观公司/产品分析` | `Micro Company/Product Analysis` |
| `业务/产品组合分析` | `Business/Product Portfolio Analysis` |
| `竞争对手对比` | `Competitor Comparison` |
| `资本市场表现与估值预期变化` | `Capital-Market Performance and Valuation Expectation Changes` |
| `后续行动建议` | `Recommended Next Actions` |
| `方法论和数据来源说明` | `Methodology and Data Sources` |

Do not accept capitalization changes, hyphen changes, synonym substitutions, old v62 headings, dynamic target-name fields, or mixed-language headers as equivalent canonical contracts.
