#!/usr/bin/env python3
"""
手動確認用 - 現在のワークフロー状態詳細確認
"""

import os

import requests
from dotenv import load_dotenv

load_dotenv()


def verify_current_state():
    """現在の状態を詳細確認"""

    base_url = "https://dd1107.app.n8n.cloud"
    api_key = os.getenv("N8N_API_KEY")
    headers = {
        "X-N8N-API-KEY": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    print("🔍 現在のワークフロー状態詳細確認")
    print("=" * 60)

    # 全ワークフロー確認
    response = requests.get(f"{base_url}/api/v1/workflows?limit=250", headers=headers)
    workflows = response.json().get("data", [])

    print(f"📊 総ワークフロー数: {len(workflows)}")

    for i, wf in enumerate(workflows, 1):
        name = wf.get("name", "")
        if "claude" in name.lower() or "working" in name.lower():
            wf_id = wf["id"]
            active = wf.get("active", False)

            print(f"\n{i}. 【{name}】")
            print(f"   ID: {wf_id}")
            print(f"   Active: {active}")
            print(f"   Created: {wf.get('createdAt')}")

            # 詳細確認
            detail_response = requests.get(
                f"{base_url}/api/v1/workflows/{wf_id}", headers=headers
            )
            if detail_response.status_code == 200:
                detail = detail_response.json()

                print(f"   詳細Active: {detail.get('active')}")
                print(f"   ノード数: {len(detail.get('nodes', []))}")

                # Webhookノード確認
                for node in detail.get("nodes", []):
                    if node.get("type") == "n8n-nodes-base.webhook":
                        webhook_path = node.get("parameters", {}).get("path", "N/A")
                        print(f"   🌐 Webhook Path: /{webhook_path}")
                        print(f"   📡 Test URL: {base_url}/webhook-test/{webhook_path}")
                        print(f"   🎯 Prod URL: {base_url}/webhook/{webhook_path}")

                # 最近の実行確認
                exec_response = requests.get(
                    f"{base_url}/api/v1/executions?limit=3&workflowId={wf_id}",
                    headers=headers,
                )

                if exec_response.status_code == 200:
                    executions = exec_response.json().get("data", [])
                    print(f"   📋 最近の実行: {len(executions)}件")

                    for exec_data in executions[:2]:
                        print(
                            f"      - {exec_data.get('status', 'N/A')} ({exec_data.get('mode', 'N/A')})"
                        )

            print("   " + "-" * 50)


def manual_instructions():
    """手動対応指示"""

    print("\n🔧 手動対応が必要です")
    print("=" * 40)

    print("1. **n8n UIでワークフロー確認**:")
    print("   https://dd1107.app.n8n.cloud")

    print("\n2. **「Working Claude AI v1752496422」を開く**")

    print("\n3. **右上のトグルスイッチ確認**:")
    print("   - 現在: Inactive（グレー）の可能性")
    print("   - 手動でActive（緑）に切り替え")

    print("\n4. **確認後、以下を実行**:")
    print(
        "   curl -X POST 'https://dd1107.app.n8n.cloud/webhook/working-claude-1752496422' \\"
    )
    print("     -H 'Content-Type: application/json' \\")
    print(
        '     -d \'{"session_id":"manual_ui_test","success":true,"execution_time":1.0,"tools_used":"manual","error_count":0,"thinking_tag_used":true,"todo_tracking":true,"task_complexity":"simple","learning_score":5}\''
    )

    print("\n5. **成功確認**:")
    print('   - 応答: {"message":"Workflow was started"}')
    print("   - Supabaseデータ確認")


if __name__ == "__main__":
    verify_current_state()
    manual_instructions()
