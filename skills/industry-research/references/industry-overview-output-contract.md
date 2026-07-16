# Industry Overview Output Contract

Use this route when the user wants a broad understanding of an industry, market, sector, track, business category, or opportunity space rather than one narrow causal question or one target company or product.

This file owns only the overview route trigger, opening, orchestration, and overview-specific delta. Load `references/common-report-section-contract.md` for all shared section titles, fields, equivalent fulfillment, and closeout ordering. Load `assets/industry-overview-template.md` for the copyable Markdown skeleton.

## Opening

Start with exactly one dynamic H1. The next nonempty line must be the language-matched overview discriminator:

- Chinese: `## 1. 行业一句话定义`.
- English: `## 1. One-Sentence Industry Definition`.

Do not use company front matter or the specific-route direct-answer opening.

## Route Orchestration

Use this order:

```text
dynamic H1
industry definition opening
research scope and research trace
industry map
lifecycle assessment
seven core modules analysis
trend outlook
fact, opinion, and inference layers
multi-perspective pressure test
risks, opportunities, and uncertainties
follow-up verification checklist
report compliance checklist
fixed disclaimer
```

The exact v63 numbered skeleton is in `assets/industry-overview-template.md`. Section numbers are route rendering, not shared semantic identities.

## Overview-Specific Delta

- `趋势推演` or `Trend Outlook` is required after seven-module analysis.
- Trend outlook must connect future direction to evidence, mechanisms, leading indicators, and explicit trigger conditions.
- Fact, opinion, and inference classification is an independent visible section on this route.
- Macro and meso layers are required. Micro analysis is optional and only supports representative cases.

## Route Failure Conditions

Rewrite before output when the draft:

- does not open with the overview discriminator;
- lacks the industry map, lifecycle assessment, or seven independent modules;
- omits trend outlook;
- substitutes an old v62-or-earlier shared heading or field;
- puts risk before pressure testing or omits the executable verification checklist;
- compresses a standard or deep report into a market summary.

Resolve the active Skill root from the loaded `industry-research/SKILL.md`, then run `python -B "<skill-root>/scripts/report_contract_check.py" <report.md> --profile overview` from the report workspace and rerun it with `--profile auto` before delivery. Both profiles must return the same result.
