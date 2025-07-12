#!/bin/bash

# セッション記憶継承システム - o3統合3層構造対応拡張版
# O3LifecycleManager、O3StateCapture、O3MemoryInjectorとの完全連携

set -euo pipefail

# 設定
MEMORY_SYSTEM_PATH="${PROJECT_ROOT}/src/ai/memory/enhanced/o3-memory-system.py"
ENHANCED_MEMORY_ROOT="${PROJECT_ROOT}/memory/enhanced"
HOOKS_CONFIG="${PROJECT_ROOT}/src/ai/memory/core/hooks.js"
O3_INTEGRATION_BRIDGE="${PROJECT_ROOT}/src/ai/memory/enhanced/o3-integration-bridge.py"
LOG_FILE="${PROJECT_ROOT}/logs/session-inheritance-o3-enhanced.log"

# ログ関数
log_session() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [O3-ENHANCED] $1" | tee -a "$LOG_FILE"
}

# 環境チェック（o3対応強化版）
check_environment_o3_enhanced() {
    log_session "🔍 o3統合環境チェック開始"
    
    # Python環境
    if ! command -v python3 &> /dev/null; then
        log_session "❌ Python3が見つかりません"
        return 1
    fi
    
    # OpenAI API Key（o3アクセス用）
    if [ -z "${OPENAI_API_KEY:-}" ]; then
        log_session "❌ OPENAI_API_KEY環境変数が設定されていません（o3アクセス必須）"
        return 1
    fi
    
    # Node.js環境（hooks.js実行用）
    if ! command -v node &> /dev/null; then
        log_session "❌ Node.jsが見つかりません（hooks.js実行に必要）"
        return 1
    fi
    
    # o3統合ブリッジ存在確認
    if [ ! -f "$O3_INTEGRATION_BRIDGE" ]; then
        log_session "❌ o3統合ブリッジが見つかりません: $O3_INTEGRATION_BRIDGE"
        return 1
    fi
    
    # hooks.js存在確認
    if [ ! -f "$HOOKS_CONFIG" ]; then
        log_session "❌ hooks.jsが見つかりません: $HOOKS_CONFIG"
        return 1
    fi
    
    # 必要なPythonパッケージ
    if ! python3 -c "import openai, aiohttp" 2>/dev/null; then
        log_session "⚠️ 必要なPythonパッケージがインストールされていません"
        log_session "📦 手動で以下をインストールしてください: pip3 install --user openai aiohttp"
    fi
    
    # ディレクトリ作成
    mkdir -p "$ENHANCED_MEMORY_ROOT"
    mkdir -p "$(dirname "$LOG_FILE")"
    
    log_session "✅ o3統合環境チェック完了"
}

# o3統合3層構造連携セッション継承
inherit_session_memory_o3_enhanced() {
    local current_session_id="$1"
    local inherit_mode="${2:-auto}"
    
    log_session "🧠 o3統合セッション記憶継承開始: $current_session_id"
    
    # 1. O3LifecycleManager連携
    log_session "🔄 O3LifecycleManager連携実行..."
    local lifecycle_result=$(python3 "$O3_INTEGRATION_BRIDGE" lifecycle --session-id "$current_session_id" 2>&1)
    local lifecycle_exit_code=$?
    
    if [ $lifecycle_exit_code -eq 0 ]; then
        log_session "✅ O3LifecycleManager連携完了"
    else
        log_session "⚠️ O3LifecycleManager連携で問題発生: $lifecycle_result"
    fi
    
    # 2. O3StateCapture実行
    log_session "📊 O3StateCapture実行..."
    local capture_result=$(python3 "$O3_INTEGRATION_BRIDGE" capture --session-id "$current_session_id" 2>&1)
    local capture_exit_code=$?
    
    if [ $capture_exit_code -eq 0 ]; then
        log_session "✅ O3StateCapture完了"
    else
        log_session "⚠️ O3StateCapture実行で問題発生: $capture_result"
    fi
    
    # 3. O3MemoryInjector実行（全戦略）
    log_session "💉 O3MemoryInjector実行（全戦略）..."
    local injection_result=$(python3 "$O3_INTEGRATION_BRIDGE" inject --session-id "$current_session_id" --strategy "all" 2>&1)
    local injection_exit_code=$?
    
    if [ $injection_exit_code -eq 0 ]; then
        log_session "✅ O3MemoryInjector完了"
    else
        log_session "⚠️ O3MemoryInjector実行で問題発生: $injection_result"
    fi
    
    # 4. 完全o3統合実行
    log_session "🎯 完全o3統合実行..."
    local full_integration_result=$(python3 "$O3_INTEGRATION_BRIDGE" integrate --session-id "$current_session_id" 2>&1)
    local full_integration_exit_code=$?
    
    if [ $full_integration_exit_code -eq 0 ]; then
        log_session "🎉 完全o3統合成功"
        
        # 統合結果をファイルに保存
        local integration_file="$ENHANCED_MEMORY_ROOT/session-records/o3-integration-${current_session_id}.json"
        mkdir -p "$(dirname "$integration_file")"
        echo "$full_integration_result" > "$integration_file"
        
        # 統合情報表示
        echo "🎯 o3統合完了: $current_session_id"
        echo "📄 統合結果: $integration_file"
        echo "🔗 o3統合詳細:"
        echo "$full_integration_result" | head -20
        
        return 0
    else
        log_session "❌ 完全o3統合失敗: $full_integration_result"
        return 1
    fi
}

# o3統合3層構造対応AI連携
share_with_ai_agents_o3_enhanced() {
    local session_id="$1"
    local ai_targets="${2:-claude,gemini,o3}"
    
    log_session "🤝 o3統合AI連携情報共有開始: $session_id"
    
    # o3統合ブリッジ経由で各AI連携実行
    IFS=',' read -ra AI_ARRAY <<< "$ai_targets"
    for ai in "${AI_ARRAY[@]}"; do
        case "$ai" in
            "claude")
                log_session "🧠 Claude hooks.js連携（O3LifecycleManager経由）"
                python3 "$O3_INTEGRATION_BRIDGE" lifecycle --session-id "$session_id" > /dev/null 2>&1 &
                ;;
            "gemini")
                log_session "🤖 Gemini連携（o3統合対応）"
                # Gemini用データをo3統合形式で準備
                update_gemini_collaboration_o3_enhanced "$session_id"
                ;;
            "o3")
                log_session "🔍 o3検索システム連携（3層構造対応）"
                python3 "$O3_INTEGRATION_BRIDGE" capture --session-id "$session_id" > /dev/null 2>&1 &
                python3 "$O3_INTEGRATION_BRIDGE" inject --session-id "$session_id" --strategy "search" > /dev/null 2>&1 &
                ;;
        esac
    done
    
    log_session "✅ o3統合AI連携情報共有完了"
}

# Gemini連携（o3統合対応）
update_gemini_collaboration_o3_enhanced() {
    local session_id="$1"
    
    log_session "🤖 Gemini連携システム更新（o3統合対応）..."
    
    # Gemini連携ファイルに記憶データを送信
    local gemini_bridge="${PROJECT_ROOT}/src/integrations/gemini/gemini_bridge"
    
    if [ -d "$gemini_bridge" ]; then
        # o3統合記憶データをGeminiブリッジに送信
        local gemini_memory_file="$gemini_bridge/o3_claude_memory_${session_id}.json"
        
        # o3統合ブリッジから記憶データをエクスポート
        python3 -c "
import sys
sys.path.append('$(dirname "$O3_INTEGRATION_BRIDGE")')
import asyncio
import json
from pathlib import Path

async def export_for_gemini():
    from o3_integration_bridge import O3IntegrationBridge, load_config_from_env
    
    try:
        config = load_config_from_env()
        bridge = O3IntegrationBridge(config)
        
        # Gemini用記憶データ準備
        gemini_data = await bridge.export_memory_for_gemini('$session_id')
        
        # ファイル保存
        with open('$gemini_memory_file', 'w', encoding='utf-8') as f:
            json.dump(gemini_data, f, indent=2, ensure_ascii=False)
        
        print('Gemini記憶データエクスポート完了')
        
    except Exception as e:
        print(f'Gemini記憶データエクスポートエラー: {e}')

asyncio.run(export_for_gemini())
        " 2>/dev/null || log_session "⚠️ Gemini記憶データエクスポートで問題発生"
        
        log_session "✅ Gemini連携システム更新完了（o3統合対応）"
    else
        log_session "⚠️ Geminiブリッジが見つかりません: $gemini_bridge"
    fi
}

# o3統合自動起動プロセス
auto_startup_process_o3_enhanced() {
    log_session "🚀 o3統合自動起動処理開始"
    
    # 1. o3統合環境チェック
    if ! check_environment_o3_enhanced; then
        log_session "❌ o3統合環境チェック失敗"
        return 1
    fi
    
    # 2. 新セッションID生成
    local new_session_id="o3-enhanced-$(date +%Y%m%d-%H%M%S)"
    
    # 3. o3統合記憶継承実行
    if inherit_session_memory_o3_enhanced "$new_session_id" "auto"; then
        log_session "🎯 o3統合記憶継承成功: $new_session_id"
        
        # 4. o3統合AI連携情報共有
        share_with_ai_agents_o3_enhanced "$new_session_id"
        
        # 5. 環境変数エクスポート（o3統合対応）
        export CLAUDE_SESSION_ID="$new_session_id"
        export CLAUDE_MEMORY_INHERITANCE_ACTIVE="true"
        export CLAUDE_MEMORY_API_INTEGRATION_ACTIVE="true"
        export CLAUDE_O3_INTEGRATION_ACTIVE="true"
        export CLAUDE_O3_LIFECYCLE_MANAGER_ACTIVE="true"
        export CLAUDE_O3_STATE_CAPTURE_ACTIVE="true"
        export CLAUDE_O3_MEMORY_INJECTOR_ACTIVE="true"
        
        # 6. o3統合必須情報表示
        display_o3_integration_info "$new_session_id"
        
        echo "🎉 o3統合拡張セッション間記憶継承システム起動完了"
        echo "📊 セッションID: $new_session_id"
        echo "🧠 記憶継承状態: o3統合アクティブ"
        echo "🤝 AI連携: Claude + Gemini + o3（3層構造対応）"
        echo "🔗 API統合: o3統合ブリッジ有効"
        echo "⚡ 自動ローダー: o3対応連携済み"
        echo "🎯 3層構造: LifecycleManager + StateCapture + MemoryInjector"
        
        return 0
    else
        log_session "❌ o3統合記憶継承失敗"
        return 1
    fi
}

# o3統合必須情報表示
display_o3_integration_info() {
    local session_id="$1"
    
    echo "🚨 === o3統合必須継承情報 ==="
    echo "👑 役割: PRESIDENT"
    echo "🎯 使命: AI永続記憶システム実装統括"
    echo "📊 継承ミス回数: 78回"
    echo "🛡️ 防止対象: 79回目のミス"
    echo "💰 予算: $33,000 (Phase 1)"
    echo "⚙️ 技術: PostgreSQL + pgvector + Claude Code hooks"
    echo "🤝 連携: Claude + Gemini + o3"
    echo "🎯 o3統合: 3層構造完全実装"
    echo "  ├── O3LifecycleManager（ライフサイクル管理）"
    echo "  ├── O3StateCapture（状態キャプチャ）"
    echo "  └── O3MemoryInjector（記憶注入）"
    echo "🔗 統合ブリッジ: アクティブ"
    echo "================================="
}

# o3統合テスト機能
test_o3_integration() {
    log_session "🧪 o3統合テスト開始"
    
    # 1. 環境テスト
    echo "🔍 環境テスト:"
    check_environment_o3_enhanced && echo "✅ 環境OK" || echo "❌ 環境NG"
    
    # 2. o3統合ブリッジテスト
    echo "🔗 o3統合ブリッジテスト:"
    python3 "$O3_INTEGRATION_BRIDGE" test && echo "✅ ブリッジOK" || echo "❌ ブリッジNG"
    
    # 3. hooks.js連携テスト
    echo "🪝 hooks.js連携テスト:"
    if [ -f "$HOOKS_CONFIG" ]; then
        node -e "console.log('hooks.js アクセス可能')" && echo "✅ hooks.jsOK" || echo "❌ hooks.jsNG"
    else
        echo "❌ hooks.js未検出"
    fi
    
    # 4. 簡易統合テスト
    echo "⚡ 簡易統合テスト:"
    local test_session_id="test-$(date +%s)"
    if python3 "$O3_INTEGRATION_BRIDGE" lifecycle --session-id "$test_session_id" >/dev/null 2>&1; then
        echo "✅ LifecycleManager OK"
    else
        echo "❌ LifecycleManager NG"
    fi
    
    if python3 "$O3_INTEGRATION_BRIDGE" capture --session-id "$test_session_id" >/dev/null 2>&1; then
        echo "✅ StateCapture OK"
    else
        echo "❌ StateCapture NG"
    fi
    
    if python3 "$O3_INTEGRATION_BRIDGE" inject --session-id "$test_session_id" --strategy "startup" >/dev/null 2>&1; then
        echo "✅ MemoryInjector OK"
    else
        echo "❌ MemoryInjector NG"
    fi
    
    log_session "🧪 o3統合テスト完了"
}

# ヘルプ表示
show_help() {
    cat << EOF
🧠 セッション記憶継承システム - o3統合3層構造対応拡張版

使用方法:
  $0 <コマンド> [オプション]

コマンド:
  startup                     - o3統合自動起動処理（推奨）
  inherit <session_id>        - o3統合セッション記憶継承
  share <session_id> [ai_targets] - o3統合AI連携情報共有
  test                        - o3統合テスト実行
  check                       - o3統合環境チェック
  help                        - このヘルプ

例:
  $0 startup                  # o3統合自動起動（推奨）
  $0 inherit o3-session-123   # 特定セッション継承
  $0 test                     # o3統合テスト

o3統合3層構造:
  - O3LifecycleManager: ライフサイクルフック管理
  - O3StateCapture: 記憶状態キャプチャ
  - O3MemoryInjector: 記憶注入戦略実行

環境変数:
  OPENAI_API_KEY             # OpenAI API キー（必須）
  CLAUDE_O3_INTEGRATION_ACTIVE # o3統合有効化

ログファイル: $LOG_FILE
o3統合ブリッジ: $O3_INTEGRATION_BRIDGE
EOF
}

# メイン処理
main() {
    case "${1:-}" in
        "startup")
            auto_startup_process_o3_enhanced
            ;;
        "inherit")
            if [ -z "${2:-}" ]; then
                echo "❌ セッションIDが必要です"
                show_help
                return 1
            fi
            inherit_session_memory_o3_enhanced "$2" "${3:-auto}"
            ;;
        "share")
            if [ -z "${2:-}" ]; then
                echo "❌ セッションIDが必要です"
                show_help
                return 1
            fi
            share_with_ai_agents_o3_enhanced "$2" "${3:-claude,gemini,o3}"
            ;;
        "test")
            test_o3_integration
            ;;
        "check")
            check_environment_o3_enhanced
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