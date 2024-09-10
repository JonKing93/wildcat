from pathlib import Path

import pytest

from wildcat._utils._find import _main


@pytest.fixture
def config(raster, vector):
    raster = Path(raster.name)
    vector = Path(vector.name)
    return {
        # Input datasets
        "perimeter": vector,
        "dem": raster,
        "dnbr": raster,
        "severity": raster,
        "kf": vector,
        "kf_fill": False,
        "evt": raster,
        "retainments": vector,
        "excluded": vector,
        "included": vector,
        "iswater": vector,
        "isdeveloped": vector,
        # Preprocessed rasters
        "perimeter_p": raster,
        "dem_p": raster,
        "dnbr_p": raster,
        "severity_p": raster,
        "kf_p": raster,
        "retainments_p": raster,
        "excluded_p": raster,
        "included_p": raster,
        "iswater_p": raster,
        "isdeveloped_p": raster,
    }


@pytest.fixture
def folder(raster):
    return raster.parent


class TestIOFolders:
    def test(_, inputs, outputs, logcheck):
        config = {
            "project": inputs.parent,
            "inputs": Path(inputs.name),
            "preprocessed": Path(outputs.name),
        }
        out1, out2 = _main.io_folders(config, "inputs", "preprocessed", logcheck.log)
        assert out1 == inputs
        assert out2 == outputs
        logcheck.check(
            [
                ("INFO", "Locating IO folders"),
                ("DEBUG", f"    inputs: {inputs}"),
                ("DEBUG", f"    preprocessed: {outputs}"),
            ]
        )


class TestPaths:
    def test_basic(_, vector, raster, folder, logcheck):
        paths = {
            "perimeter": Path(vector.name),
            "dem": Path(raster.name),
        }
        paths = _main._resolved_paths(
            paths, folder, [], ["perimeter"], logcheck.log, "test files"
        )
        assert paths == {
            "perimeter": vector,
            "dem": raster,
        }
        logcheck.check(
            [
                ("INFO", "Locating test files"),
                ("DEBUG", f"    perimeter:  {vector}"),
                ("DEBUG", f"    dem:        {raster}"),
            ]
        )

    def test_missing_required(_, folder, errcheck, logcheck):
        paths = {"kf": Path("missing")}
        with pytest.raises(FileNotFoundError) as error:
            _main._resolved_paths(paths, folder, ["kf"], [], logcheck.log, "test title")
        errcheck(error, f"Could not locate the kf file")

    def test_missing_optional(_, folder, logcheck):
        paths = {"kf": Path("kf")}
        paths = _main._resolved_paths(paths, folder, [], [], logcheck.log, "test files")
        assert paths == {"kf": None}
        logcheck.check(
            [
                ("INFO", "Locating test files"),
                ("DEBUG", f"    kf:  None"),
            ]
        )

    def test_missing_altered(_, folder, errcheck, logcheck):
        paths = {"kf": Path("missing")}
        with pytest.raises(FileNotFoundError) as error:
            _main._resolved_paths(paths, folder, [], [], logcheck.log, "test files")
        errcheck(error, "Could not locate the kf file")

    def test_features_are_raster(_, folder, raster, logcheck):
        paths = {"kf": Path(raster.stem)}
        paths = _main._resolved_paths(
            paths, folder, ["kf"], ["kf"], logcheck.log, "test files"
        )
        assert paths == {"kf": raster}
        logcheck.check(
            [
                ("INFO", "Locating test files"),
                ("DEBUG", f"    kf:  {raster}"),
            ]
        )


class TestInputs:
    def test_standard(_, config, folder, raster, vector, logcheck):
        paths = _main.inputs(config, folder, logcheck.log)
        assert paths == {
            "perimeter": vector,
            "dem": raster,
            "dnbr": raster,
            "severity": raster,
            "kf": vector,
            "evt": raster,
            "retainments": vector,
            "excluded": vector,
            "included": vector,
            "iswater": vector,
            "isdeveloped": vector,
        }
        logcheck.check(
            [
                ("INFO", "Locating input datasets"),
                ("DEBUG", f"    perimeter:    {vector}"),
                ("DEBUG", f"    dem:          {raster}"),
                ("DEBUG", f"    dnbr:         {raster}"),
                ("DEBUG", f"    severity:     {raster}"),
                ("DEBUG", f"    kf:           {vector}"),
                ("DEBUG", f"    evt:          {raster}"),
                ("DEBUG", f"    retainments:  {vector}"),
                ("DEBUG", f"    excluded:     {vector}"),
                ("DEBUG", f"    included:     {vector}"),
                ("DEBUG", f"    iswater:      {vector}"),
                ("DEBUG", f"    isdeveloped:  {vector}"),
            ]
        )

    @pytest.mark.parametrize("missing", ("perimeter", "dem"))
    def test_missing_required(_, missing, config, folder, errcheck, logcheck):
        config[missing] = Path("missing")
        with pytest.raises(FileNotFoundError) as error:
            _main.inputs(config, folder, logcheck.log)
        errcheck(error, f"Could not locate the {missing} file")

    def test_missing_optional(_, config, folder, vector, raster, logcheck):
        for name in config:
            if name not in ["perimeter", "dem", "kf_fill"]:
                config[name] = Path(name)
        paths = _main.inputs(config, folder, logcheck.log)
        assert paths == {
            "perimeter": vector,
            "dem": raster,
            "dnbr": None,
            "severity": None,
            "kf": None,
            "evt": None,
            "retainments": None,
            "excluded": None,
            "included": None,
            "iswater": None,
            "isdeveloped": None,
        }
        logcheck.check(
            [
                ("INFO", "Locating input datasets"),
                ("DEBUG", f"    perimeter:    {vector}"),
                ("DEBUG", f"    dem:          {raster}"),
                ("DEBUG", f"    dnbr:         None"),
                ("DEBUG", f"    severity:     None"),
                ("DEBUG", f"    kf:           None"),
                ("DEBUG", f"    evt:          None"),
                ("DEBUG", f"    retainments:  None"),
                ("DEBUG", f"    excluded:     None"),
                ("DEBUG", f"    included:     None"),
                ("DEBUG", f"    iswater:      None"),
                ("DEBUG", f"    isdeveloped:  None"),
            ]
        )

    def test_missing_altered(_, config, folder, errcheck, logcheck):
        config["kf"] = Path("missing")
        with pytest.raises(FileNotFoundError) as error:
            _main.inputs(config, folder, logcheck.log)
        errcheck(error, "Could not locate the kf file")

    def test_features_are_raster(_, config, folder, raster, logcheck):
        for name in config:
            if name not in ["dem", "dnbr", "evt", "kf_fill"]:
                config[name] = Path(raster.stem)
        paths = _main.inputs(config, folder, logcheck.log)
        assert paths == {
            "perimeter": raster,
            "dem": raster,
            "dnbr": raster,
            "severity": raster,
            "kf": raster,
            "evt": raster,
            "retainments": raster,
            "excluded": raster,
            "included": raster,
            "iswater": raster,
            "isdeveloped": raster,
        }
        logcheck.check(
            [
                ("INFO", "Locating input datasets"),
                ("DEBUG", f"    perimeter:    {raster}"),
                ("DEBUG", f"    dem:          {raster}"),
                ("DEBUG", f"    dnbr:         {raster}"),
                ("DEBUG", f"    severity:     {raster}"),
                ("DEBUG", f"    kf:           {raster}"),
                ("DEBUG", f"    evt:          {raster}"),
                ("DEBUG", f"    retainments:  {raster}"),
                ("DEBUG", f"    excluded:     {raster}"),
                ("DEBUG", f"    included:     {raster}"),
                ("DEBUG", f"    iswater:      {raster}"),
                ("DEBUG", f"    isdeveloped:  {raster}"),
            ]
        )

    def test_kf_fill(_, config, folder, raster, vector, logcheck):
        config["kf_fill"] = vector
        paths = _main.inputs(config, folder, logcheck.log)
        assert paths == {
            "perimeter": vector,
            "dem": raster,
            "dnbr": raster,
            "severity": raster,
            "kf": vector,
            "evt": raster,
            "retainments": vector,
            "excluded": vector,
            "included": vector,
            "iswater": vector,
            "isdeveloped": vector,
            "kf_fill": vector,
        }
        logcheck.check(
            [
                ("INFO", "Locating input datasets"),
                ("DEBUG", f"    perimeter:    {vector}"),
                ("DEBUG", f"    dem:          {raster}"),
                ("DEBUG", f"    dnbr:         {raster}"),
                ("DEBUG", f"    severity:     {raster}"),
                ("DEBUG", f"    kf:           {vector}"),
                ("DEBUG", f"    evt:          {raster}"),
                ("DEBUG", f"    retainments:  {vector}"),
                ("DEBUG", f"    excluded:     {vector}"),
                ("DEBUG", f"    included:     {vector}"),
                ("DEBUG", f"    iswater:      {vector}"),
                ("DEBUG", f"    isdeveloped:  {vector}"),
                ("DEBUG", f"    kf_fill:      {vector}"),
            ]
        )


class TestPreprocessed:
    def test_standard(_, config, folder, raster, logcheck):
        paths = _main.preprocessed(config, folder, logcheck.log)
        assert paths == {
            "perimeter_p": raster,
            "dem_p": raster,
            "dnbr_p": raster,
            "severity_p": raster,
            "kf_p": raster,
            "retainments_p": raster,
            "excluded_p": raster,
            "included_p": raster,
            "iswater_p": raster,
            "isdeveloped_p": raster,
        }
        logcheck.check(
            [
                ("INFO", "Locating preprocessed rasters"),
                ("DEBUG", f"    perimeter_p:    {raster}"),
                ("DEBUG", f"    dem_p:          {raster}"),
                ("DEBUG", f"    dnbr_p:         {raster}"),
                ("DEBUG", f"    severity_p:     {raster}"),
                ("DEBUG", f"    kf_p:           {raster}"),
                ("DEBUG", f"    retainments_p:  {raster}"),
                ("DEBUG", f"    excluded_p:     {raster}"),
                ("DEBUG", f"    included_p:     {raster}"),
                ("DEBUG", f"    iswater_p:      {raster}"),
                ("DEBUG", f"    isdeveloped_p:  {raster}"),
            ]
        )

    @pytest.mark.parametrize(
        "missing", ("perimeter_p", "dem_p", "dnbr_p", "severity_p", "kf_p")
    )
    def test_missing_required(_, missing, config, folder, errcheck, logcheck):
        config[missing] = Path("missing")
        with pytest.raises(FileNotFoundError) as error:
            _main.preprocessed(config, folder, logcheck.log)
        errcheck(error, f"Could not locate the {missing} file")

    def test_missing_optional(_, config, folder, raster, logcheck):
        for name in ["retainments", "excluded", "included", "iswater", "isdeveloped"]:
            key = f"{name}_p"
            config[key] = Path(name)
        paths = _main.preprocessed(config, folder, logcheck.log)
        assert paths == {
            "perimeter_p": raster,
            "dem_p": raster,
            "dnbr_p": raster,
            "severity_p": raster,
            "kf_p": raster,
            "retainments_p": None,
            "excluded_p": None,
            "included_p": None,
            "iswater_p": None,
            "isdeveloped_p": None,
        }
        logcheck.check(
            [
                ("INFO", "Locating preprocessed rasters"),
                ("DEBUG", f"    perimeter_p:    {raster}"),
                ("DEBUG", f"    dem_p:          {raster}"),
                ("DEBUG", f"    dnbr_p:         {raster}"),
                ("DEBUG", f"    severity_p:     {raster}"),
                ("DEBUG", f"    kf_p:           {raster}"),
                ("DEBUG", f"    retainments_p:  None"),
                ("DEBUG", f"    excluded_p:     None"),
                ("DEBUG", f"    included_p:     None"),
                ("DEBUG", f"    iswater_p:      None"),
                ("DEBUG", f"    isdeveloped_p:  None"),
            ]
        )

    def test_missing_altered(_, config, folder, errcheck, logcheck):
        config["kf_p"] = Path("missing")
        with pytest.raises(FileNotFoundError) as error:
            _main.preprocessed(config, folder, logcheck.log)
        errcheck(error, "Could not locate the kf_p file")
