"""
Functions that pass CLI args to wildcat commands
----------
The functions in this module use args parsed from the CLI to run a wildcat command.
Each function imports the appropriate subcommand, converts CLI args to a keyword
dict, and then calls the subcommand.

A note on imports:
    This module imports wildcat commands within the functions, rather than at
    the top of the module. This allows the CLI to avoid lengthy imports when
    not necessary. Many of the wildcat subcommands rely on the pysheds package,
    which is quite slow to import. However, other subcommands - such as 
    "wildcat initialize" or displaying help text - do not require this package. 
    Importing the commands within the functions allows the CLI to skip this 
    lengthy import when not needed, thereby returning help/version information quickly.
"""

from wildcat.cli import kwargs


def initialize(args):
    from wildcat.initialize_ import initialize

    initialize(args.folder)


def preprocess(args):
    from wildcat.preprocess_ import preprocess

    args = kwargs.preprocess(args)
    preprocess(**args)
