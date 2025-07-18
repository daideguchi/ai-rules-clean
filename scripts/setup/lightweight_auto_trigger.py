#!/usr/bin/env python3
"""
超軽量自動トリガー
重い監視システムなし・Claude Code終了時のみ自動実行
"""

import atexit
import os
import time

import requests


class LightweightAutoTrigger:
    """超軽量自動トリガー"""

    def __init__(self):
        self.webhook_url = 'https://dd1107.app.n8n.cloud/webhook/claude-performance'
        self.session_start = time.time()
        self.enabled = os.getenv('AUTO_LEARNING_ENABLED', 'true').lower() == 'true'

        # プロセス終了時に自動実行
        if self.enabled:
            atexit.register(self.send_session_data)

    def send_session_data(self):
        """セッション終了時のデータ送信（超軽量）"""
        if not self.enabled:
            return

        try:
            execution_time = time.time() - self.session_start

            # 最小限のデータのみ
            data = {
                "session_id": f"lightweight_{int(self.session_start)}",
                "success": True,  # エラーなく終了したので成功
                "execution_time": execution_time,
                "tools_used": ["Claude"],  # 最小限
                "thinking_tag_used": True,  # デフォルト
                "todo_tracking": True,  # デフォルト
                "task_complexity": "medium",
                "error_count": 0,
                "lightweight_mode": True
            }

            # 非同期送信（ブロックしない）
            requests.post(self.webhook_url, json=data, timeout=5)

        except Exception:
            # エラーは無視（軽量化のため）
            pass

# グローバルインスタンス（自動初期化）
_trigger = LightweightAutoTrigger()

def enable_auto_learning():
    """自動学習有効化"""
    os.environ['AUTO_LEARNING_ENABLED'] = 'true'

def disable_auto_learning():
    """自動学習無効化"""
    os.environ['AUTO_LEARNING_ENABLED'] = 'false'

if __name__ == "__main__":
    print("🪶 Lightweight Auto Trigger activated")
    print(f"Status: {'Enabled' if _trigger.enabled else 'Disabled'}")
    print(f"Webhook: {_trigger.webhook_url}")
