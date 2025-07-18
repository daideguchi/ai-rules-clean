#!/usr/bin/env python3
"""
ファイル作成ルール強制システム
============================

Pythonファイル量産防止のための厳格な作成ルールと強制システム

【絶対禁止事項】
1. 重複機能のファイル作成
2. 一時的・実験的ファイルの残置
3. 機能分離の過度な細分化
4. テストファイルの本番混在
5. 設定ファイルの分散

【強制ルール】
1. 新規ファイル作成前の重複チェック必須
2. 機能統合可能性の検証必須
3. ファイル作成理由の明文化必須
4. 定期的な不要ファイル削除必須
5. 総ファイル数上限の厳守必須
"""

import hashlib
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# PostgreSQL connection for logging
try:
    import psycopg2
    import psycopg2.extras

    POSTGRESQL_AVAILABLE = True
except ImportError:
    POSTGRESQL_AVAILABLE = False


class FileCreationRules:
    """ファイル作成ルール強制システム"""

    def __init__(self):
        self.project_root = project_root
        self.rules_file = self.project_root / "runtime" / "file_creation_rules.json"
        self.violation_log = (
            self.project_root / "runtime" / "file_creation_violations.json"
        )
        self.allowed_extensions = {
            ".py",
            ".md",
            ".json",
            ".yaml",
            ".yml",
            ".txt",
            ".sh",
            ".sql",
        }

        # 現在のファイル数制限
        self.max_files = {
            "python": 500,  # 現在346個 → 500個上限
            "markdown": 350,  # 現在327個 → 350個上限
            "total": 1000,  # 全体1000個上限
        }

        # 必須構造
        self.required_structure = {
            "scripts/": {
                "allowed_subdirs": [
                    "automation",
                    "enforcement",
                    "hooks",
                    "maintenance",
                    "setup",
                    "system",
                    "tools",
                ],
                "max_files_per_dir": 20,
                "description": "システムスクリプト",
            },
            "src/": {
                "allowed_subdirs": [
                    "ai",
                    "conductor",
                    "enforcement",
                    "memory",
                    "orchestrator",
                    "session_management",
                ],
                "max_files_per_dir": 30,
                "description": "メインソースコード",
            },
            "tests/": {
                "allowed_subdirs": ["integration", "unit"],
                "max_files_per_dir": 50,
                "description": "テストコード",
            },
            "docs/": {
                "allowed_subdirs": ["api", "guides", "reference", "setup"],
                "max_files_per_dir": 100,
                "description": "ドキュメント",
            },
            "config/": {
                "allowed_subdirs": ["n8n", "supabase"],
                "max_files_per_dir": 10,
                "description": "設定ファイル",
            },
        }

        # 禁止パターン
        self.forbidden_patterns = [
            r".*_test\.py$",  # テストファイル（testsディレクトリ以外）
            r".*_backup\.py$",  # バックアップファイル
            r".*_old\.py$",  # 古いファイル
            r".*_temp\.py$",  # 一時ファイル
            r".*_debug\.py$",  # デバッグファイル
            r".*_experiment\.py$",  # 実験ファイル
            r".*_draft\.py$",  # 下書きファイル
            r".*_copy\.py$",  # コピーファイル
            r".*_v\d+\.py$",  # バージョン番号付きファイル
            r".*_final\.py$",  # 最終版ファイル
            r".*_ultimate\.py$",  # 究極版ファイル
            r".*_hybrid\.py$",  # ハイブリッドファイル
            r".*_complete\.py$",  # 完全版ファイル
            r".*_simple\.py$",  # シンプル版ファイル
            r".*_quick\.py$",  # クイック版ファイル
            r".*_auto\.py$",  # 自動版ファイル
            r".*_manual\.py$",  # 手動版ファイル
            r".*_fix\.py$",  # 修正版ファイル
            r".*_solution\.py$",  # ソリューションファイル
            r".*_setup\.py$",  # セットアップファイル（setup.pyを除く）
        ]

        # DB接続設定
        self.db_config = {
            "host": "localhost",
            "port": 5432,
            "database": "coding_rule2_ai",
            "user": "dd",
            "password": "",
        }

        self.initialize_rules()

    def initialize_rules(self):
        """ルールファイル初期化"""
        self.rules_file.parent.mkdir(parents=True, exist_ok=True)
        self.violation_log.parent.mkdir(parents=True, exist_ok=True)

        if not self.rules_file.exists():
            rules_data = {
                "version": "1.0",
                "created_at": datetime.now().isoformat(),
                "rules": {
                    "max_files": self.max_files,
                    "required_structure": self.required_structure,
                    "forbidden_patterns": self.forbidden_patterns,
                    "allowed_extensions": list(self.allowed_extensions),
                },
                "enforcement_level": "strict",
                "auto_delete": True,
            }

            with open(self.rules_file, "w") as f:
                json.dump(rules_data, f, indent=2)

    def check_file_creation(
        self, file_path: str, content: str = "", reason: str = ""
    ) -> Tuple[bool, List[str]]:
        """ファイル作成チェック"""
        violations = []
        file_path = Path(file_path)

        # 1. 拡張子チェック
        if file_path.suffix not in self.allowed_extensions:
            violations.append(f"禁止拡張子: {file_path.suffix}")

        # 2. 禁止パターンチェック
        for pattern in self.forbidden_patterns:
            if re.match(pattern, file_path.name):
                violations.append(f"禁止パターン: {pattern}")

        # 3. 構造チェック
        if not self._check_directory_structure(file_path):
            violations.append("不正なディレクトリ構造")

        # 4. 重複チェック
        duplicates = self._check_duplicates(file_path, content)
        if duplicates:
            violations.append(f"重複ファイル: {', '.join(duplicates)}")

        # 5. ファイル数制限チェック
        if not self._check_file_limits():
            violations.append("ファイル数制限超過")

        # 6. 必要性チェック
        if not reason:
            violations.append("作成理由が未記載")

        # 違反ログ記録
        if violations:
            self._log_violation(file_path, violations, reason)

        return len(violations) == 0, violations

    def _check_directory_structure(self, file_path: Path) -> bool:
        """ディレクトリ構造チェック"""
        str(file_path)

        # プロジェクトルートからの相対パス
        try:
            rel_path = file_path.relative_to(self.project_root)
        except ValueError:
            return False

        # 第1階層のディレクトリをチェック
        parts = rel_path.parts
        if len(parts) == 0:
            return False

        first_dir = parts[0]

        # 許可されたトップレベルディレクトリかチェック
        if first_dir not in self.required_structure:
            return False

        # サブディレクトリ制限チェック
        if len(parts) > 1:
            sub_dir = parts[1]
            allowed_subdirs = self.required_structure[first_dir]["allowed_subdirs"]
            if sub_dir not in allowed_subdirs:
                return False

        return True

    def _check_duplicates(self, file_path: Path, content: str) -> List[str]:
        """重複ファイルチェック"""
        duplicates = []

        if not content:
            return duplicates

        # 内容のハッシュ化
        content_hash = hashlib.md5(content.encode()).hexdigest()

        # 同じ拡張子のファイルをチェック
        for existing_file in self.project_root.rglob(f"*{file_path.suffix}"):
            if existing_file == file_path:
                continue

            try:
                with open(existing_file, encoding="utf-8") as f:
                    existing_content = f.read()

                existing_hash = hashlib.md5(existing_content.encode()).hexdigest()

                # 完全一致または類似度チェック
                if content_hash == existing_hash:
                    duplicates.append(str(existing_file))
                elif self._calculate_similarity(content, existing_content) > 0.8:
                    duplicates.append(str(existing_file))

            except Exception:
                continue

        return duplicates

    def _calculate_similarity(self, content1: str, content2: str) -> float:
        """内容の類似度計算"""
        # 簡易的な類似度計算（実際にはより精密な計算が必要）
        lines1 = set(content1.split("\n"))
        lines2 = set(content2.split("\n"))

        if not lines1 or not lines2:
            return 0.0

        intersection = len(lines1.intersection(lines2))
        union = len(lines1.union(lines2))

        return intersection / union if union > 0 else 0.0

    def _check_file_limits(self) -> bool:
        """ファイル数制限チェック"""
        current_counts = self.get_current_file_counts()

        # Python ファイル数チェック
        if current_counts["python"] >= self.max_files["python"]:
            return False

        # Markdown ファイル数チェック
        if current_counts["markdown"] >= self.max_files["markdown"]:
            return False

        # 総ファイル数チェック
        if current_counts["total"] >= self.max_files["total"]:
            return False

        return True

    def get_current_file_counts(self) -> Dict[str, int]:
        """現在のファイル数取得"""
        python_count = len(list(self.project_root.rglob("*.py")))
        markdown_count = len(list(self.project_root.rglob("*.md")))
        total_count = python_count + markdown_count

        return {
            "python": python_count,
            "markdown": markdown_count,
            "total": total_count,
        }

    def _log_violation(self, file_path: Path, violations: List[str], reason: str):
        """違反ログ記録"""
        violation_entry = {
            "timestamp": datetime.now().isoformat(),
            "file_path": str(file_path),
            "violations": violations,
            "reason": reason,
            "session_id": os.environ.get("CLAUDE_SESSION_ID", "unknown"),
        }

        # ファイルに記録
        if self.violation_log.exists():
            with open(self.violation_log) as f:
                log_data = json.load(f)
        else:
            log_data = {"violations": []}

        log_data["violations"].append(violation_entry)

        with open(self.violation_log, "w") as f:
            json.dump(log_data, f, indent=2)

        # PostgreSQL にも記録
        if POSTGRESQL_AVAILABLE:
            self._log_to_postgresql(violation_entry)

    def _log_to_postgresql(self, violation_entry: Dict):
        """PostgreSQL に違反ログ記録"""
        try:
            with psycopg2.connect(**self.db_config) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT log_system_event(
                            'file_creation_violation',
                            %s::jsonb,
                            'warning',
                            %s,
                            'file_creation_rules.py'
                        )
                    """,
                        (json.dumps(violation_entry), violation_entry["session_id"]),
                    )

                    conn.commit()
        except Exception:
            pass  # ログ記録失敗は非致命的

    def cleanup_violations(self) -> Dict[str, int]:
        """違反ファイルクリーンアップ"""
        cleaned_count = 0

        for file_path in self.project_root.rglob("*.py"):
            file_name = file_path.name

            # 禁止パターンチェック
            for pattern in self.forbidden_patterns:
                if re.match(pattern, file_name):
                    try:
                        file_path.unlink()
                        cleaned_count += 1
                        print(f"🗑️ 削除: {file_path}")
                    except Exception as e:
                        print(f"❌ 削除失敗 {file_path}: {e}")
                    break

        return {"cleaned_files": cleaned_count}

    def generate_report(self) -> Dict:
        """ファイル作成ルール報告書生成"""
        current_counts = self.get_current_file_counts()

        report = {
            "timestamp": datetime.now().isoformat(),
            "file_counts": current_counts,
            "limits": self.max_files,
            "compliance": {
                "python": current_counts["python"] < self.max_files["python"],
                "markdown": current_counts["markdown"] < self.max_files["markdown"],
                "total": current_counts["total"] < self.max_files["total"],
            },
            "violations": [],
        }

        # 違反ログ読み込み
        if self.violation_log.exists():
            with open(self.violation_log) as f:
                log_data = json.load(f)
                report["violations"] = log_data.get("violations", [])

        return report

    def enforce_rules(self) -> Dict:
        """ルール強制実行"""
        print("🚨 ファイル作成ルール強制実行開始")
        print("=" * 50)

        # 現在のファイル数確認
        current_counts = self.get_current_file_counts()
        print("📊 現在のファイル数:")
        print(f"  Python: {current_counts['python']}/{self.max_files['python']}")
        print(f"  Markdown: {current_counts['markdown']}/{self.max_files['markdown']}")
        print(f"  Total: {current_counts['total']}/{self.max_files['total']}")

        # 違反ファイルクリーンアップ
        cleanup_result = self.cleanup_violations()
        print(f"🗑️ 違反ファイル削除: {cleanup_result['cleaned_files']}件")

        # 更新後のファイル数確認
        updated_counts = self.get_current_file_counts()
        print("📊 更新後のファイル数:")
        print(f"  Python: {updated_counts['python']}/{self.max_files['python']}")
        print(f"  Markdown: {updated_counts['markdown']}/{self.max_files['markdown']}")
        print(f"  Total: {updated_counts['total']}/{self.max_files['total']}")

        # 報告書生成
        report = self.generate_report()
        report_file = self.project_root / "runtime" / "file_creation_rules_report.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        print(f"📝 報告書生成: {report_file}")

        return {
            "enforcement_completed": True,
            "files_cleaned": cleanup_result["cleaned_files"],
            "current_counts": updated_counts,
            "compliance_status": all(report["compliance"].values()),
            "report_file": str(report_file),
        }


def main():
    """メイン実行"""
    rules = FileCreationRules()

    try:
        result = rules.enforce_rules()

        if result["compliance_status"]:
            print("\n✅ ファイル作成ルール適合")
            print("💡 今後のファイル作成は厳格にチェックされます")
        else:
            print("\n⚠️ ファイル数制限に近づいています")
            print("🚨 新規ファイル作成を控えてください")

        print("\n🎉 ファイル作成ルール強制システム稼働開始！")

    except Exception as e:
        print(f"\n❌ ルール強制中にエラーが発生: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
