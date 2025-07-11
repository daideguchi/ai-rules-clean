#!/usr/bin/env python3
"""
🔍 Pre-Bash Validator Hook
Bashコマンド実行前の検証とベストプラクティス適用
"""

import json
import re
import sys


def validate_bash_command(command: str) -> list[str]:
    """Bashコマンドの検証ルール"""
    issues = []

    # 記事の推奨に従ったルール
    validation_rules = [
        (
            r"\bgrep\b(?!.*\|)",
            "🚀 Use 'rg' (ripgrep) instead of 'grep' for better performance",
        ),
        (
            r"\bfind\s+\S+\s+-name\b",
            "🚀 Use 'rg --files | rg pattern' instead of 'find -name'",
        ),
        (
            r"\bcat\s+[^|]*$",
            "💡 Consider using 'Read' tool instead of 'cat' for file reading",
        ),
        (
            r"rm\s+-rf\s+/",
            "⚠️  Dangerous: recursive delete from root - please be more specific",
        ),
        (r"sudo\s+", "🔒 Security: sudo command detected - ensure this is necessary"),
        (
            r">\s*/dev/null\s+2>&1",
            "📝 Consider using proper error handling instead of silencing",
        ),
    ]

    for pattern, message in validation_rules:
        if re.search(pattern, command):
            issues.append(message)

    return issues


def suggest_alternatives(command: str) -> str:
    """コマンドの改善提案"""
    suggestions = []

    # grepをrgに変換
    if "grep" in command and "rg" not in command:
        improved = re.sub(r"\bgrep\b", "rg", command)
        suggestions.append(f"💡 Suggested: {improved}")

    # find to rg変換
    if re.search(r"find\s+.*-name", command):
        match = re.search(r'find\s+(\S+)\s+-name\s+["\']([^"\']+)["\']', command)
        if match:
            path, pattern = match.groups()
            improved = f"rg --files {path} | rg '{pattern}'"
            suggestions.append(f"💡 Suggested: {improved}")

    return "\n".join(suggestions)


def main():
    try:
        # Hookからの入力を取得
        input_data = json.load(sys.stdin)

        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})
        command = tool_input.get("command", "")

        if tool_name != "Bash" or not command:
            sys.exit(0)

        # コマンド検証
        issues = validate_bash_command(command)
        suggestions = suggest_alternatives(command)

        # 結果出力
        if issues or suggestions:
            output = {"continue": True, "suppressOutput": False}

            feedback = []
            if issues:
                feedback.append("🔍 Command Analysis:")
                feedback.extend([f"  {issue}" for issue in issues])

            if suggestions:
                feedback.append("🚀 Improvement Suggestions:")
                feedback.append(f"  {suggestions}")

            # ユーザーに表示（transcript mode用）
            print("\n".join(feedback))

            # JSON出力でClaude Codeに制御情報を返す
            print(json.dumps(output), file=sys.stderr)

        sys.exit(0)

    except json.JSONDecodeError as e:
        print(f"❌ Hook Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Hook Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
