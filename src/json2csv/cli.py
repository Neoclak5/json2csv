"""Command-line interface for json2csv."""

from __future__ import annotations

import argparse
import sys

from json2csv.converter import Json2CsvError, convert


def _build_parser() -> argparse.ArgumentParser:
    """Build and return the CLI argument parser.

    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        prog="json2csv",
        description="Convert a JSON file to CSV format.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "examples:\n"
            "  json2csv data.json --output data.csv\n"
            "  json2csv records.json -o output/results.csv\n"
        ),
    )
    parser.add_argument("input", help="Path to the input JSON file.")
    parser.add_argument(
        "--output",
        "-o",
        required=True,
        metavar="FILE",
        help="Path to the output CSV file.",
    )
    return parser


def main() -> None:
    """Entry point for the json2csv command-line tool."""
    parser = _build_parser()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    try:
        rows = convert(args.input, args.output)
        print(f"Converted {rows} record(s)  ->  {args.output}")
    except Json2CsvError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
