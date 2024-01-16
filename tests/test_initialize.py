from pathlib import Path

import pytest

from wildcat import initialize


class TestInitialize:
    def test_exists(_, tmp_path):
        folder = Path(tmp_path) / "test"
        folder.mkdir()
        with pytest.raises(FileExistsError) as error:
            initialize(folder)
        assert (
            "Cannot initialize the project folder because the folder already exists"
            in error.value.args[0]
        )

    def test_valid(_, tmp_path):
        folder = Path(tmp_path) / "test"
        initialize(folder)
        assert folder.exists()
        config = folder / "config.py"
        assert config.exists()

    def test_nested(_, tmp_path):
        folder = Path(tmp_path) / "test" / "test" / "test"
        initialize(folder)
        assert folder.exists()
        config = folder / "config.py"
        assert config.exists()
