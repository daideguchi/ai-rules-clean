#!/usr/bin/env python3
"""
ワークフロー設定詳細確認
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def check_workflow_config():
    base_url = "https://dd1107.app.n8n.cloud"
    api_key = os.getenv("N8N_API_KEY")
    headers = {
        "X-N8N-API-KEY": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    workflow_id = "A64aaEvlA0TSbc0o"
    
    print("🔍 ワークフロー設定詳細確認")
    print("=" * 50)
    
    response = requests.get(f"{base_url}/api/v1/workflows/{workflow_id}", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        
        print(f"名前: {data.get('name')}")
        print(f"Active: {data.get('active')}")
        print(f"ノード数: {len(data.get('nodes', []))}")
        
        # 各ノードの詳細確認
        nodes = data.get('nodes', [])
        
        print(f"\n📋 ノード詳細:")
        for i, node in enumerate(nodes, 1):
            print(f"\n{i}. 【{node.get('name')}】")
            print(f"   Type: {node.get('type')}")
            print(f"   ID: {node.get('id')}")
            
            # パラメータ確認
            params = node.get('parameters', {})
            if params:
                print(f"   Parameters:")
                for key, value in params.items():
                    if isinstance(value, dict) or isinstance(value, list):
                        print(f"      {key}: {json.dumps(value, indent=8, ensure_ascii=False)}")
                    else:
                        print(f"      {key}: {value}")
        
        # 接続確認
        connections = data.get('connections', {})
        print(f"\n🔗 接続確認:")
        if connections:
            for source_node, targets in connections.items():
                print(f"   {source_node} -> {targets}")
        else:
            print(f"   ❌ 接続が設定されていません！")
        
        return True
    else:
        print(f"❌ 取得失敗: {response.status_code}")
        return False

if __name__ == "__main__":
    check_workflow_config()