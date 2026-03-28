# Troubleshooting

Common issues when using `multidimensional_evaluation_engine`.

## CSV load errors

**Error:** Missing required columns

- Ensure the CSV includes:
  - `candidate_id`
  - `candidate_name`

All other columns are treated as dimensions.

## TOML load errors

**Error:** Missing required sections

- Ensure the policy includes:
  - `scales`
  - `weights`
  - `interpretation`

## Evaluation errors

**Error:** Unknown scale value

- A candidate contains a value not defined in the policy scale.
- Ensure all candidate dimension values exist in `policy.scales`.

**Error:** Missing dimension

- A policy references a dimension not present in the candidate data.
- Ensure CSV headers match policy dimension names exactly.

## Empty or unexpected results

- Verify that:
  - CSV and TOML files are loaded correctly
  - dimension names align between inputs
  - weights are defined for each label

## Notes

- The engine performs structural validation only.
- All semantics are defined by the input data and policy.
