#!/bin/bash
# 🔄 Periodic Review System - 定期レビューシステム統合
# ================================================
# weekly-mistake-review.sh + monitoring-dashboard.sh + daily_check.sh統合
# o3推奨のPhase 1実装：低リスク統合から開始

set -euo pipefail

PROJECT_ROOT="/Users/dd/Desktop/1_dev/coding-rule2"
REVIEW_DIR="$PROJECT_ROOT/runtime/periodic_reviews"
LOG_FILE="$REVIEW_DIR/periodic_review_$(date +%Y%m%d_%H%M%S).log"

# ディレクトリ作成
mkdir -p "$REVIEW_DIR"/{weekly,daily,monitoring}

# o3推奨：構造化ログ出力
log_structured() {
    local level=$1
    local component=$2
    local message=$3
    local timestamp=$(date -Iseconds)
    
    echo "{\"timestamp\":\"$timestamp\",\"level\":\"$level\",\"component\":\"$component\",\"message\":\"$message\"}" | tee -a "$LOG_FILE"
    logger -t periodic-review "[$level] $component: $message"
}

show_usage() {
    cat << EOF
Periodic Review System - 定期レビューシステム統合

使用方法:
  $0 [OPTIONS] <mode>

モード:
  weekly          週次ミス分析レビュー
  daily           日次システムチェック
  monitoring      監視ダッシュボード更新
  all             全レビュータスクを実行

オプション:
  --dry-run       実行内容をプレビューのみ
  --scope <name>  特定スコープのみ実行
  --throttle <n>  実行間隔調整（秒）
  --output <fmt>  出力形式 (json|text|html)
  -v, --verbose   詳細ログ出力
  -h, --help      このヘルプを表示

例:
  $0 --dry-run weekly          # 週次レビューのドライラン
  $0 --output json all         # 全レビューをJSON形式で
  $0 --scope mistakes daily    # ミス関連の日次チェックのみ

統合元スクリプト:
  - weekly-mistake-review.sh
  - monitoring-dashboard.sh  
  - daily_check.sh
EOF
}

# o3推奨：単一インスタンス実行制御
acquire_lock() {
    local lock_file="/tmp/periodic_review.lock"
    local lock_timeout=300  # 5分
    
    if [ -f "$lock_file" ]; then
        local lock_pid=$(cat "$lock_file" 2>/dev/null || echo "")
        if [ -n "$lock_pid" ] && kill -0 "$lock_pid" 2>/dev/null; then
            log_structured "ERROR" "lock" "Another instance is running (PID: $lock_pid)"
            exit 1
        else
            log_structured "WARN" "lock" "Stale lock file removed"
            rm -f "$lock_file"
        fi
    fi
    
    echo $$ > "$lock_file"
}

# 週次ミス分析レビュー（weekly-mistake-review.sh統合）
execute_weekly_review() {
    local dry_run=${1:-false}
    local output_format=${2:-text}
    
    log_structured "INFO" "weekly" "Starting weekly mistake analysis review"
    
    if [ "$dry_run" = "true" ]; then
        log_structured "INFO" "weekly" "[DRY-RUN] Would analyze mistake patterns from last 7 days"
        log_structured "INFO" "weekly" "[DRY-RUN] Would generate improvement recommendations"
        log_structured "INFO" "weekly" "[DRY-RUN] Would update learning database"
        return 0
    fi
    
    # ミス履歴分析
    local mistake_count=0
    local patterns_found=0
    
    if [ -f "$PROJECT_ROOT/runtime/mistake_history.log" ]; then
        mistake_count=$(tail -n 100 "$PROJECT_ROOT/runtime/mistake_history.log" | grep -c "$(date -d '7 days ago' '+%Y-%m-%d')" || echo "0")
        
        # パターン分析
        patterns_found=$(tail -n 100 "$PROJECT_ROOT/runtime/mistake_history.log" | \
            awk '{print $3}' | sort | uniq -c | sort -nr | head -5 | wc -l)
    fi
    
    # レポート生成
    local report_file="$REVIEW_DIR/weekly/weekly_review_$(date +%Y%m%d).json"
    
    cat > "$report_file" << EOF
{
  "review_type": "weekly_mistake_analysis",
  "period": "$(date -d '7 days ago' '+%Y-%m-%d') to $(date '+%Y-%m-%d')",
  "metrics": {
    "total_mistakes": $mistake_count,
    "patterns_identified": $patterns_found,
    "improvement_rate": $(( patterns_found > 0 ? (mistake_count * 100 / patterns_found) : 0 ))
  },
  "recommendations": [
    "継続的なパターン監視の実施",
    "特定エラーパターンの自動化対応",
    "予防的措置の強化"
  ],
  "next_review": "$(date -d '+7 days' '+%Y-%m-%d')"
}
EOF
    
    log_structured "INFO" "weekly" "Weekly review completed: $mistake_count mistakes, $patterns_found patterns"
    
    if [ "$output_format" = "json" ]; then
        cat "$report_file"
    else
        echo "📊 週次レビュー完了: ミス $mistake_count 件、パターン $patterns_found 種類"
    fi
}

# 日次システムチェック（daily_check.sh統合）
execute_daily_check() {
    local dry_run=${1:-false}
    local scope=${2:-all}
    
    log_structured "INFO" "daily" "Starting daily system check (scope: $scope)"
    
    if [ "$dry_run" = "true" ]; then
        log_structured "INFO" "daily" "[DRY-RUN] Would check system health"
        log_structured "INFO" "daily" "[DRY-RUN] Would verify service status"
        log_structured "INFO" "daily" "[DRY-RUN] Would analyze resource usage"
        return 0
    fi
    
    local checks_passed=0
    local checks_total=0
    
    # システムヘルスチェック
    if [ "$scope" = "all" ] || [ "$scope" = "system" ]; then
        ((checks_total++))
        
        # ディスク使用量チェック
        local disk_usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
        if [ "$disk_usage" -lt 80 ]; then
            ((checks_passed++))
            log_structured "INFO" "daily" "Disk usage OK: ${disk_usage}%"
        else
            log_structured "WARN" "daily" "Disk usage high: ${disk_usage}%"
        fi
    fi
    
    # サービス状態チェック
    if [ "$scope" = "all" ] || [ "$scope" = "services" ]; then
        ((checks_total++))
        
        # tmuxセッション確認
        if tmux list-sessions 2>/dev/null | grep -q "multiagent\|president"; then
            ((checks_passed++))
            log_structured "INFO" "daily" "AI organization sessions active"
        else
            log_structured "WARN" "daily" "AI organization sessions not found"
        fi
    fi
    
    # ミス防止システムチェック
    if [ "$scope" = "all" ] || [ "$scope" = "mistakes" ]; then
        ((checks_total++))
        
        if [ -f "$PROJECT_ROOT/src/ai/constitutional_ai.py" ]; then
            ((checks_passed++))
            log_structured "INFO" "daily" "Constitutional AI system present"
        else
            log_structured "ERROR" "daily" "Constitutional AI system missing"
        fi
    fi
    
    # 日次レポート生成
    local report_file="$REVIEW_DIR/daily/daily_check_$(date +%Y%m%d).json"
    
    cat > "$report_file" << EOF
{
  "check_type": "daily_system_check",
  "date": "$(date -Iseconds)",
  "scope": "$scope",
  "results": {
    "checks_total": $checks_total,
    "checks_passed": $checks_passed,
    "success_rate": $(( checks_total > 0 ? (checks_passed * 100 / checks_total) : 0 ))
  },
  "status": "$([ $checks_passed -eq $checks_total ] && echo "healthy" || echo "degraded")"
}
EOF
    
    log_structured "INFO" "daily" "Daily check completed: $checks_passed/$checks_total checks passed"
    
    echo "📋 日次チェック完了: $checks_passed/$checks_total 合格"
}

# 監視ダッシュボード更新（monitoring-dashboard.sh統合）
execute_monitoring_update() {
    local dry_run=${1:-false}
    local output_format=${2:-text}
    
    log_structured "INFO" "monitoring" "Starting monitoring dashboard update"
    
    if [ "$dry_run" = "true" ]; then
        log_structured "INFO" "monitoring" "[DRY-RUN] Would update system metrics"
        log_structured "INFO" "monitoring" "[DRY-RUN] Would refresh AI organization status"
        log_structured "INFO" "monitoring" "[DRY-RUN] Would generate performance charts"
        return 0
    fi
    
    # システムメトリクス収集
    local cpu_usage=$(top -l 1 | grep "CPU usage" | awk '{print $3}' | sed 's/%//' || echo "0")
    local memory_usage=$(vm_stat | awk '/Pages active/ {active=$3} /Pages free/ {free=$3} END {printf "%.1f", (active/(active+free))*100}' || echo "0")
    local load_avg=$(uptime | awk -F'load averages:' '{print $2}' | awk '{print $1}' | sed 's/,//' || echo "0")
    
    # AI組織状態取得
    local ai_roles_active=0
    if python3 -c "
import sys; sys.path.append('$PROJECT_ROOT')
try:
    from src.ai.ai_organization_system import DynamicAIOrganizationSystem
    org = DynamicAIOrganizationSystem()
    status = org.get_organization_status()
    print(status['active_roles'])
except: print('0')
" 2>/dev/null; then
        ai_roles_active=$(python3 -c "
import sys; sys.path.append('$PROJECT_ROOT')
try:
    from src.ai.ai_organization_system import DynamicAIOrganizationSystem
    org = DynamicAIOrganizationSystem()
    status = org.get_organization_status()
    print(status['active_roles'])
except: print('0')
" 2>/dev/null || echo "0")
    fi
    
    # ダッシュボードデータ生成
    local dashboard_file="$REVIEW_DIR/monitoring/dashboard_$(date +%Y%m%d_%H%M).json"
    
    cat > "$dashboard_file" << EOF
{
  "dashboard_type": "system_monitoring",
  "timestamp": "$(date -Iseconds)",
  "system_metrics": {
    "cpu_usage": $cpu_usage,
    "memory_usage": $memory_usage,
    "load_average": $load_avg
  },
  "ai_organization": {
    "active_roles": $ai_roles_active,
    "status": "$([ $ai_roles_active -gt 0 ] && echo "active" || echo "standby")"
  },
  "health_score": $(( (100 - ${cpu_usage%.*}) + (100 - ${memory_usage%.*}) / 2 ))
}
EOF
    
    log_structured "INFO" "monitoring" "Dashboard updated: CPU ${cpu_usage}%, Memory ${memory_usage}%, AI roles $ai_roles_active"
    
    if [ "$output_format" = "json" ]; then
        cat "$dashboard_file"
    else
        echo "📊 監視更新完了: CPU ${cpu_usage}%, メモリ ${memory_usage}%, AI役職 $ai_roles_active"
    fi
}

# o3推奨：全レビュータスク実行
execute_all_reviews() {
    local dry_run=${1:-false}
    local throttle=${2:-1}
    local output_format=${3:-text}
    
    log_structured "INFO" "all" "Starting all periodic reviews"
    
    execute_daily_check "$dry_run" "all"
    sleep "$throttle"
    
    execute_monitoring_update "$dry_run" "$output_format"
    sleep "$throttle"
    
    execute_weekly_review "$dry_run" "$output_format"
    
    log_structured "INFO" "all" "All periodic reviews completed"
    echo "🎯 全定期レビュー完了"
}

# メイン実行関数
main() {
    local mode=""
    local dry_run=false
    local scope="all"
    local throttle=1
    local output_format="text"
    local verbose=false
    
    # 引数解析
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dry-run)
                dry_run=true
                shift
                ;;
            --scope)
                scope="$2"
                shift 2
                ;;
            --throttle)
                throttle="$2"
                shift 2
                ;;
            --output)
                output_format="$2"
                shift 2
                ;;
            -v|--verbose)
                verbose=true
                shift
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            weekly|daily|monitoring|all)
                mode="$1"
                shift
                ;;
            *)
                echo "エラー: 不明なオプション $1" >&2
                show_usage
                exit 1
                ;;
        esac
    done
    
    if [ -z "$mode" ]; then
        echo "エラー: モードを指定してください" >&2
        show_usage
        exit 1
    fi
    
    # o3推奨：ロック取得
    acquire_lock
    
    # バージョン情報
    if [ "$verbose" = "true" ]; then
        log_structured "INFO" "main" "Periodic Review System v1.0 (integrated from 3 scripts)"
    fi
    
    # モード実行
    case $mode in
        weekly)
            execute_weekly_review "$dry_run" "$output_format"
            ;;
        daily)
            execute_daily_check "$dry_run" "$scope"
            ;;
        monitoring)
            execute_monitoring_update "$dry_run" "$output_format"
            ;;
        all)
            execute_all_reviews "$dry_run" "$throttle" "$output_format"
            ;;
    esac
}

# o3推奨：エラーハンドラ
cleanup() {
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        log_structured "ERROR" "main" "Script failed with exit code $exit_code"
    fi
    rm -f /tmp/periodic_review.lock 2>/dev/null || true
}

trap cleanup EXIT ERR INT TERM

# スクリプトが直接実行された場合
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi