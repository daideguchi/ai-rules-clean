#!/usr/bin/env python3
"""
ワークフローの強制アクティブ化スクリプト
"""

import os
import time

import requests
from dotenv import load_dotenv

load_dotenv()


def force_activate_workflow():
    """ワークフローを強制的にアクティブ化"""

    base_url = "https://dd1107.app.n8n.cloud"
    api_key = os.getenv("N8N_API_KEY")
    headers = {
        "X-N8N-API-KEY": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    print("🔧 ワークフロー強制アクティブ化開始")

    # 1. ワークフロー検索
    response = requests.get(f"{base_url}/api/v1/workflows?limit=250", headers=headers)
    workflows = response.json().get("data", [])

    target_workflow = None
    for workflow in workflows:
        if "Claude Performance Rebuilt" in workflow.get("name", ""):
            target_workflow = workflow
            break

    if not target_workflow:
        print("❌ 対象ワークフローが見つかりません")
        return False

    workflow_id = target_workflow["id"]
    workflow_name = target_workflow["name"]
    current_active = target_workflow.get("active", False)

    print("📋 対象ワークフロー:")
    print(f"   名前: {workflow_name}")
    print(f"   ID: {workflow_id}")
    print(f"   現在のActive状態: {current_active}")

    if current_active:
        print("   ✅ 既にアクティブ状態です")
        return True

    # 2. 複数の方法でアクティブ化を試行
    print("\n🚀 アクティブ化試行開始...")

    # 方法1: POST /activate
    print("   方法1: POST /activate エンドポイント")
    activate_response1 = requests.post(
        f"{base_url}/api/v1/workflows/{workflow_id}/activate", headers=headers
    )
    print(f"   Status: {activate_response1.status_code}")

    # 方法2: PUT with active=True
    print("   方法2: PUT with active=True")
    activate_response2 = requests.put(
        f"{base_url}/api/v1/workflows/{workflow_id}",
        headers=headers,
        json={"active": True},
    )
    print(f"   Status: {activate_response2.status_code}")

    # 方法3: PATCH with active=True
    print("   方法3: PATCH with active=True")
    activate_response3 = requests.patch(
        f"{base_url}/api/v1/workflows/{workflow_id}",
        headers=headers,
        json={"active": True},
    )
    print(f"   Status: {activate_response3.status_code}")

    # 3. 結果確認
    time.sleep(2)  # 少し待つ

    print("\n🔍 結果確認...")
    check_response = requests.get(
        f"{base_url}/api/v1/workflows/{workflow_id}", headers=headers
    )

    if check_response.status_code == 200:
        check_data = check_response.json()
        new_active_status = check_data.get("active", False)

        print(f"   新しいActive状態: {new_active_status}")

        if new_active_status:
            print("   ✅ アクティブ化成功！")

            # Webhookテスト
            print("\n🧪 Webhook即座テスト...")
            webhook_url = (
                "https://dd1107.app.n8n.cloud/webhook/claude-performance-rebuild"
            )
            test_data = {"session_id": "activation_test", "success": True}

            test_response = requests.post(webhook_url, json=test_data, timeout=10)
            print(f"   Webhook Status: {test_response.status_code}")

            if test_response.status_code == 200:
                print("   ✅ Webhook正常動作確認")
                return True
            else:
                print("   ❌ Webhookまだ動作せず")
                return False
        else:
            print("   ❌ アクティブ化失敗")
            return False
    else:
        print(f"   ❌ 確認取得失敗: {check_response.status_code}")
        return False


def main():
    print("🔧 n8nワークフロー強制アクティブ化")
    print("=" * 50)

    success = force_activate_workflow()

    if success:
        print("\n🎉 **アクティブ化完全成功**")
        print("   ワークフローが正常に動作しています")
    else:
        print("\n🚨 **アクティブ化失敗**")
        print("   手動での確認が必要です")

    return success


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
