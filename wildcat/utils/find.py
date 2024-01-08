"""
Functions that locate input files
----------
Most wildcat routines require various files as input. Users can provide these
files explicitly, but wildcat is also able to search for default file names.
These functions implement that file searching logic and also log file paths as
appropriate. To locate a default file, the functions scan a folder for a file
with a recognized name and supported extension.
----------
Attributes:
    raster_extensions   - Recognized raster file extensions
    vector_extensions   - Recognzied vector-feature file extensions

Functions:
    file        - Searches a folder for a default file with a known extension
    raster      - Searches for a raster with a known extension
    perimeter   - Searches for a perimeter feature file with known extension
"""

from pathlib import Path
from typing import Sequence

import fiona.drvsupport
import rasterio.drivers

from wildcat.utils import log
from wildcat.utils.typing import PathArg

raster_extensions = rasterio.drivers.raster_driver_extensions().keys()
vector_extensions = fiona.drvsupport.vector_driver_extensions().keys()


def file(
    path: PathArg, folder: Path, name: str, extensions: Sequence[str] = []
) -> Path | None:
    "Searches a folder for a default file with a known extension"

    # If the path already exists, just return it directly
    log.status(2, f"\tFinding {name} file: ", end="")
    if path is not None:
        log.filepath(path)
        return path

    # Otherwise, check for a default file for each extension
    for ext in extensions:
        path = folder / f"{name}.{ext}"
        if path.exists():
            log.filepath(path)
            return path

    # Exit if no file is found
    log.status(2, "File not found")
    return None


def raster(path: PathArg, folder: Path, name: str, required: bool) -> Path | None:
    "Searches for a default raster file using known raster extensions"

    path = file(path, folder, name, raster_extensions)
    if required and path is None:
        raise FileNotFoundError(f"Could not locate the {name} raster file.")
    return path


def perimeter(path: PathArg, folder: Path) -> Path:
    "Searches for a default perimeter file using known vector extensions"

    path = file(path, folder, "perimeter", vector_extensions)
    if path is None:
        raise FileNotFoundError("Could not locate the fire perimeter feature file.")
    return path
