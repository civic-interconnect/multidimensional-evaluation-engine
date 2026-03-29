"""tests/test_evaluator.py: Unit tests for candidate evaluation."""

import pytest

from multidimensional_evaluation_engine.domain.factors import (
    FactorForm,
    FactorSpec,
    FactorValue,
)
from multidimensional_evaluation_engine.evaluation.evaluator import evaluate_candidate
from multidimensional_evaluation_engine.policy.policy import (
    Comparator,
    ConstraintRule,
    NumericBand,
    Policy,
    ScoreRule,
)
from tests.builders import make_candidate, make_constraint_policy, make_policy


def test_evaluates_categorical_scores_and_total() -> None:
    """Categorical score rules should contribute weighted scores and total."""
    candidate = make_candidate()

    result = evaluate_candidate(candidate, make_policy())

    assert result.scores["speed_score"] == 1.5
    assert result.scores["cost_score"] == 1.5
    assert result.scores["total"] == 3.0
    assert result.scores["admissible"] == 1.0
    assert result.scores["interpretation:high"] == 1.0


def test_raises_key_error_for_missing_factor() -> None:
    """Missing factor values should raise KeyError."""
    candidate = make_candidate(
        factor_values={
            "speed": FactorValue(
                factor_id="speed",
                form=FactorForm.CATEGORICAL,
                value="fast",
            )
        }
    )

    with pytest.raises(KeyError, match="cost"):
        evaluate_candidate(candidate, make_policy())


def test_raises_value_error_for_unknown_categorical_value() -> None:
    """Unknown categorical values should raise ValueError."""
    candidate = make_candidate(
        factor_values={
            "speed": FactorValue(
                factor_id="speed",
                form=FactorForm.CATEGORICAL,
                value="medium",
            ),
            "cost": FactorValue(
                factor_id="cost",
                form=FactorForm.CATEGORICAL,
                value="low",
            ),
        }
    )

    with pytest.raises(ValueError, match="Unknown categorical value"):
        evaluate_candidate(candidate, make_policy())


def test_hard_constraint_failure_sets_admissible_to_zero() -> None:
    """Failed hard constraints should set admissible to 0.0."""
    candidate = make_candidate(
        factor_values={
            "zoning_ok": FactorValue(
                factor_id="zoning_ok",
                form=FactorForm.BINARY,
                value=False,
            ),
            "interconnection_years": FactorValue(
                factor_id="interconnection_years",
                form=FactorForm.NUMERIC,
                value=1.5,
            ),
        }
    )

    result = evaluate_candidate(candidate, make_constraint_policy())

    assert result.scores["admissible"] == 0.0
    assert result.scores["interconnection_speed"] == 5.0
    assert result.scores["total"] == 5.0
    assert result.scores["interpretation:strong"] == 1.0


def test_hard_constraint_success_sets_admissible_to_one() -> None:
    """Passed hard constraints should set admissible to 1.0."""
    candidate = make_candidate(
        factor_values={
            "zoning_ok": FactorValue(
                factor_id="zoning_ok",
                form=FactorForm.BINARY,
                value=True,
            ),
            "interconnection_years": FactorValue(
                factor_id="interconnection_years",
                form=FactorForm.NUMERIC,
                value=3.0,
            ),
        }
    )

    result = evaluate_candidate(candidate, make_constraint_policy())

    assert result.scores["admissible"] == 1.0
    assert result.scores["interconnection_speed"] == 3.0
    assert result.scores["total"] == 3.0


def test_numeric_band_scoring_uses_matching_band() -> None:
    """Numeric score rules should use the matching numeric band."""
    candidate = make_candidate(
        factor_values={
            "zoning_ok": FactorValue(
                factor_id="zoning_ok",
                form=FactorForm.BINARY,
                value=True,
            ),
            "interconnection_years": FactorValue(
                factor_id="interconnection_years",
                form=FactorForm.NUMERIC,
                value=5.0,
            ),
        }
    )

    result = evaluate_candidate(candidate, make_constraint_policy())

    assert result.scores["interconnection_speed"] == 1.0
    assert result.scores["total"] == 1.0
    assert result.scores["interpretation:weak"] == 1.0


def test_binary_score_rule_works() -> None:
    """Binary score rules should map bool values to scores."""
    policy = Policy(
        factor_specs=[
            FactorSpec(
                factor_id="review_available",
                label="Review Available",
                form=FactorForm.BINARY,
            )
        ],
        constraint_rules=[],
        score_rules=[
            ScoreRule(
                rule_id="review_score",
                factor_id="review_available",
                weight=1.0,
                binary_scores={True: 4.0, False: 1.0},
            )
        ],
        interpretation={"low": 1.0, "high": 4.0},
        metadata={},
    )

    candidate = make_candidate(
        factor_values={
            "review_available": FactorValue(
                factor_id="review_available",
                form=FactorForm.BINARY,
                value=True,
            )
        }
    )

    result = evaluate_candidate(candidate, policy)

    assert result.scores["review_score"] == 4.0
    assert result.scores["total"] == 4.0
    assert result.scores["admissible"] == 1.0
    assert result.scores["interpretation:high"] == 1.0


def test_raises_value_error_for_unmatched_numeric_band() -> None:
    """Numeric values outside all bands should raise ValueError."""
    policy = Policy(
        factor_specs=[
            FactorSpec(
                factor_id="interconnection_years",
                label="Interconnection Years",
                form=FactorForm.NUMERIC,
                unit="years",
            )
        ],
        constraint_rules=[],
        score_rules=[
            ScoreRule(
                rule_id="interconnection_speed",
                factor_id="interconnection_years",
                weight=1.0,
                numeric_bands=(
                    NumericBand(
                        min_inclusive=0.0,
                        max_inclusive=2.0,
                        score=5.0,
                        band="excellent",
                    ),
                ),
            )
        ],
        interpretation={},
        metadata={},
    )

    candidate = make_candidate(
        factor_values={
            "interconnection_years": FactorValue(
                factor_id="interconnection_years",
                form=FactorForm.NUMERIC,
                value=5.0,
            )
        }
    )

    with pytest.raises(ValueError, match="did not match any band"):
        evaluate_candidate(candidate, policy)


def test_constraint_in_comparator_works_for_categorical_values() -> None:
    """IN constraint should work with categorical factor values."""
    policy = Policy(
        factor_specs=[
            FactorSpec(
                factor_id="zoning_category",
                label="Zoning Category",
                form=FactorForm.CATEGORICAL,
                allowed_values=("industrial", "mixed_use"),
            ),
            FactorSpec(
                factor_id="cost",
                label="Cost",
                form=FactorForm.CATEGORICAL,
                allowed_values=("low", "high"),
            ),
        ],
        constraint_rules=[
            ConstraintRule(
                rule_id="zoning_allowed",
                factor_id="zoning_category",
                comparator=Comparator.IN,
                threshold=("industrial", "heavy_industrial"),
                message="Zoning category must be allowed.",
            )
        ],
        score_rules=[
            ScoreRule(
                rule_id="cost_score",
                factor_id="cost",
                weight=1.0,
                categorical_scores={"low": 3.0, "high": 1.0},
            )
        ],
        interpretation={"low": 1.0, "high": 3.0},
        metadata={},
    )

    candidate = make_candidate(
        factor_values={
            "zoning_category": FactorValue(
                factor_id="zoning_category",
                form=FactorForm.CATEGORICAL,
                value="industrial",
            ),
            "cost": FactorValue(
                factor_id="cost",
                form=FactorForm.CATEGORICAL,
                value="low",
            ),
        }
    )

    result = evaluate_candidate(candidate, policy)

    assert result.scores["admissible"] == 1.0
    assert result.scores["cost_score"] == 3.0
    assert result.scores["total"] == 3.0


def test_no_interpretation_key_when_no_threshold_is_satisfied() -> None:
    """No interpretation key should be added if none of the thresholds are met."""
    policy = Policy(
        factor_specs=[
            FactorSpec(
                factor_id="cost",
                label="Cost",
                form=FactorForm.CATEGORICAL,
                allowed_values=("low", "high"),
            )
        ],
        constraint_rules=[],
        score_rules=[
            ScoreRule(
                rule_id="cost_score",
                factor_id="cost",
                weight=1.0,
                categorical_scores={"low": 1.0, "high": 0.5},
            )
        ],
        interpretation={"strong": 5.0},
        metadata={},
    )

    candidate = make_candidate(
        factor_values={
            "cost": FactorValue(
                factor_id="cost",
                form=FactorForm.CATEGORICAL,
                value="low",
            )
        }
    )

    result = evaluate_candidate(candidate, policy)

    assert result.scores["total"] == 1.0
    assert all(
        not label.startswith("interpretation:")
        for label in result.scores
    )


def test_constraint_gt_comparator_works_for_numeric_values() -> None:
    """GT constraint should work with numeric factor values."""
    policy = Policy(
        factor_specs=[
            FactorSpec(
                factor_id="tax_relief",
                label="Tax Relief",
                form=FactorForm.NUMERIC,
                unit="usd",
            ),
            FactorSpec(
                factor_id="cost",
                label="Cost",
                form=FactorForm.CATEGORICAL,
                allowed_values=("low", "high"),
            ),
        ],
        constraint_rules=[
            ConstraintRule(
                rule_id="minimum_tax_relief",
                factor_id="tax_relief",
                comparator=Comparator.GT,
                threshold=1000.0,
                message="Tax relief must exceed minimum threshold.",
            )
        ],
        score_rules=[
            ScoreRule(
                rule_id="cost_score",
                factor_id="cost",
                weight=1.0,
                categorical_scores={"low": 3.0, "high": 1.0},
            )
        ],
        interpretation={"low": 1.0, "high": 3.0},
        metadata={},
    )

    candidate = make_candidate(
        factor_values={
            "tax_relief": FactorValue(
                factor_id="tax_relief",
                form=FactorForm.NUMERIC,
                value=3000.0,
            ),
            "cost": FactorValue(
                factor_id="cost",
                form=FactorForm.CATEGORICAL,
                value="low",
            ),
        }
    )

    result = evaluate_candidate(candidate, policy)

    assert result.scores["admissible"] == 1.0
    assert result.scores["cost_score"] == 3.0
    assert result.scores["total"] == 3.0


def test_raises_value_error_for_invalid_boolean_coercion() -> None:
    """Invalid boolean-like values should raise ValueError for binary scoring."""
    policy = Policy(
        factor_specs=[
            FactorSpec(
                factor_id="review_available",
                label="Review Available",
                form=FactorForm.BINARY,
            )
        ],
        constraint_rules=[],
        score_rules=[
            ScoreRule(
                rule_id="review_score",
                factor_id="review_available",
                weight=1.0,
                binary_scores={True: 4.0, False: 1.0},
            )
        ],
        interpretation={},
        metadata={},
    )

    candidate = make_candidate(
        factor_values={
            "review_available": FactorValue(
                factor_id="review_available",
                form=FactorForm.BINARY,
                value="maybe",
            )
        }
    )

    with pytest.raises(ValueError, match="Cannot coerce value"):
        evaluate_candidate(candidate, policy)


def test_raises_value_error_when_score_rule_has_no_supported_mapping() -> None:
    """A malformed score rule with no mapping should raise ValueError."""
    policy = Policy(
        factor_specs=[
            FactorSpec(
                factor_id="cost",
                label="Cost",
                form=FactorForm.CATEGORICAL,
                allowed_values=("low", "high"),
            )
        ],
        constraint_rules=[],
        score_rules=[],
        interpretation={},
        metadata={},
    )

    bad_rule = object.__new__(ScoreRule)
    object.__setattr__(bad_rule, "rule_id", "broken_rule")
    object.__setattr__(bad_rule, "factor_id", "cost")
    object.__setattr__(bad_rule, "weight", 1.0)
    object.__setattr__(bad_rule, "categorical_scores", {})
    object.__setattr__(bad_rule, "numeric_bands", ())
    object.__setattr__(bad_rule, "binary_scores", {})
    object.__setattr__(bad_rule, "rationale", "")

    object.__setattr__(policy, "score_rules", [bad_rule])

    candidate = make_candidate(
        factor_values={
            "cost": FactorValue(
                factor_id="cost",
                form=FactorForm.CATEGORICAL,
                value="low",
            )
        }
    )

    with pytest.raises(ValueError, match="has no supported mapping"):
        evaluate_candidate(candidate, policy)
