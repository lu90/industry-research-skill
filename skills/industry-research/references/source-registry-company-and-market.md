# Source Registry: Company and Market

Load this registry for company filings, financials, operating metrics, securities prices, valuation, financing, and M&A Claims. Start with the relevant company IR page when known, then use the registered filing or market venue. Apply `source-registry-schema.md`.

## Records

<!-- source-registry:start -->
```json
[
  {
    "source_id": "us-sec-edgar",
    "name": "SEC EDGAR",
    "publisher_type": "securities-regulator",
    "evidence_tier": "primary",
    "geography": ["United-States", "foreign-issuers-in-US"],
    "industries": ["cross-industry"],
    "claim_types": ["financial", "filing", "ownership", "risk", "capital-structure", "corporate-action"],
    "documents": ["10-K", "10-Q", "8-K", "20-F", "6-K", "prospectus", "XBRL"],
    "access_mode": ["web", "HTML", "XBRL", "API"],
    "access_status": "public",
    "update_frequency": "real-time-filings",
    "canonical_entry": "https://www.sec.gov/search-filings",
    "fallback_sources": ["company-investor-relations", "relevant-stock-exchange"],
    "definition_risks": "Fiscal periods, GAAP versus non-GAAP measures, amendments, filing form, and issuer identity must match.",
    "independence_notes": "A filing on EDGAR and the same filing on company IR are the same origin and only a same-origin cross-check.",
    "registry_status": "registered",
    "last_reviewed": "2026-07-15"
  },
  {
    "source_id": "hk-hkexnews",
    "name": "HKEXnews",
    "publisher_type": "stock-exchange",
    "evidence_tier": "primary",
    "geography": ["Hong-Kong"],
    "industries": ["cross-industry"],
    "claim_types": ["financial", "filing", "listing", "corporate-action", "ownership"],
    "documents": ["announcement", "annual-report", "interim-report", "prospectus", "circular"],
    "access_mode": ["web", "PDF"],
    "access_status": "public",
    "update_frequency": "real-time-filings",
    "canonical_entry": "https://www.hkexnews.hk/",
    "fallback_sources": ["company-investor-relations", "hong-kong-exchanges-and-clearing"],
    "definition_risks": "Issuer stock code, announcement category, reporting period, restatements, and bilingual document versions require checks.",
    "independence_notes": "The same issuer document on HKEXnews and company IR is one original disclosure.",
    "registry_status": "registered",
    "last_reviewed": "2026-07-15"
  },
  {
    "source_id": "cn-cninfo",
    "name": "CNINFO",
    "publisher_type": "official-disclosure-platform",
    "evidence_tier": "primary",
    "geography": ["China"],
    "industries": ["cross-industry"],
    "claim_types": ["financial", "filing", "corporate-action", "ownership", "listing"],
    "documents": ["announcement", "annual-report", "interim-report", "prospectus"],
    "access_mode": ["web", "PDF"],
    "access_status": "public",
    "update_frequency": "real-time-filings",
    "canonical_entry": "https://www.cninfo.com.cn/?lang=zh",
    "fallback_sources": ["cn-stock-exchange", "company-investor-relations"],
    "definition_risks": "Ticker, exchange, consolidated versus parent statements, cumulative periods, corrections, and restatements require checks.",
    "independence_notes": "The issuer announcement on CNINFO, an exchange page, and company IR is normally the same origin.",
    "registry_status": "registered",
    "last_reviewed": "2026-07-15"
  },
  {
    "source_id": "sg-sgx-announcements",
    "name": "SGX Company Announcements",
    "publisher_type": "stock-exchange",
    "evidence_tier": "primary",
    "geography": ["Singapore"],
    "industries": ["cross-industry"],
    "claim_types": ["financial", "filing", "listing", "corporate-action", "ownership"],
    "documents": ["announcement", "financial-statement", "annual-report", "circular"],
    "access_mode": ["web", "PDF"],
    "access_status": "public",
    "update_frequency": "real-time-filings",
    "canonical_entry": "https://www.sgx.com/securities/company-announcements?type=company",
    "fallback_sources": ["company-investor-relations", "singapore-regulator"],
    "definition_risks": "Issuer identity, security type, announcement category, fiscal period, and amended releases require checks.",
    "independence_notes": "An SGX-hosted issuer document and its company IR copy are the same original disclosure.",
    "registry_status": "registered",
    "last_reviewed": "2026-07-15"
  },
  {
    "source_id": "global-bloomberg-terminal",
    "name": "Bloomberg Terminal",
    "publisher_type": "market-data-vendor",
    "evidence_tier": "near-primary",
    "geography": ["global"],
    "industries": ["cross-industry"],
    "claim_types": ["price", "valuation", "consensus", "financial", "ownership", "market-data"],
    "documents": ["market-dataset", "company-data", "consensus-data"],
    "access_mode": ["terminal", "export"],
    "access_status": "paid-database",
    "update_frequency": "real-time-and-periodic",
    "canonical_entry": "https://www.bloomberg.com/professional/products/bloomberg-terminal/",
    "fallback_sources": ["relevant-stock-exchange", "company-investor-relations", "public-market-data"],
    "definition_risks": "Adjusted prices, timezone, currency, consensus window, vendor-calculated fields, and as-of time require checks.",
    "independence_notes": "Price fields may originate from exchanges and filing fields from issuer disclosures; do not pair the vendor view with the same upstream source as independent evidence.",
    "registry_status": "registered",
    "last_reviewed": "2026-07-15"
  }
]
```
<!-- source-registry:end -->
