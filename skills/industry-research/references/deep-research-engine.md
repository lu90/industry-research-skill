# Deep Research Engine

Use this reference as the execution layer for standard and deep reports. It is mandatory for standard and deep reports unless the user explicitly triggers Explicit Short Answer Mode.

## Purpose

Deep Research Engine turns a user request into a traceable research process: plan, Claim routing, source matrix, Evidence Ledger, multi-step retrieval, evidence classification, cross-checking, contradiction handling, synthesis, and verification. It should improve research discipline without exposing long internal scratch work. Use `information-sources.md` for routing and `source-registry-schema.md` as the normative Claim, Source, access, registry, and independence contract.

## Execution Flow

1. Research plan: define the mother question, sub-questions, boundary, selected analysis layers, required evidence, and 5-15 high-impact Claims. Assign each Claim a stable `claim_id`, type, geography, time range, and required evidence tier.
2. Source matrix: use `information-sources.md` to route each Claim, load only the matching Source Registry, and map `claim_id` to preferred registered `source_id` values and fallbacks.
3. First retrieval pass: call `deep-search-protocol.md` once with the high-impact Claim queue, v61 source routes, evidence requirements, known Evidence, and open Gaps. The Protocol performs the provider-neutral breadth pass and returns auditable Evidence, Learnings, Attempts, Gaps, contradictions, and a stop reason. Registries are preferred routes, not a closed whitelist.
4. Compression pass: write attempted and obtained documents to the internal Evidence Ledger, then summarize findings into facts, opinions, inferences, forecasts, weak evidence, and evidence gaps.
5. Build a retrieval-gap queue: after the first retrieval pass, list high-impact missing evidence that can materially change the conclusion.
6. Three-Round Retrieval Gap Closure Loop: for every high-impact gap, the Engine may authorize up to three targeted closure rounds before drafting the final report. For each authorized round, call `deep-search-protocol.md` with the selected Gap, current Evidence, Learnings, and source routes. The Protocol executes only that bounded round and returns control to the Engine. Stop early only when the gap is resolved, or when a clear access barrier proves further public retrieval is not useful.
7. Gap status classification: after up to three closure rounds, label each gap as `已补齐`, `部分补齐`, or `仍未补齐`. Keep `仍未补齐` only when the source is inaccessible, requires a paid database, requires login, or public search returns no reliable result.
8. Cross-verification: for key data and conclusions, compare `origin_source_id` values and try to verify with at least two independent data-generating origins. Use the schema `independence_status`; multiple copies of one original document are not independent.
9. Contradiction handling: do not force inconsistent sources into one number. Explain definition, geography, period, or source-incentive differences and assign a shared `contradiction_group` in the Ledger.
10. Claim admission: after v61 Evidence validation, calculate one status for every final Plan Claim. A Claim is `supported`, `refuted`, `conflicted`, `gapped`, or `orphaned` under the v64 rules below.
11. Pre-report gate: draft a formal report only when every Plan Claim is `supported` or `refuted`. Keep refuted Claims in the research result, but present the denial, narrowing, or lack of support faithfully.
12. Working draft and initial binding: answer the user's question first when applicable, then present evidence, mechanism, uncertainty, and follow-up checks. Create one canonical `report-claims.json` binding for every Plan Claim and audit the bound numbers.
13. Pressure Test closure: run `pressure-test.md` against the working draft, write `challenges.json`, route only retrieval Challenges into the Gap Closure Loop, resolve each Challenge, rewrite the report, and obtain reviewer closure.
14. Post-challenge truthfulness rerun: when Pressure Test changes Claim content, Claim status, Evidence selection, numbers, or body text, rerun affected v64 Claim admission and binding. Then run the v64 final fidelity audit against the revised report.
15. Formal registration: grant final permission and set Manifest `report_path` only after the v63 structure check, v64 final fidelity check, v65 Challenge Ledger and reader-view checks, and sampling audit pass.

## v64 Claim Admission

Evidence qualifies for one Claim only when `claim_id` matches, `access_status` is `obtained`, `relation` is `support` or `refute`, `evidence_span` and `page_or_section` are nonempty, and the document tier meets the Claim requirement. Tier admission is monotonic: primary satisfies every tier, near-primary satisfies near-primary through weak, secondary satisfies secondary or weak, and weak satisfies only weak.

| Status | Deterministic meaning | Formal-report behavior |
|---|---|---|
| `supported` | At least one qualifying support record and no unresolved material conflict | Admit with Evidence limitations visible |
| `refuted` | Qualifying refute Evidence and no qualifying support conflict | Admit only as a denied, narrowed, or unsupported proposition |
| `conflicted` | Qualifying support and refute Evidence coexist, or `unresolved-conflict` remains | Deny a single formal conclusion |
| `gapped` | No qualifying Evidence and an explicit Gap exists for the same Claim | Finalize the Run as incomplete and return Summary plus Gaps |
| `orphaned` | No qualifying Evidence and no matching Gap | Contract failure until Evidence or an honest Gap is added |

Do not impose a universal two-source rule. `single-source-primary` may admit an authoritative primary fact with its limitation visible. `independently_verified` still requires two distinct `origin_source_id` values, and same-origin copies never count as independent verification.

## Retrieval Gap Closure Loop

The gap section is not a place to park shallow research. It is the residual queue after up to three targeted closure rounds.

For each high-impact gap:

1. Name the exact missing metric, filing, dataset, quote page, regulatory document, or primary source.
2. Authorize up to three targeted retrieval rounds against primary or near-primary sources before writing the final conclusion. Execute each authorized round through `deep-search-protocol.md`.
3. Record what was attempted in each round, such as company IR, exchange filings, official statistics, industry associations, regulators, credible databases, or market-data sources.
4. Classify the status:
   - `已补齐`: primary or near-primary evidence was found. Use it in the relevant analysis section instead of keeping it as a gap.
   - `部分补齐`: only secondary evidence, incomplete figures, or mismatched period/geography/definition was found. Use it only with evidence-tier labeling and keep the limitation visible.
   - `仍未补齐`: keep the gap only when the source is not publicly accessible, requires a paid database, requires login, blocks access, or public search returns no reliable result.
5. State why the remaining gap matters to the conclusion and which exact source should be checked next.

Do not stop after one broad search if the missing evidence affects market size, lifecycle, financials, valuation, stock movement, policy, regulation, demand, supply, cost, profitability, or core competitive claims. Use the first closure round for the most direct primary source, the second for near-primary or official-adjacent sources, and the third for cross-checking, alternate terms, archive pages, local-language queries, or credible secondary sources clearly marked as limitations.

Pressure Test may add or reuse Gaps only for Challenges with `verification_method: retrieval`. Definition, calculation, logic, scope, and scenario reviews stay in `challenges.json` and do not consume retrieval rounds. The Engine selects each retrieval Challenge Gap and authorizes any closure round; the Protocol does not decide materiality, resolution, report rewrite, reviewer closure, or formal-report permission.

## Source Matrix

| Layer | Typical claims | Preferred sources | Evidence level |
|---|---|---|---|
| Macro | Policy, interest rates, exchange rates, consumption cycle, technology cycle, risk appetite | Regulators, official statistics, central banks, ministries, international organizations | High when primary, medium when interpreted by reports |
| Meso | Market size, growth, penetration, value chain, competition, lifecycle, prosperity indicators | Industry associations, official statistics, credible databases, consulting reports, broker reports | High for primary data, medium for forecasts/opinions |
| Micro | Company financials, products, operations, channels, customers, margins, cash flow | Company filings, annual/interim/quarterly reports, IR, announcements, exchange filings | High when company-filed |
| Capital market | Stock movement, valuation, expectation gap, liquidity, multiple changes, buyback, market risk appetite | Exchange data, company filings, IR, broker/consensus data when available, financial databases, market reports | High for reported facts, medium for market interpretation |

Internally, add `claim_id`, preferred `source_id`, actual Evidence-record `access_status`, `registry_status`, `independence_status`, and definition limitations. Keep the reader-facing matrix concise. Detailed document title, URL, date, period, page or section, and short supporting span belong in the Evidence Ledger, not the report body.

## Output Trace Requirements

Standard and deep reports should include visible traces of the engine without dumping internal notes:

- State the research boundary and selected layers.
- Include a research plan summary.
- Include a source/evidence matrix or methodology note.
- Include a key evidence quality note.
- Make key Claims traceable to actual sources through the internal `claim_id` and `source_id` relationship.
- Include the retrieval-gap closure loop result, not only first-pass missing items.
- Include three-round closure attempts, current gap status, reason for unresolved gaps, and source-oriented follow-up verification.
- Mark evidence quality for important claims.
- State evidence gaps and next verification steps.
- Separate facts, opinions, forecasts, and inferences when the distinction affects the conclusion.
- Keep `report-claims.json` and `truthfulness-audit.md` internal. The reader-facing report does not need to expose internal Claim IDs outside the existing source matrix.
- Keep the full `challenges.json` internal. Expose only the canonical nine-column Pressure Test rows required by `pressure-test.md`, plus the truthful `review_mode` disclosure.
- Bind every Plan Claim to one exact reader-visible sentence or shortest complete statement in a real analytical section. Source matrices, compliance checklists, methodology notes, and disclaimers cannot serve as the canonical body binding.

## Minimum Visible Output Blocks

For standard and deep reports, include these blocks either near the research boundary or in the methodology section:

1. Research plan summary: mother question, sub-questions, selected layers, and what must be verified.
2. Source matrix or evidence matrix: key Claim, source type, use, evidence level, actual access state, independent-verification state, and limitation.
3. Key evidence quality note: strongest sources, weak sources, and unresolved evidence gaps.
4. Three-round retrieval closure table: specific missing data, attempted sources by round, current status, unresolved reason, and where to verify next.

Keep these blocks concise. They are report-facing discipline, not internal chain-of-thought.

## Failure Handling

If network access, database access, filings, or primary sources are unavailable, do not fill gaps with generic claims. Record the exact Evidence-record `access_status`, keep `evidence_span` empty, and do not describe the source as obtained. Write the evidence gap, the three-round closure attempts already made or the access barrier that stopped the loop early, the reason it remains unresolved, the likely impact on confidence, and the next source to verify.

This Engine owns evidence admission, independent verification, contradiction handling, and the three-round gap-closure decision. It does not define provider-specific search calls, query generation, Search and Visit loops, recursion, saturation, budgets, worker coordination, or run bundles; those are v62 responsibilities.

The Engine also owns the minimum evidence threshold and formal-report permission. A Search Protocol result marked saturated or budget-exhausted is not permission to draft. If any Claim is `conflicted`, `gapped`, or `orphaned`, the Controller must deny a single formal conclusion, keep `report_path` null, and return only the Run Summary, conflicts, and Gaps. A draft also remains nonformal when any Challenge is pending or any high Challenge is open or disputed. It becomes formal only after Pressure Test closure, rerun of affected v64 admission and binding, the v63 structure checker, v64 final fidelity checker, v65 ledger and reader-view checks, and Claim sampling audit all pass.
