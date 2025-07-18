#!/usr/bin/env python3
"""
既存の動作実績ワークフローを使用
"""

import os
import time

import requests
from dotenv import load_dotenv

load_dotenv()


def use_existing_workflow():
    """既存ワークフロー（My workflow）を使用"""

    base_url = "https://dd1107.app.n8n.cloud"
    api_key = os.getenv("N8N_API_KEY")
    headers = {
        "X-N8N-API-KEY": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    # 既存ワークフロー: My workflow (ID: cHzlzhsUcNoXMI8q)
    existing_workflow_id = "cHzlzhsUcNoXMI8q"
    webhook_url = "https://dd1107.app.n8n.cloud/webhook/claude-performance"

    print("🔄 既存ワークフロー使用")
    print("=" * 40)
    print("ワークフロー: My workflow")
    print(f"ID: {existing_workflow_id}")
    print(f"Webhook URL: {webhook_url}")

    # 現在の状態確認
    detail_response = requests.get(
        f"{base_url}/api/v1/workflows/{existing_workflow_id}", headers=headers
    )

    if detail_response.status_code == 200:
        workflow_data = detail_response.json()
        current_active = workflow_data.get("active", False)

        print(f"現在のActive状態: {current_active}")

        if not current_active:
            # アクティブ化試行
            print("⚡ アクティブ化試行...")
            activate_response = requests.post(
                f"{base_url}/api/v1/workflows/{existing_workflow_id}/activate",
                headers=headers,
            )
            print(f"   アクティブ化レスポンス: {activate_response.status_code}")

        # 60秒待機
        print("⏳ 60秒待機（完全同期）...")
        for i in range(12):
            print(f"   残り {60 - (i * 5)}秒...", end="\r")
            time.sleep(5)
        print("\n")

        # テスト実行
        print("🧪 既存ワークフローテスト")

        test_data = {
            "session_id": f"existing_workflow_{int(time.time())}",
            "task_success": True,
            "execution_time_seconds": 10.0,
            "tools_used": "existing_workflow",
            "error_count": 0,
            "thinking_tag_used": True,
            "todo_tracking": True,
            "task_complexity": "high",
            "learning_score": 10,
            "session_notes": "Using existing proven workflow",
        }

        print(f"📤 送信: {test_data['session_id']}")

        test_response = requests.post(webhook_url, json=test_data, timeout=20)
        print(f"   Webhook Status: {test_response.status_code}")
        print(f"   Response: {test_response.text}")

        if test_response.status_code == 200:
            print("   ✅ Webhook送信成功")

            # Supabase確認
            print("   ⏳ 15秒待機（データ処理）...")
            time.sleep(15)

            supabase_headers = {
                "apikey": os.getenv("SUPABASE_ANON_KEY"),
                "Authorization": f"Bearer {os.getenv('SUPABASE_ANON_KEY')}",
            }

            check_response = requests.get(
                f"{os.getenv('SUPABASE_URL')}/rest/v1/ai_performance_log?session_id=eq.{test_data['session_id']}",
                headers=supabase_headers,
            )

            print(f"   Supabase確認 Status: {check_response.status_code}")

            if check_response.status_code == 200 and check_response.json():
                print("   🎉 **Supabaseデータ確認成功**")
                print("\n🎊 **既存ワークフロー統合成功** 🎊")
                print(f"📡 使用URL: {webhook_url}")
                print("🔄 Claude→n8n→Supabase自動化達成")
                return True, webhook_url
            else:
                print("   ⚠️ Supabaseデータ確認失敗")
                print(f"   Response: {check_response.text}")
                return False, webhook_url
        else:
            print("   ❌ Webhook送信失敗")
            return False, webhook_url
    else:
        print(f"❌ ワークフロー詳細取得失敗: {detail_response.status_code}")
        return False, None


if __name__ == "__main__":
    success, url = use_existing_workflow()

    if success:
        print("\n🎯 **既存ワークフロー統合成功**")
        print(f"📡 URL: {url}")
        print("✅ 自律AI成長システム稼働開始")
    else:
        print("\n⚠️ **既存ワークフローでも統合未完了**")
        print("🔧 n8n UI手動確認が必要")
