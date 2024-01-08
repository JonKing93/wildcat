"Functions that build the parser for the init subcommand"

from pathlib import Path

from wildcat.cli import hooks


def init(subparsers):

    # Initialize parser
    init = subparsers.add_parser(
        "init", help="Initializes a folder and config file for a project"
    )

    # Add required folder option
    init.add_argument(
        "folder",
        type=Path,
        help="The folder that will be created to hold the new project",
    )

    # Run the initializer when called
    init.set_defaults(run=hooks.init)
