# Source Registry: Research and Technology

Load this registry for papers, technology maturity, scientific mechanisms, patents, standards, and prior-art Claims. Metadata indexes help discovery but do not replace reading the original paper, patent, or standard. Apply `source-registry-schema.md`.

## Records

<!-- source-registry:start -->
```json
[
  {
    "source_id": "global-crossref-metadata",
    "name": "Crossref Metadata",
    "publisher_type": "scholarly-metadata-registry",
    "evidence_tier": "near-primary",
    "geography": ["global"],
    "industries": ["cross-industry"],
    "claim_types": ["paper", "publication", "citation-metadata", "research-discovery"],
    "documents": ["article-metadata", "conference-metadata", "dataset-metadata", "DOI-record"],
    "access_mode": ["web", "API", "bulk-data"],
    "access_status": "public",
    "update_frequency": "continuous",
    "canonical_entry": "https://www.crossref.org/documentation/retrieve-metadata/",
    "fallback_sources": ["global-openalex", "publisher-site", "discipline-index"],
    "definition_risks": "Deposited metadata completeness, publication date variants, versions, retractions, and citation coverage require checks.",
    "independence_notes": "Crossref metadata comes from publishers and members; it is not independent confirmation of a paper's findings.",
    "registry_status": "registered",
    "last_reviewed": "2026-07-15"
  },
  {
    "source_id": "global-openalex",
    "name": "OpenAlex",
    "publisher_type": "scholarly-knowledge-graph",
    "evidence_tier": "near-primary",
    "geography": ["global"],
    "industries": ["cross-industry"],
    "claim_types": ["paper", "publication", "citation", "institution", "research-trend"],
    "documents": ["work-record", "author-record", "institution-record", "citation-graph"],
    "access_mode": ["web", "API", "snapshot"],
    "access_status": "public",
    "update_frequency": "continuous",
    "canonical_entry": "https://openalex.org/",
    "fallback_sources": ["global-crossref-metadata", "discipline-index", "publisher-site"],
    "definition_risks": "Work types, merged records, citation counts, source coverage, author identity, and update timing require checks.",
    "independence_notes": "OpenAlex can ingest Crossref and publisher metadata; OpenAlex and Crossref records for one paper are not independent evidence of findings.",
    "registry_status": "registered",
    "last_reviewed": "2026-07-15"
  },
  {
    "source_id": "us-pubmed",
    "name": "PubMed",
    "publisher_type": "government-bibliographic-database",
    "evidence_tier": "near-primary",
    "geography": ["global"],
    "industries": ["healthcare", "life-sciences", "medicine"],
    "claim_types": ["paper", "clinical-research", "biomedical-mechanism", "research-discovery"],
    "documents": ["citation-record", "abstract", "publication-type", "indexing-record"],
    "access_mode": ["web", "API"],
    "access_status": "public",
    "update_frequency": "daily",
    "canonical_entry": "https://pubmed.ncbi.nlm.nih.gov/",
    "fallback_sources": ["publisher-site", "clinical-trial-registry", "global-crossref-metadata"],
    "definition_risks": "Indexing coverage, publication type, preprint versus peer review, corrections, retractions, population, endpoint, and study design require checks.",
    "independence_notes": "PubMed indexes publisher records and abstracts; it is a discovery layer, not an independent replication of study results.",
    "registry_status": "registered",
    "last_reviewed": "2026-07-15"
  },
  {
    "source_id": "global-wipo-patentscope",
    "name": "WIPO PATENTSCOPE",
    "publisher_type": "international-patent-database",
    "evidence_tier": "primary",
    "geography": ["global", "PCT", "participating-national-collections"],
    "industries": ["cross-industry"],
    "claim_types": ["patent", "patent-application", "prior-art", "assignee", "technology-trend"],
    "documents": ["PCT-application", "bibliographic-record", "patent-document", "legal-status-record"],
    "access_mode": ["web", "PDF"],
    "access_status": "public",
    "update_frequency": "daily-and-weekly",
    "canonical_entry": "https://patentscope.wipo.int/search/en/search.jsf",
    "fallback_sources": ["national-patent-office", "global-espacenet"],
    "definition_risks": "Applications, publications, grants, family members, priority dates, jurisdictions, legal status, and assignee normalization must remain distinct.",
    "independence_notes": "The same patent family across jurisdictions is not multiple independent inventions; family and priority relationships must be deduplicated.",
    "registry_status": "registered",
    "last_reviewed": "2026-07-15"
  },
  {
    "source_id": "global-iso-standards",
    "name": "ISO Standards Catalogue",
    "publisher_type": "standards-organization",
    "evidence_tier": "primary",
    "geography": ["global"],
    "industries": ["cross-industry"],
    "claim_types": ["standard", "technical-requirement", "conformity", "technology-maturity"],
    "documents": ["standard-metadata", "standard", "technical-report"],
    "access_mode": ["web", "PDF"],
    "access_status": "paid-database",
    "update_frequency": "irregular",
    "canonical_entry": "https://www.iso.org/standards.html",
    "fallback_sources": ["national-standards-body", "industry-standards-organization", "official-standard-preview"],
    "definition_risks": "Edition, amendment, corrigendum, withdrawal status, normative versus informative text, and national adoption require checks.",
    "independence_notes": "National adoptions of the same ISO text are same-origin for the technical requirement unless they add independent national provisions.",
    "registry_status": "registered",
    "last_reviewed": "2026-07-15"
  }
]
```
<!-- source-registry:end -->
