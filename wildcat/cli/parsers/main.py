import argparse

from wildcat.cli import parsers


def main():
    # Initialize the main parser
    parser = argparse.ArgumentParser(
        prog="wildcat",
        description="Assess and map post-fire debris-flow hazards",
    )

    # Add subcommands
    subparsers = parser.add_subparsers()
    subcommands = ["initialize", "run", "preprocess", "assess", "map"]
    for command in subcommands:
        module = getattr(parsers, command)
        add_parser = getattr(module, command)
        add_parser(subparsers)
    return parser
