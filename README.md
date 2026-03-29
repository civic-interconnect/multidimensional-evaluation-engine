# multidimensional-evaluation-engine

[![PyPI version](https://img.shields.io/pypi/v/multidimensional-evaluation-engine)](https://pypi.org/project/multidimensional-evaluation-engine/)
[![Latest Release](https://img.shields.io/github/v/release/civic-interconnect/multidimensional-evaluation-engine)](https://github.com/civic-interconnect/multidimensional-evaluation-engine/releases)
[![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://civic-interconnect.github.io/multidimensional-evaluation-engine/)
[![CI Status](https://github.com/civic-interconnect/multidimensional-evaluation-engine/actions/workflows/ci-python-zensical.yml/badge.svg?branch=main)](https://github.com/civic-interconnect/multidimensional-evaluation-engine/actions/workflows/ci-python-zensical.yml)
[![Deploy-Docs](https://github.com/civic-interconnect/multidimensional-evaluation-engine/actions/workflows/deploy-zensical.yml/badge.svg?branch=main)](https://github.com/civic-interconnect/multidimensional-evaluation-engine/actions/workflows/deploy-zensical.yml)
[![Check Links](https://github.com/civic-interconnect/multidimensional-evaluation-engine/actions/workflows/links.yml/badge.svg)](https://github.com/civic-interconnect/multidimensional-evaluation-engine/actions/workflows/links.yml)
[![Dependabot](https://img.shields.io/badge/Dependabot-enabled-brightgreen.svg)](https://github.com/civic-interconnect/multidimensional-evaluation-engine/security)
[![Python 3.14+](https://img.shields.io/badge/python-3.14%2B-blue?logo=python)](#)
[![MIT](https://img.shields.io/badge/license-see%20LICENSE-yellow.svg)](./LICENSE)

> A domain-neutral engine for multidimensional evaluation under explicit policy assumptions.


## What the Engine Does

The engine:

- applies a configurable policy
- evaluates candidate configurations
- computes scores using rule-based mappings
- evaluates constraint-based admissibility
- derives interpretation indicators from score thresholds
- supports structured comparison across alternative designs

The system is designed to make assumptions explicit and results inspectable.

## Important Note

This project does not advocate for a specific solution.

It provides a structured way to examine:

- how design choices affect outcomes
- where tradeoffs become significant
- how governance assumptions shape results

## This Project

This project provides a reusable framework for multidimensional evaluation under explicit assumptions and constraints.
It:

- supports policy-driven evaluation across multiple domains
- represents inputs as typed factors (binary, numeric, categorical)
- applies constraint rules and score rules defined in policy
- separates input structure, policy logic, and evaluation

The goal is to provide a stable core that can support multiple
exploratory systems built on a shared evaluation model.

## Contribution

The contribution is the engine for structured multidimensional evaluation,
not the specific values used in any given scenario.

- Factors and their structure are explicitly defined
- Scoring and constraints are policy-driven
- Assumptions are explicit and inspectable
- Results are comparative and scenario-dependent
- The core logic is domain-neutral

This project does not determine outcomes or recommend decisions.
It provides a way to examine how different
assumptions and constraints shape results.

## Working Files

Working files are found in these areas:

- **docs/** - documentation and examples
- **src/** - implementation

## Capabilities

- Loads policy definitions (factor specs, constraint rules, score rules)
- Evaluates candidates using typed factor values
- Computes score profiles, admissibility, and interpretation indicators
- Supports reusable integration into domain-specific explorer systems

## Command Reference

<details>
<summary>Show command reference</summary>

### In a machine terminal (open in your `Repos` folder)

After you get a copy of this repo in your own GitHub account,
open a machine terminal in your `Repos` folder:

```shell
# Replace username with YOUR GitHub username.
git clone https://github.com/username/multidimensional-evaluation-engine

cd multidimensional-evaluation-engine
code .
```

### In a VS Code terminal

```shell
# Set Up the Environment
uv self update
uv python pin 3.14
uv sync --extra dev --extra docs --upgrade
uvx pre-commit install

# Local format + lint
uv run ruff format --check .
uv run ruff check .

# Pre-commit (enforce repo rules)
git add -A
uvx pre-commit run --all-files
# repeat if changes were made
git add -A
uvx pre-commit run --all-files

# Static + security + dependency checks
uv run validate-pyproject pyproject.toml
uv run deptry .
uv run bandit -c pyproject.toml -r src

# Tests (after static checks pass)
uv run pytest --cov=src --cov-report=term-missing

# Docs build (after everything passes)
uv run zensical build

# Commit and push
git add -A
git commit -m "update"
git push -u origin main

# Reinstall + sanity checks (post-push validation)
uv sync --reinstall

uv run python -c "import multidimensional_evaluation_engine; print(multidimensional_evaluation_engine.__version__)"
uv run python -c "from multidimensional_evaluation_engine.evaluation.evaluator import evaluate_candidate; print(evaluate_candidate)"

# Build artifacts (verify release)
uv build
```

</details>

## Annotations

[ANNOTATIONS.md](./ANNOTATIONS.md)

## Citation

[CITATION.cff](./CITATION.cff)

## License

[MIT](./LICENSE)

## SE Manifest

[SE_MANIFEST.md](./SE_MANIFEST.toml)
