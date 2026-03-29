"""reporting/tables.py: Simple text-table reporting for scored results."""

from ..domain.results import CandidateResult


def format_results(results: list[CandidateResult]) -> str:
    """Format evaluation results as a plain-text report.

    Produces a deterministic, human-readable summary of scores for each candidate.

    Args:
        results: List of candidate evaluation results.

    Returns:
        Formatted string suitable for console output or logging.
    """
    lines: list[str] = []

    for r in results:
        lines.append(f"{r.candidate.candidate_id} | {r.candidate.candidate_name}")

        # Separate interpretation labels
        interpretations = [
            label.split(":", 1)[1]
            for label in r.scores
            if label.startswith("interpretation:")
        ]

        # Deterministic ordering for stable output (excluding interpretation keys)
        for label in sorted(r.scores):
            if label.startswith("interpretation:"):
                continue
            score = r.scores[label]
            lines.append(f"  - {label}: {score:.2f}")

        if interpretations:
            lines.append(f"  * interpretation: {', '.join(sorted(interpretations))}")

        lines.append("")

    return "\n".join(lines).rstrip()
