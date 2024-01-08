from typing import Optional, Sequence

from wildcat.cli import parsers

strs = Sequence[str]


def main(args: Optional[strs] = None):
    parser = parsers.main()
    args = parser.parse_args(args)
    args.run(args)
