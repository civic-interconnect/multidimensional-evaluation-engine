"""domain/factors.py: Core factor and recorded-value models."""

from dataclasses import dataclass
from enum import StrEnum


class FactorForm(StrEnum):
    """Structural form of a factor value."""

    BINARY = "binary"
    NUMERIC = "numeric"
    CATEGORICAL = "categorical"
    EVIDENCE = "evidence"


@dataclass(frozen=True)
class EvidenceRef:
    """Reference to supporting source material."""

    source_label: str
    locator: str = ""
    note: str = ""


@dataclass(frozen=True)
class FactorValue:
    """Neutral recorded value for one factor."""

    factor_id: str
    form: FactorForm
    value: bool | float | str
    evidence: tuple[EvidenceRef, ...] = ()
    note: str = ""


@dataclass(frozen=True)
class FactorSpec:
    """Structural definition of a factor."""

    factor_id: str
    label: str
    form: FactorForm
    description: str = ""
    unit: str = ""
    allowed_values: tuple[str, ...] = ()
