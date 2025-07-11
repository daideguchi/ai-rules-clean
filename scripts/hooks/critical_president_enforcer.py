#!/usr/bin/env python3
"""
🚨 CRITICAL PRESIDENT ENFORCER 🚨
このプロダクトの最大の課題に対する最終解決策

PRESIDENT宣言なしでは絶対に何もできないシステム
- Read/LS/Edit/Write/Task/Bash等、全ツールを完全ブロック
- make declare-president のみ実行可能
- 宣言済みチェックは永続的（セッション跨ぎ対応）
"""

import json
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DECLARATION_FLAG = PROJECT_ROOT / "runtime/secure_state/president_session.json"


def is_president_declared():
    """PRESIDENT宣言済みかチェック（永続的）"""
    try:
        if not DECLARATION_FLAG.exists():
            return False

        with open(DECLARATION_FLAG) as f:
            state = json.load(f)
            return state.get("president_declared", False)
    except Exception:
        return False


def get_tool_info():
    """ツール情報取得"""
    tool_name = os.environ.get("CLAUDE_TOOL_NAME", "unknown")
    bash_command = os.environ.get("CLAUDE_BASH_COMMAND", "")
    return tool_name, bash_command


def main():
    """🚨 CRITICAL ENFORCEMENT 🚨"""
    try:
        tool_name, bash_command = get_tool_info()

        # PRESIDENT宣言チェック
        if not is_president_declared():
            # 宣言関連Bashのみ許可
            if tool_name == "Bash":
                allowed_commands = [
                    "make declare-president",
                    "python3 scripts/utilities/secure-president-declare.py",
                    "secure-president-declare",
                ]

                if any(cmd in bash_command for cmd in allowed_commands):
                    print(json.dumps({"allow": True}))
                    return

            # その他全ツールを完全ブロック
            error_response = {
                "allow": False,
                "error": "🚨 CRITICAL: PRESIDENT宣言必須",
                "message": (
                    "🚨🚨🚨 CRITICAL ENFORCEMENT 🚨🚨🚨\n\n"
                    "このプロダクトの最大の課題:\n"
                    "PRESIDENT宣言忘れの完全防止\n\n"
                    "【現在の状態】\n"
                    f"• ブロック対象ツール: {tool_name}\n"
                    f"• 宣言状態: 未実行\n\n"
                    "【解決方法】\n"
                    "make declare-president\n\n"
                    "【重要】\n"
                    "宣言なしでは一切のツールが使用不可能です。\n"
                    "Read/LS/Edit/Write/Task等、全て完全ブロックされます。"
                ),
                "required_action": "make declare-president 即座実行",
                "blocked_tool": tool_name,
                "severity": "CRITICAL",
                "product_critical_issue": True,
            }
            print(json.dumps(error_response))
            return

        # 宣言済みの場合は全ツール許可
        print(json.dumps({"allow": True}))

    except Exception as e:
        # エラー時も安全にブロック
        error_response = {
            "allow": False,
            "error": f"CRITICAL ENFORCER ERROR: {str(e)}",
            "message": "安全のため全ツールをブロックしました",
        }
        print(json.dumps(error_response))


if __name__ == "__main__":
    main()
