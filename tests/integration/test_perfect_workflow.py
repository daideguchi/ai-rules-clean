#!/usr/bin/env python3
"""
完全準拠ワークフローテスト
"""

import os
import time

import requests
from dotenv import load_dotenv

load_dotenv()

def test_perfect_integration():
    """完全準拠統合テスト"""

    webhook_url = "https://dd1107.app.n8n.cloud/webhook/perfect-ai-1752535562"
    timestamp = int(time.time())

    print("🧪 完全準拠統合テスト")
    print("="*30)
    print(f"📡 URL: {webhook_url}")

    test_data = {
        "session_id": f"perfect_test_{timestamp}",
        "task_success": True,
        "execution_time": 8.5,
        "tool_calls": ["Bash", "Write", "Read"],
        "error_count": 0,
        "thinking_tag_used": True,
        "todo_tracking": True,
        "task_complexity": "high",
        "learning_score": 9.5
    }

    print(f"📤 送信: {test_data['session_id']}")

    try:
        response = requests.post(webhook_url, json=test_data, timeout=20)
        print(f"   Webhook Status: {response.status_code}")
        print(f"   Response: {response.text}")

        if response.status_code == 200:
            print("   ✅ Webhook送信成功")

            # Supabase確認
            print("   ⏳ 15秒待機（データ処理）...")
            time.sleep(15)

            supabase_headers = {
                "apikey": os.getenv("SUPABASE_ANON_KEY"),
                "Authorization": f"Bearer {os.getenv('SUPABASE_ANON_KEY')}"
            }

            check_response = requests.get(
                f"{os.getenv('SUPABASE_URL')}/rest/v1/ai_performance_log?session_id=eq.{test_data['session_id']}",
                headers=supabase_headers
            )

            print(f"   Supabase確認 Status: {check_response.status_code}")

            if check_response.status_code == 200 and check_response.json():
                print("   🎉 **Supabaseデータ確認成功**")
                print("\n🎊 **完全準拠統合成功** 🎊")
                print(f"📡 本番URL: {webhook_url}")
                print("🔄 Claude→n8n→Supabase自動化達成")
                print("🧠 自律AI成長システム稼働開始")
                print("✅ AIパフォーマンスデータ自動蓄積開始")
                return True
            else:
                print("   ⚠️ Supabaseデータ確認失敗")
                print(f"   Response: {check_response.text}")
                return False
        else:
            print("   ❌ Webhook送信失敗")
            return False
    except Exception as e:
        print(f"   ❌ テスト実行エラー: {e}")
        return False

if __name__ == "__main__":
    print("🎯 ワークフローID: fGTBSKXEut8vhU8h")
    print("📝 名前: Perfect AI v1752535562")
    print("⚠️ ワークフローがアクティブ化されていることを確認してください")
    print()

    success = test_perfect_integration()

    if success:
        print("\n🎊 **完全統合達成** 🎊")
        print("🚀 自律AI成長システム稼働開始")
    else:
        print("\n⚠️ **統合テスト要再確認**")
        print("🔧 n8n UIでワークフローのアクティブ化状態を確認してください")
