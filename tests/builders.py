"""tests/test_models.py: Canonical test model builders for the evaluation engine."""

from multidimensional_evaluation_engine.domain.candidates import Candidate
from multidimensional_evaluation_engine.domain.factors import (
    FactorForm,
    FactorSpec,
    FactorValue,
)
from multidimensional_evaluation_engine.domain.results import CandidateResult
from multidimensional_evaluation_engine.policy.policy import (
    Comparator,
    ConstraintRule,
    NumericBand,
    Policy,
    ScoreRule,
)

# ---------------------------------------------------------------------------
# Candidate builders
# ---------------------------------------------------------------------------


def make_candidate(
    candidate_id: str = "c1",
    candidate_name: str = "Test Candidate",
    factor_values: dict[str, FactorValue] | None = None,
    notes: str = "",
    metadata: dict[str, str] | None = None,
) -> Candidate:
    """Return a Candidate with sensible defaults."""
    return Candidate(
        candidate_id=candidate_id,
        candidate_name=candidate_name,
        factor_values=(
            factor_values
            if factor_values is not None
            else {
                "speed": FactorValue(
                    factor_id="speed",
                    form=FactorForm.CATEGORICAL,
                    value="fast",
                ),
                "cost": FactorValue(
                    factor_id="cost",
                    form=FactorForm.CATEGORICAL,
                    value="low",
                ),
            }
        ),
        notes=notes,
        metadata=metadata if metadata is not None else {},
    )


# ---------------------------------------------------------------------------
# FactorSpec builders
# ---------------------------------------------------------------------------


def make_factor_specs() -> list[FactorSpec]:
    """Return default factor specifications."""
    return [
        FactorSpec(
            factor_id="speed",
            label="Speed",
            form=FactorForm.CATEGORICAL,
            allowed_values=("slow", "fast"),
        ),
        FactorSpec(
            factor_id="cost",
            label="Cost",
            form=FactorForm.CATEGORICAL,
            allowed_values=("low", "high"),
        ),
    ]


# ---------------------------------------------------------------------------
# Policy builders
# ---------------------------------------------------------------------------


def make_policy(
    factor_specs: list[FactorSpec] | None = None,
    constraint_rules: list[ConstraintRule] | None = None,
    score_rules: list[ScoreRule] | None = None,
    interpretation: dict[str, float] | None = None,
    metadata: dict[str, str] | None = None,
) -> Policy:
    """Return a Policy with sensible defaults."""
    return Policy(
        factor_specs=factor_specs if factor_specs is not None else make_factor_specs(),
        constraint_rules=constraint_rules if constraint_rules is not None else [],
        score_rules=(
            score_rules
            if score_rules is not None
            else [
                ScoreRule(
                    rule_id="speed_score",
                    factor_id="speed",
                    weight=0.5,
                    categorical_scores={"slow": 1.0, "fast": 3.0},
                ),
                ScoreRule(
                    rule_id="cost_score",
                    factor_id="cost",
                    weight=0.5,
                    categorical_scores={"low": 3.0, "high": 1.0},
                ),
            ]
        ),
        interpretation=(
            interpretation
            if interpretation is not None
            else {
                "low": 1.0,
                "mid": 2.0,
                "high": 3.0,
            }
        ),
        metadata=metadata if metadata is not None else {},
    )


def make_constraint_policy() -> Policy:
    """Return a Policy with one hard constraint and one scored factor."""
    return Policy(
        factor_specs=[
            FactorSpec(
                factor_id="zoning_ok",
                label="Zoning Compatible",
                form=FactorForm.BINARY,
            ),
            FactorSpec(
                factor_id="interconnection_years",
                label="Interconnection Years",
                form=FactorForm.NUMERIC,
                unit="years",
            ),
        ],
        constraint_rules=[
            ConstraintRule(
                rule_id="zoning_required",
                factor_id="zoning_ok",
                comparator=Comparator.EQ,
                threshold=True,
                message="Zoning must be compatible.",
            )
        ],
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
                    NumericBand(
                        min_inclusive=2.01,
                        max_inclusive=4.0,
                        score=3.0,
                        band="moderate",
                    ),
                    NumericBand(
                        min_inclusive=4.01,
                        max_inclusive=20.0,
                        score=1.0,
                        band="weak",
                    ),
                ),
            )
        ],
        interpretation={"weak": 1.0, "strong": 4.0},
        metadata={},
    )


# ---------------------------------------------------------------------------
# CandidateResult builders
# ---------------------------------------------------------------------------


def make_result(
    candidate: Candidate | None = None,
    scores: dict[str, float] | None = None,
) -> CandidateResult:
    """Return a CandidateResult with sensible defaults."""
    return CandidateResult(
        candidate=candidate if candidate is not None else make_candidate(),
        scores=scores if scores is not None else {"total": 3.0},
    )
