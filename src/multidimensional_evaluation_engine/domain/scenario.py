"""domain/scenario.py: Generic scenario models."""

from dataclasses import dataclass, field
from typing import cast


@dataclass(frozen=True)
class Scenario:
    """A generic scenario for structured exploration."""

    name: str
    description: str
    notes: str = ""
    candidate_overrides: dict[str, str] = field(
        default_factory=lambda: cast(dict[str, str], {})
    )
    policy_overrides: dict[str, str] = field(
        default_factory=lambda: cast(dict[str, str], {})
    )


@dataclass(frozen=True)
class EvaluationResult:
    """Structured result for scenario evaluation."""

    decision: str
    reason: str
