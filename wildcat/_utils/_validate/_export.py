"""
Functions that implement specialized validations for export settings
----------
Functions:
    filename    - Checks an input is a string or allowed ASCII text
    file_format - Checks an input is a supported file format driver
    rename      - Checks an input is a property renaming dict
    _strlist    - Checks a parameter value in a renaming dict is a list of strings
"""

from string import ascii_letters, digits
from typing import Any

from pfdf.utils import driver

from wildcat._utils import _parameters
from wildcat._utils._validate._core import aslist, optional_string
from wildcat.typing import Config


def filename(config: Config, name: str) -> None:
    "Checks an input is a string of allowed ascii text"

    # Must be a string. Convert None to an empty string
    optional_string(config, name)
    if config[name] is None:
        config[name] = ""

    # Every character must be an ascii letter, number, -, or _
    allowed = ascii_letters + digits + "-" + "_"
    for c, char in enumerate(config[name]):
        if char not in allowed:
            raise ValueError(
                f'The "{name}" setting must be a string of ASCII letters, numbers, '
                f'underscores, and/or hyphens. However, {name}[{c}] (value = "{char}") '
                f"is not an allowed character."
            )


def file_format(config: Config, name: str) -> None:
    "Checks an input is a string representing a file format driver"

    # Must be a string
    input = config[name]
    if not isinstance(input, str):
        raise TypeError(f'The "{name}" setting must be a string')

    # Get recognized driver names (both standard, and lowercased)
    allowed = driver.vectors().index.tolist()
    allowed_lower = [name.lower() for name in allowed]

    # Require a recognized driver
    input = input.lower()
    if input not in allowed_lower:
        raise ValueError(
            f'The "{name}" setting must be a recognized vector file format driver. '
            "Please see the documentation for a list of recognized drivers."
        )

    # Standardize capitalization
    k = allowed_lower.index(input)
    config[name] = allowed[k]


def rename(config: Config, name: str) -> None:
    "Checks that an input is a valid renaming dict"

    # Convert None to empty dict
    input = config[name]
    if input is None:
        input = {}

    # Must be a dict
    if not isinstance(input, dict):
        raise TypeError(f'The "{name}" setting must be a dict')

    # Each key must be a string
    for k, (key, value) in enumerate(input.items()):
        if not isinstance(key, str):
            raise TypeError(
                f'Each key of the "{name}" dict must be a string, '
                f"but key[{k}] is not."
            )

        # Parameters must use a string list
        elif key in _parameters.names():
            value = _strlist(name, key, value)

        # Anything else must be a string
        elif not isinstance(value, str):
            raise TypeError(
                f'The value of the "{key}" key in the "{name}" setting must be a string.'
            )
    config[name] = input


def _strlist(name: str, key: str, value: Any) -> list[str]:
    "Checks a parameter key of a renaming dict is a string list"

    # None becomes an empty list
    if value is None:
        return []

    # Must be convertible to a list
    elif not isinstance(value, (list, tuple, str)):
        raise TypeError(
            f'The value of the "{key}" key in the "{name}" setting '
            "must be a list, tuple, or string."
        )
    value = aslist(value)

    # Each element must be a string
    for k, element in enumerate(value):
        if not isinstance(element, str):
            raise TypeError(
                f'Each element of the "{key}" key in the "{name}" setting must '
                f'be a string, but {name}["{key}"][{k}] is not.'
            )
    return value
