#!/bin/bash

echo "🧪 Supabaseノード修正後の最終テスト"
echo "=================================="

curl -X POST 'https://dd1107.app.n8n.cloud/webhook/working-claude-1752496422' \
  -H 'Content-Type: application/json' \
  -d '{"session_id":"supabase_fix_final","success":true,"execution_time":10.0,"tools_used":"supabase_fix","error_count":0,"thinking_tag_used":true,"todo_tracking":true,"task_complexity":"ultimate","learning_score":10}'

echo -e "\n⏳ 10秒待機後Supabase確認..."
sleep 10

echo "🔍 Supabaseデータ確認中..."
result=$(curl -s -H "apikey: $SUPABASE_ANON_KEY" \
  -H "Authorization: Bearer $SUPABASE_ANON_KEY" \
  "$SUPABASE_URL/rest/v1/ai_performance_log?session_id=eq.supabase_fix_final")

echo "$result"

if [[ "$result" != "[]" ]]; then
    echo ""
    echo "🎉 **🎊 完全統合成功 🎊**"
    echo "✅ Claude→n8n→Supabase自動化達成"
    echo "🔄 自律AI成長システム稼働開始"
    echo "📡 本番URL: https://dd1107.app.n8n.cloud/webhook/working-claude-1752496422"
else
    echo ""
    echo "⚠️ まだSupabaseにデータが確認できません"
fi