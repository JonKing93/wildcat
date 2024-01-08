"""
Common type hints used throughout the package
"""

from pathlib import Path
from typing import Sequence

Pathlike = str | Path
PathArg = Pathlike | None
scalar = int | float
vector = scalar | Sequence[scalar]
