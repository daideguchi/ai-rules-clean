#!/bin/bash

echo "🧪 手動アクティブ化後の最終統合テスト"
echo "======================================"

SESSION_ID="manual_activation_$(date +%s)"

echo "📤 テストデータ送信..."
echo "Session ID: $SESSION_ID"

RESPONSE=$(curl -s -X POST 'https://dd1107.app.n8n.cloud/webhook/working-claude-1752496422' \
  -H 'Content-Type: application/json' \
  -d "{\"session_id\":\"$SESSION_ID\",\"task_success\":true,\"execution_time_seconds\":15.0,\"tools_used\":\"manual_activation\",\"error_count\":0,\"thinking_tag_used\":true,\"todo_tracking\":true,\"task_complexity\":\"ultimate\",\"learning_score\":10,\"session_notes\":\"Manual activation success\"}")

echo "Webhook応答: $RESPONSE"

if [[ "$RESPONSE" == *"Workflow was started"* ]]; then
    echo "✅ Webhook送信成功"
    
    echo "⏳ 15秒待機（データ処理）..."
    sleep 15
    
    echo "🔍 Supabaseデータ確認..."
    SUPABASE_DATA=$(curl -s -H "apikey: $SUPABASE_ANON_KEY" \
      -H "Authorization: Bearer $SUPABASE_ANON_KEY" \
      "$SUPABASE_URL/rest/v1/ai_performance_log?session_id=eq.$SESSION_ID")
    
    echo "Supabaseデータ: $SUPABASE_DATA"
    
    if [[ "$SUPABASE_DATA" != "[]" ]]; then
        echo ""
        echo "🎉 **🎊 完全統合成功 🎊**"
        echo "✅ Claude→n8n→Supabase自動化達成"
        echo "🔄 自律AI成長システム稼働開始"
        echo "📡 本番URL: https://dd1107.app.n8n.cloud/webhook/working-claude-1752496422"
        echo "🧠 AIパフォーマンスデータ自動蓄積開始"
    else
        echo ""
        echo "⚠️ Webhookは成功したがSupabaseデータ未反映"
        echo "📋 n8nワークフロー内でSupabaseノードエラーの可能性"
    fi
else
    echo "❌ Webhook送信失敗"
    echo "📋 ワークフローが正しくアクティブ化されていません"
fi

echo ""
echo "======================================"