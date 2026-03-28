"""tests/test_models.py: Canonical test model builders for the evaluation engine."""

from typing import Any

from multidimensional_evaluation_engine.domain.candidates import Candidate
from multidimensional_evaluation_engine.domain.results import CandidateResult
from multidimensional_evaluation_engine.policy.policy import Policy

# ---------------------------------------------------------------------------
# Candidate builders
# ---------------------------------------------------------------------------


def make_candidate(
    candidate_id: str = "c1",
    candidate_name: str = "Test Candidate",
    dimensions: dict[str, str] | None = None,
    notes: str = "",
    metadata: dict[str, str] | None = None,
) -> Candidate:
    """Return a Candidate with sensible defaults."""
    return Candidate(
        candidate_id=candidate_id,
        candidate_name=candidate_name,
        dimensions=dimensions
        if dimensions is not None
        else {"speed": "fast", "cost": "low"},
        notes=notes,
        metadata=metadata if metadata is not None else {},
    )


# ---------------------------------------------------------------------------
# Policy builders
# ---------------------------------------------------------------------------


def make_policy(
    scales: dict[str, dict[str, int | float]] | None = None,
    weights: dict[str, dict[str, float]] | None = None,
    interpretation: dict[str, float] | None = None,
    patterns: list[dict[str, Any]] | None = None,
    rules: list[dict[str, Any]] | None = None,
    metadata: dict[str, str] | None = None,
) -> Policy:
    """Return a Policy with sensible defaults."""
    return Policy(
        scales=scales
        if scales is not None
        else {
            "speed": {"slow": 1, "fast": 3},
            "cost": {"low": 3, "high": 1},
        },
        weights=weights
        if weights is not None
        else {
            "overall": {"speed": 0.5, "cost": 0.5},
        },
        interpretation=interpretation
        if interpretation is not None
        else {
            "low": 1.0,
            "mid": 2.0,
            "high": 3.0,
        },
        patterns=patterns if patterns is not None else [],
        rules=rules if rules is not None else [],
        metadata=metadata if metadata is not None else {},
    )


# ---------------------------------------------------------------------------
# CandidateResult builders
# ---------------------------------------------------------------------------


def make_result(
    candidate: Candidate | None = None,
    scores: dict[str, float] | None = None,
    levels: dict[str, str] | None = None,
    visual_levels: dict[str, str] | None = None,
) -> CandidateResult:
    """Return a CandidateResult with sensible defaults."""
    return CandidateResult(
        candidate=candidate if candidate is not None else make_candidate(),
        scores=scores if scores is not None else {"overall": 3.0},
        levels=levels if levels is not None else {},
        visual_levels=visual_levels if visual_levels is not None else {},
    )
