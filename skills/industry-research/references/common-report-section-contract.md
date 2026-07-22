# Common Report Section Contract

Use this reference as the single authority for shared formal-report section semantics, canonical Chinese and English titles, field contracts, equivalent fulfillment, and relative ordering. Route output contracts decide openings and route-specific orchestration. Templates render the actual Markdown skeleton. Section numbers are not semantic identities.

This contract applies only to standard or deep formal reports. Prompt Builder Mode, Explicit Short Answer Mode, and visible research briefs do not use these shared formal-report validators.

## Shared Section Registry

| `section_id` | Canonical Chinese title | Canonical English title | Contract type | Applies to | Cardinality |
|---|---|---|---|---|---|
| `research_scope` | `研究边界` | `Research Scope` | visible section | all formal routes | required |
| `research_plan` | `研究计划摘要` | `Research Plan Summary` | visible subsection | all formal routes | required |
| `source_matrix` | `来源矩阵和证据质量` | `Source Matrix and Evidence Quality` | visible subsection | all formal routes | required |
| `retrieval_gap_closure` | `检索缺口闭环结果` | `Retrieval Gap Closure Results` | visible subsection | all formal routes | required |
| `industry_definition` | `行业一句话定义` | `One-Sentence Industry Definition` | visible section or subsection | all formal routes | required |
| `industry_map` | `行业地图` | `Industry Map` | visible section or subsection | all formal routes | required |
| `lifecycle` | `生命周期判断` | `Lifecycle Assessment` | visible section or subsection | all formal routes | required |
| `seven_modules` | `七个核心模块分析` | `Seven Core Modules Analysis` | visible section | all formal routes | required |
| `evidence_classification` | `事实, 观点和推断分层` | `Fact, Opinion, and Inference Layers` | analytical obligation | all formal routes | required |
| `pressure_test` | `多视角压力测试` | `Multi-Perspective Pressure Test` | visible section | all formal routes | required |
| `risk_uncertainty` | `风险, 机会和不确定性` | `Risks, Opportunities, and Uncertainties` | visible section | all formal routes | required |
| `verification_checklist` | `后续验证清单` | `Follow-up Verification Checklist` | visible section | all formal routes | required |
| `compliance_checklist` | `报告合规自检表` | `Report Compliance Checklist` | visible section | all formal routes | required |

The checker accepts only these v63 canonical titles and fields. Do not add old-title aliases, legacy profiles, dual-read logic, or warning-only fallback.

## Shared Field Contracts

### Source Matrix And Evidence Quality

Use this exact field order:

```text
关键 Claim | 来源类型 | 本报告用途 | 证据层级 | 证据质量 | 来源状态 | 独立验证状态 | 限制和缺口处理
Key Claim | Source Type | Use in This Report | Evidence Tier | Evidence Quality | Source Status | Independent Verification Status | Limitations and Gap Handling
```

- `关键 Claim` uses `` `{claim_id}`: reader-facing Claim ``. Each row contains exactly one stable `claim_id` from `plan.json` so its evidence tier, access status, and independence status can be checked against Evidence Ledger records for that same Claim.
- `证据层级` is `primary`, `near-primary`, `secondary`, or `weak` and describes source directness.
- `证据质量` is `high`, `medium`, or `low`. It is a reader-view judgment derived from freshness, definition match, completeness, and support strength. It does not replace Evidence Ledger fields.
- `来源状态` must reflect the final Evidence Ledger `access_status`: `obtained`, `public-but-technical-failure`, `login-required`, `paid-database`, `API-key-required`, `blocked`, `not-found`, or `definition-mismatch`.
- `独立验证状态` must reflect Evidence Ledger independence, not page count: `independently_verified`, `same-origin-cross-check`, `single-source-primary`, `secondary-only`, or `unresolved-conflict`.
- `限制和缺口处理` records limitations, alternatives, residual gaps, and the next source route.

Each row uses exactly one canonical evidence tier, evidence quality, and source status. Do not combine values such as `primary/near-primary`, replace them with prose, or put Gap status into Source Status. When several sources support one row, select the tier that best describes the evidence directly supporting the Claim and explain the mix under source type or limitations.

The table must be compressed from the final Plan and Controller-merged Evidence Ledger. A report must not claim that evidence was obtained or independently verified when the Run does not support that state.

### Retrieval Gap Closure Results

Use this exact field order:

```text
缺口 | 已尝试轮次和来源 | 当前状态 | 为什么仍重要 | 未补齐原因 | 下一步来源
Gap | Attempted Rounds and Sources | Current Status | Why It Still Matters | Unresolved Reason | Next Source
```

The `Gap` cell uses `` `{gap_id}`: reader-facing missing item ``. Each unresolved row contains exactly one `gap_id` from final `gaps.json`; copy its current status, unresolved reason, and next source route into the matching row. The section consumes the final `gaps.json` and Controller-merged `evidence.jsonl`. Worker summaries may support attempted-action traceability but cannot authorize obtained evidence, independent verification, or final Gap status. Up to three Engine-authorized closure rounds are allowed; early stop is valid when evidence is sufficient or an access barrier is established. The report must not invent unused rounds.

### Lifecycle Assessment

Every route uses these exact labels:

```text
阶段结论 / Lifecycle Phase
证据 / Evidence
反证 / Counterevidence
置信度 / Confidence
研究含义 / Research Implication
```

The `研究含义` body must explicitly name its object: the industry, the user question, or the target company or product.

### Seven Core Modules Analysis

Keep seven independent subsections: feasibility, scalability, defensibility, profitability, valuation, external factors, and prosperity. Every subsection uses these exact labels:

```text
结论 / Conclusion
证据 / Evidence
机制 / Mechanism
研究含义 / Research Implication
关键指标和后续验证 / Key Metrics and Follow-up Verification
```

Route and lifecycle weighting belong in the body, not in a different main heading. Company and capital-market depth deltas remain in the company route contract and checker.

### Fact, Opinion, And Inference

Independent classification tables use:

```text
类型 | 内容 | 来源/依据 | 证据层级 | 证据质量 | 来源状态 | 置信度
Type | Content | Source/Basis | Evidence Tier | Evidence Quality | Source Status | Confidence
```

Evidence tier, evidence quality, and source status use the same single-value enums as the source matrix.

Overview and company routes require the independent visible section. The specific route fulfills the same obligation through `证据链分析` or `Evidence Chain Analysis` with:

```text
子问题 | 结论 | 事实 | 观点 | 推断 | 来源/依据 | 证据层级 | 证据质量 | 来源状态 | 置信度
Sub-question | Conclusion | Fact | Opinion | Inference | Source/Basis | Evidence Tier | Evidence Quality | Source Status | Confidence
```

Do not add a duplicate fact-opinion-inference section to the specific route.

### Multi-Perspective Pressure Test

Use:

```text
视角 | 质疑 | 为什么重要 | 需要验证
Perspective | Challenge | Why It Matters | Verification Needed
```

Minimum perspective count and depth are controlled by the compliance gate and checker.

### Risks, Opportunities, And Uncertainties

The body must distinguish fact risk, assumption risk, data gap, upside opportunity, and trigger condition. Company reports must additionally separate industry-structure drivers from target-specific drivers.

### Follow-up Verification Checklist

Use:

```text
待验证问题 | 当前证据状态 | 为什么重要 | 推荐来源 | 优先级
Verification Item | Current Evidence Status | Why It Matters | Recommended Source | Priority
```

Company `后续行动建议` or `Recommended Next Actions` is a route-specific action chapter and does not fulfill this evidence-verification obligation.

## v64 Claim Fidelity Contract

The reader-facing section registry remains unchanged. v64 adds internal audit artifacts rather than new report chapters.

Every final Plan Claim must have exactly one record in `research_runs/<run_id>/report-claims.json` with `claim_id`, `claim_status`, `assertion_kind`, `report_section`, `report_span`, `evidence_refs`, `numeric_checks`, `numeric_exclusions`, `verification_notes`, and `manual_review_required`. Only `supported` and `refuted` are allowed in this file.

Use this top-level shape:

```json
{
  "schema_version": "v64",
  "run_id": "<run_id>",
  "report_path": "reports/<run_id>.md",
  "claims": []
}
```

Each Claim binding uses this complete interface:

| Field | Rule |
|---|---|
| `claim_id` | One ID from final `plan.json`; every Plan Claim appears exactly once |
| `claim_status` | `supported` or `refuted`, matching pre-report calculation |
| `assertion_kind` | `fact`, `external-opinion`, `inference`, `causal`, or `forecast` |
| `report_section` | Exact canonical heading text without Markdown hashes |
| `report_span` | Shortest complete body statement, appearing exactly once |
| `evidence_refs` | One or more uniquely locating Evidence references |
| `numeric_checks` | One record for every Claim-number token that is checked |
| `numeric_exclusions` | One record for every date, identifier, section number, or non-Claim number |
| `verification_notes` | Nonempty scope, definition, inference, or review note |
| `manual_review_required` | Boolean; true whenever any numeric mode is `manual` |

Each Evidence reference contains exactly the locating values `source_id`, `document_url`, `page_or_section`, `relation`, and `evidence_span_sha256`. Calculate the hash from Unicode-NFKC normalized `evidence_span` with whitespace collapsed to single spaces.

Each numeric check contains `reported_value`, `mode`, `evidence_values`, `unit`, `currency`, `reporting_period`, and a nonempty `review_note`. Add `operation` for `derived` or `converted`, and add `tolerance` for floating-point or rounded results. Allowed operations are `identity`, `sum`, `difference`, `ratio`, `share`, `percentage-change`, and `decimal-scale`. Operand order is first-minus-second for `difference`, numerator then denominator for `ratio` and `share`, and old value then new value for `percentage-change`. `share` and `percentage-change` return percentage points. `converted` permits only `decimal-scale`; exchange rates, adjusted prices, reconstructed tables, and complex statistics use `manual`.

Each numeric exclusion contains `value`, one reason from `date`, `identifier`, `section-number`, or `non-claim-context`, and a nonempty `review_note`. Repeated number tokens require repeated check or exclusion records so coverage remains exact.

Assertion kinds have different review duties:

| `assertion_kind` | Minimum duty |
|---|---|
| `fact` | Match period, geography, unit, currency, definition, and support or refute relation |
| `external-opinion` | Name the opinion holder and source; do not rewrite the opinion as objective fact; disclose incentives and limits |
| `inference` | Cite at least one admitted factual basis and record the reasoning bridge, confidence, and disconfirmation condition |
| `causal` | Use multiple factual bases or explicitly lower confidence; distinguish correlation, sequence, and alternative explanations |
| `forecast` | State assumptions and observation horizon; keep future statements distinct from occurred facts and name verification indicators |

The deterministic checker treats machine-verifiable shape, identity, exact binding, and numeric conflicts as errors. Complex semantic duties remain warning and sampling-review obligations rather than automated proof.

- `report_span` is the shortest complete reader-visible statement that represents the Claim. It appears exactly once inside the named canonical analytical section.
- A source matrix, Gap table, compliance checklist, methodology note, or disclaimer cannot be the canonical `report_span` location.
- Each Evidence reference uses `source_id`, `document_url`, `page_or_section`, `relation`, and the SHA-256 of normalized `evidence_span`; the combination must uniquely locate one obtained Evidence record for the same Claim.
- A refuted Claim must be written as denied, narrowed, or unsupported. It cannot preserve the original support wording.
- Every numeric token in `report_span` is covered exactly once by `numeric_checks` or `numeric_exclusions`. Allowed automatic modes are direct values, fixed safe derived operations, and explicit decimal scaling. All other calculations use manual review.
- Save `truthfulness-audit.md` inside the Run and sample at least three Claims, or all Claims when fewer than three exist. The audit must include every `manual_review_required` Claim and state whether the reviewer is human or `agent-self-check`.

Start the audit with these machine-readable lines, then add the per-Claim review notes:

```text
# Truthfulness Audit

- reviewer_type: human|agent-self-check
- reviewed_claim_ids: claim-a, claim-b, claim-c

## claim-a

- atomicity: <nonempty review>
- evidence_relation: <nonempty review>
- report_fidelity: <nonempty review>
- numeric_scope: <nonempty review>
- inference_limits: <nonempty review>
- counterevidence: <nonempty review>
```

Repeat the H2 review block for every ID in `reviewed_claim_ids`. For every sampled Claim, review atomicity, Evidence support or refutation, body paraphrase fidelity, numbers and units, inference limits, and visible counterevidence. An Agent may complete this review only as `agent-self-check`.

These internal artifacts do not alter v61 Evidence fields, v62 Run schemas, or the v63 reader-facing heading contract.

## Route Rendering And Equivalent Fulfillment

| Route | Industry definition | Industry map | Lifecycle | Evidence classification |
|---|---|---|---|---|
| overview | H2 opening | H2 | H2 | independent H2 section |
| specific | H2 after research trace | H2 before issue tree | H2 after evidence chain | equivalent fulfillment through canonical evidence-chain fields |
| company | H3 inside meso analysis | H3 with target position in the body | H3 | independent H2 section |

The map must precede lifecycle and seven-module analysis. Company target position is required content under the canonical `行业地图` title, not part of a different heading.

## Shared Closeout Ordering

All routes preserve this relative order:

```text
pressure_test
risk_uncertainty
verification_checklist
compliance_checklist
fixed disclaimer
```

Company recommended actions and methodology may appear between risk and verification. The compliance checklist must remain immediately before the fixed language-matched disclaimer.

## Route Skeletons

### Overview

`industry_definition -> research_scope and trace -> industry_map -> lifecycle -> seven_modules -> trend_outlook -> evidence_classification -> pressure_test -> risk_uncertainty -> verification_checklist -> compliance_checklist -> disclaimer`

### Specific

`direct_answer -> conclusion_summary -> research_scope and trace -> industry_definition -> industry_map -> issue_tree -> evidence_chain -> lifecycle -> seven_modules -> pressure_test -> risk_uncertainty -> verification_checklist -> compliance_checklist -> disclaimer`

### Company

`front_matter -> overall_assessment -> research_scope and trace -> macro -> meso with conditional multi-business split, industry_definition, metrics, industry_map, lifecycle -> seven_modules -> micro -> SWOT -> conditional portfolio -> competitors -> evidence_classification -> conditional capital_market -> pressure_test -> risk_uncertainty -> recommended_actions -> methodology -> verification_checklist -> compliance_checklist -> disclaimer`

## Conditional Modules

| Module | Enable when | Disabled behavior |
|---|---|---|
| `multi_business_split` | the target has multiple material businesses, or the route is company-capital | Single-business company reports may omit it. Company-capital must keep it and explain whether a material split exists. |
| `portfolio_analysis` | at least two material businesses, products, or resource-allocation objects exist | Omit the section. Do not render an empty BCG or portfolio matrix. |
| `capital_market` | the question concerns share price, valuation, expectation gap, market-cap repair, investability, or rise/fall | Omit the entire chapter for non-capital company reports. |

The internal research brief and routing sanity check decide module activation. The checker enforces the selected explicit or auto-detected profile and validates any rendered conditional section.

Company and company-capital reports copy the internal decision into the `研究计划摘要` or `Research Plan Summary` table using one row:

```text
条件模块 | multi_business_split=enabled|disabled; portfolio_analysis=enabled|disabled; capital_market=enabled|disabled
Conditional Modules | multi_business_split=enabled|disabled; portfolio_analysis=enabled|disabled; capital_market=enabled|disabled
```

Use one concrete state for every module. The checker rejects a declaration that conflicts with the rendered sections or selected profile.
