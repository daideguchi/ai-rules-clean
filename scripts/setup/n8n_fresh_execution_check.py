#!/usr/bin/env python3
"""
新しく作成されたワークフローの実行エラー詳細確認
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def find_fresh_workflow():
    """新しいワークフローを検索"""
    
    base_url = "https://dd1107.app.n8n.cloud"
    api_key = os.getenv("N8N_API_KEY")
    headers = {
        "X-N8N-API-KEY": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    response = requests.get(f"{base_url}/api/v1/workflows?limit=250", headers=headers)
    workflows = response.json().get("data", [])
    
    for wf in workflows:
        if "Claude Fresh AI Growth" in wf.get('name', ''):
            return wf, headers, base_url
    
    return None, None, None

def check_detailed_executions(workflow_id, headers, base_url):
    """実行詳細とエラー確認"""
    
    print(f"🔍 実行詳細エラー確認 (ワークフローID: {workflow_id[:8]}...)")
    
    try:
        response = requests.get(
            f"{base_url}/api/v1/executions?limit=5&workflowId={workflow_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            executions = data.get("data", [])
            
            print(f"📊 実行数: {len(executions)}")
            
            for i, execution in enumerate(executions):
                print(f"\n📋 実行 {i+1}:")
                print(f"   ID: {execution.get('id', 'N/A')}")
                print(f"   Status: {execution.get('status', 'N/A')}")
                print(f"   Started: {execution.get('startedAt', 'N/A')}")
                print(f"   Finished: {execution.get('stoppedAt', 'N/A')}")
                print(f"   Mode: {execution.get('mode', 'N/A')}")
                
                # 最新の実行の詳細確認
                if i == 0:
                    print(f"\n   🔍 最新実行の詳細確認...")
                    detail_response = requests.get(
                        f"{base_url}/api/v1/executions/{execution['id']}",
                        headers=headers
                    )
                    
                    if detail_response.status_code == 200:
                        detail = detail_response.json()
                        
                        print(f"   詳細Status: {detail.get('status', 'N/A')}")
                        
                        # データ部分確認
                        data_section = detail.get('data', {})
                        result_data = data_section.get('resultData', {})
                        run_data = result_data.get('runData', {})
                        
                        print(f"   ノード実行数: {len(run_data)}")
                        
                        # 各ノードの詳細確認
                        for node_name, node_executions in run_data.items():
                            print(f"\n      🔹 ノード: {node_name}")
                            
                            if node_executions:
                                latest_node_exec = node_executions[0]
                                
                                # エラー確認
                                error = latest_node_exec.get('error')
                                if error:
                                    print(f"         ❌ エラー詳細:")
                                    print(f"            メッセージ: {error.get('message', 'N/A')}")
                                    print(f"            タイプ: {error.get('name', 'N/A')}")
                                    if 'cause' in error:
                                        print(f"            原因: {error.get('cause', 'N/A')}")
                                    if 'stack' in error:
                                        print(f"            スタック: {error.get('stack', 'N/A')[:200]}...")
                                else:
                                    print(f"         ✅ 正常実行")
                                    
                                # 実行データ確認
                                data = latest_node_exec.get('data', {})
                                if data:
                                    main_data = data.get('main', [])
                                    if main_data and main_data[0]:
                                        print(f"         📊 データ出力: {len(main_data[0])}件")
                                        if main_data[0]:
                                            first_item = main_data[0][0]
                                            if 'json' in first_item:
                                                json_keys = list(first_item['json'].keys())
                                                print(f"         📝 JSONキー: {json_keys[:5]}...")
                            else:
                                print(f"         ⚠️ 実行データなし")
                    else:
                        print(f"   詳細取得失敗: {detail_response.status_code}")
            
            return True
        else:
            print(f"❌ 実行履歴取得失敗: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False

def main():
    print("🔍 新規ワークフロー実行エラー詳細確認")
    print("=" * 60)
    
    # 1. ワークフロー検索
    workflow, headers, base_url = find_fresh_workflow()
    if not workflow:
        print("❌ 新規ワークフローが見つかりません")
        return False
    
    print(f"✅ ワークフロー発見: {workflow['name']}")
    print(f"   ID: {workflow['id']}")
    print(f"   Active: {workflow.get('active', False)}")
    
    # 2. 実行詳細確認
    success = check_detailed_executions(workflow['id'], headers, base_url)
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)