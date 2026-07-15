# Information Sources

Use this file as the single entry point for source selection and Claim routing. Select sources for a defined Claim, not for search convenience. For standard and deep reports, also read `source-registry-schema.md` before recording evidence.

## Source Priority

| Priority | Source type | Use for | Caution |
|---|---|---|---|
| 1 | Official statistics, laws, regulatory filings, company filings | Facts, policy, financials, reported operations | Check date, geography, period, unit, and definition. |
| 2 | Industry associations, exchanges, reputable international organizations, direct datasets | Industry structure and independently produced measurements | Check whether the source reuses another body's data. |
| 3 | Academic research, patents, standards, method-transparent research and databases | Mechanisms, technology, forecasts, and comparable indicators | Separate observed facts from models and author judgments. |
| 4 | News, expert interviews, and communities | Events, narratives, cases, and qualitative signals | Trace material claims to the original document. |
| 5 | Social media and unsourced material | Weak signals and hypotheses | Never use as the sole proof for a key Claim. |

Evidence tier and accessibility are separate. A paid primary source remains `primary`; an easy-to-open summary does not become primary.

## Claim Routing

1. Define 5-15 high-impact Claims for each standard or deep report. Give each a stable `claim_id`, `claim_type`, geography, time range, and required evidence tier.
2. Load only the registry needed for the Claim. Mixed questions may load more than one registry.
3. Select a registered source by Claim fit, evidence tier, definition match, and independence. Start with its `canonical_entry`, then use its `fallback_sources`.
4. Record actual documents and access outcomes in the Evidence Ledger defined by `source-registry-schema.md`.
5. Permit open discovery when registered sources do not cover the Claim. Assign a temporary `source_id` beginning with `temp-` and set `registry_status: unregistered`.

| Claim family | Load | Preferred source categories | Do not use as sole core proof |
|---|---|---|---|
| Industry size, policy, regulation, supply, demand, trade, macro conditions | `source-registry-official-and-industry.md` | Official statistics, regulators, ministries, international organizations, association original surveys | Unsourced media, vendor marketing |
| Company financials, filings, operations, price, valuation, financing, M&A | `source-registry-company-and-market.md` | Company filings, exchanges, regulators, official quote sources, credible market databases | News summaries, community posts |
| Technology maturity, papers, patents, standards, scientific mechanisms | `source-registry-research-and-technology.md` | Standards bodies, patent offices, scholarly metadata, original papers, official technical documents | Vendor claims or a single review article |
| Consumer perception and channel behavior | The registry matching the underlying Claim, plus first-hand research when needed | Original surveys, platform structured data, channel checks | A single popular post |

## Independence Rules

Count independent data-generating origins, not pages or citations.

- Treat two sources as potentially independent when they use different original producers, samples, or methods.
- Treat a filing on company IR and the same filing in an exchange archive as `same-origin-cross-check`.
- Treat multiple media articles citing one press release, multiple quote sites reproducing one exchange feed, and mirrors of one database as the same origin.
- Check whether an international organization directly republishes a national submission before counting both as independent.
- Use only the `independence_status` values defined in `source-registry-schema.md`. If only one authoritative source exists, retain the Claim with the correct limitation instead of manufacturing a second source.

## Access and Fallback

Use the registry `access_status` to plan access and the Evidence record `access_status` to record what actually happened. Do not claim to have obtained content behind a paywall, login, API key, block, or technical failure.

Fallback is source-oriented: try the registered canonical entry and listed alternatives, then an official archive or alternate format, then a near-primary source, and finally a clearly labeled secondary source. Query generation, Search and Visit loops, run budgets, saturation, and run bundles belong to v62 and are not defined here.

## Reader-Facing Output

Keep report citations and source matrices readable. Preserve detailed Claim-to-document traceability in the internal Evidence Ledger through `claim_id` and `source_id`; do not paste the full ledger into the report body.
