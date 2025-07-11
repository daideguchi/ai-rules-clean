#!/bin/bash

# =============================================================================
# AI-TEAM: 統合メインスクリプト
# TeamAI プロジェクト ワンストップソリューション
# =============================================================================
#
# 🎯 目的: 全ての機能を1つのスクリプトに統合
# - 初回セットアップ
# - AI組織起動
# - 設定変更
# - トラブルシューティング
#
# 🚀 使用方法:
# ./ai-team.sh           # メインメニューから選択
# ./ai-team.sh setup     # 初回セットアップ
# ./ai-team.sh start     # AI組織起動
# ./ai-team.sh president # PRESIDENT単体起動
# ./ai-team.sh quick     # クイック起動
#
# =============================================================================

set -euo pipefail

# =============================================================================
# カラーコード & ログ関数
# =============================================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "\n${PURPLE}==== $1 ====${NC}"; }

# プログレスバー
show_progress() {
    local current=$1 total=$2 step_name="$3"
    local percent=$((current * 100 / total))
    local completed=$((current * 50 / total))
    local remaining=$((50 - completed))
    
    printf "\r${CYAN}Progress [${GREEN}"
    printf "%${completed}s" | tr ' ' '='
    printf "${NC}${CYAN}"
    printf "%${remaining}s" | tr ' ' '-'
    printf "] ${percent}%% - ${step_name}${NC}"
    
    [ $current -eq $total ] && echo ""
}

# エラーハンドラー
fatal_error() {
    log_error "致命的エラー: $1"
    exit 1
}

# =============================================================================
# メニュー表示
# =============================================================================

show_main_menu() {
    clear
    echo -e "${CYAN}"
    echo "🤖 AI-TEAM: TeamAI プロジェクト統合管理"
    echo "=========================================="
    echo -e "${NC}"
    echo "TeamAI - 5人のAIチームによる協調開発プラットフォーム"
    echo ""
    echo -e "${GREEN}📋 利用可能なオプション:${NC}"
    echo ""
    echo -e "${YELLOW}1)${NC} 🚀 AI組織起動          - AI組織システムを起動"
    echo -e "${YELLOW}2)${NC} 👑 PRESIDENT単体起動    - 簡潔タスク用（個人作業）"
    echo -e "${YELLOW}3)${NC} ⚙️  初回セットアップ      - 環境構築・認証設定"
    echo -e "${YELLOW}4)${NC} ⚡ クイック起動         - 簡易起動（設定済み環境用）"
    echo -e "${YELLOW}5)${NC} 🔧 設定変更           - 認証・設定の変更"
    echo -e "${YELLOW}6)${NC} 🆘 トラブルシューティング  - 問題解決・復旧"
    echo -e "${YELLOW}7)${NC} 📊 ステータス確認       - システム状態確認"
    echo -e "${YELLOW}8)${NC} 📋 要件定義書管理       - TODO・仕様更新"
    echo -e "${YELLOW}9)${NC} 📚 ヘルプ・使用方法      - 詳細ガイド"
    echo -e "${YELLOW}0)${NC} 🚪 終了"
    echo ""
}

# =============================================================================
# 各機能の実装
# =============================================================================

# 初回セットアップ機能
run_setup() {
    log_step "初回セットアップ開始"
    
    echo -e "${CYAN}🤖 AI開発支援ツール セットアップ${NC}"
    echo "=================================="
    echo ""
    echo -e "${GREEN}📋 3つの設定パターン:${NC}"
    echo ""
    echo -e "${YELLOW}1) 🟢 基本設定${NC}          - Cursor Rules のみ"
    echo -e "${YELLOW}2) 🟡 開発環境設定${NC}       - Cursor + Claude Code 連携"
    echo -e "${YELLOW}3) 🔴 完全設定${NC}          - AI組織システム + 全機能"
    echo ""
    
    while true; do
        read -p "選択してください [1-3]: " choice
        case $choice in
            1) setup_basic; break;;
            2) setup_development; break;;
            3) setup_complete; break;;
            *) echo "無効な選択です。1-3を入力してください。";;
        esac
    done
}

# 基本設定
setup_basic() {
    log_info "基本設定を開始します..."
    # Cursor Rules設定
    cp -r cursor-rules/.cursor/ ./ 2>/dev/null || true
    log_success "Cursor Rules設定完了"
    echo "✅ Cursorを再起動してAI支援を開始してください"
}

# 開発環境設定
setup_development() {
    log_info "開発環境設定を開始します..."
    setup_basic
    # Claude Code設定
    log_info "Claude Code連携を設定中..."
    log_success "開発環境設定完了"
    echo "✅ Claude Codeでプロジェクトを開いてください"
}

# 完全設定
setup_complete() {
    log_info "完全設定を開始します..."
    setup_development
    
    # AI組織システム設定
    log_info "AI組織システムを設定中..."
    
    # 認証設定確認
    echo ""
    echo -e "${YELLOW}🔐 認証方法を選択してください:${NC}"
    echo "1) claude.ai Pro (推奨)"
    echo "2) ANTHROPIC_API_KEY"
    
    read -p "選択 [1-2]: " auth_choice
    case $auth_choice in
        1) 
            log_info "claude.ai Pro認証を設定"
            export CLAUDE_AUTH_METHOD="web"
            ;;
        2) 
            read -p "ANTHROPIC_API_KEY を入力: " api_key
            export ANTHROPIC_API_KEY="$api_key"
            export CLAUDE_AUTH_METHOD="api"
            ;;
    esac
    
    # 設定完了マーク
    touch ./.ai-org-configured
    log_success "完全設定完了"
    echo ""
    echo "🎉 AI組織システムが利用可能になりました！"
    echo "💡 次は './ai-team.sh start' でAI組織を起動してください"
}

# AI組織起動機能（統合版）
start_ai_org() {
    log_step "AI組織起動開始"
    
    # 設定確認
    if [[ ! -f "./.ai-org-configured" ]]; then
        log_warning "初回セットアップが必要です"
        echo "先に './ai-team.sh setup' を実行してください"
        return 1
    fi
    
    echo -e "${CYAN}🚀 AI組織統合起動システム${NC}"
    echo "============================="
    echo "複雑な5ステップ → シンプル1コマンド"
    echo ""
    
    read -p "AI組織を起動しますか？ [Y/n]: " -n 1 -r
    echo
    [[ ! $REPLY =~ ^[Yy]$ ]] && [[ ! -z $REPLY ]] && return 0
    
    # 段階的実行
    check_dependencies
    cleanup_existing_sessions
    auto_authentication
    start_president_session
    setup_multiagent_layout
    auto_message_distribution
    verify_agents_startup
    final_setup
}

# クイック起動
quick_start() {
    log_step "クイック起動"
    
    if [[ ! -f "./.ai-org-configured" ]]; then
        log_error "初回セットアップが必要です"
        echo "先に './ai-team.sh setup' を実行してください"
        return 1
    fi
    
    log_info "AI組織をクイック起動中..."
    start_ai_org
}

# 設定変更
change_settings() {
    log_step "設定変更"
    
    echo "🔧 設定変更メニュー"
    echo "=================="
    echo "1) 認証方法変更"
    echo "2) AI組織設定リセット"
    echo "3) Cursor Rules更新"
    echo "0) 戻る"
    echo ""
    
    read -p "選択 [0-3]: " choice
    case $choice in
        1) change_auth;;
        2) reset_ai_org;;
        3) update_cursor_rules;;
        0) return;;
        *) echo "無効な選択です";;
    esac
}

# 認証方法変更
change_auth() {
    log_info "認証方法を変更します..."
    rm -f ./.ai-org-configured
    setup_complete
}

# AI組織設定リセット
reset_ai_org() {
    log_warning "AI組織設定をリセットします..."
    read -p "続行しますか？ [y/N]: " -n 1 -r
    echo
    [[ $REPLY =~ ^[Yy]$ ]] || return 0
    
    # tmuxセッション終了
    tmux kill-session -t president 2>/dev/null || true
    tmux kill-session -t multiagent 2>/dev/null || true
    
    # 設定ファイル削除
    rm -f ./.ai-org-configured
    
    log_success "リセット完了"
}

# Cursor Rules更新
update_cursor_rules() {
    log_info "Cursor Rules を更新中..."
    cp -r cursor-rules/.cursor/ ./ 2>/dev/null || true
    log_success "Cursor Rules更新完了"
}

# トラブルシューティング
troubleshooting() {
    log_step "トラブルシューティング"
    
    echo "🆘 トラブルシューティング"
    echo "======================"
    echo "1) AI組織強制停止・再起動"
    echo "2) 権限エラー修復"
    echo "3) ログ確認"
    echo "4) 緊急Enter送信"
    echo "0) 戻る"
    echo ""
    
    read -p "選択 [0-4]: " choice
    case $choice in
        1) force_restart;;
        2) fix_permissions;;
        3) check_logs;;
        4) emergency_enter;;
        0) return;;
        *) echo "無効な選択です";;
    esac
}

# 強制再起動
force_restart() {
    log_warning "AI組織を強制停止・再起動します..."
    tmux kill-session -t president 2>/dev/null || true
    tmux kill-session -t multiagent 2>/dev/null || true
    sleep 2
    start_ai_org
}

# 権限修復
fix_permissions() {
    log_info "権限エラーを修復中..."
    chmod +x *.sh 2>/dev/null || true
    chmod +x ai-agents/*.sh 2>/dev/null || true
    chmod +x scripts/*/*.sh 2>/dev/null || true
    log_success "権限修復完了"
}

# ログ確認
check_logs() {
    log_info "最新ログを表示します..."
    echo ""
    if [[ -f "./logs/ai-agents/system.log" ]]; then
        tail -20 ./logs/ai-agents/system.log
    else
        echo "ログファイルが見つかりません"
    fi
}

# 緊急Enter送信
emergency_enter() {
    log_info "緊急Enter送信を実行中..."
    tmux send-keys -t president C-m 2>/dev/null || true
    for i in {0..3}; do
        tmux send-keys -t "multiagent:0.$i" C-m 2>/dev/null || true
    done
    log_success "Enter送信完了"
}

# ステータス確認
check_status() {
    log_step "システムステータス確認"
    
    echo "📊 TeamAI システム状態"
    echo "===================="
    echo ""
    
    # 設定状態
    if [[ -f "./.ai-org-configured" ]]; then
        echo "✅ AI組織設定: 完了"
    else
        echo "❌ AI組織設定: 未完了"
    fi
    
    # tmuxセッション
    if tmux has-session -t president 2>/dev/null; then
        echo "✅ PRESIDENTセッション: アクティブ"
    else
        echo "❌ PRESIDENTセッション: 非アクティブ"
    fi
    
    if tmux has-session -t multiagent 2>/dev/null; then
        echo "✅ マルチエージェントセッション: アクティブ"
    else
        echo "❌ マルチエージェントセッション: 非アクティブ"
    fi
    
    # プロセス確認
    local claude_count=$(ps aux | grep claude | grep -v grep | wc -l)
    echo "📊 Claudeプロセス数: $claude_count"
    
    echo ""
    echo "💡 詳細は ./logs/ai-agents/ でログを確認してください"
}

# 要件定義書管理
manage_requirements() {
    log_step "要件定義書管理"
    
    if [[ -f "./scripts/update-requirements.sh" ]]; then
        ./scripts/update-requirements.sh
    else
        echo "📋 要件定義書管理"
        echo "=================="
        echo ""
        echo "📊 docs/REQUIREMENTS_SPECIFICATION.md - 包括的仕様書"
        echo "📊 docs/PROJECT-STATUS.md - 現在の状況"
        echo ""
        echo "💡 更新方法:"
        echo "1. ファイルを直接編集"
        echo "2. git で変更履歴管理"
        echo "3. 定期的なバックアップ"
        echo ""
        read -p "Enterキーで戻る..."
    fi
}

# PRESIDENT単体起動
start_president_solo() {
    log_step "PRESIDENT単体起動"
    
    echo -e "${CYAN}👑 PRESIDENT Solo Mode${NC}"
    echo "========================"
    echo ""
    echo -e "${GREEN}個人作業・簡潔タスク用のPRESIDENT単体起動です${NC}"
    echo ""
    echo -e "${YELLOW}特徴:${NC}"
    echo "• 1対1の直接対話"
    echo "• 完全記録業務"
    echo "• 高品質成果物"
    echo "• 既存記録システム統合"
    echo ""
    
    read -p "PRESIDENT単体モードを起動しますか？ [Y/n]: " -n 1 -r
    echo
    [[ ! $REPLY =~ ^[Yy]$ ]] && [[ ! -z $REPLY ]] && return 0
    
    # スクリプトパス確認
    local start_president_script="./ai-agents/scripts/start-president.sh"
    
    if [[ ! -f "$start_president_script" ]]; then
        log_error "start-president.shが見つかりません: $start_president_script"
        return 1
    fi
    
    if [[ ! -x "$start_president_script" ]]; then
        log_error "start-president.shに実行権限がありません"
        return 1
    fi
    
    # PRESIDENT単体起動スクリプト実行
    log_info "PRESIDENT単体起動スクリプトを実行中..."
    "$start_president_script"
    
    local exit_code=$?
    if [[ $exit_code -eq 0 ]]; then
        log_success "PRESIDENT単体起動完了"
        echo ""
        echo -e "${GREEN}🎉 接続方法:${NC}"
        echo -e "  ${YELLOW}tmux attach-session -t president${NC}"
        echo ""
        echo -e "${BLUE}💡 ヒント:${NC}"
        echo "• すべての作業は自動的に記録されます"
        echo "• 完了時は必ず作業記録を更新してください"
        echo "• 複雑なタスクは AI組織起動 を検討してください"
    else
        log_error "PRESIDENT単体起動に失敗しました (終了コード: $exit_code)"
    fi
}

# ヘルプ
show_help() {
    clear
    echo -e "${CYAN}📚 AI-TEAM ヘルプ & 使用方法${NC}"
    echo "================================"
    echo ""
    echo -e "${GREEN}🎯 基本的な使用の流れ:${NC}"
    echo ""
    echo "1️⃣ 初回セットアップ"
    echo "   ./ai-team.sh setup"
    echo "   または"
    echo "   ./ai-team.sh → 2を選択"
    echo ""
    echo "2️⃣ AI組織起動"
    echo "   ./ai-team.sh start"
    echo "   または"
    echo "   ./ai-team.sh → 1を選択"
    echo ""
    echo "3️⃣ 開発開始"
    echo "   AI組織が起動したら開発タスクを依頼"
    echo ""
    echo -e "${GREEN}⚡ コマンドライン引数:${NC}"
    echo ""
    echo "./ai-team.sh           # メインメニュー"
    echo "./ai-team.sh setup     # セットアップ"
    echo "./ai-team.sh start     # AI組織起動"
    echo "./ai-team.sh quick     # クイック起動"
    echo "./ai-team.sh status    # ステータス確認"
    echo "./ai-team.sh help      # このヘルプ"
    echo ""
    echo -e "${GREEN}🔧 トラブル時:${NC}"
    echo ""
    echo "./ai-team.sh → 5 (トラブルシューティング)"
    echo ""
    echo -e "${GREEN}📁 重要なファイル・ディレクトリ:${NC}"
    echo ""
    echo "PROJECT-STATUS.md      # プロジェクト現状"
    echo "logs/ai-agents/        # AI組織ログ"
    echo "ai-agents/             # AI組織システム"
    echo ""
    
    read -p "Enterキーで戻る..."
}

# =============================================================================
# AI組織起動の内部関数（既存機能を統合）
# =============================================================================

check_dependencies() {
    show_progress 1 8 "依存関係確認"
    
    for cmd in tmux claude; do
        command -v "$cmd" &> /dev/null || fatal_error "必須コマンド '$cmd' が見つかりません"
    done
    
    [[ ! -d "./ai-agents" ]] && fatal_error "ai-agentsディレクトリが見つかりません"
    [[ ! -f "./ai-agents/instructions/president.md" ]] && fatal_error "president.md指示書が見つかりません"
    
    log_success "依存関係確認完了"
}

cleanup_existing_sessions() {
    show_progress 2 8 "セッション整理"
    
    for session in president multiagent; do
        if tmux has-session -t $session 2>/dev/null; then
            log_info "既存の${session}セッションを終了中..."
            tmux kill-session -t $session
        fi
    done
    
    log_success "セッション整理完了"
}

auto_authentication() {
    show_progress 3 8 "認証処理"
    
    if [[ -n "${ANTHROPIC_API_KEY:-}" ]]; then
        log_info "API Key認証を使用"
        export CLAUDE_AUTH_METHOD="api"
    else
        log_info "Claude.ai認証を使用"
        export CLAUDE_AUTH_METHOD="web"
    fi
    
    log_success "認証設定完了"
}

start_president_session() {
    show_progress 4 8 "PRESIDENT起動"
    
    tmux new-session -d -s president -c "$(pwd)"
    tmux send-keys -t president "claude --dangerously-skip-permissions" C-m
    
    local timeout=60 elapsed=0
    while [ $elapsed -lt $timeout ]; do
        if tmux capture-pane -t president -p | grep -E "(Welcome to Claude Code|cwd:|Bypassing Permissions)" >/dev/null 2>&1; then
            log_success "PRESIDENT起動確認完了"
            break
        fi
        sleep 1
        elapsed=$((elapsed + 1))
    done
    
    [ $elapsed -ge $timeout ] && fatal_error "PRESIDENT起動がタイムアウトしました"
    
    sleep 2
    tmux send-keys -t president C-m
    sleep 1
}

setup_multiagent_layout() {
    show_progress 5 8 "マルチエージェント構築"
    
    tmux new-session -d -s multiagent -c "$(pwd)"
    tmux split-window -h -t multiagent
    tmux split-window -v -t multiagent:0.0
    tmux split-window -v -t multiagent:0.1
    tmux select-layout -t multiagent tiled
    
    local titles=("👔 BOSS1" "💻 WORKER1" "🔧 WORKER2" "🎨 WORKER3")
    for i in {0..3}; do
        tmux select-pane -t multiagent:0.$i -T "${titles[$i]}"
        tmux send-keys -t "multiagent:0.$i" "claude --dangerously-skip-permissions" C-m
        sleep 2
        tmux send-keys -t "multiagent:0.$i" C-m
        sleep 1
    done
    
    log_success "マルチエージェント構築完了"
}

auto_message_distribution() {
    show_progress 6 8 "メッセージ配信"
    
    local timeout=120 elapsed=0
    while [ $elapsed -lt $timeout ]; do
        if tmux capture-pane -t president -p | grep -q "How can I help you"; then
            break
        fi
        sleep 1
        elapsed=$((elapsed + 1))
    done
    
    local president_message=">あなたはプレジデントです。./ai-agents/instructions/president.mdの指示書を参照して実行してください。
【重要】ワーカーに指示を送る時は必ず文頭に「>」を付けてください。
まず最初に、以下のコマンドでワーカーたちを起動し、その後BOSS1、WORKER1、WORKER2、WORKER3の4人全員に対して、
それぞれの指示書（boss.md、worker.md）を確認するよう指示を出してください。"
    
    tmux send-keys -t president "$president_message" C-m
    sleep 2
    tmux send-keys -t president C-m
    
    log_success "メッセージ配信完了"
}

verify_agents_startup() {
    show_progress 7 8 "起動確認"
    
    local agents=("president" "multiagent:0.0" "multiagent:0.1" "multiagent:0.2" "multiagent:0.3")
    local names=("PRESIDENT" "BOSS1" "WORKER1" "WORKER2" "WORKER3")
    
    for i in "${!agents[@]}"; do
        local pane="${agents[$i]}" name="${names[$i]}"
        log_info "Checking ${name}..."
        
        local timeout=30 elapsed=0
        while [ $elapsed -lt $timeout ]; do
            if tmux capture-pane -t "$pane" -p | grep -E "(How can I help|>|Welcome)" > /dev/null; then
                log_success "${name} 起動確認完了"
                break
            fi
            sleep 1
            elapsed=$((elapsed + 1))
        done
        
        [ $elapsed -ge $timeout ] && log_warning "${name} 起動確認がタイムアウト（継続）"
    done
}

final_setup() {
    show_progress 8 8 "セットアップ完了"
    
    tmux set-option -t multiagent status on
    tmux set-option -t multiagent pane-border-status top
    tmux set-option -t multiagent pane-border-format "#{pane_title}"
    
    log_success "AI組織完全起動完了！"
    echo ""
    echo "🎉 AI組織システムが正常に起動しました"
    echo "💻 PRESIDENTセッション: tmux attach-session -t president"
    echo "👥 マルチエージェント: tmux attach-session -t multiagent"
}

# =============================================================================
# メイン実行部分
# =============================================================================

main() {
    # コマンドライン引数処理
    case "${1:-}" in
        "setup"|"s")
            run_setup
            ;;
        "start"|"run"|"r")
            start_ai_org
            ;;
        "president"|"p"|"solo")
            start_president_solo
            ;;
        "quick"|"q")
            quick_start
            ;;
        "status"|"stat")
            check_status
            ;;
        "help"|"h"|"--help")
            show_help
            ;;
        "")
            # メインメニューループ
            while true; do
                show_main_menu
                read -p "選択してください [0-9]: " choice
                echo ""
                
                case $choice in
                    1) start_ai_org;;
                    2) start_president_solo;;
                    3) run_setup;;
                    4) quick_start;;
                    5) change_settings;;
                    6) troubleshooting;;
                    7) check_status;;
                    8) manage_requirements;;
                    9) show_help;;
                    0) 
                        echo "👋 AI-TEAM を終了します"
                        exit 0
                        ;;
                    *)
                        echo "❌ 無効な選択です。0-9を入力してください。"
                        read -p "Enterキーで続行..."
                        ;;
                esac
                
                echo ""
                read -p "Enterキーでメインメニューに戻る..."
            done
            ;;
        *)
            echo "❌ 無効な引数: $1"
            echo "💡 使用方法: ./ai-team.sh [setup|start|president|quick|status|help]"
            exit 1
            ;;
    esac
}

# エラーハンドリング設定
trap 'fatal_error "予期しないエラーが発生しました"' ERR

# スクリプト実行
main "$@"