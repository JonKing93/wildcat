import argparse
from pathlib import Path

import pytest

from wildcat.cli import hooks
from wildcat.cli.parsers import preprocess
from wildcat.utils import defaults


@pytest.fixture
def path(tmp_path):
    return Path(tmp_path)


def build_parser(add_options, main=False):
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    if not main:
        sub = sub.add_parser("preprocess")
    add_options(sub)
    return parser


class Base:
    def parse(self, *options):
        options = ("preprocess",) + options
        return self.parser.parse_args(options)


class TestPreprocess(Base):
    parser = build_parser(preprocess.preprocess, main=True)

    def test(self):
        args = self.parse()
        assert args.in_folder is None
        assert args.out_folder is None
        assert args.buffer == defaults.buffer
        assert args.quiet == False
        assert args.verbose == False
        assert args.perimeter is None
        assert args.dem is None
        assert args.dnbr is None
        assert args.severity is None
        assert args.evt is None
        assert args.kf_factor is None
        assert args.dnbr_range == [defaults.dnbr_min, defaults.dnbr_max]
        assert args.dnbr_no_adjust == False
        assert args.water == defaults.water
        assert args.no_water == False
        assert args.developed == defaults.developed
        assert args.no_developed == False
        assert args.run is hooks.preprocess


class TestIOFolders(Base):
    parser = build_parser(preprocess.io_folders)

    def test_none(self):
        args = self.parse()
        assert args.in_folder is None
        assert args.out_folder is None

    def test_one(self, path):
        args = self.parse(str(path))
        assert args.in_folder == path
        assert args.out_folder is None

    def test_both(self, path):
        args = self.parse(str(path), str(path))
        assert args.in_folder == path
        assert args.out_folder == path


class TestVerbosity(Base):
    parser = build_parser(preprocess.verbosity)

    def test_neither(self):
        args = self.parse()
        assert args.quiet == False
        assert args.verbose == False

    def test_both(self):
        with pytest.raises(SystemExit):
            self.parse("--quiet", "--verbose")

    @pytest.mark.parametrize("option", ("-v", "--verbose"))
    def test_quiet(self, option):
        args = self.parse(option)
        assert args.quiet == False
        assert args.verbose == True

    @pytest.mark.parametrize("option", ("-q", "--quiet"))
    def test_verbose(self, option):
        args = self.parse(option)
        assert args.quiet == True
        assert args.verbose == False


class TestBuffer(Base):
    parser = build_parser(preprocess.buffer)

    def test_default(self):
        args = self.parse()
        assert args.buffer == defaults.buffer

    def test_set(self):
        args = self.parse("--buffer", "123456")
        assert args.buffer == 123456


class TestFilePaths(Base):
    parser = build_parser(preprocess.file_paths)

    @pytest.mark.parametrize(
        "option", ("perimeter", "dem", "dnbr", "severity", "evt", "kf-factor")
    )
    def test(self, option, path):
        args = self.parse(f"--{option}", str(path))
        att = option.replace("-", "_")
        assert getattr(args, att) == path


class TestValidRanges(Base):
    parser = build_parser(preprocess.valid_ranges)

    def test_default(self):
        args = self.parse()
        assert args.dnbr_range == [defaults.dnbr_min, defaults.dnbr_max]
        assert args.dnbr_no_adjust == False
        assert args.kf_no_adjust == False
        assert args.kf_nodata is None

    def test_set_dnbr(self):
        args = self.parse("--dnbr-range", "1", "2")
        assert args.dnbr_range == [1, 2]
        assert args.dnbr_no_adjust == False

    def test_disable_dnbr(self):
        args = self.parse("--dnbr-no-adjust")
        assert args.dnbr_no_adjust == True

    def test_invalid_dnbr(self):
        with pytest.raises(SystemExit):
            self.parse("--dnbr-range", "1", "2", "--dnbr-no-adjust")

    def test_set_kf(self):
        args = self.parse("--kf-nodata", "2.2")
        assert args.kf_no_adjust == False
        assert args.kf_nodata == 2.2

    def test_disable_kf(self):
        args = self.parse("--kf-no-adjust")
        assert args.kf_no_adjust == True
        assert args.kf_nodata is None

    def test_invalid_kf(self):
        with pytest.raises(SystemExit):
            self.parse("--kf-nodata", "1", "--kf-no-adjust")

    def test_disable_both(self):
        args = self.parse("--kf-no-adjust", "--dnbr-no-adjust")
        assert args.kf_no_adjust == True
        assert args.dnbr_no_adjust == True


class TestEvtMasks(Base):
    parser = build_parser(preprocess.evt_masks)

    def test_default_water(self):
        args = self.parse()
        assert args.water == defaults.water
        assert args.no_water == False

    def test_water(self):
        args = self.parse("--water", "1", "2", "3")
        assert args.water == [1, 2, 3]
        assert args.no_water == False

    def test_no_water(self):
        args = self.parse("--no-water")
        assert args.no_water == True

    def test_invalid_water(self):
        with pytest.raises(SystemExit):
            self.parse("--water", "1", "--no-water")

    def test_default_developed(self):
        args = self.parse()
        assert args.developed == defaults.developed
        assert args.no_developed == False

    def test_developed(self):
        args = self.parse("--developed", "1", "2", "3")
        assert args.developed == [1, 2, 3]
        assert args.no_developed == False

    def test_no_developed(self):
        args = self.parse("--no-developed")
        assert args.no_developed == True

    def test_invalid_developed(self):
        with pytest.raises(SystemExit):
            self.parse("--developed", "1", "--no-developed")
