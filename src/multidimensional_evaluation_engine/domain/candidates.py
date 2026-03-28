"""domain/candidates.py: Domain models for evaluation inputs."""

from dataclasses import dataclass, field


def _default_metadata() -> dict[str, str]:
    """Return default empty metadata mapping."""
    return {}


@dataclass(frozen=True)
class Candidate:
    """A generic candidate for multidimensional evaluation.

    A candidate represents an entity being evaluated under a policy.
    All domain-specific attributes are expressed as dimension values.

    Attributes:
        candidate_id: Stable identifier for the candidate.
        candidate_name: Human-readable name.
        dimensions: Mapping of dimension name to categorical value.
        notes: Optional free-text annotation.
        metadata: Optional auxiliary key-value data not used in scoring.
    """

    candidate_id: str
    candidate_name: str
    dimensions: dict[str, str]
    notes: str = ""
    metadata: dict[str, str] = field(default_factory=_default_metadata)
