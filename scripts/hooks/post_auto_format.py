#!/usr/bin/env python3
"""
✨ Post Auto Format Hook
ファイル編集後の自動フォーマット適用
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Tuple


def format_python_file(file_path: str) -> Tuple[bool, str]:
    """Python ファイルの自動フォーマット"""
    try:
        # black でフォーマット
        result = subprocess.run(
            ["python", "-m", "black", "--line-length", "88", file_path],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            return True, "✨ Python file formatted with black"
        else:
            return False, f"⚠️  Black formatting failed: {result.stderr}"

    except subprocess.TimeoutExpired:
        return False, "⚠️  Black formatting timed out"
    except FileNotFoundError:
        # blackがない場合はskip
        return True, "⚠️  Black not found, skipping Python formatting"
    except Exception as e:
        return False, f"❌ Black formatting error: {e}"


def format_json_file(file_path: str) -> Tuple[bool, str]:
    """JSON ファイルの自動フォーマット"""
    try:
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, sort_keys=True)

        return True, "✨ JSON file formatted"

    except json.JSONDecodeError as e:
        return False, f"⚠️  Invalid JSON format: {e}"
    except Exception as e:
        return False, f"❌ JSON formatting error: {e}"


def format_markdown_file(file_path: str) -> Tuple[bool, str]:
    """Markdown ファイルの軽微なフォーマット"""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # 基本的な整形
        lines = content.split("\n")
        formatted_lines = []

        for line in lines:
            # 末尾空白削除
            line = line.rstrip()
            formatted_lines.append(line)

        # 最後に空行がない場合は追加
        if formatted_lines and formatted_lines[-1] != "":
            formatted_lines.append("")

        formatted_content = "\n".join(formatted_lines)

        if formatted_content != content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(formatted_content)
            return True, "✨ Markdown file formatted"
        else:
            return True, "ℹ️  Markdown file already formatted"

    except Exception as e:
        return False, f"❌ Markdown formatting error: {e}"


def apply_formatting(file_path: str) -> Tuple[bool, str]:
    """ファイル拡張子に応じたフォーマット適用"""

    if not file_path or not Path(file_path).exists():
        return True, "ℹ️  File not found or invalid path"

    extension = Path(file_path).suffix.lower()

    if extension == ".py":
        return format_python_file(file_path)
    elif extension == ".json":
        return format_json_file(file_path)
    elif extension in [".md", ".markdown"]:
        return format_markdown_file(file_path)
    else:
        return True, f"ℹ️  No formatter available for {extension}"


def main():
    try:
        # Hookからの入力を取得
        input_data = json.load(sys.stdin)

        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})

        if tool_name not in ["Edit", "Write", "MultiEdit"]:
            sys.exit(0)

        file_path = tool_input.get("file_path", "")

        if not file_path:
            sys.exit(0)

        # フォーマット適用
        success, message = apply_formatting(file_path)

        # 結果出力

        print(f"🎨 Auto Format: {message}")

        if not success:
            # フォーマットエラーは警告のみ、継続
            print("⚠️  Formatting failed but continuing...", file=sys.stderr)

        sys.exit(0)

    except json.JSONDecodeError as e:
        print(f"❌ Hook Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Hook Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
