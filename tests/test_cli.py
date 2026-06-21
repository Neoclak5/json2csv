"""Tests for json2csv.cli — covers all branches of main()."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from json2csv.cli import _build_parser, main


class TestBuildParser:
    """Unit tests for _build_parser."""

    def test_prog_name(self) -> None:
        """Parser prog is set to 'json2csv'."""
        assert _build_parser().prog == "json2csv"

    def test_input_and_output_args(self) -> None:
        """Parser accepts positional input and --output."""
        args = _build_parser().parse_args(["input.json", "--output", "out.csv"])
        assert args.input == "input.json"
        assert args.output == "out.csv"

    def test_short_output_flag(self) -> None:
        """Short flag -o is an alias for --output."""
        args = _build_parser().parse_args(["input.json", "-o", "out.csv"])
        assert args.output == "out.csv"


class TestMain:
    """Unit tests for main()."""

    def test_no_args_prints_help_and_exits_zero(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Calling with no arguments prints help and exits 0."""
        with patch("sys.argv", ["json2csv"]):
            with pytest.raises(SystemExit) as exc:
                main()
        assert exc.value.code == 0
        assert capsys.readouterr().out  # some output was produced

    def test_successful_conversion_prints_count(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """A valid conversion prints the number of records converted."""
        src = tmp_path / "data.json"
        dst = tmp_path / "out.csv"
        src.write_text('[{"a": 1}, {"a": 2}]', encoding="utf-8")
        with patch("sys.argv", ["json2csv", str(src), "-o", str(dst)]):
            main()
        assert "2 record" in capsys.readouterr().out

    def test_missing_file_exits_one(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """A missing input file prints an error to stderr and exits 1."""
        with patch("sys.argv", ["json2csv", str(tmp_path / "ghost.json"), "-o", "x.csv"]):
            with pytest.raises(SystemExit) as exc:
                main()
        assert exc.value.code == 1
        assert "Error" in capsys.readouterr().err

    def test_invalid_json_exits_one(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Invalid JSON prints an error to stderr and exits 1."""
        src = tmp_path / "bad.json"
        src.write_text("{bad json}", encoding="utf-8")
        with patch("sys.argv", ["json2csv", str(src), "-o", str(tmp_path / "out.csv")]):
            with pytest.raises(SystemExit) as exc:
                main()
        assert exc.value.code == 1
        assert "Error" in capsys.readouterr().err

    def test_empty_json_array_exits_one(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """An empty JSON array prints an error to stderr and exits 1."""
        src = tmp_path / "empty.json"
        src.write_text("[]", encoding="utf-8")
        with patch("sys.argv", ["json2csv", str(src), "-o", str(tmp_path / "out.csv")]):
            with pytest.raises(SystemExit) as exc:
                main()
        assert exc.value.code == 1
