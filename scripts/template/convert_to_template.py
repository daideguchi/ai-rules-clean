#!/usr/bin/env python3
"""
Template Conversion Script
=========================

This script converts the project from a specific instance (with hardcoded "88回")
to a template-friendly version that starts from 0 mistakes and uses dynamic
mistake counting.

Usage:
    python scripts/template/convert_to_template.py [--dry-run] [--backup]
"""

import argparse
import json
import os
import re
import shutil
from datetime import datetime
from typing import Any, Dict, List, Tuple


class TemplateConverter:
    """Converts hardcoded mistake references to template-friendly dynamic system"""

    def __init__(self, project_root: str = None):
        self.project_root = project_root or os.getcwd()
        self.backup_dir = os.path.join(self.project_root, "backup_pre_template")
        self.conversion_log = []

        # Patterns to replace
        self.replacement_patterns = [
            # Core pattern: "88回"
            (r"88回", "{{mistake_count}}回"),
            (r"88回ミス", "{{mistake_count}}回ミス"),
            (r"88回の", "{{mistake_count}}回の"),
            (r"88回同じ", "{{mistake_count}}回同じ"),
            (r"88回繰り返し", "{{mistake_count}}回繰り返し"),
            (r"88回から", "{{mistake_count}}回から"),
            (r"88回のミス", "{{mistake_count}}回のミス"),
            # Specific system names
            (r"88回ミス防止", "ミス防止"),
            (r"88回ミス防止システム", "ミス防止システム"),
            (r"88回ミス防止・", "ミス防止・"),
            (r"88回ミス防止AI", "ミス防止AI"),
            (r"88回ミス防止メカニズム", "ミス防止メカニズム"),
            # Project names and titles
            (r"coding-rule2: 88回ミス防止", "coding-rule2: AI安全ガバナンス"),
            (r"CODING-RULE2.*88回", "CODING-RULE2 AI安全ガバナンスシステム"),
            # Specific contextual references
            (r"88回実行", "{{mistake_count}}回実行"),
            (r"88回実績", "{{mistake_count}}回実績"),
            (r"88回という", "{{mistake_count}}回という"),
            (r"88回に", "{{mistake_count}}回に"),
            (r"88回で", "{{mistake_count}}回で"),
            (r"88回を", "{{mistake_count}}回を"),
            (r"88回が", "{{mistake_count}}回が"),
            (r"88回は", "{{mistake_count}}回は"),
            # Comments and documentation
            (r"# 88回", "# {{mistake_count}}回"),
            (r"## 88回", "## {{mistake_count}}回"),
            (r"### 88回", "### {{mistake_count}}回"),
            (r"88回.*システム", "ミス防止システム"),
            # Error messages and logs
            (r"88回.*エラー", "{{mistake_count}}回エラー"),
            (r"88回.*違反", "{{mistake_count}}回違反"),
            (r"88回.*問題", "{{mistake_count}}回問題"),
            # Template-specific adjustments
            (r"88回.*テンプレート", "テンプレート"),
            (r"88回.*template", "template"),
        ]

        # Files to exclude from conversion
        self.exclude_patterns = [
            "backup_pre_template/*",
            ".git/*",
            "node_modules/*",
            "__pycache__/*",
            "*.pyc",
            "runtime/logs/*",
            "runtime/mistakes/*",
            "scripts/template/convert_to_template.py",  # Don't convert this script
        ]

        # Special handling for specific files
        self.special_file_handlers = {
            "CLAUDE.md": self._handle_claude_md,
            "README.md": self._handle_readme_md,
            "Index.md": self._handle_index_md,
            "startup_checklist.md": self._handle_startup_checklist,
        }

    def should_exclude_file(self, file_path: str) -> bool:
        """Check if file should be excluded from conversion"""
        rel_path = os.path.relpath(file_path, self.project_root)

        for pattern in self.exclude_patterns:
            if re.match(pattern.replace("*", ".*"), rel_path):
                return True
        return False

    def backup_files(self):
        """Create backup of original files"""
        if os.path.exists(self.backup_dir):
            shutil.rmtree(self.backup_dir)

        print(f"📦 Creating backup in {self.backup_dir}")
        shutil.copytree(
            self.project_root,
            self.backup_dir,
            ignore=shutil.ignore_patterns(".git", "node_modules", "__pycache__"),
        )

        self.conversion_log.append(f"Backup created: {self.backup_dir}")

    def find_files_to_convert(self) -> List[str]:
        """Find all files that need conversion"""
        files_to_convert = []

        # Find all text files
        text_extensions = [".py", ".md", ".txt", ".json", ".sh", ".yml", ".yaml"]

        for root, dirs, files in os.walk(self.project_root):
            # Skip excluded directories
            dirs[:] = [
                d for d in dirs if not self.should_exclude_file(os.path.join(root, d))
            ]

            for file in files:
                file_path = os.path.join(root, file)

                # Skip excluded files
                if self.should_exclude_file(file_path):
                    continue

                # Check extension
                if any(file.endswith(ext) for ext in text_extensions):
                    # Check if file contains "88回"
                    try:
                        with open(file_path, encoding="utf-8") as f:
                            content = f.read()
                            if "88回" in content:
                                files_to_convert.append(file_path)
                    except (UnicodeDecodeError, PermissionError):
                        continue

        return files_to_convert

    def convert_file(
        self, file_path: str, dry_run: bool = False
    ) -> Tuple[bool, List[str]]:
        """Convert a single file"""
        changes = []

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            original_content = content

            # Apply special handler if available
            filename = os.path.basename(file_path)
            if filename in self.special_file_handlers:
                content = self.special_file_handlers[filename](content, file_path)
                if content != original_content:
                    changes.append(f"Applied special handler for {filename}")

            # Apply general patterns
            for pattern, replacement in self.replacement_patterns:
                old_content = content
                content = re.sub(pattern, replacement, content)
                if content != old_content:
                    changes.append(f"Applied pattern: {pattern} -> {replacement}")

            # Write back if changes were made and not dry run
            if content != original_content and not dry_run:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                return True, changes

            return content != original_content, changes

        except Exception as e:
            changes.append(f"Error: {str(e)}")
            return False, changes

    def _handle_claude_md(self, content: str, file_path: str) -> str:
        """Special handler for CLAUDE.md"""
        # Replace the main title
        content = re.sub(
            r"# CLAUDE\.md - 88回ミス防止.*",
            "# CLAUDE.md - AI安全ガバナンスシステム テンプレート",
            content,
        )

        # Add template notice
        template_notice = """
## 🎯 テンプレートについて

このシステムは**テンプレート**として設計されています：
- **ミス数**: 0回からスタート（プロジェクト固有でインクリメント）
- **動的計数**: 実際のミス発生時に自動カウント
- **学習システム**: 各プロジェクトの固有パターンを学習
- **予防機能**: 蓄積されたミス防止アルゴリズムを活用

```bash
# 現在のミス数確認
python3 src/ai/mistake_counter_system.py

# 新しいミス記録
python3 src/ai/mistake_counter_system.py --add-mistake
```

"""

        # Insert template notice after the title
        content = re.sub(r"(# CLAUDE\.md.*\n\n)", r"\1" + template_notice, content)

        return content

    def _handle_readme_md(self, content: str, file_path: str) -> str:
        """Special handler for README.md"""
        # Update project description
        content = re.sub(
            r"88回ミス防止.*システム",
            "AI安全ガバナンスシステム（テンプレート）",
            content,
        )

        # Add template section
        template_section = """
## 🎯 テンプレートとしての使用

このプロジェクトは**AI安全ガバナンステンプレート**として設計されています：

### 特徴
- **0回スタート**: 新プロジェクトは0ミスから開始
- **動的計数**: 実際のミス発生時に自動インクリメント
- **学習機能**: プロジェクト固有のパターンを学習
- **予防システム**: 蓄積されたミス防止アルゴリズムを活用

### 使用方法
```bash
# 1. テンプレートの初期化
make template-init

# 2. 現在のミス数確認
make mistake-count

# 3. システム起動
make startup
```

"""

        # Insert template section after the main description
        content = re.sub(
            r"(## 📋 プロジェクト概要.*?\n\n)",
            r"\1" + template_section,
            content,
            flags=re.DOTALL,
        )

        return content

    def _handle_index_md(self, content: str, file_path: str) -> str:
        """Special handler for Index.md"""
        # Update the bottom tagline
        content = re.sub(
            r"\*\*🎯 88回ミス防止システム.*\*\*",
            "**🎯 AI安全ガバナンステンプレート - 動的ミス防止システム**",
            content,
        )

        return content

    def _handle_startup_checklist(self, content: str, file_path: str) -> str:
        """Special handler for startup checklist"""
        # Add template initialization step
        template_step = """
## 🎯 テンプレート初期化（新プロジェクト時のみ）

### 必須：最初の1回のみ実行
```bash
# テンプレート初期化
make template-init

# ミス数確認（0回になることを確認）
make mistake-count
```

"""

        # Insert template step at the beginning
        content = re.sub(r"(# .*\n\n)", r"\1" + template_step, content)

        return content

    def create_template_makefile_targets(self):
        """Add template-specific targets to Makefile"""
        makefile_path = os.path.join(self.project_root, "Makefile")

        template_targets = """
## Template Management Commands
template-init: ## テンプレート初期化（新プロジェクト用）
\t@echo "🎯 テンプレート初期化開始..."
\t@python3 src/ai/mistake_counter_system.py --init-template
\t@echo "✅ テンプレート初期化完了"

mistake-count: ## 現在のミス数確認
\t@echo "🔢 現在のミス数:"
\t@python3 src/ai/mistake_counter_system.py --count

add-mistake: ## 新しいミス記録
\t@echo "📝 新しいミス記録:"
\t@python3 src/ai/mistake_counter_system.py --add-mistake

mistake-stats: ## ミス統計表示
\t@echo "📊 ミス統計:"
\t@python3 src/ai/mistake_counter_system.py --stats

template-export: ## テンプレート設定エクスポート
\t@echo "📦 テンプレート設定エクスポート:"
\t@python3 src/ai/mistake_counter_system.py --export-template
"""

        try:
            with open(makefile_path, encoding="utf-8") as f:
                content = f.read()

            # Add template targets at the end
            if "template-init:" not in content:
                content += template_targets

                with open(makefile_path, "w", encoding="utf-8") as f:
                    f.write(content)

                self.conversion_log.append("Added template targets to Makefile")
        except Exception as e:
            self.conversion_log.append(f"Error updating Makefile: {str(e)}")

    def create_template_config(self):
        """Create template configuration files"""
        config_dir = os.path.join(self.project_root, "runtime", "mistakes")
        os.makedirs(config_dir, exist_ok=True)

        # Create template configuration
        template_config = {
            "project_name": "AI Safety Governance System (Template)",
            "template_mode": True,
            "mistake_count": 0,
            "mistake_limit_warning": 50,
            "mistake_limit_critical": 100,
            "auto_prevention_enabled": True,
            "learning_system_enabled": True,
            "started_from_template": True,
            "template_version": "1.0.0",
            "initialization_date": datetime.now().isoformat(),
            "conversion_date": datetime.now().isoformat(),
            "original_project_mistakes": 88,  # Keep as reference
            "template_notes": "This template starts from 0 mistakes and increments as needed",
        }

        config_file = os.path.join(config_dir, "mistake_config.json")
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(template_config, f, indent=2, ensure_ascii=False)

        # Create empty mistake history
        history_file = os.path.join(config_dir, "mistake_history.json")
        history_data = {
            "mistakes": [],
            "total_count": 0,
            "last_updated": datetime.now().isoformat(),
            "template_initialized": True,
        }

        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(history_data, f, indent=2, ensure_ascii=False)

        self.conversion_log.append("Created template configuration files")

    def convert_to_template(
        self, dry_run: bool = False, create_backup: bool = True
    ) -> Dict[str, Any]:
        """Main conversion function"""
        print("🔄 Template Conversion Starting...")
        print("=" * 50)

        # Create backup if requested
        if create_backup and not dry_run:
            self.backup_files()

        # Find files to convert
        files_to_convert = self.find_files_to_convert()
        print(f"📁 Found {len(files_to_convert)} files to convert")

        # Convert files
        converted_files = []
        failed_files = []

        for file_path in files_to_convert:
            rel_path = os.path.relpath(file_path, self.project_root)
            print(f"🔄 Converting: {rel_path}")

            success, changes = self.convert_file(file_path, dry_run)

            if success:
                converted_files.append((rel_path, changes))
            else:
                failed_files.append((rel_path, changes))

        # Create template-specific files
        if not dry_run:
            self.create_template_makefile_targets()
            self.create_template_config()

        # Generate report
        report = {
            "conversion_date": datetime.now().isoformat(),
            "dry_run": dry_run,
            "backup_created": create_backup and not dry_run,
            "files_found": len(files_to_convert),
            "files_converted": len(converted_files),
            "files_failed": len(failed_files),
            "converted_files": converted_files,
            "failed_files": failed_files,
            "conversion_log": self.conversion_log,
        }

        # Save report
        if not dry_run:
            report_file = os.path.join(
                self.project_root, "template_conversion_report.json"
            )
            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

        return report


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Convert project to template-friendly version"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without making changes",
    )
    parser.add_argument("--no-backup", action="store_true", help="Skip creating backup")
    parser.add_argument("--project-root", default=".", help="Project root directory")

    args = parser.parse_args()

    # Initialize converter
    converter = TemplateConverter(args.project_root)

    # Run conversion
    report = converter.convert_to_template(
        dry_run=args.dry_run, create_backup=not args.no_backup
    )

    # Display results
    print("\n" + "=" * 50)
    print("🎉 Template Conversion Complete!")
    print("=" * 50)

    print(f"📊 Files processed: {report['files_found']}")
    print(f"✅ Files converted: {report['files_converted']}")
    print(f"❌ Files failed: {report['files_failed']}")

    if report["dry_run"]:
        print("\n⚠️  This was a dry run - no changes were made")
    else:
        print("\n✅ Template conversion completed successfully")
        if report["backup_created"]:
            print("📦 Backup created in: backup_pre_template/")
        print("📄 Report saved to: template_conversion_report.json")

    # Show some converted files
    if report["converted_files"]:
        print("\n📝 Sample converted files:")
        for file_path, changes in report["converted_files"][:5]:
            print(f"  • {file_path} ({len(changes)} changes)")

    # Show failed files
    if report["failed_files"]:
        print("\n⚠️  Failed files:")
        for file_path, errors in report["failed_files"]:
            print(f"  • {file_path}: {errors}")


if __name__ == "__main__":
    main()
