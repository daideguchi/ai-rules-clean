#!/bin/bash

# Claude Code自動記憶継承ローダー
# Claude Code起動時に自動で記憶を読み込むシステム

set -euo pipefail

# 設定
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SESSION_BRIDGE_SCRIPT="$SCRIPT_DIR/session-inheritance-bridge.sh"
MEMORY_CONFIG_DIR="${PROJECT_ROOT}/memory/core"
CLAUDE_CODE_MEMORY_FILE="$MEMORY_CONFIG_DIR/claude-code-memory-state.json"
LOG_FILE="${PROJECT_ROOT}/logs/claude-code-auto-memory.log"

# 環境変数設定ファイル
MEMORY_ENV_FILE="$MEMORY_CONFIG_DIR/memory-env.conf"

# ログ関数
log_memory() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [CLAUDE-AUTO-MEMORY] $1" | tee -a "$LOG_FILE"
}

# 環境変数読み込み
load_memory_environment() {
    log_memory "🔧 環境変数読み込み開始"
    
    # デフォルト環境変数設定
    export CLAUDE_MEMORY_AUTO_LOAD="${CLAUDE_MEMORY_AUTO_LOAD:-true}"
    export CLAUDE_MEMORY_INHERITANCE_MODE="${CLAUDE_MEMORY_INHERITANCE_MODE:-auto}"
    export CLAUDE_MEMORY_AI_TARGETS="${CLAUDE_MEMORY_AI_TARGETS:-claude,gemini,o3}"
    export CLAUDE_MEMORY_PRIORITY_THRESHOLD="${CLAUDE_MEMORY_PRIORITY_THRESHOLD:-medium}"
    export CLAUDE_MEMORY_SESSION_TIMEOUT="${CLAUDE_MEMORY_SESSION_TIMEOUT:-3600}"
    
    # 環境設定ファイルから読み込み
    if [ -f "$MEMORY_ENV_FILE" ]; then
        log_memory "📄 設定ファイル読み込み: $MEMORY_ENV_FILE"
        source "$MEMORY_ENV_FILE"
    else
        log_memory "⚠️ 設定ファイルが見つかりません、デフォルト設定を使用: $MEMORY_ENV_FILE"
    fi
    
    # 必須環境変数チェック
    if [ -z "${OPENAI_API_KEY:-}" ]; then
        log_memory "❌ OPENAI_API_KEY が設定されていません"
        return 1
    fi
    
    log_memory "✅ 環境変数読み込み完了"
    return 0
}

# 記憶状態ファイル作成
create_memory_state_file() {
    local session_id="$1"
    
    log_memory "📝 記憶状態ファイル作成: $session_id"
    
    mkdir -p "$MEMORY_CONFIG_DIR"
    
    cat > "$CLAUDE_CODE_MEMORY_FILE" << EOF
{
  "session_id": "$session_id",
  "load_timestamp": "$(date -Iseconds)",
  "auto_load_enabled": ${CLAUDE_MEMORY_AUTO_LOAD},
  "inheritance_mode": "$CLAUDE_MEMORY_INHERITANCE_MODE",
  "ai_targets": "$CLAUDE_MEMORY_AI_TARGETS",
  "priority_threshold": "$CLAUDE_MEMORY_PRIORITY_THRESHOLD",
  "session_timeout": $CLAUDE_MEMORY_SESSION_TIMEOUT,
  "memory_state": {
    "inheritance_completed": false,
    "ai_sync_completed": false,
    "critical_info_displayed": false
  },
  "environment": {
    "claude_code_version": "$(claude --version 2>/dev/null || echo 'unknown')",
    "python_version": "$(python3 --version 2>/dev/null || echo 'unknown')",
    "system": "$(uname -s)",
    "working_directory": "$(pwd)"
  }
}
EOF
    
    log_memory "✅ 記憶状態ファイル作成完了: $CLAUDE_CODE_MEMORY_FILE"
}

# Claude Code起動フック
claude_code_startup_hook() {
    log_memory "🚀 Claude Code起動フック開始"
    
    # 環境変数読み込み
    if ! load_memory_environment; then
        log_memory "❌ 環境変数読み込み失敗"
        return 1
    fi
    
    # 自動読み込み無効チェック
    if [ "$CLAUDE_MEMORY_AUTO_LOAD" != "true" ]; then
        log_memory "⏸️ 自動記憶読み込みは無効に設定されています"
        return 0
    fi
    
    # セッションID生成
    local session_id="claude-code-$(date +%Y%m%d-%H%M%S)-$$"
    
    # 記憶状態ファイル作成
    create_memory_state_file "$session_id"
    
    # セッション記憶継承実行
    log_memory "🧠 セッション記憶継承開始: $session_id"
    
    if [ -f "$SESSION_BRIDGE_SCRIPT" ]; then
        # session-inheritance-bridge.sh呼び出し
        if "$SESSION_BRIDGE_SCRIPT" startup; then
            log_memory "✅ セッション記憶継承成功"
            
            # 状態ファイル更新
            update_memory_state "inheritance_completed" true
            update_memory_state "ai_sync_completed" true
            update_memory_state "critical_info_displayed" true
            
            # 成功メッセージ表示
            display_memory_load_success "$session_id"
            
        else
            log_memory "❌ セッション記憶継承失敗"
            return 1
        fi
    else
        log_memory "❌ セッション継承スクリプトが見つかりません: $SESSION_BRIDGE_SCRIPT"
        return 1
    fi
    
    log_memory "🎉 Claude Code起動フック完了"
    return 0
}

# 記憶状態更新
update_memory_state() {
    local key="$1"
    local value="$2"
    
    if [ -f "$CLAUDE_CODE_MEMORY_FILE" ]; then
        # JSONファイル更新（簡易版）
        local tmp_file=$(mktemp)
        python3 -c "
import json
import sys

try:
    with open('$CLAUDE_CODE_MEMORY_FILE', 'r') as f:
        data = json.load(f)
    
    data['memory_state']['$key'] = $value
    
    with open('$tmp_file', 'w') as f:
        json.dump(data, f, indent=2)
    
    print('OK')
except Exception as e:
    print(f'ERROR: {e}', file=sys.stderr)
    sys.exit(1)
"
        if [ $? -eq 0 ]; then
            mv "$tmp_file" "$CLAUDE_CODE_MEMORY_FILE"
            log_memory "📝 記憶状態更新: $key = $value"
        else
            log_memory "❌ 記憶状態更新失敗: $key = $value"
            rm -f "$tmp_file"
        fi
    fi
}

# 成功メッセージ表示
display_memory_load_success() {
    local session_id="$1"
    
    cat << EOF

🧠 ===============================
   Claude Code 記憶継承システム
   ～ セッション間記憶喪失根絶 ～
===============================

✅ 記憶継承状態: 完了
🆔 セッションID: $session_id
🤖 AI連携: $CLAUDE_MEMORY_AI_TARGETS
⚙️ 継承モード: $CLAUDE_MEMORY_INHERITANCE_MODE
📊 優先度閾値: $CLAUDE_MEMORY_PRIORITY_THRESHOLD

🚨 重要継承情報:
   👑 役割: PRESIDENT
   🎯 使命: AI永続記憶システム実装統括
   📊 継承ミス回数: 78回
   🛡️ 防止対象: 79回目のミス
   💰 予算: \$33,000 (Phase 1)
   ⚙️ 技術: PostgreSQL + pgvector + Claude Code hooks

🎯 準備完了 - 記憶を引き継いだ状態でスタートします！

===============================

EOF
}

# 手動記憶読み込み
manual_memory_load() {
    local force_reload="${1:-false}"
    
    log_memory "🔄 手動記憶読み込み開始 (force_reload: $force_reload)"
    
    if [ "$force_reload" = "true" ] || [ ! -f "$CLAUDE_CODE_MEMORY_FILE" ]; then
        claude_code_startup_hook
    else
        log_memory "⚠️ 既に記憶が読み込まれています。強制読み込みには --force オプションを使用してください"
        return 1
    fi
}

# 記憶状態確認
check_memory_status() {
    log_memory "📊 記憶状態確認"
    
    if [ -f "$CLAUDE_CODE_MEMORY_FILE" ]; then
        echo "📄 記憶状態ファイル: 存在"
        echo "📊 記憶状態:"
        cat "$CLAUDE_CODE_MEMORY_FILE" | python3 -m json.tool
    else
        echo "❌ 記憶状態ファイル: 不存在"
        echo "💡 記憶を読み込むには: $0 load を実行してください"
    fi
    
    echo ""
    echo "🔧 環境変数状態:"
    echo "  CLAUDE_MEMORY_AUTO_LOAD: ${CLAUDE_MEMORY_AUTO_LOAD:-未設定}"
    echo "  CLAUDE_MEMORY_INHERITANCE_MODE: ${CLAUDE_MEMORY_INHERITANCE_MODE:-未設定}"
    echo "  CLAUDE_MEMORY_AI_TARGETS: ${CLAUDE_MEMORY_AI_TARGETS:-未設定}"
    echo "  OPENAI_API_KEY: ${OPENAI_API_KEY:+設定済み}" 
}

# 環境設定ファイル作成
create_env_config() {
    log_memory "📝 環境設定ファイル作成"
    
    mkdir -p "$MEMORY_CONFIG_DIR"
    
    cat > "$MEMORY_ENV_FILE" << EOF
# Claude Code 自動記憶継承設定
# このファイルを編集して記憶継承の動作をカスタマイズできます

# 自動記憶読み込み有効/無効
CLAUDE_MEMORY_AUTO_LOAD=true

# 記憶継承モード: auto, manual, selective
CLAUDE_MEMORY_INHERITANCE_MODE=auto

# AI連携対象: claude,gemini,o3 (カンマ区切り)
CLAUDE_MEMORY_AI_TARGETS=claude,gemini,o3

# 記憶優先度閾値: low, medium, high, critical
CLAUDE_MEMORY_PRIORITY_THRESHOLD=medium

# セッションタイムアウト（秒）
CLAUDE_MEMORY_SESSION_TIMEOUT=3600

# OpenAI API キー（必須）
# OPENAI_API_KEY=your_api_key_here

# デバッグモード
CLAUDE_MEMORY_DEBUG=false

# 記憶データ保存先
# CLAUDE_MEMORY_DATA_DIR=/custom/path/to/memory

# AI連携詳細設定
CLAUDE_MEMORY_CLAUDE_HOOKS_ENABLED=true
CLAUDE_MEMORY_GEMINI_BRIDGE_ENABLED=true
CLAUDE_MEMORY_O3_SEARCH_ENABLED=true
EOF
    
    log_memory "✅ 環境設定ファイル作成完了: $MEMORY_ENV_FILE"
    echo "📝 設定ファイルが作成されました: $MEMORY_ENV_FILE"
    echo "💡 このファイルを編集して記憶継承の動作をカスタマイズできます"
}

# ヘルプ表示
show_help() {
    cat << EOF
🧠 Claude Code 自動記憶継承ローダー

使用方法:
  $0 <コマンド> [オプション]

コマンド:
  startup                  - 起動時自動記憶読み込み（内部使用）
  load [--force]          - 手動記憶読み込み
  status                  - 記憶状態確認
  config                  - 環境設定ファイル作成
  env                     - 環境変数読み込みテスト
  help                    - このヘルプ

例:
  $0 load                 # 記憶読み込み
  $0 load --force         # 強制記憶読み込み
  $0 status               # 状態確認
  $0 config               # 設定ファイル作成

設定ファイル: $MEMORY_ENV_FILE
状態ファイル: $CLAUDE_CODE_MEMORY_FILE
ログファイル: $LOG_FILE

環境変数:
  CLAUDE_MEMORY_AUTO_LOAD - 自動読み込み有効/無効
  OPENAI_API_KEY          - OpenAI API キー（必須）
EOF
}

# メイン処理
main() {
    case "${1:-}" in
        "startup")
            claude_code_startup_hook
            ;;
        "load")
            manual_memory_load "${2:-false}"
            ;;
        "status")
            check_memory_status
            ;;
        "config")
            create_env_config
            ;;
        "env")
            load_memory_environment && echo "✅ 環境変数読み込み成功"
            ;;
        "help"|"-h"|"--help"|"")
            show_help
            ;;
        *)
            echo "❌ 無効なコマンド: $1"
            show_help
            return 1
            ;;
    esac
}

# 実行
main "$@"