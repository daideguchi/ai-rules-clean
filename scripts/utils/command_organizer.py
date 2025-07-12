#!/usr/bin/env python3
"""
Command Organizer - Streamlined Command Management
=================================================

This script analyzes and organizes the scattered commands in the Makefile
to provide a more intuitive and user-friendly command structure.

Features:
- Command categorization and grouping
- Duplicate command detection
- Usage frequency analysis
- Streamlined command suggestions
- Interactive command help
"""

import os
import re
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple


@dataclass
class Command:
    """Represents a single command"""

    name: str
    description: str
    category: str
    dependencies: List[str]
    frequency: str  # common, occasional, rare
    essential: bool
    complexity: str  # simple, medium, complex


class CommandOrganizer:
    """Organizes and streamlines project commands"""

    def __init__(self, project_root: str = None):
        self.project_root = project_root or os.getcwd()
        self.makefile_path = os.path.join(self.project_root, "Makefile")
        self.commands = {}
        self.categories = {}
        self.load_commands()

    def load_commands(self):
        """Load commands from Makefile"""
        try:
            with open(self.makefile_path, encoding="utf-8") as f:
                content = f.read()

            # Parse command definitions
            command_pattern = r"^([a-zA-Z0-9_-]+):\s*##\s*(.+)$"
            matches = re.findall(command_pattern, content, re.MULTILINE)

            for name, description in matches:
                self.commands[name] = Command(
                    name=name,
                    description=description,
                    category=self._categorize_command(name, description),
                    dependencies=self._extract_dependencies(name, content),
                    frequency=self._determine_frequency(name),
                    essential=self._is_essential(name),
                    complexity=self._determine_complexity(name),
                )

            self._organize_categories()

        except FileNotFoundError:
            print(f"Error: Makefile not found at {self.makefile_path}")
        except Exception as e:
            print(f"Error loading commands: {e}")

    def _categorize_command(self, name: str, description: str) -> str:
        """Categorize command based on name and description"""
        category_patterns = {
            "startup": ["startup", "start", "init", "declare", "quick-start"],
            "ai_organization": ["ai-org", "ai-roles", "memory", "db-connect"],
            "evaluation": ["evaluate", "metrics", "test", "integration-test"],
            "maintenance": ["cleanup", "install", "setup", "lint", "validate"],
            "ui": ["ui-", "dashboard", "command", "worker"],
            "template": ["template-", "mistake-", "export"],
            "documentation": ["docs", "help"],
            "development": ["daily-check", "handle-instruction", "check-root"],
        }

        name_lower = name.lower()
        desc_lower = description.lower()

        for category, patterns in category_patterns.items():
            if any(
                pattern in name_lower or pattern in desc_lower for pattern in patterns
            ):
                return category

        return "other"

    def _extract_dependencies(self, name: str, content: str) -> List[str]:
        """Extract command dependencies from Makefile"""
        # Look for make commands called within this command
        command_section = self._extract_command_section(name, content)
        if not command_section:
            return []

        make_pattern = r"@make\s+([a-zA-Z0-9_-]+)"
        matches = re.findall(make_pattern, command_section)

        return list(set(matches))

    def _extract_command_section(self, name: str, content: str) -> str:
        """Extract the section of Makefile for a specific command"""
        lines = content.split("\n")
        in_command = False
        command_lines = []

        for line in lines:
            if line.startswith(f"{name}:"):
                in_command = True
                command_lines.append(line)
            elif in_command:
                if line.startswith("\t") or line.strip() == "":
                    command_lines.append(line)
                elif line and not line.startswith("\t"):
                    break

        return "\n".join(command_lines)

    def _determine_frequency(self, name: str) -> str:
        """Determine how frequently a command is likely to be used"""
        common_commands = ["startup", "help", "status", "test", "startup-check"]
        occasional_commands = ["ai-org-start", "memory-recall", "cleanup", "install"]

        if name in common_commands:
            return "common"
        elif name in occasional_commands:
            return "occasional"
        else:
            return "rare"

    def _is_essential(self, name: str) -> bool:
        """Determine if a command is essential for basic operation"""
        essential_commands = [
            "startup",
            "declare-president",
            "ai-org-start",
            "memory-recall",
            "db-connect",
            "integration-test",
            "help",
            "status",
        ]
        return name in essential_commands

    def _determine_complexity(self, name: str) -> str:
        """Determine command complexity"""
        simple_commands = ["help", "status", "startup-check", "mistake-count"]
        complex_commands = [
            "full-startup",
            "evaluate",
            "ui-dashboard",
            "template-export",
        ]

        if name in simple_commands:
            return "simple"
        elif name in complex_commands:
            return "complex"
        else:
            return "medium"

    def _organize_categories(self):
        """Organize commands by category"""
        for command in self.commands.values():
            if command.category not in self.categories:
                self.categories[command.category] = []
            self.categories[command.category].append(command)

        # Sort commands within each category
        for category in self.categories:
            self.categories[category].sort(
                key=lambda x: (not x.essential, x.frequency, x.name)
            )

    def get_streamlined_commands(self) -> Dict[str, List[Command]]:
        """Get streamlined command organization"""
        streamlined = {
            "Essential Quick Start": [],
            "Daily Operations": [],
            "System Management": [],
            "Development & Testing": [],
            "Template & Configuration": [],
            "Advanced Features": [],
        }

        # Essential commands for quick start
        essential_startup = ["startup", "quick-start", "help", "status"]
        for cmd_name in essential_startup:
            if cmd_name in self.commands:
                streamlined["Essential Quick Start"].append(self.commands[cmd_name])

        # Daily operations
        daily_ops = [
            "declare-president",
            "ai-org-start",
            "memory-recall",
            "integration-test",
        ]
        for cmd_name in daily_ops:
            if cmd_name in self.commands:
                streamlined["Daily Operations"].append(self.commands[cmd_name])

        # System management
        system_mgmt = ["cleanup", "install", "setup-hooks", "validate", "check-root"]
        for cmd_name in system_mgmt:
            if cmd_name in self.commands:
                streamlined["System Management"].append(self.commands[cmd_name])

        # Development & testing
        dev_test = ["test", "lint", "evaluate", "metrics", "docs"]
        for cmd_name in dev_test:
            if cmd_name in self.commands:
                streamlined["Development & Testing"].append(self.commands[cmd_name])

        # Template commands
        template_cmds = [
            name
            for name in self.commands.keys()
            if name.startswith("template-") or name.startswith("mistake-")
        ]
        for cmd_name in template_cmds:
            streamlined["Template & Configuration"].append(self.commands[cmd_name])

        # Advanced features (UI, etc.)
        advanced_cmds = [
            name
            for name in self.commands.keys()
            if name.startswith("ui-") or name.startswith("full-")
        ]
        for cmd_name in advanced_cmds:
            streamlined["Advanced Features"].append(self.commands[cmd_name])

        return streamlined

    def detect_redundant_commands(self) -> List[Tuple[str, str, str]]:
        """Detect potentially redundant commands"""
        redundancies = []

        # Check for similar descriptions
        commands_by_desc = defaultdict(list)
        for cmd in self.commands.values():
            # Normalize description
            normalized = re.sub(r"[^a-zA-Z0-9\s]", "", cmd.description.lower())
            commands_by_desc[normalized].append(cmd.name)

        for desc, cmd_names in commands_by_desc.items():
            if len(cmd_names) > 1:
                redundancies.append(("similar_description", desc, ", ".join(cmd_names)))

        # Check for similar functionality
        func_groups = {
            "startup": ["startup", "quick-start", "full-startup"],
            "testing": ["test", "integration-test", "evaluate"],
            "ui": ["ui-dashboard", "ui-command", "ui-worker"],
            "status": ["status", "startup-check", "daily-check"],
        }

        for group_name, cmd_names in func_groups.items():
            existing_cmds = [name for name in cmd_names if name in self.commands]
            if len(existing_cmds) > 2:
                redundancies.append(
                    ("similar_functionality", group_name, ", ".join(existing_cmds))
                )

        return redundancies

    def generate_optimal_makefile(self) -> str:
        """Generate an optimized Makefile structure"""
        streamlined = self.get_streamlined_commands()

        makefile_content = """.PHONY: help
.DEFAULT_GOAL := help

help: ## Show this help message
\t@echo "AI Safety Governance System - Command Reference"
\t@echo "=============================================="
\t@echo ""
\t@echo "Quick Start Commands:"
\t@awk 'BEGIN {FS = ":.*##"; category=""} /^## / {category=substr($$0,4)} /^[a-zA-Z_-]+:.*##/ {if(category=="Essential Quick Start") printf "  \\033[36m%-20s\\033[0m %s\\n", $$1, $$2}' $(MAKEFILE_LIST)
\t@echo ""
\t@echo "Daily Operations:"
\t@awk 'BEGIN {FS = ":.*##"; category=""} /^## / {category=substr($$0,4)} /^[a-zA-Z_-]+:.*##/ {if(category=="Daily Operations") printf "  \\033[32m%-20s\\033[0m %s\\n", $$1, $$2}' $(MAKEFILE_LIST)
\t@echo ""
\t@echo "System Management:"
\t@awk 'BEGIN {FS = ":.*##"; category=""} /^## / {category=substr($$0,4)} /^[a-zA-Z_-]+:.*##/ {if(category=="System Management") printf "  \\033[33m%-20s\\033[0m %s\\n", $$1, $$2}' $(MAKEFILE_LIST)
\t@echo ""
\t@echo "For more commands, run: make help-all"

help-all: ## Show all available commands
\t@echo "AI Safety Governance System - Complete Command Reference"
\t@echo "======================================================="
\t@awk 'BEGIN {FS = ":.*##"; category=""} /^## / {category=substr($$0,4); printf "\\n\\033[1m%s:\\033[0m\\n", category} /^[a-zA-Z_-]+:.*##/ {printf "  \\033[36m%-20s\\033[0m %s\\n", $$1, $$2}' $(MAKEFILE_LIST)

"""

        # Add streamlined categories
        for category, commands in streamlined.items():
            if not commands:
                continue

            makefile_content += f"\n## {category}\n"
            for cmd in commands:
                makefile_content += f"{cmd.name}: ## {cmd.description}\n"
                # Add command implementation (simplified)
                if cmd.name == "startup":
                    makefile_content += """\t@echo "🚀 システム起動中..."
\t@make declare-president || true
\t@make ai-org-start || true
\t@make memory-recall || true
\t@make integration-test || true
\t@echo "✅ システム起動完了"

"""
                elif cmd.name == "help":
                    makefile_content += """\t@make help

"""
                else:
                    makefile_content += f"\t@echo '🔧 {cmd.description} 実行中...'\n"
                    makefile_content += f"\t# TODO: Implement {cmd.name}\n\n"

        return makefile_content

    def analyze_commands(self) -> Dict[str, Any]:
        """Comprehensive command analysis"""
        analysis = {
            "total_commands": len(self.commands),
            "by_category": {cat: len(cmds) for cat, cmds in self.categories.items()},
            "by_frequency": {},
            "by_complexity": {},
            "essential_commands": [],
            "redundant_commands": self.detect_redundant_commands(),
            "streamlined_structure": self.get_streamlined_commands(),
        }

        # Frequency analysis
        freq_count = defaultdict(int)
        for cmd in self.commands.values():
            freq_count[cmd.frequency] += 1
        analysis["by_frequency"] = dict(freq_count)

        # Complexity analysis
        complexity_count = defaultdict(int)
        for cmd in self.commands.values():
            complexity_count[cmd.complexity] += 1
        analysis["by_complexity"] = dict(complexity_count)

        # Essential commands
        analysis["essential_commands"] = [
            cmd.name for cmd in self.commands.values() if cmd.essential
        ]

        return analysis

    def generate_user_guide(self) -> str:
        """Generate user-friendly command guide"""
        guide = """# 🎯 Command Usage Guide - AI Safety Governance System

## Quick Start (新規ユーザー向け)

### 1. 初回セットアップ
```bash
make startup          # 完全システム起動
make help            # コマンド一覧確認
```

### 2. 日常の使用
```bash
make declare-president    # セッション開始時（必須）
make ai-org-start        # AI組織起動
make integration-test    # システム確認
```

### 3. 問題発生時
```bash
make status              # システム状態確認
make cleanup            # システムクリーンアップ
make validate           # 構造検証
```

## コマンド分類

### 🚀 Essential Quick Start
必須コマンド - 基本操作に必要
"""

        streamlined = self.get_streamlined_commands()

        for category, commands in streamlined.items():
            if not commands:
                continue

            guide += f"\n### {category}\n"
            for cmd in commands:
                guide += f"- `make {cmd.name}` - {cmd.description}\n"

        guide += """
## 使用頻度別推奨

### 毎日使用
- `make startup` - システム起動
- `make declare-president` - セッション開始
- `make status` - 状態確認

### 週1回程度
- `make cleanup` - システムクリーンアップ
- `make integration-test` - 統合テスト
- `make evaluate` - システム評価

### 必要に応じて
- `make install` - 依存関係インストール
- `make setup-hooks` - Git フック設定
- `make template-init` - テンプレート初期化

## トラブルシューティング

### よくある問題と解決法
1. **PRESIDENT宣言失敗** → `make declare-president`
2. **AI組織起動失敗** → `make ai-org-start`
3. **データベース接続失敗** → `make db-connect`
4. **統合テスト失敗** → `make integration-test`

### 緊急時
```bash
make cleanup         # 全体クリーンアップ
make validate        # 構造検証
make startup         # システム再起動
```
"""

        return guide


def main():
    """Main function for command organization analysis"""
    print("🔧 Command Organizer - Streamlined Command Management")
    print("=" * 60)

    # Initialize organizer
    organizer = CommandOrganizer()

    # Analyze commands
    analysis = organizer.analyze_commands()

    print("📊 Command Analysis:")
    print(f"   Total Commands: {analysis['total_commands']}")
    print(f"   Categories: {len(analysis['by_category'])}")
    print(f"   Essential Commands: {len(analysis['essential_commands'])}")
    print(f"   Redundant Commands: {len(analysis['redundant_commands'])}")

    # Show category breakdown
    print("\n📋 By Category:")
    for category, count in analysis["by_category"].items():
        print(f"   {category}: {count} commands")

    # Show frequency breakdown
    print("\n⚡ By Frequency:")
    for freq, count in analysis["by_frequency"].items():
        print(f"   {freq}: {count} commands")

    # Show essential commands
    print("\n🎯 Essential Commands:")
    for cmd_name in analysis["essential_commands"]:
        print(f"   • {cmd_name}")

    # Show redundancies
    if analysis["redundant_commands"]:
        print("\n⚠️  Potential Redundancies:")
        for redundancy_type, desc, commands in analysis["redundant_commands"]:
            print(f"   {redundancy_type}: {desc} → {commands}")

    # Generate optimized structure
    print("\n📦 Streamlined Structure:")
    streamlined = analysis["streamlined_structure"]
    for category, commands in streamlined.items():
        if commands:
            print(f"   {category}: {len(commands)} commands")

    # Generate user guide
    guide = organizer.generate_user_guide()
    guide_file = "docs/COMMAND_USAGE_GUIDE.md"
    os.makedirs(os.path.dirname(guide_file), exist_ok=True)
    with open(guide_file, "w", encoding="utf-8") as f:
        f.write(guide)
    print(f"\n📚 User guide generated: {guide_file}")

    print("\n✅ Command organization analysis completed")


if __name__ == "__main__":
    main()
