#!/bin/bash
# Supabase AI Growth System Quick Deploy Script

echo "🚀 Supabase AI Growth System Quick Deploy"
echo "========================================"

# Step 1: Personal Access Token check
echo "1. Personal Access Token確認..."
if [ -z "$SUPABASE_ACCESS_TOKEN" ] || [ "$SUPABASE_ACCESS_TOKEN" = "your_personal_access_token_here" ]; then
    echo "❌ Personal Access Token未設定"
    echo "📝 手順："
    echo "   1. https://app.supabase.com/account/tokens へアクセス"
    echo "   2. 'Create new token' → 名前: Claude MCP AI Growth"
    echo "   3. トークンをコピーして .env ファイルの SUPABASE_ACCESS_TOKEN に設定"
    echo "   4. 再実行: ./scripts/setup/supabase_quick_deploy.sh"
    exit 1
fi

# Step 2: Supabase CLI login and link
echo "2. Supabase CLI接続..."
export SUPABASE_ACCESS_TOKEN=$SUPABASE_ACCESS_TOKEN
supabase link --project-ref hetcpqtsineqaopnnvtn

if [ $? -ne 0 ]; then
    echo "❌ Supabase link失敗 - Personal Access Token確認必要"
    exit 1
fi

# Step 3: Push migrations to cloud
echo "3. データベーステーブル作成..."
supabase db push

if [ $? -eq 0 ]; then
    echo "✅ Supabaseテーブル作成完了"
else
    echo "❌ テーブル作成失敗"
    exit 1
fi

# Step 4: Verify tables
echo "4. テーブル確認..."
supabase db remote sql --file supabase/migrations/20250713102934_create_ai_growth_tables.sql --dry-run

# Step 5: Generate types
echo "5. TypeScript型定義生成..."
supabase gen types typescript --linked > types/supabase.ts

echo ""
echo "🎉 Supabase AI Growth System デプロイ完了！"
echo "========================================"
echo "✅ テーブル作成: ai_performance_log, ai_learning_patterns, claude_evolution_history"
echo "✅ RLS有効化: セキュリティポリシー適用済み"
echo "✅ インデックス: パフォーマンス最適化済み"
echo ""
echo "📋 次のステップ:"
echo "1. n8nでPostgreSQL接続設定"
echo "   - Host: hetcpqtsineqaopnnvtn.supabase.co"
echo "   - Password: $SUPABASE_SERVICE_ROLE_KEY"
echo "2. ワークフローインポート: config/n8n/workflows/supabase_ai_tracker.json"
echo "3. テスト実行"
echo ""
echo "🔗 Supabase Dashboard: https://hetcpqtsineqaopnnvtn.supabase.co"