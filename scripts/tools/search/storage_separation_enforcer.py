#!/usr/bin/env python3
"""
Storage Separation Enforcer
データベースvsローカルストレージの厳格分離システム
"""

import json
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class StorageSeparationEnforcer:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.database_dir = self.project_root / "src/memory/persistent-learning"
        self.local_dir = self.project_root / "runtime"
        self.temp_dir = self.project_root / "data/local"

        self.separation_rules = self.load_separation_rules()
        self.misplaced_files = []

    def load_separation_rules(self) -> Dict:
        """分離ルール定義"""
        return {
            "database_storage": {
                "path": "src/memory/persistent-learning/",
                "description": "Persistent AI learning data",
                "file_patterns": [
                    "*mistakes-database.json",
                    "*learning-patterns.json",
                    "*ai-behavior-model.json",
                    "*long-term-memory.json",
                    "*behavioral-improvements.json",
                ],
                "criteria": [
                    "Cross-session persistence required",
                    "AI learning and improvement data",
                    "Mistake prevention patterns",
                    "Long-term behavioral changes",
                    "Training data and model updates",
                ],
            },
            "local_storage": {
                "path": "runtime/",
                "description": "Session-specific temporary data",
                "file_patterns": [
                    "*session*.json",
                    "*temp*.json",
                    "*debug*.log",
                    "*api*.log",
                    "*current*.json",
                    "*state*.json",
                ],
                "criteria": [
                    "Session-specific data",
                    "Temporary processing files",
                    "Debug and log information",
                    "Current state snapshots",
                    "API interaction logs",
                ],
            },
            "temp_storage": {
                "path": "data/local/",
                "description": "Temporary working files",
                "file_patterns": ["*temp*", "*cache*", "*working*", "*scratch*"],
                "criteria": [
                    "Temporary working files",
                    "Cache data",
                    "Disposable content",
                    "Short-term scratch space",
                ],
            },
        }

    def analyze_file_placement(self, file_path: Path) -> Dict:
        """ファイル配置の分析"""
        analysis = {
            "file_path": str(file_path),
            "current_location": self.get_location_type(file_path),
            "recommended_location": None,
            "placement_score": 0,
            "reasons": [],
        }

        file_name = file_path.name.lower()

        # Content-based analysis
        try:
            if file_path.suffix in [".json", ".jsonl"]:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                # Database storage indicators
                if any(
                    keyword in content
                    for keyword in [
                        "mistakes",
                        "learning",
                        "patterns",
                        "behavioral",
                        "persistent",
                        "cross-session",
                        "prevention",
                    ]
                ):
                    analysis["recommended_location"] = "database_storage"
                    analysis["placement_score"] = 90
                    analysis["reasons"].append(
                        "Contains AI learning/mistake prevention data"
                    )

                # Local storage indicators
                elif any(
                    keyword in content
                    for keyword in [
                        "session_id",
                        "timestamp",
                        "current",
                        "temp",
                        "debug",
                        "api_log",
                        "state",
                    ]
                ):
                    analysis["recommended_location"] = "local_storage"
                    analysis["placement_score"] = 85
                    analysis["reasons"].append("Contains session-specific data")

                # Temp storage indicators
                elif any(
                    keyword in content
                    for keyword in ["cache", "temporary", "working", "scratch"]
                ):
                    analysis["recommended_location"] = "temp_storage"
                    analysis["placement_score"] = 80
                    analysis["reasons"].append("Contains temporary working data")

        except Exception:
            # Fallback to filename analysis
            pass

        # Filename-based analysis
        if not analysis["recommended_location"]:
            for storage_type, rules in self.separation_rules.items():
                for pattern in rules["file_patterns"]:
                    import fnmatch

                    if fnmatch.fnmatch(file_name, pattern):
                        analysis["recommended_location"] = storage_type
                        analysis["placement_score"] = 70
                        analysis["reasons"].append(
                            f"Filename matches {storage_type} pattern"
                        )
                        break

        # Default classification
        if not analysis["recommended_location"]:
            analysis["recommended_location"] = "local_storage"
            analysis["placement_score"] = 50
            analysis["reasons"].append("Default classification")

        return analysis

    def get_location_type(self, file_path: Path) -> str:
        """ファイルの現在の場所タイプを取得"""
        relative_path = file_path.relative_to(self.project_root)

        if str(relative_path).startswith("src/memory/persistent-learning"):
            return "database_storage"
        elif str(relative_path).startswith("runtime"):
            return "local_storage"
        elif str(relative_path).startswith("data/local"):
            return "temp_storage"
        else:
            return "unknown"

    def find_misplaced_files(self) -> List[Dict]:
        """配置ミスファイルの検出"""
        misplaced = []

        # JSON/JSONL files in various locations
        search_paths = [
            self.project_root / "src/memory",
            self.project_root / "src/runtime",
            self.project_root / "runtime",
            self.project_root / "data",
        ]

        for search_path in search_paths:
            if search_path.exists():
                for file_path in search_path.rglob("*.json*"):
                    analysis = self.analyze_file_placement(file_path)

                    if analysis["current_location"] != analysis["recommended_location"]:
                        misplaced.append(
                            {
                                "file": file_path,
                                "current": analysis["current_location"],
                                "recommended": analysis["recommended_location"],
                                "score": analysis["placement_score"],
                                "reasons": analysis["reasons"],
                            }
                        )

        return sorted(misplaced, key=lambda x: x["score"], reverse=True)

    def create_migration_plan(self) -> Dict:
        """移行計画の作成"""
        misplaced_files = self.find_misplaced_files()

        migration_plan = {
            "timestamp": datetime.now().isoformat(),
            "total_files": len(misplaced_files),
            "migrations": [],
            "estimated_time": len(misplaced_files) * 2,  # 2 seconds per file
            "safety_backups": True,
        }

        for item in misplaced_files:
            file_path = item["file"]
            recommended = item["recommended"]

            # Determine target path
            target_base = self.separation_rules[recommended]["path"]
            target_path = self.project_root / target_base / file_path.name

            migration_plan["migrations"].append(
                {
                    "source": str(file_path),
                    "target": str(target_path),
                    "type": recommended,
                    "score": item["score"],
                    "reasons": item["reasons"],
                    "backup_path": str(file_path) + ".backup",
                }
            )

        return migration_plan

    def execute_migration(self, migration_plan: Dict, dry_run: bool = True) -> Dict:
        """移行の実行"""
        execution_result = {
            "timestamp": datetime.now().isoformat(),
            "dry_run": dry_run,
            "successful_migrations": 0,
            "failed_migrations": 0,
            "errors": [],
            "completed_migrations": [],
        }

        for migration in migration_plan["migrations"]:
            try:
                source_path = Path(migration["source"])
                target_path = Path(migration["target"])
                backup_path = Path(migration["backup_path"])

                if not dry_run:
                    # Create backup
                    shutil.copy2(source_path, backup_path)

                    # Ensure target directory exists
                    target_path.parent.mkdir(parents=True, exist_ok=True)

                    # Move file
                    shutil.move(source_path, target_path)

                execution_result["successful_migrations"] += 1
                execution_result["completed_migrations"].append(
                    {
                        "file": migration["source"],
                        "new_location": migration["target"],
                        "type": migration["type"],
                    }
                )

            except Exception as e:
                execution_result["failed_migrations"] += 1
                execution_result["errors"].append(
                    {"file": migration["source"], "error": str(e)}
                )

        return execution_result

    def create_enforcement_rules(self) -> str:
        """強制ルールの作成"""
        rules_content = f"""# Storage Separation Enforcement Rules

## Database Storage: {self.separation_rules["database_storage"]["path"]}
**Purpose:** {self.separation_rules["database_storage"]["description"]}

**Criteria:**
{chr(10).join(f"- {criterion}" for criterion in self.separation_rules["database_storage"]["criteria"])}

**File Patterns:**
{chr(10).join(f"- {pattern}" for pattern in self.separation_rules["database_storage"]["file_patterns"])}

## Local Storage: {self.separation_rules["local_storage"]["path"]}
**Purpose:** {self.separation_rules["local_storage"]["description"]}

**Criteria:**
{chr(10).join(f"- {criterion}" for criterion in self.separation_rules["local_storage"]["criteria"])}

**File Patterns:**
{chr(10).join(f"- {pattern}" for pattern in self.separation_rules["local_storage"]["file_patterns"])}

## Temp Storage: {self.separation_rules["temp_storage"]["path"]}
**Purpose:** {self.separation_rules["temp_storage"]["description"]}

**Criteria:**
{chr(10).join(f"- {criterion}" for criterion in self.separation_rules["temp_storage"]["criteria"])}

**File Patterns:**
{chr(10).join(f"- {pattern}" for pattern in self.separation_rules["temp_storage"]["file_patterns"])}

## Enforcement Actions
1. Automatic detection of misplaced files
2. Migration plan generation
3. Safe file relocation with backups
4. Prevention of future violations
"""
        return rules_content

    def generate_report(self) -> str:
        """分離状況レポート生成"""
        misplaced_files = self.find_misplaced_files()
        migration_plan = self.create_migration_plan()

        report = f"""
## 📊 Database vs Local Storage Separation Analysis

**分析時刻:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**検出された配置ミス:** {len(misplaced_files)}件

### 🚨 配置ミスファイル詳細:

"""

        for i, item in enumerate(misplaced_files[:10], 1):  # Top 10
            report += f"""
**{i}. {item["file"].name}**
- 現在の場所: {item["current"]}
- 推奨場所: {item["recommended"]}
- スコア: {item["score"]}/100
- 理由: {", ".join(item["reasons"])}
"""

        if len(misplaced_files) > 10:
            report += (
                f"\n*他 {len(misplaced_files) - 10}件のファイルも検出されました*\n"
            )

        report += f"""

### 📋 推奨移行プラン:
- 移行対象ファイル数: {migration_plan["total_files"]}
- 推定実行時間: {migration_plan["estimated_time"]}秒
- バックアップ作成: {migration_plan["safety_backups"]}

### 🛠️ 実行コマンド:
```bash
# ドライラン実行
python3 scripts/utilities/storage_separation_enforcer.py --dry-run

# 実際の移行実行
python3 scripts/utilities/storage_separation_enforcer.py --execute
```
"""

        return report.strip()


def main():
    """メイン処理"""
    enforcer = StorageSeparationEnforcer()

    if "--dry-run" in sys.argv:
        migration_plan = enforcer.create_migration_plan()
        result = enforcer.execute_migration(migration_plan, dry_run=True)
        print("【ドライラン実行結果】")
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif "--execute" in sys.argv:
        migration_plan = enforcer.create_migration_plan()
        result = enforcer.execute_migration(migration_plan, dry_run=False)
        print("【移行実行結果】")
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif "--rules" in sys.argv:
        rules = enforcer.create_enforcement_rules()
        print(rules)

    else:
        report = enforcer.generate_report()
        print(report)


if __name__ == "__main__":
    main()
