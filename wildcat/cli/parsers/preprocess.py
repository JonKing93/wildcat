"Functions that build the parser for the preprocess subcommand"

from pathlib import Path

from wildcat.cli import hooks
from wildcat.utils import defaults


def preprocess(subparsers):
    "Builds the parser for the preprocess subcommand"

    parser = subparsers.add_parser(
        "preprocess", help="Clean input datasets in preparation for assessment"
    )
    io_folders(parser)
    verbosity(parser)
    buffer(parser)
    file_paths(parser)
    valid_ranges(parser)
    evt_masks(parser)
    parser.set_defaults(run=hooks.preprocess)


def io_folders(parser):
    "Adds optional positional arguments for the input and output folders"

    folders = parser.add_argument_group("IO folders")
    folders.add_argument(
        "in_folder",
        nargs="?",
        type=Path,
        help="The default folder containing input files for preprocessing.",
    )
    folders.add_argument(
        "out_folder",
        nargs="?",
        type=Path,
        help="The folder in which to save preprocessed output files.",
    )


def verbosity(parser):
    "Adds options for quiet and verbose console messaging"

    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument(
        "-q", "--quiet", action="store_true", help="Do not print progress messages"
    )
    verbosity.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Prints more detailed progress messages (useful for debugging)",
    )


def buffer(parser):
    "Adds an option for the fire perimeter buffer distance"

    parser.add_argument(
        "--buffer",
        type=float,
        default=defaults.buffer,
        help=(
            f"The distance to buffer the fire perimeter (default: {defaults.buffer}). "
            "Units are the same as the perimeter's CRS (usually meters)."
        ),
    )


def file_paths(parser):
    "Adds options to explicitly provide input file paths"

    # Fire perimeter feature file
    paths = parser.add_argument_group("File Paths")
    paths.add_argument(
        "--perimeter",
        type=Path,
        metavar="path",
        help="The path to the fire perimeter feature file",
    )

    # Raster paths
    rasters = {
        "dem": "the DEM",
        "dnbr": "the dNBR",
        "severity": "a BARC4-like burn severity",
        "evt": "an existing vegetation type",
        "kf-factor": "a KF-factor",
    }
    for name, description in rasters.items():
        option = f"--{name}"
        help = f"The path to {description} raster"
        paths.add_argument(option, type=Path, metavar="path", help=help)


def valid_ranges(parser):
    "Adds options for the valid dNBR and KF-factor ranges"

    # Initialize group
    ranges = parser.add_argument_group("Data Ranges")

    # dNBR
    dnbr = ranges.add_mutually_exclusive_group()
    dnbr.add_argument(
        "--dnbr-range",
        nargs=2,
        type=float,
        default=[defaults.dnbr_min, defaults.dnbr_max],
        metavar=("MIN", "MAX"),
        help=(
            "The min and max data values for the dNBR "
            f"(default: [{defaults.dnbr_min}, {defaults.dnbr_max}]). "
            "Values outside the bounds will be set to the nearest bound."
        ),
    )
    dnbr.add_argument(
        "--dnbr-no-adjust",
        action="store_true",
        help="Stops the preprocessor from constraining dNBR data values.",
    )

    # KF-Factor
    kf = ranges.add_mutually_exclusive_group()
    kf.add_argument(
        "--kf-no-adjust",
        action="store_true",
        help="Stops the preprocessor from constaining KF-factor data to positive values.",
    )
    kf.add_argument(
        "--kf-nodata",
        type=float,
        help=(
            "A NoData value for filling negative KF-factors. "
            "Only used if the KF-factor raster does not already have a NoData value. "
            "The input value will be casted to the dtype of the KF-factor raster."
        ),
    )


def evt_masks(parser):
    "Adds options for the EVT-derived water and development masks"

    # Water
    evt = parser.add_argument_group("EVT Masks")
    water = evt.add_mutually_exclusive_group()
    water.add_argument(
        "--water",
        nargs="+",
        type=float,
        default=defaults.water,
        metavar="evt_class",
        help=(
            "EVT values that should be classified as water. "
            f"(default: {defaults.water[0]})"
        ),
    )
    water.add_argument(
        "--no-water",
        action="store_true",
        help="Stop the preprocessor from creating a water mask.",
    )

    # Development
    developed = evt.add_mutually_exclusive_group()
    developed.add_argument(
        "--developed",
        nargs="+",
        type=float,
        default=defaults.developed,
        metavar="evt_class",
        help=(
            "EVT values that should be classified as developed. "
            f"(default: {defaults.developed[0]} - {defaults.developed[-1]})"
        ),
    )
    developed.add_argument(
        "--no-developed",
        action="store_true",
        help="Stop the preprocessor from creating a development mask.",
    )
