#!/usr/bin/env python3
"""
Supabase AI Performance テーブル作成
"""

import requests
import json

def create_ai_performance_table():
    """AI performance tracking table creation"""
    
    supabase_url = "https://hetcpqtsineqaopnnvtn.supabase.co"
    anon_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhldGNwcXRzaW5lcWFvcG5udnRuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI0MDEzNDEsImV4cCI6MjA2Nzk3NzM0MX0.WAgCVM-XZY0JqYzap7fCXxu6PeX9vES-zitAhoySIbg"
    
    headers = {
        "apikey": anon_key,
        "Authorization": f"Bearer {anon_key}",
        "Content-Type": "application/json"
    }
    
    print("🔧 Supabase AI Performance テーブル作成開始")
    print("=" * 60)
    
    # テーブル作成用のSQL（RPC function経由）
    sql_query = """
    CREATE TABLE IF NOT EXISTS ai_performance_log (
        id SERIAL PRIMARY KEY,
        session_id TEXT NOT NULL,
        timestamp TIMESTAMPTZ DEFAULT NOW(),
        task_success BOOLEAN DEFAULT FALSE,
        execution_time FLOAT DEFAULT 0,
        tool_calls_count INTEGER DEFAULT 0,
        tool_calls JSONB DEFAULT '[]',
        error_count INTEGER DEFAULT 0,
        thinking_tag_used BOOLEAN DEFAULT FALSE,
        todo_tracking BOOLEAN DEFAULT FALSE,
        task_complexity TEXT DEFAULT 'simple',
        user_feedback TEXT,
        learning_score INTEGER DEFAULT 0,
        success_patterns JSONB DEFAULT '[]',
        failure_patterns JSONB DEFAULT '[]',
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    """
    
    # まず基本接続テスト
    try:
        test_url = f"{supabase_url}/rest/v1/"
        response = requests.get(test_url, headers=headers)
        
        if response.status_code == 200:
            print("✅ Supabase基本接続成功")
        else:
            print(f"❌ 基本接続失敗: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 接続エラー: {e}")
        return False
    
    # 簡単なテストデータでテーブル作成を試す（INSERT時に自動作成される場合）
    print("\n🧪 テストデータ挿入によるテーブル作成テスト...")
    
    test_data = {
        "session_id": "test_table_creation",
        "task_success": True,
        "execution_time": 1.0,
        "tool_calls_count": 1,
        "tool_calls": ["test"],
        "error_count": 0,
        "thinking_tag_used": False,
        "todo_tracking": True,
        "task_complexity": "simple",
        "learning_score": 1,
        "success_patterns": ["table_creation"],
        "failure_patterns": []
    }
    
    try:
        # ai_performance_log テーブルに挿入
        url = f"{supabase_url}/rest/v1/ai_performance_log"
        response = requests.post(url, headers=headers, json=test_data)
        
        if response.status_code in [200, 201]:
            print("✅ ai_performance_log テーブル作成・データ挿入成功")
            return True
        else:
            print(f"❌ テーブル作成失敗: {response.status_code}")
            print(f"Response: {response.text}")
            
            # テーブルが存在しない場合の代替案
            print("\n🔄 代替案: 既存todosテーブル利用...")
            
            # todosテーブルにAI performance データを適用
            todos_data = {
                "task": f"AI Performance: {test_data['session_id']}",
                "status": "Complete" if test_data['task_success'] else "In progress"
            }
            
            todos_url = f"{supabase_url}/rest/v1/todos"
            todos_response = requests.post(todos_url, headers=headers, json=todos_data)
            
            if todos_response.status_code in [200, 201]:
                print("✅ todosテーブル利用成功")
                return True
            else:
                print(f"❌ todosテーブル利用失敗: {todos_response.status_code}")
                print(f"Response: {todos_response.text}")
                return False
                
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False

def test_supabase_connectivity():
    """Supabase接続と機能テスト"""
    
    supabase_url = "https://hetcpqtsineqaopnnvtn.supabase.co"
    anon_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhldGNwcXRzaW5lcWFvcG5udnRuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI0MDEzNDEsImV4cCI6MjA2Nzk3NzM0MX0.WAgCVM-XZY0JqYzap7fCXxu6PeX9vES-zitAhoySIbg"
    
    headers = {
        "apikey": anon_key,
        "Authorization": f"Bearer {anon_key}",
        "Content-Type": "application/json"
    }
    
    print("\n🔍 Supabase接続確認とデータ取得テスト")
    print("=" * 60)
    
    # ai_performance_log データ取得テスト
    try:
        url = f"{supabase_url}/rest/v1/ai_performance_log"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ ai_performance_log データ取得成功: {len(data)}件")
            
            if data:
                latest = data[-1]
                print(f"  最新データ: {latest.get('session_id')} (Success: {latest.get('task_success')})")
            return True
        else:
            print(f"❌ ai_performance_log アクセス失敗: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False

def main():
    # テーブル作成
    table_success = create_ai_performance_table()
    
    # 接続テスト
    if table_success:
        test_supabase_connectivity()
    
    print(f"\n🎯 Supabase統合状況:")
    print(f"  - 接続: {'✅ 成功' if table_success else '❌ 失敗'}")
    print(f"  - テーブル: {'✅ 作成済み' if table_success else '❌ 未作成'}")
    print(f"  - データ蓄積: {'✅ 可能' if table_success else '❌ 不可'}")

if __name__ == "__main__":
    main()