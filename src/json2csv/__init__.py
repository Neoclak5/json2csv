"""json2csv — Convert JSON files to CSV format.

Programmatic usage::

    from json2csv import convert
    rows = convert("data.json", "data.csv")
"""

from __future__ import annotations

from json2csv.converter import (
    InputFileNotFoundError,
    InvalidJsonError,
    Json2CsvError,
    UnsupportedStructureError,
    convert,
)

__version__ = "0.1.0"

__all__ = [
    "convert",
    "Json2CsvError",
    "InputFileNotFoundError",
    "InvalidJsonError",
    "UnsupportedStructureError",
]
