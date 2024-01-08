"Functions that build the parser for the assess subcommand"


def assess(subparsers):
    subparsers.add_parser(
        "assess", help="Compute a hazard assessment from preprocessed inputs"
    )
