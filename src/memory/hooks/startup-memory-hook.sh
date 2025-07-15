#!/bin/bash
# 🚀 Claude Code起動時自動記憶継承フック
# ユーザーが何も言わなくても、起動時に自動で記憶を継承表示

set -euo pipefail

# 設定
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MEMORY_UI_SCRIPT="${SCRIPT_DIR}/../ui/auto-memory-display.js"
MEMORY_CONFIG="${SCRIPT_DIR}/../../../memory/core/memory-env.conf"
LOG_FILE="${SCRIPT_DIR}/../../../../logs/claude-code-startup-hook.log"

# ログ関数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "${LOG_FILE}"
}

# 設定読み込み
load_memory_config() {
    if [[ -f "${MEMORY_CONFIG}" ]]; then
        # shellcheck source=/dev/null
        source "${MEMORY_CONFIG}"
        log "✅ 記憶設定読み込み完了: ${MEMORY_CONFIG}"
    else
        log "⚠️ 記憶設定ファイル未検出、デフォルト設定使用"
        CLAUDE_MEMORY_AUTO_LOAD=true
        CLAUDE_MEMORY_INHERITANCE_MODE=auto
    fi
}

# 記憶継承が有効かチェック
is_memory_inheritance_enabled() {
    [[ "${CLAUDE_MEMORY_AUTO_LOAD:-true}" == "true" ]] && \
    [[ "${CLAUDE_MEMORY_INHERITANCE_MODE:-auto}" == "auto" ]]
}

# Claude Code起動検出
detect_claude_code_startup() {
    # プロセス名やコマンドラインでClaude Code起動を検出
    if pgrep -f "claude.*code" > /dev/null 2>&1; then
        return 0
    fi
    
    # 環境変数での検出
    if [[ "${CLAUDE_CODE_SESSION:-}" ]]; then
        return 0
    fi
    
    # フォールバック: 手動起動
    return 1
}

# 記憶継承表示実行
execute_memory_inheritance() {
    log "🧠 自動記憶継承開始..."
    
    # Node.js記憶表示システム実行
    if [[ -f "${MEMORY_UI_SCRIPT}" ]]; then
        if node "${MEMORY_UI_SCRIPT}" 2>&1; then
            log "✅ 記憶継承表示完了"
            return 0
        else
            log "❌ 記憶継承表示エラー"
            return 1
        fi
    else
        log "❌ 記憶表示スクリプト未検出: ${MEMORY_UI_SCRIPT}"
        return 1
    fi
}

# フォールバック記憶表示
fallback_memory_display() {
    log "🔄 フォールバック記憶表示実行..."
    
    echo ""
    echo "=================================================================================="
    echo "🧠 Claude Code 記憶継承システム"
    echo "=================================================================================="
    echo "📋 前回セッションの記憶を継承しています..."
    echo ""
    
    # 基本情報表示
    if [[ -d "${SCRIPT_DIR}/../../../memory/core/session-records" ]]; then
        local session_count
        session_count=$(find "${SCRIPT_DIR}/../../../memory/core/session-records" -name "*.json" | wc -l)
        echo "📊 記録済みセッション数: ${session_count}"
    fi
    
    # 重要な設定表示
    echo "⚙️ 記憶継承モード: ${CLAUDE_MEMORY_INHERITANCE_MODE:-auto}"
    echo "🎯 AI連携対象: ${CLAUDE_MEMORY_AI_TARGETS:-claude,gemini,o3}"
    echo ""
    
    # 簡易指示表示
    echo "💡 記憶継承ヒント:"
    echo "   • 前回の作業内容は自動で継承されます"
    echo "   • 重要な指示・禁止事項は優先表示されます"
    echo "   • 未完了タスクがある場合は続行できます"
    echo ""
    echo "=================================================================================="
    echo "✅ 記憶継承準備完了 - 作業を開始できます"
    echo "=================================================================================="
    echo ""
}

# 起動時チェック機能
startup_environment_check() {
    log "🔍 起動環境チェック開始..."
    
    # Node.js確認
    if ! command -v node > /dev/null 2>&1; then
        log "⚠️ Node.js未検出 - フォールバックモード"
        return 1
    fi
    
    # Python確認
    if ! command -v python3 > /dev/null 2>&1; then
        log "⚠️ Python3未検出 - 基本機能のみ"
        return 1
    fi
    
    # 記憶ディレクトリ確認
    if [[ ! -d "${SCRIPT_DIR}/../../../memory" ]]; then
        log "⚠️ 記憶ディレクトリ未検出"
        return 1
    fi
    
    log "✅ 起動環境チェック完了"
    return 0
}

# メイン実行フロー
main() {
    # ログディレクトリ作成
    mkdir -p "$(dirname "${LOG_FILE}")"
    
    log "🚀 Claude Code起動時記憶継承フック開始"
    
    # 設定読み込み
    load_memory_config
    
    # 記憶継承有効性チェック
    if ! is_memory_inheritance_enabled; then
        log "ℹ️ 記憶継承無効 - スキップ"
        exit 0
    fi
    
    # Claude Code起動検出
    if ! detect_claude_code_startup; then
        log "ℹ️ Claude Code起動未検出 - 手動実行"
    fi
    
    # 起動環境チェック
    if startup_environment_check; then
        # フル機能記憶継承実行
        if ! execute_memory_inheritance; then
            log "🔄 フォールバックモードに切り替え"
            fallback_memory_display
        fi
    else
        # フォールバック表示
        fallback_memory_display
    fi
    
    log "✅ 記憶継承フック完了"
}

# 引数処理
case "${1:-auto}" in
    "manual")
        log "🎯 手動記憶継承実行"
        load_memory_config
        execute_memory_inheritance
        ;;
    "test")
        log "🧪 記憶継承テスト実行"
        load_memory_config
        startup_environment_check
        fallback_memory_display
        ;;
    "status")
        load_memory_config
        echo "記憶継承設定状態:"
        echo "  自動読み込み: ${CLAUDE_MEMORY_AUTO_LOAD:-true}"
        echo "  継承モード: ${CLAUDE_MEMORY_INHERITANCE_MODE:-auto}"
        echo "  AI連携対象: ${CLAUDE_MEMORY_AI_TARGETS:-claude,gemini,o3}"
        ;;
    "auto"|*)
        main
        ;;
esac