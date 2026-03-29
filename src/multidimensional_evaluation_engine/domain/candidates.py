"""domain/candidates.py: Domain models for evaluation inputs."""

from dataclasses import dataclass, field

from .factors import FactorValue


def _default_factor_values() -> dict[str, FactorValue]:
    """Return default empty factor-value mapping."""
    return {}


def _default_metadata() -> dict[str, str]:
    """Return default empty metadata mapping."""
    return {}


@dataclass(frozen=True)
class Candidate:
    """A generic candidate for multidimensional evaluation.

    A candidate represents an entity being evaluated under a policy.
    Domain-specific inputs are carried as raw factor values keyed by factor_id.

    Attributes:
        candidate_id: Stable identifier for the candidate.
        candidate_name: Human-readable name.
        factor_values: Mapping of factor_id to raw primitive value.
        notes: Optional free-text annotation.
        metadata: Optional auxiliary key-value data not used in scoring.
    """

    candidate_id: str
    candidate_name: str
    factor_values: dict[str, FactorValue] = field(
        default_factory=_default_factor_values
    )
    notes: str = ""
    metadata: dict[str, str] = field(default_factory=_default_metadata)
