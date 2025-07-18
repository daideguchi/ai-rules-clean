#!/bin/bash

echo "🎯 右上のトグルをONにした後に実行してください！"
echo ""

echo "🚀 本番URL統合テスト実行中..."
curl -X POST "https://dd1107.app.n8n.cloud/webhook/claude-fresh-1752494073" \
  -H "Content-Type: application/json" \
  -d '{"session_id":"autonomous_growth_success","success":true,"execution_time":3.0,"tools_used":["autonomous","growth","final"],"error_count":0,"thinking_tag_used":true,"todo_tracking":true,"task_complexity":"high","learning_score":10}'

echo ""
echo "⏳ 5秒後にSupabaseデータ確認..."
sleep 5

echo "🔍 Supabaseデータ確認中..."
result=$(curl -s -H "apikey: $SUPABASE_ANON_KEY" \
  -H "Authorization: Bearer $SUPABASE_ANON_KEY" \
  "$SUPABASE_URL/rest/v1/ai_performance_log?session_id=eq.autonomous_growth_success")

echo "$result"

if [[ "$result" != "[]" ]]; then
    echo ""
    echo "🎉 **完全成功！n8n→Supabase統合が正常動作**"
    echo "✅ 自律AI成長システム稼働開始"
    echo "📡 本番URL: https://dd1107.app.n8n.cloud/webhook/claude-fresh-1752494073"
    echo "🔄 今後は完全自動でデータが蓄積されます"
else
    echo ""
    echo "⚠️ まだデータが確認できません。少し待ってから再確認が必要かもしれません。"
fi