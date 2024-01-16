"Functions that build the parser for the initialize subcommand"

from pathlib import Path

from wildcat.cli import hooks


def initialize(subparsers):

    # Initialize parser
    initialize = subparsers.add_parser(
        "initialize", help="Initializes a folder and config file for a project"
    )

    # Add required folder option
    initialize.add_argument(
        "folder",
        type=Path,
        help="The folder that will be created to hold the new project",
    )

    # Run the initializer when called
    initialize.set_defaults(run=hooks.initialize)
