"""
Functions that implement console messaging
----------
This module contains functions that implement console messages used to indicate
the progress of a command. The module recognizes 3 verbosity levels:

    0   - Does not print messages to console
    1   - Notifies console of major steps
    2   - Prints detailed progress. Useful for debugging

Calling a wildcat routine will set the _verbosity attribute to the user specified
verbosity level. The logger then compares logging message levels to the requested
verbosity and prints/does-not-print as appropriate.
----------
Internal Attribute:
    _verbosity  - The requested verbosity level for the current routine

Key Functions:
    verbosity   - Parses verbosity level from CLI args
    initialize  - Sets the verbosity level and logs the called command
    status      - Logs a message with the given status level

Leveled Logs:
    stage       - Logs the beginning of a stage (level 1)
    filepath    - Reports a filepath (level 2)
    complete    - Logs the completion of a stage (level 1)
"""

from pathlib import Path
from typing import Literal

level = Literal[0, 1, 2]
_verbosity: level = None


def verbosity(quiet: bool, verbose: bool) -> level:
    "Parses verbosity from CLI args"

    if quiet:
        return 0
    elif verbose:
        return 2
    else:
        return 1


def initialize(level: level):
    "Validates verbosity, sets _verbosity, and logs stage"

    if level not in [0, 1, 2]:
        raise ValueError("Verbosity level must be 0, 1, or 2")
    global _verbosity
    _verbosity = level


def status(level: level, message: str, end: str = "\n") -> None:
    "Prints console messages as appropriate"
    if _verbosity >= level:
        print(message, end=end)


def stage(stage: str) -> None:
    status(1, f"----- {stage} -----")


def filepath(path: Path) -> None:
    "Logs a filepath at level 2"
    status(2, path.resolve())


def complete(stage: str):
    status(1, f"Completed {stage}\n")
