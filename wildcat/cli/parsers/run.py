"Functions that build the parser for the run subcommand"


def run(subparsers):
    subparsers.add_parser(
        "run", help="Implement a hazard assessment and map the results"
    )
