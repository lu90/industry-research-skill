# Source Registry: Official and Industry

Load this registry for industry size, policy, regulation, supply, demand, trade, macroeconomic, public-health, and energy Claims. These entries are starting points, not a closed whitelist. Apply the schema and independence rules in `source-registry-schema.md`.

## Records

<!-- source-registry:start -->
```json
[
  {
    "source_id": "global-world-bank-open-data",
    "name": "World Bank Open Data",
    "publisher_type": "international-organization",
    "evidence_tier": "primary",
    "geography": ["global", "country"],
    "industries": ["cross-industry"],
    "claim_types": ["macro", "development", "demand", "infrastructure", "market-context"],
    "documents": ["dataset", "indicator-page", "data-catalog"],
    "access_mode": ["web", "CSV", "API"],
    "access_status": "public",
    "update_frequency": "varies-by-dataset",
    "canonical_entry": "https://data.worldbank.org/",
    "fallback_sources": ["global-imf-data", "national-statistics-office"],
    "definition_risks": "Indicator revisions, country reporting lags, constant versus current prices, and modeled values require checks.",
    "independence_notes": "Many series originate from national authorities or other international agencies; do not automatically count the upstream source and World Bank series as independent.",
    "registry_status": "registered",
    "last_reviewed": "2026-07-15"
  },
  {
    "source_id": "global-imf-data",
    "name": "IMF Data",
    "publisher_type": "international-organization",
    "evidence_tier": "primary",
    "geography": ["global", "country"],
    "industries": ["cross-industry"],
    "claim_types": ["macro", "forecast", "exchange-rate", "inflation", "financial-conditions"],
    "documents": ["dataset", "data-explorer", "statistical-database"],
    "access_mode": ["web", "download", "API"],
    "access_status": "public",
    "update_frequency": "varies-by-dataset",
    "canonical_entry": "https://data.imf.org/en",
    "fallback_sources": ["global-world-bank-open-data", "national-central-bank", "national-statistics-office"],
    "definition_risks": "Forecasts and observed values must be separated; vintages, revisions, exchange-rate conversion, and fiscal-year conventions may differ.",
    "independence_notes": "Country submissions may share an origin with central-bank or statistics-office series; IMF estimates may use a distinct method and must be identified as estimates.",
    "registry_status": "registered",
    "last_reviewed": "2026-07-15"
  },
  {
    "source_id": "global-un-comtrade",
    "name": "UN Comtrade",
    "publisher_type": "international-organization",
    "evidence_tier": "primary",
    "geography": ["global", "country"],
    "industries": ["cross-industry"],
    "claim_types": ["trade", "exports", "imports", "supply", "demand-proxy"],
    "documents": ["customs-dataset", "trade-table"],
    "access_mode": ["web", "CSV", "API"],
    "access_status": "public",
    "update_frequency": "monthly-and-annual",
    "canonical_entry": "https://comtradeplus.un.org/",
    "fallback_sources": ["national-customs", "global-world-bank-open-data"],
    "definition_risks": "Reporter and partner direction, HS revision, re-exports, mirror data, value basis, and quantity units must match the Claim.",
    "independence_notes": "Data largely originate from national customs submissions; Comtrade and the same national release are usually the same origin.",
    "registry_status": "registered",
    "last_reviewed": "2026-07-15"
  },
  {
    "source_id": "global-iea-data-and-statistics",
    "name": "IEA Data and Statistics",
    "publisher_type": "international-organization",
    "evidence_tier": "primary",
    "geography": ["global", "country"],
    "industries": ["energy", "transport", "utilities"],
    "claim_types": ["supply", "demand", "capacity", "generation", "price", "forecast", "emissions"],
    "documents": ["dataset", "statistics-browser", "report", "chart"],
    "access_mode": ["web", "download", "API"],
    "access_status": "public",
    "update_frequency": "monthly-and-annual",
    "canonical_entry": "https://www.iea.org/data-and-statistics",
    "fallback_sources": ["national-energy-regulator", "global-world-bank-open-data"],
    "definition_risks": "Capacity, generation, consumption, supply, scenarios, and observed values differ; some detailed data products require subscription despite the public entry.",
    "independence_notes": "IEA series often use national administration inputs; verify upstream provenance before pairing with national data as independent evidence.",
    "registry_status": "registered",
    "last_reviewed": "2026-07-15"
  },
  {
    "source_id": "cn-national-data",
    "name": "National Data of China",
    "publisher_type": "official-statistics",
    "evidence_tier": "primary",
    "geography": ["China", "China-province"],
    "industries": ["cross-industry"],
    "claim_types": ["macro", "market-context", "production", "consumption", "population", "price"],
    "documents": ["statistical-database", "yearbook-table", "indicator-page"],
    "access_mode": ["web", "download"],
    "access_status": "public",
    "update_frequency": "monthly-quarterly-annual",
    "canonical_entry": "https://data.stats.gov.cn/",
    "fallback_sources": ["cn-provincial-statistics", "cn-ministry-statistics", "global-world-bank-open-data"],
    "definition_risks": "Current versus constant prices, above-designated-size scope, cumulative versus current-period values, and national versus provincial aggregation require checks.",
    "independence_notes": "Provincial and ministry releases may feed national aggregates; confirm whether they are distinct measurements before cross-verification.",
    "registry_status": "registered",
    "last_reviewed": "2026-07-15"
  }
]
```
<!-- source-registry:end -->
