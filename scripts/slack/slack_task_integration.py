#!/usr/bin/env python3
"""
🔗 Slack Task Integration - Quick Setup & Test
=============================================
Slack連携でタスク管理システムを簡単にセットアップ・テストするスクリプト
"""

import asyncio
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

# Load environment variables from .env file
load_dotenv()

from scripts.mcp.slack_mcp_server import SlackMCPServer


def setup_slack_integration():
    """Slack統合のセットアップガイド"""
    print("🔗 Slack Task Integration Setup")
    print("=" * 40)

    # Check environment variables
    bot_token = os.getenv("SLACK_BOT_TOKEN")
    signing_secret = os.getenv("SLACK_SIGNING_SECRET")

    print("📋 Current Configuration:")
    print(f"  SLACK_BOT_TOKEN: {'✅ Set' if bot_token else '❌ Not set'}")
    print(f"  SLACK_SIGNING_SECRET: {'✅ Set' if signing_secret else '❌ Not set'}")

    if not bot_token or not signing_secret:
        print("\n🔧 Setup Required:")
        print("1. Go to https://api.slack.com/apps")
        print("2. Create a new app or select existing app")
        print("3. Go to 'OAuth & Permissions' and copy Bot User OAuth Token")
        print("4. Go to 'Basic Information' and copy Signing Secret")
        print("5. Set environment variables:")
        print("   export SLACK_BOT_TOKEN=xoxb-your-bot-token")
        print("   export SLACK_SIGNING_SECRET=your-signing-secret")
        print("\n6. Required Bot Token Scopes:")
        print("   - chat:write")
        print("   - channels:read")
        print("   - groups:read")
        print("   - im:read")
        print("   - mpim:read")
        return False

    return True

async def test_task_integration():
    """タスク統合のテスト"""
    print("\n🧪 Testing Task Integration...")

    project_root = Path.cwd()
    slack_server = SlackMCPServer(project_root)

    # Test connection
    print("1. Testing Slack connection...")
    connection_result = await slack_server.test_connection()

    if connection_result.get("connection_status") != "success":
        print(f"❌ Connection failed: {connection_result.get('error_message')}")
        return False

    print("✅ Slack connection successful!")

    # Test task retrieval
    print("2. Testing task retrieval...")
    task_list = slack_server.get_current_tasks()
    print("✅ Task list generated:")
    print(task_list[:200] + "..." if len(task_list) > 200 else task_list)

    return True

def create_sample_tasks():
    """サンプルタスクを作成"""
    print("\n📝 Creating sample tasks for testing...")

    # Create sample tasks in runtime task queue
    task_queue_dir = Path("src/runtime/task-queue")
    task_queue_dir.mkdir(parents=True, exist_ok=True)

    sample_tasks = {
        "tasks": [
            {
                "id": 1,
                "description": "Slack統合テスト完了",
                "priority": "high",
                "status": "in_progress",
                "created_at": "2025-01-16T12:00:00+09:00"
            },
            {
                "id": 2,
                "description": "タスク管理システム改善",
                "priority": "normal",
                "status": "pending",
                "created_at": "2025-01-16T12:05:00+09:00"
            },
            {
                "id": 3,
                "description": "ドキュメント更新",
                "priority": "low",
                "status": "pending",
                "created_at": "2025-01-16T12:10:00+09:00"
            }
        ],
        "next_id": 4
    }

    with open(task_queue_dir / "tasks.json", "w", encoding="utf-8") as f:
        json.dump(sample_tasks, f, ensure_ascii=False, indent=2)

    print("✅ Sample tasks created in src/runtime/task-queue/tasks.json")

def show_usage_guide():
    """使用方法ガイド"""
    print("\n📖 Usage Guide:")
    print("=" * 40)
    print("1. Slackでタスクを確認:")
    print("   - 「タスク」「task」「todo」「やること」のいずれかを投稿")
    print("   - ボットが現在のタスク一覧を返信")
    print("\n2. 利用可能なMakeコマンド:")
    print("   make slack-test          # Slack接続テスト")
    print("   make slack-send-test     # テストメッセージ送信")
    print("   make slack-status        # Slack統合状況確認")
    print("\n3. タスク管理コマンド:")
    print("   python scripts/tools/system/kanban-board.py add \"新しいタスク\"")
    print("   python scripts/tools/system/kanban-board.py show")
    print("   python scripts/tools/system/kanban-board.py report")
    print("\n4. Slack Event URL設定 (Webhook):")
    print("   https://your-domain.com/slack/events")
    print("   (ngrokやCloudflare Tunnelを使用してローカル開発)")

async def main():
    """メイン処理"""
    print("🤖 Slack Task Integration for coding-rule2")
    print("=" * 50)

    # Setup check
    if not setup_slack_integration():
        return

    # Create sample tasks
    create_sample_tasks()

    # Test integration
    success = await test_task_integration()

    if success:
        print("\n🎉 Slack Task Integration Setup Complete!")
        show_usage_guide()

        print("\n🚀 Next Steps:")
        print("1. Start Flask server for webhook:")
        print("   cd scripts/mcp && python slack_mcp_server.py")
        print("2. Use ngrok to expose webhook:")
        print("   ngrok http 5000")
        print("3. Set webhook URL in Slack app settings")
        print("4. Test by typing 'タスク' in Slack channel")
    else:
        print("\n❌ Setup incomplete. Please check configuration.")

if __name__ == "__main__":
    asyncio.run(main())
