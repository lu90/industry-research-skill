# Report Output Modes

Use this file to choose the report delivery mode. Output mode controls where the report goes, not the analytical depth.

## Workspace Report File

Workspace Report File is the default delivery mode for all standard or deep reports when the environment can write files.

Use Workspace Report File for standard or deep industry overview, industry-specific question, company/product, and listed-company capital-market reports, unless the user explicitly asks not to create files or explicitly triggers short-answer mode. Prompt Builder Mode remains a chat response unless the user asks to save the generated prompt.

Rules:

- Create `reports/` if it does not exist, then create a Markdown report file under `reports/`.
- Use the filename format `YYYYMMDD_HHMMSS_主题.md`.
- Keep the topic short, readable, and filesystem-safe.
- The report file must contain the full required template skeleton, source matrix, evidence gaps, independent seven modules, pressure test, and compliance checklist for the selected report type. Include methodology, verification appendix, and `11.1-11.4` only where the selected route contract requires them.
- After creating the file, resolve the active `industry-research` Skill root from the loaded `SKILL.md`, then run `python -B "<skill-root>/scripts/report_contract_check.py" <report.md> --profile <profile>` when Python execution is available.
- In chat, provide only the file path, report title, short summary, and whether the compliance/checker passed.
- Do not create PDF unless the user explicitly asks for PDF.
- If file writing is unavailable, fall back to Chat Report and output the complete Markdown report in the conversation.

## Chat Report

Chat Report is the fallback mode.

Use Chat Report when the user explicitly asks not to create files, when file writing is unavailable, for Explicit Short Answer Mode, or for Prompt Builder Mode unless the user asks to save the generated prompt.

Rules:

- Output the complete Markdown report in the conversation.
- Do not shorten a standard or deep report only because it is in chat.
- Do not shorten a standard or deep report only because an existing report file, active editor tab, prior generated report, or forward-test artifact is available.
- If an existing report is available and the user asks the same research question again, treat the file as optional context, not as permission to output a condensed judgment.
- A same-topic rerun creates a new `run_id`, Research Run, and report. Link lineage through `parent_run_id` or `supersedes` when applicable; do not overwrite the prior Run or report.
- Summarize, condense, review, compare, or continue an existing report only when the user explicitly asks for that file operation.
- Keep the same skeleton, depth, source discipline, and compliance checklist required by the report type.
- If the report is very long, use clear Markdown headings and compact tables, but do not collapse required sections.
- For any standard or deep report, do not keep the full report only in chat when file writing is available. Create the workspace report file instead.

## File Report

File Report is the explicit export variant. Use it when the user asks for PDF or another export format, or supplies a specific output path outside the default `reports/` location. A generic request to generate or save a Markdown research report still uses Workspace Report File, because that mode already writes the complete report to disk.

Rules:

- Create a Markdown report file first.
- Use the user-specified path when provided. Otherwise use `reports/` for an explicitly requested export.
- Use the filename format `YYYYMMDD_HHMMSS_主题.md`.
- Keep the topic short, readable, and filesystem-safe.
- If the user also asks for PDF, generate PDF after the Markdown report when the environment supports it, using the same basename and `.pdf`.
- If the environment does not support file writing or PDF export, say so and fall back to Chat Report.
- In the chat response after file creation, provide only the file path, report title, short summary, and whether the compliance checklist passed.

## Depth

Workspace Report File and File Report do not replace research quality. Standard and deep reports still need the full template skeleton, Deep Research visible trace, source matrix, seven-module analysis, and final compliance checklist.

Use File Report only for an explicit export format or specific output path. For all standard and deep reports, including long reports and generic requests to generate or save Markdown, use Workspace Report File by default when file writing is available. Without file writing capability, keep Chat Report and preserve the full structure.
