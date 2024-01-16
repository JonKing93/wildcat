from math import inf
from pathlib import Path

import fiona
import numpy as np
import pytest
from pfdf.raster import CRS, Affine, Raster

import wildcat.preprocess_ as preprocess
from wildcat.utils import log

log.initialize(2)


def check_log(capfd, *messages):
    output = capfd.readouterr().out
    for message in messages:
        assert message in output


def check_quiet(capfd):
    check_log(capfd, "")


def check_error(error, *messages):
    for message in messages:
        assert message in error.value.args[0]


@pytest.fixture
def araster(crs, transform):
    values = np.arange(100).reshape(10, 10)
    return Raster.from_array(values, crs=crs, transform=transform, nodata=0)


@pytest.fixture
def crs():
    return CRS.from_epsg(26910)


@pytest.fixture
def pcrs():
    return CRS.from_epsg(26911)


@pytest.fixture
def transform():
    return Affine(0.5, 0, 0, 0, -0.5, 0)


@pytest.fixture
def fraster(araster, tmp_path):
    path = Path(tmp_path) / "test.tif"
    araster.save(path)
    return path


@pytest.fixture
def perimeter(pcrs, tmp_path):
    path = Path(tmp_path) / "perimeter.shp"
    schema = {"geometry": "Polygon", "properties": {}}
    record = {
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[0, 0], [0, 5], [5, 5], [5, 0], [0, 0]]],
        }
    }
    with fiona.open(
        path,
        "w",
        driver="Shapefile",
        schema=schema,
        crs=pcrs,
    ) as file:
        file.write(record)
    return path


@pytest.fixture
def perimeter2(crs, tmp_path):
    path = Path(tmp_path) / "perimeter.shp"
    schema = {"geometry": "Polygon", "properties": {}}
    record = {
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[0, 0], [0, 5], [5, 5], [5, 0], [0, 0]]],
        }
    }
    with fiona.open(
        path,
        "w",
        driver="Shapefile",
        schema=schema,
        crs=crs,
    ) as file:
        file.write(record)
    return path


@pytest.fixture
def praster(pcrs, transform):
    transform = Affine(transform.a, 0, 0, 0, transform.e, 5)
    values = np.ones((10, 10), dtype=bool)
    return Raster.from_array(values, crs=pcrs, transform=transform, nodata=False)


@pytest.fixture
def dnbr(araster):
    values = araster.values.copy()
    small = values < 10
    values[small] = -5000
    big = values > 90
    values[big] = 5000
    return Raster.from_array(values, spatial=araster, nodata=0)


@pytest.fixture
def kf(araster):
    values = araster.values.copy()
    values[values < 10] = -5
    return Raster.from_array(values, spatial=araster, nodata=0)


class TestFindFolders:
    def test_both_none(_, capfd):
        input, output = preprocess._find_folders(None, None)
        assert input == Path.cwd()
        assert output == Path.cwd() / "preprocessed"
        check_log(capfd, f"Input folder: {Path.cwd()}\n")

    def test_input_only(_, capfd, tmp_path):
        path = Path(tmp_path)
        input, output = preprocess._find_folders(path, None)
        assert input == path
        assert output == path / "preprocessed"
        check_log(capfd, f"Input folder: {path}\n")

    def test_output_only(_, capfd, tmp_path):
        path = Path(tmp_path)
        input, output = preprocess._find_folders(None, path)
        assert input == Path.cwd()
        assert output == path
        check_log(capfd, f"Input folder: {Path.cwd()}\n")

    def test_both(_, capfd, tmp_path):
        path = Path(tmp_path)
        inpath = path / "input"
        outpath = path / "output"
        input, output = preprocess._find_folders(inpath, outpath)
        assert input == inpath
        assert output == outpath
        check_log(capfd, f"Input folder: {inpath}\n")


class TestLoadRasters:
    def test_path(_, fraster, araster, capfd):
        rasters = {"test": (fraster, True)}
        preprocess._load_rasters(rasters, fraster.parent / "other-folder")
        assert rasters == {"test": araster}
        check_log(capfd, "Loading rasters", "\tLoading test raster")

    def test_default(_, fraster, araster, capfd):
        rasters = {"test": (None, True)}
        preprocess._load_rasters(rasters, folder=fraster.parent)
        assert rasters == {"test": araster}
        check_log(capfd, "Loading rasters", "\tLoading test raster")

    def test_empty(_, capfd, tmp_path):
        rasters = {"test": (None, False)}
        preprocess._load_rasters(rasters, folder=Path(tmp_path))
        assert rasters == {}
        check_log(capfd, "Loading rasters", "File not found")

    def test_missing(_, tmp_path):
        rasters = {"test": (None, True)}
        with pytest.raises(FileNotFoundError) as error:
            preprocess._load_rasters(rasters, folder=Path(tmp_path))
        check_error(error, "Could not locate the test raster")


class TestBufferedPerimeter:
    def test_path(_, perimeter, praster, araster, capfd):
        output = preprocess._buffered_perimeter(
            perimeter, perimeter.parent / "other-folder", buffer=10, resolution=araster
        )
        praster.buffer(10)
        assert output == praster
        check_log(
            capfd,
            "Building buffered perimeter mask",
            "\tCreating mask",
            "\tBuffering perimeter",
        )

    def test_default(_, perimeter, praster, araster, capfd):
        output = preprocess._buffered_perimeter(
            None, perimeter.parent, buffer=10, resolution=araster
        )
        praster.buffer(10)
        assert output == praster
        check_log(
            capfd,
            "Building buffered perimeter mask",
            "\tCreating mask",
            "\tBuffering perimeter",
        )

    def test_missing(_, tmp_path, araster):
        with pytest.raises(FileNotFoundError) as error:
            preprocess._buffered_perimeter(None, Path(tmp_path), 10, araster)
        check_error(error, "Could not locate the fire perimeter feature file.")


class TestReproject:
    def test(_, praster, araster, capfd):
        rasters = {
            "perimeter": praster,
            "dem": araster,
            "dnbr": araster,
            "kf_factor": araster,
        }
        preprocess._reproject(rasters)

        assert rasters["perimeter"].crs == araster.crs
        for name in ["dem", "dnbr", "kf_factor"]:
            assert rasters[name].bounds == rasters["perimeter"].bounds
        check_log(
            capfd,
            "Reprojecting perimeter",
            "Reprojecting dnbr",
            "Reprojecting kf_factor",
            "Clipping dem",
            "Clipping dnbr",
            "Clipping kf_factor",
        )


class TestConstrainDnbr:
    def test(self, dnbr, capfd):
        expected = dnbr.values.copy()
        expected[expected < -1000] = -1000
        expected[expected > 1000] = 1000
        preprocess._constrain_dnbr(dnbr, min=-1000, max=1000)
        assert np.array_equal(dnbr.values, expected)
        check_log(capfd, "Constraining dNBR data range")

    def test_disable(self, dnbr, capfd):
        expected = dnbr.copy()
        preprocess._constrain_dnbr(dnbr, min=-inf, max=inf)
        assert dnbr == expected
        check_quiet(capfd)


class TestConstrainKf:
    def check(self, output, initial):
        values = initial.values.copy()
        values[values < 0] = 0
        assert np.array_equal(output.values, values)

    def test_disable(self, kf, capfd):
        expected = kf.copy()
        preprocess._constrain_kf(kf, constrain=False, nodata=None)
        assert kf == expected
        check_quiet(capfd)

    def test_missing_nodata(self, kf):
        kf._nodata = None
        with pytest.raises(ValueError) as error:
            preprocess._constrain_kf(kf, constrain=True, nodata=None)
        check_error(error, "raster does not have a NoData value")

    def test_raster_nodata(self, kf, capfd):
        initial = kf.copy()
        preprocess._constrain_kf(kf, constrain=True, nodata=None)
        self.check(kf, initial)
        check_log(capfd, "Removing negative KF-factors")

    def test_user_nodata(self, kf, capfd):
        kf._nodata = None
        initial = kf.copy()
        preprocess._constrain_kf(kf, constrain=True, nodata=0)
        self.check(kf, initial)
        check_log(capfd, "Removing negative KF-factors")

    def test_both_nodata(self, kf, capfd):
        initial = kf.copy()
        preprocess._constrain_kf(kf, constrain=True, nodata=2.2)
        self.check(kf, initial)
        check_log(capfd, "Removing negative KF-factors")

    def test_nodata_casting(self, kf, capfd):
        kf._nodata = None
        initial = kf.copy()
        preprocess._constrain_kf(kf, constrain=True, nodata=0.2)
        self.check(kf, initial)
        check_log(capfd, "Removing negative KF-factors")

    def test_constrain_int(self, kf, capfd):
        initial = kf.copy()
        preprocess._constrain_kf(kf, constrain=True, nodata=None)
        self.check(kf, initial)
        check_log(capfd, "Removing negative KF-factors")

    def test_constrain_float(self, kf, capfd):
        kf._values = kf._values.astype(float)
        initial = kf.copy()
        preprocess._constrain_kf(kf, constrain=True, nodata=None)
        self.check(kf, initial)
        check_log(capfd, "Removing negative KF-factors")


class TestEstimateSeverity:
    def test(_, crs, transform, capfd):
        values = np.array(
            [
                [-1000, 0, np.nan, 200, 250],
                [251, 400, 500, 600, 1000],
            ]
        )
        raster = Raster.from_array(values, crs=crs, transform=transform)
        preprocess._estimate_severity(raster)
        expected = np.array(
            [
                [1, 1, np.nan, 2, 2],
                [3, 3, 3, 4, 4],
            ]
        )
        np.array_equal(raster.values, expected, equal_nan=True)
        check_log(capfd, "Estimating severity from dNBR")


class TestBuildMasks:
    def evt(_, araster):
        return {"evt": araster}

    def expected(_, araster, values):
        values = np.isin(araster.values, values)
        return Raster.from_array(values, spatial=araster, nodata=False)

    def test_no_evt(_, capfd):
        rasters = {"dem": 1, "dnbr": 2}
        preprocess._build_masks(rasters, [], [])
        assert rasters == {"dem": 1, "dnbr": 2}
        check_quiet(capfd)

    def test_both(self, araster, capfd):
        water = [4, 15, 17]
        developed = [6, 7, 8, 9]
        rasters = self.evt(araster)
        preprocess._build_masks(rasters, water, developed)
        assert rasters == {
            "evt": araster,
            "iswater": self.expected(araster, water),
            "isdeveloped": self.expected(araster, developed),
        }
        check_log(
            capfd,
            "Building EVT masks",
            "Building water mask",
            "Building development mask",
        )

    def test_no_water(self, araster, capfd):
        water = []
        developed = [6, 7, 8, 9]
        rasters = self.evt(araster)
        preprocess._build_masks(rasters, water, developed)
        assert rasters == {
            "evt": araster,
            "isdeveloped": self.expected(araster, developed),
        }
        check_log(capfd, "Building EVT masks", "Building development mask")

    def test_no_developed(self, araster, capfd):
        water = [4, 15, 17]
        developed = []
        rasters = self.evt(araster)
        preprocess._build_masks(rasters, water, developed)
        assert rasters == {
            "evt": araster,
            "iswater": self.expected(araster, water),
        }
        check_log(capfd, "Building EVT masks", "Building water mask")

    def test_neither(self, araster, capfd):
        water = []
        developed = []
        rasters = self.evt(araster)
        preprocess._build_masks(rasters, water, developed)
        assert rasters == {
            "evt": araster,
        }
        check_quiet(capfd)


class TestSaveRasters:
    def test(_, araster, tmp_path):
        folder = Path(tmp_path)
        rasters = {"test": araster, "test2": araster}
        assert not (folder / "test.tif").exists()
        preprocess._save_rasters(folder, rasters)
        assert (folder / "test.tif").exists()
        assert (folder / "test2.tif").exists()


class TestPreprocess:
    def test(_, fraster, perimeter2, dnbr, kf):
        assert perimeter2.exists()
        files = {
            "dem": fraster,
            "dnbr": dnbr,
            "evt": fraster,
            "kf_factor": kf,
        }
        for name, raster in files.items():
            path = fraster.parent / f"{name}.tif"
            Raster(raster).save(path)

        output = preprocess.preprocess(fraster.parent, verbosity=2, save=True)

        assert isinstance(output, dict)
        rasters = (
            "dem",
            "dnbr",
            "evt",
            "kf_factor",
            "perimeter",
            "severity",
            "iswater",
            "isdeveloped",
        )
        assert sorted(output.keys()) == sorted(rasters)
        for raster in output.values():
            assert isinstance(raster, Raster)
        assert output["iswater"].dtype == bool
        assert output["isdeveloped"].dtype == bool
        assert np.min(output["dnbr"].values) == -1000
        assert np.max(output["dnbr"].values) == 1000
        assert output["dem"].crs == output["perimeter"].crs
        assert output["dem"].bounds == output["perimeter"].bounds

        folder = fraster.parent / "preprocessed"
        for raster in output.keys():
            path = folder / f"{raster}.tif"
            assert path.exists()
