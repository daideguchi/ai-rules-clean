#!/usr/bin/env python3
"""
🛡️ Gemini Command Validator Hook
Geminiコマンド使用時の構文エラー防止システム
84回目のミス防止：毎回同じGeminiコマンド構文エラーを防ぐ
"""

import os
import re
import sys


def validate_gemini_command():
    """Geminiコマンド構文を自動修正"""

    # 環境変数からツール情報を取得
    tool_name = os.environ.get("TOOL_NAME", "")
    tool_input = os.environ.get("TOOL_INPUT", "")

    if tool_name != "Bash":
        return

    # Geminiコマンドチェック
    command = tool_input.strip()
    if not command.startswith("gemini "):
        return

    # 既知の間違いパターンをチェック
    if re.match(r'^gemini\s+"[^"]*"$', command):
        # パターン: gemini "テキスト"
        text = re.search(r'^gemini\s+"([^"]*)"$', command).group(1)
        corrected = f'gemini -p "{text}"'

        print("🔧 Geminiコマンド自動修正:")
        print(f"   ❌ 間違い: {command}")
        print(f"   ✅ 修正後: {corrected}")

        # 修正されたコマンドを環境変数に設定
        os.environ["TOOL_INPUT"] = corrected

    elif re.match(r"^gemini\s+[^-]", command):
        # パターン: gemini テキスト（引用符なし）
        text = command[7:].strip()  # "gemini " を除去
        corrected = f'gemini -p "{text}"'

        print("🔧 Geminiコマンド自動修正:")
        print(f"   ❌ 間違い: {command}")
        print(f"   ✅ 修正後: {corrected}")

        os.environ["TOOL_INPUT"] = corrected


def main():
    """メイン処理"""
    try:
        validate_gemini_command()
    except Exception as e:
        print(f"⚠️ Geminiコマンド検証エラー: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
