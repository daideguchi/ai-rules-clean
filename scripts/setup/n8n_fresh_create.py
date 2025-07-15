#!/usr/bin/env python3
"""
完全に新しいワークフローを一から作成
"""

import requests
import json
import os
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def delete_all_claude_workflows():
    """全てのClaude関連ワークフローを削除"""
    
    base_url = "https://dd1107.app.n8n.cloud"
    api_key = os.getenv("N8N_API_KEY")
    headers = {
        "X-N8N-API-KEY": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    print("🗑️ 全Claude関連ワークフロー削除")
    
    response = requests.get(f"{base_url}/api/v1/workflows?limit=250", headers=headers)
    workflows = response.json().get("data", [])
    
    deleted_count = 0
    for workflow in workflows:
        name = workflow.get('name', '')
        if any(keyword in name.lower() for keyword in ['claude', 'performance', 'rebuilt']):
            workflow_id = workflow['id']
            print(f"   削除中: {name}")
            
            delete_response = requests.delete(f"{base_url}/api/v1/workflows/{workflow_id}", headers=headers)
            if delete_response.status_code == 200:
                print(f"   ✅ 削除成功")
                deleted_count += 1
            else:
                print(f"   ❌ 削除失敗: {delete_response.status_code}")
    
    print(f"📋 削除完了: {deleted_count}件")
    return deleted_count > 0

def create_fresh_workflow():
    """完全に新しいワークフローを作成"""
    
    base_url = "https://dd1107.app.n8n.cloud"
    api_key = os.getenv("N8N_API_KEY")
    headers = {
        "X-N8N-API-KEY": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    print("🆕 完全新規ワークフロー作成")
    
    # タイムスタンプ付きの一意な名前
    timestamp = int(datetime.now().timestamp())
    unique_name = f"Claude Fresh AI Growth v{timestamp}"
    unique_path = f"claude-fresh-{timestamp}"
    
    print(f"   名前: {unique_name}")
    print(f"   Webhook Path: {unique_path}")
    
    # Supabase設定
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_anon_key = os.getenv("SUPABASE_ANON_KEY")
    
    # 最小限のワークフロー定義
    workflow_definition = {
        "name": unique_name,
        "nodes": [
            {
                "parameters": {
                    "httpMethod": "POST",
                    "path": unique_path,
                    "responseMode": "onReceived"
                },
                "id": "webhook1",
                "name": "AI Growth Webhook",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 1,
                "position": [240, 300]
            },
            {
                "parameters": {
                    "url": f"{supabase_url}/rest/v1/ai_performance_log",
                    "requestMethod": "POST",
                    "sendHeaders": True,
                    "headerParameters": {
                        "parameters": [
                            {"name": "apikey", "value": supabase_anon_key},
                            {"name": "Authorization", "value": f"Bearer {supabase_anon_key}"},
                            {"name": "Content-Type", "value": "application/json"},
                            {"name": "Prefer", "value": "return=minimal"}
                        ]
                    },
                    "sendBody": True,
                    "bodyContentType": "json",
                    "jsonParameters": True,
                    "bodyParameters": {
                        "parameters": [
                            {"name": "session_id", "value": "={{$json.session_id}}"},
                            {"name": "task_success", "value": "={{$json.success}}"},
                            {"name": "execution_time_seconds", "value": "={{$json.execution_time}}"},
                            {"name": "tools_used", "value": "={{$json.tools_used}}"},
                            {"name": "error_count", "value": "={{$json.error_count}}"},
                            {"name": "thinking_tag_used", "value": "={{$json.thinking_tag_used}}"},
                            {"name": "todo_tracking", "value": "={{$json.todo_tracking}}"},
                            {"name": "task_complexity", "value": "={{$json.task_complexity}}"},
                            {"name": "learning_score", "value": "={{$json.learning_score}}"},
                            {"name": "session_notes", "value": "Fresh workflow - autonomous AI growth"}
                        ]
                    }
                },
                "id": "supabase1",
                "name": "Store AI Performance",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.1,
                "position": [440, 300]
            }
        ],
        "connections": {
            "AI Growth Webhook": {
                "main": [[{"node": "Store AI Performance", "type": "main", "index": 0}]]
            }
        },
        "settings": {}
    }
    
    try:
        # ワークフロー作成
        response = requests.post(f"{base_url}/api/v1/workflows", headers=headers, json=workflow_definition)
        
        if response.status_code in [200, 201]:
            workflow_data = response.json()
            workflow_id = workflow_data.get('id')
            
            print(f"✅ ワークフロー作成成功: {workflow_id}")
            
            # アクティブ化（複数の方法を試行）
            print(f"   ⚡ アクティブ化開始...")
            
            # 方法1: /activate エンドポイント
            activate_response = requests.post(f"{base_url}/api/v1/workflows/{workflow_id}/activate", headers=headers)
            if activate_response.status_code == 200:
                print(f"   ✅ アクティブ化成功（方法1）")
            else:
                print(f"   ⚠️ 方法1失敗: {activate_response.status_code}")
                
                # 方法2: PUT with active=True
                activate_response2 = requests.put(f"{base_url}/api/v1/workflows/{workflow_id}", headers=headers, json={"active": True})
                if activate_response2.status_code == 200:
                    print(f"   ✅ アクティブ化成功（方法2）")
                else:
                    print(f"   ⚠️ 方法2も失敗: {activate_response2.status_code}")
            
            webhook_url = f"{base_url}/webhook/{unique_path}"
            
            # 少し待ってから確認
            print(f"   ⏳ 5秒待機（サーバー同期待ち）...")
            time.sleep(5)
            
            return workflow_id, webhook_url, unique_name
        else:
            print(f"❌ ワークフロー作成失敗: {response.status_code}")
            print(f"   Response: {response.text}")
            return None, None, None
            
    except Exception as e:
        print(f"❌ エラー: {e}")
        return None, None, None

def test_fresh_workflow(webhook_url, workflow_name):
    """新しいワークフローをテスト"""
    
    print(f"🧪 新規ワークフローテスト: {workflow_name}")
    
    test_data = {
        "session_id": f"fresh_test_{int(datetime.now().timestamp())}",
        "success": True,
        "execution_time": 2.0,
        "tools_used": ["fresh", "rebuild", "autonomous"],
        "error_count": 0,
        "thinking_tag_used": True,
        "todo_tracking": True,
        "task_complexity": "medium",
        "learning_score": 5
    }
    
    print(f"📤 テストデータ送信...")
    print(f"   URL: {webhook_url}")
    print(f"   Session ID: {test_data['session_id']}")
    
    try:
        response = requests.post(webhook_url, json=test_data, timeout=15)
        print(f"   Webhook Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ Webhook送信成功")
            
            # Supabase確認
            print(f"   ⏳ 3秒待機（データ反映待ち）...")
            time.sleep(3)
            
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_anon_key = os.getenv("SUPABASE_ANON_KEY")
            
            supabase_headers = {
                "apikey": supabase_anon_key,
                "Authorization": f"Bearer {supabase_anon_key}",
                "Content-Type": "application/json"
            }
            
            check_url = f"{supabase_url}/rest/v1/ai_performance_log?session_id=eq.{test_data['session_id']}"
            check_response = requests.get(check_url, headers=supabase_headers)
            
            print(f"   Supabase確認 Status: {check_response.status_code}")
            
            if check_response.status_code == 200:
                data = check_response.json()
                if data:
                    print(f"   ✅ Supabaseデータ確認成功: {len(data)}件")
                    return True
                else:
                    print(f"   ❌ Supabaseデータなし")
                    return False
            else:
                print(f"   ❌ Supabase確認失敗: {check_response.status_code}")
                return False
        else:
            print(f"   ❌ Webhook送信失敗: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        return False

def main():
    print("🆕 n8n完全新規ワークフロー作成")
    print("=" * 60)
    
    # 1. 既存削除
    delete_all_claude_workflows()
    
    print(f"\n{'='*60}")
    
    # 2. 新規作成
    workflow_id, webhook_url, workflow_name = create_fresh_workflow()
    
    if not workflow_id:
        print("❌ 新規ワークフロー作成失敗")
        return False
    
    print(f"\n{'='*60}")
    
    # 3. テスト
    test_success = test_fresh_workflow(webhook_url, workflow_name)
    
    print(f"\n🎯 最終結果:")
    print(f"  - ワークフロー作成: ✅ 成功")
    print(f"  - 統合テスト: {'✅ 成功' if test_success else '❌ 失敗'}")
    
    if test_success:
        print(f"\n🎉 **完全新規作成成功**")
        print(f"   ワークフロー名: {workflow_name}")
        print(f"   Webhook URL: {webhook_url}")
        print(f"   n8n→Supabase統合が正常動作")
    else:
        print(f"\n🚨 **統合テスト失敗**")
        print(f"   Webhook URLまたはSupabase連携に問題")
    
    return test_success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)