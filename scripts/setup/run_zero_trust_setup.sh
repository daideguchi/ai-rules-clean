#!/bin/bash
# Cloudflare Zero Trust + n8n セットアップ実行

echo "🌐 Cloudflare Zero Trust セットアップ"
echo "=================================="

# 環境変数設定
echo "🔑 Cloudflare認証情報を入力してください:"
read -p "API Token: " CF_API_TOKEN
read -p "Account ID: " CF_ACCOUNT_ID

# 環境変数設定
export CLOUDFLARE_API_TOKEN="$CF_API_TOKEN"
export CLOUDFLARE_ACCOUNT_ID="$CF_ACCOUNT_ID"

# n8n設定も環境変数に設定
source .env
export N8N_API_KEY="$N8N_API_KEY"
export N8N_API_URL="$N8N_API_URL"

echo "✅ 環境変数設定完了"

# Zero Trust セットアップ実行
echo "🚀 Zero Trust セットアップ実行中..."
python3 scripts/setup/cloudflare_zero_trust_setup.py

if [ $? -eq 0 ]; then
    echo "🎉 Zero Trust セットアップ成功!"
    echo "🧬 自律AI成長システム準備完了!"
    
    # 環境変数を.envに保存
    cat >> .env << EOF

# Cloudflare Zero Trust ($(date))
CLOUDFLARE_API_TOKEN=$CF_API_TOKEN
CLOUDFLARE_ACCOUNT_ID=$CF_ACCOUNT_ID
ZERO_TRUST_SETUP_COMPLETED=true
EOF
    
    echo "📝 設定を.envに保存完了"
    
else
    echo "❌ Zero Trust セットアップ失敗"
    echo "💡 代替案: bash scripts/setup/webhook_url_setup.sh"
fi