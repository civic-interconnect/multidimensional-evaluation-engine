# Troubleshooting

Common issues when using `multidimensional_evaluation_engine`.

## CSV load errors

**Error:** Missing required columns

- Ensure the CSV includes:
  - `candidate_id`
  - `candidate_name`

All other columns are treated as **factor inputs**.



**Error:** Unknown factor column

- A CSV column does not match any `factor_id` in the policy.
- Ensure all CSV headers (except reserved fields) match `policy.factor_specs`.



**Error:** Value cannot be parsed for factor form

- A value cannot be coerced to the expected type:
  - binary → must be true/false-like
  - numeric → must be parseable as float
  - categorical → must be a valid string (and optionally in allowed_values)

- Ensure CSV values are consistent with the factor’s `form`.



## TOML load errors

**Error:** Missing required sections

- Ensure the policy includes:
  - `factor_specs`
  - `score_rules`
  - `interpretation`

Optional:
- `constraint_rules`
- `metadata`



**Error:** Invalid rule configuration

- A `ScoreRule` must define exactly one of:
  - `categorical_scores`
  - `numeric_bands`
  - `binary_scores`

- Ensure rule definitions are structurally valid.



## Evaluation errors

**Error:** Missing factor value

- A required `factor_id` is referenced by a rule but not present in the candidate.
- Ensure CSV columns cover all factors used in policy rules.



**Error:** Unknown categorical value

- A categorical value is not defined in `categorical_scores`.
- Ensure all candidate values are included in the rule mapping.



**Error:** Numeric value did not match any band

- A numeric value falls outside all defined `numeric_bands`.
- Ensure bands fully cover the expected input range.



**Error:** Cannot coerce value

- A value cannot be interpreted as the required type (e.g., invalid boolean).
- Ensure inputs match the expected factor form.



## Unexpected results

- Verify that:
  - CSV headers align with `factor_specs`
  - factor forms match the actual data
  - score rules are defined for all relevant factors
  - numeric bands cover the full domain
  - constraint rules are correctly specified



## Notes

- The engine performs **structural and type validation**, not domain validation.
- All scoring, constraints, and interpretation are defined by the policy.
- The engine does not impose causal or normative assumptions.
