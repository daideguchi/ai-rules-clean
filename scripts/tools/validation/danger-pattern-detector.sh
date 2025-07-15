#!/bin/bash

# =============================================================================
# [LEGACY WRAPPER] danger-pattern-detector.sh
# 
# このスクリプトは unified-validation-tool.py に統合されました。
# Phase 6 統合完了 - レガシー互換性のためのwrapperスクリプト
# 
# 新しい使用方法:
#   scripts/tools/unified-validation-tool.py danger-check "<command>"
# =============================================================================

echo "⚠️  [LEGACY] danger-pattern-detector.sh は統合されました"
echo "📦 unified-validation-tool.py danger-check に移行してください"
echo ""
echo "🔄 自動転送中..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 引数をまとめて統合ツールに転送
command_to_check="$*"
if [[ -z "$command_to_check" ]]; then
    command_to_check="echo test"
fi

exec python3 "$SCRIPT_DIR/../unified-validation-tool.py" danger-check "$command_to_check"

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PATTERNS_FILE="$PROJECT_ROOT/runtime/ai_api_logs/danger_patterns.json"

# 危険パターン定義
init_patterns() {
    mkdir -p "$PROJECT_ROOT/runtime/ai_api_logs"
    
    cat > "$PATTERNS_FILE" << 'EOF'
{
  "gemini_cli_errors": [
    {
      "pattern": "npx.*gemini-cli.*-c",
      "error": "CLI引数誤用: -cは設定ファイルではありません",
      "fix": "モデル指定は -m オプションを使用"
    },
    {
      "pattern": "gemini-2\\.0-flash-latest",
      "error": "存在しないモデル名",
      "fix": "gemini-1.5-pro または gemini-1.5-flash を使用"
    },
    {
      "pattern": "gemini.*--model-file",
      "error": "存在しないオプション",
      "fix": "--help で正しいオプションを確認"
    }
  ],
  "security_risks": [
    {
      "pattern": "api-key.*[^=]",
      "error": "APIキー直接指定",
      "fix": "環境変数を使用"
    },
    {
      "pattern": "rm -rf.*runtime",
      "error": "重要データ削除",
      "fix": "個別ファイルを指定"
    }
  ]
}
EOF
}

# コマンド検証
check_command() {
    local command="$1"
    local found_issues=()
    
    echo "🔍 危険パターン検出中: $command"
    
    # シンプルなパターンマッチング（jq依存排除）
    if [[ "$command" =~ npx.*gemini-cli.*\ -c ]]; then
        found_issues+=("❌ CLI引数誤用: -cは設定ファイルではありません | 修正: -m オプションを使用")
    fi
    
    if [[ "$command" =~ "gemini-2\.0-flash-latest" ]]; then
        found_issues+=("❌ 存在しないモデル名 | 修正: gemini-2.5-pro または gemini-2.0-flash を使用")
    fi
    
    if [[ "$command" =~ "gemini.*--model-file" ]]; then
        found_issues+=("❌ 存在しないオプション | 修正: --help で確認")
    fi
    
    if [[ "$command" =~ "api-key.*[^=]" ]]; then
        found_issues+=("❌ APIキー直接指定 | 修正: 環境変数を使用")
    fi
    
    # 結果表示
    if [[ ${#found_issues[@]} -gt 0 ]]; then
        echo ""
        echo "🚨 危険なパターンを検出しました:"
        for issue in "${found_issues[@]}"; do
            echo "   $issue"
        done
        echo ""
        return 1
    else
        echo "✅ 危険パターンなし"
        return 0
    fi
}

# 過去の失敗例表示
show_historical_context() {
    echo ""
    echo "📚 過去の同様失敗例:"
    echo "   2025-07-07: Gemini CLI引数誤用"
    echo "   - エラー: -c オプションの誤解"
    echo "   - 結果: Unknown argument エラー"
    echo ""
    echo "   2025-07-07: 存在しないモデル名"
    echo "   - エラー: gemini-2.0-flash-latest"
    echo "   - 結果: 404 Not Found"
    echo ""
}

# メイン処理
main() {
    # 初期化
    [[ -f "$PATTERNS_FILE" ]] || init_patterns
    
    if [[ $# -eq 0 ]]; then
        echo "使用法: $0 <command>"
        echo "例: $0 'echo \"test\" | npx https://github.com/google-gemini/gemini-cli -m gemini-1.5-pro'"
        exit 1
    fi
    
    local command="$*"
    
    # パターンチェック
    if ! check_command "$command"; then
        show_historical_context
        
        echo "このコマンドを実行しますか？"
        read -p "危険を承知で続行 [y/N]: " choice
        
        if [[ "$choice" != "y" ]]; then
            echo "🛑 実行をキャンセルしました"
            exit 1
        fi
    fi
    
    echo "🎯 安全なコマンドです"
}

main "$@"