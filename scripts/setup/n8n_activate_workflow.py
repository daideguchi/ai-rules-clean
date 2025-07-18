#!/usr/bin/env python3
"""
n8nワークフローアクティブ化スクリプト
"""

import os

import requests
from dotenv import load_dotenv

load_dotenv()


class N8nWorkflowActivator:
    def __init__(self):
        self.base_url = "https://dd1107.app.n8n.cloud"
        self.api_key = os.getenv("N8N_API_KEY")
        self.headers = {
            "X-N8N-API-KEY": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def find_claude_workflow(self):
        """claude-performanceワークフローを検索"""

        print("🔍 ワークフロー検索中...")

        response = requests.get(
            f"{self.base_url}/api/v1/workflows?limit=250", headers=self.headers
        )

        if response.status_code != 200:
            print(f"❌ ワークフロー取得失敗: {response.status_code}")
            return None

        workflows = response.json().get("data", [])

        for wf in workflows:
            nodes = wf.get("nodes", [])
            for node in nodes:
                if node.get("type") == "n8n-nodes-base.webhook":
                    path = node.get("parameters", {}).get("path", "")
                    if "claude-performance" in path.lower():
                        print(
                            f"✅ ワークフロー発見: {wf['name']} (ID: {wf['id'][:8]}...)"
                        )
                        print(
                            f"   現在の状態: {'Active' if wf.get('active') else 'Inactive'}"
                        )
                        return wf

        print("❌ claude-performanceワークフローが見つかりません")
        return None

    def activate_workflow(self, workflow_id):
        """ワークフローをアクティブ化"""

        print(f"🚀 ワークフローアクティブ化中... (ID: {workflow_id[:8]}...)")

        try:
            response = requests.post(
                f"{self.base_url}/api/v1/workflows/{workflow_id}/activate",
                headers=self.headers,
            )

            if response.status_code == 200:
                print("✅ ワークフローアクティブ化成功")
                return True
            else:
                print(f"❌ ワークフローアクティブ化失敗: {response.status_code}")
                print(f"Response: {response.text}")
                return False

        except Exception as e:
            print(f"❌ アクティブ化エラー: {e}")
            return False

    def verify_activation(self, workflow_id):
        """アクティブ化確認"""

        print("🔍 アクティブ化確認中...")

        try:
            response = requests.get(
                f"{self.base_url}/api/v1/workflows/{workflow_id}", headers=self.headers
            )

            if response.status_code == 200:
                workflow = response.json()
                is_active = workflow.get("active", False)

                if is_active:
                    print("✅ ワークフローがアクティブであることを確認")

                    # Webhook URLを表示
                    nodes = workflow.get("nodes", [])
                    for node in nodes:
                        if node.get("type") == "n8n-nodes-base.webhook":
                            path = node.get("parameters", {}).get("path", "")
                            webhook_url = f"https://dd1107.app.n8n.cloud/webhook/{path}"
                            print(f"📡 Webhook URL: {webhook_url}")
                            break

                    return True
                else:
                    print("❌ ワークフローがまだ非アクティブです")
                    return False
            else:
                print(f"❌ 確認失敗: {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ 確認エラー: {e}")
            return False


def main():
    """メイン処理"""

    print("🚀 n8nワークフローアクティブ化開始")
    print("=" * 60)

    activator = N8nWorkflowActivator()

    # 1. ワークフロー検索
    workflow = activator.find_claude_workflow()
    if not workflow:
        return False

    # 2. 既にアクティブかチェック
    if workflow.get("active", False):
        print("✅ ワークフローは既にアクティブです")

        # Webhook URLを表示
        nodes = workflow.get("nodes", [])
        for node in nodes:
            if node.get("type") == "n8n-nodes-base.webhook":
                path = node.get("parameters", {}).get("path", "")
                webhook_url = f"https://dd1107.app.n8n.cloud/webhook/{path}"
                print(f"📡 Webhook URL: {webhook_url}")
                break

        return True

    # 3. アクティブ化実行
    success = activator.activate_workflow(workflow["id"])
    if not success:
        return False

    # 4. アクティブ化確認
    verified = activator.verify_activation(workflow["id"])

    if verified:
        print("\n🎉 ワークフローアクティブ化完了！")
        print("🔧 次のステップ:")
        print("1. 統合テスト実行: python3 scripts/setup/n8n_supabase_debug.py")
        print("2. 成功確認: n8n→Supabase統合が 0/2 → 2/2 に変化")
        return True
    else:
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
