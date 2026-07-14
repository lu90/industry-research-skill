# Report Depth Rubric

Use this file before final output for standard and deep reports. It converts "content depth" into a repeatable self-check. Use it with `references/section-depth-playbook.md`. Do not output the rubric unless the user explicitly asks for quality scoring.

## Scoring Dimensions

Score each major analytical section from 0 to 2 on five dimensions:

| Dimension | 0 | 1 | 2 |
|---|---|---|---|
| Specific conclusion | Generic label or no conclusion | Conclusion exists but is broad | Specific, falsifiable, and tied to the question |
| Evidence density | No evidence or only vague claims | 1 evidence point or only secondary evidence | 2+ evidence points, source pointers, or named evidence gaps |
| Mechanism clarity | Lists factors without causality | Some causal explanation | Clear causal chain from evidence to conclusion |
| Implication | No industry/target implication | Implication is generic | Concrete implication for industry, target, metric, risk, or decision |
| Uncertainty discipline | Ignores uncertainty | Mentions uncertainty vaguely | Names missing source, confidence, and next verification step |

Maximum section score: 10.

## Minimum Thresholds

Before final output:

- Standard report major analytical sections should score at least 7/10.
- Deep report major analytical sections should score at least 8/10.
- Seven-module subsections should score at least 7/10 in standard reports and 8/10 in deep reports.
- Capital-market priority sections and section `11` should score at least 8/10 in standard listed-company capital-market reports.

If a section scores below threshold, rewrite the section before final output. Do not lower the threshold because the report is delivered in chat.

## Major Sections To Score

For industry overview reports, score:

- Lifecycle judgment.
- Seven modules.
- Trend projection.
- Risk and opportunity.
- Fact/opinion/inference section.

For industry-specific question reports, score:

- Direct answer.
- Issue tree.
- Evidence chain.
- Seven modules.
- Risk and uncertainty.

For company/product reports, score:

- Macro analysis.
- Meso industry analysis.
- Seven modules.
- Micro company/product analysis.
- Fact/opinion/inference section.
- Capital-market section when applicable.
- Pressure test.

## Automatic Rewrite Triggers

Rewrite a section before final output when any of these appear:

- The section is mostly a table with little explanatory prose.
- The section repeats the same claim in different wording.
- Evidence is mentioned but not connected to the conclusion.
- The mechanism uses generic phrases such as "this will affect growth" without explaining how.
- Evidence gaps are stated without naming the missing source and verification step.
- A checklist row claims the section passed while the body lacks the required analysis.
- The section fails the anti-thinness gate in `references/section-depth-playbook.md`.

## Checklist Wording

In the final visible compliance checklist, mark depth as passed only when the relevant sections meet the threshold. Do not use "partially passed" in a final standard or deep report. If the score is below threshold, rewrite first, then output.
