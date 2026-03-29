"""domain/scenario.py: Generic scenario models."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Scenario:
    """A generic scenario for structured exploration."""

    name: str
    description: str
    notes: str = ""
    candidate_overrides: dict[str, str] = field(default_factory=dict)
    policy_overrides: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class EvaluationResult:
    """Structured result for scenario evaluation."""

    decision: str
    reason: str
