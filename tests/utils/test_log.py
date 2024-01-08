from pathlib import Path

import pytest

from wildcat.utils import log


@pytest.fixture
def folder(tmp_path):
    return Path(tmp_path)


def check_log(capfd, message):
    assert message == capfd.readouterr().out


def check_quiet(capfd):
    check_log(capfd, "")


def check_error(error, messages):
    for message in messages:
        assert message in error.value.args[0]


class TestInitialize:
    @pytest.mark.parametrize("level", (0, 1, 2))
    def test_valid(_, level):
        log.initialize(level)
        assert log._verbosity == level

    def test_invalid(_):
        with pytest.raises(ValueError) as error:
            log.initialize(2.2)
        check_error(error, "Verbosity level must be 0, 1, or 2")


class TestStatus:
    @pytest.mark.parametrize("level", (1, 2))
    def test_print(_, level, capfd):
        log.initialize(level)
        log.status(1, "test message")
        check_log(capfd, "test message\n")

    def test_quiet(_, capfd):
        log.initialize(0)
        log.status(1, "test message")
        check_quiet(capfd)


class TestStage:
    def test_print(_, capfd):
        log.initialize(1)
        log.stage("Test")
        check_log(capfd, "----- Test -----\n")

    def test_quiet(_, capfd):
        log.initialize(0)
        log.stage("Test")
        check_quiet(capfd)


class TestFilepath:
    def test_print(_, capfd, folder):
        log.initialize(2)
        log.filepath(folder)
        check_log(capfd, f"{folder}\n")

    def test_quiet(_, capfd, folder):
        log.initialize(1)
        log.filepath(folder)
        check_quiet(capfd)


class TestComplete:
    def test_print(_, capfd):
        log.initialize(1)
        log.complete("test")
        check_log(capfd, "Completed test\n\n")

    def test_quiet(_, capfd):
        log.initialize(0)
        log.complete("test")
        check_quiet(capfd)


class TestVerbosity:
    @pytest.mark.parametrize(
        "quiet, verbose, level",
        (
            (True, False, 0),
            (False, False, 1),
            (False, True, 2),
        ),
    )
    def test(_, quiet, verbose, level):
        assert log.verbosity(quiet, verbose) == level
