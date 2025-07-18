#!/usr/bin/env python3
"""
作成されたワークフローの長時間待機後テスト
"""

import os
import time
from datetime import datetime

import requests
from dotenv import load_dotenv

load_dotenv()


def find_latest_workflow():
    """最新のClaude関連ワークフローを検索"""

    base_url = "https://dd1107.app.n8n.cloud"
    api_key = os.getenv("N8N_API_KEY")
    headers = {
        "X-N8N-API-KEY": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    response = requests.get(f"{base_url}/api/v1/workflows?limit=250", headers=headers)
    workflows = response.json().get("data", [])

    latest_workflow = None
    for workflow in workflows:
        name = workflow.get("name", "")
        if "Claude Fresh AI Growth" in name:
            latest_workflow = workflow
            break

    return latest_workflow, headers, base_url


def detailed_workflow_check(workflow, headers, base_url):
    """ワークフローの詳細確認"""

    workflow_id = workflow["id"]
    workflow_name = workflow["name"]

    print("🔍 詳細ワークフロー確認")
    print(f"   名前: {workflow_name}")
    print(f"   ID: {workflow_id}")
    print(f"   作成日: {workflow.get('createdAt')}")
    print(f"   更新日: {workflow.get('updatedAt')}")
    print(f"   Active: {workflow.get('active')}")

    # 詳細情報取得
    detail_response = requests.get(
        f"{base_url}/api/v1/workflows/{workflow_id}", headers=headers
    )

    if detail_response.status_code == 200:
        detail = detail_response.json()

        print(f"   詳細Active: {detail.get('active')}")
        print(f"   ノード数: {len(detail.get('nodes', []))}")

        # Webhookノード確認
        for node in detail.get("nodes", []):
            if node.get("type") == "n8n-nodes-base.webhook":
                webhook_path = node.get("parameters", {}).get("path")
                print(f"   Webhook Path: {webhook_path}")
                return f"{base_url}/webhook/{webhook_path}"

    return None


def multiple_activation_attempts(workflow_id, headers, base_url):
    """複数回アクティブ化試行"""

    print("🔄 複数回アクティブ化試行")

    methods = [
        (
            "POST /activate",
            lambda: requests.post(
                f"{base_url}/api/v1/workflows/{workflow_id}/activate", headers=headers
            ),
        ),
        (
            "PUT active=true",
            lambda: requests.put(
                f"{base_url}/api/v1/workflows/{workflow_id}",
                headers=headers,
                json={"active": True},
            ),
        ),
        (
            "PATCH active=true",
            lambda: requests.patch(
                f"{base_url}/api/v1/workflows/{workflow_id}",
                headers=headers,
                json={"active": True},
            ),
        ),
    ]

    for i, (method_name, method_func) in enumerate(methods, 1):
        print(f"   試行 {i}: {method_name}")

        try:
            response = method_func()
            print(f"      Status: {response.status_code}")

            if response.status_code == 200:
                print("      ✅ 成功")

                # 確認
                time.sleep(2)
                check_response = requests.get(
                    f"{base_url}/api/v1/workflows/{workflow_id}", headers=headers
                )
                if check_response.status_code == 200:
                    active_status = check_response.json().get("active", False)
                    print(f"      確認結果: Active = {active_status}")

                    if active_status:
                        return True
            else:
                print("      ❌ 失敗")

        except Exception as e:
            print(f"      ❌ エラー: {e}")

    return False


def long_wait_test(webhook_url, max_attempts=6, wait_interval=30):
    """長時間待機テスト"""

    print("⏳ 長時間待機テスト開始")
    print(f"   最大試行回数: {max_attempts}")
    print(f"   待機間隔: {wait_interval}秒")
    print(f"   対象URL: {webhook_url}")

    test_data = {
        "session_id": f"long_wait_test_{int(datetime.now().timestamp())}",
        "success": True,
        "execution_time": 1.0,
        "tools_used": ["long_wait", "retry"],
        "error_count": 0,
        "thinking_tag_used": True,
        "todo_tracking": True,
        "task_complexity": "simple",
        "learning_score": 1,
    }

    for attempt in range(1, max_attempts + 1):
        print(f"\n📡 試行 {attempt}/{max_attempts}")

        try:
            response = requests.post(webhook_url, json=test_data, timeout=15)
            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                print("   ✅ 成功！Webhookが応答しました")

                # Supabase確認
                print("   🔍 Supabaseデータ確認...")
                time.sleep(3)

                supabase_url = os.getenv("SUPABASE_URL")
                supabase_anon_key = os.getenv("SUPABASE_ANON_KEY")

                supabase_headers = {
                    "apikey": supabase_anon_key,
                    "Authorization": f"Bearer {supabase_anon_key}",
                    "Content-Type": "application/json",
                }

                check_url = f"{supabase_url}/rest/v1/ai_performance_log?session_id=eq.{test_data['session_id']}"
                check_response = requests.get(check_url, headers=supabase_headers)

                if check_response.status_code == 200 and check_response.json():
                    print("   ✅ Supabaseデータも確認成功")
                    return True
                else:
                    print("   ⚠️ Webhookは成功したがSupabaseデータなし")
                    return False
            else:
                print(f"   ❌ 失敗: {response.status_code}")
                if attempt < max_attempts:
                    print(f"   ⏳ {wait_interval}秒待機...")
                    time.sleep(wait_interval)

        except Exception as e:
            print(f"   ❌ エラー: {e}")
            if attempt < max_attempts:
                print(f"   ⏳ {wait_interval}秒待機...")
                time.sleep(wait_interval)

    print("\n❌ 全ての試行が失敗しました")
    return False


def main():
    print("⏳ n8nワークフロー長時間待機テスト")
    print("=" * 60)

    # 1. 最新ワークフロー検索
    workflow, headers, base_url = find_latest_workflow()

    if not workflow:
        print("❌ 対象ワークフローが見つかりません")
        return False

    # 2. 詳細確認
    webhook_url = detailed_workflow_check(workflow, headers, base_url)

    if not webhook_url:
        print("❌ Webhook URL取得失敗")
        return False

    print(f"\n{'=' * 60}")

    # 3. 複数回アクティブ化試行
    activation_success = multiple_activation_attempts(workflow["id"], headers, base_url)

    print(f"\n{'=' * 60}")

    # 4. 長時間待機テスト
    test_success = long_wait_test(webhook_url)

    print("\n🎯 最終結果:")
    print(f"  - アクティブ化: {'✅ 成功' if activation_success else '❌ 失敗'}")
    print(f"  - 統合テスト: {'✅ 成功' if test_success else '❌ 失敗'}")

    if test_success:
        print("\n🎉 **長時間待機テスト成功**")
        print("   n8n→Supabase統合が正常動作")
        print(f"   使用可能URL: {webhook_url}")
    else:
        print("\n🚨 **統合依然として失敗**")
        print("   n8nの設定に根本的な問題がある可能性")

    return test_success


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
