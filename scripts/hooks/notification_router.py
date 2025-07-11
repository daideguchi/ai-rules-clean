#!/usr/bin/env python3
"""
📢 Notification Router Hook
通知の最適化とルーティング
"""

import datetime
import json
import sys
from pathlib import Path


def categorize_notification(message: str, title: str) -> dict:
    """通知の分類と重要度判定"""

    category = "general"
    priority = "normal"
    action_required = False

    # メッセージ内容による分類
    message_lower = message.lower()
    title.lower()

    # エラー・警告系
    if any(
        keyword in message_lower
        for keyword in ["error", "failed", "exception", "critical"]
    ):
        category = "error"
        priority = "high"
        action_required = True
    elif any(
        keyword in message_lower for keyword in ["warning", "caution", "attention"]
    ):
        category = "warning"
        priority = "medium"

    # セキュリティ系
    elif any(
        keyword in message_lower
        for keyword in ["security", "unauthorized", "forbidden", "blocked"]
    ):
        category = "security"
        priority = "high"
        action_required = True

    # 完了・成功系
    elif any(
        keyword in message_lower
        for keyword in ["completed", "success", "finished", "done"]
    ):
        category = "success"
        priority = "low"

    # タスク・作業系
    elif any(
        keyword in message_lower
        for keyword in ["task", "waiting", "input", "permission"]
    ):
        category = "task"
        priority = "medium"
        action_required = True

    return {
        "category": category,
        "priority": priority,
        "action_required": action_required,
        "should_notify": priority in ["high", "medium"] or action_required,
    }


def format_notification(message: str, title: str, classification: dict) -> str:
    """通知メッセージのフォーマット"""

    # アイコンマッピング
    icons = {
        "error": "🚨",
        "warning": "⚠️",
        "security": "🔒",
        "success": "✅",
        "task": "📋",
        "general": "ℹ️",
    }

    # 優先度インジケーター
    priority_indicators = {"high": "🔴", "medium": "🟡", "low": "🟢"}

    icon = icons.get(classification["category"], "ℹ️")
    priority_icon = priority_indicators.get(classification["priority"], "⚪")

    formatted = f"{icon} {priority_icon} {title}\\n{message}"

    if classification["action_required"]:
        formatted += "\\n👆 Action Required"

    return formatted


def should_suppress_notification(message: str, title: str) -> bool:
    """通知抑制の判定"""

    # 重複通知の抑制（簡易実装）
    suppress_patterns = [
        "Waiting for input",
        "File saved successfully",
        "Command completed",
    ]

    for pattern in suppress_patterns:
        if pattern.lower() in message.lower() or pattern.lower() in title.lower():
            return True

    return False


def log_notification(message: str, title: str, classification: dict, session_id: str):
    """通知ログの記録"""

    log_dir = Path("src/runtime/logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "notifications.jsonl"

    log_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "session_id": session_id,
        "title": title,
        "message": message,
        "category": classification["category"],
        "priority": classification["priority"],
        "action_required": classification["action_required"],
    }

    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\\n")
    except Exception as e:
        print(f"⚠️  Failed to log notification: {e}", file=sys.stderr)


def main():
    try:
        # Hookからの入力を取得
        input_data = json.load(sys.stdin)

        message = input_data.get("message", "")
        title = input_data.get("title", "Claude Code")
        session_id = input_data.get("session_id", "unknown")

        if not message:
            sys.exit(0)

        # 通知の分類
        classification = categorize_notification(message, title)

        # 抑制判定
        if should_suppress_notification(message, title):
            print("🔇 Notification suppressed (duplicate/low-value)")
            sys.exit(0)

        # ログ記録
        log_notification(message, title, classification, session_id)

        # 通知のフォーマット
        if classification["should_notify"]:
            formatted_message = format_notification(message, title, classification)
            print(f"📢 Notification Router:\\n{formatted_message}")
        else:
            print(f"📝 Low-priority notification logged: {title}")

        sys.exit(0)

    except json.JSONDecodeError as e:
        print(f"❌ Hook Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Hook Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
