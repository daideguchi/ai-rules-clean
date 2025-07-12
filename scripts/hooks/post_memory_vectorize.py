#!/usr/bin/env python3
"""
🧠 Post Memory Vectorize Hook
AI Memory Inheritance System への操作記録とベクトル化
"""

import datetime
import hashlib
import json
import sys
from pathlib import Path


def extract_operation_context(
    tool_name: str, tool_input: dict, tool_response: dict
) -> dict:
    """操作コンテキストの抽出"""

    context = {
        "timestamp": datetime.datetime.now().isoformat(),
        "tool": tool_name,
        "operation_type": "unknown",
        "content_hash": None,
        "file_path": None,
        "description": "",
        "tags": [],
    }

    # ツール別コンテキスト抽出
    if tool_name in ["Edit", "Write", "MultiEdit"]:
        context["operation_type"] = "file_modification"
        context["file_path"] = tool_input.get("file_path", "")

        # ファイル内容のハッシュ化
        content = tool_input.get("content", "") or tool_input.get("new_string", "")
        if content:
            context["content_hash"] = hashlib.sha256(content.encode()).hexdigest()[:16]
            context["description"] = (
                f"File {tool_name.lower()}: {Path(context['file_path']).name}"
            )

        # ファイル拡張子をタグとして追加
        if context["file_path"]:
            ext = Path(context["file_path"]).suffix
            if ext:
                context["tags"].append(f"ext:{ext[1:]}")

    elif tool_name == "Bash":
        context["operation_type"] = "command_execution"
        command = tool_input.get("command", "")
        context["description"] = (
            f"Bash: {command[:50]}..." if len(command) > 50 else f"Bash: {command}"
        )
        context["content_hash"] = hashlib.sha256(command.encode()).hexdigest()[:16]

        # コマンドタイプをタグとして分析
        if command:
            cmd_parts = command.strip().split()
            if cmd_parts:
                context["tags"].append(f"cmd:{cmd_parts[0]}")

    elif tool_name.startswith("mcp__"):
        context["operation_type"] = "mcp_operation"
        server = tool_name.split("__")[1] if "__" in tool_name else "unknown"
        operation = (
            tool_name.split("__")[2] if tool_name.count("__") >= 2 else "unknown"
        )
        context["description"] = f"MCP {server}: {operation}"
        context["tags"].extend([f"mcp:{server}", f"op:{operation}"])

    elif tool_name in ["Read", "Glob", "Grep"]:
        context["operation_type"] = "information_retrieval"
        context["description"] = f"{tool_name}: Information retrieval"
        context["tags"].append(f"retrieval:{tool_name.lower()}")

    return context


def save_to_memory_system(context: dict, session_id: str):
    """AI Memory Inheritance System への保存"""

    memory_dir = Path("src/memory/operations")
    memory_dir.mkdir(parents=True, exist_ok=True)

    # 操作ログファイル
    log_file = memory_dir / "operation_log.jsonl"

    log_entry = {"session_id": session_id, **context}

    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"⚠️  Failed to save to memory system: {e}", file=sys.stderr)
        return False

    return True


def analyze_operation_patterns(context: dict) -> str:
    """操作パターンの分析とインサイト"""

    insights = []

    # ファイル操作パターン分析
    if context["operation_type"] == "file_modification":
        file_path = context.get("file_path", "")
        if file_path:
            if "config" in file_path.lower():
                insights.append(
                    "📝 Configuration file modified - consider documentation update"
                )
            elif file_path.endswith(".py"):
                insights.append("🐍 Python code modified - consider running tests")
            elif file_path.endswith(".md"):
                insights.append("📚 Documentation updated - great for knowledge base")

    # コマンド実行パターン分析
    elif context["operation_type"] == "command_execution":
        if "git" in context.get("tags", []):
            insights.append("🔄 Git operation - tracking version control activity")
        elif "test" in context.get("description", "").lower():
            insights.append("🧪 Testing activity detected - maintaining code quality")

    # MCP操作パターン分析
    elif context["operation_type"] == "mcp_operation":
        insights.append("🔗 MCP operation - enhancing AI capabilities")

    return (
        " | ".join(insights) if insights else "📊 Operation recorded in memory system"
    )


def main():
    try:
        # Hookからの入力を取得
        input_data = json.load(sys.stdin)

        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})
        tool_response = input_data.get("tool_response", {})
        session_id = input_data.get("session_id", "unknown")

        if not tool_name:
            sys.exit(0)

        # 操作コンテキスト抽出
        context = extract_operation_context(tool_name, tool_input, tool_response)

        # メモリシステムへの保存
        saved = save_to_memory_system(context, session_id)

        # パターン分析
        insights = analyze_operation_patterns(context)

        # 結果出力

        if saved:
            print(f"🧠 Memory: {context['description']}")
            print(f"💡 {insights}")
        else:
            print("⚠️  Memory system save failed", file=sys.stderr)

        sys.exit(0)

    except json.JSONDecodeError as e:
        print(f"❌ Hook Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Hook Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
