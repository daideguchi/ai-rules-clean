#!/usr/bin/env python3
"""
n8nワークフロー自動更新スクリプト
APIを使ってワークフローにSupabaseノードを自動追加
"""

import os
import sys
from datetime import datetime

import requests
from dotenv import load_dotenv

load_dotenv()


class N8nWorkflowUpdater:
    def __init__(self):
        self.base_url = "https://dd1107.app.n8n.cloud"
        self.api_key = os.getenv("N8N_API_KEY")

        if not self.api_key:
            print("❌ N8N_API_KEY環境変数が設定されていません")
            print("\n📋 APIキー取得手順:")
            print("1. https://dd1107.app.n8n.cloud にログイン")
            print("2. Settings > n8n API > Create an API key")
            print("3. .envファイルに N8N_API_KEY=your_key_here を追加")
            print(
                "\n📝 詳細手順: /Users/dd/Desktop/1_dev/coding-rule2/config/n8n/N8N_API_SETUP_GUIDE.md"
            )
            sys.exit(1)

        self.headers = {
            "X-N8N-API-KEY": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_anon_key = os.getenv("SUPABASE_ANON_KEY")

    def list_workflows(self):
        """ワークフロー一覧取得"""

        print("🔍 ワークフロー一覧取得中...")

        try:
            response = requests.get(
                f"{self.base_url}/api/v1/workflows?limit=250", headers=self.headers
            )

            if response.status_code == 401:
                print("❌ API認証失敗 - APIキーを確認してください")
                print("💡 無料プランの場合は有料プランにアップグレードが必要です")
                print(f"🔍 APIキー（先頭20文字）: {self.api_key[:20]}...")
                return None
            elif response.status_code != 200:
                print(f"❌ API呼び出し失敗: {response.status_code}")
                print(f"Response: {response.text}")
                print(f"🔍 Request URL: {response.url}")
                return None

            data = response.json()
            workflows = data.get("data", data.get("workflows", []))

            print(f"✅ {len(workflows)}個のワークフローを取得")
            print(f"🔍 Response keys: {list(data.keys())}")

            if len(workflows) == 0:
                print("⚠️ ワークフローが0個の理由:")
                print(f"  - 全レスポンス: {data}")
                print(
                    "  - 可能な原因: 無料プラン制限、アクセス権限不足、ワークフロー未作成"
                )

            for wf in workflows:
                print(f"  - {wf['name']} (ID: {wf['id'][:8]}...)")

            return workflows

        except Exception as e:
            print(f"❌ ワークフロー取得エラー: {e}")
            return None

    def find_workflow_by_name(self, workflows, name):
        """名前またはWebhookパスでワークフローを検索"""

        # まず名前で検索
        for wf in workflows:
            if name.lower() in wf["name"].lower():
                return wf

        # 次にWebhookのパスで検索
        for wf in workflows:
            nodes = wf.get("nodes", [])
            for node in nodes:
                if node.get("type") == "n8n-nodes-base.webhook":
                    path = node.get("parameters", {}).get("path", "")
                    if name.lower() in path.lower():
                        print(f"✅ Webhookパスで発見: {wf['name']} (path: {path})")
                        return wf

        return None

    def get_workflow_details(self, workflow_id):
        """ワークフロー詳細取得"""

        print(f"📋 ワークフロー詳細取得中... (ID: {workflow_id[:8]}...)")

        try:
            response = requests.get(
                f"{self.base_url}/api/v1/workflows/{workflow_id}", headers=self.headers
            )

            if response.status_code != 200:
                print(f"❌ ワークフロー詳細取得失敗: {response.status_code}")
                return None

            workflow = response.json()

            print(f"✅ ワークフロー詳細取得完了: {workflow['name']}")
            print(f"  - ノード数: {len(workflow.get('nodes', []))}")

            return workflow

        except Exception as e:
            print(f"❌ ワークフロー詳細取得エラー: {e}")
            return None

    def create_supabase_http_node(self, workflow):
        """Supabase HTTP Requestノード作成"""

        # 次のノードIDを生成
        [node.get("id", "") for node in workflow.get("nodes", [])]
        node_id = f"supabase-http-{int(datetime.now().timestamp())}"

        # 適切な位置を計算
        max_x = max(
            [node.get("position", [0, 0])[0] for node in workflow.get("nodes", [])],
            default=0,
        )
        position = [max_x + 200, 300]

        http_node = {
            "id": node_id,
            "name": "Supabase Insert",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4,
            "position": position,
            "parameters": {
                "method": "POST",
                "url": f"{self.supabase_url}/rest/v1/ai_performance_log",
                "responseFormat": "json",
                "sendHeaders": True,
                "headerParameters": {
                    "parameters": [
                        {"name": "apikey", "value": "={{$env.SUPABASE_ANON_KEY}}"},
                        {
                            "name": "Authorization",
                            "value": "=Bearer {{$env.SUPABASE_ANON_KEY}}",
                        },
                        {"name": "Content-Type", "value": "application/json"},
                    ]
                },
                "sendBody": True,
                "bodyParameters": {"parameters": []},
                "jsonParameters": '={"session_id": "{{$json.session_id}}", "task_success": {{$json.success || $json.task_success}}, "execution_time": {{$json.execution_time}}, "tool_calls_count": {{$json.tools_used ? $json.tools_used.length : ($json.tool_calls_count || 0)}}, "tool_calls": {{$json.tools_used || $json.tool_calls || []}}, "error_count": {{$json.error_count || 0}}, "thinking_tag_used": {{$json.thinking_tag_used || false}}, "todo_tracking": {{$json.todo_tracking || false}}, "task_complexity": "{{$json.task_complexity || \'medium\'}}", "learning_score": {{$json.learning_score || 0}}, "success_patterns": {{$json.success_patterns || []}}, "failure_patterns": {{$json.failure_patterns || []}}}',
                "options": {},
            },
        }

        return http_node

    def find_webhook_node(self, workflow):
        """Webhookノードを検索"""

        for node in workflow.get("nodes", []):
            if node.get("type") == "n8n-nodes-base.webhook":
                return node
        return None

    def update_workflow_connections(self, workflow, webhook_node, http_node):
        """ワークフロー接続を更新"""

        webhook_name = webhook_node["name"]
        http_name = http_node["name"]

        # 既存の接続を保持しつつ、新しい接続を追加
        connections = workflow.get("connections", {})

        if webhook_name not in connections:
            connections[webhook_name] = {"main": [[]]}

        if "main" not in connections[webhook_name]:
            connections[webhook_name]["main"] = [[]]

        if not connections[webhook_name]["main"]:
            connections[webhook_name]["main"] = [[]]

        # HTTP Requestノードへの接続を追加
        new_connection = {"node": http_name, "type": "main", "index": 0}

        connections[webhook_name]["main"][0].append(new_connection)

        return connections

    def update_workflow(self, workflow_id, updated_workflow):
        """ワークフローを更新"""

        print(f"🔧 ワークフロー更新中... (ID: {workflow_id[:8]}...)")

        # 更新用のペイロード（必要なフィールドのみ）
        payload = {
            "name": updated_workflow["name"],
            "nodes": updated_workflow["nodes"],
            "connections": updated_workflow["connections"],
            "settings": updated_workflow.get("settings", {}),
        }

        try:
            response = requests.put(
                f"{self.base_url}/api/v1/workflows/{workflow_id}",
                headers=self.headers,
                json=payload,
            )

            if response.status_code == 200:
                print("✅ ワークフロー更新成功")
                return True
            else:
                print(f"❌ ワークフロー更新失敗: {response.status_code}")
                print(f"Response: {response.text}")
                return False

        except Exception as e:
            print(f"❌ ワークフロー更新エラー: {e}")
            return False

    def update_claude_performance_workflow(self):
        """claude-performanceワークフローを更新"""

        print("🚀 claude-performanceワークフロー自動更新開始")
        print("=" * 60)

        # 1. ワークフロー一覧取得
        workflows = self.list_workflows()
        if not workflows:
            return False

        # 2. claude-performanceワークフローを検索
        target_workflow = self.find_workflow_by_name(workflows, "claude-performance")
        if not target_workflow:
            print("❌ 'claude-performance'ワークフローが見つかりません")
            print("💡 利用可能なワークフロー:")
            for wf in workflows:
                print(f"  - {wf['name']}")
            return False

        print(f"✅ ターゲットワークフロー発見: {target_workflow['name']}")

        # 3. ワークフロー詳細取得
        workflow = self.get_workflow_details(target_workflow["id"])
        if not workflow:
            return False

        # 4. Webhookノードを検索
        webhook_node = self.find_webhook_node(workflow)
        if not webhook_node:
            print("❌ Webhookノードが見つかりません")
            return False

        print(f"✅ Webhookノード発見: {webhook_node['name']}")

        # 5. 既にSupabaseノードが存在するかチェック
        supabase_nodes = [
            node
            for node in workflow.get("nodes", [])
            if "supabase" in node.get("name", "").lower()
        ]

        if supabase_nodes:
            print("⚠️ Supabaseノードが既に存在します:")
            for node in supabase_nodes:
                print(f"  - {node['name']}")
            print("💡 手動で確認してください")
            return True

        # 6. Supabase HTTP Requestノード作成
        http_node = self.create_supabase_http_node(workflow)
        print(f"✅ Supabaseノード作成: {http_node['name']}")

        # 7. ノードを追加
        workflow["nodes"].append(http_node)

        # 8. 接続を更新
        workflow["connections"] = self.update_workflow_connections(
            workflow, webhook_node, http_node
        )

        # 9. ワークフローを更新
        success = self.update_workflow(target_workflow["id"], workflow)

        if success:
            print("\n🎉 ワークフロー更新完了！")
            print("🔧 次のステップ:")
            print("1. n8nダッシュボードで確認")
            print("2. 環境変数SUPABASE_ANON_KEYを設定")
            print("3. テスト実行: python3 scripts/setup/n8n_supabase_debug.py")
            return True
        else:
            return False


def main():
    """メイン処理"""

    updater = N8nWorkflowUpdater()
    success = updater.update_claude_performance_workflow()

    if success:
        print("\n✅ n8nワークフロー自動更新成功")
    else:
        print("\n❌ n8nワークフロー自動更新失敗")
        print(
            "💡 手動設定手順: /Users/dd/Desktop/1_dev/coding-rule2/config/n8n/WORKFLOW_FIX_INSTRUCTIONS.md"
        )

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
