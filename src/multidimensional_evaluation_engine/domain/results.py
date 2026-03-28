"""domain/results.py: Result models for candidate evaluation."""

from dataclasses import dataclass, field

from .candidates import Candidate


def _default_levels() -> dict[str, str]:
    """Return default empty levels mapping."""
    return {}


def _default_visual_levels() -> dict[str, str]:
    """Return default empty visual levels mapping."""
    return {}


@dataclass(frozen=True)
class CandidateResult:
    """Result of evaluating a candidate under a policy.

    Contains computed scores and optional derived representations
    for interpretation or visualization.

    Attributes:
        candidate: The evaluated candidate.
        scores: Mapping of label to numeric score.
        levels: Optional mapping of label to qualitative level
            (e.g., "low", "medium", "high").
        visual_levels: Optional mapping of label to presentation-oriented
            categories (e.g., for UI color or grouping).
    """

    candidate: Candidate
    scores: dict[str, float]
    levels: dict[str, str] = field(default_factory=_default_levels)
    visual_levels: dict[str, str] = field(default_factory=_default_visual_levels)
