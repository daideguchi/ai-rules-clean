#!/usr/bin/env python3
"""
📊 MCP Operation Logger Hook
MCP tool使用を記録・分析
"""

import datetime
import json
import sys
from pathlib import Path


def log_mcp_operation(tool_name: str, tool_input: dict, session_id: str):
    """MCP操作をログファイルに記録"""

    log_dir = Path("src/runtime/logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "mcp_operations.jsonl"

    log_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "session_id": session_id,
        "tool_name": tool_name,
        "tool_input": tool_input,
        "server": tool_name.split("__")[1] if "__" in tool_name else "unknown",
        "operation": tool_name.split("__")[2]
        if tool_name.count("__") >= 2
        else "unknown",
    }

    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"⚠️  Failed to log MCP operation: {e}", file=sys.stderr)


def analyze_mcp_usage(tool_name: str) -> str:
    """MCP使用パターンの分析とアドバイス"""

    server = tool_name.split("__")[1] if "__" in tool_name else "unknown"
    operation = tool_name.split("__")[2] if tool_name.count("__") >= 2 else "unknown"

    advice = []

    # サーバー別アドバイス
    if server == "memory":
        advice.append("🧠 Memory operation: Consider batch operations for efficiency")
    elif server == "filesystem":
        advice.append("📁 File operation: Ensure proper error handling")
    elif server == "github":
        advice.append("🐙 GitHub operation: Watch rate limits")
    elif server == "o3":
        advice.append("🔮 o3 operation: High-quality model - use for complex tasks")
    elif server == "gemini":
        advice.append("💎 Gemini operation: Fast responses - good for real-time")

    # 操作別アドバイス
    if "create" in operation:
        advice.append("➕ Create operation: Verify uniqueness constraints")
    elif "delete" in operation:
        advice.append("🗑️  Delete operation: Consider backup/recovery")
    elif "search" in operation:
        advice.append("🔍 Search operation: Optimize query parameters")

    return " | ".join(advice) if advice else "ℹ️  MCP operation logged"


def main():
    try:
        # Hookからの入力を取得
        input_data = json.load(sys.stdin)

        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})
        session_id = input_data.get("session_id", "unknown")

        # MCP toolのパターンマッチング
        if not tool_name.startswith("mcp__"):
            sys.exit(0)

        # ログ記録
        log_mcp_operation(tool_name, tool_input, session_id)

        # 使用パターン分析とアドバイス
        advice = analyze_mcp_usage(tool_name)

        # 結果出力

        print(f"📊 MCP Logger: {tool_name}")
        print(f"💡 {advice}")

        sys.exit(0)

    except json.JSONDecodeError as e:
        print(f"❌ Hook Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Hook Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
