from math import inf

import pytest

from wildcat.cli import kwargs, parsers
from wildcat.utils import defaults


def parse(*options):
    parser = parsers.main()
    return parser.parse_args(options)


class TestPreprocess:
    def test_default(_):
        args = parse("preprocess")
        output = kwargs.preprocess(args)
        assert output == {
            "input_folder": None,
            "perimeter": None,
            "dem": None,
            "dnbr": None,
            "kf_factor": None,
            "severity": None,
            "evt": None,
            "buffer": defaults.buffer,
            "dnbr_min": defaults.dnbr_min,
            "dnbr_max": defaults.dnbr_max,
            "constrain_kf": True,
            "kf_nodata": None,
            "water": defaults.water,
            "developed": defaults.developed,
            "save": True,
            "output_folder": None,
            "verbosity": 1,
        }

    def test_disable(_):
        args = parse(
            "preprocess",
            "--dnbr-no-adjust",
            "--no-water",
            "--no-developed",
            "--kf-no-adjust",
        )
        output = kwargs.preprocess(args)
        assert output == {
            "input_folder": None,
            "perimeter": None,
            "dem": None,
            "dnbr": None,
            "kf_factor": None,
            "severity": None,
            "evt": None,
            "buffer": defaults.buffer,
            "dnbr_min": -inf,
            "dnbr_max": inf,
            "constrain_kf": False,
            "kf_nodata": None,
            "water": [],
            "developed": [],
            "save": True,
            "output_folder": None,
            "verbosity": 1,
        }

    def test_set(_):
        args = parse(
            "preprocess",
            "--buffer",
            "1",
            "--dnbr-range",
            "2",
            "3",
            "--kf-nodata",
            "4",
            "--water",
            "5",
            "6",
            "--developed",
            "7",
            "8",
            "9",
        )
        output = kwargs.preprocess(args)
        assert output == {
            "input_folder": None,
            "perimeter": None,
            "dem": None,
            "dnbr": None,
            "kf_factor": None,
            "severity": None,
            "evt": None,
            "buffer": 1,
            "dnbr_min": 2,
            "dnbr_max": 3,
            "constrain_kf": True,
            "kf_nodata": 4,
            "water": [5, 6],
            "developed": [7, 8, 9],
            "save": True,
            "output_folder": None,
            "verbosity": 1,
        }

    @pytest.mark.parametrize(
        "option, level", (("--quiet", 0), ("", 1), ("--verbose", 2))
    )
    def test_verbosity(_, option, level):
        args = parse("preprocess", option)
        output = kwargs.preprocess(args)
        assert output["verbosity"] == level
