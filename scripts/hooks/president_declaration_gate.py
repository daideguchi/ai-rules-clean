#!/usr/bin/env python3
"""
PRESIDENT宣言強制フックシステム
セッション開始時にPRESIDENT宣言を必須化し、全ツール使用をブロック
"""

import hashlib
import json
import os
import sys
from pathlib import Path

# プロジェクトルート設定
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SECURE_STATE_DIR = PROJECT_ROOT / "runtime" / "secure_state"
SESSION_STATE_FILE = SECURE_STATE_DIR / "president_session.json"
BACKUP_STATE_FILE = SECURE_STATE_DIR / "president_session.backup.json"

# 必須確認ファイル
CRITICAL_FILES = [
    "CLAUDE.md",
    "src/memory/persistent-learning/mistakes-database.json",
    "docs/03_processes/file-organization-rules.md",
    "docs/03_processes/language-usage-rules.md",
]

# 言語使用ルール
LANGUAGE_RULES = {
    "processing": "english",  # Tool usage, technical implementation
    "declaration": "japanese",  # PRESIDENT declaration, cursor rules
    "reporting": "japanese",  # Final reports to user
    "user_preferred_format": "japanese_declaration_english_process_japanese_report",
}

# 言語使用違反パターン
LANGUAGE_VIOLATION_PATTERNS = {
    "mixed_processing": r"(I will|Let me|I'll|I'm going to|I need to).*?(処理|実装|修正|対応)",
    "english_declaration": r"(I hereby declare|I declare|Declaration:|President|PRESIDENT).*?(activated|started|initiated)",
    "mixed_reporting": r"(Successfully|Completed|Finished|Done).*?(完了|成功|終了)",
    "forbidden_mixing": r"(する|した|します|でした).*(will|shall|would|should|can|could|must|may|might)",
}

# 絶対保護対象ファイル・ディレクトリ
PROTECTED_PATHS = [
    ".specstory",
    ".vscode",
    "CLAUDE.md",
    "src/memory/core",
    "src/memory/persistent-learning/mistakes-database.json",
]

# ルートディレクトリ許可リスト
ALLOWED_ROOT_FILES = [
    "CHANGELOG.md",
    "CLAUDE.md",
    "Index.md",
    "LICENSE",
    "Makefile",
    "README.md",
    "pyproject.toml",
    ".gitignore",
    ".gitattributes",
    "config",
    "docs",
    "scripts",
    "src",
    "tests",
    "runtime",
    "gemini_env",
    "data",
]


def get_file_hash(file_path):
    """ファイルのSHA256ハッシュを取得"""
    try:
        with open(PROJECT_ROOT / file_path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except FileNotFoundError:
        return None


def load_session_state():
    """セッション状態を安全に読み込み"""
    for state_file in [SESSION_STATE_FILE, BACKUP_STATE_FILE]:
        if not state_file.exists():
            continue

        try:
            with open(state_file, encoding="utf-8") as f:
                data = json.load(f)

                # 基本的なスキーマ検証
                required_fields = [
                    "president_declared",
                    "session_start",
                    "declaration_timestamp",
                ]
                if all(field in data for field in required_fields):
                    return data

        except (json.JSONDecodeError, KeyError, OSError):
            continue

    return None


def check_root_organization():
    """ルートディレクトリの整理状態をチェック"""
    try:
        root_items = list(PROJECT_ROOT.iterdir())
        root_names = [item.name for item in root_items]

        # 許可されていないファイルをチェック
        unauthorized = [name for name in root_names if name not in ALLOWED_ROOT_FILES]

        if unauthorized:
            return False, f"ルート整理未完了: {unauthorized}"

        if len(root_names) > 16:  # 許可リスト + 予備
            return False, f"ルートファイル数過多: {len(root_names)}個"

        return True, "Root directory organized"
    except Exception as e:
        return False, f"Root check error: {str(e)}"


def check_protected_files():
    """保護対象ファイルの存在チェック"""
    try:
        missing = []
        for path in PROTECTED_PATHS:
            full_path = PROJECT_ROOT / path
            if not full_path.exists():
                missing.append(path)

        if missing:
            return False, f"保護対象ファイル消失: {missing}"

        return True, "Protected files intact"
    except Exception as e:
        return False, f"Protection check error: {str(e)}"


def is_president_declared():
    """PRESIDENT宣言済みかチェック"""
    state = load_session_state()
    if not state:
        return False

    # PRESIDENT宣言は永久有効（期限チェック削除）
    # session_start = datetime.fromisoformat(state.get('session_start', ''))
    # if (datetime.now() - session_start).total_seconds() > 14400:  # 永久有効
    #     return False

    return state.get("president_declared", False)


def comprehensive_organization_check():
    """包括的な組織チェック"""
    issues = []

    # 1. ルート整理チェック
    root_ok, root_msg = check_root_organization()
    if not root_ok:
        issues.append(root_msg)

    # 2. 保護ファイルチェック
    protect_ok, protect_msg = check_protected_files()
    if not protect_ok:
        issues.append(protect_msg)

    # 3. 重要ファイル存在チェック
    for critical_file in CRITICAL_FILES:
        if not (PROJECT_ROOT / critical_file).exists():
            issues.append(f"重要ファイル不在: {critical_file}")

    return len(issues) == 0, issues


def check_language_usage(text):
    """言語使用ルール違反をチェック"""
    import re

    violations = []

    for violation_type, pattern in LANGUAGE_VIOLATION_PATTERNS.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            violations.append(
                {"type": violation_type, "pattern": pattern, "matches": matches}
            )

    return violations


def get_tool_name_from_input():
    """環境変数からツール名を抽出（stdin読み込み回避）"""
    try:
        # 環境変数から取得を試行
        tool_name = os.environ.get("CLAUDE_TOOL_NAME", "")
        if tool_name:
            return tool_name

        # コマンドライン引数から取得
        if len(sys.argv) > 1:
            return sys.argv[1]

        return "unknown"
    except Exception:
        return "unknown"


def main():
    """メイン処理"""
    try:
        tool_name = get_tool_name_from_input()

        # 言語使用ルール チェック（全入力に対して）
        input_text = os.environ.get("CLAUDE_INPUT_TEXT", "")
        if input_text:
            violations = check_language_usage(input_text)
            if violations:
                error_response = {
                    "allow": False,
                    "error": "🔴 言語使用ルール違反",
                    "message": (
                        "🔴 言語使用ルール違反が検出されました：\n\n"
                        + "\n".join(
                            f"• {v['type']}: {v['matches']}" for v in violations
                        )
                        + "\n\n【正しい使い方】\n"
                        + "• 処理内容: 英語のみ\n"
                        + "• 宣言・報告: 日本語のみ\n"
                        + "• 混合使用: 禁止\n\n"
                        + "例: 'Let me implement this feature' → 'この機能を実装します'"
                    ),
                    "required_action": "言語使用ルール修正",
                    "blocked_tool": tool_name,
                    "violations": violations,
                }
                print(json.dumps(error_response))
                return

        # PRESIDENT宣言前は絶対に最小限ツールのみ許可
        # 🚨 最大の課題解決: 宣言なしでは何もできない 🚨
        essential_tools = ["Bash"]  # Read, LS も制限
        if tool_name in essential_tools:
            # Bashの場合は宣言関連のみ
            if tool_name == "Bash":
                try:
                    # 環境変数から確認
                    bash_command = os.environ.get("CLAUDE_BASH_COMMAND", "")
                    allowed_commands = [
                        "secure-president-declare",
                        "president-declare",
                        "make declare-president",
                        "python3 scripts/utilities/secure-president-declare.py",
                    ]
                    if any(keyword in bash_command for keyword in allowed_commands):
                        print(json.dumps({"allow": True}))
                        return
                    else:
                        # 宣言関連以外のBashは完全ブロック
                        pass
                except Exception:
                    pass

        # PRESIDENT宣言チェック - より厳格な判定
        if not is_president_declared():
            error_response = {
                "allow": False,
                "error": "🔴 PRESIDENT必須宣言未完了",
                "message": (
                    "🔴 セキュアPRESIDENT宣言が必要です。\n\n"
                    "宣言手順：\n"
                    "1. make declare-president\n"
                    "2. または: python3 scripts/utilities/secure-president-declare.py\n\n"
                    "⚠️ 宣言用Bashのみ使用可能です。\n"
                    "⚠️ Read/LS/Edit/Write/Task等は全てブロックされます。\n"
                    "✅ 宣言後、全てのツールが安全に使用可能になります。"
                ),
                "required_action": "make declare-president 実行",
                "blocked_tool": tool_name,
                "hint": "宣言後に全ツールが使用可能になります",
            }
            print(json.dumps(error_response))
            return

        # 組織整理状態チェック（PRESIDENT宣言後）
        org_ok, org_issues = comprehensive_organization_check()
        if not org_ok:
            error_response = {
                "allow": False,
                "error": "🔴 プロジェクト組織未完了",
                "message": (
                    "🔴 プロジェクト組織に問題があります：\n\n"
                    + "\n".join(f"• {issue}" for issue in org_issues)
                    + "\n\n組織ルール確認: docs/03_processes/file-organization-rules.md"
                ),
                "required_action": "組織問題修正",
                "blocked_tool": tool_name,
                "organization_issues": org_issues,
            }
            print(json.dumps(error_response))
            return

        # 宣言済みの場合は通常処理継続
        print(json.dumps({"allow": True}))

    except Exception as e:
        # エラー時も安全にブロック
        error_response = {
            "allow": False,
            "error": f"PRESIDENT宣言チェックエラー: {str(e)}",
            "message": "安全のためツール使用をブロックしました",
        }
        print(json.dumps(error_response))


if __name__ == "__main__":
    main()
