#!/bin/bash
set -euo pipefail
# 重複ファイル再発防止システム
# ============================

PROJECT_ROOT="${PROJECT_ROOT:-$(pwd)}"
LOG_FILE="$PROJECT_ROOT/runtime/logs/duplicate-prevention.log"

# ログ関数
log_action() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 重複ファイル検出関数
detect_duplicates() {
    log_action "🔍 重複ファイル検査開始"
    
    # 危険パターン検出（日付ファイルとnode_modulesは除外）
    DANGEROUS_PATTERNS=(
        "*2.md" "*3.md" 
        "*2.sh" "*3.sh"  
        "*2.py" "*3.py"
        "*backup*" "*.old" "*.bak"
    )
    
    DUPLICATES_FOUND=0
    
    for pattern in "${DANGEROUS_PATTERNS[@]}"; do
        while IFS= read -r -d '' file; do
            if [ -f "$file" ]; then
                log_action "⚠️  重複ファイル発見: $file"
                ((DUPLICATES_FOUND++))
            fi
        done < <(find "$PROJECT_ROOT" -name "$pattern" -type f -print0 2>/dev/null)
    done
    
    log_action "📊 重複ファイル合計: $DUPLICATES_FOUND 個"
    return $DUPLICATES_FOUND
}

# 自動削除関数（安全確認付き）
auto_cleanup() {
    if [ "$1" = "--force" ]; then
        log_action "🚨 強制削除モード - 重複ファイル削除実行"
        
        find "$PROJECT_ROOT" -name "*2.*" -delete 2>/dev/null
        find "$PROJECT_ROOT" -name "*3.*" -delete 2>/dev/null
        find "$PROJECT_ROOT" -name "*backup*" -delete 2>/dev/null
        find "$PROJECT_ROOT" -name "*.old" -delete 2>/dev/null
        
        log_action "✅ 重複ファイル削除完了"
    else
        log_action "💡 自動削除には --force オプションが必要です"
        log_action "   使用例: $0 --force"
    fi
}

# Pre-commit hook統合
setup_prevention_hook() {
    HOOK_FILE="$PROJECT_ROOT/.git/hooks/pre-commit-duplicate-check"
    
    cat > "$HOOK_FILE" << 'EOL'
#!/bin/bash
# 重複ファイル検出 pre-commit hook

if [ -f "scripts/duplicate-prevention-system.sh" ]; then
    if ! ./scripts/duplicate-prevention-system.sh; then
        echo "❌ 重複ファイルが検出されました。コミット前に削除してください。"
        echo "   修正方法: ./scripts/duplicate-prevention-system.sh --force"
        exit 1
    fi
fi
EOL
    
    chmod +x "$HOOK_FILE"
    log_action "🔗 Pre-commit hook設定完了: $HOOK_FILE"
}

# メイン実行
main() {
    case "$1" in
        "--force")
            auto_cleanup --force
            ;;
        "--setup-hook")
            setup_prevention_hook
            ;;
        "")
            detect_duplicates
            exit $?
            ;;
        *)
            echo "使用法: $0 [--force|--setup-hook]"
            echo "  (引数なし): 重複ファイル検出のみ"
            echo "  --force: 重複ファイル自動削除"
            echo "  --setup-hook: Git pre-commit hook設定"
            exit 1
            ;;
    esac
}

main "$@"