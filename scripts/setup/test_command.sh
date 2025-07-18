#!/bin/bash

echo "🚀 Execute workflowボタンを押した直後にこのコマンドを実行してください！"
echo ""

curl -X POST "https://dd1107.app.n8n.cloud/webhook-test/claude-fresh-1752494073" \
  -H "Content-Type: application/json" \
  -d '{"session_id":"final_integration_test","success":true,"execution_time":2.0,"tools_used":["final","integration"],"error_count":0,"thinking_tag_used":true,"todo_tracking":true,"task_complexity":"medium","learning_score":5}'

echo ""
echo "⏳ 3秒後にSupabaseデータ確認..."
sleep 3

echo "🔍 Supabaseデータ確認中..."
curl -H "apikey: $SUPABASE_ANON_KEY" \
  -H "Authorization: Bearer $SUPABASE_ANON_KEY" \
  "$SUPABASE_URL/rest/v1/ai_performance_log?session_id=eq.final_integration_test"

echo ""
echo "✅ 統合テスト完了"