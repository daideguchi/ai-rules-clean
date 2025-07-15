#!/usr/bin/env python3
"""
全ワークフローリスト表示
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def list_all_workflows():
    base_url = "https://dd1107.app.n8n.cloud"
    api_key = os.getenv("N8N_API_KEY")
    headers = {
        "X-N8N-API-KEY": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    print("📋 全ワークフローリスト")
    print("=" * 50)
    
    response = requests.get(f"{base_url}/api/v1/workflows?limit=250", headers=headers)
    
    if response.status_code == 200:
        workflows = response.json().get("data", [])
        
        print(f"🔍 ワークフロー総数: {len(workflows)}")
        
        for i, wf in enumerate(workflows, 1):
            name = wf.get('name', 'N/A')
            wf_id = wf.get('id', 'N/A')
            active = wf.get('active', False)
            created = wf.get('createdAt', 'N/A')
            
            print(f"\n{i}. 【{name}】")
            print(f"   ID: {wf_id}")
            print(f"   Active: {active}")
            print(f"   Created: {created}")
            
            # Webhook確認
            detail_response = requests.get(f"{base_url}/api/v1/workflows/{wf_id}", headers=headers)
            if detail_response.status_code == 200:
                detail = detail_response.json()
                nodes = detail.get('nodes', [])
                
                for node in nodes:
                    if node.get('type') == 'n8n-nodes-base.webhook':
                        webhook_path = node.get('parameters', {}).get('path', 'N/A')
                        print(f"   🌐 Webhook: /{webhook_path}")
                        print(f"   📡 テストURL: {base_url}/webhook-test/{webhook_path}")
                        print(f"   🎯 本番URL: {base_url}/webhook/{webhook_path}")
        
        return workflows
    else:
        print(f"❌ ワークフロー取得失敗: {response.status_code}")
        print(f"Response: {response.text}")
        return []

if __name__ == "__main__":
    workflows = list_all_workflows()
    
    if workflows:
        print(f"\n🎯 **アクション必要**:")
        print(f"   上記のワークフローの中で、")
        print(f"   「Claude」が含まれる名前のワークフローの")
        print(f"   Active状態をtrueにしてください")
    else:
        print(f"\n❌ ワークフローが存在しません")