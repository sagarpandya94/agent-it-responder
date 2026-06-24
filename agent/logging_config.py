"""
Centralised logging configuration for the IT Responder agent.

Call `setup_logging()` once at the top of main.py.
All other modules simply do `logger = logging.getLogger(__name__)`.
"""

import logging
import sys


def setup_logging(level: str = "INFO") -> None:
    """
    Configure root logger with a clean, readable format.

    Args:
        level: Logging level string — "DEBUG", "INFO", "WARNING", "ERROR".
               Defaults to "INFO". Set to "DEBUG" to see full tool payloads.
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    datefmt = "%H:%M:%S"

    logging.basicConfig(
        level=numeric_level,
        format=fmt,
        datefmt=datefmt,
        stream=sys.stdout,
        force=True,   # override any handlers pytest or other libs may have set
    )

    # Silence noisy third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
