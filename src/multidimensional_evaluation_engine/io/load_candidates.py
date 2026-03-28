"""io/load_candidates.py: Load candidates from CSV."""

import csv
from pathlib import Path

from ..domain.candidates import Candidate
from ..utils.logging_utils import get_logger

logger = get_logger(__name__)

# CSV contract (local to loader):
_REQUIRED_COLUMNS = {"candidate_id", "candidate_name"}
_RESERVED_COLUMNS = {"candidate_id", "candidate_name", "notes"}


def load_candidates(csv_path: Path) -> list[Candidate]:
    """Load candidates from a CSV file.

    Args:
        csv_path: Path to the CSV file.

    Returns:
        List of Candidate objects.

    Raises:
        ValueError: If required columns are missing.
    """
    logger.info(f"Loading candidates from: {csv_path}")
    candidates: list[Candidate] = []

    with csv_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError("CSV file must include a header row.")

        headers = [header.strip() for header in reader.fieldnames]

        missing = _REQUIRED_COLUMNS - set(headers)
        if missing:
            missing_str = ", ".join(sorted(missing))
            raise ValueError(f"CSV file is missing required columns: {missing_str}")

        dimension_headers = [
            header for header in headers if header not in _RESERVED_COLUMNS
        ]

        for row in reader:
            cleaned_row = {
                key.strip(): (value.strip() if value is not None else "")
                for key, value in row.items()
                if key is not None
            }

            dimensions = {
                header: cleaned_row.get(header, "") for header in dimension_headers
            }

            candidates.append(
                Candidate(
                    candidate_id=cleaned_row["candidate_id"],
                    candidate_name=cleaned_row["candidate_name"],
                    dimensions=dimensions,
                    notes=cleaned_row.get("notes", ""),
                )
            )

    logger.info(f"Loaded {len(candidates)} candidates.")
    return candidates
