# Industry Research Skill

An industry research skill for general AI agents. It supports industry
overviews, company and product positioning, industry mapping, lifecycle
assessment, profitability and valuation analysis, competitive analysis,
and structured Markdown research reports.

## Install

Install the skill from the repository with the open agent skills CLI:

```bash
npx skills add <github-owner>/industry-research-skill --skill industry-research
```

Replace `<github-owner>` with the GitHub account or organization that hosts
this repository.

## Repository Structure

```text
skills/industry-research/  Installable skill and supporting files
reports/                   Noncommercial example research reports
```

## Licensing

### Skill

The files under `skills/industry-research/` are licensed under the
[Apache License 2.0](LICENSE). Commercial use of the skill is permitted,
including using the skill to generate reports for commercial purposes.

A copy of the Apache License is also included inside the skill directory so
that the license accompanies standalone skill installations.

### Example Reports

The existing reports under `reports/` are licensed separately under the
[Creative Commons Attribution-NonCommercial 4.0 International License](reports/LICENSE).
They may not be used commercially without separate permission from the
copyright holder.

### Generated Outputs

Reports independently generated through normal use of the skill are not
automatically subject to the CC BY-NC 4.0 license applied to `reports/`.
Users may commercialize independently generated reports, subject to
applicable law, third-party rights, model-provider terms, and their own
professional or regulatory obligations.

Output that copies or is substantially derived from an existing report in
`reports/` remains subject to that report's license.

## Disclaimer

This project does not provide investment or other professional advice.
Users are responsible for verifying generated content and for all decisions,
distribution, and commercialization based on it. See [DISCLAIMER.md](DISCLAIMER.md)
for the complete disclaimer.
