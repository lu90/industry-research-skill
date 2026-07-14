# Research Pipeline

Use this file for information collection, cleaning, compression, and synthesis.

## Pipeline

1. Input information.
2. Clean information.
3. Classify as fact, opinion, or inference.
4. Group and find patterns.
5. Extract key points.
6. Synthesize core conclusions.

## Evidence Types

| Type | Definition | Weight | Output rule |
|---|---|---|---|
| Fact | Official data, policy, filing, financial statement, announcement, first-party statistic, credible primary source | Highest | Use as core evidence. Include date and scope. |
| Opinion | Research report, media commentary, expert view, interview judgment | Medium | Mark source and standpoint. Cross-check. |
| Inference | Agent conclusion based on facts and opinions | Conditional | Explain reasoning and uncertainty. |

## Multi-Agent Collection Loop

Default to multi-agent division when available:

- Macro researcher: policy, economy, social/cultural, technology.
- Industry researcher: market size, value chain, competition, lifecycle.
- Data researcher: indicators, facts, time series, charts.
- Company/product researcher: target company/product and representative players.
- Synthesis lead: compresses findings and resolves contradictions.

If the environment does not support multi-agent execution, state the limitation and simulate these roles in one agent.

## Quality Rules

- Do not invent data.
- Prefer primary sources for factual claims.
- Use multiple sources when a data point can be disputed.
- Treat outdated data as lower confidence.
- Separate current facts from forecasts.
- For forecasts, always state assumptions and scenario context.
