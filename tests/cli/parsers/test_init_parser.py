import argparse
from pathlib import Path

import pytest

from wildcat.cli import hooks
from wildcat.cli.parsers import initialize


@pytest.fixture
def parsers():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    return parser, subparsers


class TestInit:
    def test(_, tmp_path, parsers):
        folder = Path(tmp_path).resolve()
        initialize.init(parsers[1])

        args = parsers[0].parse_args(["init", str(folder)])
        assert args.folder == folder
        assert args.run is hooks.init
