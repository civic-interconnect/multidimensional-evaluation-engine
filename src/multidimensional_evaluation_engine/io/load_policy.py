"""io/load_policy.py: Load policy from TOML."""

from pathlib import Path
import tomllib

from ..policy.policy import Policy
from ..utils.logging_utils import get_logger

logger = get_logger(__name__)


def load_policy(path: Path) -> Policy:
    """Load a policy from a TOML file.

    Args:
        path: Path to TOML policy file.

    Returns:
        Policy instance.

    Raises:
        FileNotFoundError: If the file does not exist.
        tomllib.TOMLDecodeError: If TOML parsing fails.
        KeyError: If required policy fields are missing.
    """
    logger.info(f"Loading policy from: {path}")

    if not path.exists():
        raise FileNotFoundError(f"Policy file not found: {path}")

    with path.open("rb") as f:
        data = tomllib.load(f)

    # Minimal structural validation (core-level only)
    required = {"scales", "weights", "interpretation"}
    missing = required - set(data)
    if missing:
        missing_str = ", ".join(sorted(missing))
        raise KeyError(f"Policy is missing required sections: {missing_str}")

    policy = Policy.from_dict(data)

    logger.info("Policy loaded successfully.")
    return policy
