"""scenarios/example.py: Example scenario (values are for illustration only)."""

from ..domain.scenario import Scenario


def get_scenario() -> Scenario:
    """Return an example scenario."""
    return Scenario(
        name="Example",
        description="Illustrative scenario for structured exploration.",
        notes="Values are examples only and do not recommend any outcome.",
        candidate_overrides={},
        policy_overrides={},
    )
