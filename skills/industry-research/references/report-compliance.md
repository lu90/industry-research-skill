# Report Compliance Gate

Run this gate before delivering any standard or deep formal report. This file aggregates shared gates and route deltas. It does not redefine shared section bodies or reproduce complete route skeletons.

## Shared Gates

### Shell And Language

- Exactly one dynamic H1 is the first nonempty line.
- The next nonempty line is the language-matched route opening.
- All reader-facing contract headings and fields use one language.
- The language-matched fixed disclaimer is the final nonempty line and appears exactly once.

### Shared Structure

- Load `references/common-report-section-contract.md` and use every applicable canonical shared title and field.
- Industry map precedes lifecycle assessment and seven-module analysis.
- Pressure test precedes risks, opportunities, and uncertainties.
- The verification checklist follows risk and any route-specific action or methodology chapters.
- The compliance checklist appears immediately before the disclaimer.
- No v62-or-earlier shared title, field alias, legacy profile, or warning-only fallback is present.

### Research Trace And Run Binding

- Research scope includes geography, time horizon, industry definition, inclusions, exclusions, and assumptions.
- Research plan, source matrix, and retrieval-gap closure results are substantive.
- Every source-matrix row names exactly one `claim_id` from final `plan.json`; its evidence tier, source status, and independence status match Evidence Ledger records for that same Claim.
- Every unresolved Gap row names exactly one `gap_id`; its status, unresolved reason, and next source match that same entry in final `gaps.json`.
- Attempted rounds and sources are traceable to Run actions. Unused rounds are not invented.
- A formal report is generated only for a `completed` Run with `engine_report_permission: true`.
- Report filename stem, `run_id`, Manifest `report_path`, and `report_status: generated` form one unique association.
- `challenges.json` exists for a generated report, shares the Run ID, contains all four core reviewer roles, and passes Challenge schema and cross-artifact validation.

### Claim Admission And Fidelity

- Every Plan Claim has one deterministic pre-report status. Only `supported` and `refuted` Claims enter a formal report.
- `conflicted`, `gapped`, or `orphaned` Claims deny formal-report permission. The Run returns a Summary, conflicts, and Gaps instead of a formal report.
- `report-claims.json` contains exactly one canonical binding for every Plan Claim and no unknown Claim IDs.
- Every Evidence reference uniquely locates obtained Evidence for the same Claim and meets that Claim's required evidence tier.
- Every `report_span` appears exactly once in its named analytical section and does not bind to source matrices, methodology, compliance, or disclaimer boilerplate.
- Refuted Claims are visibly denied, narrowed, or described as unsupported.
- Every numeric token is checked or explicitly excluded. Unsupported calculations use `manual` and set `manual_review_required: true`.
- `truthfulness-audit.md` reviews at least three Claims, or all Claims when fewer than three exist, includes every manual Claim, and truthfully declares `human` or `agent-self-check`.
- Manifest report registration happens only after report structure and final fidelity checks pass.
- Pressure Test report changes invalidate affected v64 admission, binding, and fidelity results until those checks are rerun against the revised report.

### Pressure Test Closure

- The working draft is reviewed before Manifest formal registration.
- Only retrieval Challenges create or reuse a same-Claim Gap and enter the Deep Search Protocol.
- No Challenge remains `pending`; no high Challenge remains `open` or `disputed`.
- Every high Challenge is closed by its original reviewer. Medium and low Challenges may be closed by the Organizer.
- `confirmed` and `partially_valid` Challenges produce concrete report changes. High unresolved Challenges downgrade or withdraw confidence and disclose the limitation.
- The report discloses `review_mode` and uses the canonical nine-column summary.
- Every required reader-facing row matches `challenges.json` for ID, target, materiality, challenge, resolution, Evidence or Gap, report change, and reviewer status.

### Shared Analytical Quality

- Lifecycle assessment includes phase, evidence, counterevidence, confidence, and research implication.
- Seven modules remain seven independent subsections with all five canonical blocks.
- Overview and company routes include an independent fact-opinion-inference section. Specific fulfills this through the canonical evidence chain.
- Pressure testing includes at least industry expert, investment researcher, policy or regulatory, and operator or entrepreneur perspectives for every formal route.
- Risks distinguish fact risk, assumption risk, data gap, upside opportunity, and trigger condition.
- Verification items include current evidence status, importance, recommended source, and priority.
- Missing evidence is disclosed, not invented.

### Depth And Delivery

- Apply `references/output-format.md`, `references/section-depth-playbook.md`, and `references/report-depth-rubric.md` without reducing existing thresholds.
- A heading with token body text fails even when the skeleton is complete.
- Workspace Report File is the default in writable environments. The full report is stored under `reports/`; chat returns only the path, title, short summary, and checker status.
- Existing reports are context only and do not trigger summary degradation unless the user explicitly asks to summarize, review, compare, condense, or continue one.

## Overview Delta

- Opening is the industry-definition heading.
- Trend outlook is required after the seven modules.
- The independent fact-opinion-inference section is required.
- Macro and meso analysis are present; micro is optional representative-case support.

## Specific-Question Delta

- Opening is the direct-answer heading and the answer is substantive.
- Conclusion summary, independent industry definition, issue tree, and evidence chain are required.
- The evidence chain includes all canonical fact, opinion, inference, source, evidence-quality, source-status, and confidence fields.
- Do not add a duplicate fact-opinion-inference chapter.

## Company Delta

- Opening is company front matter with substantive `0.1-0.4`.
- Overall assessment, macro, meso, micro, SWOT, competitor comparison, recommended actions, and methodology are required.
- The meso chapter contains the industry definition, key metrics, canonical map with target position in the body, and lifecycle assessment.
- Each seven-module evidence block has at least two evidence points, source directions, or explicit gaps.
- Company risk analysis separates industry-structure drivers from target-specific drivers.
- Conditional modules follow the single activation matrix in `references/common-report-section-contract.md` and `references/routing-sanity-check.md`.
- The research-plan summary declares all three conditional-module states, and each declaration matches the rendered sections and selected profile.

## Company-Capital Delta

- The multi-business split is required, including a no-material-split explanation for a genuine single-business target.
- The complete capital-market chapter and `11.1-11.4` are required.
- `5.4-5.7` are visibly deeper than `5.1-5.3`.
- The capital chapter passes paragraph-density and concept gates for price window, benchmark, fundamentals, valuation anchor, expectation gap, rerating or derating, triggers, downside risks, scenarios, tracking indicators, and no-investment-advice framing.
- No target price, buy or sell instruction, or guaranteed return is present.

## Conditional Module Failures

- A company-capital report without multi-business split fails.
- A non-capital company report with a capital-market chapter fails.
- A rendered multi-business or portfolio section with empty or token content fails.
- A single-business company report should omit portfolio analysis rather than render an empty matrix.

## Runtime And Maintenance Commands

For an installed Skill, resolve `<skill-root>` from the loaded `industry-research/SKILL.md`. Run report commands from the report workspace so `--repo-root .` points to the workspace that contains `reports/` and `research_runs/`. Repository maintainers may substitute `skills/industry-research` for `<skill-root>` when running from this repository root.

```text
python -B "<skill-root>/scripts/report_contract_check.py" --self-test
python -B "<skill-root>/scripts/report_contract_check.py" <report.md> --profile <profile> --language auto
python -B "<skill-root>/scripts/report_contract_check.py" <report.md> --profile <profile> --run-dir <research-run-directory> --repo-root .
python -B "<skill-root>/scripts/deep_search_contract_check.py" <research-run-directory> --repo-root .
python -B "<skill-root>/scripts/truthfulness_contract_check.py" --stage pre-report --run-dir <research-run-directory> --repo-root .
python -B "<skill-root>/scripts/truthfulness_contract_check.py" --stage final --run-dir <research-run-directory> --report reports/<run_id>.md --repo-root .
```

Passing the report checker proves reader-visible structure, not fact accuracy. Passing the Deep Search checker proves Run and report association, not narrative quality. Passing the truthfulness checker proves Evidence-to-Claim-to-text contract fidelity, not external truth. Formal reports require all applicable checkers plus the declared sampling review.
