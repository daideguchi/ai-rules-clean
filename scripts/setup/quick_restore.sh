#!/bin/bash

echo "🚀 APIキー復旧後の即座実行スクリプト"
echo "使用方法: ./quick_restore.sh YOUR_N8N_API_KEY"

if [ -z "$1" ]; then
    echo "❌ エラー: n8n APIキーを引数として渡してください"
    echo "例: ./quick_restore.sh n8n_1234567890abcdef"
    exit 1
fi

N8N_KEY="$1"

echo "🔧 .envファイル更新中..."
sed -i '' "s/N8N_API_KEY=PASTE_YOUR_NEW_API_KEY_HERE/N8N_API_KEY=$N8N_KEY/" .env

echo "✅ n8n APIキー復旧完了"
echo "🚀 究極統合テスト実行中..."

# 環境変数再読み込み
source .env

# 究極統合テスト実行
python3 ultimate_solution.py

echo "🎯 復旧完了！"