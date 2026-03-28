"""utils/logging_utils.py: Logging helpers for the project."""

import logging
from pathlib import Path

PROJECT_LOGGER_NAME = "multidimensional_evaluation_engine"


def get_logger(name: str | None = None, level: str = "INFO") -> logging.Logger:
    """Return a configured project logger.

    Args:
        name: Optional child logger name.
        level: Logging level for the root project logger.

    Returns:
        Logger instance scoped to the project.
    """
    logger = logging.getLogger(PROJECT_LOGGER_NAME)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.setLevel(level)

    if name:
        return logger.getChild(name)
    return logger


def log_header(title: str, logger: logging.Logger | None = None) -> None:
    """Log a section header.

    Args:
        title: Header text.
        logger: Logger to use (defaults to project logger).
    """
    active_logger = logger or get_logger()
    active_logger.info("=" * 60)
    active_logger.info(title)
    active_logger.info("=" * 60)


def log_path(
    name: str,
    path: Path | str,
    logger: logging.Logger | None = None,
) -> None:
    """Log a filesystem path.

    Args:
        name: Label for the path.
        path: Filesystem path.
        logger: Logger to use (defaults to project logger).
    """
    active_logger = logger or get_logger()
    active_logger.info(f"{name}: {Path(path)}")
