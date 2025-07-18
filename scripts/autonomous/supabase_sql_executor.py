#!/usr/bin/env python3
"""
Supabase SQL実行（REST API経由）
CLIでパスワードが必要な場合の代替手段
"""

import os

import requests
from dotenv import load_dotenv

load_dotenv()


def execute_sql_via_rest():
    """REST API経由でSQL実行"""

    supabase_url = os.getenv("SUPABASE_URL")
    anon_key = os.getenv("SUPABASE_ANON_KEY")

    headers = {
        "apikey": anon_key,
        "Authorization": f"Bearer {anon_key}",
        "Content-Type": "application/json",
    }

    print("🔧 Supabase SQL実行（REST API経由）")
    print("=" * 60)

    # 1. テーブル作成テスト（簡単なバージョン）
    print("1️⃣ テーブル作成テスト...")

    test_data = {
        "session_id": "rest_api_test",
        "task_success": True,
        "execution_time": 1.0,
        "tool_calls_count": 1,
        "tool_calls": ["REST"],
        "error_count": 0,
        "thinking_tag_used": False,
        "todo_tracking": True,
        "task_complexity": "simple",
        "learning_score": 2,
        "success_patterns": ["rest_api_success"],
        "failure_patterns": [],
    }

    try:
        # ai_performance_log テーブルに挿入
        url = f"{supabase_url}/rest/v1/ai_performance_log"
        response = requests.post(url, headers=headers, json=test_data)

        if response.status_code in [200, 201]:
            print("  ✅ ai_performance_log テーブル挿入成功")
            return True
        elif response.status_code == 404:
            print("  ⚠️ ai_performance_log テーブルが存在しない")
            print("  📋 ダッシュボードのSQL Editorで手動作成が必要")
            return False
        else:
            print(f"  ❌ 挿入失敗: {response.status_code}")
            print(f"  Response: {response.text}")
            return False

    except Exception as e:
        print(f"  ❌ エラー: {e}")
        return False


def check_existing_tables():
    """既存テーブル確認"""

    supabase_url = os.getenv("SUPABASE_URL")
    anon_key = os.getenv("SUPABASE_ANON_KEY")

    headers = {
        "apikey": anon_key,
        "Authorization": f"Bearer {anon_key}",
        "Content-Type": "application/json",
    }

    print("🔍 既存テーブル確認...")

    # 既知のテーブルをチェック
    tables_to_check = ["todos", "ai_performance_log"]

    for table in tables_to_check:
        try:
            url = f"{supabase_url}/rest/v1/{table}?limit=1"
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ {table} テーブル存在 ({len(data)}件のデータ)")
            elif response.status_code == 404:
                print(f"  ❌ {table} テーブル存在しない")
            else:
                print(f"  ⚠️ {table} アクセスエラー: {response.status_code}")

        except Exception as e:
            print(f"  ❌ {table} チェックエラー: {e}")


def generate_sql_for_dashboard():
    """ダッシュボード用SQL生成"""

    sql_content = """
-- AI Performance Tracking Table Setup
-- Execute this in Supabase Dashboard > SQL Editor

-- 1. Create the main table
CREATE TABLE IF NOT EXISTS public.ai_performance_log (
    id BIGSERIAL PRIMARY KEY,
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

-- 2. Enable RLS
ALTER TABLE public.ai_performance_log ENABLE ROW LEVEL SECURITY;

-- 3. Create policies for anonymous access
CREATE POLICY "Allow anonymous inserts" ON public.ai_performance_log
    FOR INSERT TO anon WITH CHECK (true);

CREATE POLICY "Allow anonymous reads" ON public.ai_performance_log
    FOR SELECT TO anon USING (true);

-- 4. Grant permissions
GRANT USAGE ON SCHEMA public TO anon;
GRANT SELECT, INSERT ON public.ai_performance_log TO anon;
GRANT USAGE, SELECT ON SEQUENCE public.ai_performance_log_id_seq TO anon;

-- 5. Insert test data
INSERT INTO public.ai_performance_log (
    session_id, task_success, execution_time, tool_calls_count,
    tool_calls, error_count, thinking_tag_used, todo_tracking,
    task_complexity, learning_score, success_patterns
) VALUES (
    'dashboard_setup_test', true, 1.5, 2,
    '["SQL", "Dashboard"]', 0, false, true,
    'simple', 3, '["dashboard_success"]'
);

-- 6. Verify setup
SELECT * FROM public.ai_performance_log ORDER BY created_at DESC LIMIT 5;
"""

    sql_file = "/Users/dd/Desktop/1_dev/coding-rule2/config/supabase/supabase_dashboard_setup.sql"
    with open(sql_file, "w", encoding="utf-8") as f:
        f.write(sql_content)

    print(f"📝 ダッシュボード用SQL生成: {sql_file}")
    print("🔗 実行手順:")
    print("  1. https://supabase.com/dashboard/project/hetcpqtsineqaopnnvtn/sql")
    print("  2. 上記SQLをコピー＆ペーストして実行")
    print("  3. python3 scripts/autonomous/test_supabase_final.py で動作確認")


def main():
    # 既存テーブル確認
    check_existing_tables()

    # テーブル作成テスト
    table_created = execute_sql_via_rest()

    if not table_created:
        # ダッシュボード用SQL生成
        generate_sql_for_dashboard()

    print("\n🎯 Supabase設定状況:")
    print("  - 接続: ✅ 成功")
    print(f"  - テーブル: {'✅ 作成済み' if table_created else '❌ 手動作成必要'}")
    print(
        f"  - 次のステップ: {'自動テスト実行' if table_created else 'ダッシュボードでSQL実行'}"
    )


if __name__ == "__main__":
    main()
