"""tests/test_evaluator.py: Unit tests for evaluate_candidate."""

import math

import pytest

from multidimensional_evaluation_engine.domain.candidates import Candidate
from multidimensional_evaluation_engine.domain.results import CandidateResult
from multidimensional_evaluation_engine.evaluation.evaluator import evaluate_candidate
from multidimensional_evaluation_engine.policy.policy import Policy

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def simple_candidate() -> Candidate:
    return Candidate(
        candidate_id="c1",
        candidate_name="Test Candidate",
        dimensions={"speed": "fast", "cost": "low"},
    )


@pytest.fixture()
def simple_policy() -> Policy:
    return Policy(
        scales={"speed": {"slow": 1, "fast": 3}, "cost": {"low": 3, "high": 1}},
        weights={"overall": {"speed": 0.5, "cost": 0.5}},
        interpretation={"low": 1.0, "mid": 2.0, "high": 3.0},
    )


# ---------------------------------------------------------------------------
# Happy-path tests
# ---------------------------------------------------------------------------


def test_returns_candidate_result(
    simple_candidate: Candidate, simple_policy: Policy
) -> None:
    result = evaluate_candidate(simple_candidate, simple_policy)
    assert isinstance(result, CandidateResult)


def test_result_references_original_candidate(
    simple_candidate: Candidate, simple_policy: Policy
) -> None:
    result = evaluate_candidate(simple_candidate, simple_policy)
    assert result.candidate is simple_candidate


def test_score_keys_match_policy_labels(
    simple_candidate: Candidate, simple_policy: Policy
) -> None:
    result = evaluate_candidate(simple_candidate, simple_policy)
    assert set(result.scores.keys()) == {"overall"}


def test_weighted_score_is_correct(
    simple_candidate: Candidate, simple_policy: Policy
) -> None:
    # speed=fast → 3 * 0.5 = 1.5; cost=low → 3 * 0.5 = 1.5; total = 3.0
    result = evaluate_candidate(simple_candidate, simple_policy)
    assert math.isclose(result.scores["overall"], 3.0)


def test_score_is_rounded_to_three_decimal_places() -> None:
    policy = Policy(
        scales={"x": {"a": 1}},
        weights={"label": {"x": 1 / 3}},
        interpretation={"low": 0.0, "high": 1.0},
    )
    candidate = Candidate(candidate_id="c", candidate_name="C", dimensions={"x": "a"})
    result = evaluate_candidate(candidate, policy)
    assert math.isclose(result.scores["label"], 0.333, abs_tol=1e-3)


def test_multiple_labels_scored_independently() -> None:
    policy = Policy(
        scales={"speed": {"slow": 1, "fast": 3}},
        weights={"label_a": {"speed": 1.0}, "label_b": {"speed": 2.0}},
        interpretation={"low": 1.0, "high": 3.0},
    )
    candidate = Candidate(
        candidate_id="c", candidate_name="C", dimensions={"speed": "fast"}
    )
    result = evaluate_candidate(candidate, policy)
    assert math.isclose(result.scores["label_a"], 3.0)
    assert math.isclose(result.scores["label_b"], 6.0)


def test_zero_weight_contributes_zero() -> None:
    policy = Policy(
        scales={"speed": {"fast": 9}},
        weights={"label": {"speed": 0.0}},
        interpretation={"low": 0.0, "high": 9.0},
    )
    candidate = Candidate(
        candidate_id="c", candidate_name="C", dimensions={"speed": "fast"}
    )
    result = evaluate_candidate(candidate, policy)
    assert math.isclose(result.scores["label"], 0.0)


# ---------------------------------------------------------------------------
# Error-path tests
# ---------------------------------------------------------------------------


def test_raises_for_missing_candidate_dimension(simple_policy: Policy) -> None:
    candidate = Candidate(
        candidate_id="c_bad", candidate_name="Bad", dimensions={"speed": "fast"}
    )
    with pytest.raises(KeyError, match="c_bad"):
        evaluate_candidate(candidate, simple_policy)


def test_raises_for_missing_policy_scale() -> None:
    policy = Policy(
        scales={},
        weights={"label": {"speed": 1.0}},
        interpretation={"low": 0.0, "high": 1.0},
    )
    candidate = Candidate(
        candidate_id="c", candidate_name="C", dimensions={"speed": "fast"}
    )
    with pytest.raises(KeyError, match="speed"):
        evaluate_candidate(candidate, policy)


def test_raises_for_unknown_dimension_value(simple_policy: Policy) -> None:
    candidate = Candidate(
        candidate_id="c",
        candidate_name="C",
        dimensions={"speed": "turbo", "cost": "low"},
    )
    with pytest.raises(KeyError, match="turbo"):
        evaluate_candidate(candidate, policy=simple_policy)
