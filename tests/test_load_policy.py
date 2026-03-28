"""tests/test_load_policy.py: Unit tests for load_policy."""

from pathlib import Path
import tomllib

import pytest

from multidimensional_evaluation_engine.io.load_policy import load_policy
from multidimensional_evaluation_engine.policy.policy import Policy

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def write_toml(tmp_path: Path, filename: str, content: str) -> Path:
    """Write content to a temp TOML file and return its path."""
    p = tmp_path / filename
    p.write_text(content, encoding="utf-8")
    return p


VALID_TOML = """\
[scales.speed]
slow = 1
fast = 3

[scales.cost]
low = 3
high = 1

[weights.overall]
speed = 0.5
cost = 0.5

[interpretation]
low = 1.0
mid = 2.0
high = 3.0
"""


# ---------------------------------------------------------------------------
# Happy-path tests
# ---------------------------------------------------------------------------


def test_returns_policy_instance(tmp_path: Path) -> None:
    path = write_toml(tmp_path, "policy.toml", VALID_TOML)
    result = load_policy(path)
    assert isinstance(result, Policy)


def test_scales_loaded_correctly(tmp_path: Path) -> None:
    path = write_toml(tmp_path, "policy.toml", VALID_TOML)
    result = load_policy(path)
    assert result.scales == {
        "speed": {"slow": 1, "fast": 3},
        "cost": {"low": 3, "high": 1},
    }


def test_weights_loaded_correctly(tmp_path: Path) -> None:
    path = write_toml(tmp_path, "policy.toml", VALID_TOML)
    result = load_policy(path)
    assert result.weights == {"overall": {"speed": 0.5, "cost": 0.5}}


def test_interpretation_loaded_correctly(tmp_path: Path) -> None:
    path = write_toml(tmp_path, "policy.toml", VALID_TOML)
    result = load_policy(path)
    assert result.interpretation == {"low": 1.0, "mid": 2.0, "high": 3.0}


def test_optional_sections_default_to_empty(tmp_path: Path) -> None:
    path = write_toml(tmp_path, "policy.toml", VALID_TOML)
    result = load_policy(path)
    assert result.patterns == []
    assert result.rules == []
    assert result.metadata == {}


def test_optional_sections_loaded_when_present(tmp_path: Path) -> None:
    toml = VALID_TOML + '\n[metadata]\nauthor = "test"\n'
    path = write_toml(tmp_path, "policy.toml", toml)
    result = load_policy(path)
    assert result.metadata == {"author": "test"}


# ---------------------------------------------------------------------------
# Error-path tests
# ---------------------------------------------------------------------------


def test_raises_file_not_found_for_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="Policy file not found"):
        load_policy(tmp_path / "nonexistent.toml")


def test_raises_toml_decode_error_for_invalid_toml(tmp_path: Path) -> None:
    path = write_toml(tmp_path, "bad.toml", "not valid toml = = =")
    with pytest.raises(tomllib.TOMLDecodeError):
        load_policy(path)


def test_raises_key_error_when_scales_missing(tmp_path: Path) -> None:
    toml = """\
[weights.overall]
speed = 0.5

[interpretation]
low = 1.0
"""
    path = write_toml(tmp_path, "policy.toml", toml)
    with pytest.raises(KeyError, match="scales"):
        load_policy(path)


def test_raises_key_error_when_weights_missing(tmp_path: Path) -> None:
    toml = """\
[scales.speed]
fast = 3

[interpretation]
low = 1.0
"""
    path = write_toml(tmp_path, "policy.toml", toml)
    with pytest.raises(KeyError, match="weights"):
        load_policy(path)


def test_raises_key_error_when_interpretation_missing(tmp_path: Path) -> None:
    toml = """\
[scales.speed]
fast = 3

[weights.overall]
speed = 1.0
"""
    path = write_toml(tmp_path, "policy.toml", toml)
    with pytest.raises(KeyError, match="interpretation"):
        load_policy(path)


def test_raises_key_error_when_all_required_sections_missing(tmp_path: Path) -> None:
    path = write_toml(tmp_path, "policy.toml", '[metadata]\nauthor = "x"\n')
    with pytest.raises(KeyError, match="interpretation"):
        load_policy(path)
