#!/bin/bash

# Claude Code 起動時フック - 自動記憶継承システム
# Claude Code起動時に自動実行される統合フックシステム

set -e

# 設定
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${PROJECT_ROOT}"
MEMORY_SYSTEM_ROOT="$PROJECT_ROOT/src/ai/memory/enhanced"
LOG_FILE="$PROJECT_ROOT/logs/claude-code-startup-hook.log"

# ログ関数
log_hook() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [STARTUP-HOOK] $1" | tee -a "$LOG_FILE"
}

# 起動フック実行
execute_startup_hook() {
    log_hook "🚀 Claude Code起動フック開始"
    
    # ログディレクトリ作成
    mkdir -p "$(dirname "$LOG_FILE")"
    
    # 環境変数読み込み
    if [ -f "$PROJECT_ROOT/memory/core/memory-env.conf" ]; then
        log_hook "📄 環境設定読み込み"
        source "$PROJECT_ROOT/memory/core/memory-env.conf" 2>/dev/null || true
    fi
    
    # 自動記憶継承有効チェック
    local auto_load="${CLAUDE_MEMORY_AUTO_LOAD:-true}"
    
    if [ "$auto_load" != "true" ]; then
        log_hook "⏸️ 自動記憶継承は無効に設定されています"
        echo "💡 自動記憶継承を有効にするには環境変数 CLAUDE_MEMORY_AUTO_LOAD=true を設定してください"
        return 0
    fi
    
    log_hook "🧠 自動記憶継承システム実行開始"
    
    # session-inheritance-bridge.sh 実行
    local bridge_script="$MEMORY_SYSTEM_ROOT/session-inheritance-bridge.sh"
    
    if [ -f "$bridge_script" ]; then
        log_hook "🔗 記憶継承ブリッジ実行"
        
        # バックグラウンドで実行（Claude Code起動を阻害しないように）
        ("$bridge_script" startup 2>&1 | while IFS= read -r line; do
            log_hook "🧠 $line"
        done) &
        
        local bridge_pid=$!
        log_hook "📊 記憶継承プロセス開始: PID $bridge_pid"
        
        # 少し待機してプロセス状態確認
        sleep 1
        
        if kill -0 "$bridge_pid" 2>/dev/null; then
            log_hook "✅ 記憶継承プロセス実行中"
            echo "🧠 Claude Code記憶継承システムが起動しました"
            echo "📊 プロセスID: $bridge_pid"
            echo "📄 ログファイル: $LOG_FILE"
        else
            log_hook "⚠️ 記憶継承プロセスが早期終了しました"
        fi
        
    else
        log_hook "❌ 記憶継承スクリプトが見つかりません: $bridge_script"
        echo "❌ 記憶継承システムの初期化に失敗しました"
        return 1
    fi
    
    # 自動ローダー実行
    local auto_loader="$MEMORY_SYSTEM_ROOT/claude-code-auto-memory-loader.sh"
    
    if [ -f "$auto_loader" ]; then
        log_hook "⚡ 自動ローダー起動"
        
        # 軽量起動（起動を阻害しない）
        ("$auto_loader" load 2>&1 | while IFS= read -r line; do
            log_hook "⚡ $line"
        done) &
        
        local loader_pid=$!
        log_hook "📊 自動ローダープロセス開始: PID $loader_pid"
        
    else
        log_hook "⚠️ 自動ローダースクリプトが見つかりません: $auto_loader"
    fi
    
    # 成功メッセージ
    echo ""
    echo "🧠 ==============================================="
    echo "   Claude Code 自動記憶継承システム 起動完了"
    echo "==============================================="
    echo ""
    echo "✅ 状態: 記憶継承システム起動中"
    echo "📊 プロセス管理: バックグラウンド実行"
    echo "📄 ログ確認: tail -f $LOG_FILE"
    echo "⚙️ 設定変更: $PROJECT_ROOT/memory/core/memory-env.conf"
    echo ""
    echo "💡 記憶継承システムはバックグラウンドで動作し、"
    echo "   Claude Codeの起動を阻害しません。"
    echo ""
    echo "==============================================="
    echo ""
    
    log_hook "🎉 Claude Code起動フック完了"
    return 0
}

# 状況確認
check_status() {
    log_hook "📊 起動フック状況確認"
    
    echo "🔍 Claude Code記憶継承システム状況:"
    echo ""
    
    # 環境設定確認
    if [ -f "$PROJECT_ROOT/memory/core/memory-env.conf" ]; then
        echo "✅ 環境設定ファイル: 存在"
        local auto_load=$(grep "CLAUDE_MEMORY_AUTO_LOAD" "$PROJECT_ROOT/memory/core/memory-env.conf" 2>/dev/null | cut -d'=' -f2 || echo "未設定")
        echo "⚙️ 自動読み込み設定: $auto_load"
    else
        echo "❌ 環境設定ファイル: 不存在"
    fi
    
    # スクリプトファイル確認
    local scripts=(
        "session-inheritance-bridge.sh"
        "claude-code-auto-memory-loader.sh"
        "claude-code-memory-api.py"
    )
    
    echo ""
    echo "📂 システムファイル確認:"
    for script in "${scripts[@]}"; do
        local script_path="$MEMORY_SYSTEM_ROOT/$script"
        if [ -f "$script_path" ]; then
            echo "✅ $script: 存在"
        else
            echo "❌ $script: 不存在"
        fi
    done
    
    # ログファイル確認
    echo ""
    echo "📄 ログファイル:"
    if [ -f "$LOG_FILE" ]; then
        echo "✅ 起動フックログ: $LOG_FILE"
        local log_lines=$(wc -l < "$LOG_FILE" 2>/dev/null || echo "0")
        echo "📊 ログ行数: $log_lines"
        
        if [ -f "$PROJECT_ROOT/logs/session-inheritance.log" ]; then
            local inheritance_lines=$(wc -l < "$PROJECT_ROOT/logs/session-inheritance.log" 2>/dev/null || echo "0")
            echo "🧠 記憶継承ログ: $inheritance_lines 行"
        fi
        
        if [ -f "$PROJECT_ROOT/logs/claude-code-auto-memory.log" ]; then
            local auto_memory_lines=$(wc -l < "$PROJECT_ROOT/logs/claude-code-auto-memory.log" 2>/dev/null || echo "0")
            echo "⚡ 自動記憶ログ: $auto_memory_lines 行"
        fi
    else
        echo "❌ 起動フックログ: 未作成"
    fi
    
    echo ""
    echo "💡 起動フック実行: $0 startup"
    echo "🔧 設定ファイル作成: $MEMORY_SYSTEM_ROOT/claude-code-auto-memory-loader.sh config"
}

# デバッグモード
debug_mode() {
    log_hook "🐛 デバッグモード実行"
    
    echo "🐛 Claude Code記憶継承システム - デバッグ情報"
    echo ""
    
    # 環境変数表示
    echo "🔧 関連環境変数:"
    env | grep -E "(CLAUDE|OPENAI|MEMORY)" | sort || echo "  関連環境変数なし"
    
    echo ""
    echo "📂 プロジェクト構造確認:"
    ls -la "$MEMORY_SYSTEM_ROOT" 2>/dev/null || echo "  ディレクトリアクセス不可"
    
    echo ""
    echo "🔍 プロセス確認:"
    ps aux | grep -E "(claude|python.*memory|session-inheritance)" | grep -v grep || echo "  関連プロセスなし"
    
    echo ""
    echo "📄 最新ログ (最新10行):"
    if [ -f "$LOG_FILE" ]; then
        tail -10 "$LOG_FILE"
    else
        echo "  ログファイル未作成"
    fi
}

# ヘルプ表示
show_help() {
    cat << EOF
🚀 Claude Code 起動時フック - 自動記憶継承システム

使用方法:
  $0 <コマンド>

コマンド:
  startup     - 起動フック実行（Claude Code起動時自動実行）
  status      - システム状況確認
  debug       - デバッグ情報表示
  help        - このヘルプ

起動フック自動実行設定:
  1. Claude Code起動時にこのスクリプトが自動実行されるよう設定
  2. 記憶継承システムがバックグラウンドで起動
  3. Claude Codeの起動は阻害されません

ファイル:
  設定ファイル: $PROJECT_ROOT/memory/core/memory-env.conf
  ログファイル: $LOG_FILE
  システム本体: $MEMORY_SYSTEM_ROOT/

統合システム:
  - session-inheritance-bridge.sh (記憶継承ブリッジ)
  - claude-code-auto-memory-loader.sh (自動ローダー)
  - claude-code-memory-api.py (API統合)
EOF
}

# メイン処理
main() {
    case "${1:-}" in
        "startup")
            execute_startup_hook
            ;;
        "status")
            check_status
            ;;
        "debug")
            debug_mode
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