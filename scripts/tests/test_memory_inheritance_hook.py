#!/usr/bin/env python3
"""
Memory Inheritance Hook テストスクリプト
"""

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
HOOK_SCRIPT = PROJECT_ROOT / "scripts/hooks/memory_inheritance_hook.py"


def test_hook(test_name: str, hook_data: dict):
    """フックをテスト"""
    print(f"\n=== {test_name} ===")

    # フックを実行
    result = subprocess.run(
        [sys.executable, str(HOOK_SCRIPT)],
        input=json.dumps(hook_data),
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"❌ エラー: {result.stderr}")
        return

    try:
        response = json.loads(result.stdout)
        print(f"✅ 結果: {json.dumps(response, ensure_ascii=False, indent=2)}")
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析エラー: {e}")
        print(f"出力: {result.stdout}")


def main():
    """テスト実行"""

    # テスト1: 危険なパターン（虚偽報告）
    test_hook(
        "危険パターンテスト - 虚偽報告",
        {
            "tool_name": "Edit",
            "arguments": {
                "file_path": "test.py",
                "new_string": "システムは正常に稼働中です。",
            },
        },
    )

    # テスト2: 推測表現
    test_hook(
        "推測表現テスト",
        {
            "tool_name": "Write",
            "arguments": {
                "file_path": "doc.md",
                "content": "おそらくこの機能は正しく動作するでしょう。",
            },
        },
    )

    # テスト3: 安全なコード
    test_hook(
        "安全なコードテスト",
        {
            "tool_name": "Edit",
            "arguments": {
                "file_path": "main.py",
                "new_string": "def calculate(x, y):\n    return x + y",
            },
        },
    )

    # テスト4: 危険なBashコマンド
    test_hook(
        "危険コマンドテスト",
        {
            "tool_name": "Bash",
            "arguments": {"command": "echo '実装済みです' > status.txt"},
        },
    )

    # テスト5: ファイルパス問題
    test_hook(
        "絶対パステスト",
        {
            "tool_name": "Write",
            "arguments": {"file_path": "test.py", "content": "print('test')"},
        },
    )


if __name__ == "__main__":
    main()
