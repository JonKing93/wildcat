"""
Functions that load datasets as rasters for the preprocessor
----------
Functions:
    buffered_perimeter  - Loads and buffers the fire perimeter
    dem                 - Loads the DEM in the perimeter, requiring georeferencing
    datasets            - Loads the remaining datasets as rasters
"""

import warnings
from logging import Logger

from pfdf.raster import Raster
from rasterio.errors import NotGeoreferencedWarning

import wildcat._utils._paths.preprocess as _paths
from wildcat._utils import _extensions
from wildcat.errors import GeoreferencingError
from wildcat.typing import Config, PathDict, RasterDict


def buffered_perimeter(config: Config, paths: PathDict, log: Logger) -> Raster:
    "Loads and buffers a fire perimeter"

    # Log step and extract inputs
    log.info("Building buffered burn perimeter")
    perimeter = paths["perimeter"]
    buffer_km = config["buffer_km"]

    # Load the initial raster
    log.debug("    Loading perimeter mask")
    if perimeter.suffix in _extensions.vector():
        perimeter = Raster.from_polygons(perimeter, resolution=10, units="meters")
    else:
        perimeter = Raster.from_file(perimeter, isbool=True)
    perimeter.name = "perimeter"

    # Buffer
    log.debug("    Buffering perimeter")
    perimeter.buffer(buffer_km, units="kilometers")
    return perimeter


def dem(paths: PathDict, perimeter: Raster, log: Logger) -> Raster:
    "Loads the DEM in the perimeter, requiring georeferencing"

    # Load the file
    log.info("Loading DEM")
    with warnings.catch_warnings(action="error", category=NotGeoreferencedWarning):
        try:
            dem = Raster.from_file(paths["dem"], name="dem", bounds=perimeter)

        # Informative error if missing a transform
        except NotGeoreferencedWarning:
            raise GeoreferencingError(
                "The input DEM does not have an affine transform. Please provide "
                "a properly georeferenced DEM instead."
            )
    return dem


def datasets(
    config: Config, paths: PathDict, perimeter: Raster, dem: Raster, log: Logger
) -> RasterDict:
    """Loads all remaining datasets as rasters. Returns all loaded rasters
    (including the perimeter and DEM) in a dict"""

    # Log step and initialize rasters dict
    log.info("Loading remaining datasets")
    rasters = {"perimeter": perimeter, "dem": dem}

    # Iterate through remaining datasets. Skip missing files
    for name, path in paths.items():
        if path is None or name in ["perimeter", "dem"]:
            continue
        log.debug(f"    Loading {name}")

        # Detect vector features
        isfeatures = name in _paths.features() and path.suffix in _extensions.vector()

        # Retainment features are points
        if isfeatures and name == "retainments":
            raster = Raster.from_points(path, resolution=dem, bounds=perimeter)

        # KF and severity features require a field
        elif isfeatures and name in _paths.field():
            field_arg = f"{name}_field"
            field = config[field_arg]
            if field is None:
                raise ValueError(
                    f"{name} is a vector feature file, so {field_arg} cannot be None."
                )
            raster = Raster.from_polygons(path, field, resolution=dem, bounds=perimeter)

        # All other features are masks
        elif isfeatures:
            raster = Raster.from_polygons(path, resolution=dem, bounds=perimeter)

        # Non-feature datasets are file-based rasters.
        else:
            raster = Raster.from_file(path, bounds=perimeter)

        # Give each dataset raster a name, and record in a dict
        raster.name = name
        rasters[name] = raster
    return rasters
