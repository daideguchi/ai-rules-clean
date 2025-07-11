#!/usr/bin/env python3
"""
Todo状況追跡フック - TodoRead/TodoWrite使用時の状況記録
タスク明確化の強制と追跡
"""

import json
import os
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TODO_STATUS_FILE = PROJECT_ROOT / "runtime" / "ai_api_logs" / "todo_status.json"


def main():
    """メイン処理"""
    try:
        # 環境変数からツール名取得
        tool_name = os.environ.get("CLAUDE_TOOL_NAME", "unknown")

        # Todo関連ツールのみ処理
        if tool_name not in ["TodoRead", "TodoWrite"]:
            print(json.dumps({"continue": True}))
            return

        # 既存のTodo状況を読み込み
        current_todos = []
        if TODO_STATUS_FILE.exists():
            try:
                with open(TODO_STATUS_FILE, encoding="utf-8") as f:
                    current_todos = json.load(f)
            except Exception:
                current_todos = []

        # TodoWrite の場合、新しいTodo状況を記録
        if tool_name == "TodoWrite":
            # 実際のTodoデータは後で更新されるので、現在の状況を維持
            pass

        # 使用記録
        usage_entry = {
            "timestamp": datetime.now().isoformat(),
            "tool_name": tool_name,
            "todo_count": len(current_todos),
            "session_id": os.environ.get("CLAUDE_SESSION_ID", "unknown"),
        }

        # ログ記録
        usage_log = PROJECT_ROOT / "runtime" / "ai_api_logs" / "todo_usage.log"
        usage_log.parent.mkdir(parents=True, exist_ok=True)
        with open(usage_log, "a", encoding="utf-8") as f:
            f.write(json.dumps(usage_entry, ensure_ascii=False) + "\n")

        print(json.dumps({"continue": True}))

    except Exception:
        # エラーが発生してもTodo操作は継続
        print(json.dumps({"continue": True}))


if __name__ == "__main__":
    main()
