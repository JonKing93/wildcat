"Functions that build the parser for the map subcommand"


def map(subparsers):
    subparsers.add_parser("map", help="Create hazard maps from assessment results")
