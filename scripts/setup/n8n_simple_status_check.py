#!/usr/bin/env python3
"""
n8n単純ステータス確認スクリプト
実行状況の生データを確認
"""

import requests
import json
import os
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def find_workflow():
    """ワークフロー検索"""
    
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
        if "Claude Performance Simple v2" in wf.get('name', ''):
            return wf, headers, base_url
    
    return None, None, None

def send_test_webhook():
    """テストWebhook送信"""
    
    webhook_url = "https://dd1107.app.n8n.cloud/webhook/claude-performance-simple"
    test_data = {
        "session_id": f"simple_test_{int(datetime.now().timestamp())}",
        "success": True,
        "execution_time": 1.0,
        "tools_used": ["simple", "test"],
        "error_count": 0,
        "thinking_tag_used": True,
        "todo_tracking": True,
        "task_complexity": "simple",
        "learning_score": 2
    }
    
    print(f"🚀 テストWebhook送信: {test_data['session_id']}")
    
    try:
        response = requests.post(webhook_url, json=test_data, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        return test_data["session_id"] if response.status_code == 200 else None
    except Exception as e:
        print(f"   ❌ エラー: {e}")
        return None

def check_executions_raw(workflow_id, headers, base_url):
    """実行履歴生データ確認"""
    
    print(f"\n📋 実行履歴生データ確認 (ワークフローID: {workflow_id[:8]}...)")
    
    try:
        response = requests.get(
            f"{base_url}/api/v1/executions?limit=3&workflowId={workflow_id}",
            headers=headers
        )
        
        print(f"   API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            executions = data.get("data", [])
            
            print(f"   実行数: {len(executions)}")
            
            for i, execution in enumerate(executions):
                print(f"\n   📊 実行 {i+1}:")
                print(f"      ID: {execution.get('id', 'N/A')}")
                print(f"      Status: {execution.get('status', 'N/A')}")
                print(f"      Started: {execution.get('startedAt', 'N/A')}")
                print(f"      Finished: {execution.get('stoppedAt', 'N/A')}")
                print(f"      Mode: {execution.get('mode', 'N/A')}")
                
                # 最新の実行の詳細確認
                if i == 0:
                    print(f"\n      🔍 最新実行の詳細確認...")
                    detail_response = requests.get(
                        f"{base_url}/api/v1/executions/{execution['id']}",
                        headers=headers
                    )
                    
                    if detail_response.status_code == 200:
                        detail = detail_response.json()
                        print(f"      詳細Status: {detail.get('status', 'N/A')}")
                        
                        # エラー情報確認
                        data_section = detail.get('data', {})
                        result_data = data_section.get('resultData', {})
                        run_data = result_data.get('runData', {})
                        
                        print(f"      ノード実行数: {len(run_data)}")
                        
                        for node_name, node_executions in run_data.items():
                            print(f"         🔹 {node_name}:")
                            if node_executions:
                                latest_node_exec = node_executions[0]
                                error = latest_node_exec.get('error')
                                if error:
                                    print(f"            ❌ エラー: {error.get('message', 'N/A')}")
                                    if 'cause' in error:
                                        print(f"            原因: {error.get('cause', 'N/A')}")
                                else:
                                    print(f"            ✅ 正常")
                            else:
                                print(f"            ⚠️ 実行データなし")
                    else:
                        print(f"      詳細取得失敗: {detail_response.status_code}")
            
            return executions
        else:
            print(f"   ❌ 実行履歴取得失敗: {response.status_code}")
            print(f"   Response: {response.text}")
            return []
            
    except Exception as e:
        print(f"   ❌ エラー: {e}")
        return []

def check_supabase_data(session_id):
    """Supabaseデータ確認"""
    
    print(f"\n🔍 Supabaseデータ確認: {session_id}")
    
    supabase_url = os.getenv("SUPABASE_URL")
    anon_key = os.getenv("SUPABASE_ANON_KEY")
    
    headers = {
        "apikey": anon_key,
        "Authorization": f"Bearer {anon_key}",
        "Content-Type": "application/json"
    }
    
    try:
        url = f"{supabase_url}/rest/v1/ai_performance_log?session_id=eq.{session_id}"
        response = requests.get(url, headers=headers)
        
        print(f"   Supabase Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data:
                print(f"   ✅ データ発見: {len(data)}件")
                for item in data:
                    print(f"      ID: {item.get('id')}, Success: {item.get('task_success')}")
                return True
            else:
                print(f"   ❌ データなし")
                return False
        else:
            print(f"   ❌ Supabase確認失敗: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ エラー: {e}")
        return False

def main():
    """メイン処理"""
    
    print("🔍 n8n単純ステータス確認開始")
    print("=" * 60)
    
    # 1. ワークフロー検索
    workflow, headers, base_url = find_workflow()
    if not workflow:
        print("❌ ワークフローが見つかりません")
        return False
    
    print(f"✅ ワークフロー発見: {workflow['name']}")
    
    # 2. テストWebhook送信
    session_id = send_test_webhook()
    if not session_id:
        print("❌ Webhook送信失敗")
        return False
    
    # 3. 少し待つ
    print("\n⏳ 3秒待機...")
    time.sleep(3)
    
    # 4. 実行履歴確認
    executions = check_executions_raw(workflow['id'], headers, base_url)
    
    # 5. Supabaseデータ確認
    supabase_success = check_supabase_data(session_id)
    
    print(f"\n🎯 最終診断:")
    
    if executions:
        latest = executions[0]
        status = latest.get('status', 'unknown')
        print(f"  - 最新実行ステータス: {status}")
        
        if status == 'error':
            print(f"  🚨 **重大問題**: n8nワークフロー内部でエラーが発生")
            print(f"  📋 **統合状況**: 完全に機能していません")
            print(f"  💡 **対応必要**: ワークフロー設定の修正が必要")
        elif status == 'success':
            if supabase_success:
                print(f"  ✅ **完全成功**: n8n→Supabase統合が正常動作")
            else:
                print(f"  ⚠️ **部分成功**: n8nは動作するがSupabase反映に問題")
        else:
            print(f"  ❓ **不明状態**: 実行ステータスが特定できません")
    else:
        print(f"  ❌ **実行確認失敗**: 実行履歴を取得できませんでした")
    
    print(f"  - Supabaseデータ: {'✅ 成功' if supabase_success else '❌ 失敗'}")
    
    return executions and executions[0].get('status') == 'success' and supabase_success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)