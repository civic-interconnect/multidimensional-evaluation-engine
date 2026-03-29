"""policy/policy.py: Policy models for multidimensional evaluation."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, cast

from ..domain.factors import FactorForm, FactorSpec


class EvaluationRole(str, Enum):
    """Role a factor plays in evaluation."""

    HARD_CONSTRAINT = "hard_constraint"
    SCORED_FINDING = "scored_finding"


class Comparator(str, Enum):
    """Comparison operator for threshold rules."""

    LT = "lt"
    LE = "le"
    EQ = "eq"
    GE = "ge"
    GT = "gt"
    IN = "in"


def _default_metadata() -> dict[str, str]:
    """Return default empty metadata map."""
    return {}


def _default_factor_specs() -> list["FactorSpec"]:
    """Return default empty factor specification list."""
    return []


def _default_constraint_rules() -> list["ConstraintRule"]:
    """Return default empty constraint rule list."""
    return []


def _default_score_rules() -> list["ScoreRule"]:
    """Return default empty score rule list."""
    return []


def _default_string_float_map() -> dict[str, float]:
    """Return default empty string-float mapping."""
    return {}


def _default_bool_float_map() -> dict[bool, float]:
    """Return default empty bool-float mapping."""
    return {}


def _default_interpretation() -> dict[str, float]:
    """Return default empty interpretation mapping."""
    return {}


@dataclass(frozen=True)
class ConstraintRule:
    """Rule for evaluating a hard constraint.

    Attributes:
        rule_id: Stable identifier for the rule.
        factor_id: Factor to which this rule applies.
        comparator: Comparison operator.
        threshold: Comparison target. May be bool, number, string, or tuple.
        message: Human-readable result text.
        rationale: Optional explanation of why the rule exists.
    """

    rule_id: str
    factor_id: str
    comparator: Comparator
    threshold: bool | float | str | tuple[str, ...]
    message: str
    rationale: str = ""


@dataclass(frozen=True)
class NumericBand:
    """Numeric range mapped to a score and optional qualitative band.

    Attributes:
        min_inclusive: Inclusive lower bound.
        max_inclusive: Inclusive upper bound.
        score: Numeric score assigned to values in this band.
        band: Optional qualitative label such as 'low' or 'strong'.
    """

    min_inclusive: float
    max_inclusive: float
    score: float
    band: str = ""


@dataclass(frozen=True)
class ScoreRule:
    """Rule for converting a factor value into a score.

    Exactly one mapping style must be used for a given rule:
    - categorical_scores for categorical factors
    - numeric_bands for numeric factors
    - binary_scores for binary factors

    Raises:
        ValueError: If not exactly one mapping style is populated.
    """

    rule_id: str
    factor_id: str
    weight: float
    categorical_scores: dict[str, float] = field(
        default_factory=_default_string_float_map
    )

    numeric_bands: tuple[NumericBand, ...] = ()
    binary_scores: dict[bool, float] = field(default_factory=_default_bool_float_map)
    rationale: str = ""

    def __post_init__(self) -> None:
        """Validate that exactly one mapping style is populated."""
        active = sum(
            (
                bool(self.categorical_scores),
                bool(self.numeric_bands),
                bool(self.binary_scores),
            )
        )
        if active != 1:
            raise ValueError(
                f"ScoreRule {self.rule_id!r} must specify exactly one mapping style "
                f"(categorical_scores, numeric_bands, or binary_scores); "
                f"{active} were populated."
            )


@dataclass(frozen=True)
class Policy:
    """Configuration for multidimensional evaluation.

    A policy defines:
    - which factors are recognized
    - which factors are hard constraints versus scored findings
    - how raw factor values are mapped to pass/fail findings or scores
    - how aggregate numeric results are interpreted

    Note:
        factor_specs, constraint_rules, and score_rules are stored as lists
        for construction convenience. Callers should treat them as logically
        immutable; the frozen dataclass prevents field reassignment but does
        not prevent mutation of list contents.
    """

    factor_specs: list[FactorSpec] = field(default_factory=_default_factor_specs)
    constraint_rules: list[ConstraintRule] = field(
        default_factory=_default_constraint_rules
    )
    score_rules: list[ScoreRule] = field(default_factory=_default_score_rules)
    interpretation: dict[str, float] = field(default_factory=_default_interpretation)
    metadata: dict[str, str] = field(default_factory=_default_metadata)

    def __post_init__(self) -> None:
        """Validate cross-references between factor specs and rules."""
        known_ids = {spec.factor_id for spec in self.factor_specs}

        for rule in self.constraint_rules:
            if rule.factor_id not in known_ids:
                raise ValueError(
                    f"ConstraintRule {rule.rule_id!r} references unknown "
                    f"factor_id {rule.factor_id!r}."
                )

        for rule in self.score_rules:
            if rule.factor_id not in known_ids:
                raise ValueError(
                    f"ScoreRule {rule.rule_id!r} references unknown "
                    f"factor_id {rule.factor_id!r}."
                )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Policy":
        """Create a Policy from a dictionary.

        Args:
            data: Parsed policy configuration, typically from TOML.

        Returns:
            Policy instance with typed factor and rule objects.
        """
        raw_factor_specs = _as_list_of_maps(data.get("factor_specs", []))
        raw_constraint_rules = _as_list_of_maps(data.get("constraint_rules", []))
        raw_score_rules = _as_list_of_maps(data.get("score_rules", []))

        factor_specs = [
            FactorSpec(
                factor_id=str(item["factor_id"]),
                label=str(item["label"]),
                form=FactorForm(str(item["form"])),
                description=str(item.get("description", "")),
                unit=str(item.get("unit", "")),
                allowed_values=tuple(str(v) for v in item.get("allowed_values", ())),
            )
            for item in raw_factor_specs
        ]

        constraint_rules = [
            ConstraintRule(
                rule_id=str(item["rule_id"]),
                factor_id=str(item["factor_id"]),
                comparator=Comparator(str(item["comparator"])),
                threshold=_coerce_threshold(item["threshold"]),
                message=str(item["message"]),
                rationale=str(item.get("rationale", "")),
            )
            for item in raw_constraint_rules
        ]

        score_rules = [
            ScoreRule(
                rule_id=str(item["rule_id"]),
                factor_id=str(item["factor_id"]),
                weight=float(item["weight"]),
                categorical_scores=_as_string_float_map(
                    item.get("categorical_scores", {})
                ),
                numeric_bands=tuple(
                    NumericBand(
                        min_inclusive=float(band["min_inclusive"]),
                        max_inclusive=float(band["max_inclusive"]),
                        score=float(band["score"]),
                        band=band.get("band", ""),
                    )
                    for band in item.get("numeric_bands", [])
                ),
                binary_scores=_as_bool_float_map(item.get("binary_scores", {})),
                rationale=str(item.get("rationale", "")),
            )
            for item in raw_score_rules
        ]

        return cls(
            factor_specs=factor_specs,
            constraint_rules=constraint_rules,
            score_rules=score_rules,
            interpretation=_as_string_float_map(data.get("interpretation", {})),
            metadata=_as_string_string_map(data.get("metadata", {})),
        )


# ---------------------------------------------------------------------------
# Internal coercion helpers
# ---------------------------------------------------------------------------


def _as_string_float_map(value: Any) -> dict[str, float]:
    """Return a mapping with string keys and float values."""
    if not isinstance(value, Mapping):
        raise TypeError(f"Expected mapping, got {type(value).__name__}.")
    m = cast(Mapping[str, Any], value)
    result: dict[str, float] = {}
    for key, item in m.items():
        result[str(key)] = float(item)
    return result


def _as_bool_float_map(value: Any) -> dict[bool, float]:
    """Return a mapping with bool keys and float values."""
    if not isinstance(value, Mapping):
        raise TypeError(f"Expected mapping, got {type(value).__name__}.")
    m = cast(Mapping[str, Any], value)
    return {_coerce_bool(k): float(v) for k, v in m.items()}


def _as_string_string_map(value: Any) -> dict[str, str]:
    """Return a mapping with string keys and string values."""
    if not isinstance(value, Mapping):
        raise TypeError(f"Expected mapping, got {type(value).__name__}.")
    m = cast(Mapping[str, Any], value)
    result: dict[str, str] = {}
    for key, item in m.items():
        result[str(key)] = str(item)
    return result


def _as_list_of_maps(value: Any) -> list[dict[str, Any]]:
    """Return a list of string-keyed dictionaries."""
    if not isinstance(value, list):
        raise TypeError(f"Expected list, got {type(value).__name__}.")
    result: list[dict[str, Any]] = []
    for item in cast(list[object], value):
        if not isinstance(item, Mapping):
            raise TypeError(f"Expected mapping in list, got {type(item).__name__}.")
        m = cast(Mapping[str, Any], item)
        mapped: dict[str, Any] = {}
        for key, mapped_item in m.items():
            mapped[str(key)] = mapped_item
        result.append(mapped)
    return result


def _coerce_threshold(value: Any) -> bool | float | str | tuple[str, ...]:
    """Normalize threshold values loaded from configuration.

    Note:
        The bool check must precede the int/float check because bool is a
        subclass of int in Python; without this ordering, True and False
        would be silently coerced to 1.0 and 0.0.
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return tuple(str(item) for item in cast(list[Any], value))
    if isinstance(value, tuple):
        return tuple(str(item) for item in cast(tuple[Any, ...], value))
    raise TypeError(f"Unsupported threshold value: {value!r}")


def _coerce_bool(value: Any) -> bool:
    """Convert configuration keys or values into booleans."""
    if isinstance(value, bool):
        return value
    normalized = str(value).strip().lower()
    if normalized in {"true", "yes", "1"}:
        return True
    if normalized in {"false", "no", "0"}:
        return False
    raise ValueError(f"Cannot coerce to bool: {value!r}")
