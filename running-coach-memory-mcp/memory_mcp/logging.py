"""Logging configuration for Running Coach Memory MCP."""

import logging
from logging.handlers import RotatingFileHandler

from memory_mcp.config import Settings

# Module logger
logger = logging.getLogger("running_coach_memory")


def setup_logging(settings: Settings) -> None:
    """Configure logging with file handler.

    Args:
        settings: Application settings containing log_path
    """
    log_path = settings.log_file_path
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Configure root logger for this package
    logger.setLevel(logging.DEBUG)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # File handler with rotation (5MB max, keep 3 backups)
    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)

    # Format with timestamp and context
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.info("Logging initialized: %s", log_path)
