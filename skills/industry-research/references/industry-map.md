# Industry Map

The industry map is a mandatory formal report chapter. It must appear before lifecycle judgment and the seven core modules.

## Required Components

### 1. Vertical Value Chain

Map `Upstream -> Midstream -> Downstream -> Channels -> End customers`. Include key resources, production, distribution, and final demand.

### 2. Horizontal Competitive Structure

Show main players in each value-chain link, segments, substitute solutions, potential entrants, and platform/ecosystem players when relevant.

### 3. Target Position

- For industry overview: mark which value-chain links are included in the research scope.
- For company/product analysis: mark where the target sits and which links it depends on.
- For specific questions: highlight the part of the map most relevant to the question.

### 4. Production Factors

Identify labor, land/resources/sites/scenarios, capital, technology, and data.

### 5. Production Relations

Identify supplier, channel, customer, government/regulatory, platform/ecosystem, and capital relationships.

### 6. Key Flows

Map revenue flow, cost flow, data flow, traffic flow, and policy influence flow.

## Default Visual Output

Use Mermaid plus a compact table. If evidence is insufficient, mark the map as preliminary.

```mermaid
flowchart LR
  U[Upstream] --> M[Midstream]
  M --> D[Downstream]
  D --> C[Channels]
  C --> E[End customers]
```

## Link to Later Analysis

- Use production factors and relations in defensibility analysis.
- Use supplier/customer/channel power in profitability analysis.
- Use flows and bottlenecks to identify prosperity indicators.
