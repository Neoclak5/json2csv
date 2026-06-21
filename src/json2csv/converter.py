"""Core JSON-to-CSV conversion logic for json2csv."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


class Json2CsvError(Exception):
    """Base exception for all json2csv errors."""


class InputFileNotFoundError(Json2CsvError):
    """Raised when the input file does not exist or is not a file."""


class InvalidJsonError(Json2CsvError):
    """Raised when the input file contains malformed JSON."""


class UnsupportedStructureError(Json2CsvError):
    """Raised when the JSON structure cannot be mapped to CSV rows."""


def _flatten(
    obj: Any,
    prefix: str = "",
    sep: str = ".",
) -> dict[str, Any]:
    """Flatten a nested mapping into a single-level dict with dot-notation keys.

    Args:
        obj: Value to flatten. Usually a dict, but may be any JSON-compatible type.
        prefix: Key prefix accumulated during recursion.
        sep: Separator inserted between nested key segments.

    Returns:
        A flat dictionary whose keys use dot-notation for nested fields.
        List values are serialised as compact JSON strings.
    """
    items: dict[str, Any] = {}
    if isinstance(obj, dict):
        for key, value in obj.items():
            new_key = f"{prefix}{sep}{key}" if prefix else key
            if isinstance(value, dict):
                items.update(_flatten(value, new_key, sep))
            elif isinstance(value, list):
                items[new_key] = json.dumps(value, ensure_ascii=False)
            else:
                items[new_key] = value
    else:
        items[prefix] = obj
    return items


def load_json(path: str | Path) -> Any:
    """Load and parse a JSON file from *path*.

    Args:
        path: Filesystem path to the JSON input file.

    Returns:
        The deserialised JSON value (list, dict, or primitive).

    Raises:
        InputFileNotFoundError: If *path* does not exist or is a directory.
        InvalidJsonError: If the file content is not valid JSON.
        Json2CsvError: If the file cannot be opened due to a permission error.
    """
    resolved = Path(path)
    if not resolved.exists():
        raise InputFileNotFoundError(f"Input file not found: {resolved}")
    if not resolved.is_file():
        raise InputFileNotFoundError(f"Path is not a file: {resolved}")
    try:
        with resolved.open(encoding="utf-8") as fh:
            return json.load(fh)
    except json.JSONDecodeError as exc:
        raise InvalidJsonError(
            f"Invalid JSON in '{resolved}': {exc}"
        ) from exc
    except PermissionError as exc:
        raise Json2CsvError(
            f"Cannot read file '{resolved}': {exc}"
        ) from exc


def normalize_records(data: Any) -> list[dict[str, Any]]:
    """Normalise JSON data into a list of flat dictionaries.

    Args:
        data: Parsed JSON value — either a list of objects or a single object.

    Returns:
        A list of flat dicts, each representing one CSV row.

    Raises:
        UnsupportedStructureError: If *data* is an empty array, an array
            whose elements are not all objects, or a type other than list
            or dict.
    """
    if isinstance(data, list):
        if not data:
            raise UnsupportedStructureError(
                "JSON array is empty — there is nothing to convert."
            )
        if not all(isinstance(item, dict) for item in data):
            raise UnsupportedStructureError(
                "JSON array must contain only objects (dictionaries)."
            )
        return [_flatten(item) for item in data]
    if isinstance(data, dict):
        return [_flatten(data)]
    raise UnsupportedStructureError(
        f"Unsupported JSON root type: '{type(data).__name__}'. "
        "Expected an array of objects or a single object."
    )


def write_csv(records: list[dict[str, Any]], path: str | Path) -> int:
    """Write *records* to a CSV file at *path*.

    The header is derived from the union of all keys found across every
    record, in order of first appearance.  Missing values in a given row
    are written as empty strings.

    Args:
        records: Non-empty list of flat dicts to serialise.
        path: Destination path for the CSV output.

    Returns:
        The number of data rows written (excluding the header).

    Raises:
        Json2CsvError: If the destination file cannot be created or written.
    """
    dest = Path(path)
    dest.parent.mkdir(parents=True, exist_ok=True)

    fieldnames: list[str] = []
    seen: set[str] = set()
    for record in records:
        for key in record:
            if key not in seen:
                seen.add(key)
                fieldnames.append(key)

    try:
        with dest.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(
                fh,
                fieldnames=fieldnames,
                extrasaction="ignore",
                restval="",
            )
            writer.writeheader()
            writer.writerows(records)
    except PermissionError as exc:
        raise Json2CsvError(f"Cannot write to '{dest}': {exc}") from exc

    return len(records)


def convert(input_path: str | Path, output_path: str | Path) -> int:
    """Convert a JSON file to a CSV file.

    This is the primary public entry-point for programmatic usage.

    Args:
        input_path: Path to the source JSON file.
        output_path: Path where the CSV output will be written.

    Returns:
        The number of rows written to the CSV (excluding the header).

    Raises:
        InputFileNotFoundError: If *input_path* does not exist.
        InvalidJsonError: If *input_path* contains malformed JSON.
        UnsupportedStructureError: If the JSON cannot be mapped to CSV rows.
        Json2CsvError: For any other I/O error during reading or writing.
    """
    data = load_json(input_path)
    records = normalize_records(data)
    return write_csv(records, output_path)
