#!/usr/bin/env python3
"""
行動監視フック - 実際の行動を監視して自律成長
"""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from src.memory.core.behavior_monitor import (  # noqa: E402
    get_session_summary,
    monitor_action,
)


def main():
    """PostToolUseフックとして動作"""
    try:
        # フックデータを読み込み
        hook_data = json.loads(sys.stdin.read())
        tool_name = hook_data.get("tool_name", "")
        tool_args = hook_data.get("arguments", {})
        tool_result = hook_data.get("result", {})

        # 行動を監視
        monitor_action(tool_name, tool_args, str(tool_result))

        # セッションサマリーを取得
        summary = get_session_summary()

        # 応答（PostToolUseフックは常にallow）
        response = {
            "allow": True,
            "info": f"📊 行動監視中 - 記録: {summary['behaviors_recorded']}件, 自律学習: {summary['growth']['auto_learned_patterns']}件",
        }

        print(json.dumps(response, ensure_ascii=False))

    except Exception as e:
        print(json.dumps({"allow": True, "error": f"行動監視エラー: {str(e)}"}))


if __name__ == "__main__":
    main()
