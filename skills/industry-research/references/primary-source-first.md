# Primary Source First

Use this reference for company/product reports, listed-company capital-market reports, and any report that makes claims about company financials, stock price, valuation, delivery/order data, market size, regulation, or industry statistics.

Route each high-impact Claim through `information-sources.md`. Read `source-registry-schema.md`, then load `source-registry-company-and-market.md` for company and capital-market Claims or `source-registry-official-and-industry.md` for industry, policy, supply, demand, trade, and macro Claims. Use the registry for concrete entries and access conditions; do not duplicate its source list here.

## First-Pass Retrieval Order

Before using media summaries as evidence, attempt to locate primary or near-primary sources in this order:

1. Company facts: company announcements, annual/interim/quarterly reports, investor relations releases, earnings presentations, earnings call transcripts, exchange filings, and regulatory filings.
2. Stock price and valuation facts: exchange pages, official quote sources, company exchange announcements, Bloomberg, FactSet, Refinitiv, Wind, Choice, iFinD, or other credible market databases when available.
3. Industry facts: official statistics, regulators, industry associations, international organizations, customs data, central banks, ministries, and credible industry databases.
4. Company operating metrics: company announcements, IR releases, delivery reports, product launch disclosures, regulatory filings, or official channel statements.
5. Opinion and market narrative: broker research, consensus data, media, interviews, expert comments, and social media.

## Evidence Hierarchy

Use this hierarchy when writing the source matrix and evidence notes:

| Evidence tier | Source type | Allowed use |
|---|---|---|
| Primary | Company filings, exchange filings, regulators, official statistics, company IR | Core facts and quantitative claims |
| Near-primary | Exchange/market data vendors, credible databases, industry association datasets | Core market, valuation, and industry facts |
| Secondary | Broker research, consulting reports, reputable financial media | Opinions, context, interpretation, and supplementary signals |
| Weak | Social media, unsourced articles, informal commentary | Only weak signals, never core proof |

## Hard Rules

- Do not use media summaries as the only support for core company financial facts when company filings, IR, exchange filings, or regulatory filings are available.
- Do not use media summaries as the only support for stock price movement, valuation multiples, or market-cap data when exchange or market-data sources are available.
- Do not use media summaries as the only support for industry size, penetration, policy, exports, or sales data when official statistics, regulators, associations, or credible databases are available.
- If only media or secondary sources are available in the active environment, mark the claim as `secondary evidence` or `evidence gap`.
- Record each attempted or obtained document using the internal Evidence Ledger contract in `source-registry-schema.md`.
- In `2.2 来源矩阵和证据质量`, state whether primary-source retrieval was attempted.
- In `2.3 二次检索缺口`, list only the high-impact gaps that remain after up to three targeted closure rounds, including round-by-round attempted sources, status, unresolved reason, and exact primary sources that should be checked next.

## Required Disclosure Pattern

When primary evidence is unavailable, write:

```md
一手来源检索状态: 未取得 {source}. 当前使用 {secondary source} 作为补充信号, 不作为最终核心证明. 下一步应核验 {specific primary source}.
```

Use the precise Evidence-record `access_status` from `source-registry-schema.md` internally. Do not describe paid, login-required, blocked, missing, or technically failed material as obtained.

For three-round retrieval gaps, use this residual-gap pattern:

```md
缺口闭环状态: {部分补齐/仍未补齐}. 三轮闭环已尝试 {第1轮: direct primary sources; 第2轮: near-primary or official-adjacent sources; 第3轮: cross-check, alternate terms, local-language queries, or credible secondary sources}. 未补齐原因: {不可访问/付费库/需要登录/公开检索无可靠结果/口径不匹配}. 为什么重要: {impact}. 下一步应核验 {specific primary or near-primary source}.
```

Do not keep a gap as `仍未补齐` unless the report explains why it could not be closed in the active environment.

For listed companies, the minimum next-step source list should include:

- Company IR or financial report page.
- Relevant exchange announcement page.
- Exchange or credible market-data quote page.
- Official industry or association data for the key industry claim.

## Fact Table Labeling

In `10. 事实, 观点和推断分层`, show evidence tier and primary-source status for every row.

- Use `事实` only when the source is primary or near-primary, or when the evidence tier is explicitly shown.
- Use `待核验事实` for quantitative claims supported by secondary quote sites, media summaries, broker notes, or translated/republished data.
- Media-transmitted industry statistics must be marked as `二手` or `弱证据` unless the original official or association data is checked.
- Inferences must state which facts and evidence tiers they rely on.
- Do not let the word `事实` hide source-quality differences.

## Capital-Market Reports

For stock price, valuation, expectation gap, market-cap repair, investability, or rise/fall questions:

1. First identify the stock ticker, listing venue, and target time window.
2. Try to verify the price move with exchange or credible market data.
3. Try to verify financial and operating facts with company filings or IR.
4. Use media only to explain market narrative, not to replace price, financial, or operating facts.
5. If the active environment cannot access primary sources, make the limitation visible in `2.2`, `2.3`, `10`, `15`, and `17`.
