#!/usr/bin/env python3
"""
実績あるワークフローのアクティブ化と最終テスト
"""

import requests
import json
import os
import time
from dotenv import load_dotenv

load_dotenv()

def activate_proven_workflow():
    """実績あるワークフローをアクティブ化"""
    
    base_url = "https://dd1107.app.n8n.cloud"
    api_key = os.getenv("N8N_API_KEY")
    headers = {
        "X-N8N-API-KEY": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # 実績ワークフロー: My workflow (ID: cHzlzhsUcNoXMI8q)
    proven_workflow_id = "cHzlzhsUcNoXMI8q"
    webhook_url = "https://dd1107.app.n8n.cloud/webhook/claude-performance"
    
    print("🔄 実績ワークフローアクティブ化")
    print("="*50)
    print(f"ワークフロー: My workflow")
    print(f"ID: {proven_workflow_id}")
    print(f"Webhook: {webhook_url}")
    
    # アクティブ化
    activate_response = requests.post(f"{base_url}/api/v1/workflows/{proven_workflow_id}/activate", headers=headers)
    print(f"✅ アクティブ化: {activate_response.status_code}")
    
    # 30秒待機
    print("⏳ 30秒待機（サーバー同期）...")
    time.sleep(30)
    
    # 最終統合テスト
    print("\n🧪 実績ワークフロー最終テスト")
    print("="*40)
    
    test_data = {
        "session_id": f"proven_workflow_{int(time.time())}",
        "success": True,
        "execution_time": 8.0,
        "tools_used": "proven,workflow,final",
        "error_count": 0,
        "thinking_tag_used": True,
        "todo_tracking": True,
        "task_complexity": "complex",
        "learning_score": 10
    }
    
    print(f"📤 送信: {test_data['session_id']}")
    
    response = requests.post(webhook_url, json=test_data, timeout=20)
    print(f"   Webhook Status: {response.status_code}")
    print(f"   Response: {response.text}")
    
    if response.status_code == 200:
        print("   ✅ Webhook送信成功")
        
        # Supabase確認
        print("   ⏳ 10秒待機（データ処理）...")
        time.sleep(10)
        
        supabase_headers = {
            "apikey": os.getenv("SUPABASE_ANON_KEY"),
            "Authorization": f"Bearer {os.getenv('SUPABASE_ANON_KEY')}"
        }
        
        check_response = requests.get(
            f"{os.getenv('SUPABASE_URL')}/rest/v1/ai_performance_log?session_id=eq.{test_data['session_id']}",
            headers=supabase_headers
        )
        
        print(f"   Supabase確認 Status: {check_response.status_code}")
        
        if check_response.status_code == 200 and check_response.json():
            print(f"   🎉 **Supabaseデータ確認成功**")
            
            print(f"\n🎊 **完全統合成功** 🎊")
            print(f"📡 本番URL: {webhook_url}")
            print(f"🔄 自律AI成長システム稼働開始")
            print(f"🧠 AIパフォーマンスデータ自動蓄積開始")
            print(f"✅ Claude→n8n→Supabase完全自動化達成")
            
            return True, webhook_url
        else:
            print(f"   ⚠️ Supabaseデータ確認失敗")
            print(f"   Response: {check_response.text}")
            return False, webhook_url
    else:
        print(f"   ❌ Webhook送信失敗")
        return False, webhook_url

def final_completion():
    """最終完了処理"""
    
    print(f"\n📋 最終完了処理")
    print("="*30)
    
    # .envファイル更新
    with open('.env', 'r') as f:
        env_content = f.read()
    
    if 'claude-performance' not in env_content:
        with open('.env', 'a') as f:
            f.write('\n# Final Working Configuration\n')
            f.write('N8N_WEBHOOK_URL_WORKING=https://dd1107.app.n8n.cloud/webhook/claude-performance\n')
        
        print("✅ .env設定更新完了")
    
    print("✅ 統合システム稼働準備完了")

if __name__ == "__main__":
    success, webhook_url = activate_proven_workflow()
    
    if success:
        final_completion()
        print(f"\n🎯 **完全成功 - n8n→Supabase統合達成**")
        print(f"📡 使用URL: {webhook_url}")
    else:
        print(f"\n⚠️ **実績ワークフローでも統合未完了**")