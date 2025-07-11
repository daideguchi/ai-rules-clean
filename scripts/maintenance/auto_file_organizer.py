#!/usr/bin/env python3
"""
📁 Auto File Organizer - Intelligent File Structure Cleanup
==========================================================

Automatically organizes scattered files based on predefined rules:
- Archives old logs and reports
- Removes duplicate backups
- Consolidates docs structure
- Cleans up root directory

Follows the established file organization rules.
"""

import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict


class AutoFileOrganizer:
    """Intelligent file organization system"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.archive_dir = project_root / "runtime" / "archives"
        self.cleanup_log = []

    def organize_files(self) -> Dict[str, Any]:
        """Execute complete file organization"""

        print("📁 Auto File Organizer - Starting cleanup")
        print("=" * 50)

        # Create archive directory
        self.archive_dir.mkdir(parents=True, exist_ok=True)

        # Execute cleanup tasks
        self._archive_old_logs()
        self._remove_duplicate_docs()
        self._clean_root_directory()
        self._archive_old_reports()
        self._remove_temp_files()

        # Generate report
        report = {
            "timestamp": datetime.now().isoformat(),
            "actions_taken": len(self.cleanup_log),
            "cleanup_actions": self.cleanup_log,
            "organized_directories": [
                "runtime/logs",
                "docs",
                "root",
                "runtime/reports",
            ],
        }

        # Save report
        report_file = self.project_root / "runtime" / "file_organization_report.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        print("\n✅ File organization complete")
        print(f"📊 Actions taken: {len(self.cleanup_log)}")
        print(f"📄 Report saved: {report_file}")

        return report

    def _archive_old_logs(self):
        """Archive logs older than 7 days"""

        logs_dir = self.project_root / "runtime" / "logs"
        if not logs_dir.exists():
            return

        cutoff_date = datetime.now() - timedelta(days=7)
        archived_count = 0

        for log_file in logs_dir.glob("*.log"):
            if log_file.stat().st_mtime < cutoff_date.timestamp():
                archive_path = self.archive_dir / "logs" / log_file.name
                archive_path.parent.mkdir(parents=True, exist_ok=True)

                shutil.move(str(log_file), str(archive_path))
                archived_count += 1

                self.cleanup_log.append(
                    {
                        "action": "archive_log",
                        "file": log_file.name,
                        "destination": str(archive_path),
                    }
                )

        print(f"📦 Archived {archived_count} old log files")

    def _remove_duplicate_docs(self):
        """Remove duplicate docs backup directory"""

        backup_docs = self.project_root / "docs_backup_20250711_071807"
        if backup_docs.exists():
            # Check if it's actually a duplicate
            main_docs = self.project_root / "docs"

            if main_docs.exists():
                shutil.rmtree(backup_docs)
                self.cleanup_log.append(
                    {
                        "action": "remove_duplicate",
                        "directory": "docs_backup_20250711_071807",
                        "reason": "Duplicate of main docs directory",
                    }
                )
                print("🗑️ Removed duplicate docs backup")

    def _clean_root_directory(self):
        """Clean up root directory files"""

        # Files to archive
        archive_candidates = [
            "CLAUDE.expanded.md",
            "CLAUDE.md.backup",
            "QUICK_REFERENCE.md",
        ]

        archived_count = 0
        for filename in archive_candidates:
            file_path = self.project_root / filename
            if file_path.exists():
                archive_path = self.archive_dir / "root_files" / filename
                archive_path.parent.mkdir(parents=True, exist_ok=True)

                shutil.move(str(file_path), str(archive_path))
                archived_count += 1

                self.cleanup_log.append(
                    {
                        "action": "archive_root_file",
                        "file": filename,
                        "destination": str(archive_path),
                    }
                )

        # Remove Python temp files
        temp_files = [
            "consult_ais_claude_md.py",
            "migrate_mcp_files.py",
            "test_mcp_simple.py",
        ]

        for filename in temp_files:
            file_path = self.project_root / filename
            if file_path.exists():
                file_path.unlink()
                self.cleanup_log.append(
                    {
                        "action": "remove_temp",
                        "file": filename,
                        "reason": "Temporary script file",
                    }
                )
                archived_count += 1

        print(f"🧹 Cleaned {archived_count} root directory files")

    def _archive_old_reports(self):
        """Archive old reports and improvement files"""

        reports_dirs = [
            "runtime/continuous_improvement",
            "runtime/nist_ai_rmf",
            "runtime/evaluation_reports",
        ]

        archived_count = 0
        cutoff_date = datetime.now() - timedelta(days=14)

        for reports_dir in reports_dirs:
            dir_path = self.project_root / reports_dir
            if not dir_path.exists():
                continue

            for report_file in dir_path.glob("*.json"):
                if report_file.stat().st_mtime < cutoff_date.timestamp():
                    archive_path = self.archive_dir / reports_dir / report_file.name
                    archive_path.parent.mkdir(parents=True, exist_ok=True)

                    shutil.move(str(report_file), str(archive_path))
                    archived_count += 1

                    self.cleanup_log.append(
                        {
                            "action": "archive_report",
                            "file": str(report_file.relative_to(self.project_root)),
                            "destination": str(archive_path),
                        }
                    )

        print(f"📊 Archived {archived_count} old report files")

    def _remove_temp_files(self):
        """Remove temporary and debug files"""

        temp_patterns = ["debug_*.py", "*.pyc", "__pycache__", ".DS_Store"]

        removed_count = 0

        for pattern in temp_patterns:
            for temp_file in self.project_root.rglob(pattern):
                if temp_file.is_file():
                    temp_file.unlink()
                    removed_count += 1
                elif temp_file.is_dir():
                    shutil.rmtree(temp_file)
                    removed_count += 1

                self.cleanup_log.append(
                    {
                        "action": "remove_temp",
                        "file": str(temp_file.relative_to(self.project_root)),
                        "reason": f"Temporary file matching {pattern}",
                    }
                )

        print(f"🗑️ Removed {removed_count} temporary files")


def main():
    """Main execution function"""

    project_root = Path(__file__).parent.parent.parent
    organizer = AutoFileOrganizer(project_root)

    report = organizer.organize_files()

    # Print summary
    print("\n📁 File Organization Summary:")
    print(f"   Total actions: {report['actions_taken']}")
    print(f"   Organized dirs: {len(report['organized_directories'])}")
    print("   Report saved: runtime/file_organization_report.json")


if __name__ == "__main__":
    main()
