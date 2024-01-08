"""
Note that these tests are only checking that the hooks are able to successfully
call the associated subcommand. As such, most tests are designed to trigger a
validation error within the subcommand and exit quickly.
"""
from pathlib import Path

import pytest

from wildcat.cli import hooks, parsers


def check_error(error, message):
    assert error.value.args[0] == message


def parse(*options):
    parser = parsers.main()
    return parser.parse_args(options)


def test_init(tmp_path):
    folder = Path(tmp_path) / "test"
    assert not folder.exists()
    args = parse("init", str(folder.resolve()))
    hooks.init(args)
    assert folder.exists()


def test_preprocess(tmp_path):
    folder = Path(tmp_path)
    args = parse("preprocess", str(folder.resolve()))
    with pytest.raises(FileNotFoundError) as error:
        hooks.preprocess(args)
    check_error(error, "Could not locate the dem raster file.")
