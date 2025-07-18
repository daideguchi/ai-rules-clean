#!/usr/bin/env python3
"""
Supabaseテーブル構造に完全準拠したワークフロー作成
"""

import os
import time
from datetime import datetime

import requests
from dotenv import load_dotenv

load_dotenv()


def create_perfect_workflow():
    """Supabase実構造に完全準拠したワークフロー作成"""

    base_url = "https://dd1107.app.n8n.cloud"
    api_key = os.getenv("N8N_API_KEY")
    headers = {
        "X-N8N-API-KEY": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    timestamp = int(datetime.now().timestamp())
    workflow_name = f"Perfect AI v{timestamp}"
    webhook_path = f"perfect-ai-{timestamp}"

    print("🎯 完全準拠ワークフロー作成")
    print("=" * 50)
    print(f"名前: {workflow_name}")
    print(f"Path: {webhook_path}")

    # Webhookノード
    webhook_node = {
        "parameters": {
            "httpMethod": "POST",
            "path": webhook_path,
            "responseMode": "onReceived",
        },
        "id": "perfect_webhook",
        "name": "Perfect Webhook",
        "type": "n8n-nodes-base.webhook",
        "typeVersion": 1,
        "position": [240, 300],
    }

    # Supabase実構造準拠のHTTP Requestノード
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")

    http_node = {
        "parameters": {
            "url": f"{supabase_url}/rest/v1/ai_performance_log",
            "requestMethod": "POST",
            "sendHeaders": True,
            "headerParameters": {
                "parameters": [
                    {"name": "apikey", "value": supabase_key},
                    {"name": "Authorization", "value": f"Bearer {supabase_key}"},
                    {"name": "Content-Type", "value": "application/json"},
                    {"name": "Prefer", "value": "return=minimal"},
                ]
            },
            "sendBody": True,
            "bodyContentType": "json",
            "jsonParameters": True,
            "bodyParameters": {
                "parameters": [
                    {"name": "session_id", "value": "={{$json.session_id}}"},
                    {"name": "task_success", "value": "={{$json.task_success}}"},
                    {"name": "execution_time", "value": "={{$json.execution_time}}"},
                    {"name": "tool_calls", "value": "={{$json.tool_calls}}"},
                    {
                        "name": "tool_calls_count",
                        "value": "={{$json.tool_calls.length}}",
                    },
                    {"name": "error_count", "value": "={{$json.error_count}}"},
                    {
                        "name": "thinking_tag_used",
                        "value": "={{$json.thinking_tag_used}}",
                    },
                    {"name": "todo_tracking", "value": "={{$json.todo_tracking}}"},
                    {"name": "task_complexity", "value": "={{$json.task_complexity}}"},
                    {"name": "learning_score", "value": "={{$json.learning_score}}"},
                ]
            },
        },
        "id": "perfect_supabase",
        "name": "Perfect Supabase",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.1,
        "position": [440, 300],
    }

    # ワークフロー定義
    workflow_data = {
        "name": workflow_name,
        "nodes": [webhook_node, http_node],
        "connections": {
            "Perfect Webhook": {
                "main": [[{"node": "Perfect Supabase", "type": "main", "index": 0}]]
            }
        },
        "settings": {},
    }

    # 作成
    response = requests.post(
        f"{base_url}/api/v1/workflows", headers=headers, json=workflow_data
    )

    if response.status_code in [200, 201]:
        result = response.json()
        workflow_id = result["id"]

        print(f"✅ ワークフロー作成成功: {workflow_id}")

        # アクティブ化（API制限により手動が必要）
        activate_response = requests.post(
            f"{base_url}/api/v1/workflows/{workflow_id}/activate", headers=headers
        )
        print(f"⚡ アクティブ化試行: {activate_response.status_code}")

        webhook_url = f"{base_url}/webhook/{webhook_path}"

        print(f"📡 Webhook URL: {webhook_url}")
        print(
            "🔧 手動アクティブ化が必要: n8n UIでワークフローを手動でアクティブ化してください"
        )

        return True, webhook_url, workflow_id, workflow_name
    else:
        print(f"❌ 作成失敗: {response.status_code} - {response.text}")
        return False, None, None, None


def test_perfect_integration(webhook_url):
    """完全準拠統合テスト"""

    timestamp = int(time.time())

    print("\n🧪 完全準拠統合テスト")
    print("=" * 30)

    test_data = {
        "session_id": f"perfect_test_{timestamp}",
        "task_success": True,
        "execution_time": 8.5,
        "tool_calls": ["Bash", "Write", "Read"],
        "error_count": 0,
        "thinking_tag_used": True,
        "todo_tracking": True,
        "task_complexity": "high",
        "learning_score": 9.5,
    }

    print(f"📤 送信: {test_data['session_id']}")
    print(f"🔗 URL: {webhook_url}")

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
                "Authorization": f"Bearer {os.getenv('SUPABASE_ANON_KEY')}",
            }

            check_response = requests.get(
                f"{os.getenv('SUPABASE_URL')}/rest/v1/ai_performance_log?session_id=eq.{test_data['session_id']}",
                headers=supabase_headers,
            )

            print(f"   Supabase確認 Status: {check_response.status_code}")

            if check_response.status_code == 200 and check_response.json():
                print("   🎉 **Supabaseデータ確認成功**")
                print("\n🎊 **完全準拠統合成功** 🎊")
                print(f"📡 本番URL: {webhook_url}")
                print("🔄 Claude→n8n→Supabase自動化達成")
                print("🧠 自律AI成長システム稼働開始")
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
    success, url, workflow_id, name = create_perfect_workflow()

    if success:
        print("\n🎯 **完全準拠ワークフロー作成成功**")
        print(f"📡 URL: {url}")
        print(f"🆔 ワークフローID: {workflow_id}")
        print(f"📝 名前: {name}")
        print("\n⚠️ 次のステップ:")
        print("1. n8n UIでワークフローを手動アクティブ化")
        print("2. アクティブ化後にテスト実行")

        # ユーザーがアクティブ化したかを確認
        input_response = input("\nワークフローをアクティブ化しましたか？ (y/n): ")
        if input_response.lower() == "y":
            test_success = test_perfect_integration(url)
            if test_success:
                print("\n🎊 **完全統合達成** 🎊")
            else:
                print("\n⚠️ **統合テスト要再確認**")
    else:
        print("\n❌ **ワークフロー作成失敗**")
