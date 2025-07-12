#!/bin/bash
set -euo pipefail

# Purpose: 統合ユーティリティ - 複数小機能を1つのコマンドに集約
# Usage: ./utils.sh <command> [options]
# Author: PRESIDENT AI組織
# Last Modified: 2025-07-08

VERSION="1.0.0"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

show_help() {
    cat << EOF
🔧 Utils.sh - 統合ユーティリティシステム v${VERSION}

USAGE:
    ./utils.sh <command> [options]

COMMANDS:
    api-check           AI API疎通確認
    env-load            環境変数読み込み
    basic-check         基本システムチェック
    danger-detect       危険パターン検出
    mistake-search      ミスパターン検索
    help                このヘルプを表示
    version             バージョン情報

EXAMPLES:
    ./utils.sh api-check
    ./utils.sh env-load .env
    ./utils.sh danger-detect --scan-all
    ./utils.sh mistake-search "ファイル作成"

EOF
}

# AI API疎通確認 (ai-api-check.sh 統合)
cmd_api_check() {
    echo "🔍 AI API疎通確認開始..."
    
    # Gemini API確認
    if command -v gemini >/dev/null; then
        echo "✅ Gemini CLI利用可能"
        if gemini -p "test" >/dev/null 2>&1; then
            echo "✅ Gemini API疎通OK"
        else
            echo "❌ Gemini API疎通NG"
        fi
    else
        echo "❌ Gemini CLI未インストール"
    fi
    
    # Claude Code確認
    if command -v claude >/dev/null; then
        echo "✅ Claude Code利用可能"
    else
        echo "❌ Claude Code未インストール"
    fi
    
    echo "🔍 AI API疎通確認完了"
}

# 環境変数読み込み (load-env.sh 統合)
cmd_env_load() {
    local env_file="${1:-.env}"
    
    if [[ ! -f "$env_file" ]]; then
        echo "❌ 環境ファイル未存在: $env_file"
        return 1
    fi
    
    echo "🔧 環境変数読み込み中: $env_file"
    
    # .envファイルを読み込み、exportする
    while IFS= read -r line || [[ -n "$line" ]]; do
        # コメント行と空行をスキップ
        [[ "$line" =~ ^[[:space:]]*# ]] && continue
        [[ -z "${line// }" ]] && continue
        
        # KEY=VALUE形式の行を処理
        if [[ "$line" =~ ^[[:space:]]*([^=]+)=(.*)$ ]]; then
            key="${BASH_REMATCH[1]}"
            value="${BASH_REMATCH[2]}"
            
            # 前後の空白を削除
            key="${key// /}"
            
            # クォートを削除
            value="${value#\"}"
            value="${value%\"}"
            value="${value#\'}"
            value="${value%\'}"
            
            export "$key=$value"
            echo "  ✅ $key"
        fi
    done < "$env_file"
    
    echo "✅ 環境変数読み込み完了"
}

# 基本システムチェック (basic_check_commands.sh 統合)
cmd_basic_check() {
    echo "🔍 基本システムチェック開始..."
    
    # 必須コマンド確認
    local required_commands=("git" "python3" "node" "tmux")
    
    for cmd in "${required_commands[@]}"; do
        if command -v "$cmd" >/dev/null; then
            echo "  ✅ $cmd"
        else
            echo "  ❌ $cmd (未インストール)"
        fi
    done
    
    # ディスク容量確認
    echo "💾 ディスク容量:"
    df -h . | tail -1 | awk '{print "  使用率: " $5 " (利用可能: " $4 ")"}'
    
    # プロセス確認
    echo "🔄 プロセス確認:"
    if pgrep -f "claude" >/dev/null; then
        echo "  ✅ Claude Code実行中"
    else
        echo "  ℹ️ Claude Code停止中"
    fi
    
    echo "✅ 基本システムチェック完了"
}

# 危険パターン検出 (danger-pattern-detector.sh 統合)
cmd_danger_detect() {
    local scan_all=false
    
    if [[ "${1:-}" == "--scan-all" ]]; then
        scan_all=true
    fi
    
    echo "⚠️ 危険パターン検出開始..."
    
    # 危険なファイルパターン
    local dangerous_patterns=(
        "*.log"
        "*.tmp"
        "secret*"
        "password*"
        "key*"
    )
    
    for pattern in "${dangerous_patterns[@]}"; do
        if find . -name "$pattern" -type f | head -5 | grep -q .; then
            echo "  ⚠️ 発見: $pattern"
            if [[ "$scan_all" == true ]]; then
                find . -name "$pattern" -type f | head -5
            fi
        fi
    done
    
    # 大きなファイル検出
    echo "📊 大きなファイル (>10MB):"
    find . -type f -size +10M -exec ls -lh {} \; | head -5
    
    echo "✅ 危険パターン検出完了"
}

# ミスパターン検索 (mistake-pattern-search.sh 統合)
cmd_mistake_search() {
    local search_term="${1:-}"
    
    if [[ -z "$search_term" ]]; then
        echo "❌ 検索キーワードが必要です"
        echo "使用法: ./utils.sh mistake-search <キーワード>"
        return 1
    fi
    
    echo "🔍 ミスパターン検索開始: '$search_term'"
    
    # ログファイルから検索
    local log_dirs=("runtime" "logs" ".")
    
    for dir in "${log_dirs[@]}"; do
        if [[ -d "$dir" ]]; then
            echo "📁 検索中: $dir/"
            find "$dir" -name "*.log" -o -name "*.md" | \
                xargs grep -l "$search_term" 2>/dev/null | \
                head -5 | \
                while read -r file; do
                    echo "  🎯 $file"
                done
        fi
    done
    
    echo "✅ ミスパターン検索完了"
}

# メイン処理
main() {
    case "${1:-help}" in
        api-check)
            cmd_api_check
            ;;
        env-load)
            cmd_env_load "${2:-}"
            ;;
        basic-check)
            cmd_basic_check
            ;;
        danger-detect)
            cmd_danger_detect "${2:-}"
            ;;
        mistake-search)
            cmd_mistake_search "${2:-}"
            ;;
        version)
            echo "Utils.sh version $VERSION"
            ;;
        help|--help|-h|"")
            show_help
            ;;
        *)
            echo "❌ 不明なコマンド: $1"
            echo "使用可能コマンド: api-check, env-load, basic-check, danger-detect, mistake-search, help"
            exit 1
            ;;
    esac
}

main "$@"