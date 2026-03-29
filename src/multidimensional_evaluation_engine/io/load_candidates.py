"""io/load_candidates.py: Load candidates from CSV."""

import csv
from pathlib import Path

from ..domain.candidates import Candidate
from ..domain.factors import FactorForm, FactorSpec, FactorValue
from ..utils.logging_utils import get_logger

logger = get_logger(__name__)

_REQUIRED_COLUMNS = {"candidate_id", "candidate_name"}
_RESERVED_COLUMNS = {"candidate_id", "candidate_name", "notes"}


def load_candidates(
    csv_path: Path,
    factor_specs: list[FactorSpec],
) -> list[Candidate]:
    """Load candidates from a CSV file.

    Candidate factor values are typed using structural factor specifications.

    Args:
        csv_path: Path to the CSV file.
        factor_specs: Structural factor definitions used to type CSV columns.

    Returns:
        List of Candidate objects.

    Raises:
        FileNotFoundError: If the CSV file does not exist.
        ValueError: If required columns are missing, if unknown factor columns
            are present, or if a value cannot be coerced to the required type.
    """
    logger.info(f"Loading candidates from: {csv_path}")
    candidates: list[Candidate] = []

    if not csv_path.exists():
        raise FileNotFoundError(f"Candidate CSV file not found: {csv_path}")

    factor_specs_by_id = {spec.factor_id: spec for spec in factor_specs}

    with csv_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError("CSV file must include a header row.")

        headers = [header.strip() for header in reader.fieldnames]

        missing = _REQUIRED_COLUMNS - set(headers)
        if missing:
            missing_str = ", ".join(sorted(missing))
            raise ValueError(f"CSV file is missing required columns: {missing_str}")

        factor_headers = [header for header in headers if header not in _RESERVED_COLUMNS]

        unknown_headers = [
            header for header in factor_headers if header not in factor_specs_by_id
        ]
        if unknown_headers:
            unknown_str = ", ".join(sorted(unknown_headers))
            raise ValueError(
                f"CSV contains factor columns not defined in factor specs: {unknown_str}"
            )

        for row_number, row in enumerate(reader, start=2):
            cleaned_row = {
                key.strip(): (value.strip() if value is not None else "")
                for key, value in row.items()
                if key is not None
            }

            factor_values: dict[str, FactorValue] = {}

            for factor_id in factor_headers:
                raw_text = cleaned_row.get(factor_id, "")
                spec = factor_specs_by_id[factor_id]
                typed_value = _coerce_candidate_value(
                    raw_text=raw_text,
                    factor_id=factor_id,
                    form=spec.form,
                    row_number=row_number,
                )
                factor_values[factor_id] = FactorValue(
                    factor_id=factor_id,
                    form=spec.form,
                    value=typed_value,
                )

            candidates.append(
                Candidate(
                    candidate_id=cleaned_row["candidate_id"],
                    candidate_name=cleaned_row["candidate_name"],
                    factor_values=factor_values,
                    notes=cleaned_row.get("notes", ""),
                )
            )

    logger.info(f"Loaded {len(candidates)} candidates.")
    return candidates


def _coerce_candidate_value(
    raw_text: str,
    factor_id: str,
    form: FactorForm,
    row_number: int,
) -> str | float | bool:
    """Coerce a CSV cell string into the primitive type required by a factor."""
    if form in {FactorForm.CATEGORICAL, FactorForm.EVIDENCE}:
        return raw_text

    if form == FactorForm.NUMERIC:
        if raw_text == "":
            raise ValueError(
                f"Row {row_number}: factor {factor_id!r} requires a numeric value."
            )
        try:
            return float(raw_text)
        except ValueError as exc:
            raise ValueError(
                f"Row {row_number}: cannot parse numeric value {raw_text!r} "
                f"for factor {factor_id!r}."
            ) from exc

    if form == FactorForm.BINARY:
        normalized = raw_text.lower()
        if normalized in {"true", "yes", "1"}:
            return True
        if normalized in {"false", "no", "0"}:
            return False
        raise ValueError(
            f"Row {row_number}: cannot parse binary value {raw_text!r} "
            f"for factor {factor_id!r}."
        )

    raise ValueError(
        f"Row {row_number}: unsupported factor form {form!r} for factor {factor_id!r}."
    )
