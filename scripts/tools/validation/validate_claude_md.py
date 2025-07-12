#!/usr/bin/env python3
"""
CLAUDE.md Validation & Integrity Check Script
===========================================

Gemini-recommended safety improvement for modular AI instruction architecture.
Validates all @import paths, checks dependencies, ensures critical modules exist.

Usage:
    python scripts/validate_claude_md.py

Features:
    - @import path validation
    - Circular dependency detection
    - Critical module presence check
    - Pre-commit hook compatible
"""

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Set, Tuple


@dataclass
class ValidationResult:
    """Validation result with detailed findings"""

    is_valid: bool
    errors: List[str]
    warnings: List[str]
    module_count: int
    total_lines: int


class CLAUDEMdValidator:
    """Comprehensive CLAUDE.md validation system"""

    # Critical modules that must always exist (relative to base_path)
    CRITICAL_MODULES = {
        "claude_modules/system/ai_safety_governance.md",
        "claude_modules/core/emergency_procedures.md",
        "claude_modules/core/session_initialization.md",
        "claude_modules/system/knowledge_management.md",
    }

    def __init__(self, base_path: Path = None):
        self.base_path = base_path or Path.cwd()
        self.processed_files: Set[Path] = set()
        self.import_stack: List[Path] = []
        self.dependency_graph: Dict[Path, List[Path]] = {}

    def validate_file(self, file_path: Path) -> ValidationResult:
        """
        Comprehensive validation of CLAUDE.md and all imports

        Returns:
            ValidationResult with detailed findings
        """
        errors = []
        warnings = []
        module_count = 0
        total_lines = 0

        try:
            # Check main file existence
            if not file_path.exists():
                errors.append(f"Main file not found: {file_path}")
                return ValidationResult(False, errors, warnings, 0, 0)

            # Parse and validate recursively
            try:
                content, modules_found = self._validate_recursive(file_path)
                module_count = len(modules_found)
                total_lines = len(content.splitlines())

            except Exception as e:
                errors.append(f"Parsing error: {e}")
                return ValidationResult(False, errors, warnings, 0, 0)

            # Check critical modules (convert to relative paths for comparison)
            modules_relative = set()
            for m in modules_found:
                try:
                    rel_path = str(m.relative_to(self.base_path))
                    modules_relative.add(rel_path)
                except ValueError:
                    # Path is not relative to base_path, skip
                    pass

            missing_critical = self.CRITICAL_MODULES - modules_relative
            if missing_critical:
                errors.extend(
                    [f"Critical module missing: {m}" for m in missing_critical]
                )

            # Check for circular dependencies
            circular_deps = self._detect_circular_dependencies()
            if circular_deps:
                errors.extend(
                    [
                        f"Circular dependency: {' -> '.join(str(p) for p in cycle)}"
                        for cycle in circular_deps
                    ]
                )

            # Validate module versions (if present)
            version_warnings = self._check_module_versions(modules_found)
            warnings.extend(version_warnings)

            # Size validation
            if total_lines < 50:
                warnings.append(f"Unexpectedly small total size: {total_lines} lines")
            elif total_lines > 1000:
                warnings.append(f"Very large total size: {total_lines} lines")

            is_valid = len(errors) == 0

        except Exception as e:
            errors.append(f"Validation failed: {e}")
            is_valid = False

        return ValidationResult(is_valid, errors, warnings, module_count, total_lines)

    def _validate_recursive(
        self, file_path: Path, level: int = 0
    ) -> Tuple[str, Set[Path]]:
        """Recursively validate file and all imports"""

        # Prevent infinite recursion
        if level > 10:
            raise ValueError(f"Import depth too deep (>10): {file_path}")

        abs_path = file_path.resolve()

        # Check for circular imports
        if abs_path in self.import_stack:
            raise ValueError(
                f"Circular import: {' -> '.join(str(p) for p in self.import_stack)} -> {abs_path}"
            )

        self.import_stack.append(abs_path)
        modules_found = set()

        try:
            content = abs_path.read_text(encoding="utf-8")

            # Find all @import statements
            import_pattern = r"^@import\s+(.+?)(?:\s*$)"
            imports = []

            for line_num, line in enumerate(content.splitlines(), 1):
                match = re.match(import_pattern, line.strip())
                if match:
                    import_path_str = match.group(1).strip()
                    imports.append((line_num, import_path_str))

            # Validate each import
            for line_num, import_path_str in imports:
                # Resolve import path
                if import_path_str.startswith("/"):
                    import_path = self.base_path / import_path_str.lstrip("/")
                else:
                    import_path = abs_path.parent / import_path_str

                # Add common extensions
                if not import_path.suffix:
                    if (import_path.with_suffix(".md")).exists():
                        import_path = import_path.with_suffix(".md")
                    elif (import_path.with_suffix(".txt")).exists():
                        import_path = import_path.with_suffix(".txt")

                # Check file exists
                if not import_path.exists():
                    raise ValueError(
                        f"Import not found at line {line_num}: {import_path}"
                    )

                # Record dependency
                if abs_path not in self.dependency_graph:
                    self.dependency_graph[abs_path] = []
                self.dependency_graph[abs_path].append(import_path)

                # Add to modules found
                modules_found.add(import_path)

                # Recursively validate
                _, nested_modules = self._validate_recursive(import_path, level + 1)
                modules_found.update(nested_modules)

            self.processed_files.add(abs_path)
            return content, modules_found

        finally:
            self.import_stack.pop()

    def _detect_circular_dependencies(self) -> List[List[Path]]:
        """Detect circular dependencies in the import graph"""
        circular_deps = []
        visited = set()
        rec_stack = set()

        def dfs(node: Path, path: List[Path]) -> bool:
            visited.add(node)
            rec_stack.add(node)

            for neighbor in self.dependency_graph.get(node, []):
                if neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    circular_deps.append(path[cycle_start:] + [neighbor])
                    return True
                elif neighbor not in visited:
                    if dfs(neighbor, path + [neighbor]):
                        return True

            rec_stack.remove(node)
            return False

        for node in self.dependency_graph:
            if node not in visited:
                dfs(node, [node])

        return circular_deps

    def _check_module_versions(self, modules: Set[Path]) -> List[str]:
        """Check for version information in modules"""
        warnings = []

        for module_path in modules:
            try:
                content = module_path.read_text(encoding="utf-8")
                # Look for version comments
                if not re.search(r"#.*version:", content, re.IGNORECASE):
                    warnings.append(f"No version info in module: {module_path}")
            except Exception:
                warnings.append(
                    f"Could not read module for version check: {module_path}"
                )

        return warnings


def main():
    """Main validation function"""

    # Determine CLAUDE.md path
    claude_md_path = Path("CLAUDE.md")
    if not claude_md_path.exists():
        claude_md_path = Path("claude.md")
    if not claude_md_path.exists():
        print("❌ CLAUDE.md not found in current directory", file=sys.stderr)
        sys.exit(1)

    # Run validation
    validator = CLAUDEMdValidator()
    result = validator.validate_file(claude_md_path)

    # Report results
    print("🔍 CLAUDE.md Validation Report")
    print("=" * 40)

    if result.is_valid:
        print("✅ VALIDATION PASSED")
    else:
        print("❌ VALIDATION FAILED")

    print("📊 Statistics:")
    print(f"   Modules processed: {result.module_count}")
    print(f"   Total lines: {result.total_lines:,}")

    if result.errors:
        print(f"\n🚨 Errors ({len(result.errors)}):")
        for error in result.errors:
            print(f"   ❌ {error}")

    if result.warnings:
        print(f"\n⚠️  Warnings ({len(result.warnings)}):")
        for warning in result.warnings:
            print(f"   ⚠️  {warning}")

    if result.is_valid and not result.warnings:
        print("\n🎉 CLAUDE.md architecture is healthy and well-structured!")

    # Exit with appropriate code
    sys.exit(0 if result.is_valid else 1)


if __name__ == "__main__":
    main()
