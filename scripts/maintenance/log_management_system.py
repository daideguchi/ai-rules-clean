#!/usr/bin/env python3
"""Comprehensive log management and rotation system."""

import gzip
import json
import os
import shutil
from collections import defaultdict
from datetime import datetime
from pathlib import Path


class LogManagementSystem:
    def __init__(self):
        self.runtime_dir = Path("runtime")
        self.logs_dir = self.runtime_dir / "logs"
        self.config = self.load_config()

    def load_config(self):
        """Load or create log management configuration."""
        config_file = self.runtime_dir / "log_management_config.json"

        default_config = {
            "log_categories": {
                "system_logs": {
                    "path": "logs/*.log",
                    "max_size_mb": 10,
                    "max_age_days": 30,
                    "compress_after_days": 7,
                },
                "evaluation_reports": {
                    "path": "evaluations/*.json",
                    "consolidate": True,
                    "max_age_days": 90,
                    "archive_pattern": "archives/evaluations/{year}-{month}",
                },
                "nist_compliance": {
                    "path": "nist_ai_rmf/compliance_report_*.json",
                    "consolidate_by": "daily",
                    "max_age_days": 180,
                },
                "continuous_improvement": {
                    "path": "continuous_improvement/improvement_report_*.json",
                    "consolidate_by": "weekly",
                    "max_age_days": 90,
                },
            },
            "archive_settings": {
                "base_path": "archives",
                "compression": "gzip",
                "structure": "{category}/{year}/{month}/{filename}",
            },
        }

        if config_file.exists():
            with open(config_file) as f:
                return json.load(f)
        else:
            with open(config_file, "w") as f:
                json.dump(default_config, f, indent=2)
            return default_config

    def rotate_logs_by_size(self, pattern, max_size_mb):
        """Rotate logs that exceed size limit."""
        max_size_bytes = max_size_mb * 1024 * 1024
        rotated = []

        for log_file in self.runtime_dir.glob(pattern):
            if log_file.stat().st_size > max_size_bytes:
                # Create rotated filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                rotated_name = f"{log_file.stem}_{timestamp}{log_file.suffix}"
                rotated_path = log_file.parent / rotated_name

                # Move current log
                shutil.move(str(log_file), str(rotated_path))

                # Compress if needed
                self.compress_file(rotated_path)
                rotated.append(rotated_path)

                # Create new empty log
                log_file.touch()

        return rotated

    def compress_file(self, file_path):
        """Compress a file using gzip."""
        compressed_path = Path(f"{file_path}.gz")

        with open(file_path, "rb") as f_in:
            with gzip.open(compressed_path, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)

        # Remove original
        os.remove(file_path)
        return compressed_path

    def consolidate_reports(self, pattern, consolidate_by="daily"):
        """Consolidate multiple report files by time period."""
        reports = defaultdict(list)

        for report_file in self.runtime_dir.glob(pattern):
            try:
                # Extract timestamp from filename
                parts = report_file.stem.split("_")
                date_str = parts[-2] + parts[-1]
                file_date = datetime.strptime(date_str, "%Y%m%d%H%M%S")

                # Group by period
                if consolidate_by == "daily":
                    key = file_date.strftime("%Y%m%d")
                elif consolidate_by == "weekly":
                    key = file_date.strftime("%Y-W%U")
                elif consolidate_by == "monthly":
                    key = file_date.strftime("%Y%m")
                else:
                    key = date_str

                reports[key].append(report_file)

            except Exception as e:
                print(f"Error processing {report_file}: {e}")

        # Create consolidated files
        consolidated_dir = self.runtime_dir / f"{pattern.split('/')[0]}_consolidated"
        consolidated_dir.mkdir(exist_ok=True)

        for period, files in reports.items():
            consolidated_data = {
                "period": period,
                "consolidate_by": consolidate_by,
                "reports": [],
                "summary": {
                    "total_reports": len(files),
                    "consolidated_at": datetime.now().isoformat(),
                },
            }

            for report_file in files:
                with open(report_file) as f:
                    data = json.load(f)
                    consolidated_data["reports"].append(
                        {"filename": report_file.name, "data": data}
                    )

            # Save consolidated file
            consolidated_file = consolidated_dir / f"consolidated_{period}.json"
            with open(consolidated_file, "w") as f:
                json.dump(consolidated_data, f, indent=2)

            # Archive original files
            archive_dir = self.runtime_dir / "archives" / pattern.split("/")[0] / period
            archive_dir.mkdir(parents=True, exist_ok=True)

            for report_file in files:
                shutil.move(str(report_file), str(archive_dir / report_file.name))

        return len(reports)

    def create_monitoring_dashboard(self):
        """Create a log monitoring dashboard configuration."""
        dashboard = {"log_statistics": {}, "alerts": [], "recommendations": []}

        # Analyze log sizes and counts
        for category, settings in self.config["log_categories"].items():
            pattern = settings["path"]
            files = list(self.runtime_dir.glob(pattern))

            if files:
                total_size = sum(f.stat().st_size for f in files)
                oldest_file = min(files, key=lambda f: f.stat().st_mtime)
                newest_file = max(files, key=lambda f: f.stat().st_mtime)

                dashboard["log_statistics"][category] = {
                    "file_count": len(files),
                    "total_size_mb": round(total_size / 1024 / 1024, 2),
                    "oldest_file": oldest_file.name,
                    "newest_file": newest_file.name,
                    "average_size_kb": round((total_size / len(files)) / 1024, 2),
                }

                # Generate alerts
                if total_size > 100 * 1024 * 1024:  # 100MB
                    dashboard["alerts"].append(
                        {
                            "category": category,
                            "type": "size_warning",
                            "message": f"{category} logs exceed 100MB",
                        }
                    )

                if len(files) > 100:
                    dashboard["alerts"].append(
                        {
                            "category": category,
                            "type": "count_warning",
                            "message": f"{category} has {len(files)} files",
                        }
                    )

        # Generate recommendations
        dashboard["recommendations"] = self.generate_cleanup_recommendations()

        # Save dashboard
        dashboard_file = self.runtime_dir / "log_monitoring_dashboard.json"
        with open(dashboard_file, "w") as f:
            json.dump(dashboard, f, indent=2)

        return dashboard

    def generate_cleanup_recommendations(self):
        """Generate specific cleanup recommendations."""
        recommendations = []

        # Check NIST compliance reports
        nist_files = list(self.runtime_dir.glob("nist_ai_rmf/compliance_report_*.json"))
        if len(nist_files) > 30:
            recommendations.append(
                {
                    "priority": "high",
                    "action": "consolidate",
                    "target": "nist_ai_rmf",
                    "reason": f"Found {len(nist_files)} compliance reports",
                    "command": "python scripts/maintenance/log_management_system.py --consolidate-nist",
                }
            )

        # Check evaluation reports
        eval_files = list(self.runtime_dir.glob("evaluations/*.json"))
        if len(eval_files) > 50:
            recommendations.append(
                {
                    "priority": "high",
                    "action": "archive",
                    "target": "evaluations",
                    "reason": f"Found {len(eval_files)} evaluation reports",
                    "command": "python scripts/maintenance/log_management_system.py --archive-evaluations",
                }
            )

        # Check log file sizes
        large_logs = []
        for log_file in self.logs_dir.glob("*.log"):
            if log_file.stat().st_size > 10 * 1024 * 1024:  # 10MB
                large_logs.append(log_file.name)

        if large_logs:
            recommendations.append(
                {
                    "priority": "medium",
                    "action": "rotate",
                    "target": "large_logs",
                    "files": large_logs,
                    "reason": "Log files exceed 10MB",
                    "command": "python scripts/maintenance/log_management_system.py --rotate-large",
                }
            )

        return recommendations


if __name__ == "__main__":
    manager = LogManagementSystem()

    print("=== Log Management System ===")

    # Create monitoring dashboard
    dashboard = manager.create_monitoring_dashboard()

    print("\nLog Statistics:")
    for category, stats in dashboard["log_statistics"].items():
        print(f"\n{category}:")
        print(f"  Files: {stats['file_count']}")
        print(f"  Total Size: {stats['total_size_mb']} MB")
        print(f"  Average Size: {stats['average_size_kb']} KB")

    if dashboard["alerts"]:
        print("\n⚠️ Alerts:")
        for alert in dashboard["alerts"]:
            print(f"  - {alert['message']}")

    if dashboard["recommendations"]:
        print("\n📋 Recommendations:")
        for rec in dashboard["recommendations"]:
            print(f"\n  Priority: {rec['priority']}")
            print(f"  Action: {rec['action']} - {rec['reason']}")
            print(f"  Command: {rec['command']}")
