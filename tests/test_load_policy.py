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
    path = tmp_path / filename
    path.write_text(content, encoding="utf-8")
    return path


VALID_TOML = """\
[[factor_specs]]
factor_id = "speed"
label = "Speed"
form = "categorical"
role = "scored_finding"
allowed_values = ["slow", "fast"]

[[factor_specs]]
factor_id = "cost"
label = "Cost"
form = "categorical"
role = "scored_finding"
allowed_values = ["low", "high"]

[[constraint_rules]]
rule_id = "speed_allowed"
factor_id = "speed"
comparator = "in"
threshold = ["slow", "fast"]
message = "Speed value must be recognized."

[[score_rules]]
rule_id = "speed_score"
factor_id = "speed"
weight = 0.5
categorical_scores = { slow = 1, fast = 3 }

[[score_rules]]
rule_id = "cost_score"
factor_id = "cost"
weight = 0.5
categorical_scores = { low = 3, high = 1 }

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


def test_factor_specs_loaded_correctly(tmp_path: Path) -> None:
    path = write_toml(tmp_path, "policy.toml", VALID_TOML)
    result = load_policy(path)

    assert len(result.factor_specs) == 2
    assert result.factor_specs[0].factor_id == "speed"
    assert result.factor_specs[0].label == "Speed"
    assert result.factor_specs[0].form.value == "categorical"
    assert result.factor_specs[0].allowed_values == ("slow", "fast")

    assert result.factor_specs[1].factor_id == "cost"
    assert result.factor_specs[1].allowed_values == ("low", "high")


def test_constraint_rules_loaded_correctly(tmp_path: Path) -> None:
    path = write_toml(tmp_path, "policy.toml", VALID_TOML)
    result = load_policy(path)

    assert len(result.constraint_rules) == 1
    rule = result.constraint_rules[0]
    assert rule.rule_id == "speed_allowed"
    assert rule.factor_id == "speed"
    assert rule.comparator.value == "in"
    assert rule.threshold == ("slow", "fast")
    assert rule.message == "Speed value must be recognized."


def test_score_rules_loaded_correctly(tmp_path: Path) -> None:
    path = write_toml(tmp_path, "policy.toml", VALID_TOML)
    result = load_policy(path)

    assert len(result.score_rules) == 2

    speed_rule = result.score_rules[0]
    assert speed_rule.rule_id == "speed_score"
    assert speed_rule.factor_id == "speed"
    assert speed_rule.weight == 0.5
    assert speed_rule.categorical_scores == {"slow": 1.0, "fast": 3.0}

    cost_rule = result.score_rules[1]
    assert cost_rule.rule_id == "cost_score"
    assert cost_rule.factor_id == "cost"
    assert cost_rule.weight == 0.5
    assert cost_rule.categorical_scores == {"low": 3.0, "high": 1.0}


def test_interpretation_loaded_correctly(tmp_path: Path) -> None:
    path = write_toml(tmp_path, "policy.toml", VALID_TOML)
    result = load_policy(path)
    assert result.interpretation == {"low": 1.0, "mid": 2.0, "high": 3.0}


def test_metadata_defaults_to_empty(tmp_path: Path) -> None:
    path = write_toml(tmp_path, "policy.toml", VALID_TOML)
    result = load_policy(path)
    assert result.metadata == {}


def test_metadata_loaded_when_present(tmp_path: Path) -> None:
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


def test_raises_key_error_when_factor_specs_missing(tmp_path: Path) -> None:
    toml = """\
[[constraint_rules]]
rule_id = "speed_allowed"
factor_id = "speed"
comparator = "in"
threshold = ["slow", "fast"]
message = "Speed value must be recognized."

[[score_rules]]
rule_id = "speed_score"
factor_id = "speed"
weight = 1.0
categorical_scores = { slow = 1, fast = 3 }

[interpretation]
low = 1.0
"""
    path = write_toml(tmp_path, "policy.toml", toml)
    with pytest.raises(KeyError, match="factor_specs"):
        load_policy(path)


def test_raises_key_error_when_constraint_rules_missing(tmp_path: Path) -> None:
    toml = """\
[[factor_specs]]
factor_id = "speed"
label = "Speed"
form = "categorical"
role = "scored_finding"
allowed_values = ["slow", "fast"]

[[score_rules]]
rule_id = "speed_score"
factor_id = "speed"
weight = 1.0
categorical_scores = { slow = 1, fast = 3 }

[interpretation]
low = 1.0
"""
    path = write_toml(tmp_path, "policy.toml", toml)
    with pytest.raises(KeyError, match="constraint_rules"):
        load_policy(path)


def test_raises_key_error_when_score_rules_missing(tmp_path: Path) -> None:
    toml = """\
[[factor_specs]]
factor_id = "speed"
label = "Speed"
form = "categorical"
role = "scored_finding"
allowed_values = ["slow", "fast"]

[[constraint_rules]]
rule_id = "speed_allowed"
factor_id = "speed"
comparator = "in"
threshold = ["slow", "fast"]
message = "Speed value must be recognized."

[interpretation]
low = 1.0
"""
    path = write_toml(tmp_path, "policy.toml", toml)
    with pytest.raises(KeyError, match="score_rules"):
        load_policy(path)


def test_raises_key_error_when_interpretation_missing(tmp_path: Path) -> None:
    toml = """\
[[factor_specs]]
factor_id = "speed"
label = "Speed"
form = "categorical"
role = "scored_finding"
allowed_values = ["slow", "fast"]

[[constraint_rules]]
rule_id = "speed_allowed"
factor_id = "speed"
comparator = "in"
threshold = ["slow", "fast"]
message = "Speed value must be recognized."

[[score_rules]]
rule_id = "speed_score"
factor_id = "speed"
weight = 1.0
categorical_scores = { slow = 1, fast = 3 }
"""
    path = write_toml(tmp_path, "policy.toml", toml)
    with pytest.raises(KeyError, match="interpretation"):
        load_policy(path)


def test_raises_key_error_when_all_required_sections_missing(tmp_path: Path) -> None:
    path = write_toml(tmp_path, "policy.toml", '[metadata]\nauthor = "x"\n')
    with pytest.raises(KeyError, match="constraint_rules|factor_specs|interpretation|score_rules"):
        load_policy(path)
