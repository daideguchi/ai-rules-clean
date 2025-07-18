#!/usr/bin/env python3
"""
n8nワークフロー分析スクリプト
現在のワークフロー構成を詳細に分析
"""

import os

import requests
from dotenv import load_dotenv

load_dotenv()


class N8nWorkflowAnalyzer:
    def __init__(self):
        self.base_url = "https://dd1107.app.n8n.cloud"
        self.api_key = os.getenv("N8N_API_KEY")
        self.headers = {
            "X-N8N-API-KEY": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def get_workflows(self):
        """ワークフロー一覧取得"""
        response = requests.get(
            f"{self.base_url}/api/v1/workflows?limit=250", headers=self.headers
        )
        return response.json().get("data", [])

    def find_claude_workflow(self, workflows):
        """claude-performanceワークフローを検索"""
        print("🔍 Claude関連ワークフロー検索:")

        found_workflows = []
        for wf in workflows:
            nodes = wf.get("nodes", [])
            for node in nodes:
                if node.get("type") == "n8n-nodes-base.webhook":
                    path = node.get("parameters", {}).get("path", "")
                    if "claude-performance" in path.lower():
                        print(
                            f"  ✅ 発見: {wf['name']} (path: {path}, active: {wf.get('active')})"
                        )
                        found_workflows.append(wf)
                        break

        if not found_workflows:
            print("  ❌ Claude関連ワークフローが見つかりません")
            return None

        # アクティブなものを優先
        for wf in found_workflows:
            if wf.get("active", False):
                print(f"  🎯 アクティブワークフロー選択: {wf['name']}")
                return wf

        # アクティブなものがなければ最初のものを返す
        print(f"  ⚠️ 非アクティブワークフロー選択: {found_workflows[0]['name']}")
        return found_workflows[0]

    def analyze_workflow_structure(self, workflow):
        """ワークフロー構造分析"""

        print(f"📋 ワークフロー分析: {workflow['name']}")
        print(f"ID: {workflow['id']}")
        print(f"Active: {workflow.get('active', False)}")
        print(f"ノード数: {len(workflow.get('nodes', []))}")
        print()

        nodes = workflow.get("nodes", [])
        connections = workflow.get("connections", {})

        print("🔗 ノード一覧:")
        for i, node in enumerate(nodes):
            node_type = node.get("type", "unknown")
            node_name = node.get("name", "unnamed")
            print(f"  {i + 1}. {node_name} ({node_type})")

            # Webhook詳細
            if node_type == "n8n-nodes-base.webhook":
                params = node.get("parameters", {})
                print(f"     Path: {params.get('path', 'N/A')}")
                print(f"     Method: {params.get('httpMethod', 'GET')}")

            # HTTP Request詳細
            elif node_type == "n8n-nodes-base.httpRequest":
                params = node.get("parameters", {})
                print(f"     URL: {params.get('url', 'N/A')}")
                print(f"     Method: {params.get('method', 'GET')}")

            # PostgreSQL詳細
            elif node_type == "n8n-nodes-base.postgres":
                params = node.get("parameters", {})
                print(f"     Table: {params.get('table', 'N/A')}")
                print(f"     Operation: {params.get('operation', 'N/A')}")

        print("\n🔗 接続情報:")
        for source_node, targets in connections.items():
            main_targets = targets.get("main", [[]])
            if main_targets and main_targets[0]:
                target_names = [t["node"] for t in main_targets[0]]
                print(f"  {source_node} → {', '.join(target_names)}")

        return nodes, connections

    def check_supabase_integration(self, nodes):
        """Supabase統合確認"""

        print("\n🔍 Supabase統合チェック:")

        supabase_nodes = []
        postgres_nodes = []
        http_nodes = []

        for node in nodes:
            node_type = node.get("type", "")
            node_name = node.get("name", "")

            if "supabase" in node_name.lower():
                supabase_nodes.append(node)
            elif node_type == "n8n-nodes-base.postgres":
                postgres_nodes.append(node)
            elif node_type == "n8n-nodes-base.httpRequest":
                http_nodes.append(node)

        if supabase_nodes:
            print(f"  ✅ Supabaseノード発見: {len(supabase_nodes)}個")
            for node in supabase_nodes:
                print(f"    - {node['name']}")
        else:
            print("  ❌ Supabaseノードなし")

        if postgres_nodes:
            print(f"  📊 PostgreSQLノード: {len(postgres_nodes)}個")
            for node in postgres_nodes:
                params = node.get("parameters", {})
                print(f"    - {node['name']} (Table: {params.get('table', 'N/A')})")

        if http_nodes:
            print(f"  🌐 HTTPノード: {len(http_nodes)}個")
            for node in http_nodes:
                params = node.get("parameters", {})
                url = params.get("url", "N/A")
                if "supabase" in url:
                    print(f"    - {node['name']} → {url}")
                else:
                    print(f"    - {node['name']} → {url[:50]}...")

        return len(supabase_nodes) > 0 or any(
            "supabase" in node.get("parameters", {}).get("url", "")
            for node in http_nodes
        )

    def generate_fix_recommendation(self, workflow, has_supabase_integration):
        """修正推奨を生成"""

        print("\n💡 修正推奨:")

        if not has_supabase_integration:
            print("  🔧 問題: Supabase統合が見つかりません")
            print("  📋 解決策:")
            print("    1. 既存のPostgreSQLノードを削除または無効化")
            print("    2. Supabase REST API用のHTTP Requestノードを追加")
            print("    3. 環境変数SUPABASE_ANON_KEYを設定")

        if not workflow.get("active", False):
            print("  ⚠️ ワークフローが非アクティブです")
            print("  📋 解決策: n8nダッシュボードでワークフローをアクティブ化")

        # PostgreSQLノードがある場合の警告
        nodes = workflow.get("nodes", [])
        postgres_nodes = [
            n for n in nodes if n.get("type") == "n8n-nodes-base.postgres"
        ]
        if postgres_nodes:
            print("  ⚠️ PostgreSQLノードが検出されました")
            print(
                "  📋 問題: Supabase REST APIとPostgreSQLノードは競合する可能性があります"
            )


def main():
    """メイン処理"""

    print("🔍 n8nワークフロー詳細分析開始")
    print("=" * 60)

    analyzer = N8nWorkflowAnalyzer()

    # ワークフロー取得
    workflows = analyzer.get_workflows()
    print(f"📊 合計ワークフロー数: {len(workflows)}")

    # claude-performanceワークフロー検索
    claude_workflow = analyzer.find_claude_workflow(workflows)

    if not claude_workflow:
        print("❌ claude-performanceワークフローが見つかりません")
        print("💡 利用可能なワークフロー:")
        for wf in workflows:
            print(f"  - {wf['name']} (ID: {wf['id'][:8]}...)")
        return False

    # 詳細分析
    nodes, connections = analyzer.analyze_workflow_structure(claude_workflow)

    # Supabase統合確認
    has_supabase = analyzer.check_supabase_integration(nodes)

    # 修正推奨
    analyzer.generate_fix_recommendation(claude_workflow, has_supabase)

    print("\n🎯 分析結果:")
    print(f"  - ワークフロー: {claude_workflow['name']}")
    print(f"  - アクティブ: {'✅' if claude_workflow.get('active') else '❌'}")
    print(f"  - Supabase統合: {'✅' if has_supabase else '❌'}")
    print(f"  - ノード数: {len(nodes)}")

    return has_supabase


if __name__ == "__main__":
    main()
