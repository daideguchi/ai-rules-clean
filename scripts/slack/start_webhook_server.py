#!/usr/bin/env python3
"""
🚀 Slack Webhook Server Starter
===============================
Slackイベント受信用Webhookサーバーを起動
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

# Load environment variables from .env file
load_dotenv()

# Import and run Flask app
from scripts.mcp.slack_mcp_server import app  # noqa: E402

if __name__ == "__main__":
    # Get configuration from environment
    port = int(os.environ.get('WEBHOOK_PORT', 5001))
    host = os.environ.get('WEBHOOK_HOST', '0.0.0.0')
    debug = os.environ.get('DEBUG', 'true').lower() == 'true'

    print("🚀 Starting Slack Webhook Server...")
    print("=" * 40)
    print(f"🔗 Bot Token: {os.environ.get('SLACK_BOT_TOKEN', 'Not set')[:20]}...")
    print(f"🔐 Signing Secret: {'Set' if os.environ.get('SLACK_SIGNING_SECRET') else 'Not set'}")
    print(f"📡 Server will run on: http://{host}:{port}")
    print(f"🌐 Webhook endpoint: http://{host}:{port}/slack/events")
    print("\n💡 For external access, use ngrok:")
    print(f"   ngrok http {port}")
    print("\n🎯 Test by typing 'タスク' in Slack!")
    print("=" * 40)

    # Run Flask app
    app.run(
        host=host,
        port=port,
        debug=debug
    )
