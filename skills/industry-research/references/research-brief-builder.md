# Research Brief Builder

Use this file before drafting any standard or deep report. It converts the user's natural-language request into an executable research brief so the report route, template, output language, source plan, and depth contract are locked before writing.

## When To Use

Use for every standard or deep report, including:

- Industry overview reports.
- Industry-specific question reports.
- Company/product reports.
- Listed-company stock price, valuation, expectation gap, investability, market-cap repair, or rise/fall potential reports.

Do not use as a visible report chapter unless the user explicitly asks to see the research brief, prompt, requirement summary, or reusable instruction, or the visible brief gate below is triggered.

## Build The Internal Brief

Before collecting evidence or drafting, write an internal brief with these fields:

| Field | Required content |
|---|---|
| Original request | Copy the user's exact request or concise paraphrase. |
| Inferred intent | Industry overview, industry-specific question, company/product analysis, or listed-company capital-market question. |
| Report depth | Explicit short answer, standard report, or deep report. Default to standard when short answer is not explicitly requested. |
| Delivery mode | Workspace Report File, Chat Report, or File Report, following `references/report-output-modes.md`. |
| Output language | `zh` or `en`, selected through `references/report-language.md`. |
| Target | Industry, company, product, ticker, business line, geography, and time horizon. |
| Core questions | 3-7 research questions the report must answer. |
| Required layers | Macro, meso, micro, and capital-market layer when applicable. |
| Required template | Exact asset template to use. |
| Required references | Exact reference files to read before writing. |
| Conditional modules | Capital-market section, multi-business meso split, SWOT, BCG, or other conditional sections. |
| Source priority | Primary and near-primary sources to attempt first, plus secondary sources allowed only as supplementary evidence. |
| Depth contract | Target character range and section-level depth targets from `references/output-format.md`. |
| Rewrite triggers | Missing skeleton sections, compressed seven modules, missing source matrix, missing compliance checklist, or weak evidence not marked. |

## Pre-Output Brief Check

Before final output, confirm internally that the brief can answer these questions:

1. What is the request type, and why is it not a lower-specificity route?
2. Is the report short, standard, or deep, and what phrase from the user triggered that depth?
3. Which template and output language are mandatory, and what H1, language-matched route opening, and disclaimer must the report use?
4. Which references were required before writing?
5. Which conditional modules are required, especially capital-market `11.1-11.4` or multi-business `4.0`?
6. What is the section-level depth contract?
7. Which primary or near-primary sources should be attempted first?
8. What would force a rewrite before final output?

If any answer is missing, pause drafting, complete the internal brief, then continue. Do not expose this internal check unless the user asks for the brief or prompt.

## Depth Calibration

Use the brief to calibrate depth before writing the report:

- A section is too thin if it only repeats the conclusion, lists factors without mechanism, or uses a table as the main analysis.
- A section is too thin if it mentions evidence but does not explain how the evidence changes the conclusion.
- A section is too thin if it uses generic phrases such as "need further verification" without naming the missing source and the next verification step.
- For standard listed-company capital-market reports, section `11` must be a substantive analysis chapter, not a three-row scenario table.
- For deep reports, the brief must explicitly name which modules deserve extra depth and why.

Thin sections must be rewritten before the final compliance checklist is marked as passed.

For company and company-capital reports, copy the three executable conditional decisions into the visible research-plan summary using `multi_business_split`, `portfolio_analysis`, and `capital_market`, each set to `enabled` or `disabled`. This exposes the decision to the report checker without changing the Research Run schema.

## Visible Brief Gate

Use visible brief mode before drafting when either condition is true:

- The user asks to organize the requirement, define the research task, generate a reusable prompt, prepare instructions for another agent, or confirm the research scope first.
- The request is a standard or deep report request, but missing boundaries would materially change the route, template, source plan, or depth contract.

Visible brief mode must not become a short answer. It is a pre-report contract. Output a compact requirement brief with these fields:

| Field | Required content |
|---|---|
| Report objective | The decision or understanding the report should support. |
| Recommended route | Industry overview, industry-specific question, company/product, or listed-company capital-market report. |
| Required depth | Standard or deep report, with target character range. |
| Output language | Selected report language and the signal used to select it. |
| Research boundaries | Geography, time horizon, industry scope, included items, excluded items, and assumptions. |
| Core questions | 3-7 questions the final report must answer. |
| Mandatory template | Exact asset template, dynamic H1 rule, required route opening, and fixed disclaimer. |
| Mandatory sections | Required section list, including conditional modules such as `11.1-11.4`. |
| Source plan | Primary, near-primary, and secondary source priorities. |
| Rewrite triggers | Missing skeleton, thin seven modules, weak section `11`, missing source matrix, or missing compliance checklist. |

After the visible brief, either:

- ask up to 3 high-impact confirmation questions when the answer would change the report route or scope; or
- provide a ready-to-use prompt from `assets/research-prompt-template.md` when the user asked for a prompt.

If the user says to proceed after the visible brief, write the final report from the locked brief and do not downgrade it into a summary.

## Routing Rules

Use the brief to make routing explicit:

- If the request names a company, product, brand, project, or business line, route to company/product analysis.
- If the request asks about a listed company's stock price, valuation, market expectation, investability, market-cap repair, or rise/fall potential, route to company/product analysis plus the capital-market module.
- If the request asks a pure industry phenomenon question without a target company/product, route to industry-specific question.
- If the request names only a sector or market and asks for understanding, route to industry overview.

The brief overrides casual wording. A vague question such as "why did Xiaomi fall so much" must not become a quick market comment when the target is a listed company.

## Prompt Builder Mode

If the user explicitly asks to "generate a prompt", "整理需求", "输出 prompt", "给另一个 agent 用", "先生成研究 brief", "帮我设置目标", or "把需求梳理清楚", output a reusable prompt instead of the final report.

Use `assets/research-prompt-template.md` as the output shape. Fill it with the inferred route, output language, required references, required sections, depth targets, and evidence rules. Translate the complete visible prompt through `references/report-language.md`.

The generated prompt must be executable as a report contract. It must name the output language, mandatory template, dynamic H1 rule, language-matched route opening, fixed disclaimer, required section checklist, target depth, section-level depth expectations, primary-source-first evidence rules, and rewrite-before-output triggers. For listed-company capital-market questions, it must explicitly require language-matched `11.1-11.4`, `4.0`, company front matter, independent `5.1-5.7`, multi-perspective pressure testing, and the final report compliance checklist.

If important boundaries are missing and would materially change the report, ask at most 1-3 high-impact questions. If the user wants to proceed, state assumptions in the prompt and continue.

## Internal Brief Example

User request:

```text
请帮助我调研一下小米公司为什么股价跌了这么多呢?
```

Internal brief:

```text
Inferred intent: Listed-company capital-market question.
Report type: Standard company/product capital-market report.
Output language: Chinese, selected from the user's request.
Target: Xiaomi Group, 1810.HK.
Core questions:
1. What were the direct stock-price catalysts?
2. Did fundamentals change or did expectations change?
3. How did valuation logic and market expectation gap shift?
4. Which upside triggers and downside risks should be tracked?
Required template: assets/company-product-template.md.
Required references: company-product-output-contract, capital-market-question, primary-source-first, output-format, report-compliance, layered-analysis.
Required shell: one dynamic Chinese H1, then ## 0. 研报前置区, with the exact Chinese disclaimer as the final line.
Conditional sections: 4.0 multi-business meso split, 11.1-11.4 capital-market analysis.
Depth contract: 12000-18000 Chinese characters; seven modules independent; priority modules and section 11 expanded.
Rewrite triggers: missing or duplicate H1, wrong route opening, missing 0, 2.1-2.3, 5.1-5.7, 11.1-11.4, 12, 17, paraphrased disclaimer, or seven modules compressed into a table.
```

Do not output this internal brief unless the user explicitly requests it.
