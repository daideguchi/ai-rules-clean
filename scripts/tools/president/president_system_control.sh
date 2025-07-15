#!/bin/bash

# =============================================================================
# [LEGACY WRAPPER] president_system_control.sh
# 
# このスクリプトは unified-president-tool.py に統合されました。
# Phase 5 統合完了 - レガシー互換性のためのwrapperスクリプト
# 
# 新しい使用方法:
#   scripts/tools/unified-president-tool.py control <action>
# =============================================================================

echo "⚠️  [LEGACY] president_system_control.sh は統合されました"
echo "📦 unified-president-tool.py control に移行してください"
echo ""
echo "🔄 自動転送中..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 引数変換
action="${1:-help}"
if [[ "$action" == "help" || "$action" == "--help" || "$action" == "-h" ]]; then
    # helpの場合は統合ツールのヘルプを表示
    exec python3 "$SCRIPT_DIR/../unified-president-tool.py" --help
else
    exec python3 "$SCRIPT_DIR/../unified-president-tool.py" control "$action" "$@"
fi
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_ROOT"

# カラー設定
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

show_help() {
    cat << EOF
🎯 PRESIDENT宣言システム制御

使用法: $0 [コマンド]

コマンド:
  status    - システム状態確認
  enable    - 安全版システム有効化
  disable   - システム無効化
  test      - 動作テスト
  debug     - デバッグログ表示
  reset     - セッション状態リセット
  help      - このヘルプ表示

例:
  $0 status   # 現在の状態確認
  $0 test     # 動作テスト実行
  $0 enable   # 安全版有効化
EOF
}

check_status() {
    echo -e "${BLUE}🔍 PRESIDENT宣言システム状態確認${NC}"
    echo
    
    # セッション状態確認
    if [[ -f "runtime/president_session_state.json" ]]; then
        echo -e "${GREEN}✅ セッション状態ファイル存在${NC}"
        echo "内容:"
        cat runtime/president_session_state.json | jq .
        echo
    else
        echo -e "${RED}❌ セッション状態ファイル未存在${NC}"
        echo
    fi
    
    # hooks設定確認
    if [[ -f ".claude/settings.json" ]]; then
        echo -e "${GREEN}✅ hooks設定ファイル存在${NC}"
        echo "内容:"
        cat .claude/settings.json | jq .
        echo
    else
        echo -e "${RED}❌ hooks設定ファイル未存在${NC}"
        echo
    fi
    
    # 安全版スクリプト確認
    if [[ -f "scripts/hooks/president_declaration_gate_safe.py" ]]; then
        echo -e "${GREEN}✅ 安全版スクリプト存在${NC}"
        if [[ -x "scripts/hooks/president_declaration_gate_safe.py" ]]; then
            echo -e "${GREEN}✅ 実行権限あり${NC}"
        else
            echo -e "${YELLOW}⚠️ 実行権限なし${NC}"
        fi
    else
        echo -e "${RED}❌ 安全版スクリプト未存在${NC}"
    fi
}

test_system() {
    echo -e "${BLUE}🧪 PRESIDENT宣言システムテスト${NC}"
    echo
    
    # 安全版スクリプトテスト
    if [[ -f "scripts/hooks/president_declaration_gate_safe.py" ]]; then
        echo "安全版スクリプトテスト:"
        python3 scripts/hooks/president_declaration_gate_safe.py < /dev/null
        echo
    fi
    
    # デバッグログ確認
    if [[ -f "runtime/president_gate_debug.log" ]]; then
        echo "最新デバッグログ（最後の5行）:"
        tail -5 runtime/president_gate_debug.log
        echo
    fi
}

enable_system() {
    echo -e "${YELLOW}🚀 PRESIDENT宣言システム有効化${NC}"
    echo
    
    # 実行権限確認
    chmod +x scripts/hooks/president_declaration_gate_safe.py
    
    # 安全版設定適用
    cp .claude/settings.president_safe.json .claude/settings.json
    
    echo -e "${GREEN}✅ 安全版システム有効化完了${NC}"
    echo -e "${YELLOW}⚠️ 次回Claude Code再起動時から有効${NC}"
}

disable_system() {
    echo -e "${YELLOW}🔒 PRESIDENT宣言システム無効化${NC}"
    echo
    
    # hooks無効化
    echo '{}' > .claude/settings.json
    
    echo -e "${GREEN}✅ システム無効化完了${NC}"
}

reset_session() {
    echo -e "${YELLOW}🔄 セッション状態リセット${NC}"
    echo
    
    # 現在時刻でセッション状態作成
    mkdir -p runtime
    echo "{\"president_declared\": true, \"session_start\": \"$(date -Iseconds)\"}" > runtime/president_session_state.json
    
    echo -e "${GREEN}✅ セッション状態リセット完了${NC}"
    echo "新しいセッション状態:"
    cat runtime/president_session_state.json | jq .
}

show_debug() {
    echo -e "${BLUE}🔍 デバッグログ表示${NC}"
    echo
    
    if [[ -f "runtime/president_gate_debug.log" ]]; then
        echo "全デバッグログ:"
        cat runtime/president_gate_debug.log
    else
        echo -e "${YELLOW}⚠️ デバッグログファイルが存在しません${NC}"
    fi
}

# メイン処理
case "${1:-help}" in
    "status")
        check_status
        ;;
    "enable")
        enable_system
        ;;
    "disable")
        disable_system
        ;;
    "test")
        test_system
        ;;
    "debug")
        show_debug
        ;;
    "reset")
        reset_session
        ;;
    "help"|*)
        show_help
        ;;
esac 