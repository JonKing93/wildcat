import numpy as np
import pytest
from pfdf.projection import Transform
from pfdf.raster import Raster

from wildcat import version
from wildcat._commands.preprocess import _save


@pytest.fixture
def raster():
    raster = np.arange(100).reshape(20, 5)
    return Raster.from_array(raster, crs=26911, transform=(10, 10, 0, 0))


@pytest.fixture
def config():
    return {
        "buffer_km": 3,
        "resolution_limits_m": [6.5, 11],
        "resolution_check": "error",
        "dem_crs": 26911,
        "dem_transform": Transform(10, 10, 0, 0),
        "dnbr_scaling_check": "error",
        "constrain_dnbr": True,
        "dnbr_limits": [-2000, 2000],
        "severity_field": None,
        "estimate_severity": True,
        "severity_thresholds": [125, 250, 500],
        "contain_severity": True,
        "kf_field": None,
        "constrain_kf": True,
        "missing_kf_check": "warn",
        "missing_kf_threshold": 0.05,
        "kf_fill": 2.2,
        "kf_fill_field": None,
        "water": 7292,
        "developed": [7296, 7297, 7298, 7299],
        "excluded_evt": [],
    }


@pytest.fixture
def paths(inputs):
    return {
        "perimeter": inputs / "perimeter.tif",
        "dem": inputs / "dem.tif",
        "excluded": None,
    }


class TestRasters:
    def test(_, outputs, raster, logcheck):
        perimeter = outputs / "perimeter.tif"
        dem = outputs / "dem.tif"
        rasters = {"perimeter": raster, "dem": raster}

        assert not perimeter.exists()
        assert not dem.exists()
        _save.rasters(outputs, rasters, logcheck.log)
        assert perimeter.exists()
        assert dem.exists()

        logcheck.check(
            [
                ("INFO", "Saving preprocessed rasters"),
                ("DEBUG", "    Saving perimeter"),
                ("DEBUG", "    Saving dem"),
            ]
        )

    def test_overwrite(_, outputs, raster, logcheck):
        with open(outputs / "perimeter.tif", "w") as file:
            file.write("a text file")
        with open(outputs / "dem.tif", "w") as file:
            file.write("a text file")

        perimeter = outputs / "perimeter.tif"
        dem = outputs / "dem.tif"
        rasters = {"perimeter": raster, "dem": raster}

        _save.rasters(outputs, rasters, logcheck.log)
        assert perimeter.exists()
        assert dem.exists()
        Raster(perimeter)
        Raster(dem)

        logcheck.check(
            [
                ("INFO", "Saving preprocessed rasters"),
                ("DEBUG", "    Saving perimeter"),
                ("DEBUG", "    Saving dem"),
            ]
        )


class TestConfig:
    def test(_, outputs, config, paths, outtext, logcheck):
        path = outputs / "configuration.txt"
        assert not path.exists()
        _save.config(outputs, config, paths, logcheck.log)
        assert path.exists()
        logcheck.check([("DEBUG", "    Saving configuration.txt")])

        perimeter = paths["perimeter"]
        dem = paths["dem"]
        assert outtext(path) == (
            f"# Preprocessor configuration for wildcat v{version()}\n"
            "\n"
            "# Input datasets\n"
            f'perimeter = r"{perimeter}"\n'
            f'dem = r"{dem}"\n'
            f"excluded = None\n"
            "\n"
            "# Perimeter\n"
            "buffer_km = 3\n"
            "\n"
            "# DEM\n"
            "resolution_limits_m = [6.5, 11]\n"
            'resolution_check = "error"\n'
            "\n"
            "# dNBR\n"
            'dnbr_scaling_check = "error"\n'
            "constrain_dnbr = True\n"
            "dnbr_limits = [-2000, 2000]\n"
            "\n"
            "# Burn Severity\n"
            "severity_field = None\n"
            "estimate_severity = True\n"
            "severity_thresholds = [125, 250, 500]\n"
            "contain_severity = True\n"
            "\n"
            "# KF-factors\n"
            "kf_field = None\n"
            "constrain_kf = True\n"
            'missing_kf_check = "warn"\n'
            "missing_kf_threshold = 0.05\n"
            "kf_fill = 2.2\n"
            "kf_fill_field = None\n"
            "\n"
            "# EVT masks\n"
            "water = 7292\n"
            "developed = [7296, 7297, 7298, 7299]\n"
            "excluded_evt = []\n\n"
        )

    def test_kf_fill_file(_, outputs, config, paths, outtext, logcheck):
        kf_fill = paths["perimeter"].parent / "kf_fill.shp"
        paths["kf_fill"] = kf_fill
        config["kf_fill_field"] = "KFFACT"

        path = outputs / "configuration.txt"
        assert not path.exists()
        _save.config(outputs, config, paths, logcheck.log)
        assert path.exists()
        logcheck.check([("DEBUG", "    Saving configuration.txt")])

        perimeter = paths["perimeter"]
        dem = paths["dem"]
        assert outtext(path) == (
            f"# Preprocessor configuration for wildcat v{version()}\n"
            "\n"
            "# Input datasets\n"
            f'perimeter = r"{perimeter}"\n'
            f'dem = r"{dem}"\n'
            f"excluded = None\n"
            "\n"
            "# Perimeter\n"
            "buffer_km = 3\n"
            "\n"
            "# DEM\n"
            "resolution_limits_m = [6.5, 11]\n"
            'resolution_check = "error"\n'
            "\n"
            "# dNBR\n"
            'dnbr_scaling_check = "error"\n'
            "constrain_dnbr = True\n"
            "dnbr_limits = [-2000, 2000]\n"
            "\n"
            "# Burn Severity\n"
            "severity_field = None\n"
            "estimate_severity = True\n"
            "severity_thresholds = [125, 250, 500]\n"
            "contain_severity = True\n"
            "\n"
            "# KF-factors\n"
            "kf_field = None\n"
            "constrain_kf = True\n"
            'missing_kf_check = "warn"\n'
            "missing_kf_threshold = 0.05\n"
            f'kf_fill = r"{kf_fill}"\n'
            'kf_fill_field = "KFFACT"\n'
            "\n"
            "# EVT masks\n"
            "water = 7292\n"
            "developed = [7296, 7297, 7298, 7299]\n"
            "excluded_evt = []\n\n"
        )
