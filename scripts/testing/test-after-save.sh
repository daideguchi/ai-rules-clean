#!/bin/bash

echo "🧪 保存後テストスクリプト"
echo "===================="

echo "📤 テストデータ送信中..."
curl -X POST 'https://dd1107.app.n8n.cloud/webhook/working-claude-1752496422' \
  -H 'Content-Type: application/json' \
  -d '{"session_id":"after_save_test","success":true,"execution_time":3.0,"tools_used":"save_test","error_count":0,"thinking_tag_used":true,"todo_tracking":true,"task_complexity":"medium","learning_score":8}'

echo -e "\n⏳ 5秒待機後Supabase確認..."
sleep 5

echo "🔍 Supabaseデータ確認中..."
curl -H "apikey: $SUPABASE_ANON_KEY" \
  -H "Authorization: Bearer $SUPABASE_ANON_KEY" \
  "$SUPABASE_URL/rest/v1/ai_performance_log?session_id=eq.after_save_test"

echo -e "\n✅ テスト完了"