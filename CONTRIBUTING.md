# Contributing

Thank you for helping improve the Industry Research Skill. Contributions in
English or Chinese are welcome.

## Before You Start

- Search existing Issues and Pull Requests before opening a new one.
- Open an Issue before proposing a large change to the research framework,
  report contracts, licensing, or repository structure.
- Small documentation fixes and narrowly scoped bug fixes may go directly to
  a Pull Request.
- Keep each Pull Request focused on one problem.

For security vulnerabilities, do not open a public Issue. Follow
[SECURITY.md](SECURITY.md) instead.

## Useful Contributions

- Reproducible Skill or checker failures
- Corrections to research-source routing or evidence rules
- Improvements to report contracts, templates, and documentation
- Tests that demonstrate a real failure or regression
- Compatibility findings from a clearly identified agent runtime

Requests for personal investment advice, target prices, guaranteed returns,
or unsupported promotional claims are outside the project scope.

## Pull Request Requirements

Describe:

1. The problem being solved.
2. The proposed change and its scope.
3. The validation performed.
4. Any compatibility, evidence, or licensing implications.

When changing research rules, templates, references, or checkers, include a
focused test or reproducible example whenever practical. Do not combine
unrelated formatting or refactoring changes with the contribution.

Run the relevant deterministic checks from the repository root:

```bash
python -B skills/industry-research/scripts/report_contract_check.py --self-test
python -B skills/industry-research/scripts/report_batch_check.py --self-test
python -B skills/industry-research/scripts/source_contract_check.py --self-test
python -B skills/industry-research/scripts/deep_search_contract_check.py --self-test
python -B skills/industry-research/scripts/report_batch_check.py tests/fixtures/v63/valid --json
```

Maintainers may request additional regression or forward-agent testing for
changes that affect research behavior.

## Evidence and Content Safety

- Do not include API keys, credentials, private datasets, personal data, or
  confidential client information.
- Do not submit fabricated citations or sources that you did not inspect.
- Identify important source limitations, access constraints, and unresolved
  evidence gaps.
- Do not copy paywalled or copyrighted material beyond what applicable law and
  the source license permit.

## Contribution Licensing

Files under `skills/industry-research/`, repository documentation, tests, and
automation are accepted under the Apache License 2.0 unless a file states
otherwise.

Example reports under `reports/` use the separate CC BY-NC 4.0 license in
`reports/LICENSE`. A contribution to that directory must be content you have
the right to submit and will be distributed under that license.

By submitting a contribution, you confirm that you have the right to provide
it under the license applicable to the files you change.
