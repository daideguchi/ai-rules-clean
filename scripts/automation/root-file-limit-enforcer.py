#!/usr/bin/env python3
"""
🚨 Root File Limit Enforcer - Real-time 12-File Limit Enforcement
==============================================================

Real-time monitoring and enforcement of the 12-file root directory limit.
Automatically prevents violations and maintains clean project structure.

【Core Features】
- Real-time directory monitoring
- Automatic file organization
- Violation prevention
- Production mode enforcement
- Clean project structure maintenance

【Implementation】
- File system monitoring using watchdog
- Automatic file categorization and movement
- Violation alerts and corrections
- Integration with existing hook system
"""

import json
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

try:
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer
except ImportError:
    print("Installing required dependencies...")
    subprocess.run(["pip", "install", "watchdog"], check=True)
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer


@dataclass
class FileCategory:
    """File categorization result"""

    category: str
    target_directory: str
    essential: bool
    description: str


class RootFileLimitEnforcer:
    """Real-time root file limit enforcement system"""

    MAX_ROOT_FILES = 12
    ESSENTIAL_FILES = {
        "CLAUDE.md",
        "README.md",
        "Makefile",
        "LICENSE",
        ".gitignore",
        ".gitattributes",
        "pyproject.toml",
        ".pre-commit-config.yaml",
        ".claude-project",
        ".cursorrules",
        ".env.example",
        "CHANGELOG.md",
    }

    FILE_CATEGORIES = {
        # Reports and documentation
        r".*_REPORT\.md$": FileCategory(
            "report", "docs/04_reference/", False, "Status reports"
        ),
        r".*_CONSOLIDATION.*\.md$": FileCategory(
            "report", "docs/04_reference/", False, "Consolidation reports"
        ),
        r"SETUP_.*\.md$": FileCategory(
            "guide", "docs/02_guides/", False, "Setup guides"
        ),
        r"Index\.md$": FileCategory(
            "guide", "docs/02_guides/", False, "Index documentation"
        ),
        # Docker files
        r"Dockerfile.*": FileCategory(
            "docker", "config/docker/", False, "Docker configuration"
        ),
        r"docker-compose.*\.yml$": FileCategory(
            "docker", "config/docker/", False, "Docker compose"
        ),
        # Python files
        r".*_ui_system\.py$": FileCategory("ui", "src/ui/", False, "UI system files"),
        r"demo_.*\.py$": FileCategory("ui", "src/ui/", False, "Demo files"),
        r"test_.*\.py$": FileCategory("ui", "src/ui/", False, "Test files"),
        # Requirements
        r"requirements-.*\.txt$": FileCategory(
            "config", "config/", False, "Requirements files"
        ),
        # Cursor config
        r"\.cursor.*": FileCategory(
            "config", "config/cursor/", False, "Cursor configuration"
        ),
        r"\.forbidden-.*": FileCategory(
            "config", "config/cursor/", False, "Forbidden file config"
        ),
    }

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path.cwd()
        self.runtime_dir = self.project_root / "runtime" / "file_monitoring"
        self.runtime_dir.mkdir(parents=True, exist_ok=True)

        self.log_file = self.runtime_dir / "enforcement.log"
        self.violations_file = self.runtime_dir / "violations.json"
        self.status_file = self.runtime_dir / "status.json"

        self.observer = None
        self.violations = []

        # Initialize directories
        self._ensure_target_directories()

    def _ensure_target_directories(self):
        """Ensure all target directories exist"""
        directories = [
            "docs/04_reference",
            "docs/02_guides",
            "config/docker",
            "config/cursor",
            "config",
            "src/ui",
        ]

        for dir_path in directories:
            full_path = self.project_root / dir_path
            full_path.mkdir(parents=True, exist_ok=True)

    def _log(self, message: str, level: str = "INFO"):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"

        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")

        print(log_entry)

    def _get_current_root_files(self) -> List[Path]:
        """Get current files in root directory"""
        try:
            return [f for f in self.project_root.iterdir() if f.is_file()]
        except Exception as e:
            self._log(f"Error getting root files: {e}", "ERROR")
            return []

    def _categorize_file(self, file_path: Path) -> FileCategory:
        """Categorize a file to determine its proper location"""
        import re

        filename = file_path.name

        # Check if it's an essential file
        if filename in self.ESSENTIAL_FILES:
            return FileCategory("essential", "", True, "Essential root file")

        # Check against patterns
        for pattern, category in self.FILE_CATEGORIES.items():
            if re.match(pattern, filename):
                return category

        # Default category for unknown files
        return FileCategory("unknown", "misc/", False, "Unknown file type")

    def _move_file(self, file_path: Path, target_dir: str) -> bool:
        """Move file to target directory"""
        try:
            target_path = self.project_root / target_dir
            target_path.mkdir(parents=True, exist_ok=True)

            destination = target_path / file_path.name

            # Avoid overwriting existing files
            if destination.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                stem = destination.stem
                suffix = destination.suffix
                destination = target_path / f"{stem}_{timestamp}{suffix}"

            file_path.rename(destination)
            self._log(f"Moved {file_path.name} to {target_dir}")
            return True

        except Exception as e:
            self._log(f"Error moving {file_path.name}: {e}", "ERROR")
            return False

    def check_and_enforce_limit(self) -> Dict[str, any]:
        """Check current file count and enforce limit"""
        root_files = self._get_current_root_files()
        file_count = len(root_files)

        result = {
            "timestamp": datetime.now().isoformat(),
            "file_count": file_count,
            "limit": self.MAX_ROOT_FILES,
            "violation": file_count > self.MAX_ROOT_FILES,
            "moved_files": [],
            "essential_files": [],
            "status": "OK",
        }

        if file_count > self.MAX_ROOT_FILES:
            self._log(
                f"VIOLATION: {file_count} files in root (limit: {self.MAX_ROOT_FILES})",
                "WARNING",
            )
            result["status"] = "VIOLATION"

            # Categorize all files
            non_essential_files = []
            essential_files = []

            for file_path in root_files:
                category = self._categorize_file(file_path)

                if category.essential:
                    essential_files.append(file_path.name)
                else:
                    non_essential_files.append((file_path, category))

            result["essential_files"] = essential_files

            # Move non-essential files until we're under the limit
            moved_count = 0
            for file_path, category in non_essential_files:
                if (
                    len(essential_files) + len(non_essential_files) - moved_count
                    <= self.MAX_ROOT_FILES
                ):
                    break

                if self._move_file(file_path, category.target_directory):
                    result["moved_files"].append(
                        {
                            "file": file_path.name,
                            "destination": category.target_directory,
                            "reason": category.description,
                        }
                    )
                    moved_count += 1

            # Check if we successfully resolved the violation
            new_count = len(self._get_current_root_files())
            if new_count <= self.MAX_ROOT_FILES:
                result["status"] = "RESOLVED"
                self._log(f"Violation resolved: {new_count} files remaining")
            else:
                result["status"] = "PARTIAL"
                self._log(f"Partial resolution: {new_count} files remaining", "WARNING")

        # Save status
        with open(self.status_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        return result

    def start_monitoring(self):
        """Start real-time monitoring"""
        self._log("Starting real-time root file monitoring")

        class RootFileHandler(FileSystemEventHandler):
            def __init__(self, enforcer):
                self.enforcer = enforcer

            def on_created(self, event):
                if not event.is_directory:
                    file_path = Path(event.src_path)
                    if file_path.parent == self.enforcer.project_root:
                        self.enforcer._log(f"New file detected: {file_path.name}")
                        self.enforcer.check_and_enforce_limit()

            def on_moved(self, event):
                if not event.is_directory:
                    dest_path = Path(event.dest_path)
                    if dest_path.parent == self.enforcer.project_root:
                        self.enforcer._log(f"File moved to root: {dest_path.name}")
                        self.enforcer.check_and_enforce_limit()

        handler = RootFileHandler(self)
        self.observer = Observer()
        self.observer.schedule(handler, str(self.project_root), recursive=False)
        self.observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
            self._log("Monitoring stopped")

        self.observer.join()

    def stop_monitoring(self):
        """Stop monitoring"""
        if self.observer:
            self.observer.stop()
            self.observer.join()

    def generate_report(self) -> Dict[str, any]:
        """Generate comprehensive enforcement report"""
        root_files = self._get_current_root_files()

        report = {
            "timestamp": datetime.now().isoformat(),
            "system_status": "PRODUCTION",
            "enforcement_active": True,
            "file_limit": self.MAX_ROOT_FILES,
            "current_count": len(root_files),
            "compliance": len(root_files) <= self.MAX_ROOT_FILES,
            "essential_files": list(self.ESSENTIAL_FILES),
            "current_files": [f.name for f in root_files],
            "monitoring_config": {
                "max_files": self.MAX_ROOT_FILES,
                "auto_move": True,
                "real_time": True,
            },
        }

        # Save report
        report_file = (
            self.runtime_dir
            / f"enforcement_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        return report


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Root File Limit Enforcer")
    parser.add_argument("--check", action="store_true", help="Check current status")
    parser.add_argument(
        "--monitor", action="store_true", help="Start real-time monitoring"
    )
    parser.add_argument("--report", action="store_true", help="Generate report")
    parser.add_argument("--fix", action="store_true", help="Fix current violations")

    args = parser.parse_args()

    enforcer = RootFileLimitEnforcer()

    if args.check:
        status = enforcer.check_and_enforce_limit()
        print(f"Status: {status['status']}")
        print(f"Files: {status['file_count']}/{status['limit']}")

    elif args.monitor:
        print("🚨 Starting real-time root file monitoring...")
        enforcer.start_monitoring()

    elif args.report:
        report = enforcer.generate_report()
        print(f"Report generated: {report['compliance']}")

    elif args.fix:
        print("🔧 Fixing current violations...")
        result = enforcer.check_and_enforce_limit()
        print(f"Result: {result['status']}")

    else:
        # Default: check and fix
        print("🚨 Root File Limit Enforcer - Production Mode")
        print("=" * 50)

        result = enforcer.check_and_enforce_limit()
        print(f"✅ Enforcement complete: {result['status']}")
        print(f"📊 Files: {result['file_count']}/{result['limit']}")

        if result["moved_files"]:
            print("\n📁 Files moved:")
            for moved in result["moved_files"]:
                print(f"  • {moved['file']} → {moved['destination']}")


if __name__ == "__main__":
    main()
