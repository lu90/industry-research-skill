# Routing Sanity Check

Use this reference during request classification and before choosing a report template. It prevents two common regressions:

- Company/product or listed-company capital-market questions degrade into brief market comments.
- Pure industry questions are incorrectly forced into the company/product output contract.

Do not print this internal route check as a standalone section unless the user asks for methodology. Reflect the result through the report boundary, selected layers, and template choice.

Select the output language through `references/report-language.md` before applying the opening rule. Shared headings and fields come from `references/common-report-section-contract.md`. Chinese headings below are canonical examples; use their exact English counterparts when `output_language: en`.

## Runtime Route Matrix

| User intent | Template | Required layers | Conditional modules | Opening rule |
|---|---|---|---|---|
| Industry overview | `assets/industry-overview-template.md` | Macro + meso | Micro only for representative cases | Start with one H1, then the language-matched industry overview opening |
| Pure industry-specific question | `assets/specific-question-template.md` | Macro + meso + issue tree | Micro only if a specific company, product, project, or player is central to the question | Start with one H1, then the language-matched direct-answer heading |
| Company/product analysis | `assets/company-product-template.md` | Macro + meso + micro | Multi-business and portfolio only when triggered; capital-market off | Start with one H1, then the language-matched company front matter heading |
| Listed-company stock price, valuation, expectation gap, investability, market-cap repair, or rise/fall question | `assets/company-product-template.md` | Macro + meso + micro + capital-market | Multi-business split and capital-market required; portfolio only when triggered | Start with one H1, then the language-matched company front matter heading |

## Conditional Module Matrix

| Module | Enable rule | Disabled behavior |
|---|---|---|
| `multi_business_split` | Two or more material businesses, or any company-capital route | Omit for normal single-business company reports. Company-capital keeps it and explains whether a material split exists. |
| `portfolio_analysis` | Two or more material businesses, products, or resource-allocation objects | Omit the entire section. Do not output an empty BCG or portfolio matrix. |
| `capital_market` | Share price, valuation, expectation gap, market-cap repair, investability, or rise/fall is asked | Omit the entire chapter for non-capital company reports. |

## Pre-Draft Check

Before drafting, answer these internally:

1. What is the user really asking: industry overview, pure industry-specific question, company/product analysis, or listed-company capital-market question?
2. Which template is selected?
3. Which layers are selected: macro, meso, micro, capital-market?
4. Which of `multi_business_split`, `portfolio_analysis`, and `capital_market` are enabled, and why?
5. Which direct-answer rule applies, if any?

For company routes, persist the three decisions in the `### 2.1` research-plan table using the canonical `条件模块 / Conditional Modules` field. The declaration is part of the report contract, not an internal note, and must match both the selected route and the sections actually rendered.

If the request mentions a named company, product, brand, business line, listed ticker, valuation, stock price, market expectation, or rise/fall potential, do not treat it as a pure industry-specific question unless the company is only an example and not the target of analysis.

## Conflict Rules

- Listed-company capital-market questions override the pure industry-specific direct-answer rule.
- Company/product analysis overrides generic industry-specific routing.
- Explicit Short Answer Mode overrides standard report length only when the user explicitly asks for short, quick, brief, simple, one-paragraph, one-sentence, or no-detail output.
- Chat Report does not override template requirements.
- File Report changes delivery location only; it does not reduce report depth.

## Anti-Regression Checks

Use these checks before final output:

| Scenario | Must happen | Must not happen |
|---|---|---|
| Listed-company capital-market question | Use company/product output contract, include `11.1-11.4`, disclose primary-source gaps | Use a three-part quick-comment structure such as "why it fell / can it rise / what to watch" |
| Normal company/product question | Use company/product output contract, `0. 研报前置区`, required SWOT and competitor comparison | Add capital-market section when the user did not ask about stock price, valuation, expectation, investability, or rise/fall; emit empty conditional modules |
| Pure industry-specific question | Answer the question first, then include independent industry definition, map, issue tree, and canonical evidence chain | Force `0. 研报前置区` or micro company analysis when no company/product target exists |
| Industry overview | Build industry map, lifecycle judgment, and seven modules | Collapse into a short market summary without map and lifecycle |

All four standard/deep routes must end with the exact language-matched disclaimer. Short answers, Prompt Builder outputs, and visible research briefs do not use the formal report shell.

For company routes, also fail the review when the conditional-module declaration is missing, has any value other than `enabled` or `disabled`, conflicts with the profile, or conflicts with the presence of `4.0`, `8`, or `11`.

## Maintenance Regression Prompts

Use these prompts when forward-testing skill changes:

1. `请帮助我分析一下小米公司为什么最近股票跌这么多, 后面有可能涨起来吗?`
2. `分析一下蜜雪冰城在东南亚市场的增长前景.`
3. `为什么中国新能源汽车行业最近价格战这么激烈?`
4. `帮我做一份中国宠物食品行业研究.`

Passing one prompt is not enough to claim route stability. A change that fixes prompt 1 but breaks prompts 2-4 is not acceptable.
