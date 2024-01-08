from pathlib import Path

import pytest

from wildcat.utils import find, log


@pytest.fixture
def folder(tmp_path):
    return Path(tmp_path)


def file(folder, name):
    path = folder / name
    with open(path, "w") as file:
        file.write("test")
    return path


@pytest.fixture
def raster(folder):
    return file(folder, "test.tif")


@pytest.fixture
def perimeter(folder):
    return file(folder, "perimeter.shp")


def check_log(capfd, message):
    assert message == capfd.readouterr().out


def check_error(error, messages):
    for message in messages:
        assert message in error.value.args[0]


class TestFile:
    def test_exists(_, raster, capfd):
        log.initialize(2)
        output = find.file(raster, raster.parent, "test", [])
        assert output == raster
        check_log(capfd, f"\tFinding test file: {output.resolve()}\n")

    def test_default(_, raster, capfd):
        log.initialize(2)
        output = find.file(
            None, folder=raster.parent, name="test", extensions=find.raster_extensions
        )
        assert output == raster
        check_log(capfd, f"\tFinding test file: {output.resolve()}\n")

    def test_missing(_, folder, capfd):
        log.initialize(2)
        output = find.file(None, folder, "test", ["tif"])
        assert output is None
        check_log(capfd, "\tFinding test file: File not found\n")


class TestRaster:
    def test_default(_, raster):
        output = find.raster(None, raster.parent, "test", required=True)
        assert output == raster

    def test_missing_required(_, folder):
        with pytest.raises(FileNotFoundError) as error:
            find.raster(None, folder, "test", required=True)
        check_error(error, "Could not locate the test raster")

    def test_missing_optional(_, folder):
        output = find.raster(None, folder, "test", required=False)
        assert output is None


class TestPerimeter:
    def test_default(_, perimeter):
        output = find.perimeter(None, perimeter.parent)
        assert output == perimeter

    def test_missing(_, folder):
        with pytest.raises(FileNotFoundError) as error:
            find.perimeter(None, folder)
        check_error(error, "Could not locate the fire perimeter feature file")
