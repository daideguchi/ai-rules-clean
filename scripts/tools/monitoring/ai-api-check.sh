#!/bin/bash

# =============================================================================
# [LEGACY WRAPPER] ai-api-check.sh
# 
# このスクリプトは unified-monitoring-tool.py に統合されました。
# Phase 4 統合完了 - レガシー互換性のためのwrapperスクリプト
# 
# 新しい使用方法:
#   scripts/tools/unified-monitoring-tool.py api-check --interactive
# =============================================================================

echo "⚠️  [LEGACY] ai-api-check.sh は統合されました"
echo "📦 unified-monitoring-tool.py api-check に移行してください"
echo ""
echo "🔄 自動転送中..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/../unified-monitoring-tool.py" api-check --interactive "$@"

echo "🔍 AI API 実行前チェック"
echo "=========================="

# 1. モデル名確認
echo "1. 使用予定モデル名を入力:"
echo "   gemini-1.5-pro (推奨)"
echo "   gemini-1.5-flash"
echo "   o3-mini"
read -p "モデル名: " MODEL

case "$MODEL" in
    "gemini-1.5-pro"|"gemini-1.5-flash")
        echo "✅ 有効なGeminiモデル"
        ;;
    "o3-mini")
        echo "✅ 有効なO3モデル"
        ;;
    *)
        echo "❌ 無効なモデル名: $MODEL"
        echo "過去の失敗: gemini-2.0-flash-latest, gemini-2.5-pro-latest など"
        exit 1
        ;;
esac

# 2. コマンド構文確認
echo ""
echo "2. コマンド構文確認:"
if [[ "$MODEL" =~ gemini ]]; then
    echo "正しい形式: echo \"prompt\" | npx https://github.com/google-gemini/gemini-cli -m \"$MODEL\""
    echo "間違い例: -c config.txt, --model-file など"
elif [[ "$MODEL" =~ o3 ]]; then
    echo "正しい形式: mcp__o3__o3-search with input parameter"
fi

read -p "コマンド構文確認済み？ [y/n]: " SYNTAX_OK
if [[ "$SYNTAX_OK" != "y" ]]; then
    echo "❌ コマンド構文を確認してください"
    exit 1
fi

# 3. エラー時の代替手段
echo ""
echo "3. エラー時の代替手段準備:"
echo "   - Gemini失敗 → O3使用"
echo "   - クオータ制限 → 時間を置く"
echo "   - API全体停止 → ローカル実行"

read -p "代替手段準備済み？ [y/n]: " BACKUP_OK
if [[ "$BACKUP_OK" != "y" ]]; then
    echo "❌ 代替手段を準備してください"
    exit 1
fi

# 4. ログ記録
echo ""
echo "4. 実行ログ記録:"
mkdir -p runtime/ai_api_logs
LOG_FILE="runtime/ai_api_logs/$(date +%Y%m%d_%H%M%S)_${MODEL}.log"
echo "ログファイル: $LOG_FILE"

{
    echo "=== AI API 実行ログ ==="
    echo "日時: $(date)"
    echo "モデル: $MODEL"
    echo "チェック完了: $(date)"
} > "$LOG_FILE"

echo ""
echo "✅ 事前チェック完了"
echo "安全にAPI実行してください"
echo "=========================="

# エラー記録関数をエクスポート
cat << 'EOF' > runtime/ai_api_logs/error_logger.sh
#!/bin/bash
log_api_error() {
    local error="$1"
    local command="$2"
    echo "$(date): ERROR: $error | CMD: $command" >> runtime/ai_api_logs/api_errors.log
}
EOF

echo "エラー時は以下を実行:"
echo "source runtime/ai_api_logs/error_logger.sh"
echo "log_api_error \"エラー内容\" \"実行コマンド\""