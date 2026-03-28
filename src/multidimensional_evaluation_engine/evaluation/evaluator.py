"""evaluation/evaluator.py: Evaluate candidates against policy."""

from ..domain.candidates import Candidate
from ..domain.results import CandidateResult
from ..policy.policy import Policy


def evaluate_candidate(
    candidate: Candidate,
    policy: Policy,
) -> CandidateResult:
    """Evaluate a candidate under a policy.

    Computes weighted scores for each label defined in the policy.

    Args:
        candidate: Candidate with dimension values.
        policy: Policy defining scales and weights.

    Returns:
        CandidateResult containing computed scores.

    Raises:
        KeyError: If a required dimension is missing from the candidate.
        KeyError: If a dimension is not defined in the policy scales.
        KeyError: If a candidate value is not defined in the corresponding scale.
    """
    scores: dict[str, float] = {}

    for label, weights in policy.weights.items():
        total = 0.0

        for dimension, weight in weights.items():
            if dimension not in candidate.dimensions:
                raise KeyError(
                    f"Candidate {candidate.candidate_id!r} is missing dimension {dimension!r}."
                )

            value = candidate.dimensions[dimension]

            if dimension not in policy.scales:
                raise KeyError(f"Policy is missing scale for dimension {dimension!r}.")

            if value not in policy.scales[dimension]:
                raise KeyError(
                    f"Unknown value {value!r} for dimension {dimension!r} "
                    f"in candidate {candidate.candidate_id!r}."
                )

            numeric = policy.scales[dimension][value]
            total += float(numeric) * float(weight)

        scores[label] = round(total, 3)

    return CandidateResult(
        candidate=candidate,
        scores=scores,
    )
