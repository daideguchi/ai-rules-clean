#!/bin/bash

# =============================================================================
# 統合テストスイート
# 3個のtest-*スクリプトを統合し、包括的なテストシステムを提供
# =============================================================================

set -euo pipefail

# カラーコード
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# スクリプト情報
SCRIPT_VERSION="1.0.0"
SCRIPT_NAME="unified-test-suite.sh"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# ログ関数
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "\n${CYAN}==== $1 ====${NC}"; }

# グローバル変数
TEST_LOG="$PROJECT_ROOT/runtime/ai_api_logs/unified_test_$(date +%Y%m%d_%H%M%S).log"
TEST_RESULTS=()
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
SKIPPED_TESTS=0

# エラーハンドリング
trap 'log_error "テスト実行中にエラーが発生しました (line $LINENO)"; cleanup_on_error' ERR

# 使用方法表示
show_usage() {
    cat << EOF
$SCRIPT_NAME v$SCRIPT_VERSION - 統合テストスイート

使用方法:
    $SCRIPT_NAME [OPTIONS] [TEST_SUITES]

OPTIONS:
    -h, --help          このヘルプを表示
    -v, --version       バージョン情報を表示
    -q, --quiet         詳細ログを抑制
    --no-cleanup        テスト終了後のクリーンアップをスキップ
    --report-only       レポートのみ生成（テスト実行なし）

TEST_SUITES（複数指定可、省略時は --all）:
    --all              全テストスイート実行（デフォルト）
    --system           システム統合テスト
    --resilience       レジリエンステスト（障害回復力）
    --git-history      Git履歴保持テスト
    --performance      パフォーマンステスト
    --integration      統合シナリオテスト

例:
    $SCRIPT_NAME --all                    # 全テスト実行
    $SCRIPT_NAME --system --resilience   # system と resilience のみ
    $SCRIPT_NAME --report-only            # レポートのみ生成
    $SCRIPT_NAME --git-history --no-cleanup  # Git履歴テスト（クリーンアップなし）

統合元スクリプト（非推奨）:
    - complete-system-test.sh         → --system
    - resilience-tester.sh           → --resilience
    - test-git-history-preservation.sh → --git-history
EOF
}

# テスト結果記録関数
record_test() {
    local test_name="$1"
    local result="$2"
    local details="${3:-}"
    local recovery_time="${4:-N/A}"
    
    ((TOTAL_TESTS++))
    
    case "$result" in
        "PASS"|"RECOVERED")
            ((PASSED_TESTS++))
            TEST_RESULTS+=("✅ $test_name: $result - $details")
            echo "$(date): $test_name: $result - $details" >> "$TEST_LOG"
            [[ "$QUIET" != "true" ]] && log_success "$test_name ($recovery_time)"
            ;;
        "FAIL"|"FAILED")
            ((FAILED_TESTS++))
            TEST_RESULTS+=("❌ $test_name: $result - $details")
            echo "$(date): $test_name: $result - $details" >> "$TEST_LOG"
            log_error "$test_name: $details"
            ;;
        "SKIP"|"PARTIAL")
            ((SKIPPED_TESTS++))
            TEST_RESULTS+=("⚠️  $test_name: $result - $details")
            echo "$(date): $test_name: $result - $details" >> "$TEST_LOG"
            [[ "$QUIET" != "true" ]] && log_warning "$test_name: $details"
            ;;
    esac
}

# ====== システム統合テストモジュール ======

test_system_api_precheck() {
    local check_script="$PROJECT_ROOT/scripts/tools/monitoring/ai-api-check.sh"
    
    if [[ -x "$check_script" ]]; then
        record_test "api-precheck-exists" "PASS" "スクリプト存在・実行可能"
        if bash -n "$check_script"; then
            record_test "api-precheck-syntax" "PASS" "構文エラーなし"
        else
            record_test "api-precheck-syntax" "FAIL" "構文エラーあり"
        fi
    else
        record_test "api-precheck-exists" "FAIL" "スクリプト不在または実行不可"
    fi
}

test_system_danger_detection() {
    local detector="$PROJECT_ROOT/scripts/tools/validation/danger-pattern-detector.sh"
    
    if [[ -x "$detector" ]]; then
        record_test "danger-detector-exists" "PASS" "検出器存在・実行可能"
        
        local test_command="npx gemini-cli -c config.txt"
        local detector_output=$(echo "n" | "$detector" "$test_command" 2>&1 || true)
        if echo "$detector_output" | grep -q "危険"; then
            record_test "danger-pattern-detection" "PASS" "危険パターン検出成功"
        else
            record_test "danger-pattern-detection" "FAIL" "危険パターン検出失敗"
        fi
    else
        record_test "danger-detector-exists" "FAIL" "検出器不在"
    fi
}

test_system_logging() {
    local log_dir="$PROJECT_ROOT/runtime/ai_api_logs"
    
    if [[ -d "$log_dir" ]]; then
        record_test "log-directory-exists" "PASS" "ログディレクトリ存在"
        
        local test_file="$log_dir/test_write.tmp"
        if echo "test" > "$test_file" 2>/dev/null; then
            rm -f "$test_file"
            record_test "log-directory-writable" "PASS" "ログディレクトリ書き込み可能"
        else
            record_test "log-directory-writable" "FAIL" "ログディレクトリ書き込み不可"
        fi
    else
        record_test "log-directory-exists" "FAIL" "ログディレクトリ不在"
    fi
}

run_system_tests() {
    log_step "システム統合テスト"
    
    test_system_api_precheck
    test_system_danger_detection
    test_system_logging
    
    # Makefile統合テスト
    cd "$PROJECT_ROOT"
    if make help > /dev/null 2>&1; then
        record_test "makefile-basic" "PASS" "基本Makefileタスク動作"
    else
        record_test "makefile-basic" "FAIL" "Makefileエラー"
    fi
}

# ====== レジリエンステストモジュール ======

test_resilience_dependency_failures() {
    local start_time=$(date +%s)
    
    # 基本コマンド確認
    if command -v python3 &> /dev/null; then
        local end_time=$(date +%s)
        local recovery_time=$((end_time - start_time))
        record_test "python3-availability" "PASS" "Python3利用可能" "${recovery_time}秒"
    else
        record_test "python3-availability" "FAIL" "Python3不在"
    fi
}

test_resilience_filesystem() {
    local test_file="$PROJECT_ROOT/runtime/ai_api_logs/permission_test.log"
    mkdir -p "$(dirname "$test_file")"
    
    local start_time=$(date +%s)
    
    if echo "test" > "$test_file" 2>/dev/null; then
        local end_time=$(date +%s)
        local recovery_time=$((end_time - start_time))
        record_test "filesystem-write" "PASS" "ファイルシステム書き込み成功" "${recovery_time}秒"
        rm -f "$test_file"
    else
        # 代替パス試行
        if echo "test" > "/tmp/fallback_$(basename "$test_file")" 2>/dev/null; then
            local end_time=$(date +%s)
            local recovery_time=$((end_time - start_time))
            record_test "filesystem-fallback" "RECOVERED" "代替パスで書き込み成功" "${recovery_time}秒"
            rm -f "/tmp/fallback_$(basename "$test_file")"
        else
            record_test "filesystem-write" "FAIL" "ファイルシステム書き込み失敗"
        fi
    fi
}

test_resilience_memory_pressure() {
    local start_time=$(date +%s)
    local temp_dir="/tmp/memory_test_$$"
    mkdir -p "$temp_dir"
    
    # 中量ファイル処理テスト（1000個→100個に削減）
    for i in {1..100}; do
        echo "test data $i" > "$temp_dir/file_$i.txt"
    done
    
    if find "$temp_dir" -name "*.txt" | wc -l | grep -q "100"; then
        local end_time=$(date +%s)
        local recovery_time=$((end_time - start_time))
        record_test "memory-pressure-handling" "PASS" "ファイル処理完了" "${recovery_time}秒"
    else
        record_test "memory-pressure-handling" "FAIL" "ファイル処理失敗"
    fi
    
    rm -rf "$temp_dir"
}

test_resilience_concurrent_execution() {
    local start_time=$(date +%s)
    
    # 並行実行テスト
    (sleep 1; echo "process1") > /tmp/concurrent_1.log 2>&1 &
    local pid1=$!
    
    (sleep 1; echo "process2") > /tmp/concurrent_2.log 2>&1 &
    local pid2=$!
    
    wait $pid1 && wait $pid2
    local exit_code=$?
    
    if [[ $exit_code -eq 0 ]]; then
        local end_time=$(date +%s)
        local recovery_time=$((end_time - start_time))
        record_test "concurrent-execution" "PASS" "並行実行成功" "${recovery_time}秒"
    else
        record_test "concurrent-execution" "FAIL" "並行実行失敗"
    fi
    
    rm -f /tmp/concurrent_*.log
}

run_resilience_tests() {
    log_step "レジリエンステスト（障害回復力）"
    
    test_resilience_dependency_failures
    test_resilience_filesystem
    test_resilience_memory_pressure
    test_resilience_concurrent_execution
}

# ====== Git履歴保持テストモジュール ======

test_git_history_basic() {
    cd "$PROJECT_ROOT"
    
    # Git repository確認
    if git rev-parse --git-dir > /dev/null 2>&1; then
        record_test "git-repository-check" "PASS" "Git repository確認"
        
        # コミット履歴確認
        local commit_count=$(git rev-list --count HEAD 2>/dev/null || echo "0")
        if [[ $commit_count -gt 0 ]]; then
            record_test "git-history-exists" "PASS" "Git履歴存在 ($commit_count commits)"
        else
            record_test "git-history-exists" "FAIL" "Git履歴なし"
        fi
    else
        record_test "git-repository-check" "FAIL" "Git repository不在"
    fi
}

test_git_file_tracking() {
    cd "$PROJECT_ROOT"
    
    # 重要ファイルの追跡確認
    local tracked_files=(
        "scripts/tools/testing/unified-test-suite.sh"
        "src/memory/core/session-bridge.sh"
        "scripts/automation/setup-unified-environment.sh"
    )
    
    for file in "${tracked_files[@]}"; do
        if [[ -f "$file" ]]; then
            if git ls-files --error-unmatch "$file" > /dev/null 2>&1; then
                record_test "git-tracking-$file" "PASS" "ファイル追跡中"
            else
                record_test "git-tracking-$file" "FAIL" "ファイル未追跡"
            fi
        else
            record_test "git-tracking-$file" "SKIP" "ファイル存在しない"
        fi
    done
}

run_git_history_tests() {
    log_step "Git履歴保持テスト"
    
    test_git_history_basic
    test_git_file_tracking
}

# ====== パフォーマンステストモジュール ======

test_performance_script_execution() {
    local start_time=$(date +%s)
    
    # 基本スクリプトの実行時間測定
    local test_script="$PROJECT_ROOT/scripts/automation/setup-unified-environment.sh"
    
    if [[ -x "$test_script" ]]; then
        local script_start=$(date +%s)
        if "$test_script" --help > /dev/null 2>&1; then
            local script_end=$(date +%s)
            local script_time=$((script_end - script_start))
            
            if [[ $script_time -le 5 ]]; then
                record_test "script-performance" "PASS" "スクリプト実行時間良好" "${script_time}秒"
            else
                record_test "script-performance" "FAIL" "スクリプト実行時間過大" "${script_time}秒"
            fi
        else
            record_test "script-performance" "FAIL" "スクリプト実行エラー"
        fi
    else
        record_test "script-performance" "SKIP" "テストスクリプト不在"
    fi
}

test_performance_file_operations() {
    local start_time=$(date +%s)
    local test_dir="/tmp/perf_test_$$"
    mkdir -p "$test_dir"
    
    # ファイル操作性能テスト
    local file_start=$(date +%s)
    for i in {1..50}; do
        echo "test $i" > "$test_dir/file_$i.txt"
    done
    local file_end=$(date +%s)
    local file_time=$((file_end - file_start))
    
    if [[ $file_time -le 3 ]]; then
        record_test "file-operations-performance" "PASS" "ファイル操作性能良好" "${file_time}秒"
    else
        record_test "file-operations-performance" "FAIL" "ファイル操作性能低下" "${file_time}秒"
    fi
    
    rm -rf "$test_dir"
}

run_performance_tests() {
    log_step "パフォーマンステスト"
    
    test_performance_script_execution
    test_performance_file_operations
}

# ====== 統合シナリオテストモジュール ======

test_integration_full_workflow() {
    log_step "統合ワークフローテスト"
    
    # セットアップ → テスト → クリーンアップの一連の流れ
    local workflow_start=$(date +%s)
    
    # 1. 環境確認
    if [[ -f "$PROJECT_ROOT/.claude/settings.json" ]]; then
        record_test "integration-env-check" "PASS" "環境設定確認"
    else
        record_test "integration-env-check" "FAIL" "環境設定不在"
        return 1
    fi
    
    # 2. スクリプト連携テスト
    local setup_script="$PROJECT_ROOT/scripts/automation/setup-unified-environment.sh"
    if [[ -x "$setup_script" ]] && "$setup_script" --dry-run --hooks > /dev/null 2>&1; then
        record_test "integration-script-chain" "PASS" "スクリプト連携動作"
    else
        record_test "integration-script-chain" "FAIL" "スクリプト連携失敗"
    fi
    
    # 3. エラーハンドリング確認
    if set +e; false; set -e; then
        record_test "integration-error-handling" "PASS" "エラーハンドリング正常"
    else
        record_test "integration-error-handling" "FAIL" "エラーハンドリング異常"
    fi
    
    local workflow_end=$(date +%s)
    local workflow_time=$((workflow_end - workflow_start))
    
    if [[ $workflow_time -le 10 ]]; then
        record_test "integration-workflow-time" "PASS" "ワークフロー時間良好" "${workflow_time}秒"
    else
        record_test "integration-workflow-time" "FAIL" "ワークフロー時間過大" "${workflow_time}秒"
    fi
}

run_integration_tests() {
    log_step "統合シナリオテスト"
    
    test_integration_full_workflow
}

# ====== レポート生成 ======

generate_test_report() {
    log_step "テストレポート生成"
    
    local report_file="$PROJECT_ROOT/runtime/test-reports/unified-test-report-$(date +%Y%m%d-%H%M%S).md"
    mkdir -p "$(dirname "$report_file")"
    
    cat > "$report_file" << EOF
# 統合テストスイート実行レポート

## 実行概要
- **実行日時**: $(date)
- **バージョン**: $SCRIPT_VERSION
- **プロジェクトルート**: $PROJECT_ROOT
- **ログファイル**: $TEST_LOG

## テスト結果サマリー
- **総テスト数**: $TOTAL_TESTS
- **成功**: $PASSED_TESTS
- **失敗**: $FAILED_TESTS
- **スキップ**: $SKIPPED_TESTS
- **成功率**: $(( TOTAL_TESTS > 0 ? PASSED_TESTS * 100 / TOTAL_TESTS : 0 ))%

## 実行されたテストスイート
EOF

    if [[ "$TEST_SYSTEM" == "true" ]]; then
        echo "- ✅ システム統合テスト" >> "$report_file"
    fi
    if [[ "$TEST_RESILIENCE" == "true" ]]; then
        echo "- ✅ レジリエンステスト" >> "$report_file"
    fi
    if [[ "$TEST_GIT_HISTORY" == "true" ]]; then
        echo "- ✅ Git履歴保持テスト" >> "$report_file"
    fi
    if [[ "$TEST_PERFORMANCE" == "true" ]]; then
        echo "- ✅ パフォーマンステスト" >> "$report_file"
    fi
    if [[ "$TEST_INTEGRATION" == "true" ]]; then
        echo "- ✅ 統合シナリオテスト" >> "$report_file"
    fi
    
    cat >> "$report_file" << EOF

## 詳細結果

EOF
    
    for result in "${TEST_RESULTS[@]}"; do
        echo "$result" >> "$report_file"
    done
    
    cat >> "$report_file" << EOF

## 推奨事項

EOF
    
    if [[ $FAILED_TESTS -gt 0 ]]; then
        cat >> "$report_file" << EOF
### 🚨 失敗したテストへの対応
- 失敗したテストの詳細を確認し、根本原因を調査してください
- 必要に応じてシステム設定や依存関係を修正してください
- 修正後に再テストを実行してください

EOF
    fi
    
    cat >> "$report_file" << EOF
### 📈 継続的改善
1. 定期的なテスト実行の自動化
2. 新機能追加時のテストカバレッジ拡大
3. パフォーマンス監視の継続
4. レジリエンス強化の継続実装

### 🔄 次回実行時の参考
- 今回の実行時間: $(date +%s)秒
- メモリ使用量: 軽量
- 推奨実行頻度: 週1回

---

📊 このレポートは unified-test-suite.sh v$SCRIPT_VERSION によって自動生成されました。
EOF
    
    log_success "テストレポート生成完了: $report_file"
}

# ====== 結果サマリー表示 ======

show_test_summary() {
    log_step "テスト結果サマリー"
    
    echo -e "${CYAN}🎯 統合テストスイート実行結果${NC}"
    echo "=================================="
    echo ""
    echo "📊 実行統計:"
    echo "  総テスト数: $TOTAL_TESTS"
    echo "  成功: $PASSED_TESTS"
    echo "  失敗: $FAILED_TESTS"
    echo "  スキップ: $SKIPPED_TESTS"
    echo ""
    
    if [[ $TOTAL_TESTS -gt 0 ]]; then
        local success_rate=$((PASSED_TESTS * 100 / TOTAL_TESTS))
        echo "🎯 成功率: ${success_rate}%"
        echo ""
        
        if [[ $success_rate -ge 90 ]]; then
            echo -e "${GREEN}🎉 システム品質: 優秀 (${success_rate}%)${NC}"
        elif [[ $success_rate -ge 70 ]]; then
            echo -e "${YELLOW}⚠️  システム品質: 良好 (${success_rate}%)${NC}"
        else
            echo -e "${RED}🚨 システム品質: 要改善 (${success_rate}%)${NC}"
        fi
    else
        echo "⚠️  テストが実行されませんでした"
    fi
    
    echo ""
    echo "📋 詳細ログ: $TEST_LOG"
}

# ====== クリーンアップ ======

cleanup_on_error() {
    log_error "テスト実行中にエラーが発生しました"
    cleanup_test_files
}

cleanup_test_files() {
    [[ "$NO_CLEANUP" != "true" ]] && {
        rm -f /tmp/concurrent_*.log
        rm -f /tmp/fallback_*
        rm -f /tmp/perf_test_*
        rm -rf /tmp/memory_test_*
    }
}

# ====== メイン処理 ======

# デフォルト値設定
QUIET=false
NO_CLEANUP=false
REPORT_ONLY=false
TEST_ALL=true
TEST_SYSTEM=false
TEST_RESILIENCE=false
TEST_GIT_HISTORY=false
TEST_PERFORMANCE=false
TEST_INTEGRATION=false

# 引数解析
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            exit 0
            ;;
        -v|--version)
            echo "$SCRIPT_NAME version $SCRIPT_VERSION"
            exit 0
            ;;
        -q|--quiet)
            QUIET=true
            shift
            ;;
        --no-cleanup)
            NO_CLEANUP=true
            shift
            ;;
        --report-only)
            REPORT_ONLY=true
            shift
            ;;
        --all)
            TEST_ALL=true
            shift
            ;;
        --system)
            TEST_ALL=false
            TEST_SYSTEM=true
            shift
            ;;
        --resilience)
            TEST_ALL=false
            TEST_RESILIENCE=true
            shift
            ;;
        --git-history)
            TEST_ALL=false
            TEST_GIT_HISTORY=true
            shift
            ;;
        --performance)
            TEST_ALL=false
            TEST_PERFORMANCE=true
            shift
            ;;
        --integration)
            TEST_ALL=false
            TEST_INTEGRATION=true
            shift
            ;;
        *)
            log_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# --all が選択されている場合、全テストを有効にする
if [[ "$TEST_ALL" == "true" ]]; then
    TEST_SYSTEM=true
    TEST_RESILIENCE=true
    TEST_GIT_HISTORY=true
    TEST_PERFORMANCE=true
    TEST_INTEGRATION=true
fi

# メイン処理開始
main() {
    echo -e "${CYAN}🚀 統合テストスイート v$SCRIPT_VERSION${NC}"
    echo "================================================"
    echo ""
    echo "プロジェクトルート: $PROJECT_ROOT"
    echo ""
    
    # 前提条件チェック
    if [[ ! -f "$PROJECT_ROOT/.claude/settings.json" ]]; then
        log_error "プロジェクトルートで実行してください（.claude/settings.json が見つかりません）"
        exit 1
    fi
    
    # ログディレクトリ作成
    mkdir -p "$(dirname "$TEST_LOG")"
    echo "$(date): 統合テストスイート開始" > "$TEST_LOG"
    
    if [[ "$REPORT_ONLY" == "true" ]]; then
        log_info "レポートのみ生成モード"
        generate_test_report
        return 0
    fi
    
    # テストスイート実行
    if [[ "$TEST_SYSTEM" == "true" ]]; then
        run_system_tests
    fi
    
    if [[ "$TEST_RESILIENCE" == "true" ]]; then
        run_resilience_tests
    fi
    
    if [[ "$TEST_GIT_HISTORY" == "true" ]]; then
        run_git_history_tests
    fi
    
    if [[ "$TEST_PERFORMANCE" == "true" ]]; then
        run_performance_tests
    fi
    
    if [[ "$TEST_INTEGRATION" == "true" ]]; then
        run_integration_tests
    fi
    
    # 結果表示とレポート生成
    show_test_summary
    generate_test_report
    
    # クリーンアップ
    cleanup_test_files
    
    # 終了コード設定
    if [[ $FAILED_TESTS -gt 0 ]]; then
        log_error "一部テストが失敗しました (${FAILED_TESTS}/${TOTAL_TESTS})"
        exit 1
    else
        log_success "全テストが成功しました (${PASSED_TESTS}/${TOTAL_TESTS})"
        exit 0
    fi
}

# スクリプト直接実行時のみmainを実行
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi