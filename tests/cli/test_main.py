from pathlib import Path

from wildcat.cli import main


def test(tmp_path):
    "Runs the init subcommand to ensure that the main parser builds succesfully"
    "and properly calls a subcommand hook"

    folder = Path(tmp_path) / "test"
    assert not folder.exists()
    main.main(["init", str(folder)])
    assert folder.exists()
