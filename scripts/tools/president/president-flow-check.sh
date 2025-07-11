#!/bin/bash

# =============================================================================
# [LEGACY WRAPPER] president-flow-check.sh
# 
# このスクリプトは unified-president-tool.py に統合されました。
# Phase 5 統合完了 - レガシー互換性のためのwrapperスクリプト
# 
# 新しい使用方法:
#   scripts/tools/unified-president-tool.py status
# =============================================================================

echo "⚠️  [LEGACY] president-flow-check.sh は統合されました"
echo "📦 unified-president-tool.py status に移行してください"
echo ""
echo "🔄 自動転送中..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/../unified-president-tool.py" status "$@"

echo "🚨 プレジデント処理フロー確認中..."
echo ""

# カラー定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ROOT="${PROJECT_ROOT}"

# 1. 重要ファイル存在確認
echo -e "${BLUE}📋 1. プレジデント重要ファイル確認${NC}"
files=(
    "docs/reports/ai-agents/president.md:プレジデント指示書"
    "docs/misc/president-mistakes.md:78回ミス記録"
    "ai-agents/manage.sh:AI組織起動スクリプト"
    "ai-agents/sessions/president-session.json:プレジデントセッション"
)

for file_info in "${files[@]}"; do
    file="${file_info%%:*}"
    desc="${file_info##*:}"
    
    if [ -f "$PROJECT_ROOT/$file" ]; then
        echo -e "   ${GREEN}✅ $desc${NC}"
    else
        echo -e "   ${RED}❌ $desc - $file 見つかりません${NC}"
    fi
done

echo ""

# 2. AI組織システム状態確認
echo -e "${BLUE}🤖 2. AI組織システム状態確認${NC}"

if command -v tmux &> /dev/null; then
    if tmux has-session -t multiagent 2>/dev/null; then
        echo -e "   ${GREEN}✅ multiagent セッション起動中${NC}"
        
        # セッション詳細
        session_info=$(tmux list-sessions | grep multiagent || echo "")
        if [ -n "$session_info" ]; then
            echo -e "   ${BLUE}   詳細: $session_info${NC}"
        fi
        
        # pane数確認
        pane_count=$(tmux list-panes -t multiagent 2>/dev/null | wc -l || echo "0")
        echo -e "   ${BLUE}   アクティブpane数: $pane_count${NC}"
        
    else
        echo -e "   ${YELLOW}⚠️  multiagent セッション未起動${NC}"
        echo -e "   ${YELLOW}   実行: ./ai-agents/manage.sh start${NC}"
    fi
    
    if tmux has-session -t president 2>/dev/null; then
        echo -e "   ${GREEN}✅ president セッション起動中${NC}"
    else
        echo -e "   ${YELLOW}⚠️  president セッション未起動${NC}"
    fi
else
    echo -e "   ${RED}❌ tmux コマンドが見つかりません${NC}"
fi

echo ""

# 3. プレジデントミス記録統計
echo -e "${BLUE}📈 3. プレジデントミス記録分析${NC}"

mistakes_file="$PROJECT_ROOT/docs/misc/president-mistakes.md"
if [ -f "$mistakes_file" ]; then
    mistake_count=$(grep -c "ミス\|mistake\|error" "$mistakes_file" 2>/dev/null || echo "0")
    echo -e "   ${GREEN}📋 記録済みミス: ${mistake_count}個${NC}"
    
    # 最新ミス確認
    latest_mistake=$(tail -10 "$mistakes_file" | grep -E "ミス|mistake" | tail -1 || echo "")
    if [ -n "$latest_mistake" ]; then
        echo -e "   ${BLUE}   最新: ${latest_mistake}${NC}"
    fi
else
    echo -e "   ${RED}❌ ミス記録ファイルが見つかりません${NC}"
fi

echo ""

# 4. Claude Code並列起動状況
echo -e "${BLUE}🔧 4. Claude Code並列起動状況${NC}"

if command -v claude &> /dev/null; then
    claude_processes=$(ps aux | grep -c "claude" || echo "0")
    echo -e "   ${GREEN}📊 Claude プロセス数: $claude_processes${NC}"
else
    echo -e "   ${YELLOW}⚠️  Claude Code コマンドが見つかりません${NC}"
fi

echo ""

# 5. 実行推奨コマンド表示
echo -e "${BLUE}🚀 5. 実行推奨コマンド${NC}"
echo -e "   ${GREEN}AI組織起動:${NC} ./ai-agents/manage.sh start"
echo -e "   ${GREEN}状態確認:${NC} ./ai-agents/manage.sh status"  
echo -e "   ${GREEN}Claude並列起動:${NC} ./ai-agents/manage.sh claude-setup"
echo -e "   ${GREEN}プレジデント確認:${NC} cat docs/reports/ai-agents/president.md"

echo ""

# 6. 重要リマインダー
echo -e "${RED}🚨 重要リマインダー${NC}"
echo -e "   ${YELLOW}• 会話開始前にプレジデント指示書必読${NC}"
echo -e "   ${YELLOW}• 78回のミス記録を必ず継承${NC}"
echo -e "   ${YELLOW}• AI組織システム起動状態を確認${NC}"
echo -e "   ${YELLOW}• 4画面構成: PRESIDENT + BOSS + WORKER1-3${NC}"

echo ""
echo -e "${GREEN}✅ プレジデント処理フロー確認完了${NC}"

# 7. 自動修正提案
if ! tmux has-session -t multiagent 2>/dev/null; then
    echo ""
    echo -e "${YELLOW}💡 自動修正提案: AI組織システムを起動しますか？ (y/n)${NC}"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}🚀 AI組織システム起動中...${NC}"
        cd "$PROJECT_ROOT" && ./ai-agents/manage.sh start
    fi
fi