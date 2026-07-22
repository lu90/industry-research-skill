# Industry-Specific Question Output Contract

Use this route for a pure industry question about a cause, phenomenon, trend, opportunity, risk, competition, price war, policy impact, profitability, lifecycle, or future direction when no company or product is the target of analysis.

This file owns only the specific-question trigger, opening, orchestration, and route-specific delta. Load `references/common-report-section-contract.md` for shared titles and fields. Load `assets/specific-question-template.md` for the copyable Markdown skeleton.

## Opening

Start with exactly one dynamic H1. The next nonempty line must be:

- Chinese: `## 1. 直接回答`.
- English: `## 1. Direct Answer`.

The direct answer must be substantive and explain the conclusion, evidence, and mechanism. Do not use company front matter. A named company used only as an example does not change the route; a named company used as the analytical target does.

## Route Orchestration

Use this order:

```text
dynamic H1
direct answer
conclusion summary
research scope and research trace
one-sentence industry definition
industry map
problem decomposition and issue tree
evidence chain analysis
lifecycle assessment
seven core modules analysis
multi-perspective pressure test
risks, opportunities, and uncertainties
follow-up verification checklist
report compliance checklist
fixed disclaimer
```

## Specific-Question Delta

- `直接回答`, `结论摘要`, `问题拆解和议题树`, and `证据链分析` are required route-specific chapters.
- The independent industry-definition chapter is required before the map.
- The template is self-contained. Do not instruct the writer to look at the overview template for the boundary, map, or pressure-test body.
- The canonical evidence-chain table is the equivalent fulfillment of the shared fact-opinion-inference obligation. Do not add a duplicate classification chapter.
- Macro, meso, and issue-tree layers are required. Micro is conditional on a company, product, project, or player being central to the causal mechanism without becoming the report target.
- The visible evidence-chain table does not replace v64 internal Claim binding. Every Plan Claim still needs one exact body `report_span`, same-Claim Evidence references, numeric coverage, and sampling review.
- Run the v65 Pressure Test against the working draft, close the Challenge Ledger, rewrite the direct answer and affected analysis, and rerun affected v64 admission and binding before final fidelity audit.

## Route Failure Conditions

Rewrite before output when the draft:

- delays the direct answer behind background chapters;
- omits the industry definition, map, issue tree, or evidence chain;
- lacks any canonical fact, opinion, inference, source, evidence-quality, source-status, or confidence field in the evidence chain;
- uses an overview or company opening in addition to the direct-answer opening;
- uses old shared titles or fields;
- uses the old four-column Pressure Test, omits a core reviewer role, or leaves any pending or open/disputed high Challenge;
- reduces the answer to a short commentary without an explicit short-answer request.

Resolve the active Skill root from the loaded `industry-research/SKILL.md`, then run `python -B "<skill-root>/scripts/report_contract_check.py" <report.md> --profile specific` from the report workspace and rerun it with `--profile auto` before delivery. Run the v64 final fidelity checker against the matching Research Run before Manifest registration. All results must pass.
