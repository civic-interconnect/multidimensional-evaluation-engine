# Examples

Typical usage pattern for `multidimensional_evaluation_engine`.

```python
from pathlib import Path

from multidimensional_evaluation_engine.io.load_candidates import load_candidates
from multidimensional_evaluation_engine.io.load_policy import load_policy
from multidimensional_evaluation_engine.evaluation.evaluator import evaluate_candidate
from multidimensional_evaluation_engine.reporting.tables import format_results

# Load policy first (provides factor_specs)
policy = load_policy(Path("policy.toml"))

# Load candidates using factor_specs
candidates = load_candidates(Path("candidates.csv"), policy.factor_specs)

# Evaluate
results = [evaluate_candidate(c, policy) for c in candidates]

# Report
print(format_results(results))
