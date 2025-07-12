#!/usr/bin/env python3
"""
📁 Directory Enforcer - ファイル作成時適切ディレクトリ強制システム
=========================================================

新しいファイル作成時に適切なディレクトリに配置することを強制し、
ファイル散乱を防ぐシステム
"""

import logging
import re
from enum import Enum
from pathlib import Path
from typing import Dict, Tuple


class FileType(Enum):
    """ファイルタイプ分類"""

    PYTHON_CODE = "python_code"
    DOCUMENTATION = "documentation"
    CONFIG = "config"
    TEST = "test"
    SCRIPT = "script"
    DATA = "data"
    LOG = "log"
    TEMP = "temp"
    UNKNOWN = "unknown"


class DirectoryEnforcer:
    """ディレクトリ強制システム"""

    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.logger = logging.getLogger(__name__)

        # ディレクトリマッピングルール
        self.directory_rules = {
            FileType.PYTHON_CODE: {
                "patterns": [r"\.py$", r"\.pyi$"],
                "directories": ["src/", "scripts/"],
                "subdirectory_rules": {
                    r".*test.*": "tests/",
                    r".*ai.*": "src/ai/",
                    r".*ui.*": "src/ui/",
                    r".*memory.*": "src/memory/",
                    r".*conductor.*": "src/conductor/",
                    r".*utils.*": "src/utils/",
                    r".*monitoring.*": "src/monitoring/",
                    r".*logging.*": "src/logging/",
                    r".*hooks.*": "scripts/hooks/",
                    r".*tools.*": "scripts/tools/",
                    r".*automation.*": "scripts/automation/",
                    r".*setup.*": "scripts/",
                    r".*config.*": "config/",
                },
            },
            FileType.DOCUMENTATION: {
                "patterns": [r"\.md$", r"\.rst$", r"\.txt$"],
                "directories": ["docs/"],
                "subdirectory_rules": {
                    r".*guide.*": "docs/02_guides/",
                    r".*concept.*": "docs/01_concepts/",
                    r".*example.*": "docs/03_examples/",
                    r".*reference.*": "docs/04_reference/",
                    r".*changelog.*": "docs/",
                    r".*readme.*": "docs/",
                    r".*index.*": "docs/",
                },
            },
            FileType.CONFIG: {
                "patterns": [r"\.json$", r"\.yaml$", r"\.yml$", r"\.toml$", r"\.ini$"],
                "directories": ["config/"],
                "subdirectory_rules": {
                    r".*docker.*": "config/docker/",
                    r".*cursor.*": "config/cursor/",
                    r".*claude.*": "config/",
                    r".*requirements.*": "config/",
                },
            },
            FileType.TEST: {
                "patterns": [r"test_.*\.py$", r".*_test\.py$"],
                "directories": ["tests/"],
                "subdirectory_rules": {
                    r".*integration.*": "tests/integration/",
                    r".*unit.*": "tests/unit/",
                    r".*e2e.*": "tests/e2e/",
                },
            },
            FileType.SCRIPT: {
                "patterns": [r"\.sh$", r"\.bash$", r"\.zsh$"],
                "directories": ["scripts/"],
                "subdirectory_rules": {
                    r".*setup.*": "scripts/",
                    r".*install.*": "scripts/",
                    r".*deploy.*": "scripts/",
                    r".*automation.*": "scripts/automation/",
                    r".*monitoring.*": "scripts/monitoring/",
                    r".*tools.*": "scripts/tools/",
                },
            },
            FileType.DATA: {
                "patterns": [r"\.csv$", r"\.json$", r"\.xml$", r"\.pkl$"],
                "directories": ["runtime/", "data/"],
                "subdirectory_rules": {
                    r".*log.*": "runtime/logs/",
                    r".*memory.*": "runtime/memory/",
                    r".*session.*": "runtime/sessions/",
                    r".*temp.*": "runtime/temp/",
                    r".*backup.*": "runtime/backups/",
                },
            },
            FileType.LOG: {
                "patterns": [r"\.log$", r"\.jsonl$"],
                "directories": ["runtime/logs/"],
                "subdirectory_rules": {
                    r".*error.*": "runtime/errors/",
                    r".*debug.*": "runtime/logs/debug/",
                    r".*audit.*": "runtime/logs/audit/",
                },
            },
            FileType.TEMP: {
                "patterns": [r"\.tmp$", r"\.temp$", r"temp_.*"],
                "directories": ["runtime/temp/"],
                "subdirectory_rules": {},
            },
        }

        # 禁止されたルートディレクトリファイル
        self.prohibited_root_files = {
            r"test_.*\.py$": "tests/",
            r".*_test\.py$": "tests/",
            r".*\.md$": "docs/",
            r".*config.*\.json$": "config/",
            r".*\.log$": "runtime/logs/",
            r".*\.tmp$": "runtime/temp/",
            r"setup.*\.py$": "scripts/",
            r"install.*\.py$": "scripts/",
        }

    def classify_file(self, filepath: str) -> FileType:
        """ファイルタイプを分類"""
        filename = Path(filepath).name.lower()

        for file_type, rules in self.directory_rules.items():
            for pattern in rules["patterns"]:
                if re.search(pattern, filename):
                    return file_type

        return FileType.UNKNOWN

    def get_recommended_directory(self, filepath: str) -> Tuple[str, str]:
        """推奨ディレクトリを取得"""
        file_type = self.classify_file(filepath)
        filename = Path(filepath).name.lower()

        if file_type == FileType.UNKNOWN:
            return "src/", "Unknown file type, defaulting to src/"

        rules = self.directory_rules[file_type]

        # サブディレクトリルールをチェック
        for pattern, directory in rules["subdirectory_rules"].items():
            if re.search(pattern, filename):
                return directory, f"Matched pattern: {pattern}"

        # デフォルトディレクトリ
        default_dir = rules["directories"][0]
        return default_dir, f"Default directory for {file_type.value}"

    def check_file_placement(self, filepath: str) -> Dict[str, any]:
        """ファイル配置の妥当性をチェック"""
        path = Path(filepath)

        # 絶対パスを相対パスに変換
        try:
            relative_path = path.relative_to(self.project_root)
        except ValueError:
            relative_path = path

        filename = path.name.lower()
        current_dir = str(relative_path.parent) + "/"

        # ルートディレクトリファイルチェック
        if str(relative_path.parent) == "." or str(relative_path.parent) == "":
            for pattern, suggested_dir in self.prohibited_root_files.items():
                if re.search(pattern, filename):
                    return {
                        "valid": False,
                        "current_location": current_dir,
                        "recommended_location": suggested_dir,
                        "reason": f"Root directory files matching '{pattern}' should be in {suggested_dir}",
                        "severity": "HIGH",
                    }

        # 推奨ディレクトリと比較
        recommended_dir, reason = self.get_recommended_directory(filepath)

        if not current_dir.startswith(recommended_dir):
            return {
                "valid": False,
                "current_location": current_dir,
                "recommended_location": recommended_dir,
                "reason": reason,
                "severity": "MEDIUM",
            }

        return {
            "valid": True,
            "current_location": current_dir,
            "recommended_location": recommended_dir,
            "reason": "File placement is appropriate",
            "severity": "LOW",
        }

    def enforce_file_placement(
        self, filepath: str, auto_move: bool = False
    ) -> Dict[str, any]:
        """ファイル配置を強制"""
        result = self.check_file_placement(filepath)

        if not result["valid"]:
            recommended_path = (
                Path(self.project_root)
                / result["recommended_location"]
                / Path(filepath).name
            )

            if auto_move:
                # 自動移動実行
                try:
                    recommended_path.parent.mkdir(parents=True, exist_ok=True)
                    Path(filepath).rename(recommended_path)

                    return {
                        "enforced": True,
                        "old_path": filepath,
                        "new_path": str(recommended_path),
                        "reason": result["reason"],
                        "action": "moved",
                    }

                except Exception as e:
                    return {
                        "enforced": False,
                        "error": str(e),
                        "reason": result["reason"],
                        "action": "failed",
                    }
            else:
                # 推奨のみ
                return {
                    "enforced": False,
                    "recommendation": str(recommended_path),
                    "reason": result["reason"],
                    "action": "recommend",
                }

        return {
            "enforced": True,
            "reason": "File placement is already correct",
            "action": "no_action_needed",
        }

    def validate_directory_structure(self) -> Dict[str, any]:
        """ディレクトリ構造全体を検証"""
        violations = []

        # 全ファイルをスキャン
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file() and not file_path.name.startswith("."):
                try:
                    relative_path = file_path.relative_to(self.project_root)
                    result = self.check_file_placement(str(relative_path))

                    if not result["valid"]:
                        violations.append(
                            {
                                "file": str(relative_path),
                                "current": result["current_location"],
                                "recommended": result["recommended_location"],
                                "reason": result["reason"],
                                "severity": result["severity"],
                            }
                        )

                except Exception as e:
                    self.logger.warning(f"Could not validate {file_path}: {e}")

        return {
            "total_files": len(list(self.project_root.rglob("*"))),
            "violations": violations,
            "violation_count": len(violations),
            "compliance_rate": (
                1 - len(violations) / max(1, len(list(self.project_root.rglob("*"))))
            )
            * 100,
        }

    def create_directory_structure(self):
        """推奨ディレクトリ構造を作成"""
        directories = [
            "src/ai/",
            "src/ui/",
            "src/memory/",
            "src/conductor/",
            "src/utils/",
            "src/monitoring/",
            "src/logging/",
            "docs/01_concepts/",
            "docs/02_guides/",
            "docs/03_examples/",
            "docs/04_reference/",
            "config/docker/",
            "config/cursor/",
            "scripts/hooks/",
            "scripts/tools/",
            "scripts/automation/",
            "tests/unit/",
            "tests/integration/",
            "tests/e2e/",
            "runtime/logs/",
            "runtime/memory/",
            "runtime/sessions/",
            "runtime/temp/",
            "runtime/backups/",
            "data/",
        ]

        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(parents=True, exist_ok=True)

            # .gitkeep作成
            gitkeep_path = dir_path / ".gitkeep"
            if not gitkeep_path.exists():
                gitkeep_path.touch()

        return {"created_directories": len(directories), "directories": directories}


def main():
    """メイン実行"""
    enforcer = DirectoryEnforcer()

    print("📁 Directory Enforcer - ファイル配置検証システム")
    print("=" * 50)

    # ディレクトリ構造作成
    print("\n🏗️ 推奨ディレクトリ構造作成中...")
    result = enforcer.create_directory_structure()
    print(f"✅ {result['created_directories']}個のディレクトリを作成/確認完了")

    # 全体検証
    print("\n🔍 プロジェクト全体のファイル配置検証中...")
    validation = enforcer.validate_directory_structure()

    print("📊 検証結果:")
    print(f"  - 総ファイル数: {validation['total_files']}")
    print(f"  - 違反ファイル数: {validation['violation_count']}")
    print(f"  - 準拠率: {validation['compliance_rate']:.1f}%")

    if validation["violations"]:
        print("\n⚠️ 配置違反ファイル:")
        for violation in validation["violations"][:10]:  # 最大10件表示
            print(f"  - {violation['file']}")
            print(f"    現在: {violation['current']}")
            print(f"    推奨: {violation['recommended']}")
            print(f"    理由: {violation['reason']}")
            print(f"    深刻度: {violation['severity']}")
            print()

    print("\n✅ Directory Enforcer実行完了")


if __name__ == "__main__":
    main()
