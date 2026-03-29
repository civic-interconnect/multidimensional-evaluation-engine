"""tests/test_load_candidates.py: Unit tests for load_candidates."""


from pathlib import Path

import pytest

from multidimensional_evaluation_engine.domain.candidates import Candidate
from multidimensional_evaluation_engine.domain.factors import FactorValue
from multidimensional_evaluation_engine.io.load_candidates import load_candidates
from tests.builders import make_factor_specs

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def write_csv(tmp_path: Path, filename: str, content: str) -> Path:
    """Write content to a temp CSV file and return its path."""
    path = tmp_path / filename
    path.write_text(content, encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Happy-path tests
# ---------------------------------------------------------------------------


def test_returns_list_of_candidates(tmp_path: Path) -> None:
    csv_path = write_csv(
        tmp_path,
        "c.csv",
        "candidate_id,candidate_name,speed,cost\nc1,Alpha,fast,low\n",
    )
    factor_specs = make_factor_specs()

    result: list[Candidate] = load_candidates(csv_path, factor_specs)

    assert isinstance(result, list)
    assert all(isinstance(candidate, Candidate) for candidate in result)


def test_correct_candidate_count(tmp_path: Path) -> None:
    csv_path = write_csv(
        tmp_path,
        "c.csv",
        (
            "candidate_id,candidate_name,speed,cost\n"
            "c1,Alpha,fast,low\n"
            "c2,Beta,slow,high\n"
            "c3,Gamma,fast,low\n"
        ),
    )
    factor_specs = make_factor_specs()

    result: list[Candidate] = load_candidates(csv_path, factor_specs)

    assert len(result) == 3


def test_candidate_id_and_name_mapped(tmp_path: Path) -> None:
    csv_path = write_csv(
        tmp_path,
        "c.csv",
        "candidate_id,candidate_name,speed,cost\nc1,Alpha,fast,low\n",
    )
    factor_specs = make_factor_specs()

    result: list[Candidate] = load_candidates(csv_path, factor_specs)

    assert result[0].candidate_id == "c1"
    assert result[0].candidate_name == "Alpha"


def test_factor_columns_become_factor_values(tmp_path: Path) -> None:
    csv_path = write_csv(
        tmp_path,
        "c.csv",
        "candidate_id,candidate_name,speed,cost\nc1,Alpha,fast,low\n",
    )
    factor_specs = make_factor_specs()

    result: list[Candidate] = load_candidates(csv_path, factor_specs)
    factor_values: dict[str, FactorValue] = result[0].factor_values

    assert isinstance(factor_values["speed"], FactorValue)
    assert factor_values["speed"].value == "fast"

    assert isinstance(factor_values["cost"], FactorValue)
    assert factor_values["cost"].value == "low"


def test_notes_column_mapped(tmp_path: Path) -> None:
    csv_path = write_csv(
        tmp_path,
        "c.csv",
        "candidate_id,candidate_name,notes,speed,cost\nc1,Alpha,some note,fast,low\n",
    )
    factor_specs = make_factor_specs()

    result: list[Candidate] = load_candidates(csv_path, factor_specs)

    assert result[0].notes == "some note"


def test_notes_defaults_to_empty_string_when_absent(tmp_path: Path) -> None:
    csv_path = write_csv(
        tmp_path,
        "c.csv",
        "candidate_id,candidate_name,speed,cost\nc1,Alpha,fast,low\n",
    )
    factor_specs = make_factor_specs()

    result: list[Candidate] = load_candidates(csv_path, factor_specs)

    assert result[0].notes == ""


def test_notes_not_in_factor_values(tmp_path: Path) -> None:
    csv_path = write_csv(
        tmp_path,
        "c.csv",
        "candidate_id,candidate_name,notes,speed,cost\nc1,Alpha,a note,fast,low\n",
    )
    factor_specs = make_factor_specs()

    result: list[Candidate] = load_candidates(csv_path, factor_specs)

    assert "notes" not in result[0].factor_values


def test_reserved_columns_not_in_factor_values(tmp_path: Path) -> None:
    csv_path = write_csv(
        tmp_path,
        "c.csv",
        "candidate_id,candidate_name,notes,speed,cost\nc1,Alpha,note,fast,low\n",
    )
    factor_specs = make_factor_specs()

    result: list[Candidate] = load_candidates(csv_path, factor_specs)
    factor_values: dict[str, FactorValue] = result[0].factor_values

    assert "candidate_id" not in factor_values
    assert "candidate_name" not in factor_values
    assert "notes" not in factor_values


def test_whitespace_stripped_from_headers_and_values(tmp_path: Path) -> None:
    csv_path = write_csv(
        tmp_path,
        "c.csv",
        " candidate_id , candidate_name , speed , cost \n c1 , Alpha , fast , low \n",
    )
    factor_specs = make_factor_specs()

    result: list[Candidate] = load_candidates(csv_path, factor_specs)

    assert result[0].candidate_id == "c1"
    assert result[0].factor_values["speed"].value == "fast"
    assert result[0].factor_values["cost"].value == "low"


def test_empty_string_becomes_empty_categorical_value(tmp_path: Path) -> None:
    csv_path = write_csv(
        tmp_path,
        "c.csv",
        "candidate_id,candidate_name,speed,cost\nc1,Alpha,,low\n",
    )
    factor_specs = make_factor_specs()

    result: list[Candidate] = load_candidates(csv_path, factor_specs)

    assert result[0].candidate_id == "c1"
    assert result[0].factor_values["speed"].value == ""
    assert result[0].factor_values["cost"].value == "low"


def test_empty_file_returns_empty_list(tmp_path: Path) -> None:
    csv_path = write_csv(tmp_path, "c.csv", "candidate_id,candidate_name\n")
    factor_specs = make_factor_specs()

    result: list[Candidate] = load_candidates(csv_path, factor_specs)

    assert result == []


# ---------------------------------------------------------------------------
# Error-path tests
# ---------------------------------------------------------------------------


def test_raises_for_missing_candidate_id_column(tmp_path: Path) -> None:
    csv_path = write_csv(
        tmp_path,
        "c.csv",
        "candidate_name,speed,cost\nAlpha,fast,low\n",
    )
    factor_specs = make_factor_specs()

    with pytest.raises(ValueError, match="candidate_id"):
        load_candidates(csv_path, factor_specs)


def test_raises_for_missing_candidate_name_column(tmp_path: Path) -> None:
    csv_path = write_csv(
        tmp_path,
        "c.csv",
        "candidate_id,speed,cost\nc1,fast,low\n",
    )
    factor_specs = make_factor_specs()

    with pytest.raises(ValueError, match="candidate_name"):
        load_candidates(csv_path, factor_specs)


def test_raises_for_missing_both_required_columns(tmp_path: Path) -> None:
    csv_path = write_csv(
        tmp_path,
        "c.csv",
        "speed,cost\nfast,low\n",
    )
    factor_specs = make_factor_specs()

    with pytest.raises(ValueError, match="candidate_id"):
        load_candidates(csv_path, factor_specs)


def test_raises_for_completely_empty_file(tmp_path: Path) -> None:
    csv_path = write_csv(tmp_path, "c.csv", "")
    factor_specs = make_factor_specs()

    with pytest.raises(ValueError, match="header row"):
        load_candidates(csv_path, factor_specs)


def test_raises_for_unknown_factor_column(tmp_path: Path) -> None:
    csv_path = write_csv(
        tmp_path,
        "c.csv",
        "candidate_id,candidate_name,speed,cost,unknown_factor\nc1,Alpha,fast,low,x\n",
    )
    factor_specs = make_factor_specs()

    with pytest.raises(ValueError, match="unknown_factor"):
        load_candidates(csv_path, factor_specs)
