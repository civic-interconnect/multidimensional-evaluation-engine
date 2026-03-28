"""policy/policy.py: Policy models for multidimensional evaluation."""

from dataclasses import dataclass, field
from typing import Any


def _default_patterns() -> list[dict[str, Any]]:
    """Return default empty pattern list."""
    return []


def _default_rules() -> list[dict[str, Any]]:
    """Return default empty rule list."""
    return []


def _default_metadata() -> dict[str, str]:
    """Return default empty metadata map."""
    return {}


@dataclass(frozen=True)
class Policy:
    """Configuration for multidimensional evaluation.

    A policy defines how candidate dimension values are mapped to numeric
    scores and how those scores are aggregated.

    Attributes:
        scales: Mapping of dimension -> categorical value -> numeric score.
        weights: Mapping of label -> dimension -> weight used in aggregation.
        interpretation: Thresholds for mapping numeric scores to qualitative levels.
        patterns: Optional descriptive patterns associated with configurations.
        rules: Optional rule definitions for annotations or warnings.
        metadata: Optional auxiliary information not used in scoring.
    """

    scales: dict[str, dict[str, int | float]]
    weights: dict[str, dict[str, float]]
    interpretation: dict[str, float]
    patterns: list[dict[str, Any]] = field(default_factory=_default_patterns)
    rules: list[dict[str, Any]] = field(default_factory=_default_rules)
    metadata: dict[str, str] = field(default_factory=_default_metadata)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Policy":
        """Create a Policy from a dictionary.

        Args:
            data: Parsed policy configuration (e.g., from TOML).

        Returns:
            Policy instance.
        """
        return cls(
            scales=data["scales"],
            weights=data["weights"],
            interpretation=data["interpretation"],
            patterns=data.get("patterns", []),
            rules=data.get("rules", []),
            metadata=data.get("metadata", {}),
        )
