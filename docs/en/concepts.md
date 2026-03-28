# Concepts

This engine evaluates alternatives by separating inputs, configuration, and computation.

## Candidate

A candidate is an entity being evaluated.

- identified by `candidate_id` and `candidate_name`
- described by **dimension values**
- dimensions are categorical (strings)

## Dimension

A dimension is a named attribute used in evaluation.

Examples (domain-specific, not part of the engine):
- assurance_level
- privacy_exposure
- centralization

The engine treats all dimensions generically.

## Policy

A policy defines how evaluation is performed.

It includes:

- **scales**: map dimension values to numeric scores
- **weights**: define how dimensions contribute to each label
- **interpretation**: thresholds for mapping scores to levels

Optional:
- patterns (descriptive)
- rules (annotations)

## Label

A label is an aggregate outcome computed from weighted dimensions.

Examples:
- minor_protection
- privacy_risk

Labels are defined entirely by the policy.

## Evaluation

Evaluation computes:

- a numeric score per label
- based on candidate values and policy weights

The engine performs no interpretation beyond numeric aggregation.

## Result

A result contains:

- the candidate
- computed scores
- optional derived levels (e.g., "low", "medium", "high")

## Separation of Concerns

- Candidates provide data
- Policies define meaning
- Evaluator performs computation
- Reporting presents results

The engine itself is domain-neutral.
