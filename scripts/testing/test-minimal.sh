#!/bin/bash

echo "🧪 最小限ワークフロー手動アクティブ化後テスト"
echo "============================================"

curl -X POST 'https://dd1107.app.n8n.cloud/webhook/fresh-minimal-1752530948' \
  -H 'Content-Type: application/json' \
  -d '{"test":"manual_activation"}'

echo -e "\n⏳ 8秒待機後Supabase確認..."
sleep 8

echo "🔍 固定データSupabase確認..."
curl -H "apikey: $SUPABASE_ANON_KEY" \
  -H "Authorization: Bearer $SUPABASE_ANON_KEY" \
  "$SUPABASE_URL/rest/v1/ai_performance_log?session_id=eq.minimal_test_1752530948"

echo -e "\n✅ テスト完了"