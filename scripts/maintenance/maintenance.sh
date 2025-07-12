#!/bin/bash
set -euo pipefail

# Purpose: 統合メンテナンスシステム - ファイルシステム・セットアップ機能統合
# Usage: ./maintenance.sh <command> [options]
# Author: PRESIDENT AI組織 (Phase 3 統合完了版)
# Last Modified: 2025-07-08
# Integrated: daily_check.sh(部分) + file system maintenance

VERSION="1.0.0"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

show_help() {
    cat << EOF
🧹 Maintenance.sh - 統合メンテナンスシステム v${VERSION}

USAGE:
    ./maintenance.sh <command> [options]

COMMANDS:
    duplicate-prevent   重複ファイル防止
    emergency-cleanup   緊急重複クリーンアップ
    template-optimize   テンプレート最適化
    log-cleanup         ログファイル整理
    temp-cleanup        一時ファイル削除
    setup-environment   環境セットアップ（統合）
    monitoring-health   システムヘルスチェック
    all                 全メンテナンス実行
    help                このヘルプを表示

OPTIONS:
    --dry-run          実際の削除は行わず、対象ファイルのみ表示
    --force            確認なしで実行
    --verbose          詳細出力

EXAMPLES:
    ./maintenance.sh duplicate-prevent
    ./maintenance.sh emergency-cleanup --dry-run
    ./maintenance.sh all --verbose

EOF
}

# 重複ファイル防止 (duplicate-prevention-system.sh 統合)
cmd_duplicate_prevent() {
    local dry_run=false
    local force=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dry-run)
                dry_run=true
                shift
                ;;
            --force)
                force=true
                shift
                ;;
            *)
                shift
                ;;
        esac
    done
    
    echo "🔍 重複ファイル防止システム開始..."
    
    # 一時ファイルパターン
    local temp_patterns=(
        "*.tmp"
        "*.temp"
        "*~"
        "*.bak"
        "*.backup"
        ".DS_Store"
    )
    
    # 重複候補検出
    echo "📊 重複候補ファイル検出中..."
    
    for pattern in "${temp_patterns[@]}"; do
        local found_files=$(find "$PROJECT_ROOT" -name "$pattern" -type f 2>/dev/null)
        
        if [[ -n "$found_files" ]]; then
            echo "  🎯 パターン '$pattern' で発見:"
            echo "$found_files" | while read -r file; do
                echo "    - $file"
                
                if [[ "$dry_run" == false ]]; then
                    if [[ "$force" == true ]] || read -p "    削除しますか? (y/N): " -n 1 -r && [[ $REPLY =~ ^[Yy]$ ]]; then
                        echo
                        rm "$file"
                        echo "    ✅ 削除完了: $file"
                    else
                        echo
                        echo "    ⏭️ スキップ: $file"
                    fi
                fi
            done
        fi
    done
    
    # ファイル名による重複検出
    echo "🔍 ファイル名重複検出中..."
    
    find "$PROJECT_ROOT" -type f -name "*.sh" | \
        sed 's/.*\///' | \
        sort | \
        uniq -d | \
        while read -r filename; do
            echo "  ⚠️ 重複ファイル名: $filename"
            find "$PROJECT_ROOT" -name "$filename" -type f
        done
    
    echo "✅ 重複ファイル防止完了"
}

# 緊急重複クリーンアップ (emergency-duplicate-cleanup.sh 統合)
cmd_emergency_cleanup() {
    local dry_run=false
    local force=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dry-run)
                dry_run=true
                shift
                ;;
            --force)
                force=true
                shift
                ;;
            *)
                shift
                ;;
        esac
    done
    
    echo "🚨 緊急重複クリーンアップ開始..."
    
    # 緊急削除対象パターン
    local emergency_patterns=(
        "*.log.[0-9]*"
        "*copy*"
        "*duplicate*"
        "*.old"
        "*.orig"
    )
    
    local total_size=0
    local total_files=0
    
    for pattern in "${emergency_patterns[@]}"; do
        echo "🔍 緊急パターン検索: $pattern"
        
        while IFS= read -r -d '' file; do
            local size=$(stat -f%z "$file" 2>/dev/null || echo "0")
            total_size=$((total_size + size))
            total_files=$((total_files + 1))
            
            echo "  📁 $file ($(numfmt --to=iec $size))"
            
            if [[ "$dry_run" == false ]]; then
                if [[ "$force" == true ]] || [[ $total_files -lt 5 ]]; then
                    rm "$file"
                    echo "    ✅ 削除完了"
                fi
            fi
        done < <(find "$PROJECT_ROOT" -name "$pattern" -type f -print0 2>/dev/null)
    done
    
    echo "📊 緊急クリーンアップ結果:"
    echo "  🗂️ 対象ファイル数: $total_files"
    echo "  💾 総サイズ: $(numfmt --to=iec $total_size)"
    
    echo "✅ 緊急重複クリーンアップ完了"
}

# テンプレート最適化 (template-cleanup.sh 統合)  
cmd_template_optimize() {
    echo "📄 テンプレート最適化開始..."
    
    # 設定ファイル最適化
    echo "⚙️ 設定ファイル最適化"
    
    local config_files=(
        ".gitignore"
        ".editorconfig"
        "pyproject.toml"
    )
    
    for config in "${config_files[@]}"; do
        if [[ -f "$PROJECT_ROOT/$config" ]]; then
            echo "  ✅ $config 確認済み"
            
            # 重複行削除
            if command -v sort >/dev/null && command -v uniq >/dev/null; then
                local temp_file=$(mktemp)
                sort "$PROJECT_ROOT/$config" | uniq > "$temp_file"
                
                if ! cmp -s "$PROJECT_ROOT/$config" "$temp_file"; then
                    echo "    🔧 重複行を削除"
                    mv "$temp_file" "$PROJECT_ROOT/$config"
                else
                    rm "$temp_file"
                fi
            fi
        else
            echo "  ⚠️ $config 存在しません"
        fi
    done
    
    # 空ディレクトリ検出
    echo "📁 空ディレクトリ検出"
    find "$PROJECT_ROOT" -type d -empty | while read -r dir; do
        if [[ "$dir" != "$PROJECT_ROOT/.git"* ]]; then
            echo "  📂 空ディレクトリ: $dir"
        fi
    done
    
    echo "✅ テンプレート最適化完了"
}

# ログファイル整理
cmd_log_cleanup() {
    echo "📝 ログファイル整理開始..."
    
    local log_dirs=("runtime" "logs" ".")
    local total_size=0
    
    for dir in "${log_dirs[@]}"; do
        if [[ -d "$PROJECT_ROOT/$dir" ]]; then
            echo "📁 ログディレクトリ確認: $dir"
            
            # 古いログファイル検出 (7日以上)
            find "$PROJECT_ROOT/$dir" -name "*.log" -type f -mtime +7 | while read -r logfile; do
                local size=$(stat -f%z "$logfile" 2>/dev/null || echo "0")
                total_size=$((total_size + size))
                echo "  📄 古いログ: $logfile ($(numfmt --to=iec $size))"
            done
            
            # 大きなログファイル検出 (>10MB)
            find "$PROJECT_ROOT/$dir" -name "*.log" -type f -size +10M | while read -r biglog; do
                local size=$(stat -f%z "$biglog" 2>/dev/null || echo "0")
                echo "  📈 大きなログ: $biglog ($(numfmt --to=iec $size))"
            done
        fi
    done
    
    echo "✅ ログファイル整理完了"
}

# 一時ファイル削除
cmd_temp_cleanup() {
    echo "🗑️ 一時ファイル削除開始..."
    
    local temp_patterns=(
        "*.tmp"
        "*.temp"
        ".#*"
        "*~"
        "*.swp"
        "*.swo"
    )
    
    local deleted_count=0
    local deleted_size=0
    
    for pattern in "${temp_patterns[@]}"; do
        while IFS= read -r -d '' file; do
            local size=$(stat -f%z "$file" 2>/dev/null || echo "0")
            deleted_size=$((deleted_size + size))
            deleted_count=$((deleted_count + 1))
            
            echo "  🗑️ 削除: $file"
            rm "$file"
        done < <(find "$PROJECT_ROOT" -name "$pattern" -type f -print0 2>/dev/null)
    done
    
    echo "📊 一時ファイル削除結果:"
    echo "  🗂️ 削除ファイル数: $deleted_count"
    echo "  💾 削除サイズ: $(numfmt --to=iec $deleted_size)"
    
    echo "✅ 一時ファイル削除完了"
}

# 環境セットアップ（setup-*スクリプト統合相当）
cmd_setup_environment() {
    local dry_run=false
    local component="all"
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dry-run)
                dry_run=true
                shift
                ;;
            --component)
                component="$2"
                shift 2
                ;;
            *)
                shift
                ;;
        esac
    done
    
    echo "🚀 環境セットアップ開始..."
    
    # ディレクトリ構造確認・作成
    local required_dirs=(
        "runtime/ai_api_logs"
        "runtime/backups"
        "runtime/wal_archives"
        "runtime/periodic_reviews"
        "runtime/secure_state"
        "src/memory/core/session-records"
        "logs"
        "temp"
    )
    
    echo "📁 必要ディレクトリ確認..."
    for dir in "${required_dirs[@]}"; do
        local full_path="$PROJECT_ROOT/$dir"
        if [[ ! -d "$full_path" ]]; then
            echo "  📂 作成: $dir"
            if [[ "$dry_run" == false ]]; then
                mkdir -p "$full_path"
            fi
        else
            echo "  ✅ 存在: $dir"
        fi
    done
    
    # 権限設定確認
    echo "🔒 実行権限確認..."
    find "$PROJECT_ROOT/scripts" -name "*.sh" -type f | while read -r script; do
        if [[ ! -x "$script" ]]; then
            echo "  🔧 権限付与: $(basename "$script")"
            if [[ "$dry_run" == false ]]; then
                chmod +x "$script"
            fi
        fi
    done
    
    # システムサービス状態確認
    echo "🔍 システムサービス状態確認..."
    
    # tmuxセッション確認
    if command -v tmux >/dev/null 2>&1; then
        local tmux_sessions=$(tmux list-sessions 2>/dev/null | wc -l || echo "0")
        echo "  🗺️ tmuxセッション: $tmux_sessions 個"
    else
        echo "  ⚠️ tmuxがインストールされていません"
    fi
    
    # Python環境確認
    if command -v python3 >/dev/null 2>&1; then
        local python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
        echo "  🐍 Python: $python_version"
    else
        echo "  ⚠️ Python3がインストールされていません"
    fi
    
    # Git環境確認
    if git -C "$PROJECT_ROOT" status >/dev/null 2>&1; then
        local git_branch=$(git -C "$PROJECT_ROOT" branch --show-current 2>/dev/null || echo "unknown")
        echo "  🌳 Gitブランチ: $git_branch"
    else
        echo "  ⚠️ Gitリポジトリではありません"
    fi
    
    echo "✅ 環境セットアップ完了"
}

# システムヘルスチェック（daily_check.sh機能統合）
cmd_monitoring_health() {
    local output_format="text"
    local check_scope="all"
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --output)
                output_format="$2"
                shift 2
                ;;
            --scope)
                check_scope="$2"
                shift 2
                ;;
            *)
                shift
                ;;
        esac
    done
    
    echo "👩‍⚕️ システムヘルスチェック開始..."
    
    local health_score=0
    local total_checks=0
    local warnings=()
    local errors=()
    
    # ファイルシステムチェック
    if [[ "$check_scope" == "all" || "$check_scope" == "filesystem" ]]; then
        echo "📁 ファイルシステムチェック..."
        ((total_checks++))
        
        # ディスク使用量確認
        local disk_usage=$(df "$PROJECT_ROOT" | awk 'NR==2 {print $5}' | sed 's/%//' || echo "0")
        if [[ $disk_usage -lt 80 ]]; then
            ((health_score++))
            echo "  ✅ ディスク使用量: ${disk_usage}%"
        elif [[ $disk_usage -lt 90 ]]; then
            warnings+=("Disk usage high: ${disk_usage}%")
            echo "  ⚠️ ディスク使用量高: ${disk_usage}%")
        else
            errors+=("Disk usage critical: ${disk_usage}%")
            echo "  🔴 ディスク使用量クリティカル: ${disk_usage}%"
        fi
        
        # 重要ファイル存在確認
        local critical_files=(
            "CLAUDE.md"
            "src/ai/ai_organization_system.py"
            "scripts/maintenance/db-unified-maintenance.sh"
            "scripts/maintenance/periodic-review-system.sh"
        )
        
        local missing_files=0
        for file in "${critical_files[@]}"; do
            if [[ ! -f "$PROJECT_ROOT/$file" ]]; then
                ((missing_files++))
                errors+=("Critical file missing: $file")
                echo "  🔴 重要ファイル不在: $file"
            fi
        done
        
        if [[ $missing_files -eq 0 ]]; then
            echo "  ✅ 重要ファイル: すべて存在"
        fi
    fi
    
    # システムリソースチェック
    if [[ "$check_scope" == "all" || "$check_scope" == "resources" ]]; then
        echo "📈 システムリソースチェック..."
        ((total_checks++))
        
        # メモリ使用量確認
        if command -v vm_stat >/dev/null 2>&1; then
            local memory_pressure=$(vm_stat | awk '/Pages active/ {active=$3} /Pages free/ {free=$3} END {printf "%.0f", (active/(active+free))*100}' 2>/dev/null || echo "unknown")
            if [[ "$memory_pressure" != "unknown" && $memory_pressure -lt 80 ]]; then
                ((health_score++))
                echo "  ✅ メモリ使用采: ${memory_pressure}%"
            else
                warnings+=("Memory usage: ${memory_pressure}%")
                echo "  ⚠️ メモリ使用量: ${memory_pressure}%"
            fi
        fi
        
        # ロードアベレージ確認
        local load_avg=$(uptime | awk -F'load averages:' '{print $2}' | awk '{print $1}' | sed 's/,//' 2>/dev/null || echo "0")
        local load_int=${load_avg%.*}
        if [[ $load_int -lt 2 ]]; then
            echo "  ✅ ロードアベレージ: $load_avg"
        else
            warnings+=("Load average high: $load_avg")
            echo "  ⚠️ ロードアベレージ高: $load_avg"
        fi
    fi
    
    # AI組織システムチェック
    if [[ "$check_scope" == "all" || "$check_scope" == "ai_systems" ]]; then
        echo "🤖 AI組織システムチェック..."
        ((total_checks++))
        
        # tmuxセッション確認
        if command -v tmux >/dev/null 2>&1; then
            local tmux_sessions=$(tmux list-sessions 2>/dev/null | grep -E "multiagent|president" | wc -l || echo "0")
            if [[ $tmux_sessions -gt 0 ]]; then
                ((health_score++))
                echo "  ✅ AI組織セッション: $tmux_sessions 個活動中"
            else
                warnings+=("No AI organization sessions found")
                echo "  ⚠️ AI組織セッションが見つかりません"
            fi
        fi
        
        # 動的AI組織システム確認
        if python3 -c "from src.ai.ai_organization_system import DynamicAIOrganizationSystem; print('OK')" 2>/dev/null; then
            echo "  ✅ 動的AI組織システム: 正常"
        else
            warnings+=("Dynamic AI organization system not accessible")
            echo "  ⚠️ 動的AI組織システムアクセス不可"
        fi
    fi
    
    # 結果サマリー
    local health_percentage=$((health_score * 100 / total_checks))
    
    echo ""
    echo "📈 ヘルスチェック結果:"
    echo "  🎯 総合スコア: $health_score/$total_checks ($health_percentage%)"
    echo "  ⚠️ 警告: ${#warnings[@]} 件"
    echo "  🔴 エラー: ${#errors[@]} 件"
    
    # 警告・エラー表示
    if [[ ${#warnings[@]} -gt 0 ]]; then
        echo ""
        echo "⚠️ 警告一覧:"
        for warning in "${warnings[@]}"; do
            echo "  - $warning"
        done
    fi
    
    if [[ ${#errors[@]} -gt 0 ]]; then
        echo ""
        echo "🔴 エラー一覧:"
        for error in "${errors[@]}"; do
            echo "  - $error"
        done
    fi
    
    # JSON出力
    if [[ "$output_format" == "json" ]]; then
        local warnings_json=$(printf '"%s",' "${warnings[@]}" | sed 's/,$//')
        local errors_json=$(printf '"%s",' "${errors[@]}" | sed 's/,$//')
        echo ""
        echo "{\"health_score\":$health_score,\"total_checks\":$total_checks,\"health_percentage\":$health_percentage,\"warnings\":[$warnings_json],\"errors\":[$errors_json]}"
    fi
    
    # ログ記録
    echo "$(date -Iseconds): Health check completed - Score: $health_score/$total_checks" >> "$PROJECT_ROOT/runtime/health_check.log"
    
    echo ""
    echo "✅ システムヘルスチェック完了"
    
    return 0
}

# 全メンテナンス実行
cmd_all() {
    local verbose=false
    
    if [[ "${1:-}" == "--verbose" ]]; then
        verbose=true
    fi
    
    echo "🎯 全メンテナンス実行開始..."
    
    echo "="*50
    cmd_duplicate_prevent --force
    
    echo "="*50
    cmd_template_optimize
    
    echo "="*50
    cmd_log_cleanup
    
    echo "="*50
    cmd_temp_cleanup
    
    echo "="*50
    cmd_setup_environment
    
    echo "="*50
    cmd_monitoring_health
    
    echo "="*50
    echo "🎉 全メンテナンス実行完了"
}

# メイン処理
main() {
    case "${1:-help}" in
        duplicate-prevent)
            shift
            cmd_duplicate_prevent "$@"
            ;;
        emergency-cleanup)
            shift
            cmd_emergency_cleanup "$@"
            ;;
        template-optimize)
            cmd_template_optimize
            ;;
        log-cleanup)
            cmd_log_cleanup
            ;;
        temp-cleanup)
            cmd_temp_cleanup
            ;;
        setup-environment)
            shift
            cmd_setup_environment "$@"
            ;;
        monitoring-health)
            shift
            cmd_monitoring_health "$@"
            ;;
        all)
            shift
            cmd_all "$@"
            ;;
        help|--help|-h|"")
            show_help
            ;;
        *)
            echo "❌ 不明なコマンド: $1"
            echo "使用可能コマンド: duplicate-prevent, emergency-cleanup, template-optimize, log-cleanup, temp-cleanup, setup-environment, monitoring-health, all, help"
            exit 1
            ;;
    esac
}

main "$@"