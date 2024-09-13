"""
Functions to locate file paths from config settings and log the results
----------
Functions:
    io_folders      - Locates IO folders and logs the paths
    inputs          - Locates input datasets for the preprocessor
    preprocessed    - Locates preprocessed rasters for the assessment
    _resolved_paths - Resolves config paths and logs the locations
"""

from logging import Logger
from pathlib import Path

from wildcat._utils import _paths
from wildcat._utils._find import _file, _folders
from wildcat.typing import Config, IOFolders, PathDict


def io_folders(config: Config, inputs: str, outputs: str, log: Logger) -> IOFolders:
    "Locates IO folders using config settings and logs the paths"

    return _folders.io_folders(
        config["project"],
        config[inputs],
        inputs,
        config[outputs],
        outputs,
        log,
    )


def inputs(config: Config, folder: Path, log: Logger) -> PathDict:
    "Locate the paths to input datasets for the preprocessor"

    # Initialize path dict with config settings. Optionally include kf_fill
    paths = {name: config[name] for name in _paths.preprocess.standard()}
    if not isinstance(config["kf_fill"], (bool, float, int)):
        paths["kf_fill"] = config["kf_fill"]

    # Locate each path
    return _resolved_paths(
        paths,
        folder,
        required=_paths.preprocess.required(),
        features=_paths.preprocess.features(),
        log=log,
        title="input datasets",
    )


def preprocessed(config: Config, folder: Path, log: Logger) -> PathDict:
    "Locate the paths to preprocessed rasters for the assessment"

    paths = {name: config[name] for name in _paths.assess.all()}
    return _resolved_paths(
        paths,
        folder,
        required=_paths.assess.required(),
        features=[],
        log=log,
        title="preprocessed rasters",
    )


def _resolved_paths(
    paths: PathDict,
    folder: Path,
    required: list[str],
    features: list[str],
    log: Logger,
    title: str,
) -> PathDict:
    "Resolves config paths and logs the locations"

    # Start logger and get message padding
    log.info(f"Locating {title}")
    padding = max([len(name) for name in paths]) + 3

    # Resolve the path to each dataset
    for name, input in paths.items():
        paths[name] = _file.file(
            folder, input, name, name in required, name in features
        )

        # Log each path
        heading = f"{name}: ".ljust(padding, " ")
        log.debug(f"    {heading}{paths[name]}")
    return paths
