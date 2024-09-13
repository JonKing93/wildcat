"""
Function that returns the names of a function's args
----------
Function:
    collect - Returns a list of function arg names
"""

import inspect
from typing import Callable


def collect(command: Callable) -> list[str]:
    "Returns a list of function arg names"

    return list(inspect.signature(command).parameters.keys())
