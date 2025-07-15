#!/usr/bin/env python3
"""
メインエージェントワークフローの接続更新
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def update_main_agent_connections():
    """メインエージェントワークフローを更新して画像作成ツールと接続"""
    
    base_url = "https://dd1107.app.n8n.cloud"
    api_key = os.getenv("N8N_API_KEY")
    headers = {
        "X-N8N-API-KEY": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    main_agent_id = "3I3jzE0SB7WwczxI"  # メインエージェントID
    image_tool_id = "CpFHfBuSqlk52X5X"   # 画像作成ツールID
    
    print("🔗 メインエージェント接続更新")
    print("="*40)
    print(f"メインエージェントID: {main_agent_id}")
    print(f"画像作成ツールID: {image_tool_id}")
    
    # 現在のワークフロー取得
    response = requests.get(f"{base_url}/api/v1/workflows/{main_agent_id}", headers=headers)
    
    if response.status_code == 200:
        workflow_data = response.json()
        
        print(f"📋 ワークフロー: {workflow_data.get('name')}")
        
        # ノード更新
        for node in workflow_data.get('nodes', []):
            if node.get('id') == 'create_image_subflow':
                # Execute WorkflowノードのワークフローIDを正しく設定
                node['parameters']['workflowId'] = image_tool_id
                print(f"✅ 画像作成ツール接続設定: {image_tool_id}")
        
        # 更新用データ
        update_data = {
            "name": workflow_data['name'],
            "nodes": workflow_data['nodes'],
            "connections": workflow_data.get('connections', {}),
            "settings": workflow_data.get('settings', {})
        }
        
        # ワークフロー更新
        update_response = requests.put(
            f"{base_url}/api/v1/workflows/{main_agent_id}",
            headers=headers,
            json=update_data
        )
        
        print(f"   更新ステータス: {update_response.status_code}")
        
        if update_response.status_code == 200:
            print(f"   ✅ メインエージェント接続更新成功")
            return True
        else:
            print(f"   ❌ 更新失敗: {update_response.text}")
            return False
    else:
        print(f"❌ ワークフロー取得失敗: {response.status_code}")
        return False

def create_supabase_marketing_table():
    """Supabaseにマーケティング画像ログテーブル作成"""
    
    print(f"\n📊 Supabaseマーケティングテーブル作成")
    print("="*40)
    
    # CREATE TABLE SQL
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS marketing_image_log (
        id SERIAL PRIMARY KEY,
        title VARCHAR(255),
        type VARCHAR(50) DEFAULT 'image',
        request TEXT,
        generated_prompt TEXT,
        file_name VARCHAR(255),
        creation_timestamp TIMESTAMP DEFAULT NOW(),
        telegram_chat_id VARCHAR(100),
        created_at TIMESTAMP DEFAULT NOW()
    );
    """
    
    headers = {
        "apikey": os.getenv("SUPABASE_ANON_KEY"),
        "Authorization": f"Bearer {os.getenv('SUPABASE_ANON_KEY')}",
        "Content-Type": "application/json"
    }
    
    # Supabase RPC経由でテーブル作成（実際にはSupabase UIで作成推奨）
    print("⚠️ テーブル作成SQLを生成しました:")
    print(create_table_sql)
    print("\nSupabase SQLエディタで上記SQLを実行してください")
    
    return True

if __name__ == "__main__":
    print("🛠️ マーケティングワークフロー統合設定")
    
    # 1. メインエージェント接続更新
    connection_success = update_main_agent_connections()
    
    # 2. Supabaseテーブル作成準備
    table_success = create_supabase_marketing_table()
    
    if connection_success and table_success:
        print(f"\n🎊 **統合設定成功** 🎊")
        print(f"✅ メインエージェント ⟷ 画像作成ツール接続完了")
        print(f"✅ データベース設計完了")
        print(f"\n📡 テスト用URL:")
        print(f"https://dd1107.app.n8n.cloud/webhook/marketing-agent-1752541701")
    else:
        print(f"\n⚠️ **統合設定要確認**")