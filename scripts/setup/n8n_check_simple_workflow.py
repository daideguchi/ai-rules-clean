#!/usr/bin/env python3
"""
n8nシンプルワークフロー状態確認スクリプト
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

class N8nSimpleWorkflowChecker:
    def __init__(self):
        self.base_url = "https://dd1107.app.n8n.cloud"
        self.api_key = os.getenv("N8N_API_KEY")
        self.headers = {
            "X-N8N-API-KEY": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def find_simple_workflow(self):
        """シンプルワークフローを検索"""
        
        print("🔍 シンプルワークフロー検索中...")
        
        response = requests.get(
            f"{self.base_url}/api/v1/workflows?limit=250",
            headers=self.headers
        )
        
        workflows = response.json().get("data", [])
        
        for wf in workflows:
            if "Claude Performance Simple" in wf.get('name', ''):
                print(f"✅ シンプルワークフロー発見: {wf['name']}")
                print(f"   ID: {wf['id']}")
                print(f"   Active: {wf.get('active', False)}")
                print(f"   Created: {wf.get('createdAt', 'N/A')}")
                print(f"   Updated: {wf.get('updatedAt', 'N/A')}")
                return wf
        
        print("❌ シンプルワークフローが見つかりません")
        return None

    def get_workflow_details(self, workflow_id):
        """ワークフロー詳細取得"""
        
        print(f"\n📋 ワークフロー詳細取得中... (ID: {workflow_id})")
        
        response = requests.get(
            f"{self.base_url}/api/v1/workflows/{workflow_id}",
            headers=self.headers
        )
        
        if response.status_code != 200:
            print(f"❌ 詳細取得失敗: {response.status_code}")
            return None
        
        workflow = response.json()
        
        print(f"✅ 詳細取得成功")
        print(f"   Name: {workflow['name']}")
        print(f"   Active: {workflow.get('active', False)}")
        print(f"   Nodes: {len(workflow.get('nodes', []))}")
        
        # Webhookノード詳細
        nodes = workflow.get('nodes', [])
        for node in nodes:
            if node.get('type') == 'n8n-nodes-base.webhook':
                params = node.get('parameters', {})
                print(f"\n🔗 Webhookノード詳細:")
                print(f"   Name: {node.get('name', 'N/A')}")
                print(f"   Path: {params.get('path', 'N/A')}")
                print(f"   Method: {params.get('httpMethod', 'GET')}")
                print(f"   Webhook ID: {node.get('webhookId', 'N/A')}")
                
                expected_url = f"https://dd1107.app.n8n.cloud/webhook/{params.get('path', '')}"
                print(f"   Expected URL: {expected_url}")
        
        return workflow

    def test_webhook_manually(self, path):
        """Webhook手動テスト"""
        
        print(f"\n🧪 Webhook手動テスト: {path}")
        
        webhook_url = f"https://dd1107.app.n8n.cloud/webhook/{path}"
        test_data = {
            "session_id": "manual_test_123",
            "success": True,
            "execution_time": 2.0,
            "tools_used": ["manual", "test"],
            "error_count": 0,
            "thinking_tag_used": True,
            "todo_tracking": True,
            "task_complexity": "simple",
            "learning_score": 3
        }
        
        try:
            response = requests.post(webhook_url, json=test_data, timeout=10)
            
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            
            if response.status_code == 200:
                print("   ✅ Webhook成功")
                return True
            else:
                print("   ❌ Webhook失敗")
                return False
                
        except Exception as e:
            print(f"   ❌ Webhookエラー: {e}")
            return False

    def reactivate_workflow(self, workflow_id):
        """ワークフロー再アクティブ化"""
        
        print(f"\n🔄 ワークフロー再アクティブ化中... (ID: {workflow_id})")
        
        # まず非アクティブ化
        try:
            response = requests.delete(
                f"{self.base_url}/api/v1/workflows/{workflow_id}/activate",
                headers=self.headers
            )
            print(f"   非アクティブ化: {response.status_code}")
        except:
            print("   非アクティブ化スキップ")
        
        # 再アクティブ化
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/workflows/{workflow_id}/activate",
                headers=self.headers
            )
            
            if response.status_code == 200:
                print("   ✅ 再アクティブ化成功")
                return True
            else:
                print(f"   ❌ 再アクティブ化失敗: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ 再アクティブ化エラー: {e}")
            return False

def main():
    """メイン処理"""
    
    print("🔍 n8nシンプルワークフロー詳細チェック開始")
    print("=" * 60)
    
    checker = N8nSimpleWorkflowChecker()
    
    # 1. シンプルワークフロー検索
    workflow = checker.find_simple_workflow()
    if not workflow:
        return False
    
    # 2. 詳細取得
    details = checker.get_workflow_details(workflow['id'])
    if not details:
        return False
    
    # 3. Webhook手動テスト
    nodes = details.get('nodes', [])
    webhook_path = None
    for node in nodes:
        if node.get('type') == 'n8n-nodes-base.webhook':
            webhook_path = node.get('parameters', {}).get('path', '')
            break
    
    if webhook_path:
        webhook_success = checker.test_webhook_manually(webhook_path)
        
        if not webhook_success:
            print("\n🔄 Webhook失敗 - 再アクティブ化を試行...")
            reactivate_success = checker.reactivate_workflow(workflow['id'])
            
            if reactivate_success:
                print("\n🧪 再アクティブ化後テスト...")
                webhook_success = checker.test_webhook_manually(webhook_path)
    
    print(f"\n🎯 最終結果:")
    print(f"  - ワークフロー存在: ✅")
    print(f"  - アクティブ状態: {'✅' if details.get('active') else '❌'}")
    print(f"  - Webhook動作: {'✅' if webhook_success else '❌'}")
    
    return webhook_success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)