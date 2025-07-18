#!/usr/bin/env python3
"""
実行エラーの詳細取得
"""

import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()


def get_execution_error():
    """最新実行のエラー詳細取得"""

    base_url = "https://dd1107.app.n8n.cloud"
    api_key = os.getenv("N8N_API_KEY")
    headers = {
        "X-N8N-API-KEY": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    workflow_id = "h5TN1MoxQ6XrYLXA"

    print("🔍 実行エラー詳細取得")
    print("=" * 30)

    # 最新実行取得
    response = requests.get(
        f"{base_url}/api/v1/executions?limit=1&workflowId={workflow_id}",
        headers=headers,
    )

    if response.status_code == 200:
        executions = response.json().get("data", [])

        if executions:
            latest = executions[0]
            exec_id = latest.get("id")

            print(f"📋 最新実行ID: {exec_id}")
            print(f"   Status: {latest.get('status')}")

            # 詳細データ取得
            detail_response = requests.get(
                f"{base_url}/api/v1/executions/{exec_id}", headers=headers
            )

            if detail_response.status_code == 200:
                detail = detail_response.json()

                # 完全なJSON構造をダンプ
                print("\n📄 完全な実行データ:")
                print("=" * 50)
                print(json.dumps(detail, indent=2, ensure_ascii=False))

                return True
            else:
                print(f"❌ 詳細取得失敗: {detail_response.status_code}")
                return False
        else:
            print("⚠️ 実行履歴なし")
            return False
    else:
        print(f"❌ 実行履歴取得失敗: {response.status_code}")
        return False


if __name__ == "__main__":
    get_execution_error()
