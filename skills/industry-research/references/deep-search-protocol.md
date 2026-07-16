# Deep Search Protocol

Use this provider-neutral protocol whenever the Deep Research Engine requests a first retrieval pass or one bounded gap-closure round. The Engine remains the authority for research policy and formal-report admission. This protocol owns retrieval execution and auditable run artifacts only.

## Authority Boundary

| Component | Sole authority |
|---|---|
| Deep Research Engine | Research plan, high-impact Claims, required Evidence tier, evidence admission, independent-verification requirement, contradiction treatment, gap-closure round decisions, minimum evidence threshold, and formal-report permission. |
| Deep Search Protocol | Breadth and follow-up query generation, Search, Visit, and Extract actions, recursion inside one Engine-authorized round, deduplication, saturation, safety budgets, Worker coordination, and Research Run artifacts. |
| v61 source system | Claim routing, Source records, Evidence records, access outcomes, registry status, and source-independence fields. |

If rules appear to conflict, the Engine governs research quality and report admission, while this protocol governs retrieval execution. This protocol must not redefine the Engine's evidence threshold, two-origin rule, or three-round gap-closure limit.

## Provider-neutral Capabilities

The host may implement these capabilities with any browser, search service, scholarly index, local file reader, database connector, or human-assisted workflow:

- `Search(query, constraints)`: discover candidate documents and return titles, URLs or document identifiers, publisher hints, dates, and result status.
- `Visit(locator)`: retrieve or open one candidate and return actual access status, resolved locator, content metadata, and content when available.
- `Extract(content, claim_context)`: produce the shortest verifiable Evidence span plus document metadata, Learnings, Gaps, and contradictions.

A tool name, API payload, ranking algorithm, or Provider credential must not enter this contract. An external action is one Search or Visit call. Extract is local when it operates only on already obtained content; if Extract invokes an external service, the runtime counts it as an external action for retry and elapsed-time accounting.

## Round Input and Output

Each task from the Engine contains at least:

| Field | Rule |
|---|---|
| `run_id` | Stable identifier shared by every artifact in the Run. |
| `round_id` | `initial` or the Engine-authorized closure round identifier. |
| `claim_id`, `claim_text`, `claim_type` | v61 Claim interface values. |
| `geography`, `time_range` | Retrieval boundary. |
| `required_evidence_tier` | Engine requirement, consumed but never changed by the Protocol. |
| `preferred_source_categories` | v61 Claim-routing output. |
| `preferred_sources` | Registered Source records, including canonical entries. |
| `fallback_sources` | Registered fallback routes. |
| `known_evidence` | Existing Evidence and compressed Learnings. |
| `open_gaps` | Engine-selected missing or contradictory items for this round. |
| `budgets` | Run safety caps and current usage. |

Each task returns `evidence_records`, `learnings`, `attempted_queries`, `visited_sources`, `new_source_candidates`, `remaining_gaps`, `contradictions`, and `stop_reason`. Evidence records conform exactly to `source-registry-schema.md`.

## Initial Breadth Pass

The first pass is Claim-led, not a fixed query taxonomy:

1. Take the Engine's high-impact Claim queue in priority order.
2. Route each uncovered Claim through `information-sources.md` and load only matching registries.
3. Create at least one registered-route action for every selected high-impact Claim before repeating a Claim, unless its canonical entry is directly visited.
4. Visit registered canonical entries first when they are document-level or searchable official entry points. Otherwise Search with the Claim boundary and registered publisher or dataset identity.
5. Try registered fallbacks after canonical failure or definition mismatch.
6. Use open discovery only when registered routes do not resolve the Gap, do not cover the geography or period, or reveal a necessary unregistered primary source.
7. Save attempts and short Evidence; do not draft conclusions during retrieval.

Breadth means coverage across the Engine-selected high-impact Claims and relevant source origins. It does not require seven fixed query types, equal query counts per Claim, or a minimum number of results.

## Evidence, Learnings, Gaps, and Follow-up Queries

After each useful action, compress results into four separate objects:

- Evidence: v61 records for obtained or honestly failed documents.
- Learnings: concise terms, entities, document series, definitions, periods, causal mechanisms, and source leads learned from actual results.
- Gaps: exact missing metric, period, geography, definition, origin, contradiction, or access route, with impact and status.
- Contradictions: incompatible values or claims that may require a v61 `contradiction_group`.

A Follow-up Query is allowed only when it cites at least one `claim_id`, one `gap_id`, and one concrete input from Evidence or Learnings. Record `derived_from_evidence_ids`, `derived_from_learning_ids`, and the intended `gap_id`. A query that merely paraphrases an attempted query without a new boundary, source lead, definition, origin, or contradiction target is a duplicate and must not run.

Useful optional transformations include local-language terms, document titles, discovered official series, alternative metric definitions, period or geography constraints, original-source tracing, and counter-evidence. They are strategies, not mandatory categories.

## Search, Visit, and Extract Loop

For each Engine-authorized round:

1. Controller reserves budget and deduplicates the proposed Query or locator.
2. Worker performs Search or Visit and records the attempt once, including failures and retry count.
3. Worker visits only candidates that can improve a selected Claim, resolve a Gap, establish an independent origin, or clarify a contradiction.
4. Worker extracts the shortest supporting span and complete v61 Evidence metadata. Unavailable content uses an empty span and `relation: neutral`.
5. Worker writes only its own Evidence JSONL and Summary JSON.
6. Controller updates run-wide deduplication sets, usage, progress signals, Learnings, Gaps, and candidate sources.
7. Controller either schedules a derived Follow-up Query inside the same bounded round or returns control to the Engine.

An action failure may be retried at most twice by default. Retries retain one logical attempt identifier and increment `retry_count`; they do not create fake breadth.

## Registry-first and Open Discovery

Registered sources are preferred routes, not a whitelist. Record route stages as `registered_canonical`, `registered_fallback`, or `open_discovery`. Open discovery may yield a temporary `source_id` beginning with `temp-` and `registry_status: unregistered`. Using an unregistered source does not update a maintained registry automatically; promotion requires later human review.

## Deduplication

Controller applies all four layers before final merge:

1. Query: Unicode-normalize, case-fold, collapse whitespace, and normalize equivalent boundary tokens where the runtime can do so safely.
2. URL: lowercase scheme and host, remove fragments and known tracking parameters, normalize the default port, sort remaining query parameters, and preserve parameters that identify a document or dataset.
3. Document: prefer a content hash; otherwise combine normalized title, publishing body, publication date, and stable document-series identifier. Mirrors remain one document.
4. Source independence: group Evidence by `origin_source_id`. Copies, syndications, archives, and summaries of one origin cannot count as independent verification.

Deduplication never deletes audit history. Duplicate attempts remain in Worker summaries with a skipped status, while the final Evidence Ledger keeps the best complete record per Claim-document relation and preserves conflicting records.

## Saturation and Stop Precedence

An effective retrieval action is a completed non-duplicate Search or Visit that had a realistic chance to improve the selected Claim or Gap. Information is saturated only after two consecutive effective actions produce all three outcomes:

- no new high-quality Evidence;
- no improvement in high-impact Claim coverage;
- no new high-impact contradiction.

Failed, blocked, duplicate, or retry actions do not count toward the two-action saturation window. Saturation is not evidence sufficiency. Return remaining Gaps to the Engine whenever saturation occurs below the minimum evidence threshold.

Evaluate stop conditions after every external action in this order:

1. `evidence_sufficient`, only when the Engine signals its threshold is met.
2. `information_saturated`.
3. `budget_exhausted`.
4. `access_blocked` when all material remaining routes are inaccessible.
5. `tool_error`, `user_stopped`, or continued execution.

The default Run safety caps are 60 Search actions, 120 Visit actions, two retries for each external action, and 30 elapsed minutes when measurable. Runtime may override caps for cost, environment, or an explicit user instruction, but must record overrides in the Manifest and must not expose quick, normal, or deep tiers. Evidence sufficiency and saturation are preferred early stops; caps are insurance, not quotas.

## Research Run Bundle

New standard and deep runs use the final v62 root contract:

```text
research_runs/<run_id>/
├── manifest.json
├── plan.json
├── workers/
│   ├── <worker_id>-evidence.jsonl
│   └── <worker_id>-summary.json
├── evidence.jsonl
├── gaps.json
├── run-summary.md
└── raw/
```

`research_runs/` is ignored by Git but retained locally by default. For a Run that generates a formal report, determine the planned report filename before retrieval and use its filename stem as `run_id` and the Run directory name. This gives `reports/<run_id>.md` a directly matching `research_runs/<run_id>/`. A Run that does not generate a report uses a stable timestamp plus normalized topic. A rerun always creates a new `run_id` and uses `parent_run_id` or `supersedes`; it never overwrites an old Run.

### Manifest

`manifest.json` contains `schema_version`, `run_id`, `status`, `stop_reason`, `question`, `created_at`, `completed_at`, `parent_run_id`, `supersedes`, `controller_id`, `worker_ids`, `budgets`, `usage`, `budget_overrides`, `engine_report_permission`, `report_path`, `report_status`, and `errors`. Status is only `running`, `completed`, or `incomplete`. Stop reason is null while running and otherwise one of the protocol stop reasons.

`report_status` is `not_generated`, `generated`, or `superseded`. `engine_report_permission` records the Engine decision and is never inferred by the Controller. An incomplete Run must set it to false, use `report_path: null`, and use `report_status: not_generated`. A generated report requires it to be true, must exist under `reports/`, must have a filename stem equal to `run_id`, and must point back to exactly one Run through its Manifest.

### Plan, Gaps, and Worker Summary

`plan.json` contains the research boundary, Engine-owned Claim queue, source routes, Worker assignments, and Engine-authorized round identifiers. It records policy inputs without redefining them.

`gaps.json` contains `run_id`, `gaps`, and `contradictions`. Each Gap has `gap_id`, `claim_id`, exact missing item, impact, status, attempted rounds or actions, unresolved reason, and next source route.

Each Worker Summary contains `run_id`, `worker_id`, assignment, attempted queries, visited sources, Learnings, remaining Gaps, contradictions, new source candidates, usage, and Worker stop reason. Structure uses JSON, Evidence uses JSONL, and the human review summary uses Markdown.

### Ownership and Merge

Workers write separate files and never append to final `evidence.jsonl`. Controller alone merges, deduplicates, assigns Claim relations and contradiction groups, writes final Gaps, chooses final status, and updates the Manifest. A single-Agent runtime follows the same contract with one Worker.

Only the Engine decides whether the minimum evidence threshold is satisfied and whether a formal report may be generated. Controller maps that decision to `completed` or `incomplete`; it does not infer a new threshold.

## Engine Integration

The Engine invokes this protocol once for the initial breadth pass. After compression, the Engine selects high-impact Gaps and separately authorizes closure round 1, 2, or 3. Each invocation returns Evidence, Learnings, Attempts, Gaps, contradictions, and a stop reason. The Engine evaluates gap status, evidence admission, and whether another round is allowed.

An `incomplete` Run may produce `run-summary.md` and visible Gaps but no formal report. A `completed` Run may generate a report only after Controller merge and Engine permission. This separation prevents retrieval saturation, budget exhaustion, or a polished summary from being mistaken for research completion.
