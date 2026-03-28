"""tests/test_load_candidates.py: Unit tests for load_candidates."""

from pathlib import Path

import pytest

from multidimensional_evaluation_engine.domain.candidates import Candidate
from multidimensional_evaluation_engine.io.load_candidates import load_candidates

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def write_csv(tmp_path: Path, filename: str, content: str) -> Path:
    """Write content to a temp CSV file and return its path."""
    p = tmp_path / filename
    p.write_text(content, encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# Happy-path tests
# ---------------------------------------------------------------------------


def test_returns_list_of_candidates(tmp_path: Path):
    csv = write_csv(
        tmp_path,
        "c.csv",
        ("candidate_id,candidate_name,speed,cost\nc1,Alpha,fast,low\n"),
    )
    result = load_candidates(csv)
    assert isinstance(result, list)
    assert all(isinstance(c, Candidate) for c in result)


def test_correct_candidate_count(tmp_path: Path):
    csv = write_csv(
        tmp_path,
        "c.csv",
        (
            "candidate_id,candidate_name,speed\n"
            "c1,Alpha,fast\n"
            "c2,Beta,slow\n"
            "c3,Gamma,fast\n"
        ),
    )
    assert len(load_candidates(csv)) == 3


def test_candidate_id_and_name_mapped(tmp_path: Path):
    csv = write_csv(tmp_path, "c.csv", ("candidate_id,candidate_name\nc1,Alpha\n"))
    result = load_candidates(csv)
    assert result[0].candidate_id == "c1"
    assert result[0].candidate_name == "Alpha"


def test_dimension_columns_become_dimensions(tmp_path: Path):
    csv = write_csv(
        tmp_path,
        "c.csv",
        ("candidate_id,candidate_name,speed,cost\nc1,Alpha,fast,low\n"),
    )
    result = load_candidates(csv)
    assert result[0].dimensions == {"speed": "fast", "cost": "low"}


def test_notes_column_mapped(tmp_path: Path):
    csv = write_csv(
        tmp_path,
        "c.csv",
        ("candidate_id,candidate_name,notes\nc1,Alpha,some note\n"),
    )
    assert load_candidates(csv)[0].notes == "some note"


def test_notes_defaults_to_empty_string_when_absent(tmp_path: Path):
    csv = write_csv(tmp_path, "c.csv", ("candidate_id,candidate_name\nc1,Alpha\n"))
    assert load_candidates(csv)[0].notes == ""


def test_notes_not_in_dimensions(tmp_path: Path):
    csv = write_csv(
        tmp_path,
        "c.csv",
        ("candidate_id,candidate_name,notes,speed\nc1,Alpha,a note,fast\n"),
    )
    assert "notes" not in load_candidates(csv)[0].dimensions


def test_reserved_columns_not_in_dimensions(tmp_path: Path):
    csv = write_csv(
        tmp_path,
        "c.csv",
        ("candidate_id,candidate_name,notes,speed\nc1,Alpha,note,fast\n"),
    )
    dims = load_candidates(csv)[0].dimensions
    assert "candidate_id" not in dims
    assert "candidate_name" not in dims
    assert "notes" not in dims


def test_whitespace_stripped_from_headers_and_values(tmp_path: Path):
    csv = write_csv(
        tmp_path,
        "c.csv",
        (" candidate_id , candidate_name , speed \n c1 , Alpha , fast \n"),
    )
    result = load_candidates(csv)
    assert result[0].candidate_id == "c1"
    assert result[0].dimensions == {"speed": "fast"}


def test_none_value_becomes_empty_string(tmp_path: Path):
    # csv.DictReader yields None for a column with no value beyond the last comma
    csv = write_csv(
        tmp_path, "c.csv", ("candidate_id,candidate_name,speed\nc1,Alpha,\n")
    )
    result = load_candidates(csv)
    assert result[0].dimensions["speed"] == ""


def test_empty_file_returns_empty_list(tmp_path: Path):
    csv = write_csv(tmp_path, "c.csv", ("candidate_id,candidate_name\n"))
    assert load_candidates(csv) == []


# ---------------------------------------------------------------------------
# Error-path tests
# ---------------------------------------------------------------------------


def test_raises_for_missing_candidate_id_column(tmp_path: Path):
    csv = write_csv(tmp_path, "c.csv", ("candidate_name,speed\nAlpha,fast\n"))
    with pytest.raises(ValueError, match="candidate_id"):
        load_candidates(csv)


def test_raises_for_missing_candidate_name_column(tmp_path: Path):
    csv = write_csv(tmp_path, "c.csv", ("candidate_id,speed\nc1,fast\n"))
    with pytest.raises(ValueError, match="candidate_name"):
        load_candidates(csv)


def test_raises_for_missing_both_required_columns(tmp_path: Path):
    csv = write_csv(tmp_path, "c.csv", ("speed,cost\nfast,low\n"))
    with pytest.raises(ValueError, match="candidate_id"):
        load_candidates(csv)


def test_raises_for_completely_empty_file(tmp_path: Path):
    csv = write_csv(tmp_path, "c.csv", "")
    with pytest.raises(ValueError, match="header row"):
        load_candidates(csv)
