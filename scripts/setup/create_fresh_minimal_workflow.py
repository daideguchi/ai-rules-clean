#!/usr/bin/env python3
"""
最小限の新しいワークフロー作成
"""

import requests
import json
import os
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def create_minimal_workflow():
    """最小限のワークフロー作成"""
    
    base_url = "https://dd1107.app.n8n.cloud"
    api_key = os.getenv("N8N_API_KEY")
    headers = {
        "X-N8N-API-KEY": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    timestamp = int(datetime.now().timestamp())
    workflow_name = f"Fresh Minimal v{timestamp}"
    webhook_path = f"fresh-minimal-{timestamp}"
    
    print("🚀 最小限ワークフロー作成")
    print("="*40)
    print(f"名前: {workflow_name}")
    print(f"Path: {webhook_path}")
    
    # 最小限のWebhookノード
    webhook_node = {
        "parameters": {
            "httpMethod": "POST",
            "path": webhook_path,
            "responseMode": "onReceived"
        },
        "id": "webhook_minimal",
        "name": "Minimal Webhook",
        "type": "n8n-nodes-base.webhook",
        "typeVersion": 1,
        "position": [300, 300]
    }
    
    # 最小限のHTTP Requestノード（固定データ）
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    
    http_node = {
        "parameters": {
            "url": f"{supabase_url}/rest/v1/ai_performance_log",
            "requestMethod": "POST",
            "sendHeaders": True,
            "headerParameters": {
                "parameters": [
                    {"name": "apikey", "value": supabase_key},
                    {"name": "Authorization", "value": f"Bearer {supabase_key}"},
                    {"name": "Content-Type", "value": "application/json"},
                    {"name": "Prefer", "value": "return=minimal"}
                ]
            },
            "sendBody": True,
            "bodyContentType": "raw",
            "body": f'{{"session_id": "minimal_test_{timestamp}", "task_success": true, "execution_time_seconds": 1.0, "tools_used": "minimal", "error_count": 0, "thinking_tag_used": true, "todo_tracking": true, "task_complexity": "simple", "learning_score": 1, "session_notes": "Minimal test"}}'
        },
        "id": "http_minimal",
        "name": "Minimal HTTP",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.1,
        "position": [500, 300]
    }
    
    # ワークフロー定義
    workflow_data = {
        "name": workflow_name,
        "nodes": [webhook_node, http_node],
        "connections": {
            "Minimal Webhook": {
                "main": [[{"node": "Minimal HTTP", "type": "main", "index": 0}]]
            }
        },
        "settings": {}
    }
    
    # 作成
    response = requests.post(f"{base_url}/api/v1/workflows", headers=headers, json=workflow_data)
    
    if response.status_code in [200, 201]:
        result = response.json()
        workflow_id = result['id']
        
        print(f"✅ ワークフロー作成成功: {workflow_id}")
        
        # アクティブ化
        activate_response = requests.post(f"{base_url}/api/v1/workflows/{workflow_id}/activate", headers=headers)
        print(f"✅ アクティブ化: {activate_response.status_code}")
        
        webhook_url = f"{base_url}/webhook/{webhook_path}"
        
        # 60秒待機
        print("⏳ 60秒待機...")
        time.sleep(60)
        
        # テスト実行
        print("🧪 最小限テスト実行")
        
        test_response = requests.post(webhook_url, json={"test": "minimal"}, timeout=15)
        print(f"   Webhook Status: {test_response.status_code}")
        print(f"   Response: {test_response.text}")
        
        if test_response.status_code == 200:
            # Supabase確認
            time.sleep(8)
            
            check_response = requests.get(
                f"{supabase_url}/rest/v1/ai_performance_log?session_id=eq.minimal_test_{timestamp}",
                headers={
                    "apikey": supabase_key,
                    "Authorization": f"Bearer {supabase_key}"
                }
            )
            
            if check_response.status_code == 200 and check_response.json():
                print("🎉 **最小限統合成功**")
                return True, webhook_url
            else:
                print(f"❌ Supabaseデータなし: {check_response.text}")
                return False, webhook_url
        else:
            print("❌ Webhook失敗")
            return False, webhook_url
    else:
        print(f"❌ 作成失敗: {response.status_code} - {response.text}")
        return False, None

if __name__ == "__main__":
    success, url = create_minimal_workflow()
    
    if success:
        print(f"\n🎊 **最小限統合成功**")
        print(f"📡 URL: {url}")
        print("🔄 基本統合確立")
    else:
        print(f"\n❌ **最小限統合失敗**")