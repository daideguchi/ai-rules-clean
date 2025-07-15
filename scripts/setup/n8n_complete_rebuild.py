#!/usr/bin/env python3
"""
n8nワークフロー完全再構築スクリプト
既存ワークフローを削除して、新しい動作するワークフローを作成
"""

import requests
import json
import os
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class N8nCompleteRebuild:
    def __init__(self):
        self.base_url = "https://dd1107.app.n8n.cloud"
        self.api_key = os.getenv("N8N_API_KEY")
        self.headers = {
            "X-N8N-API-KEY": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Supabase設定
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_anon_key = os.getenv("SUPABASE_ANON_KEY")
    
    def delete_existing_workflows(self):
        """既存のClaude関連ワークフローを削除"""
        
        print("🗑️ 既存ワークフロー削除開始")
        
        try:
            # 全ワークフロー取得
            response = requests.get(f"{self.base_url}/api/v1/workflows?limit=250", headers=self.headers)
            workflows = response.json().get("data", [])
            
            deleted_count = 0
            for workflow in workflows:
                name = workflow.get('name', '')
                if any(keyword in name.lower() for keyword in ['claude', 'performance', 'simple']):
                    workflow_id = workflow['id']
                    print(f"   削除中: {name} (ID: {workflow_id[:8]}...)")
                    
                    delete_response = requests.delete(
                        f"{self.base_url}/api/v1/workflows/{workflow_id}",
                        headers=self.headers
                    )
                    
                    if delete_response.status_code == 200:
                        print(f"   ✅ 削除成功: {name}")
                        deleted_count += 1
                    else:
                        print(f"   ❌ 削除失敗: {name} - Status: {delete_response.status_code}")
            
            print(f"📋 削除完了: {deleted_count}件のワークフローを削除")
            return True
            
        except Exception as e:
            print(f"❌ 削除処理エラー: {e}")
            return False
    
    def create_simple_working_workflow(self):
        """シンプルで動作するワークフローを作成"""
        
        print("🚀 新しいワークフロー作成開始")
        
        # Webhookノード
        webhook_node = {
            "parameters": {
                "httpMethod": "POST",
                "path": "claude-performance-rebuild",
                "responseMode": "onReceived",
                "options": {}
            },
            "id": "webhook-node",
            "name": "Claude Performance Webhook",
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 1,
            "position": [240, 300]
        }
        
        # HTTP Requestノード（Supabase）
        supabase_node = {
            "parameters": {
                "url": f"{self.supabase_url}/rest/v1/ai_performance_log",
                "requestMethod": "POST",
                "sendHeaders": True,
                "headerParameters": {
                    "parameters": [
                        {
                            "name": "apikey",
                            "value": self.supabase_anon_key
                        },
                        {
                            "name": "Authorization",
                            "value": f"Bearer {self.supabase_anon_key}"
                        },
                        {
                            "name": "Content-Type",
                            "value": "application/json"
                        },
                        {
                            "name": "Prefer",
                            "value": "return=minimal"
                        }
                    ]
                },
                "sendBody": True,
                "bodyContentType": "json",
                "jsonParameters": True,
                "bodyParameters": {
                    "parameters": [
                        {
                            "name": "session_id",
                            "value": "={{$json.session_id}}"
                        },
                        {
                            "name": "task_success",
                            "value": "={{$json.success}}"
                        },
                        {
                            "name": "execution_time_seconds",
                            "value": "={{$json.execution_time}}"
                        },
                        {
                            "name": "tools_used",
                            "value": "={{$json.tools_used}}"
                        },
                        {
                            "name": "error_count",
                            "value": "={{$json.error_count}}"
                        },
                        {
                            "name": "thinking_tag_used",
                            "value": "={{$json.thinking_tag_used}}"
                        },
                        {
                            "name": "todo_tracking",
                            "value": "={{$json.todo_tracking}}"
                        },
                        {
                            "name": "task_complexity",
                            "value": "={{$json.task_complexity}}"
                        },
                        {
                            "name": "learning_score",
                            "value": "={{$json.learning_score}}"
                        },
                        {
                            "name": "session_notes",
                            "value": "Rebuilt workflow - testing integration"
                        }
                    ]
                },
                "options": {}
            },
            "id": "supabase-node",
            "name": "Insert to Supabase",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.1,
            "position": [440, 300]
        }
        
        # ワークフロー定義（読み取り専用プロパティ除外）
        workflow_definition = {
            "name": "Claude Performance Rebuilt v3",
            "nodes": [webhook_node, supabase_node],
            "connections": {
                "Claude Performance Webhook": {
                    "main": [
                        [
                            {
                                "node": "Insert to Supabase",
                                "type": "main",
                                "index": 0
                            }
                        ]
                    ]
                }
            },
            "settings": {}
        }
        
        try:
            # ワークフロー作成
            response = requests.post(
                f"{self.base_url}/api/v1/workflows",
                headers=self.headers,
                json=workflow_definition
            )
            
            if response.status_code in [200, 201]:
                workflow_data = response.json()
                workflow_id = workflow_data.get('id')
                
                print(f"✅ ワークフロー作成成功")
                print(f"   ID: {workflow_id}")
                print(f"   名前: {workflow_data.get('name')}")
                print(f"   Active: {workflow_data.get('active')}")
                
                # ワークフローをアクティブ化
                if not workflow_data.get('active'):
                    print(f"   ⚡ ワークフローアクティブ化中...")
                    activate_response = requests.post(
                        f"{self.base_url}/api/v1/workflows/{workflow_id}/activate",
                        headers=self.headers
                    )
                    
                    if activate_response.status_code == 200:
                        print(f"   ✅ アクティブ化成功")
                    else:
                        print(f"   ⚠️ アクティブ化失敗: {activate_response.status_code}")
                        print(f"   代替手段でPUTメソッド試行...")
                        
                        # 代替手段: PUTメソッド
                        activate_response2 = requests.put(
                            f"{self.base_url}/api/v1/workflows/{workflow_id}",
                            headers=self.headers,
                            json={"active": True}
                        )
                        
                        if activate_response2.status_code == 200:
                            print(f"   ✅ 代替アクティブ化成功")
                        else:
                            print(f"   ⚠️ 代替アクティブ化も失敗: {activate_response2.status_code}")
                
                webhook_url = "https://dd1107.app.n8n.cloud/webhook/claude-performance-rebuild"
                print(f"   Webhook URL: {webhook_url}")
                
                return workflow_id, webhook_url
            else:
                print(f"❌ ワークフロー作成失敗: {response.status_code}")
                print(f"   Response: {response.text}")
                return None, None
                
        except Exception as e:
            print(f"❌ ワークフロー作成エラー: {e}")
            return None, None
    
    def test_new_workflow(self, webhook_url):
        """新しいワークフローをテスト"""
        
        print(f"\n🧪 新しいワークフローテスト開始")
        
        test_data = {
            "session_id": f"rebuild_test_{int(datetime.now().timestamp())}",
            "success": True,
            "execution_time": 1.5,
            "tools_used": ["test", "rebuild"],
            "error_count": 0,
            "thinking_tag_used": True,
            "todo_tracking": True,
            "task_complexity": "simple",
            "learning_score": 3
        }
        
        print(f"📤 テストデータ送信: {test_data['session_id']}")
        
        try:
            # Webhook送信
            response = requests.post(webhook_url, json=test_data, timeout=15)
            print(f"   Webhook Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ Webhook送信成功")
                
                # 3秒待ってからSupabaseで確認
                print(f"   ⏳ 3秒待機（データ反映待ち）...")
                time.sleep(3)
                
                # Supabaseで確認
                supabase_headers = {
                    "apikey": self.supabase_anon_key,
                    "Authorization": f"Bearer {self.supabase_anon_key}",
                    "Content-Type": "application/json"
                }
                
                check_url = f"{self.supabase_url}/rest/v1/ai_performance_log?session_id=eq.{test_data['session_id']}"
                check_response = requests.get(check_url, headers=supabase_headers)
                
                print(f"   Supabase確認 Status: {check_response.status_code}")
                
                if check_response.status_code == 200:
                    data = check_response.json()
                    if data:
                        print(f"   ✅ Supabaseデータ確認成功: {len(data)}件")
                        print(f"      Session ID: {data[0].get('session_id')}")
                        print(f"      Task Success: {data[0].get('task_success')}")
                        return True
                    else:
                        print(f"   ❌ Supabaseにデータが反映されていません")
                        return False
                else:
                    print(f"   ❌ Supabase確認失敗: {check_response.status_code}")
                    return False
            else:
                print(f"   ❌ Webhook送信失敗: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ テストエラー: {e}")
            return False
    
    def verify_integration(self, workflow_id):
        """統合完全性確認"""
        
        print(f"\n🔍 統合完全性確認")
        
        try:
            # 最新の実行履歴確認
            response = requests.get(
                f"{self.base_url}/api/v1/executions?limit=3&workflowId={workflow_id}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                executions = response.json().get("data", [])
                
                if executions:
                    latest = executions[0]
                    status = latest.get('status')
                    
                    print(f"   最新実行ステータス: {status}")
                    
                    if status == 'success':
                        print(f"   ✅ ワークフロー実行成功")
                        return True
                    else:
                        print(f"   ❌ ワークフロー実行失敗: {status}")
                        return False
                else:
                    print(f"   ❌ 実行履歴なし")
                    return False
            else:
                print(f"   ❌ 実行履歴取得失敗: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 確認エラー: {e}")
            return False

def main():
    """メイン処理"""
    
    print("🔥 n8nワークフロー完全再構築開始")
    print("=" * 60)
    
    rebuilder = N8nCompleteRebuild()
    
    # 1. 既存ワークフロー削除
    if not rebuilder.delete_existing_workflows():
        print("❌ 既存ワークフロー削除失敗")
        return False
    
    print("\n" + "="*60)
    
    # 2. 新しいワークフロー作成
    workflow_id, webhook_url = rebuilder.create_simple_working_workflow()
    if not workflow_id:
        print("❌ 新しいワークフロー作成失敗")
        return False
    
    print("\n" + "="*60)
    
    # 3. テスト実行
    test_success = rebuilder.test_new_workflow(webhook_url)
    
    # 4. 統合確認
    integration_success = rebuilder.verify_integration(workflow_id)
    
    print(f"\n🎯 完全再構築結果:")
    print(f"  - ワークフロー作成: ✅ 成功")
    print(f"  - 機能テスト: {'✅ 成功' if test_success else '❌ 失敗'}")
    print(f"  - 統合確認: {'✅ 成功' if integration_success else '❌ 失敗'}")
    
    final_success = test_success and integration_success
    
    if final_success:
        print(f"\n🎉 **完全再構築成功**")
        print(f"   n8n→Supabase統合が正常に動作しています")
        print(f"   Webhook URL: {webhook_url}")
    else:
        print(f"\n🚨 **再構築失敗**")
        print(f"   追加の修正が必要です")
    
    return final_success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)