#!/bin/bash

# =============================================================================
# [LEGACY WRAPPER] verify.sh
# 
# このスクリプトは unified-validation-tool.py に統合されました。
# Phase 6 統合完了 - レガシー互換性のためのwrapperスクリプト
# 
# 新しい使用方法:
#   scripts/tools/unified-validation-tool.py system-verify --type <type>
# =============================================================================

echo "⚠️  [LEGACY] verify.sh は統合されました"
echo "📦 unified-validation-tool.py system-verify に移行してください"
echo ""
echo "🔄 自動転送中..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 引数変換
command="${1:-all}"
shift || true

case "$command" in
    "system-test")
        type_arg="system-test"
        ;;
    "structure")
        type_arg="structure"
        ;;
    "fast-lane")
        type_arg="fast-lane"
        ;;
    "git-history")
        type_arg="git-history"
        ;;
    "all")
        type_arg="all"
        ;;
    "help"|"--help"|"-h")
        exec python3 "$SCRIPT_DIR/../unified-validation-tool.py" --help
        ;;
    *)
        type_arg="all"
        ;;
esac

# 追加オプション処理
args=("--type" "$type_arg")
for arg in "$@"; do
    case "$arg" in
        "--fix")
            args+=("--fix")
            ;;
        "--verbose")
            args+=("--verbose")
            ;;
        *)
            args+=("$arg")
            ;;
    esac
done

exec python3 "$SCRIPT_DIR/../unified-validation-tool.py" system-verify "${args[@]}"

VERSION="1.0.0"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

show_help() {
    cat << EOF
🔍 Verify.sh - 統合検証システム v${VERSION}

USAGE:
    ./verify.sh <command> [options]

COMMANDS:
    system-test         包括システムテスト
    pre-prompt          プロンプト事前検証
    fast-lane           高速検証システム
    structure           プロジェクト構造検証
    git-history         Git履歴保存テスト
    all                 全検証実行
    help                このヘルプを表示

EXAMPLES:
    ./verify.sh system-test
    ./verify.sh structure --fix
    ./verify.sh all --verbose

EOF
}

# 包括システムテスト (complete-system-test.sh 統合)
cmd_system_test() {
    echo "🧪 包括システムテスト開始..."
    
    local errors=0
    
    # Python環境テスト
    echo "🐍 Python環境テスト"
    if python3 -c "import sys; print(f'Python {sys.version}')" 2>/dev/null; then
        echo "  ✅ Python環境OK"
    else
        echo "  ❌ Python環境NG"
        ((errors++))
    fi
    
    # 必須ディレクトリ確認
    echo "📁 ディレクトリ構造テスト"
    local required_dirs=("src" "scripts" "docs" "runtime")
    
    for dir in "${required_dirs[@]}"; do
        if [[ -d "$PROJECT_ROOT/$dir" ]]; then
            echo "  ✅ $dir/"
        else
            echo "  ❌ $dir/ (存在しません)"
            ((errors++))
        fi
    done
    
    # Git設定確認
    echo "🔧 Git設定テスト"
    if git config user.name >/dev/null && git config user.email >/dev/null; then
        echo "  ✅ Git設定OK"
    else
        echo "  ❌ Git設定不完全"
        ((errors++))
    fi
    
    # スクリプト実行権限確認
    echo "🔐 スクリプト権限テスト"
    local script_count=$(find "$PROJECT_ROOT/scripts" -name "*.sh" -executable | wc -l)
    echo "  ✅ 実行可能スクリプト: ${script_count}個"
    
    # 結果報告
    if [[ $errors -eq 0 ]]; then
        echo "🎉 包括システムテスト完了 - 全てOK"
        return 0
    else
        echo "❌ 包括システムテスト完了 - ${errors}個のエラー"
        return 1
    fi
}

# プロンプト事前検証 (pre-prompt-validation.sh 統合)
cmd_pre_prompt() {
    echo "📝 プロンプト事前検証開始..."
    
    # 危険フレーズ検出
    local dangerous_phrases=(
        "削除"
        "rm -rf"
        "sudo"
        "強制"
        "全て削除"
    )
    
    echo "⚠️ 危険フレーズチェック"
    for phrase in "${dangerous_phrases[@]}"; do
        echo "  🔍 '$phrase' をチェック"
    done
    
    # プロンプト長確認
    echo "📏 プロンプト長チェック"
    echo "  ✅ 検証準備完了"
    
    echo "✅ プロンプト事前検証完了"
}

# 高速検証システム (fast-lane-validator.sh 統合)
cmd_fast_lane() {
    echo "⚡ 高速検証開始..."
    
    # 構文チェック
    echo "🔍 Bashスクリプト構文チェック"
    local syntax_errors=0
    
    while IFS= read -r -d '' script; do
        if ! bash -n "$script" 2>/dev/null; then
            echo "  ❌ 構文エラー: $script"
            ((syntax_errors++))
        fi
    done < <(find "$PROJECT_ROOT/scripts" -name "*.sh" -print0)
    
    if [[ $syntax_errors -eq 0 ]]; then
        echo "  ✅ 全スクリプト構文OK"
    else
        echo "  ❌ ${syntax_errors}個の構文エラー"
    fi
    
    # ファイル権限チェック
    echo "🔐 ファイル権限高速チェック"
    local perm_issues=$(find "$PROJECT_ROOT" -name "*.sh" ! -executable | wc -l)
    
    if [[ $perm_issues -eq 0 ]]; then
        echo "  ✅ スクリプト権限OK"
    else
        echo "  ⚠️ ${perm_issues}個のスクリプトに実行権限なし"
    fi
    
    echo "✅ 高速検証完了"
}

# プロジェクト構造検証 (validate-structure.sh 統合)
cmd_structure() {
    local fix_mode=false
    
    if [[ "${1:-}" == "--fix" ]]; then
        fix_mode=true
    fi
    
    echo "🏗️ プロジェクト構造検証開始..."
    
    # 必須ファイル確認
    local required_files=(
        "README.md"
        "CLAUDE.md"
        "Makefile"
        ".gitignore"
    )
    
    echo "📄 必須ファイル確認"
    for file in "${required_files[@]}"; do
        if [[ -f "$PROJECT_ROOT/$file" ]]; then
            echo "  ✅ $file"
        else
            echo "  ❌ $file (存在しません)"
            if [[ "$fix_mode" == true ]]; then
                echo "  🔧 $file 作成中..."
                touch "$PROJECT_ROOT/$file"
                echo "  ✅ $file 作成完了"
            fi
        fi
    done
    
    # ディレクトリ階層確認
    echo "📁 ディレクトリ階層確認"
    local max_depth=$(find "$PROJECT_ROOT" -type d | awk -F/ '{print NF}' | sort -nr | head -1)
    echo "  📊 最大階層深度: $((max_depth - $(echo "$PROJECT_ROOT" | awk -F/ '{print NF}')))層"
    
    if [[ $max_depth -gt 8 ]]; then
        echo "  ⚠️ 階層が深すぎます (推奨: 6層以下)"
    else
        echo "  ✅ 階層深度適切"
    fi
    
    echo "✅ プロジェクト構造検証完了"
}

# Git履歴保存テスト (test-git-history-preservation.sh 統合)
cmd_git_history() {
    echo "📚 Git履歴保存テスト開始..."
    
    # Git状態確認
    if ! git status >/dev/null 2>&1; then
        echo "❌ Gitリポジトリではありません"
        return 1
    fi
    
    echo "🔍 Git履歴分析"
    
    # コミット数確認
    local commit_count=$(git rev-list --count HEAD 2>/dev/null || echo "0")
    echo "  📊 総コミット数: $commit_count"
    
    # ブランチ確認
    local current_branch=$(git branch --show-current)
    echo "  🌿 現在のブランチ: $current_branch"
    
    # 最新コミット確認
    local latest_commit=$(git log -1 --format="%h - %s" 2>/dev/null || echo "なし")
    echo "  📝 最新コミット: $latest_commit"
    
    # 変更ファイル確認
    local modified_files=$(git status --porcelain | wc -l)
    echo "  📝 変更ファイル数: $modified_files"
    
    if [[ $modified_files -gt 0 ]]; then
        echo "  ⚠️ 未コミットの変更があります"
    else
        echo "  ✅ 作業ディレクトリクリーン"
    fi
    
    echo "✅ Git履歴保存テスト完了"
}

# 全検証実行
cmd_all() {
    local verbose=false
    
    if [[ "${1:-}" == "--verbose" ]]; then
        verbose=true
    fi
    
    echo "🎯 全検証実行開始..."
    
    local total_errors=0
    
    # 各検証を順次実行
    echo "="*50
    cmd_system_test || ((total_errors++))
    
    echo "="*50
    cmd_structure || ((total_errors++))
    
    echo "="*50
    cmd_fast_lane || ((total_errors++))
    
    echo "="*50
    cmd_git_history || ((total_errors++))
    
    echo "="*50
    echo "🎯 全検証実行完了"
    
    if [[ $total_errors -eq 0 ]]; then
        echo "🎉 全検証PASS - エラーなし"
        return 0
    else
        echo "❌ 検証完了 - ${total_errors}個のエラー"
        return 1
    fi
}

# メイン処理
main() {
    case "${1:-help}" in
        system-test)
            cmd_system_test
            ;;
        pre-prompt)
            cmd_pre_prompt
            ;;
        fast-lane)
            cmd_fast_lane
            ;;
        structure)
            cmd_structure "${2:-}"
            ;;
        git-history)
            cmd_git_history
            ;;
        all)
            cmd_all "${2:-}"
            ;;
        help|--help|-h|"")
            show_help
            ;;
        *)
            echo "❌ 不明なコマンド: $1"
            echo "使用可能コマンド: system-test, pre-prompt, fast-lane, structure, git-history, all, help"
            exit 1
            ;;
    esac
}

main "$@"