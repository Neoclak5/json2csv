"""Tests for json2csv.converter — targets 85%+ branch coverage."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from unittest.mock import patch

import pytest

from json2csv.converter import (
    InputFileNotFoundError,
    InvalidJsonError,
    Json2CsvError,
    UnsupportedStructureError,
    _flatten,
    convert,
    load_json,
    normalize_records,
    write_csv,
)


# ── _flatten ───────────────────────────────────────────────────────────────

class TestFlatten:
    """Unit tests for the _flatten helper."""

    def test_flat_dict_unchanged(self) -> None:
        """A dict with no nested values comes out identical."""
        assert _flatten({"a": 1, "b": "x"}) == {"a": 1, "b": "x"}

    def test_single_level_nested(self) -> None:
        """One level of nesting produces a.b key."""
        assert _flatten({"a": {"b": 1}}) == {"a.b": 1}

    def test_deeply_nested(self) -> None:
        """Three levels of nesting produce a.b.c key."""
        assert _flatten({"a": {"b": {"c": 7}}}) == {"a.b.c": 7}

    def test_mixed_nested(self) -> None:
        """Flat and nested keys coexist correctly."""
        obj = {"a": 1, "b": {"c": 2, "d": {"e": 3}}}
        assert _flatten(obj) == {"a": 1, "b.c": 2, "b.d.e": 3}

    def test_list_value_serialised_as_json(self) -> None:
        """List values are JSON-serialised into a string."""
        result = _flatten({"items": [1, 2, 3]})
        assert result["items"] == "[1, 2, 3]"

    def test_custom_separator(self) -> None:
        """A custom separator is respected."""
        assert _flatten({"a": {"b": 1}}, sep="__") == {"a__b": 1}

    def test_with_prefix(self) -> None:
        """A prefix is prepended with the separator."""
        assert _flatten({"b": 1}, prefix="a") == {"a.b": 1}

    def test_scalar_passthrough(self) -> None:
        """A bare scalar is stored under its prefix."""
        assert _flatten(42, prefix="val") == {"val": 42}

    def test_none_value(self) -> None:
        """None values are preserved."""
        assert _flatten({"x": None}) == {"x": None}

    def test_boolean_value(self) -> None:
        """Boolean values are preserved."""
        assert _flatten({"flag": True}) == {"flag": True}


# ── load_json ──────────────────────────────────────────────────────────────

class TestLoadJson:
    """Unit tests for load_json."""

    def test_loads_array(self, tmp_path: Path) -> None:
        """A JSON array is parsed and returned."""
        f = tmp_path / "d.json"
        f.write_text('[{"a": 1}]', encoding="utf-8")
        assert load_json(f) == [{"a": 1}]

    def test_loads_object(self, tmp_path: Path) -> None:
        """A JSON object is parsed and returned."""
        f = tmp_path / "d.json"
        f.write_text('{"x": 2}', encoding="utf-8")
        assert load_json(f) == {"x": 2}

    def test_accepts_string_path(self, tmp_path: Path) -> None:
        """A string path is accepted in addition to Path objects."""
        f = tmp_path / "d.json"
        f.write_text('[{"a": 1}]', encoding="utf-8")
        assert load_json(str(f)) == [{"a": 1}]

    def test_missing_file_raises(self, tmp_path: Path) -> None:
        """InputFileNotFoundError is raised for a non-existent path."""
        with pytest.raises(InputFileNotFoundError):
            load_json(tmp_path / "nope.json")

    def test_directory_path_raises(self, tmp_path: Path) -> None:
        """InputFileNotFoundError is raised when path is a directory."""
        with pytest.raises(InputFileNotFoundError):
            load_json(tmp_path)

    def test_invalid_json_raises(self, tmp_path: Path) -> None:
        """InvalidJsonError is raised for malformed JSON."""
        f = tmp_path / "bad.json"
        f.write_text("{ not json }", encoding="utf-8")
        with pytest.raises(InvalidJsonError):
            load_json(f)

    def test_empty_file_raises(self, tmp_path: Path) -> None:
        """InvalidJsonError is raised for an empty file."""
        f = tmp_path / "empty.json"
        f.write_text("", encoding="utf-8")
        with pytest.raises(InvalidJsonError):
            load_json(f)

    def test_permission_error_raises(self, tmp_path: Path) -> None:
        """Json2CsvError is raised when the file cannot be opened."""
        f = tmp_path / "d.json"
        f.write_text('[{"a": 1}]', encoding="utf-8")
        with patch.object(Path, "open", side_effect=PermissionError("denied")):
            with pytest.raises(Json2CsvError, match="Cannot read"):
                load_json(f)


# ── normalize_records ──────────────────────────────────────────────────────

class TestNormalizeRecords:
    """Unit tests for normalize_records."""

    def test_list_of_dicts(self) -> None:
        """A list of dicts is returned as-is (after flattening)."""
        result = normalize_records([{"a": 1}, {"a": 2}])
        assert result == [{"a": 1}, {"a": 2}]

    def test_single_dict_wrapped(self) -> None:
        """A single dict is wrapped in a one-element list."""
        assert normalize_records({"a": 1}) == [{"a": 1}]

    def test_empty_list_raises(self) -> None:
        """UnsupportedStructureError is raised for an empty array."""
        with pytest.raises(UnsupportedStructureError, match="empty"):
            normalize_records([])

    def test_list_with_non_dicts_raises(self) -> None:
        """UnsupportedStructureError is raised when array elements are not objects."""
        with pytest.raises(UnsupportedStructureError):
            normalize_records([1, 2, 3])

    def test_string_raises(self) -> None:
        """UnsupportedStructureError is raised for a JSON string root."""
        with pytest.raises(UnsupportedStructureError):
            normalize_records("hello")

    def test_integer_raises(self) -> None:
        """UnsupportedStructureError is raised for a JSON integer root."""
        with pytest.raises(UnsupportedStructureError):
            normalize_records(123)

    def test_none_raises(self) -> None:
        """UnsupportedStructureError is raised for a JSON null root."""
        with pytest.raises(UnsupportedStructureError):
            normalize_records(None)

    def test_nested_dicts_flattened(self) -> None:
        """Nested dicts inside list elements are flattened."""
        result = normalize_records([{"user": {"name": "Ana"}}])
        assert result == [{"user.name": "Ana"}]


# ── write_csv ──────────────────────────────────────────────────────────────

class TestWriteCsv:
    """Unit tests for write_csv."""

    def test_writes_header_and_row(self, tmp_path: Path) -> None:
        """A single record produces a header and one data row."""
        out = tmp_path / "out.csv"
        n = write_csv([{"a": 1, "b": 2}], out)
        assert n == 1
        rows = list(csv.DictReader(out.open(encoding="utf-8")))
        assert rows == [{"a": "1", "b": "2"}]

    def test_returns_row_count(self, tmp_path: Path) -> None:
        """Return value equals the number of records written."""
        out = tmp_path / "out.csv"
        assert write_csv([{"x": i} for i in range(10)], out) == 10

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Missing parent directories are created automatically."""
        out = tmp_path / "a" / "b" / "c.csv"
        write_csv([{"k": "v"}], out)
        assert out.exists()

    def test_inconsistent_keys_fills_blanks(self, tmp_path: Path) -> None:
        """Missing keys in a row are written as empty strings."""
        out = tmp_path / "out.csv"
        write_csv([{"a": 1, "b": 2}, {"a": 3}], out)
        rows = list(csv.DictReader(out.open(encoding="utf-8")))
        assert rows[1]["b"] == ""

    def test_unicode_content(self, tmp_path: Path) -> None:
        """Unicode values round-trip through the CSV correctly."""
        out = tmp_path / "out.csv"
        write_csv([{"nombre": "José", "ciudad": "Córdoba"}], out)
        rows = list(csv.DictReader(out.open(encoding="utf-8")))
        assert rows[0]["nombre"] == "José"

    def test_accepts_string_path(self, tmp_path: Path) -> None:
        """A string path is accepted in addition to Path objects."""
        out = tmp_path / "out.csv"
        write_csv([{"a": 1}], str(out))
        assert out.exists()

    def test_permission_error_raises(self, tmp_path: Path) -> None:
        """Json2CsvError is raised when the destination cannot be written."""
        out = tmp_path / "out.csv"
        with patch.object(Path, "open", side_effect=PermissionError("denied")):
            with pytest.raises(Json2CsvError, match="Cannot write"):
                write_csv([{"a": 1}], out)


# ── convert (integration) ──────────────────────────────────────────────────

class TestConvert:
    """Integration tests for convert (load → normalise → write)."""

    def test_simple_array(self, tmp_path: Path) -> None:
        """A flat JSON array produces one CSV row per element."""
        src = tmp_path / "in.json"
        dst = tmp_path / "out.csv"
        src.write_text('[{"name": "Alice", "age": 30}]', encoding="utf-8")
        assert convert(src, dst) == 1
        rows = list(csv.DictReader(dst.open(encoding="utf-8")))
        assert rows[0]["name"] == "Alice"
        assert rows[0]["age"] == "30"

    def test_multiple_records(self, tmp_path: Path) -> None:
        """All records in a large array are written."""
        data = [{"id": i, "val": i * 2} for i in range(20)]
        src = tmp_path / "in.json"
        src.write_text(json.dumps(data), encoding="utf-8")
        assert convert(src, tmp_path / "out.csv") == 20

    def test_single_object(self, tmp_path: Path) -> None:
        """A single JSON object produces exactly one CSV row."""
        src = tmp_path / "in.json"
        src.write_text('{"k": "v"}', encoding="utf-8")
        assert convert(src, tmp_path / "out.csv") == 1

    def test_nested_json(self, tmp_path: Path) -> None:
        """Nested fields are flattened with dot-notation headers."""
        src = tmp_path / "in.json"
        src.write_text('[{"u": {"n": "Bob", "a": 25}}]', encoding="utf-8")
        dst = tmp_path / "out.csv"
        convert(src, dst)
        rows = list(csv.DictReader(dst.open(encoding="utf-8")))
        assert rows[0]["u.n"] == "Bob"

    def test_list_value_in_record(self, tmp_path: Path) -> None:
        """Array-valued fields are JSON-serialised into a single CSV cell."""
        src = tmp_path / "in.json"
        src.write_text('[{"tags": ["a", "b"]}]', encoding="utf-8")
        dst = tmp_path / "out.csv"
        convert(src, dst)
        rows = list(csv.DictReader(dst.open(encoding="utf-8")))
        assert rows[0]["tags"] == '["a", "b"]'

    def test_missing_input_raises(self, tmp_path: Path) -> None:
        """InputFileNotFoundError is propagated from load_json."""
        with pytest.raises(InputFileNotFoundError):
            convert(tmp_path / "missing.json", tmp_path / "out.csv")

    def test_invalid_json_raises(self, tmp_path: Path) -> None:
        """InvalidJsonError is propagated from load_json."""
        src = tmp_path / "bad.json"
        src.write_text("{bad}", encoding="utf-8")
        with pytest.raises(InvalidJsonError):
            convert(src, tmp_path / "out.csv")

    def test_empty_array_raises(self, tmp_path: Path) -> None:
        """UnsupportedStructureError is propagated from normalize_records."""
        src = tmp_path / "empty.json"
        src.write_text("[]", encoding="utf-8")
        with pytest.raises(UnsupportedStructureError):
            convert(src, tmp_path / "out.csv")

    def test_string_paths_accepted(self, tmp_path: Path) -> None:
        """String paths work end-to-end."""
        src = tmp_path / "in.json"
        src.write_text('[{"x": 1}]', encoding="utf-8")
        assert convert(str(src), str(tmp_path / "out.csv")) == 1
