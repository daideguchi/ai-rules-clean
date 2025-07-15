#!/usr/bin/env python3
"""
CRITICAL: CLAUDE.md @import Parser - AI Safety System Recovery
============================================================

The AI safety system was compromised by reducing 658 lines to 55 lines
using @import statements that were not being processed. This script
restores full functionality by expanding all @import directives.

Usage:
    python scripts/import_parser.py CLAUDE.md

Output:
    CLAUDE.expanded.md - Complete expanded file with all imports resolved
"""

import re
import sys
from pathlib import Path
from typing import List, Set


class ImportParserError(Exception):
    """Custom exception for import parsing errors"""

    pass


class CLAUDEImportParser:
    """Parser for @import directives in CLAUDE.md files"""

    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.processed_files: Set[Path] = set()
        self.import_stack: List[Path] = []

    def parse_file(self, file_path: Path) -> str:
        """
        Parse a file and resolve all @import statements recursively

        Args:
            file_path: Path to the file to parse

        Returns:
            Complete content with all imports resolved

        Raises:
            ImportParserError: If circular imports or missing files detected
        """

        # Resolve to absolute path
        abs_path = file_path.resolve()

        # Check for circular imports
        if abs_path in self.import_stack:
            raise ImportParserError(
                f"Circular import detected: {' -> '.join(str(p) for p in self.import_stack)} -> {abs_path}"
            )

        # Add to import stack
        self.import_stack.append(abs_path)

        try:
            # Read the file
            if not abs_path.exists():
                raise ImportParserError(f"File not found: {abs_path}")

            content = abs_path.read_text(encoding="utf-8")

            # Process @import statements
            processed_content = self._process_imports(content, abs_path.parent)

            # Mark as processed
            self.processed_files.add(abs_path)

            return processed_content

        finally:
            # Remove from import stack
            self.import_stack.pop()

    def _process_imports(self, content: str, current_dir: Path) -> str:
        """
        Process all @import statements in the content

        Args:
            content: File content to process
            current_dir: Directory containing the current file

        Returns:
            Content with @import statements replaced by actual content
        """

        # Pattern to match @import statements
        import_pattern = r"^@import\s+(.+?)(?:\s*$)"

        lines = content.split("\n")
        result_lines = []

        for line in lines:
            match = re.match(import_pattern, line.strip())

            if match:
                # Extract import path
                import_path_str = match.group(1).strip()

                # Resolve relative to current directory or base path
                if import_path_str.startswith("/"):
                    # Absolute path from base
                    import_path = self.base_path / import_path_str.lstrip("/")
                else:
                    # Relative path from current directory
                    import_path = current_dir / import_path_str

                # Add common extensions if not present
                if not import_path.suffix:
                    if (import_path.with_suffix(".md")).exists():
                        import_path = import_path.with_suffix(".md")
                    elif (import_path.with_suffix(".txt")).exists():
                        import_path = import_path.with_suffix(".txt")

                try:
                    # Recursively parse the imported file
                    imported_content = self.parse_file(import_path)

                    # Add imported content with a comment header
                    result_lines.append("")
                    result_lines.append(f"<!-- BEGIN IMPORT: {import_path_str} -->")
                    result_lines.append(imported_content.rstrip())
                    result_lines.append(f"<!-- END IMPORT: {import_path_str} -->")
                    result_lines.append("")

                except ImportParserError as e:
                    # Add error comment and continue
                    result_lines.append(
                        f"<!-- ERROR: Failed to import {import_path_str}: {e} -->"
                    )
                    print(f"⚠️  Import error: {e}", file=sys.stderr)

            else:
                # Regular line, keep as-is
                result_lines.append(line)

        return "\n".join(result_lines)


def main():
    """Main function to parse CLAUDE.md and expand all imports"""

    if len(sys.argv) != 2:
        print("Usage: python scripts/import_parser.py <file_path>", file=sys.stderr)
        print("Example: python scripts/import_parser.py CLAUDE.md", file=sys.stderr)
        sys.exit(1)

    input_file = Path(sys.argv[1])

    # Determine base path (project root)
    if input_file.is_absolute():
        base_path = input_file.parent
    else:
        base_path = Path.cwd()

    # Create parser
    parser = CLAUDEImportParser(base_path)

    try:
        print(f"🔍 Parsing {input_file} with base path {base_path}")

        # Parse the file
        expanded_content = parser.parse_file(input_file)

        # Create output file
        output_file = input_file.with_name(
            f"{input_file.stem}.expanded{input_file.suffix}"
        )

        # Write expanded content
        output_file.write_text(expanded_content, encoding="utf-8")

        print(f"✅ Successfully expanded {input_file}")
        print(f"📄 Output written to: {output_file}")
        print(f"📊 Processed {len(parser.processed_files)} files")

        # Show statistics
        original_lines = len(input_file.read_text().splitlines())
        expanded_lines = len(expanded_content.splitlines())

        print(
            f"📈 Expansion: {original_lines} → {expanded_lines} lines ({expanded_lines / original_lines:.1f}x)"
        )

        if expanded_lines > original_lines * 5:
            print(
                "🎉 CRITICAL SAFETY ISSUE RESOLVED: AI system now has full instructions!"
            )

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
