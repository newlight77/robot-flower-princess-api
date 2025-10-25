import logging
import sys
from typing import Any

_LOGGER_CONFIGURED = False


def _configure() -> None:
    global _LOGGER_CONFIGURED
    if _LOGGER_CONFIGURED:
        return
    # Simple, readable default logging configuration for the application
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stdout,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    _LOGGER_CONFIGURED = True


def get_logger(name_or_obj: Any = None) -> logging.Logger:
    """Return a configured logger.

    Accepts either a string name or any object (uses its class name). If nothing
    passed, the module logger name is used.
    """
    _configure()
    if name_or_obj is None:
        name = __name__
    elif isinstance(name_or_obj, str):
        name = name_or_obj
    else:
        # Use the class name for objects to make logs easy to filter
        name = getattr(name_or_obj, "__class__", type(name_or_obj)).__name__

    return logging.getLogger(name)
