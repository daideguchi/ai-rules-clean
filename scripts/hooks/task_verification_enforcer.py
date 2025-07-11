#!/usr/bin/env python3
"""
タスク検証強制フック - 作業開始前の必須チェック
既存の防止システムを確実に実行させる強制システム
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
VERIFICATION_LOG = (
    PROJECT_ROOT / "runtime" / "ai_api_logs" / "task_verification_enforcer.log"
)


def is_task_sensitive_tool(tool_name):
    """タスク敏感ツールかどうかの判定"""
    task_sensitive_tools = ["Edit", "Write", "MultiEdit", "Bash", "Task"]
    return tool_name in task_sensitive_tools


def check_5_minute_rule_compliance():
    """5分検索ルール遵守チェック"""
    search_log = PROJECT_ROOT / "runtime" / "ai_api_logs" / "search_activity.log"

    if not search_log.exists():
        return False, "検索ログが見つかりません"

    try:
        with open(search_log, encoding="utf-8") as f:
            recent_searches = f.readlines()[-10:]  # 直近10件

        if not recent_searches:
            return False, "最近の検索活動がありません"

        # 最新の検索から5分以内かチェック
        last_search = json.loads(recent_searches[-1])
        last_time = datetime.fromisoformat(last_search["timestamp"])
        elapsed = (datetime.now() - last_time).total_seconds()

        if elapsed > 300:  # 5分
            return False, f"最後の検索から{elapsed / 60:.1f}分経過"

        return True, "5分検索ルール遵守"

    except Exception as e:
        return False, f"検索ログ確認エラー: {e}"


def check_todo_status():
    """Todo状況確認"""
    todo_file = PROJECT_ROOT / "runtime" / "ai_api_logs" / "todo_status.json"

    if not todo_file.exists():
        return False, "Todoファイルが見つかりません"

    try:
        with open(todo_file, encoding="utf-8") as f:
            todos = json.load(f)

        if not todos:
            return False, "タスクが明確化されていません"

        # 進行中のタスクがあるかチェック
        in_progress = [t for t in todos if t.get("status") == "in_progress"]
        if not in_progress:
            return False, "進行中のタスクが不明確"

        return True, f"進行中タスク: {in_progress[0]['content']}"

    except Exception as e:
        return False, f"Todo確認エラー: {e}"


def check_index_md_access():
    """Index.md最近アクセス確認"""
    access_log = PROJECT_ROOT / "runtime" / "ai_api_logs" / "file_access.log"

    if not access_log.exists():
        return False, "アクセスログが見つかりません"

    try:
        with open(access_log, encoding="utf-8") as f:
            recent_accesses = f.readlines()[-20:]  # 直近20件

        index_accesses = [line for line in recent_accesses if "Index.md" in line]
        if not index_accesses:
            return False, "Index.mdへの最近のアクセスがありません"

        return True, "Index.md確認済み"

    except Exception as e:
        return False, f"アクセスログ確認エラー: {e}"


def main():
    """メイン処理"""
    try:
        # 環境変数からツール名取得
        tool_name = os.environ.get("CLAUDE_TOOL_NAME", "unknown")

        # タスク敏感ツールのみチェック
        if not is_task_sensitive_tool(tool_name):
            print(json.dumps({"continue": True}))
            return

        print("🔍 タスク検証強制システム起動", file=sys.stderr)
        print("=" * 40, file=sys.stderr)

        # 必須チェック項目
        checks = [
            ("5分検索ルール", check_5_minute_rule_compliance),
            ("Todo状況", check_todo_status),
            ("Index.md確認", check_index_md_access),
        ]

        failed_checks = []
        for check_name, check_func in checks:
            passed, message = check_func()
            if passed:
                print(f"✅ {check_name}: {message}", file=sys.stderr)
            else:
                print(f"❌ {check_name}: {message}", file=sys.stderr)
                failed_checks.append((check_name, message))

        # 失敗した項目があれば作業をブロック
        if failed_checks:
            error_response = {
                "continue": False,
                "error": "タスク検証失敗",
                "message": (
                    "🚫 作業前の必須チェックに失敗しました。\n\n"
                    "失敗項目:\n"
                    + "\n".join([f"• {name}: {msg}" for name, msg in failed_checks])
                    + "\n\n必須実行項目:\n"
                    "1. TodoRead - 現在のタスクを確認\n"
                    "2. Index.md - 全体状況を確認\n"
                    "3. Grep/Read - 関連情報を5分間検索\n"
                    "4. TodoWrite - タスクを明確化\n\n"
                    "これらを実行してから再試行してください。"
                ),
                "required_actions": [
                    "TodoRead",
                    "Read Index.md",
                    "Grep/Read (5分検索)",
                    "TodoWrite",
                ],
                "blocked_tool": tool_name,
            }

            # ログ記録
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "tool_name": tool_name,
                "status": "blocked",
                "failed_checks": failed_checks,
            }

            VERIFICATION_LOG.parent.mkdir(parents=True, exist_ok=True)
            with open(VERIFICATION_LOG, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

            print(json.dumps(error_response))
            return

        # 全てのチェックが通れば継続
        print("✅ 全ての検証をクリア - 作業継続", file=sys.stderr)

        # 成功ログ記録
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "tool_name": tool_name,
            "status": "passed",
            "checks_passed": len(checks),
        }

        VERIFICATION_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(VERIFICATION_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

        print(json.dumps({"continue": True}))

    except Exception as e:
        # エラー時は安全にブロック
        error_response = {
            "continue": False,
            "error": f"タスク検証システムエラー: {str(e)}",
            "message": "安全のため作業をブロックしました",
        }
        print(json.dumps(error_response))


if __name__ == "__main__":
    main()
