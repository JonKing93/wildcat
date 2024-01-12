"""
Functions that run the initializer
----------
This module contains functions that implement "wildcat init". In brief, this
command creates a project folder with a default configuration file.
----------
Functions:
    init    - Runs the initializer
"""

from wildcat.utils.typing import Pathlike
from pathlib import Path


def init(path: Pathlike):
    """
    Initializes a folder with a configuration file for a project
    ----------
    init(path)
    Creates a new folder at the indicated path and adds a default configuration
    file named "config.py". Raises an error if the folder already exists.
    ----------
    Inputs:
        path: The path to the new project folder.
    """

    # Create the folder. Error if the folder already exists
    path = Path(path).resolve()
    path.mkdir(parents=True, exist_ok=False)
    if path.exists():
        raise FileExistsError(
            "Cannot initialize the project folder because the folder already exists.\n"
            f"Folder Path: {path}"
        )
    path.mkdir(parents=True)

    # Create a configuration file
    config = path / "config.py"
    with open(config, "w") as config:
        config.write("pass")  # Much more will be added here
