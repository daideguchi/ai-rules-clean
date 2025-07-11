#!/bin/bash

# 週次間違いレビュー強制実行システム
# 毎週の失敗パターン分析と対策効果測定

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LOG_DIR="$PROJECT_ROOT/runtime/ai_api_logs"
TRACKER_FILE="$LOG_DIR/mistake_prevention_tracker.md"
REVIEW_DIR="$LOG_DIR/weekly_reviews"

# 初期化
init_review_system() {
    mkdir -p "$REVIEW_DIR"
    
    # crontab設定
    local cron_entry="0 9 * * 1 $PROJECT_ROOT/scripts/utilities/weekly-mistake-review.sh auto"
    
    if ! crontab -l 2>/dev/null | grep -q "weekly-mistake-review"; then
        echo "📅 週次レビューのcron設定中..."
        (crontab -l 2>/dev/null || true; echo "$cron_entry") | crontab -
        echo "✅ 毎週月曜9:00にレビュー実行"
    fi
}

# 過去1週間のAPIエラー分析
analyze_api_errors() {
    local week_start=$(date -v-7d +%Y-%m-%d)
    local report_file="$REVIEW_DIR/review_$(date +%Y%m%d).md"
    
    echo "## 週次間違いレビュー - $(date +%Y-%m-%d)" > "$report_file"
    echo "" >> "$report_file"
    
    # APIエラーログ分析
    if [[ -f "$LOG_DIR/api_errors.log" ]]; then
        echo "### 🚨 今週のAPIエラー" >> "$report_file"
        
        local error_count=$(grep "$week_start" "$LOG_DIR/api_errors.log" 2>/dev/null | wc -l || echo "0")
        echo "- 発生回数: ${error_count}件" >> "$report_file"
        
        if [[ $error_count -gt 0 ]]; then
            echo "- 詳細:" >> "$report_file"
            grep "$week_start" "$LOG_DIR/api_errors.log" | while read -r line; do
                echo "  - $line" >> "$report_file"
            done
        fi
        echo "" >> "$report_file"
    fi
    
    # 同一エラーの再発チェック
    echo "### 🔄 同一エラー再発チェック" >> "$report_file"
    
    local gemini_errors=$(grep -c "gemini" "$LOG_DIR/api_errors.log" 2>/dev/null || echo "0")
    local o3_errors=$(grep -c "o3" "$LOG_DIR/api_errors.log" 2>/dev/null || echo "0")
    
    echo "- Geminiエラー: ${gemini_errors}件" >> "$report_file"
    echo "- O3エラー: ${o3_errors}件" >> "$report_file"
    
    # 警告判定
    if [[ $gemini_errors -gt 1 ]]; then
        echo "⚠️  **警告**: Geminiエラーが複数回発生" >> "$report_file"
    fi
    
    echo "" >> "$report_file"
}

# 対策システムの効果測定
measure_prevention_effectiveness() {
    local report_file="$REVIEW_DIR/review_$(date +%Y%m%d).md"
    
    echo "### 📊 対策システム効果測定" >> "$report_file"
    echo "" >> "$report_file"
    
    # チェックスクリプト使用回数
    local check_usage=$(find "$LOG_DIR" -name "checklist_*.log" -mtime -7 | wc -l)
    echo "- 事前チェック実行回数: ${check_usage}回" >> "$report_file"
    
    # 危険パターン検出回数
    if [[ -f "$LOG_DIR/api_usage.jsonl" ]]; then
        local dangerous_detected=$(grep '"dangerous_patterns"' "$LOG_DIR/api_usage.jsonl" | grep -v '\[\]' | wc -l)
        echo "- 危険パターン検出回数: ${dangerous_detected}回" >> "$report_file"
    fi
    
    # 実行ブロック回数
    local blocked_count=$(grep "BLOCKED" "$LOG_DIR/api_usage.jsonl" 2>/dev/null | wc -l || echo "0")
    echo "- 危険実行ブロック回数: ${blocked_count}回" >> "$report_file"
    
    echo "" >> "$report_file"
}

# 改善提案生成
generate_improvements() {
    local report_file="$REVIEW_DIR/review_$(date +%Y%m%d).md"
    
    echo "### 💡 今週の改善提案" >> "$report_file"
    echo "" >> "$report_file"
    
    # エラー頻度に基づく提案
    local total_errors=$(wc -l < "$LOG_DIR/api_errors.log" 2>/dev/null || echo "0")
    
    if [[ $total_errors -gt 5 ]]; then
        echo "- **緊急**: エラー頻度が高い（${total_errors}件）" >> "$report_file"
        echo "  - 追加の事前チェック項目が必要" >> "$report_file"
        echo "  - 自動化レベルを上げる" >> "$report_file"
    elif [[ $total_errors -gt 0 ]]; then
        echo "- エラーは発生しているが許容範囲内" >> "$report_file"
        echo "  - 現在の対策を継続" >> "$report_file"
    else
        echo "- ✅ エラーなし！対策が効果的" >> "$report_file"
    fi
    
    echo "" >> "$report_file"
    echo "### 📝 次週のアクション項目" >> "$report_file"
    echo "- [ ] 新しい危険パターンの追加" >> "$report_file"
    echo "- [ ] チェックスクリプトの改善" >> "$report_file"
    echo "- [ ] ドキュメント更新" >> "$report_file"
    echo "" >> "$report_file"
}

# 強制アクション実行
enforce_actions() {
    echo "🎯 週次レビュー強制アクション"
    
    # トラッカー更新の強制
    if [[ ! -f "$TRACKER_FILE" ]]; then
        echo "❌ トラッカーファイルが見つかりません"
        return 1
    fi
    
    local last_update=$(stat -f %m "$TRACKER_FILE" 2>/dev/null || echo "0")
    local week_ago=$(date -v-7d +%s)
    
    if [[ $last_update -lt $week_ago ]]; then
        echo "⚠️  トラッカーが1週間以上更新されていません"
        echo "対策が機能していない可能性があります"
        return 1
    fi
    
    return 0
}

# レポート表示
show_report() {
    local latest_report=$(find "$REVIEW_DIR" -name "review_*.md" | sort | tail -1)
    
    if [[ -n "$latest_report" ]]; then
        echo "📋 最新の週次レビュー:"
        echo "=========================="
        cat "$latest_report"
        echo "=========================="
    fi
}

# メイン処理
main() {
    local mode="${1:-interactive}"
    
    echo "📅 週次間違いレビューシステム"
    echo "=============================="
    
    # 初期化
    init_review_system
    
    # 分析実行
    echo "🔍 過去1週間の分析中..."
    analyze_api_errors
    measure_prevention_effectiveness
    generate_improvements
    
    # 強制チェック
    if ! enforce_actions; then
        echo "❌ 対策システムに問題があります"
        if [[ "$mode" == "interactive" ]]; then
            read -p "詳細を確認しますか？ [y/N]: " check
            if [[ "$check" == "y" ]]; then
                show_report
            fi
        fi
        exit 1
    fi
    
    echo "✅ 週次レビュー完了"
    
    if [[ "$mode" == "interactive" ]]; then
        show_report
    fi
}

main "$@"