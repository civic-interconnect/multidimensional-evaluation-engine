"""evaluation/evaluator.py: Evaluate candidates against policy."""


from ..domain.candidates import Candidate
from ..domain.factors import FactorValue
from ..domain.results import CandidateResult
from ..policy.policy import Comparator, Policy, ScoreRule

type PrimitiveValue = str | float | bool


def evaluate_candidate(
    candidate: Candidate,
    policy: Policy,
) -> CandidateResult:
    """Evaluate a candidate under a policy.

    This bridge evaluator supports the newer typed policy model while consuming
    candidate.factor_values.

    Current behavior:
    - hard constraints are evaluated first
    - scored findings are evaluated next
    - weighted scores are summed into a single total
    - the returned CandidateResult remains compatible with the existing
      score-dictionary shape

    Returned score keys include:
    - one entry per score rule, keyed by rule_id
    - "total" for aggregate weighted score
    - "admissible" as 1.0 or 0.0
    - optional interpretation label as 1.0 for the highest satisfied label

    Args:
        candidate: Candidate with factor values.
        policy: Policy defining factor specs, constraint rules, score rules,
            and aggregate interpretation thresholds.

    Returns:
        CandidateResult containing computed scores.

    Raises:
        KeyError: If a required factor is missing from the candidate.
        ValueError: If a factor value cannot be interpreted for its rule.
    """
    scores: dict[str, float] = {}
    admissible = True

    for rule in policy.constraint_rules:
        factor_value = _get_candidate_value(candidate, rule.factor_id)
        passed = _evaluate_constraint(factor_value, rule.comparator, rule.threshold)
        if not passed:
            admissible = False

    total = 0.0

    for rule in policy.score_rules:
        factor_value = _get_candidate_value(candidate, rule.factor_id)
        rule_score = _evaluate_score_rule(factor_value, rule)
        weighted_score = rule_score * rule.weight
        scores[rule.rule_id] = round(weighted_score, 3)
        total += weighted_score

    scores["total"] = round(total, 3)
    scores["admissible"] = 1.0 if admissible else 0.0

    interpretation_label = _interpret_total(total, policy.interpretation)
    if interpretation_label:
        scores[f"interpretation:{interpretation_label}"] = 1.0

    return CandidateResult(
        candidate=candidate,
        scores=scores,
    )


def _get_candidate_value(candidate: Candidate, factor_id: str) -> FactorValue:
    """Return the factor value for a factor id.

    Raises:
        KeyError: If factor_id is not present in candidate.factor_values.
    """
    if factor_id not in candidate.factor_values:
        raise KeyError(
            f"Candidate {candidate.candidate_id!r} is missing factor {factor_id!r}."
        )
    return candidate.factor_values[factor_id]


def _unwrap_factor_value(factor_value: FactorValue) -> PrimitiveValue:
    """Return the primitive payload stored in a FactorValue."""
    return factor_value.value


def _evaluate_constraint(
    factor_value: FactorValue,
    comparator: Comparator,
    threshold: bool | float | str | tuple[str, ...],
) -> bool:
    """Evaluate a hard constraint against a candidate factor value.

    Raises:
        ValueError: If the threshold type is unsupported or the comparator
            is incompatible with the threshold.
    """
    raw_value = _unwrap_factor_value(factor_value)

    if comparator == Comparator.IN:
        if not isinstance(threshold, tuple):
            raise ValueError(
                f"Comparator {Comparator.IN!r} requires a tuple threshold; "
                f"got {type(threshold).__name__}."
            )
        return _coerce_str(raw_value) in threshold

    if isinstance(threshold, bool):
        return _compare_bool(_coerce_bool(raw_value), comparator, threshold)

    if isinstance(threshold, float):
        return _compare_float(_coerce_float(raw_value), comparator, threshold)

    if isinstance(threshold, str):
        return _compare_str(_coerce_str(raw_value), comparator, threshold)

    raise ValueError(
        f"Unsupported constraint threshold {threshold!r} for value {raw_value!r}."
    )


def _evaluate_score_rule(factor_value: FactorValue, rule: ScoreRule) -> float:
    """Return the unweighted score for a score rule.

    Assumes ScoreRule.__post_init__ has already validated that exactly one
    mapping style is populated.

    Raises:
        ValueError: If the raw value does not match any entry in the mapping.
    """
    raw_value = _unwrap_factor_value(factor_value)

    if rule.categorical_scores:
        categorical_value = _coerce_str(raw_value)
        if categorical_value not in rule.categorical_scores:
            raise ValueError(
                f"Unknown categorical value {categorical_value!r} for factor "
                f"{rule.factor_id!r} in rule {rule.rule_id!r}."
            )
        return rule.categorical_scores[categorical_value]

    if rule.numeric_bands:
        numeric_value = _coerce_float(raw_value)
        for band in rule.numeric_bands:
            if band.min_inclusive <= numeric_value <= band.max_inclusive:
                return band.score
        raise ValueError(
            f"Numeric value {numeric_value!r} for factor {rule.factor_id!r} "
            f"did not match any band in rule {rule.rule_id!r}."
        )

    if rule.binary_scores:
        bool_value = _coerce_bool(raw_value)
        if bool_value not in rule.binary_scores:
            raise ValueError(
                f"Binary value {bool_value!r} for factor {rule.factor_id!r} "
                f"is not defined in rule {rule.rule_id!r}."
            )
        return rule.binary_scores[bool_value]

    raise ValueError(
        f"Score rule {rule.rule_id!r} has no supported mapping for factor "
        f"{rule.factor_id!r}."
    )


def _interpret_total(total: float, interpretation: dict[str, float]) -> str:
    """Return the highest satisfied interpretation label for a total score.

    Returns an empty string if no label threshold is satisfied or if the
    interpretation mapping is empty.
    """
    if not interpretation:
        return ""

    satisfied = [
        label for label, threshold in interpretation.items() if total >= threshold
    ]
    if not satisfied:
        return ""

    return max(satisfied, key=lambda label: interpretation[label])


def _coerce_float(value: PrimitiveValue) -> float:
    """Convert a candidate value to float.

    Raises:
        ValueError: If the value cannot be parsed as a float.
    """
    if isinstance(value, bool):
        raise ValueError(f"Cannot coerce bool value {value!r} to float.")
    if isinstance(value, float):
        return value
    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(f"Cannot coerce value {value!r} to float.") from exc


def _coerce_bool(value: PrimitiveValue) -> bool:
    """Convert a candidate value to bool.

    Raises:
        ValueError: If the value does not match a recognized boolean literal.
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, float):
        raise ValueError(f"Cannot coerce float value {value!r} to bool.")
    if not isinstance(value, str):
        raise ValueError(f"Cannot coerce value {value!r} to bool.")
    normalized = value.strip().lower()
    if normalized in {"true", "yes", "1"}:
        return True
    if normalized in {"false", "no", "0"}:
        return False
    raise ValueError(f"Cannot coerce value {value!r} to bool.")


def _coerce_str(value: PrimitiveValue) -> str:
    """Convert a candidate value to string."""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _compare_bool(left: bool, comparator: Comparator, right: bool) -> bool:
    """Apply a comparison operator to bool operands."""
    return _apply_comparator(left, comparator, right)


def _compare_float(left: float, comparator: Comparator, right: float) -> bool:
    """Apply a comparison operator to float operands."""
    return _apply_comparator(left, comparator, right)


def _compare_str(left: str, comparator: Comparator, right: str) -> bool:
    """Apply a comparison operator to string operands."""
    return _apply_comparator(left, comparator, right)


def _apply_comparator(
    left: bool | float | str,
    comparator: Comparator,
    right: bool | float | str,
) -> bool:
    """Apply a comparison operator to same-typed operands.

    Raises:
        ValueError: If the comparator is not supported.
    """
    if comparator == Comparator.LT:
        return left < right  # type: ignore[operator]
    if comparator == Comparator.LE:
        return left <= right  # type: ignore[operator]
    if comparator == Comparator.EQ:
        return left == right
    if comparator == Comparator.GE:
        return left >= right  # type: ignore[operator]
    if comparator == Comparator.GT:
        return left > right  # type: ignore[operator]
    raise ValueError(f"Unsupported comparator {comparator!r}.")
