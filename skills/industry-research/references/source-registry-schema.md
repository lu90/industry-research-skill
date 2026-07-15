# Source Registry and Evidence Ledger Schema

Use this file as the normative v61 contract. The three source registries contain stable source metadata. The Evidence Ledger records documents actually obtained or attempted in one standard or deep research run. Report citations remain reader-facing and link back through `claim_id` and `source_id`.

## Claim Interface

Assign stable IDs within a run using lowercase kebab case, for example `claim-cn-ev-exports-2025`.

| Field | Required | Rule |
|---|---:|---|
| `claim_id` | Yes | `claim-` plus lowercase kebab case; stable within the run. |
| `claim_text` | Yes | One verifiable statement or question. |
| `claim_type` | Yes | Domain label such as `market-size`, `policy`, `supply`, `demand`, `financial`, `valuation`, `technology`, `paper`, or `patent`. |
| `geography` | Yes | Target geography or `global`. |
| `time_range` | Yes | Target date, period, or horizon. |
| `required_evidence_tier` | Yes | One Evidence tier below. |
| `preferred_source_categories` | Yes | Categories produced by Claim routing. |

## Source Record

Each record in a registry must contain every field below. Registry Markdown files store records in one JSON array between `source-registry:start` and `source-registry:end` markers so the maintenance checker can validate them without a third-party parser.

| Field | Rule |
|---|---|
| `source_id` | Globally unique lowercase kebab-case identifier. |
| `name` | Published source or platform name. |
| `publisher_type` | Stable descriptive category, not a provider-specific tool name. |
| `evidence_tier` | Default tier; reassess at document level. |
| `geography` | JSON list of covered geographies. |
| `industries` | JSON list; use `cross-industry` when broad. |
| `claim_types` | JSON list of Claim families the source can support. |
| `documents` | JSON list of typical material types. |
| `access_mode` | JSON list such as `web`, `PDF`, `CSV`, `XBRL`, or `API`. |
| `access_status` | Access condition enum for planning. |
| `update_frequency` | Typical cadence or `irregular`. |
| `canonical_entry` | Official HTTP or HTTPS entry. |
| `fallback_sources` | JSON list of source categories or registered `source_id` values. |
| `definition_risks` | Main period, unit, scope, sample, or methodology risk. |
| `independence_notes` | Known upstream data reuse and independence cautions. |
| `registry_status` | Always `registered` inside a maintained registry. |
| `last_reviewed` | Registry review date in `YYYY-MM-DD`. |

## Evidence Record

Store the internal Evidence Ledger as UTF-8 JSONL, one object per attempted or obtained document. Keep `evidence_span` to the shortest passage or data row needed for verification.

When file writing is available for a standard or deep report, persist the Ledger as an internal JSONL artifact and retain its path for review. The host runtime chooses the task-local location. v61 does not prescribe a v62 Research Run directory or bundle layout.

| Field | Required | Rule |
|---|---:|---|
| `run_id` | Yes | Current research run identifier. |
| `claim_id` | Yes | Claim interface identifier. |
| `source_id` | Yes | Registered ID, or `temp-` plus lowercase kebab case for an unregistered source. |
| `registry_status` | Yes | `registered` or `unregistered`. |
| `document_title` | Yes | Complete document title when known. |
| `document_url` | Yes | Original URL when known; may be empty after a failed attempt. |
| `publisher` | Yes | Publishing body. |
| `published_at` | Yes | Publication date, or an explicit unknown value if the attempt failed. |
| `accessed_at` | Yes | `YYYY-MM-DD`. |
| `reporting_period` | Yes | Data period, or `not-applicable` / `unknown`. |
| `geography` | Yes | Evidence geography, not merely publisher location. |
| `unit_and_currency` | Yes | Unit and currency, or `not-applicable` / `unknown`. |
| `definition` | Yes | Metric definition, scope, or explicit unknown. |
| `page_or_section` | Yes | Page, table, section, or empty after failed access. |
| `evidence_span` | Yes | Short supporting text or data; empty unless `access_status: obtained`. |
| `relation` | Yes | Relationship to the Claim. |
| `evidence_tier` | Yes | Document-level tier. |
| `access_status` | Yes | Actual acquisition outcome. |
| `origin_source_id` | Yes | Original data-generating body or document-series ID used for independence checks. |
| `independence_status` | Yes | Claim-level verification state applied consistently to related records. |
| `contradiction_group` | Yes | Shared ID for conflicting evidence, or an empty string. |
| `confidence` | Yes | Confidence in the evidence-to-Claim relationship. |

For non-obtained evidence, set `relation: neutral` and leave `evidence_span` empty. Record the failed attempt instead of presenting unseen content as evidence. For quantitative evidence, fill period, unit, geography, and definition with concrete values; `unknown` is an explicit gap, not permission to omit the field.

## Enums

| Interface | Allowed values |
|---|---|
| `evidence_tier` | `primary`, `near-primary`, `secondary`, `weak` |
| Source record `access_status` | `public`, `login-required`, `paid-database`, `API-key-required` |
| Evidence record `access_status` | `obtained`, `public-but-technical-failure`, `login-required`, `paid-database`, `API-key-required`, `blocked`, `not-found`, `definition-mismatch` |
| `registry_status` | `registered`, `unregistered` |
| `relation` | `support`, `refute`, `neutral` |
| `independence_status` | `independently_verified`, `same-origin-cross-check`, `single-source-primary`, `secondary-only`, `unresolved-conflict` |
| `confidence` | `high`, `medium`, `low` |

## Independence Contract

- `independently_verified` requires at least two obtained records with different `origin_source_id` values and genuinely independent data generation or methods.
- `same-origin-cross-check` means multiple pages or archives reproduce one original document or dataset. It verifies transcription or filing consistency, not independent truth.
- `single-source-primary` means one primary origin supports the Claim and no independent origin was obtained.
- `secondary-only` means no primary or near-primary evidence was obtained.
- `unresolved-conflict` means material evidence conflicts remain. Give related records the same non-empty `contradiction_group`.

## v61 and v62 Boundary

v61 owns Claim routing, Source records, Evidence records, access outcomes, registry status, and independence status. It permits temporary unregistered sources, so registries are preferred routes rather than a closed whitelist. v62 may consume these fields and return Evidence records, attempts, candidates, gaps, contradictions, and a stop reason. Query generation, Search and Visit loops, recursion, saturation, budgets, worker coordination, and run-bundle layout are outside this contract.

## Deterministic Validation

Run:

```text
python -B scripts/source_contract_check.py --self-test
python -B scripts/source_contract_check.py .
python -B scripts/source_contract_check.py . --evidence path/to/evidence.jsonl
```

The checker validates required fields, enums, global `source_id` uniqueness, temporary IDs, registry membership, failed-access honesty, and the minimum same-origin rule. It does not validate factual accuracy or prove that a canonical URL is authoritative.
