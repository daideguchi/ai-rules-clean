#!/usr/bin/env python3
"""
検索活動記録フック - 5分検索ルール遵守追跡
Read/Grep/Glob/Task使用時の検索活動を記録
"""

import json
import os
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SEARCH_LOG = PROJECT_ROOT / "runtime" / "ai_api_logs" / "search_activity.log"


def main():
    """メイン処理"""
    try:
        # 環境変数からツール名取得
        tool_name = os.environ.get("CLAUDE_TOOL_NAME", "unknown")

        # 検索関連ツールのみ記録
        search_tools = ["Read", "Grep", "Glob", "Task", "LS"]
        if tool_name not in search_tools:
            print(json.dumps({"continue": True}))
            return

        # 検索活動を記録
        search_entry = {
            "timestamp": datetime.now().isoformat(),
            "tool_name": tool_name,
            "search_type": "information_gathering",
            "session_id": os.environ.get("CLAUDE_SESSION_ID", "unknown"),
        }

        # ツール固有の情報を追加
        if tool_name == "Read":
            search_entry["file_path"] = os.environ.get("CLAUDE_TOOL_ARGS", {}).get(
                "file_path", ""
            )
        elif tool_name in ["Grep", "Glob"]:
            search_entry["pattern"] = os.environ.get("CLAUDE_TOOL_ARGS", {}).get(
                "pattern", ""
            )
        elif tool_name == "Task":
            search_entry["task_type"] = "research"

        # ログ記録
        SEARCH_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(SEARCH_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(search_entry, ensure_ascii=False) + "\n")

        print(json.dumps({"continue": True}))

    except Exception:
        # エラーが発生しても検索は継続
        print(json.dumps({"continue": True}))


if __name__ == "__main__":
    main()
