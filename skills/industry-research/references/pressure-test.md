# Multi-Agent Pressure Test

Use this protocol after v64 pre-report Claim admission and creation of a working draft plus initial `report-claims.json`. Pressure Test reviews the working draft, not a Manifest-registered formal report. It is complete only after verification, resolution, report rewrite, reviewer closure, rerun of affected v64 checks, and final fidelity audit.

## Roles And Independence

- Organizer: controls scope, deduplicates Challenges, assigns materiality, selects the verification route, and checks closure completeness.
- Industry expert: reviews industry boundary, value chain, lifecycle, and business logic.
- Investment researcher: reviews financials, profit pools, valuation, capital markets, and investability logic.
- Policy or regulatory researcher: reviews policy, regulation, law, compliance, and macro assumptions.
- Operator or entrepreneur: reviews business model, channel, cost, organization, supply chain, and execution realism.
- Intern: identifies overlooked questions but cannot close a high Challenge alone.
- Devil's advocate: challenges the central conclusion, alternative explanations, counterexamples, and falsification conditions.

When subagents are available, the four core reviewers independently read the same working draft and Run artifacts without receiving expected answers. Otherwise use `single-agent-simulated` and disclose that mode in `challenges.json` and the report. Do not describe simulated roles as independent Agent review.

## Challenge Ledger

Create `research_runs/<run_id>/challenges.json` with this top-level shape:

```json
{
  "schema_version": "v65",
  "run_id": "<run_id>",
  "review_mode": "multi-agent",
  "challenges": []
}
```

`review_mode` is `multi-agent` or `single-agent-simulated`. Every Challenge uses exactly these fields:

| Field | Rule |
|---|---|
| `challenge_id` | Stable `challenge-` plus lowercase kebab case, unique in the Run |
| `reviewer_role` | `industry-expert`, `investment-researcher`, `policy-regulatory`, `operator-entrepreneur`, `intern`, or `devils-advocate` |
| `target_claim_id` | Existing Claim from final `plan.json` |
| `target_section` | Canonical working-draft section title |
| `challenge` | One concrete and verifiable or reviewable objection |
| `materiality` | `high`, `medium`, or `low` |
| `verification_method` | `retrieval`, `data-definition`, `calculation`, `logic`, `scope`, or `scenario` |
| `verification_required` | Exact Evidence, calculation, or analysis needed |
| `gap_id` | One same-Claim Gap for `retrieval`; otherwise `null` |
| `resolution` | `pending`, `confirmed`, `partially_valid`, `refuted`, `unresolved`, or `out_of_scope` |
| `evidence_refs` | Same-Claim Evidence locators used for resolution, possibly empty |
| `verification_notes` | Reproducible verification work or access limitation |
| `report_change` | Concrete report rewrite, or a reviewable reason for no change |
| `confidence_action` | `unchanged`, `downgraded`, `withdrawn`, or `not-applicable` |
| `reviewer_status` | `open`, `closed`, or `disputed` |
| `closed_by` | `original-reviewer` or `organizer` |
| `reviewer_note` | Re-review decision and closure basis |

Each Evidence locator contains only `source_id`, `document_url`, `page_or_section`, `relation`, and `evidence_span_sha256`. Calculate the hash from Unicode-NFKC normalized `evidence_span` with whitespace collapsed. The locator must uniquely match one obtained Evidence record for the same Claim.

## Materiality And Verification Routing

- `high`: may change the central conclusion, lifecycle, a key number, valuation, core risk, or formal-report permission. It requires verification, report treatment, and closure by the original reviewer.
- `medium`: may change a local conclusion, boundary, secondary metric, or recommendation priority. It requires resolution and may be closed by the Organizer.
- `low`: improves expression, background, or a noncritical limitation. Record its treatment; the Organizer may close it.

Route facts requiring external Evidence to `retrieval`. Route definition mismatches to `data-definition`, arithmetic to `calculation`, causal or inferential objections to `logic`, industry-boundary objections to `scope`, and forecasts to `scenario`. Only `retrieval` creates or reuses a Gap and returns to the Deep Research Engine and Deep Search Protocol.

## Verification And Resolution

For a retrieval Challenge, reuse an exact existing Gap or create one stable same-Claim Gap. The Engine may authorize up to three targeted closure rounds. The Protocol executes only the authorized retrieval round. New Evidence must enter final `evidence.jsonl`; Challenge resolution uses only Controller-merged Evidence and final Gap state.

For non-retrieval methods, preserve the definition comparison, calculation inputs and operation, alternative explanations, boundary analysis, or scenario assumptions in `verification_notes`. Do not create a Gap to make a non-retrieval review appear complete.

Apply these minimum duties:

| Resolution | Required report behavior |
|---|---|
| `confirmed` | Change the affected body, conclusion, number, reasoning, or recommendation |
| `partially_valid` | Narrow the original conclusion and disclose the remaining limitation |
| `refuted` | Retain the conclusion only with same-Claim Evidence or reproducible non-retrieval review grounds |
| `unresolved` | Exhaust the applicable method or record an access barrier, disclose uncertainty, and downgrade or withdraw confidence |
| `out_of_scope` | Clarify the exclusion in the research boundary rather than merely saying it is not handled |

High unresolved Challenges additionally require a concrete report rewrite and original-reviewer closure. If the central conclusion still cannot be expressed honestly through narrowing, confidence downgrade, or withdrawal, deny formal-report permission.

## Re-Review And Formal Gate

After the author updates Evidence, Gaps, Claim state, analysis, numbers, or confidence, send each Challenge back for re-review. High Challenges require `closed_by: original-reviewer`. Medium and low Challenges may use `organizer`. A reviewer may keep `disputed`; a disputed high Challenge blocks the report.

Before setting Manifest `report_path` or `report_status: generated`, require all of the following:

- `challenges.json` exists, uses the same `run_id`, and contains the four core roles.
- No Challenge has `resolution: pending`.
- No high Challenge is `open` or `disputed`.
- Resolution-specific Evidence, notes, confidence, and report-change duties pass.
- Every retrieval Challenge references a valid same-Claim Gap.
- The report nine-column summary matches the Challenge Ledger.
- Every report-affecting Pressure Test change has triggered a rerun of affected v64 Claim admission and binding.
- The v63 structure check, v64 final fidelity audit, Challenge Ledger check, and sampling review all pass.

A failed Run may return its Run Summary, Gaps, and open Challenges. It must keep formal `report_path` null.

## Reader-Facing Summary

Disclose `review_mode`, then use the exact language-matched nine-column table:

```text
质疑 ID | 视角 | 目标 Claim/章节 | 重要性 | 核心质疑 | 裁决 | 证据/Gap | 报告改动 | 复核状态
Challenge ID | Perspective | Target Claim/Section | Materiality | Core Challenge | Resolution | Evidence/Gap | Report Change | Reviewer Status
```

Display every high Challenge, every `confirmed`, `partially_valid`, or `unresolved` Challenge, and every medium or low Challenge that changed the report. Keep other closed low-impact records internal. Pressure Test Evidence and report changes must also update the source matrix, Gap results, affected analysis, and `report-claims.json`; changing only the summary table is a failure.

For a medium or low `refuted` or `out_of_scope` Challenge that causes no report rewrite, start `report_change` with `no report change:` or `无报告改动:` and then state the reason. This explicit marker keeps reader-row selection deterministic; do not use it when the report gained a limitation, disclosure, or other substantive change.
