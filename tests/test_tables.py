"""tests/test_tables.py: Unit tests for plain-text table reporting."""

from multidimensional_evaluation_engine.reporting.tables import format_results
from tests.builders import make_candidate, make_result


def test_returns_empty_string_for_empty_results() -> None:
    """Formatting no results should return an empty string."""
    assert format_results([]) == ""


def test_includes_candidate_header() -> None:
    """Report should include candidate id and name."""
    candidate = make_candidate(candidate_id="c1", candidate_name="Alpha")
    result = make_result(candidate=candidate, scores={"total": 3.0})

    text = format_results([result])

    assert "c1 | Alpha" in text


def test_formats_scores_with_two_decimal_places() -> None:
    """Scores should be rendered with two decimal places."""
    result = make_result(scores={"total": 3.0, "speed_score": 1.5})

    text = format_results([result])

    assert "  - total: 3.00" in text
    assert "  - speed_score: 1.50" in text


def test_sorts_score_labels_deterministically() -> None:
    """Score labels should be rendered in sorted order."""
    result = make_result(
        scores={
            "z_score": 2.0,
            "a_score": 1.0,
            "total": 3.0,
        }
    )

    text = format_results([result])
    lines = text.splitlines()

    a_index = lines.index("  - a_score: 1.00")
    total_index = lines.index("  - total: 3.00")
    z_index = lines.index("  - z_score: 2.00")

    assert a_index < total_index < z_index


def test_renders_interpretation_as_readable_line() -> None:
    """Interpretation keys should be rendered as readable interpretation output."""
    result = make_result(
        scores={
            "total": 4.0,
            "interpretation:strong": 1.0,
        }
    )

    text = format_results([result])

    assert "  - interpretation:strong: 1.00" not in text
    assert "  * interpretation: strong" in text


def test_sorts_multiple_interpretations_deterministically() -> None:
    """Multiple interpretations should be rendered in sorted order."""
    result = make_result(
        scores={
            "total": 4.0,
            "interpretation:strong": 1.0,
            "interpretation:mid": 1.0,
        }
    )

    text = format_results([result])

    assert "  * interpretation: mid, strong" in text


def test_adds_blank_line_between_candidates() -> None:
    """Multiple candidates should be separated by a blank line."""
    result1 = make_result(
        candidate=make_candidate(candidate_id="c1", candidate_name="Alpha"),
        scores={"total": 3.0},
    )
    result2 = make_result(
        candidate=make_candidate(candidate_id="c2", candidate_name="Beta"),
        scores={"total": 2.0},
    )

    text = format_results([result1, result2])

    assert "c1 | Alpha\n  - total: 3.00\n\nc2 | Beta" in text
