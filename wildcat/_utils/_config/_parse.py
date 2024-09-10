"""
Parse command settings from CLI/keyword args, configuration file, and default settings
----------
Wildcat commands have a large number of settings. As such, wildcat allows users
to specify a command's configuration in a variety of ways. Configuration values
can be set explicitly using CLI/keyword args, configuration files, and built-in
default values. In general, wildcat uses the following hierarchy:

    CLI/keyword args > configuration file > default settings

Essentially, CLI/keyword args have the highest priority, as these must be set
explicitly by the user. If a configuration value was not set by the user, wildcat
next checks the configuration file for a value. Finally, if the value is also not
in the confguration file, wildcat falls back onto a default value. This subpackage
provides the command to parse and return this final configuration namespace.
----------
Functions:
    parse               - Parses and returns a configuration namespace
    load                - Compiles an existing config file and returns its namespace
    _locate_project     - Determines the path to a project folder
    _parse_config_file  - Returns the configuration file namespace
"""

from logging import Logger
from pathlib import Path
from typing import Any

from wildcat._utils._defaults import defaults
from wildcat.errors import ConfigError


def parse(config: dict[str, Any], log: Logger):
    """Determines the configuration values for a wildcat command. Note that the
    'config' input should be the local symbol table for the command (via a call
    to the built-in 'locals' function)"""

    # Locate the project folder and load the config file namespace
    config["project"] = _locate_project(config["project"], log)
    config_file = _parse_config_file(config["project"], log)

    # Parse settings from keyword args, config file, and default settings
    for name, value in config.items():
        if value is None:
            if name in config_file:
                config[name] = config_file[name]
            else:
                config[name] = getattr(defaults, name)
    return config


def _locate_project(project: Any, log: Logger) -> Path:
    "Validates the project folder and resolves its Path"

    # Log steps
    log.info("Parsing configuration")
    log.debug("    Locating project folder")

    # Use the current folder if unspecified
    if project is None:
        project = Path.cwd()

    # Convert to Path
    try:
        project = Path(project).resolve()
    except TypeError as error:
        raise TypeError('Could not convert "project" to a folder path.') from error

    # Must be an existing folder
    if not project.exists():
        raise FileNotFoundError(f"The project folder does not exist.\nPath: {project}")
    elif not project.is_dir():
        raise ValueError(f"The project path is not a folder.\nPath: {project}")

    # Log and return path
    log.debug(f"        {project}")
    return project


def _parse_config_file(project: Path, log: Logger) -> dict:
    """Checks for a configuraton file. If it exists, runs the file and returns
    its namespace dict."""

    # Check for a configuration file. If it exists, return its namespace
    path = project / "configuration.py"
    if path.exists():
        log.debug("    Reading configuration file")
        return load(path)

    # If it doesn't exist, just return an empty namespace
    else:
        log.debug("    No configuration file detected")
        return {}


def load(path: Path) -> dict:
    "Compiltes an existing config file and returns its namespace"

    # Run the config file and return its namespace
    try:
        with open(path, "rb") as file:
            code = compile(file.read(), path.name, "exec")
        config = {}
        exec(code, config)
        return config

    # Informative error if failed
    except SyntaxError as error:
        message = f"There is a syntax error in your configuration file"
        raise ConfigError(message) from error
    except SystemExit as exit:
        message = "The configuration file (or a module it imported) called sys.exit()"
        raise ConfigError(message) from exit
    except Exception as error:
        message = "There is a programmable error in your configuration file"
        raise ConfigError(message) from error
