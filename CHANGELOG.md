# Changelog

All notable changes to this project will be documented in this file.

The format is based on **[Keep a Changelog](https://keepachangelog.com/en/1.1.0/)**
and this project adheres to **[Semantic Versioning](https://semver.org/spec/v2.0.0.html)**.

## [Unreleased]

---

## [0.2.1] - 2026-03-28

### Fixed

- Score evaluation no longer raises for numeric band misses on inadmissible sites; unmatched values are skipped.

---

## [0.2.0] - 2026-03-28

### Added

- Introduced typed factor model:
  - `FactorSpec` for structural definition of inputs
  - `FactorValue` for typed candidate observations (binary, numeric, categorical)
  - optional evidence references for recorded values
- Added rule-based policy system:
  - `ConstraintRule` for admissibility conditions
  - `ScoreRule` supporting categorical mappings, numeric bands, and binary scoring
- Added explicit admissibility evaluation alongside scoring
- Added interpretation indicators derived from policy thresholds
- Added factor-aware candidate loading (`load_candidates` now constructs typed values)

### Changed

- Replaced dimension-based model with factor-based model
- Replaced scales and weights with rule-based scoring
- Updated `Policy` to include:
  - `factor_specs`
  - `constraint_rules`
  - `score_rules`
  - `interpretation`
- Updated evaluator to:
  - operate on typed factor values
  - apply constraint rules and score rules
  - compute total score and admissibility indicator
- Updated reporting to:
  - separate interpretation indicators from numeric scores
- Updated documentation to reflect factor and rule-based architecture

### Removed

- Removed dimension-based scoring model:
  - `dimensions` on `Candidate`
  - `scales` and `weights` in `Policy`
- Removed implicit string-only input handling in favor of typed factor values

### Fixed

- Improved type safety and validation across candidate loading and evaluation
- Updated documentation

---

## [0.1.1] - 2026-03-27

### Fixed

- Expose package version in multidimensional_evaluation_engine/**init**.py

---

## [0.1.0] - 2026-03-27

### Added

- Initial release of multidimensional evaluation engine
- Core domain models (Candidate, CandidateResult)
- Policy model (scales, weights, interpretation)
- CSV and TOML loaders
- Evaluation logic for weighted scoring
- Plain-text reporting utilities
- Documentation site scaffolding (Zensical)
- CI/CD: GitHub Actions for validation and documentation
- Packaging configuration

---

## Notes on versioning and releases

- We use **SemVer**:
  - **MAJOR** – breaking schema/OpenAPI changes
  - **MINOR** – backward-compatible additions
  - **PATCH** – clarifications, docs, tooling
- Versions are driven by git tags via `setuptools_scm`. Tag `vX.Y.Z` to release.
- Docs are deployed per version tag and aliased to **latest**.

### Example commands

```shell
# if needed
git tag -d v0.2.1
git push origin :refs/tags/v0.2.1

# tag release
git tag v0.2.1 -m "0.2.1"
git push origin v0.2.1
```

[Unreleased]: https://github.com/civic-interconnect/multidimensional-evaluation-engine/compare/v0.2.1...HEAD
[0.2.1]: https://github.com/civic-interconnect/multidimensional-evaluation-engine/releases/tag/v0.2.1
[0.2.0]: https://github.com/civic-interconnect/multidimensional-evaluation-engine/releases/tag/v0.2.0
[0.1.1]: https://github.com/civic-interconnect/multidimensional-evaluation-engine/releases/tag/v0.1.1
[0.1.0]: https://github.com/civic-interconnect/multidimensional-evaluation-engine/releases/tag/v0.1.0
