#!/usr/bin/env python3
"""
ログファイルのSupabase移行スクリプト
=====================================

ローカルログファイルをSupabaseのai_performance_logテーブルに移行し、
ログファイルを削除してストレージを節約する
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from supabase import Client, create_client
except ImportError as e:
    print(f"❌ Required packages not installed: {e}")
    print("Run: pip install supabase")
    sys.exit(1)


class LogMigration:
    """ログファイルのSupabase移行"""

    def __init__(self):
        self.project_root = project_root
        self.supabase_url = "http://127.0.0.1:54321"
        self.supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0"
        self.supabase: Optional[Client] = None
        self.migrated_logs = []

    def connect_supabase(self) -> bool:
        """Supabaseに接続"""
        try:
            self.supabase = create_client(self.supabase_url, self.supabase_key)
            print("✅ Supabase接続成功")
            return True
        except Exception as e:
            print(f"❌ Supabase接続失敗: {e}")
            return False

    def find_log_files(self) -> List[Path]:
        """ログファイルを検索"""
        log_files = []

        # runtime/logs/
        runtime_logs = self.project_root / "runtime" / "logs"
        if runtime_logs.exists():
            log_files.extend(runtime_logs.glob("*.log"))

        # runtime/直下
        runtime_dir = self.project_root / "runtime"
        if runtime_dir.exists():
            log_files.extend(runtime_dir.glob("*.log"))

        # logs/
        logs_dir = self.project_root / "logs"
        if logs_dir.exists():
            log_files.extend(logs_dir.glob("*.log"))

        # 圧縮ログ
        if runtime_logs.exists():
            log_files.extend(runtime_logs.glob("*.log.gz"))

        return sorted(log_files)

    def parse_log_entry(self, log_path: Path, line: str) -> Optional[Dict]:
        """ログエントリを解析"""
        try:
            # JSON形式のログを試す
            if line.strip().startswith("{"):
                data = json.loads(line.strip())
                return {
                    "session_id": data.get("session_id", "unknown"),
                    "timestamp": data.get("timestamp", datetime.now().isoformat()),
                    "task_success": data.get("success", False),
                    "execution_time": data.get("execution_time", 0),
                    "tool_calls_count": data.get("tool_calls_count", 0),
                    "tool_calls": data.get("tool_calls", []),
                    "error_count": data.get("error_count", 0),
                    "thinking_tag_used": data.get("thinking_tag_used", False),
                    "todo_tracking": data.get("todo_tracking", False),
                    "task_complexity": data.get("task_complexity", "simple"),
                    "learning_score": data.get("learning_score", 0),
                    "success_patterns": data.get("success_patterns", []),
                    "failure_patterns": data.get("failure_patterns", []),
                    "user_feedback": data.get("user_feedback", ""),
                    "log_source": str(log_path.name),
                }

            # 一般的なログ形式を解析
            timestamp_match = re.search(
                r"(\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2})", line
            )
            timestamp = (
                timestamp_match.group(1)
                if timestamp_match
                else datetime.now().isoformat()
            )

            # エラーかどうかを判定
            is_error = any(
                keyword in line.lower()
                for keyword in ["error", "failed", "exception", "traceback"]
            )

            # 成功かどうかを判定
            is_success = any(
                keyword in line.lower()
                for keyword in ["success", "completed", "done", "✅"]
            )

            return {
                "session_id": f"log_migration_{log_path.stem}",
                "timestamp": timestamp,
                "task_success": is_success and not is_error,
                "execution_time": 0,
                "tool_calls_count": 0,
                "tool_calls": [],
                "error_count": 1 if is_error else 0,
                "thinking_tag_used": "<thinking>" in line,
                "todo_tracking": "todo" in line.lower(),
                "task_complexity": "simple",
                "learning_score": 0,
                "success_patterns": [],
                "failure_patterns": [],
                "user_feedback": line.strip()[:500],  # 最初の500文字
                "log_source": str(log_path.name),
            }

        except Exception as e:
            print(f"⚠️ ログ解析エラー {log_path}: {e}")
            return None

    def migrate_log_file(self, log_path: Path) -> int:
        """個別ログファイルの移行"""
        migrated_count = 0

        try:
            # 圧縮ファイルの処理
            if log_path.suffix == ".gz":
                import gzip

                with gzip.open(log_path, "rt", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()
            else:
                with open(log_path, encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()

            batch_data = []
            for line in lines:
                if line.strip():
                    entry = self.parse_log_entry(log_path, line)
                    if entry:
                        batch_data.append(entry)

                        # バッチ処理（100件ずつ）
                        if len(batch_data) >= 100:
                            if self.insert_batch(batch_data):
                                migrated_count += len(batch_data)
                            batch_data = []

            # 残りのデータを処理
            if batch_data:
                if self.insert_batch(batch_data):
                    migrated_count += len(batch_data)

            print(f"✅ {log_path.name}: {migrated_count}件移行完了")
            return migrated_count

        except Exception as e:
            print(f"❌ {log_path.name}: 移行失敗 - {e}")
            return 0

    def insert_batch(self, batch_data: List[Dict]) -> bool:
        """バッチデータをSupabaseに挿入"""
        try:
            self.supabase.table("ai_performance_log").insert(batch_data).execute()
            return True
        except Exception as e:
            print(f"❌ バッチ挿入失敗: {e}")
            return False

    def cleanup_log_files(self, log_files: List[Path]) -> int:
        """ログファイルの削除"""
        cleaned_count = 0

        for log_path in log_files:
            try:
                log_path.unlink()
                print(f"🗑️ 削除: {log_path.name}")
                cleaned_count += 1
            except Exception as e:
                print(f"❌ 削除失敗 {log_path.name}: {e}")

        return cleaned_count

    def run_migration(self) -> Dict[str, int]:
        """移行実行"""
        print("🚀 ログファイルSupabase移行開始")
        print("=" * 50)

        # Supabase接続
        if not self.connect_supabase():
            return {"error": 1}

        # ログファイル検索
        log_files = self.find_log_files()
        print(f"📁 ログファイル検出: {len(log_files)}件")

        if not log_files:
            print("ℹ️ 移行対象のログファイルが見つかりません")
            return {"files": 0, "entries": 0}

        # ログファイルリスト表示
        for log_file in log_files:
            size = log_file.stat().st_size
            print(f"  📄 {log_file.name} ({size:,} bytes)")

        # 移行実行
        total_migrated = 0
        for log_file in log_files:
            migrated = self.migrate_log_file(log_file)
            total_migrated += migrated
            self.migrated_logs.append(
                {
                    "file": str(log_file.name),
                    "entries": migrated,
                    "size": log_file.stat().st_size,
                }
            )

        # クリーンアップ
        cleaned_files = self.cleanup_log_files(log_files)

        # 結果レポート
        print("\n" + "=" * 50)
        print("📊 移行結果レポート")
        print("=" * 50)
        print(f"✅ 移行ファイル数: {len(log_files)}")
        print(f"✅ 移行エントリ数: {total_migrated:,}")
        print(f"✅ 削除ファイル数: {cleaned_files}")

        # 詳細レポート
        total_size = sum(log["size"] for log in self.migrated_logs)
        print(f"💾 解放容量: {total_size:,} bytes ({total_size / 1024 / 1024:.2f} MB)")

        return {
            "files": len(log_files),
            "entries": total_migrated,
            "cleaned": cleaned_files,
            "size_freed": total_size,
        }


def main():
    """メイン実行"""
    migrator = LogMigration()

    try:
        result = migrator.run_migration()

        # 結果保存
        result_file = project_root / "runtime" / "log_migration_report.json"
        result_file.parent.mkdir(parents=True, exist_ok=True)

        with open(result_file, "w") as f:
            json.dump(
                {
                    "migration_timestamp": datetime.now().isoformat(),
                    "results": result,
                    "migrated_logs": migrator.migrated_logs,
                },
                f,
                indent=2,
            )

        print(f"\n📝 結果レポート保存: {result_file}")

        if result.get("entries", 0) > 0:
            print("\n🎉 ログファイルSupabase移行完了！")
            print("💡 次回から新しいログは直接Supabaseに記録されます")
        else:
            print("\n⚠️ 移行対象のログエントリが見つかりませんでした")

    except KeyboardInterrupt:
        print("\n⚠️ ユーザーによって中断されました")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 移行中にエラーが発生: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
