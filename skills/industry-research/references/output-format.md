# Output Format

Use this file to control report length, analytical depth, and writing form. Shared titles and fields come only from `references/common-report-section-contract.md`; route order comes from the selected output contract and template. Select `output_language` through `references/report-language.md`. For paragraph-level expansion, use `references/section-depth-playbook.md`.

## Reference Report Patterns

Public industry reports commonly use executive summary or key takeaways before detailed chapters, table of contents or numbered trend sections, charts/exhibits/dashboards/data tables, methodology/scenario assumptions/data notes for forecasts, and endnotes or source links.

Examples used to set defaults include IEA World Energy Outlook, Deloitte industry outlooks, PwC Global Telecom and Entertainment & Media Outlook, and McKinsey Global Energy Perspective.

## Formal Research Report Layout

Standard and deep company/product reports must feel like formal institutional research, not a long chat answer. Use `references/institutional-report-benchmarks.md` as the style benchmark.

Before the main body, include:

1. Executive summary or report summary.
2. Key conclusions with evidence pointers.
3. Core metrics overview.
4. Exhibit list or exhibit placeholders.

In the main body:

1. Put industry analysis before target-specific company/product analysis.
2. Start every major chapter with a paragraph-level conclusion.
3. Include at least one evidence table, metric table, comparison table, or exhibit placeholder in each major analytical block when useful.
4. Keep prose as the main carrier of reasoning and use tables as support.

At the end, include:

1. Methodology and data source note.
2. Evidence quality summary.
3. Key assumptions.
4. Follow-up verification checklist.
5. Visible language-matched report compliance checklist.
6. The exact language-matched disclaimer from `references/report-language.md` as the final nonempty line.
## Explicit Short Answer Mode

Use short output only when the user explicitly asks for a short, simple, quick, brief, one-paragraph, one-sentence, no-detail, or no-expansion answer. Do not infer this mode from a narrow question.

If this mode is not explicitly triggered, do not use brief-only openings such as "quick take", "brief version", "first quick judgment", or "simple view". Produce the standard report structure.

## Output Modes

Use `references/report-output-modes.md` to choose delivery mode.

- Workspace Report File is the default mode for all standard or deep reports when file writing is available. It must create the full Markdown report under `reports/` and return only the path, short summary, and compliance/checker status in chat.
- Chat Report is the fallback when file writing is unavailable, the user explicitly asks not to create files, or the user triggers Explicit Short Answer Mode or unsaved Prompt Builder Mode. It must still output a complete Markdown report when used for a standard or deep report.
- File Report is triggered only when the user asks for PDF or another export format, or specifies an output path outside the default `reports/` location. Generic requests to generate or save Markdown use Workspace Report File.
- File Report must create Markdown first with filename format `YYYYMMDD_HHMMSS_主题.md`.
- If file writing or PDF export is not available, state the limitation and fall back to Chat Report.

## Default Length

The ranges below are Chinese-character baselines. For English and other alphabetic languages, preserve equivalent analytical coverage and section depth instead of treating them as literal word counts. The maintenance checker uses normalized content units defined in `references/report-language.md`.

- Explicit short answer: follow the user's requested brevity with no minimum length and a maximum of 1500 normalized content units, only when the user explicitly asks for a short, simple, quick, brief, one-paragraph, one-sentence, no-detail, or no-expansion answer.
- Standard industry overview report: 8000-12000 Chinese characters, 1 Mermaid industry map, 6-10 tables or exhibit placeholders.
- Standard industry-specific question report: 8000-12000 Chinese characters, with direct answer, issue tree, evidence chain, industry base, pressure test, and verification list.
- Standard company/product report: 10000-15000 Chinese characters, 1 Mermaid industry map, 8-14 tables or exhibit placeholders, and prose-first seven-module analysis.
- Standard listed-company capital-market report: 12000-18000 Chinese characters, with macro, meso, micro, capital-market expectation gap, and scenario analysis.
- Deep report: 18000-30000 Chinese characters, only when the user asks for depth or decision support. Prefer File Report for this mode.

## Section-Level Depth Contract

Total length is not enough. Standard and deep reports must have enough analytical body inside the required sections.

Apply `references/section-depth-playbook.md` when expanding major analytical sections. A section is not deep enough unless it contains distinct conclusion, evidence, mechanism, implication, and verification reasoning blocks where applicable.

For standard company/product reports:

- `3. 宏观环境分析`: cover at least 2-3 concrete macro variables that affect the industry and target, such as policy, consumption cycle, interest rate, cost, technology cycle, export/regional exposure, or broad risk appetite.
- `4. 中观行业分析`: include industry definition, relevant business-line split when applicable, supply-demand or competitive structure, key indicators, industry map, and lifecycle judgment.
- `5.1-5.7`: each seven-module subsection should reach roughly 300-500 Chinese characters.
- Priority modules should be longer when the user question depends on them. For listed-company capital-market questions, `5.4 盈利性`, `5.5 估值`, `5.6 外部因素`, and `5.7 景气度` should reach roughly 500-800 Chinese characters.
- `6. 微观公司/产品分析`: connect company facts to industry conclusions, not only describe the target.
- `10. 事实, 观点和推断分层`: include evidence tier, source status, and confidence for important claims.
- `8`, `10`, or `12. 多视角压力测试`: every formal route includes the four core perspectives, discloses review mode, and uses the substantive v65 nine-column closure summary.

For standard listed-company capital-market reports:

- `11. 资本市场表现与估值预期变化` should reach roughly 1800-3000 Chinese characters across `11.1-11.4`.
- `11.1` must separate price movement, timing, and likely catalysts.
- `11.2` must separate fundamental changes from expectation changes.
- `11.3` must explain valuation anchor, market expectation gap, and why the gap widened or narrowed.
- `11.4` must include upside triggers, downside risks, and scenarios without giving investment advice.

For deep reports:

- `5.1-5.7` should reach roughly 600-1000 Chinese characters each.
- If capital-market analysis applies, section `11` should reach roughly 3000-5000 Chinese characters.
- Deep reports should use File Report when the user asks to save, export, or generate a file.

Evidence gaps count toward depth only when they name the missing source, explain why it matters, and give a next verification step. Generic filler does not count.

## Universal Requirements

Every formal report must fulfill the shared analytical obligations in `references/common-report-section-contract.md`. Weight seven-module depth by lifecycle, question, and target position without changing canonical titles or fields.

## Prose-First Analysis

For standard and deep reports, the main analysis must be prose-first. Use paragraphs to explain reasoning, mechanisms, causality, and implications. Use tables only for summaries, comparisons, evidence chains, metrics, and checklists.

Do not replace core analysis with a single table. In company/product reports, the seven core modules must appear as seven analytical subsections, not as one summary table.

## Minimum Industry Overview Base

For standard and deep reports, especially company/product analysis, do not compress the industry overview base into one sentence or one generic paragraph. Include at least:

1. Industry one-sentence definition and research boundary.
2. Market size, growth rate, penetration rate, or the closest available proxy.
3. Industry map with vertical value chain and horizontal competitive structure.
4. Lifecycle judgment with evidence and counter-evidence when available.
5. Supply-demand, price, policy, regional/export, or other key industry variables relevant to the question.
6. All seven core modules. Do not omit modules because they seem less relevant. Weight the depth by lifecycle stage, user question, and target position.

Important industry judgments should prefer high-priority sources such as official statistics, regulators, industry associations, company filings, announcements, and financial reports. News, social media, and informal sources may be used only as supplementary signals unless independently verified.

## Seven-Module Section Granularity

Use all five canonical blocks from `references/common-report-section-contract.md` in every module. `references/section-depth-playbook.md` defines how to expand them. If evidence is insufficient, write the evidence gap and next verification step instead of filling the section with generic claims.

## Seven-Module Depth

For standard company/product reports, each seven-module subsection should reach roughly 300-500 Chinese characters. The goal is analysis density, not padding.

Each subsection must include at least two evidence points, data points, source pointers, or clearly marked evidence gaps, plus a causal mechanism and a concrete research implication for the applicable object.

For capital-market questions, profitability, valuation, external factors, and prosperity must be treated as priority modules and expanded more deeply than non-priority modules.

## Deep Research Visible Trace

Standard and deep reports must show concise traces of the Deep Research Engine:

1. Research plan summary.
2. Source matrix or evidence matrix.
3. Key evidence quality note.
4. Retrieval gap closure results and follow-up verification checklist.

Do not dump internal scratch work. Make the trace useful to the reader.

## Template Compliance Gate

Before producing a standard or deep company/product report, read `references/report-compliance.md` and apply its gate. If the draft fails the gate, rewrite the missing sections before final output. The final standard or deep report must include a visible `报告合规自检表` at the end.
## Industry Overview Base

1. Industry one-sentence definition.
2. Research boundary.
3. Industry map.
4. Lifecycle judgment.
5. Macro/meso analysis, and micro analysis only if useful.
6. Seven core modules.
7. Trend projection.
8. Risks, opportunities, and uncertainties.
9. Follow-up verification checklist.

For standard or deep industry overview reports, apply `references/industry-overview-output-contract.md`. Include research plan summary, source matrix, three-round retrieval closure results, fact/opinion/inference separation, multi-perspective pressure test, and final compliance checklist.

## Specific-Question Additions

Add direct answer, conclusion summary, issue tree, evidence chain, pressure test, and verification list. The direct answer must appear before the base report sections.

For standard or deep industry-specific question reports, apply `references/specific-question-output-contract.md`. Include research plan summary, source matrix, three-round retrieval closure results, and an evidence chain that separates facts, opinions, and inferences with evidence tier and source status.

## Company/Product Additions

Use the minimum industry overview base first, then add target position in the industry-map body, micro analysis, required SWOT, BCG matrix only for portfolio questions, required competitor comparison, and action suggestions. The company/product analysis must explain what the industry conclusions mean for the target, not just describe the target in isolation.

## Formatting Rules

- Use Markdown headings.
- Use `##` for major sections and `###` for subsections in formal reports.
- Do not use bold text such as `**1. Section**` as a substitute for Markdown headings.
- Use paragraphs for core reasoning.
- Use tables for comparisons, metrics, evidence chains, and summaries.
- Use Mermaid for industry maps.
- Mark weak evidence as weak evidence.
- Separate facts, opinions, and inferences when the distinction affects the conclusion.


