"""
Default values used for hazard assessments
----------
This module defines a variety of constants used to implement hazard assessments.
This ensures that defaults are consistent across:
    * CLI help text,
    * CLI commands, and
    * Commands run from the Python interpreter
"""

from wildcat.utils.typing import scalar, vector

buffer: scalar = 2000  # Fire perimeter buffer in the units of the CRS (usually meters)
dnbr_min: scalar = -1000  # Minimum valid dNBR value
dnbr_max: scalar = 1000  # Maximum valid dNBR value
water: vector = [7292]  # EVT values recognized as water
developed: vector = range(7296, 7300 + 1)  # EVT values recognized as developed
