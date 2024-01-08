"""
Functions that run the preprocessor
----------
This module contains functions that implement "wildcat preprocess". Key steps
of this command include:

    * Ensuring required datasets are present,
    * Building a buffered perimeter mask,
    * Reprojecting rasters to have the same CRS, bounds, resolution, and alignment
    * Constraining dNBR to a valid data range,
    * Removing negative KF-factors,
    * Estimating severity from dNBR when necessary, and
    * Building water and development masks from EVT data when available
----------
Main function:
    preprocess          - Runs the preprocessor

Sub-steps:
    _find_folders       - Determines input and output folders
    _load_rasters       - Locates and loads raw raster datasets
    _buffered_perimeter - Builds a buffered burn perimeter mask
    _reproject          - Places rasters in the same CRS, bounds, resolution, and alignment
    _constrain_dnbr     - Constrains the data range of the dNBR raster
    _estimate_severity  - Estimates burn severity from a dNBR
    _build_masks        - Builds water and development masks from EVT data
    _save_rasters       - Saves preprocessed rasters to an output folder
"""

from math import inf
from pathlib import Path
from typing import Optional

import numpy as np
from pfdf import severity
from pfdf.raster import Raster

from wildcat.utils import defaults, find, log
from wildcat.utils.typing import PathArg, Pathlike, scalar, vector

RasterDict = dict[str, Raster]


def preprocess(
    input_folder: Optional[Pathlike] = None,
    perimeter: Optional[Pathlike] = None,
    dem: Optional[Pathlike] = None,
    dnbr: Optional[Pathlike] = None,
    kf_factor: Optional[Pathlike] = None,
    severity: Optional[Pathlike] = None,
    evt: Optional[Pathlike] = None,
    buffer: scalar = defaults.buffer,
    dnbr_min: scalar = defaults.dnbr_min,
    dnbr_max: scalar = defaults.dnbr_max,
    constrain_kf: bool = True,
    kf_nodata: Optional[scalar] = None,
    water: vector = defaults.water,
    developed: vector = defaults.developed,
    save: bool = False,
    output_folder: Optional[Pathlike] = None,
    verbosity: log.level = 1,
) -> RasterDict:

    # Initialize the logger and the raster dict -- name: (path, required)
    log.initialize(verbosity)
    log.stage("Preprocessing")
    rasters = {
        "dem": (dem, True),
        "dnbr": (dnbr, True),
        "severity": (severity, False),
        "evt": (evt, False),
        "kf_factor": (kf_factor, True),
    }

    # Locate IO folders and load rasters. Check default locations whenever an
    # input is missing.
    input_folder, output_folder = _find_folders(input_folder, output_folder)
    _load_rasters(rasters, input_folder)

    # Build the buffered fire perimeter raster mask. Reproject the rasters to
    # match the CRS and alignment of the DEM, then clip to the bounds of the perimeter
    rasters["perimeter"] = _buffered_perimeter(
        perimeter, input_folder, buffer, resolution=rasters["dem"]
    )
    _reproject(rasters)

    # Constrain dNBR to valid range. Constrain KF-factors to positive values
    _constrain_dnbr(rasters["dnbr"], dnbr_min, dnbr_max)
    _constrain_kf(rasters["kf_factor"], constrain_kf, kf_nodata)

    # Estimate severity from dNBR if severity is missing. Build water and
    # development masks if an EVT was provided
    if "severity" not in rasters:
        rasters["severity"] = _estimate_severity(rasters["dnbr"])
    _build_masks(rasters, water, developed)

    # Optionally save, then return the dict of Raster objects
    if save:
        _save_rasters(output_folder, rasters)
    log.complete("preprocessing")
    return rasters


def _find_folders(input: Pathlike, output: Pathlike) -> tuple[Path, Path]:
    "Locates the default input and output folders"

    # Input
    if input is None:
        input = Path.cwd()
    log.status(2, f"Input folder: {input.resolve()}")

    # Output
    if output is None:
        output = input / "preprocessed"
    return input, output


def _load_rasters(rasters: dict[str, tuple[PathArg, bool]], folder: Path) -> None:
    """ "
    Locates and loads raw raster datasets. If a raster is missing, checks default
    file names. Raises an error if the raster is required, but can't be found.
    """

    # Get the path to each raster. Raises error if a required raster is missing
    empty = []
    log.status(1, "Loading rasters")
    for name, (path, required) in rasters.items():
        path = find.raster(path, folder, name, required)

        # Load any raster that is found
        if path is not None:
            log.status(2, f"\tLoading {name} raster")
            rasters[name] = Raster.from_file(path)

        # Remove empty rasters from the dict
        else:
            empty.append(name)
    for raster in empty:
        del rasters[raster]


def _buffered_perimeter(
    path: PathArg, folder, buffer: scalar, resolution: Raster
) -> Raster:
    "Builds a buffered perimeter mask from a polygon feature file"

    log.status(1, "Building buffered perimeter mask")
    path = find.perimeter(path, folder)
    log.status(2, "\tCreating mask")
    perimeter = Raster.from_polygons(path, resolution)
    log.status(2, "\tBuffering perimeter")
    perimeter.buffer(buffer)
    return perimeter


def _reproject(rasters) -> None:
    "Places rasters in the same CRS, bounds, resolution, and alignment"

    # Get the resampling algorithm for each raster
    resampling = {
        "perimeter": "max",
        "dnbr": "bilinear",
        "severity": "nearest",
        "kf_factor": "bilinear",
        "severity": "nearest",
        "evt": "nearest",
    }

    # Reproject to match the CRS, resolution, and alignment of the DEM
    for name, raster in rasters.items():
        if name != "dem":
            log.status(2, f"\tReprojecting {name}")
            raster.reproject(template=rasters["dem"], resampling=resampling[name])

    # Once everything (including perimeter) is reprojected, clip to the perimeter bounds
    for name, raster in rasters.items():
        log.status(2, f"\tClipping {name}")
        raster.clip(bounds=rasters["perimeter"])


def _constrain_dnbr(dnbr: Raster, min: scalar, max: scalar) -> None:
    "Restrict dNBR data values to a valid range"

    if min > -inf or max < inf:
        log.status(1, "Constraining dNBR data range")
        dnbr.set_range(min, max)


def _constrain_kf(kf: Raster, constrain: bool, nodata: scalar | None) -> None:
    "Replace negative KF-factor values with NoData"

    # If constraining, parse NoData. Ignore if the raster has NoData
    if constrain:
        log.status(1, "Removing negative KF-factors")
        if kf.nodata is not None:
            nodata = None

        # Constrain min to the smallest positive value in the dtype of the raster
        if np.issubdtype(kf.dtype, np.integer):
            min = 1
        else:
            min = np.nextafter(0, np.inf, dtype=kf.dtype)
        kf.set_range(min=min, fill=True, nodata=nodata, casting="unsafe")


def _estimate_severity(dnbr: Raster) -> Raster:
    "Estimates severity from a dNBR raster"
    log.status(1, "Estimating severity from dNBR")
    return severity.estimate(dnbr)


def _build_masks(rasters: RasterDict, water: vector, developed: vector) -> None:
    "Builds water and development EVT masks when possible"

    # Check if we can build masks
    if "evt" in rasters:
        mask_water = len(water) > 0
        mask_developed = len(developed) > 0
        if mask_water or mask_developed:
            log.status(1, "Building EVT masks")

        # Build the water mask
        if mask_water:
            log.status(2, "\tBuilding water mask")
            rasters["iswater"] = rasters["evt"].find(water)

        # Build the development mask
        if mask_developed:
            log.status(2, "\tBuilding development mask")
            rasters["isdeveloped"] = rasters["evt"].find(developed)


def _save_rasters(folder: Path, rasters: RasterDict) -> None:
    "Saves preprocessed rasters to an output folder"

    log.status(1, "Saving rasters")
    log.status(2, f"\tCreating output folder: {folder.resolve()}")
    folder.mkdir(parents=True, exist_ok=True)
    for name, raster in rasters.items():
        log.status(2, f"\tSaving {name} raster")
        path = folder / f"{name}.tif"
        raster.save(path, overwrite=True)
