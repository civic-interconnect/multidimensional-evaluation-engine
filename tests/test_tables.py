"""tests/test_tables.py: Unit tests for format_results."""

from multidimensional_evaluation_engine.domain.candidates import Candidate
from multidimensional_evaluation_engine.domain.results import CandidateResult
from multidimensional_evaluation_engine.reporting.tables import format_results

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _candidate(candidate_id: str = "c1", candidate_name: str = "Alpha") -> Candidate:
    return Candidate(
        candidate_id=candidate_id, candidate_name=candidate_name, dimensions={}
    )


def _result(
    candidate: Candidate | None = None,
    scores: dict[str, float] | None = None,
    levels: dict[str, str] | None = None,
) -> CandidateResult:
    return CandidateResult(
        candidate=candidate or _candidate(),
        scores=scores or {"overall": 3.0},
        levels=levels or {},
    )


# ---------------------------------------------------------------------------
# Happy-path tests
# ---------------------------------------------------------------------------


def test_returns_string() -> None:
    assert isinstance(format_results([_result()]), str)


def test_empty_list_returns_empty_string() -> None:
    assert format_results([]) == ""


def test_candidate_id_and_name_in_output() -> None:
    output = format_results(
        [_result(candidate=_candidate(candidate_id="c1", candidate_name="Alpha"))]
    )
    assert "c1" in output
    assert "Alpha" in output


def test_score_formatted_to_two_decimal_places() -> None:
    assert "2.50" in format_results([_result(scores={"overall": 2.5})])


def test_label_appears_in_output() -> None:
    assert "quality" in format_results([_result(scores={"quality": 1.5})])


def test_level_included_when_present() -> None:
    assert "(mid)" in format_results(
        [_result(scores={"overall": 2.0}, levels={"overall": "mid"})]
    )


def test_level_omitted_when_absent() -> None:
    assert "(" not in format_results([_result(scores={"overall": 2.0}, levels={})])


def test_labels_sorted_deterministically() -> None:
    output = format_results([_result(scores={"zebra": 1.0, "alpha": 2.0, "mid": 3.0})])
    positions = [output.index(label) for label in ("alpha", "mid", "zebra")]
    assert positions == sorted(positions)


def test_multiple_candidates_all_appear() -> None:
    results: list[CandidateResult] = [
        _result(candidate=_candidate(candidate_id="c1", candidate_name="Alpha")),
        _result(candidate=_candidate(candidate_id="c2", candidate_name="Beta")),
    ]
    output = format_results(results)
    assert "c1" in output
    assert "c2" in output


def test_trailing_whitespace_stripped() -> None:
    output = format_results([_result()])
    assert not output.endswith("\n")
    assert not output.endswith(" ")


def test_single_candidate_no_trailing_blank_line() -> None:
    assert not format_results([_result()]).endswith("\n")


def test_multiple_candidates_separated_by_blank_line() -> None:
    results: list[CandidateResult] = [
        _result(candidate=_candidate(candidate_id="c1", candidate_name="Alpha")),
        _result(candidate=_candidate(candidate_id="c2", candidate_name="Beta")),
    ]
    assert "\n\n" in format_results(results)


def test_score_with_integer_value_formats_correctly() -> None:
    assert "3.00" in format_results([_result(scores={"overall": 3.0})])
