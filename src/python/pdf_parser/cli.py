#!/usr/bin/env python3
"""
CLI interface for PDF resume parser.

Usage:
    python -m pdf_parser.cli <input.pdf> [output.md]
"""

import sys
from pathlib import Path

from .parser import PDFParseError, ResumeParser


def main() -> int:
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python -m pdf_parser.cli <input.pdf> [output.md]", file=sys.stderr)
        print("\nConvert a PDF resume to structured markdown format.", file=sys.stderr)
        return 1

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    if not output_path:
        # Generate output filename from input
        output_path = input_path.with_suffix(".md")

    try:
        parser = ResumeParser()
        result = parser.parse_pdf(input_path)
        markdown = parser.to_markdown(result["content"])

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write the markdown file
        output_path.write_text(markdown, encoding="utf-8")

        print(f"Successfully parsed resume to: {output_path}")
        return 0

    except PDFParseError as e:
        print(f"Error parsing PDF: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
