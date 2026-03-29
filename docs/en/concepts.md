# Concepts

This engine evaluates alternatives by separating recorded inputs, policy configuration, and computation.

## Candidate

A candidate is an entity being evaluated.

- identified by `candidate_id` and `candidate_name`
- described by **factor values**
- factor values are typed (binary, numeric, categorical)

## Factor

A factor is a named input variable used in evaluation.

Each factor has:

- a **structural form** (`FactorForm`)
  - binary
  - numeric
  - categorical
- an optional description and allowed values

Factors define the structure of inputs, independent of any scoring.

## Factor Value

A factor value is a recorded observation for a candidate.

- typed according to the factor’s form
- may include supporting evidence (optional)
- carries no scoring semantics

## Policy

A policy defines how evaluation is performed.

It includes:

- **factor_specs**: structural definitions of factors
- **constraint_rules**: admissibility conditions (pass/fail)
- **score_rules**: mappings from factor values to numeric scores
- **interpretation**: thresholds for mapping totals to qualitative levels

Policies introduce all scoring and decision semantics.

## Constraint Rule

A constraint rule defines a required condition.

- evaluated before or alongside scoring
- produces a binary admissibility outcome
- does not contribute directly to score magnitude

## Score Rule

A score rule maps a factor value to a numeric contribution.

Supported forms:

- categorical mappings
- numeric bands
- binary mappings

Each rule has an associated weight.

## Evaluation

Evaluation computes:

- per-rule scores
- a total aggregated score
- an admissibility indicator
- optional interpretation labels

The evaluator applies policy logic to candidate factor values.

## Result

A result contains:

- the candidate
- computed scores (including total and admissibility)
- optional interpretation indicators (e.g., `interpretation:high`)

## Separation of Concerns

- Candidates provide recorded values
- Factors define input structure
- Policies define scoring and constraints
- Evaluator applies policy to candidates
- Reporting presents results

The engine itself remains domain-neutral and pre-normative.
