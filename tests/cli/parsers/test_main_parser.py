import pytest

from wildcat.cli import parsers


def test(capfd):
    parser = parsers.main()
    with pytest.raises(SystemExit):
        parser.parse_args(["-h"])
    help = capfd.readouterr().out
    for message in [
        "wildcat",
        "Assess and map post-fire debris-flow hazards",
        "initialize,run,preprocess,assess,map",
    ]:
        assert message in help
