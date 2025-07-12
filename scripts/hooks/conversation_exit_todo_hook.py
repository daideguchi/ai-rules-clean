#!/usr/bin/env python3
"""
🎯 Conversation Exit TODO Hook - 会話終了時TODOフック
=====================================================
会話終了時に自動的にTODO明示プロトコルを実行するフック
Claude Code統合のStop eventで実行される
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# プロジェクトルートを追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.ai.conversation_exit_todo_protocol import (
        ConversationContext,
        ConversationExitTodoProtocol,
    )
    from src.memory.unified_memory_manager import UnifiedMemoryManager
except ImportError as e:
    print(f"インポートエラー: {e}")
    print("必要なモジュールが見つかりません。プロジェクト構造を確認してください。")
    sys.exit(1)


class ConversationExitTodoHook:
    """会話終了時TODOフック"""

    def __init__(self):
        self.project_root = project_root
        self.hook_log_file = (
            self.project_root / "runtime" / "logs" / "conversation_exit_hook.log"
        )
        self.todo_protocol = ConversationExitTodoProtocol()

        # 統合記憶管理との連携
        try:
            self.memory_manager = UnifiedMemoryManager()
        except Exception as e:
            print(f"⚠️ 記憶管理システム連携警告: {e}")
            self.memory_manager = None

        # ログファイル準備
        self.hook_log_file.parent.mkdir(parents=True, exist_ok=True)

    def execute_stop_hook(self, hook_data: dict = None) -> dict:
        """Stop フック実行"""
        try:
            self._log("🎯 会話終了時TODOフック実行開始")

            # 会話履歴を取得
            conversation_text = self._get_conversation_history()

            # 会話コンテキストを構築
            context = self._build_conversation_context()

            # TODO要約を生成
            todo_summary = self.todo_protocol.generate_exit_todo_summary(
                conversation_text, context
            )

            # 表示用フォーマット
            formatted_display = self.todo_protocol.format_exit_todo_display(
                todo_summary
            )

            # TODO要約を保存
            self.todo_protocol.save_todo_summary(todo_summary)

            # 記憶管理システムに記録
            if self.memory_manager:
                self._record_to_memory_system(todo_summary)

            # 継続性確保のためのセッション更新
            self._update_session_continuity(todo_summary)

            # 結果を出力
            print("\n" + "=" * 60)
            print("🎯 会話終了時TODO要約")
            print("=" * 60)
            print(formatted_display)
            print("\n" + "=" * 60)

            self._log(
                f"✅ TODO要約完了: {todo_summary['total_todos_extracted']}件のTODOを抽出"
            )

            return {
                "status": "success",
                "todos_extracted": todo_summary["total_todos_extracted"],
                "continuity_score": todo_summary["continuity_score"],
                "completion_status": todo_summary["completion_status"],
            }

        except Exception as e:
            self._log(f"❌ 会話終了時TODOフック実行エラー: {e}")
            return {"status": "error", "error": str(e)}

    def _get_conversation_history(self) -> str:
        """会話履歴を取得"""
        try:
            # 会話ログファイルを探す
            log_dirs = [
                self.project_root / "runtime" / "conversation_logs",
                self.project_root / "runtime" / "logs",
                self.project_root / "runtime",
            ]

            conversation_text = ""

            for log_dir in log_dirs:
                if log_dir.exists():
                    # 最新のログファイルを検索
                    log_files = list(log_dir.glob("*.jsonl")) + list(
                        log_dir.glob("*.json")
                    )
                    if log_files:
                        latest_log = max(log_files, key=lambda f: f.stat().st_mtime)
                        conversation_text = self._extract_text_from_log(latest_log)
                        break

            # フォールバック：環境変数や標準入力から
            if not conversation_text:
                conversation_text = os.environ.get("CONVERSATION_HISTORY", "")

            return conversation_text

        except Exception as e:
            self._log(f"会話履歴取得エラー: {e}")
            return ""

    def _extract_text_from_log(self, log_file: Path) -> str:
        """ログファイルからテキストを抽出"""
        try:
            with open(log_file, encoding="utf-8") as f:
                if log_file.suffix == ".jsonl":
                    # JSONL形式
                    lines = []
                    for line in f:
                        try:
                            data = json.loads(line.strip())
                            if isinstance(data, dict):
                                # メッセージ内容を抽出
                                content = (
                                    data.get("content", "")
                                    or data.get("message", "")
                                    or str(data)
                                )
                                lines.append(content)
                        except json.JSONDecodeError:
                            lines.append(line.strip())
                    return "\n".join(lines)
                else:
                    # JSON形式
                    data = json.load(f)
                    if isinstance(data, dict):
                        return str(data)
                    elif isinstance(data, list):
                        return "\n".join(str(item) for item in data)
                    else:
                        return str(data)
        except Exception as e:
            self._log(f"ログファイル読み込みエラー: {e}")
            return ""

    def _build_conversation_context(self) -> ConversationContext:
        """会話コンテキストを構築"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        return ConversationContext(
            conversation_id=f"conversation_{timestamp}",
            start_time=datetime.now().isoformat(),
            end_time=datetime.now().isoformat(),
            total_messages=1,  # 概算
            key_topics=["システム実装", "AI組織"],
            technical_domains=["ai", "backend", "system"],
            completion_status="session_ending",
        )

    def _record_to_memory_system(self, todo_summary: dict):
        """記憶管理システムに記録"""
        try:
            if self.memory_manager:
                memory_entry = {
                    "type": "conversation_exit_todos",
                    "timestamp": datetime.now().isoformat(),
                    "todos_count": todo_summary["total_todos_extracted"],
                    "continuity_score": todo_summary["continuity_score"],
                    "completion_status": todo_summary["completion_status"],
                    "priority_distribution": {
                        priority: len(todos)
                        for priority, todos in todo_summary["prioritized_todos"].items()
                    },
                }

                self.memory_manager.store_memory(
                    "conversation_exit_todos",
                    memory_entry,
                    importance=0.8,
                    context={"session_end": True},
                )

        except Exception as e:
            self._log(f"記憶システム記録エラー: {e}")

    def _update_session_continuity(self, todo_summary: dict):
        """セッション継続性を更新"""
        try:
            session_file = (
                self.project_root
                / "src"
                / "memory"
                / "core"
                / "session-records"
                / "current-session.json"
            )

            if session_file.exists():
                with open(session_file, encoding="utf-8") as f:
                    session_data = json.load(f)
            else:
                session_data = {}

            # 継続性情報を追加
            session_data["conversation_exit"] = {
                "timestamp": datetime.now().isoformat(),
                "todos_extracted": todo_summary["total_todos_extracted"],
                "continuity_score": todo_summary["continuity_score"],
                "completion_status": todo_summary["completion_status"],
                "next_session_prep": todo_summary.get(
                    "next_session_recommendations", []
                ),
            }

            # セッション品質情報を更新
            if "session_quality" not in session_data:
                session_data["session_quality"] = {}

            session_data["session_quality"]["todo_protocol_executed"] = True
            session_data["session_quality"]["conversation_continuity_ensured"] = True
            session_data["last_updated"] = datetime.now().isoformat()

            # 保存
            session_file.parent.mkdir(parents=True, exist_ok=True)
            with open(session_file, "w", encoding="utf-8") as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            self._log(f"セッション継続性更新エラー: {e}")

    def _log(self, message: str):
        """ログ出力"""
        log_entry = f"[{datetime.now().isoformat()}] {message}"
        print(log_entry)

        try:
            with open(self.hook_log_file, "a", encoding="utf-8") as f:
                f.write(log_entry + "\n")
        except Exception:
            pass


def main():
    """メイン実行（フック呼び出し）"""
    hook = ConversationExitTodoHook()

    # 引数からフックタイプを取得
    hook_type = sys.argv[1] if len(sys.argv) > 1 else "Stop"

    if hook_type == "Stop":
        result = hook.execute_stop_hook()
        print(f"🎯 会話終了時TODOプロトコル実行結果: {result['status']}")

        if result["status"] == "success":
            print(f"📋 抽出されたTODO: {result['todos_extracted']}件")
            print(f"🔄 継続性スコア: {result['continuity_score']:.2f}")
            print(f"✅ 完了状況: {result['completion_status']}")
    else:
        print(f"🎯 TODO Hook: {hook_type} event - No action required")


if __name__ == "__main__":
    main()
