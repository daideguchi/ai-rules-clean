#!/bin/bash

SESSION_ID="final_verification_$(date +%s)"
echo "🔧 n8nワークフロー修正後の最終検証"
echo "=================================="

# 1. n8nワークフローテスト
echo "1️⃣ n8nワークフローテスト..."
RESPONSE=$(curl -s -X POST 'https://dd1107.app.n8n.cloud/webhook/working-claude-1752496422' \
  -H 'Content-Type: application/json' \
  -d "{\"session_id\":\"$SESSION_ID\",\"task_success\":true,\"execution_time_seconds\":7.5,\"tools_used\":\"final_test\",\"error_count\":0,\"thinking_tag_used\":true,\"todo_tracking\":true,\"task_complexity\":\"high\",\"learning_score\":9,\"session_notes\":\"Working solution\"}")

echo "Webhook応答: $RESPONSE"

# 2. 10秒待機
echo "2️⃣ 10秒待機中..."
sleep 10

# 3. Supabaseデータ確認
echo "3️⃣ Supabaseデータ確認..."
SUPABASE_DATA=$(curl -s -X GET "https://hetcpqtsineqaopnnvtn.supabase.co/rest/v1/ai_performance_log?select=*&session_id=eq.$SESSION_ID" \
  -H 'apikey: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhldGNwcXRzaW5lcWFvcG5udnRuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI0MDEzNDEsImV4cCI6MjA2Nzk3NzM0MX0.WAgCVM-XZY0JqYzap7fCXxu6PeX9vES-zitAhoySIbg' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhldGNwcXRzaW5lcWFvcG5udnRuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI0MDEzNDEsImV4cCI6MjA2Nzk3NzM0MX0.WAgCVM-XZY0JqYzap7fCXxu6PeX9vES-zitAhoySIbg')

echo "Supabaseデータ: $SUPABASE_DATA"

# 4. 結果判定
if [[ "$SUPABASE_DATA" == "[]" ]]; then
  echo "❌ 統合失敗: Supabaseにデータが反映されていません"
  echo "📝 n8nワークフローのSupabaseノード設定を再確認してください"
else
  echo "✅ 統合成功: Claude→n8n→Supabase完全統合達成！"
  echo "🎉 おめでとうございます！"
fi

echo "==================================" 