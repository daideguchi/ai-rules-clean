#!/usr/bin/env python3
"""
ワークフロー診断 - 構造的問題特定
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def diagnose_workflow():
    """ワークフロー構造診断"""
    
    base_url = "https://dd1107.app.n8n.cloud"
    api_key = os.getenv("N8N_API_KEY")
    headers = {
        "X-N8N-API-KEY": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    workflow_id = "h5TN1MoxQ6XrYLXA"
    
    print("🔍 ワークフロー構造診断")
    print("="*40)
    
    # ワークフロー詳細取得
    response = requests.get(f"{base_url}/api/v1/workflows/{workflow_id}", headers=headers)
    
    if response.status_code == 200:
        workflow = response.json()
        
        print(f"📋 ワークフロー: {workflow.get('name')}")
        print(f"   Active: {workflow.get('active')}")
        
        nodes = workflow.get('nodes', [])
        connections = workflow.get('connections', {})
        
        print(f"\n🔹 ノード構成: {len(nodes)}個")
        
        for i, node in enumerate(nodes, 1):
            print(f"\n   {i}. 【{node.get('name')}】")
            print(f"      Type: {node.get('type')}")
            print(f"      ID: {node.get('id')}")
            
            # パラメータ要約
            params = node.get('parameters', {})
            if node.get('type') == 'n8n-nodes-base.webhook':
                print(f"      HTTP Method: {params.get('httpMethod', 'N/A')}")
                print(f"      Path: {params.get('path', 'N/A')}")
            
            elif node.get('type') == 'n8n-nodes-base.httpRequest':
                print(f"      Method: {params.get('requestMethod', 'N/A')}")
                print(f"      URL: {params.get('url', 'N/A')}")
                
                # Headers確認
                headers_params = params.get('headerParameters', {})
                if headers_params:
                    header_list = headers_params.get('parameters', [])
                    print(f"      Headers: {len(header_list)}個")
                
                # Body確認
                body_params = params.get('bodyParameters', {})
                if body_params:
                    body_list = body_params.get('parameters', [])
                    print(f"      Body Parameters: {len(body_list)}個")
                    
                    if body_list:
                        print(f"         例: {body_list[0].get('name', 'N/A')} = {body_list[0].get('value', 'N/A')}")
                else:
                    print(f"      ❌ Body Parameters: 未設定")
        
        print(f"\n🔗 接続構成:")
        if connections:
            for source, targets in connections.items():
                print(f"   {source} → {targets}")
        else:
            print(f"   ❌ 接続なし")
        
        # 問題診断
        print(f"\n🔍 問題診断:")
        
        issues = []
        
        # Webhookノード確認
        webhook_nodes = [n for n in nodes if n.get('type') == 'n8n-nodes-base.webhook']
        if not webhook_nodes:
            issues.append("❌ Webhookノードなし")
        
        # HTTP Requestノード確認
        http_nodes = [n for n in nodes if n.get('type') == 'n8n-nodes-base.httpRequest']
        if not http_nodes:
            issues.append("❌ HTTP Requestノードなし")
        else:
            for http_node in http_nodes:
                params = http_node.get('parameters', {})
                body_params = params.get('bodyParameters', {})
                if not body_params or not body_params.get('parameters'):
                    issues.append(f"❌ {http_node.get('name')}: Body Parameters未設定")
        
        # 接続確認
        if not connections:
            issues.append("❌ ノード間接続なし")
        
        if issues:
            for issue in issues:
                print(f"   {issue}")
        else:
            print(f"   ✅ 構造的問題なし")
        
        return len(issues) == 0
    else:
        print(f"❌ ワークフロー取得失敗: {response.status_code}")
        return False

if __name__ == "__main__":
    diagnose_workflow()