---
name: industry-research
description: Industry research assistant for general AI agents. Use for industry overviews, industry question decomposition, company or product positioning, industry maps, lifecycle assessment, information source selection, profitability analysis, valuation logic, prosperity indicators, PEST analysis, competitive structure, risk and opportunity analysis, and Markdown research report generation.
---

# Industry Research

Use this skill to produce structured industry research like a business analyst. The default output is Markdown. Do not generate PDF, PPT, webpage, or XMind unless the user explicitly asks after the Markdown report is complete.

## Core Workflow

1. Classify the user request.
2. Select the output language using `references/report-language.md`.
3. Build an internal research brief that translates the user's request into a report route, template, source plan, output language, and depth contract; use visible brief or prompt mode only when triggered by `references/research-brief-builder.md`.
4. Define the problem and research boundary.
5. Decompose the problem if the user asks a specific question.
6. Build a WBS research plan and run the Deep Research Engine for standard or deep reports.
7. Build and show the industry map before lifecycle analysis.
8. Collect, clean, classify, compress, and synthesize information.
9. Judge industry lifecycle stage.
10. Analyze the seven core modules.
11. Run multi-agent pressure testing by default.
12. Output the report using the matching template and selected language.

## Request Types

Classify the request by the user's underlying intent, not by whether the wording is formal or complete.

- Industry overview: the user wants to understand an industry, market, sector, track, business category, or opportunity space, even if the industry boundary is vague.
- Industry-specific question: the user asks about a phenomenon, cause, trend, opportunity, risk, competition, price war, policy impact, profitability, lifecycle, or future direction related to an industry.
- Company/product analysis: the user asks about a company, product, project, brand, business line, or startup idea, and its position, prospects, risks, or competitiveness in an industry context.

If a request matches multiple types, use the highest-specificity applicable report type while keeping the industry overview base. Company/product analysis overrides generic industry-specific question routing. Listed-company stock price, valuation, expectation gap, market-cap repair, investability, or rise/fall questions override generic specific-question routing and must use the company/product output contract plus the capital-market module. If the user wording is vague, infer the likely intent, state assumptions, and ask only the minimum necessary boundary questions.

All three report types must use the industry overview report as the base. Specific-question and company/product reports add modules; they must not skip the industry map, lifecycle judgment, or seven-module industry analysis.

## Progressive Loading

Read only the needed reference files:

- User intake and boundary clarification: `references/user-intake.md`.
- Research brief, visible requirement brief, and reusable prompt builder: `references/research-brief-builder.md`.
- Problem decomposition and issue trees: `references/problem-decomposition.md`.
- Routing sanity check and maintenance regression prompts: `references/routing-sanity-check.md`.
- Report quality regression tests, maintenance only: `references/report-regression-tests.md`.
- Industry overview output contract: `references/industry-overview-output-contract.md`.
- Specific-question output contract: `references/specific-question-output-contract.md`.
- WBS research planning: `references/research-plan.md`.
- Deep Research Engine for standard and deep reports: `references/deep-research-engine.md`.
- Provider-neutral retrieval execution, recursive follow-up, budgets, deduplication, and Research Run artifacts: `references/deep-search-protocol.md`.
- Analysis layer selection: `references/layered-analysis.md`.
- Industry map: `references/industry-map.md`.
- Research pipeline, fact/opinion/inference rules, and multi-agent collection loop: `references/research-pipeline.md`.
- Information source selection and Claim routing: `references/information-sources.md`.
- Source Registry, Claim, and Evidence Ledger contracts for standard and deep reports: `references/source-registry-schema.md`.
- Industry size, policy, regulation, supply, demand, trade, and macro sources: `references/source-registry-official-and-industry.md`.
- Company, filing, capital-market, financing, and M&A sources: `references/source-registry-company-and-market.md`.
- Paper, patent, standard, and technology sources: `references/source-registry-research-and-technology.md`.
- Lifecycle judgment: `references/lifecycle.md`.
- Seven core modules: `references/seven-modules.md`.
- Profitability details: `references/profitability-indicators.md`.
- Valuation logic: `references/valuation-logic.md`.
- Prosperity indicators: `references/prosperity-indicators.md`.
- Multi-agent pressure testing: `references/pressure-test.md`.
- Report output modes: `references/report-output-modes.md`.
- Chinese-or-English output selection and translated heading contract: `references/report-language.md`.
- Output rules and report depth: `references/output-format.md`.
- Section depth expansion playbook: `references/section-depth-playbook.md`.
- Report depth scoring rubric: `references/report-depth-rubric.md`.
- Report compliance gate: `references/report-compliance.md`.
- Primary-source-first evidence rules: `references/primary-source-first.md`.
- Company/product output contract: `references/company-product-output-contract.md`.
- Company/product few-shot examples: `references/company-product-few-shot.md`.
- Institutional report style benchmarks: `references/institutional-report-benchmarks.md`.
- Capital-market question module: read `references/capital-market-question.md` only when the user asks about stock price movement, valuation, market expectation, investability, market-cap repair, or rise/fall potential.

Use templates from `assets/`:

- Industry overview: `assets/industry-overview-template.md`.
- Industry-specific question: `assets/specific-question-template.md`.
- Company/product analysis: `assets/company-product-template.md`.
- Reusable research prompt, only when the user asks for a prompt or research brief: `assets/research-prompt-template.md`.

Maintenance scripts:

- Deterministic Markdown report checker, maintenance only: `scripts/report_contract_check.py`.
- Batch Markdown report checker, maintenance only: `scripts/report_batch_check.py`.
- Source Registry and Evidence Ledger contract checker, maintenance only: `scripts/source_contract_check.py`.
- Deep Search Protocol and Research Run contract checker, maintenance only: `scripts/deep_search_contract_check.py`.

For industry overview reports, read `references/research-brief-builder.md`, `assets/industry-overview-template.md`, `references/industry-overview-output-contract.md`, `references/output-format.md`, `references/section-depth-playbook.md`, `references/report-depth-rubric.md`, `references/report-compliance.md`, and `references/layered-analysis.md` before writing the report.

For company/product analysis, read `references/research-brief-builder.md`, `assets/company-product-template.md`, `references/company-product-output-contract.md`, `references/primary-source-first.md`, `references/output-format.md`, `references/section-depth-playbook.md`, `references/report-depth-rubric.md`, `references/report-compliance.md`, and `references/layered-analysis.md` before writing the report. For standard or deep company/product reports, also read `references/company-product-few-shot.md` and `references/institutional-report-benchmarks.md`.

For industry-specific questions, read `references/research-brief-builder.md`, `assets/specific-question-template.md`, `references/specific-question-output-contract.md`, `references/output-format.md`, `references/section-depth-playbook.md`, `references/report-depth-rubric.md`, `references/report-compliance.md`, and `references/layered-analysis.md` before writing the report.

When the user asks to generate a prompt, summarize requirements, set the research target, clarify the research scope, or create a reusable instruction for another agent, read `references/research-brief-builder.md` and `assets/research-prompt-template.md`, then output the filled prompt instead of the report.

When maintaining or validating this skill after edits, read `references/report-regression-tests.md` and use it with `references/routing-sanity-check.md`. Use `scripts/report_contract_check.py` on generated Markdown reports, `scripts/report_batch_check.py` for a directory of generated reports, `scripts/source_contract_check.py` for Source Registry or Evidence Ledger contracts, and `scripts/deep_search_contract_check.py` for Deep Search Protocol or Research Run contracts. Do not load these maintenance resources for normal report generation.

For every standard or deep report, read `references/information-sources.md` and `references/source-registry-schema.md`, then load only the registry matching each high-impact Claim. Mixed questions may load multiple registries. Keep the Evidence Ledger internal.

## Hard Rules

- Classify ambiguous user requests by intent. Do not require users to phrase requests in formal industry-research language.
- Select `output_language` as `zh` or `en` before drafting. Follow an explicit Chinese or English request; map unsupported languages to English through `references/report-language.md`. Apply the language contract to every reader-facing heading, label, table, caption, paragraph, visible brief, and Prompt Builder output. Do not mix Chinese and English contract headings.
- Start every standard or deep formal report with exactly one dynamic H1 title, place the language-matched route opening immediately after it, and end with the exact language-matched disclaimer from `references/report-language.md`. Do not apply this report shell to short answers, Prompt Builder outputs, or visible research briefs.
- Before drafting any standard or deep report, build an internal research brief using `references/research-brief-builder.md`. Do not output the brief unless the user asks for a prompt, requirement summary, or reusable instruction.
- For complex standard or deep reports with materially missing boundaries, apply the visible brief gate in `references/research-brief-builder.md` before drafting; visible brief mode is a pre-report contract, not a short answer.
- Before choosing a template, apply `references/routing-sanity-check.md` to confirm the request type, selected layers, conditional modules, and opening rule.
- For industry overview reports, apply `references/industry-overview-output-contract.md`: preserve the industry overview template, include research plan, source matrix, fact/opinion/inference separation, pressure test, and final compliance checklist.
- For pure industry-specific questions, apply `references/specific-question-output-contract.md`: start with one H1 and then the language-matched `1. 直接回答` or `1. Direct Answer`, preserve the specific-question template, and keep facts, opinions, and inferences separated in the evidence chain.
- Always state research boundary: geography, time horizon, industry scope, included items, excluded items, and assumptions.
- Always include an industry map as a formal report chapter before lifecycle and seven-module analysis.
- For company/product analysis, do not compress the industry overview base into one sentence or one generic paragraph; include the minimum industry overview base before target-specific analysis.
- For standard or deep company/product reports, use the main section skeleton from `assets/company-product-template.md` first, then fill the content. Do not freely invent a different report structure.
- For standard or deep company/product reports, apply `references/company-product-output-contract.md`: copy the required language-matched heading skeleton first, start with one H1 followed by `0. 研报前置区` or `0. Research Front Matter`, scan for required headings before final output, and rewrite if any required heading is missing.
- If a standard or deep company/product report misses required template skeleton sections, treat it as a compressed report failure and rewrite before final output.
- Standard and deep reports must not be compressed only because the answer is delivered in chat. Follow the required professional report depth in `references/output-format.md`.
- Standard and deep reports must satisfy the section-level depth contract in `references/output-format.md`; correct headings without enough analytical body are not sufficient.
- Standard and deep reports must apply `references/section-depth-playbook.md`; major analytical sections need conclusion, evidence, mechanism, implication, and verification blocks.
- Standard and deep reports must apply `references/report-depth-rubric.md`; sections below the rubric threshold must be rewritten before final output.
- Use Workspace Report File by default for all standard or deep reports when file writing is available: create a Markdown report under `reports/` using `YYYYMMDD_HHMMSS_主题.md`, then answer in chat with the path, short summary, and compliance/checker status. Use Chat Report as the fallback when file writing is unavailable, the user explicitly asks not to create files, the user explicitly triggers short-answer mode, or the user asks for Prompt Builder Mode without asking to save the prompt.
- Use File Report/PDF export only when the user explicitly asks for export/PDF or a specific file path. File Report must create Markdown first using `YYYYMMDD_HHMMSS_主题.md`.
- Existing report files, active editor tabs, prior generated reports, or forward-test artifacts must not downgrade a standard or deep report request into a summary. Use them only as context unless the user explicitly asks to summarize, condense, review, compare, or continue that file.
- Standard and deep reports must include the language-matched visible `报告合规自检表` or `Report Compliance Checklist` immediately before the fixed final disclaimer.
- For standard or deep company/product reports, do not replace the seven core modules with a single summary table; write each module as its own analytical subsection.
- If the user does not explicitly trigger Explicit Short Answer Mode, run company/product analysis as a standard report; do not output a brief, quick-comment, or executive-brief-only structure.
- Explicit Short Answer Mode is allowed only when the user explicitly asks for a short, brief, quick, simple, one-paragraph, one-sentence, or no-detail answer. Do not choose this mode by inference.
- If Explicit Short Answer Mode is not triggered, do not open with phrases like "brief version", "quick take", "first quick judgment", or "simple view"; produce the standard report structure directly.
- For standard or deep reports, run the Deep Research Engine before writing the report.
- When the Deep Research Engine requests the first retrieval pass or a gap-closure round, use `references/deep-search-protocol.md`; keep Engine research policy and Protocol retrieval execution separate.
- For standard or deep reports, assign stable `claim_id` and `source_id` values and record actual access and independence outcomes through the Evidence Ledger contract in `references/source-registry-schema.md`.
- For standard or deep reports, apply the Retrieval Gap Closure Loop in `references/deep-research-engine.md`: high-impact gaps require up to three targeted closure rounds before final drafting, and unresolved gaps must show round-by-round attempted sources, status, unresolved reason, impact, and next primary or near-primary source.
- Use the layer selector: include macro and meso layers for industry research, include micro only when the request involves a company/product/project/player, and include capital-market layer only for stock price, valuation, expectation, investability, market-cap repair, or rise/fall questions.
- Stock price, valuation, expectation gap, and rise/fall questions about a listed company must be treated as company/product analysis with a conditional capital-market module, not as a quick market comment.
- Stock price, valuation, expectation gap, and rise/fall questions about a listed company must follow the company/product output contract and the standard listed-company capital-market report shape unless Explicit Short Answer Mode is triggered.
- For capital-market questions, keep the company/product template skeleton and the capital-market section. Do not replace it with a three-part structure such as "why it fell", "what to watch", and "my judgment".
- Listed-company capital-market reports must include `4.0 多业务线中观拆分`; for genuinely single-business targets, use `4.0` to explain why no material split is needed.
- Distinguish facts, opinions, and inferences. Never present opinions as facts.
- Cite sources or clearly mark missing evidence. Do not invent data.
- For company/product and listed-company capital-market reports, apply `references/primary-source-first.md`: try primary or near-primary sources first, use media summaries only as supplementary signals or opinions, and disclose primary-source retrieval gaps in `2.2` and `2.3`.
- Use PEST only inside external factors unless the user explicitly asks to explain the PEST framework.
- Use SWOT only for company/product/project analysis, not as the default industry analysis structure.
- Use BCG matrix only for business or product portfolio analysis.
- Use multi-agent division of work by default. If the active environment has no multi-agent capability, explicitly degrade to single-agent simulated perspectives.
- For pure industry-specific questions, answer the user's question first, then present the industry analysis. Do not apply this direct-answer rule to company/product reports or listed-company capital-market questions; those must preserve the company/product output contract and start with the language-matched company front matter heading.
