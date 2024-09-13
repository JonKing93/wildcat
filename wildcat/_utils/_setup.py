"""
Function implementing setup tasks for a wildcat command
----------
Function:
    command - Initializes logger. Parses and validates config settings
"""

from logging import Logger, getLogger

from wildcat._utils import _config, _validate
from wildcat.typing import Config


def command(command: str, heading: str, locals: Config) -> tuple[Config, Logger]:
    "Initializes logger. Then parses and validates config settings"

    # Create logger and log command heading
    log = getLogger(f"wildcat.{command}")
    log.info(f"----- {heading} -----")

    # Parse and validate config settings
    config = _config.parse(locals, log)
    validate = getattr(_validate, command)
    validate(config)
    return config, log
