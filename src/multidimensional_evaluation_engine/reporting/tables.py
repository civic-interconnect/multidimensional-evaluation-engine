"""reporting/tables.py: Simple text-table reporting for scored results."""

from ..domain.results import CandidateResult


def format_results(results: list[CandidateResult]) -> str:
    """Format evaluation results as a plain-text report.

    Produces a deterministic, human-readable summary of scores and
    optional qualitative levels for each candidate.

    Args:
        results: List of candidate evaluation results.

    Returns:
        Formatted string suitable for console output or logging.
    """
    lines: list[str] = []

    for r in results:
        lines.append(f"{r.candidate.candidate_id} | {r.candidate.candidate_name}")

        # Deterministic ordering for stable output
        for label in sorted(r.scores):
            score = r.scores[label]
            level = r.levels.get(label)

            if level:
                lines.append(f"  - {label}: {score:.2f} ({level})")
            else:
                lines.append(f"  - {label}: {score:.2f}")

        lines.append("")

    return "\n".join(lines).rstrip()
