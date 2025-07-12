#!/usr/bin/env python3
"""
📝 Conversation Logger Hook - 会話ログ自動記録フック
===============================================
Claude Code統合による会話の完全自動記録システム
Start/PreToolUse/PostToolUse/Stop全フェーズで会話を記録
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
    from src.hooks.conversation_logger import ConversationLogger
except ImportError:
    # フォールバック: 基本的な会話記録機能
    class ConversationLogger:
        def __init__(self):
            self.project_root = project_root
            self.logs_dir = self.project_root / "runtime" / "conversation_logs"
            self.logs_dir.mkdir(parents=True, exist_ok=True)

            # 今日の会話ログファイル
            today = datetime.now().strftime("%Y%m%d")
            self.current_log_file = self.logs_dir / f"conversation_{today}.jsonl"

        def log_message(self, message_type, content, metadata=None):
            """メッセージログ"""
            try:
                entry = {
                    "timestamp": datetime.now().isoformat(),
                    "type": message_type,
                    "content": content,
                    "metadata": metadata or {},
                }

                with open(self.current_log_file, "a", encoding="utf-8") as f:
                    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            except Exception:
                pass


class ConversationLoggerHook:
    """会話ログ自動記録フック"""

    def __init__(self):
        self.logger = ConversationLogger()
        self.hook_log_file = project_root / "runtime" / "logs" / "conversation_hook.log"
        self.hook_log_file.parent.mkdir(parents=True, exist_ok=True)

    def execute_start_hook(self, hook_data: dict = None) -> dict:
        """Start フック実行"""
        try:
            self._log("🎯 会話セッション開始 - 自動記録開始")

            # セッション開始をログ
            self.logger.log_system_action(
                "新しい会話セッション開始 - 自動記録開始",
                {
                    "timestamp": datetime.now().isoformat(),
                    "hook_type": "Start",
                    "auto_logging": True,
                },
            )

            return {"status": "success", "logging_active": True}

        except Exception as e:
            self._log(f"❌ Start フックエラー: {e}")
            return {"status": "error", "error": str(e)}

    def execute_pre_tool_use_hook(self, hook_data: dict = None) -> dict:
        """PreToolUse フック実行"""
        try:
            tool_name = os.environ.get("CLAUDE_TOOL_NAME", "unknown")

            # ツール使用前をログ
            self.logger.log_system_action(
                f"ツール使用開始: {tool_name}",
                {
                    "tool_name": tool_name,
                    "hook_type": "PreToolUse",
                    "timestamp": datetime.now().isoformat(),
                },
            )

            return {"status": "success", "tool_logged": tool_name}

        except Exception as e:
            self._log(f"❌ PreToolUse フックエラー: {e}")
            return {"status": "error", "error": str(e)}

    def execute_post_tool_use_hook(self, hook_data: dict = None) -> dict:
        """PostToolUse フック実行"""
        try:
            tool_name = os.environ.get("CLAUDE_TOOL_NAME", "unknown")

            # ツール使用後をログ
            self.logger.log_system_action(
                f"ツール使用完了: {tool_name}",
                {
                    "tool_name": tool_name,
                    "hook_type": "PostToolUse",
                    "timestamp": datetime.now().isoformat(),
                },
            )

            return {"status": "success", "tool_completed": tool_name}

        except Exception as e:
            self._log(f"❌ PostToolUse フックエラー: {e}")
            return {"status": "error", "error": str(e)}

    def execute_stop_hook(self, hook_data: dict = None) -> dict:
        """Stop フック実行"""
        try:
            self._log("🎯 会話セッション終了 - 自動記録完了")

            # セッション終了をログ
            self.logger.log_system_action(
                "会話セッション終了 - 自動記録完了",
                {
                    "timestamp": datetime.now().isoformat(),
                    "hook_type": "Stop",
                    "auto_logging_completed": True,
                },
            )

            return {"status": "success", "session_completed": True}

        except Exception as e:
            self._log(f"❌ Stop フックエラー: {e}")
            return {"status": "error", "error": str(e)}

    def _log(self, message: str):
        """ログ出力"""
        log_entry = f"[{datetime.now().isoformat()}] {message}"

        try:
            with open(self.hook_log_file, "a", encoding="utf-8") as f:
                f.write(log_entry + "\n")
        except Exception:
            pass


def main():
    """メイン実行（フック呼び出し）"""
    hook = ConversationLoggerHook()

    # 引数からフックタイプを取得
    hook_type = sys.argv[1] if len(sys.argv) > 1 else "Start"

    if hook_type == "Start":
        result = hook.execute_start_hook()
    elif hook_type == "PreToolUse":
        result = hook.execute_pre_tool_use_hook()
    elif hook_type == "PostToolUse":
        result = hook.execute_post_tool_use_hook()
    elif hook_type == "Stop":
        result = hook.execute_stop_hook()
    else:
        result = {"status": "unknown_hook_type", "hook_type": hook_type}

    # 結果をJSON形式で出力（Claude Code要求形式）
    print(json.dumps(result))


if __name__ == "__main__":
    main()
