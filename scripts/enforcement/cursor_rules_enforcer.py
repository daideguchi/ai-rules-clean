#!/usr/bin/env python3
"""
Cursor Rules強制確認システム
===========================

セッション開始時とファイル作成時にCursor rulesの確認を強制する
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    import psycopg2
    import psycopg2.extras

    POSTGRESQL_AVAILABLE = True
except ImportError:
    POSTGRESQL_AVAILABLE = False


class CursorRulesEnforcer:
    """Cursor Rules強制確認システム"""

    def __init__(self):
        self.project_root = project_root
        self.cursor_rules_file = (
            self.project_root / "src" / "cursor-rules" / "globals.mdc"
        )
        self.verification_log = (
            self.project_root / "runtime" / "cursor_rules_verification.json"
        )
        self.session_file = self.project_root / "runtime" / "cursor_rules_session.json"

        # DB接続設定
        self.db_config = {
            "host": "localhost",
            "port": 5432,
            "database": "coding_rule2_ai",
            "user": "dd",
            "password": "",
        }

        # 重要ルール（必須確認項目）
        self.critical_rules = [
            "絶対禁止ルール",
            "PRESIDENT必須確認プロトコル",
            "Function-Based Grouping準拠",
            "5分検索ルール",
            "品質指標",
            "作業記録システム",
        ]

        self.ensure_directories()

    def ensure_directories(self):
        """必要ディレクトリの作成"""
        self.verification_log.parent.mkdir(parents=True, exist_ok=True)
        self.session_file.parent.mkdir(parents=True, exist_ok=True)

    def load_cursor_rules(self) -> Dict[str, any]:
        """Cursor rules読み込み"""
        if not self.cursor_rules_file.exists():
            return {
                "status": "error",
                "message": "Cursor rules file not found",
                "content": "",
            }

        try:
            with open(self.cursor_rules_file, encoding="utf-8") as f:
                content = f.read()

            # 重要ルールの存在確認
            missing_rules = []
            for rule in self.critical_rules:
                if rule not in content:
                    missing_rules.append(rule)

            return {
                "status": "success",
                "content": content,
                "line_count": len(content.split("\n")),
                "missing_rules": missing_rules,
                "file_path": str(self.cursor_rules_file),
            }

        except Exception as e:
            return {"status": "error", "message": str(e), "content": ""}

    def display_cursor_rules(self) -> bool:
        """Cursor rules表示"""
        rules_data = self.load_cursor_rules()

        if rules_data["status"] == "error":
            print(f"❌ Cursor rules読み込みエラー: {rules_data['message']}")
            return False

        print("📋 Cursor Rules確認 - globals.mdc")
        print("=" * 60)
        print(f"📄 ファイル: {rules_data['file_path']}")
        print(f"📊 行数: {rules_data['line_count']}")

        if rules_data["missing_rules"]:
            print(f"⚠️ 不足ルール: {', '.join(rules_data['missing_rules'])}")

        print("\n🚨 重要ルール抜粋:")
        print("-" * 40)

        lines = rules_data["content"].split("\n")
        for i, line in enumerate(lines):
            if any(rule in line for rule in self.critical_rules):
                print(f"{i + 1:3d}: {line}")

        return True

    def enforce_confirmation(self) -> bool:
        """確認強制実行"""
        print("\n🔴 Cursor Rules確認が必要です")
        print("=" * 50)

        if not self.display_cursor_rules():
            return False

        print("\n📋 確認必須項目:")
        for i, rule in enumerate(self.critical_rules, 1):
            print(f"  {i}. {rule}")

        print("\n🔴 以下のルールを理解し、遵守することを確認してください:")
        print("  - 推測報告禁止: 確認していないことは報告しない")
        print("  - 職務放棄禁止: 最後まで責任を持って完遂")
        print("  - 手抜き禁止: 全ての手順を確実に実行")
        print("  - 虚偽報告禁止: 事実のみを正確に報告")
        print("  - 5分検索ルール: 推測前に5分間の検索実行")
        print("  - 品質指標: 推測回答率0%、手順遵守率100%")

        # 非対話環境での自動確認
        if not os.isatty(sys.stdin.fileno()):
            print("\n⚠️ 非対話環境検出 - 自動確認モード")
            confirmation = "yes"
        else:
            confirmation = (
                input(
                    "\n✅ 上記すべてのルールを理解し、遵守することを確認しますか? (yes/no): "
                )
                .strip()
                .lower()
            )

        if confirmation in ["yes", "y"]:
            self.record_confirmation()
            print("\n✅ Cursor Rules確認完了！")
            return True
        else:
            print("\n❌ Cursor Rules確認が必要です。作業を開始できません。")
            return False

    def record_confirmation(self):
        """確認記録"""
        session_data = {
            "timestamp": datetime.now().isoformat(),
            "cursor_rules_confirmed": True,
            "file_path": str(self.cursor_rules_file),
            "session_id": os.environ.get("CLAUDE_SESSION_ID", "unknown"),
            "rules_version": "1.0",
        }

        # セッション記録
        with open(self.session_file, "w") as f:
            json.dump(session_data, f, indent=2)

        # 確認ログ記録
        if self.verification_log.exists():
            with open(self.verification_log) as f:
                log_data = json.load(f)
        else:
            log_data = {"confirmations": []}

        log_data["confirmations"].append(session_data)

        # 最新100件のみ保持
        if len(log_data["confirmations"]) > 100:
            log_data["confirmations"] = log_data["confirmations"][-100:]

        with open(self.verification_log, "w") as f:
            json.dump(log_data, f, indent=2)

        # PostgreSQL記録
        if POSTGRESQL_AVAILABLE:
            self.log_to_postgresql(session_data)

    def log_to_postgresql(self, session_data: Dict):
        """PostgreSQLログ記録"""
        try:
            with psycopg2.connect(**self.db_config) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT log_system_event(
                            'cursor_rules_confirmed',
                            %s::jsonb,
                            'info',
                            %s,
                            'cursor_rules_enforcer.py'
                        )
                    """,
                        (json.dumps(session_data), session_data["session_id"]),
                    )

                    conn.commit()
        except Exception:
            pass  # ログ記録失敗は非致命的

    def check_session_confirmation(self) -> bool:
        """セッション確認状況チェック"""
        if not self.session_file.exists():
            return False

        try:
            with open(self.session_file) as f:
                session_data = json.load(f)

            # 確認済みかチェック
            if not session_data.get("cursor_rules_confirmed", False):
                return False

            # 同じセッションかチェック（簡易版）
            timestamp = datetime.fromisoformat(session_data["timestamp"])
            elapsed = datetime.now() - timestamp

            # 24時間以内の確認は有効
            if elapsed.total_seconds() < 24 * 60 * 60:
                return True

            return False

        except Exception:
            return False

    def get_confirmation_stats(self) -> Dict:
        """確認統計取得"""
        stats = {
            "total_confirmations": 0,
            "last_confirmation": None,
            "session_confirmed": False,
        }

        if self.verification_log.exists():
            try:
                with open(self.verification_log) as f:
                    log_data = json.load(f)

                confirmations = log_data.get("confirmations", [])
                stats["total_confirmations"] = len(confirmations)

                if confirmations:
                    stats["last_confirmation"] = confirmations[-1]["timestamp"]

            except Exception:
                pass

        stats["session_confirmed"] = self.check_session_confirmation()

        return stats

    def run_enforcement(self) -> bool:
        """強制確認実行"""
        print("🔒 Cursor Rules強制確認システム")
        print("=" * 50)

        # 既存確認状況チェック
        if self.check_session_confirmation():
            print("✅ このセッションでは既にCursor Rules確認済みです")
            return True

        # 統計表示
        stats = self.get_confirmation_stats()
        print(f"📊 過去の確認回数: {stats['total_confirmations']}")
        if stats["last_confirmation"]:
            print(f"📅 最後の確認: {stats['last_confirmation']}")

        # 強制確認実行
        return self.enforce_confirmation()


def main():
    """メイン実行"""
    enforcer = CursorRulesEnforcer()

    try:
        result = enforcer.run_enforcement()

        if result:
            print("\n🎉 Cursor Rules確認完了！")
            print("💡 作業を開始できます")
        else:
            print("\n❌ Cursor Rules確認が必要です")
            print("💡 作業を開始する前に確認してください")
            return 1

    except Exception as e:
        print(f"\n❌ 確認中にエラーが発生: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
