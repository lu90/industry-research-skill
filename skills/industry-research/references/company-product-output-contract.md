# Company And Product Output Contract

Use this route when the user asks about a company, product, project, brand, business line, startup idea, competitive position, growth outlook, risk, or value in industry context. Listed-company share-price, valuation, expectation-gap, market-cap-repair, investability, or rise/fall questions use this route plus the capital-market conditional module.

This file owns the company trigger, opening, route orchestration, company depth delta, and conditional modules. Load `references/common-report-section-contract.md` for shared titles and fields. Load `assets/company-product-template.md` for the copyable skeleton. Load `references/capital-market-question.md` only when the capital-market trigger is active.

## Opening And Front Matter

Start with exactly one dynamic H1. The next nonempty line must be:

- Chinese: `## 0. 研报前置区`.
- English: `## 0. Research Front Matter`.

The front matter contains four substantive subsections: report summary, key conclusions, core metrics overview, and exhibit list or placeholders. It is followed by `目标公司/产品综合判断` or `Target Company/Product Overall Assessment`, which gives the full judgment on competitive position, capability, value, and constraints. These are distinct responsibilities and must not be empty duplicates.

## Route Orchestration

Use this order:

```text
dynamic H1
front matter
target company or product overall assessment
research scope and research trace
macro analysis
meso analysis
  conditional multi-business split
  one-sentence industry definition
  key industry metrics
  industry map with target position in the body
  lifecycle assessment
seven core modules analysis
micro analysis
SWOT
conditional portfolio analysis
competitor comparison
fact, opinion, and inference layers
conditional capital-market module
multi-perspective pressure test
risks, opportunities, and uncertainties
recommended next actions
methodology and data sources
follow-up verification checklist
report compliance checklist
fixed disclaimer
```

## Required Company Delta

- Macro, meso, and micro layers are required.
- `行业一句话定义`, `行业关键指标`, canonical `行业地图`, and lifecycle assessment are required inside meso analysis.
- The industry-map body must locate the target in the value chain and competitive structure. Do not put target position into a noncanonical heading.
- Seven modules remain independent subsections. Each uses the shared five-label contract.
- SWOT and competitor comparison are required. When reliable comparables do not exist, explain why, define an alternative benchmark, and disclose verification limits.
- Recommended next actions are target actions. They do not replace the shared evidence-verification checklist.
- Company reports keep the independent fact-opinion-inference chapter.
- Before drafting, every Plan Claim must pass v64 admission. Before registration, every Claim must bind to one exact analytical body span and same-Claim Evidence, with complete numeric coverage and a saved sampling audit.

## Company Depth Gate

For standard reports, each seven-module subsection should contain about 300-500 Chinese characters or equivalent English depth. Deep reports should contain about 600-1000. Evidence blocks need at least two concrete evidence points, source directions, or explicit gaps.

The front matter, macro, meso, micro, risk, pressure-test, methodology, and verification chapters must be substantive. A correct heading with token body text is a compressed-report failure.

## Conditional Modules

### Multi-Business Split

Enable `4.0 多业务线中观拆分` or `4.0 Multi-Business Meso Breakdown` when the target has multiple material businesses. It is mandatory for company-capital reports; a genuinely single-business listed company keeps the section and explains why no material split is needed. A normal single-business company report omits it.

### Portfolio Analysis

Enable portfolio analysis only when at least two material businesses, products, or resource-allocation objects exist. Otherwise omit the chapter. Never emit an empty BCG or portfolio matrix.

### Capital Market

Enable the complete capital-market chapter only for share-price, valuation, expectation-gap, market-cap-repair, investability, or rise/fall questions. A non-capital company report omits the entire chapter.

Company-capital reports must preserve `11.1-11.4` and the existing depth gate:

- `11.1` covers the price window, benchmark or sector comparison, catalysts, and evidence gaps.
- `11.2` covers revenue, margin or profitability, cash flow, orders or delivery, guidance, business mix, and fundamental-versus-expectation change.
- `11.3` covers valuation anchor, prior priced-in assumptions, expectation gap, rerating or derating mechanism, and indicators that must be proven again.
- `11.4` covers upside triggers, downside risks, scenarios, tracking indicators, and no-investment-advice framing.
- `5.4-5.7` remain visibly deeper than `5.1-5.3`.

## Route Failure Conditions

Rewrite before output when the draft:

- starts from section 1 instead of company front matter;
- omits macro, meso, micro, SWOT, competitor comparison, or the industry base;
- uses an empty or wrongly activated conditional module;
- omits `4.0` or any `11.1-11.4` subsection on a company-capital route;
- uses old shared titles or fields;
- collapses seven modules into a table;
- gives a target price, guaranteed return, or buy/sell instruction.

Resolve the active Skill root from the loaded `industry-research/SKILL.md`, then run `python -B "<skill-root>/scripts/report_contract_check.py" <report.md> --profile company` or `--profile company-capital` from the report workspace. Rerun with `--profile auto`, then run the v64 final fidelity checker against the matching Research Run before Manifest registration. All results must pass.
