#!/usr/bin/env python3
"""
n8nワークフロー詳細エラー分析スクリプト
実行の詳細エラー情報を取得
"""

import os
import time
from datetime import datetime

import requests
from dotenv import load_dotenv

load_dotenv()


class N8nDetailedErrorAnalyzer:
    def __init__(self):
        self.base_url = "https://dd1107.app.n8n.cloud"
        self.api_key = os.getenv("N8N_API_KEY")
        self.headers = {
            "X-N8N-API-KEY": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def find_simple_workflow(self):
        """シンプルワークフロー検索"""

        response = requests.get(
            f"{self.base_url}/api/v1/workflows?limit=250", headers=self.headers
        )

        workflows = response.json().get("data", [])

        for wf in workflows:
            if "Claude Performance Simple v2" in wf.get("name", ""):
                return wf

        return None

    def send_test_and_get_execution(self):
        """テスト送信して実行IDを取得"""

        print("🚀 テストWebhook送信...")

        # テスト前の実行数を記録
        workflow = self.find_simple_workflow()
        if not workflow:
            return None, None

        pre_executions = self.get_executions(workflow["id"], limit=1)
        len(pre_executions)

        # Webhook送信
        webhook_url = "https://dd1107.app.n8n.cloud/webhook/claude-performance-simple"
        test_data = {
            "session_id": f"error_analysis_{int(datetime.now().timestamp())}",
            "success": True,
            "execution_time": 2.0,
            "tools_used": ["error", "analysis"],
            "error_count": 0,
            "thinking_tag_used": True,
            "todo_tracking": True,
            "task_complexity": "medium",
            "learning_score": 3,
            "user_feedback": "Error analysis test",
        }

        try:
            response = requests.post(webhook_url, json=test_data, timeout=10)

            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")

            if response.status_code == 200:
                print("   ✅ Webhook送信成功")

                # 少し待ってから新しい実行を検索
                time.sleep(3)

                post_executions = self.get_executions(workflow["id"], limit=5)

                # 新しい実行を特定
                for execution in post_executions:
                    if execution not in pre_executions:
                        print(f"   ✅ 新しい実行発見: {execution['id'][:8]}...")
                        return execution, test_data["session_id"]

                print("   ⚠️ 新しい実行が見つかりません")
                return None, test_data["session_id"]
            else:
                print("   ❌ Webhook送信失敗")
                return None, None

        except Exception as e:
            print(f"   ❌ Webhookエラー: {e}")
            return None, None

    def get_executions(self, workflow_id, limit=5):
        """実行履歴取得"""

        try:
            response = requests.get(
                f"{self.base_url}/api/v1/executions?limit={limit}&workflowId={workflow_id}",
                headers=self.headers,
            )

            if response.status_code == 200:
                return response.json().get("data", [])
            else:
                return []

        except Exception as e:
            print(f"実行履歴取得エラー: {e}")
            return []

    def analyze_execution_error(self, execution_id):
        """実行エラー詳細分析"""

        print(f"\n🔍 実行エラー詳細分析: {execution_id[:8]}...")

        try:
            response = requests.get(
                f"{self.base_url}/api/v1/executions/{execution_id}",
                headers=self.headers,
            )

            if response.status_code != 200:
                print(f"❌ 実行詳細取得失敗: {response.status_code}")
                return None

            execution = response.json()

            print("📊 実行基本情報:")
            print(f"   Status: {execution.get('status', 'N/A')}")
            print(f"   Started: {execution.get('startedAt', 'N/A')}")
            print(f"   Finished: {execution.get('stoppedAt', 'N/A')}")
            print(f"   Mode: {execution.get('mode', 'N/A')}")

            # データの詳細分析
            data = execution.get("data", {})
            result_data = data.get("resultData", {})
            run_data = result_data.get("runData", {})

            print("\n🔍 ノード別実行結果:")

            for node_name, node_runs in run_data.items():
                print(f"\n   📋 ノード: {node_name}")

                if not node_runs:
                    print("      ❌ 実行データなし")
                    continue

                latest_run = node_runs[0]

                # 実行時間
                execution_time = latest_run.get("executionTime")
                if execution_time:
                    print(f"      ⏱️  実行時間: {execution_time}ms")

                # エラー詳細
                error = latest_run.get("error")
                if error:
                    print("      ❌ エラー:")
                    print(f"         メッセージ: {error.get('message', 'N/A')}")
                    print(f"         タイプ: {error.get('name', 'N/A')}")
                    print(f"         スタック: {error.get('stack', 'N/A')[:200]}...")

                    # HTTPエラーの場合の詳細
                    if "httpCode" in error:
                        print(f"         HTTPコード: {error.get('httpCode')}")
                    if "cause" in error:
                        print(f"         原因: {error.get('cause')}")
                else:
                    print("      ✅ 正常実行")

                # 入力データ
                input_data = latest_run.get("data", {}).get("main", [[]])
                if input_data and input_data[0]:
                    print(f"      📥 入力データ: {len(input_data[0])}件")
                    if input_data[0]:
                        first_input = input_data[0][0]
                        if "json" in first_input:
                            json_data = first_input["json"]
                            print(f"         データ例: {str(json_data)[:100]}...")

                # 出力データ
                output_data = latest_run.get("data", {}).get("main", [[]])
                if output_data and output_data[0]:
                    print(f"      📤 出力データ: {len(output_data[0])}件")

            return execution

        except Exception as e:
            print(f"❌ 実行分析エラー: {e}")
            return None

    def check_workflow_configuration(self):
        """ワークフロー設定確認"""

        print("\n🔧 ワークフロー設定確認...")

        workflow = self.find_simple_workflow()
        if not workflow:
            return False

        # 詳細取得
        response = requests.get(
            f"{self.base_url}/api/v1/workflows/{workflow['id']}", headers=self.headers
        )

        if response.status_code != 200:
            print("❌ ワークフロー詳細取得失敗")
            return False

        details = response.json()
        nodes = details.get("nodes", [])

        print("📋 ノード設定確認:")

        for node in nodes:
            node_type = node.get("type", "unknown")
            node_name = node.get("name", "unnamed")

            print(f"\n   🔹 {node_name} ({node_type})")

            if node_type == "n8n-nodes-base.httpRequest":
                params = node.get("parameters", {})

                print(f"      URL: {params.get('url', 'N/A')}")
                print(f"      Method: {params.get('method', 'N/A')}")

                # ヘッダー確認
                header_params = params.get("headerParameters", {})
                headers = header_params.get("parameters", [])

                print(f"      ヘッダー ({len(headers)}個):")
                for header in headers:
                    name = header.get("name", "N/A")
                    value = header.get("value", "N/A")
                    print(f"         {name}: {value[:50]}...")

                # ボディ確認
                body = params.get("body", params.get("jsonParameters", "N/A"))
                if body:
                    print(f"      ボディ: {str(body)[:100]}...")

        return True


def main():
    """メイン処理"""

    print("🔍 n8nワークフロー詳細エラー分析開始")
    print("=" * 60)

    analyzer = N8nDetailedErrorAnalyzer()

    # 1. ワークフロー設定確認
    config_ok = analyzer.check_workflow_configuration()
    if not config_ok:
        return False

    # 2. テスト送信と実行取得
    execution, session_id = analyzer.send_test_and_get_execution()

    if execution:
        # 3. エラー詳細分析
        analyzer.analyze_execution_error(execution["id"])

        print("\n🎯 分析結果:")
        print("  - ワークフロー設定: ✅")
        print("  - Webhook実行: ✅")
        print(f"  - 実行ステータス: {execution.get('status', 'N/A')}")
        print(f"  - セッションID: {session_id}")

        actual_status = execution.get("status", "unknown")
        if actual_status == "error":
            print("\n🚨 重大エラー: n8nワークフロー内でエラーが発生しています")
            print(
                "   統合は機能していません - 上記の詳細エラー情報を確認して修正が必要です"
            )
            return False
        elif actual_status == "success":
            print("\n✅ ワークフローは正常に実行されました")
            return True
        else:
            print(f"\n⚠️ 不明な実行ステータス: {actual_status}")
            return False
    else:
        print("\n❌ テスト実行の取得に失敗しました")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
