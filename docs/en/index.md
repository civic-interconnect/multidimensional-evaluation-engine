# multidimensional_evaluation_engine

The **multidimensional_evaluation_engine** provides a structured framework
for evaluating alternatives using typed inputs and configurable policy rules.

It includes components to:

- load candidate data (CSV to typed factor values)
- load policy configurations (TOML to factor specs, constraints, scoring rules)
- evaluate candidates using constraint and scoring logic
- compute aggregate scores and admissibility indicators
- map results to qualitative interpretations
- produce structured outputs for inspection and comparison

The engine is domain-neutral and supports scenarios where tradeoffs
must be made explicit without embedding domain-specific assumptions in the core.

## Installation

```shell
pip install multidimensional-evaluation-engine
```

Or with uv:

```shell
uv add multidimensional-evaluation-engine
uv sync
```

## Documentation

- API Reference
- Concepts
- Examples
- Troubleshooting
