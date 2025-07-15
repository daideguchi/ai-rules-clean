#!/usr/bin/env python3
"""
実行詳細確認 - Supabaseノードエラー特定
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def check_executions():
    """実行詳細確認"""
    
    base_url = "https://dd1107.app.n8n.cloud"
    api_key = os.getenv("N8N_API_KEY")
    headers = {
        "X-N8N-API-KEY": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    workflow_id = "h5TN1MoxQ6XrYLXA"
    
    print("🔍 最新実行詳細確認")
    print("="*40)
    
    # 最新の実行履歴取得
    response = requests.get(
        f"{base_url}/api/v1/executions?limit=5&workflowId={workflow_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        executions = response.json().get("data", [])
        
        print(f"📊 実行数: {len(executions)}")
        
        if executions:
            latest = executions[0]
            exec_id = latest.get('id')
            
            print(f"\n📋 最新実行 (ID: {exec_id}):")
            print(f"   Status: {latest.get('status')}")
            print(f"   Mode: {latest.get('mode')}")
            print(f"   Started: {latest.get('startedAt')}")
            print(f"   Finished: {latest.get('stoppedAt')}")
            
            # 詳細な実行データ取得
            detail_response = requests.get(f"{base_url}/api/v1/executions/{exec_id}", headers=headers)
            
            if detail_response.status_code == 200:
                detail = detail_response.json()
                
                print(f"\n🔍 実行詳細:")
                print(f"   詳細Status: {detail.get('status')}")
                
                data_section = detail.get('data', {})
                result_data = data_section.get('resultData', {})
                run_data = result_data.get('runData', {})
                
                print(f"   実行ノード数: {len(run_data)}")
                
                # 各ノードの実行結果確認
                for node_name, node_executions in run_data.items():
                    print(f"\n   🔹 ノード: {node_name}")
                    
                    if node_executions:
                        node_exec = node_executions[0]
                        
                        # エラー確認
                        if 'error' in node_exec:
                            error = node_exec['error']
                            print(f"      ❌ エラー: {error.get('message', 'N/A')}")
                            print(f"      ❌ タイプ: {error.get('name', 'N/A')}")
                            if 'cause' in error:
                                print(f"      ❌ 原因: {error.get('cause', 'N/A')}")
                        else:
                            print(f"      ✅ 正常実行")
                            
                            # データ確認
                            exec_data = node_exec.get('data', {})
                            if exec_data:
                                main_data = exec_data.get('main', [])
                                if main_data and main_data[0]:
                                    print(f"      📊 出力データ: {len(main_data[0])}件")
                                else:
                                    print(f"      📊 出力データ: なし")
                    else:
                        print(f"      ⚠️ 実行データなし")
                
                return True
            else:
                print(f"❌ 詳細取得失敗: {detail_response.status_code}")
                return False
        else:
            print("⚠️ 実行履歴なし")
            return False
    else:
        print(f"❌ 実行履歴取得失敗: {response.status_code}")
        return False

if __name__ == "__main__":
    check_executions()