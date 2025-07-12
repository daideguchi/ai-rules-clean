#!/usr/bin/env python3
"""Archive and organize conversation logs and session records."""

import json
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path


class LogArchiver:
    def __init__(self):
        self.runtime_dir = Path("runtime")
        self.archive_dir = self.runtime_dir / "archives"
        self.archive_dir.mkdir(exist_ok=True)

    def archive_old_logs(self, days_old=7):
        """Archive logs older than specified days."""
        cutoff_date = datetime.now() - timedelta(days=days_old)

        # Archive conversation logs
        conv_logs = self.runtime_dir / "conversation_logs"
        if conv_logs.exists():
            archived_count = 0
            for log_file in conv_logs.glob("*.json"):
                # Parse date from filename
                try:
                    date_str = (
                        log_file.stem.split("_")[-2] + log_file.stem.split("_")[-1]
                    )
                    file_date = datetime.strptime(date_str, "%Y%m%d%H%M%S")

                    if file_date < cutoff_date:
                        # Create monthly archive directory
                        month_dir = (
                            self.archive_dir
                            / "conversation_logs"
                            / file_date.strftime("%Y-%m")
                        )
                        month_dir.mkdir(parents=True, exist_ok=True)

                        # Move file to archive
                        shutil.move(str(log_file), str(month_dir / log_file.name))
                        archived_count += 1
                except Exception as e:
                    print(f"Error processing {log_file}: {e}")

            print(f"Archived {archived_count} conversation logs")

    def consolidate_evaluation_reports(self):
        """Consolidate repetitive evaluation reports."""
        eval_dir = self.runtime_dir / "evaluations"
        if not eval_dir.exists():
            return

        # Group by date
        reports_by_date = {}
        for report in eval_dir.glob("*.json"):
            try:
                # Extract date from filename
                parts = report.stem.split("_")
                date_str = parts[-2] + "_" + parts[-1]
                system_name = "_".join(parts[:-2])

                if date_str not in reports_by_date:
                    reports_by_date[date_str] = {}

                with open(report) as f:
                    reports_by_date[date_str][system_name] = json.load(f)

            except Exception as e:
                print(f"Error processing {report}: {e}")

        # Create consolidated daily reports
        consolidated_dir = self.runtime_dir / "evaluations_consolidated"
        consolidated_dir.mkdir(exist_ok=True)

        for date_str, systems in reports_by_date.items():
            consolidated_file = consolidated_dir / f"daily_evaluation_{date_str}.json"
            with open(consolidated_file, "w") as f:
                json.dump(
                    {
                        "date": date_str,
                        "systems": systems,
                        "summary": {
                            "total_systems": len(systems),
                            "evaluated_at": datetime.now().isoformat(),
                        },
                    },
                    f,
                    indent=2,
                )

        print(f"Consolidated {len(reports_by_date)} days of evaluation reports")

    def cleanup_empty_directories(self):
        """Remove empty directories in runtime."""
        removed = []
        for root, dirs, files in os.walk(self.runtime_dir, topdown=False):
            if not dirs and not files and root != str(self.runtime_dir):
                try:
                    os.rmdir(root)
                    removed.append(root)
                except Exception as e:
                    print(f"Could not remove {root}: {e}")

        print(f"Removed {len(removed)} empty directories")

    def organize_databases(self):
        """Move scattered database files to centralized location."""
        db_dir = self.runtime_dir / "databases"
        db_dir.mkdir(exist_ok=True)

        # Find all .db files in runtime root
        moved = 0
        for db_file in self.runtime_dir.glob("*.db"):
            if db_file.is_file():
                shutil.move(str(db_file), str(db_dir / db_file.name))
                moved += 1

        print(f"Moved {moved} database files to runtime/databases/")

    def create_log_rotation_config(self):
        """Create configuration for log rotation."""
        config = {
            "rotation_rules": {
                "conversation_logs": {
                    "max_age_days": 30,
                    "archive_after_days": 7,
                    "compression": "gzip",
                },
                "system_logs": {
                    "max_size_mb": 10,
                    "max_files": 5,
                    "compression": "gzip",
                },
                "evaluation_reports": {
                    "consolidate_daily": True,
                    "archive_after_days": 30,
                },
            },
            "archive_structure": {
                "pattern": "archives/{log_type}/{year}/{month}/{filename}",
                "compression": True,
            },
        }

        config_file = self.runtime_dir / "log_rotation_config.json"
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)

        print(f"Created log rotation configuration at {config_file}")


if __name__ == "__main__":
    archiver = LogArchiver()

    print("=== Starting Log Organization ===")
    archiver.archive_old_logs()
    archiver.consolidate_evaluation_reports()
    archiver.organize_databases()
    archiver.cleanup_empty_directories()
    archiver.create_log_rotation_config()
    print("=== Log Organization Complete ===")
