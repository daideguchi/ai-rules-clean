#!/bin/bash

# =============================================================================
# 統合環境セットアップスクリプト
# 7個のsetup-*スクリプトを統合し、モジュール化された環境構築を提供
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
SCRIPT_NAME="setup-unified-environment.sh"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# ログ関数
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "\n${CYAN}==== $1 ====${NC}"; }

# エラーハンドリング
trap 'log_error "セットアップ中にエラーが発生しました (line $LINENO)"; exit 1' ERR

# 使用方法表示
show_usage() {
    cat << EOF
$SCRIPT_NAME v$SCRIPT_VERSION - 統合環境セットアップスクリプト

使用方法:
    $SCRIPT_NAME [OPTIONS] [MODULES]

OPTIONS:
    -h, --help          このヘルプを表示
    -v, --version       バージョン情報を表示
    -d, --dry-run       実際のセットアップを実行せず、予定される操作を表示
    -q, --quiet         詳細ログを抑制
    --force            既存設定を上書き

MODULES（複数指定可、省略時は --all）:
    --all              全モジュールを実行（デフォルト）
    --hooks            Git hooks設定とフック絶対パス設定
    --status           自動ステータス表示システム
    --dev              開発環境設定（IDE連携、シンボリックリンク）
    --validation       ファイル検証システム
    --cron             定期実行設定（Janitor Bot）
    --structure        構造維持hooks
    --portable         ポータブル環境設定

例:
    $SCRIPT_NAME --all                    # 全モジュール実行
    $SCRIPT_NAME --hooks --status         # hooks と status のみ
    $SCRIPT_NAME --dry-run --all          # dry-run モードで全確認
    $SCRIPT_NAME --portable --force       # ポータブル設定を強制実行

統合元スクリプト（非推奨）:
    - setup-auto-status-hooks.sh    → --status
    - setup-dev-environment.sh      → --dev
    - setup-file-validation.sh      → --validation
    - setup-hooks.sh                → --hooks
    - setup-janitor-cron.sh         → --cron
    - setup-structure-hooks.sh      → --structure
    - setup-portable.sh             → --portable
EOF
}

# 共通ユーティリティ関数
backup_existing() {
    local target="$1"
    local backup_name="$2"
    
    if [ -e "$target" ] && [ ! -L "$target" ]; then
        local backup_file="${target}.backup-$(date +%Y%m%d-%H%M%S)"
        if [[ "$DRY_RUN" == "true" ]]; then
            log_info "[DRY-RUN] バックアップ: $target -> $backup_file"
        else
            mv "$target" "$backup_file"
            log_info "バックアップ: $target -> $backup_file"
        fi
    elif [ -L "$target" ]; then
        if [[ "$DRY_RUN" == "true" ]]; then
            log_info "[DRY-RUN] 既存シンボリックリンク削除: $target"
        else
            rm "$target"
            log_info "既存シンボリックリンク削除: $target"
        fi
    fi
}

create_symlink() {
    local source="$1"
    local target="$2"
    local description="$3"
    
    if [ -d "$source" ]; then
        backup_existing "$target" "$description"
        if [[ "$DRY_RUN" == "true" ]]; then
            log_info "[DRY-RUN] $description: $target -> $source"
        else
            ln -sf "$source" "$target"
            log_success "$description: $target -> $source"
        fi
    else
        log_warning "スキップ (ソースなし): $description"
    fi
}

# プラットフォーム検出
detect_platform() {
    case "$(uname -s)" in
        Linux*) echo "linux" ;;
        Darwin*) echo "macos" ;;
        CYGWIN*) echo "windows" ;;
        *) echo "unknown" ;;
    esac
}

# パッケージマネージャー検出
detect_package_manager() {
    if command -v brew &> /dev/null; then
        echo "brew"
    elif command -v apt-get &> /dev/null; then
        echo "apt"
    elif command -v yum &> /dev/null; then
        echo "yum"
    elif command -v dnf &> /dev/null; then
        echo "dnf"
    else
        echo "unknown"
    fi
}

# ====== モジュール実装 ======

# Git hooks設定モジュール
setup_hooks_module() {
    log_step "Git Hooks設定"
    
    local hooks_dir="$PROJECT_ROOT/.git/hooks"
    local scripts_hooks_dir="$PROJECT_ROOT/scripts/hooks"
    
    # Git hooks directory確認
    if [[ ! -d "$hooks_dir" ]]; then
        log_error "Git repository not found. Initialize git first."
        return 1
    fi
    
    # フック絶対パス設定
    if [[ -f "$PROJECT_ROOT/.claude/settings.json" ]]; then
        if [[ "$DRY_RUN" == "true" ]]; then
            log_info "[DRY-RUN] .claude/settings.json の絶対パス設定"
        else
            backup_existing "$PROJECT_ROOT/.claude/settings.json" "claude-settings"
            
            cat > "$PROJECT_ROOT/.claude/settings.json" << EOF
{
  "hooks": {
    "Notification": [
      {
        "hooks": [
          {
            "command": "$scripts_hooks_dir/notification_router.py",
            "type": "command"
          }
        ],
        "matcher": ""
      }
    ],
    "PostToolUse": [
      {
        "hooks": [
          {
            "command": "$scripts_hooks_dir/post_auto_format.py",
            "type": "command"
          }
        ],
        "matcher": "Edit|Write|MultiEdit"
      }
    ],
    "PreToolUse": [
      {
        "hooks": [
          {
            "command": "$scripts_hooks_dir/president_declaration_gate.py",
            "type": "command"
          }
        ],
        "matcher": ".*"
      }
    ]
  },
  "timeout": 120
}
EOF
            log_success "Claude hooks設定を絶対パスで更新"
        fi
    fi
    
    # Git hooks作成
    local hooks_to_create=("post-commit" "post-merge" "pre-push")
    
    for hook in "${hooks_to_create[@]}"; do
        if [[ "$DRY_RUN" == "true" ]]; then
            log_info "[DRY-RUN] $hook hook作成"
        else
            case "$hook" in
                "post-commit")
                    cat > "$hooks_dir/$hook" << 'EOF'
#!/bin/bash
cd "$(git rev-parse --show-toplevel)"
if [ -f "scripts/auto-status-display.py" ]; then
    echo "📋 Updated Project Status:"
    python3 scripts/auto-status-display.py --brief
fi
EOF
                    ;;
                "post-merge")
                    cat > "$hooks_dir/$hook" << 'EOF'
#!/bin/bash
cd "$(git rev-parse --show-toplevel)"
if [ -f "scripts/auto-status-display.py" ]; then
    echo "📋 Project Status (after merge):"
    python3 scripts/auto-status-display.py --brief
fi
EOF
                    ;;
                "pre-push")
                    cat > "$hooks_dir/$hook" << 'EOF'
#!/bin/bash
cd "$(git rev-parse --show-toplevel)"

# 構造チェック
MAX_ROOT_DIRS=8
root_dir_count=$(find . -maxdepth 1 -type d ! -name ".git" ! -name "." | wc -l)

if [ "$root_dir_count" -gt $MAX_ROOT_DIRS ]; then
    echo "❌ 構造違反: ルートディレクトリが${root_dir_count}個 (上限${MAX_ROOT_DIRS})"
    exit 1
fi

if [ -f "scripts/auto-status-display.py" ]; then
    echo "📋 Pre-push Status Check:"
    python3 scripts/auto-status-display.py --brief
fi
EOF
                    ;;
            esac
            chmod +x "$hooks_dir/$hook"
            log_success "$hook hook作成完了"
        fi
    done
}

# 自動ステータス表示モジュール
setup_status_module() {
    log_step "自動ステータス表示システム"
    
    # Shell統合設定
    for shell in zsh bash; do
        local shell_file="$PROJECT_ROOT/.shell_integration.$shell"
        if [[ "$DRY_RUN" == "true" ]]; then
            log_info "[DRY-RUN] Shell統合設定作成: $shell_file"
        else
            cat > "$shell_file" << EOF
# Auto-status display for this project
# Add to ~/.${shell}rc: source $(pwd)/.shell_integration.$shell

function _in_project_dir() {
    local current_dir="\$PWD"
    while [[ "\$current_dir" != "/" ]]; do
        if [[ -f "\$current_dir/STATUS.md" ]]; then
            return 0
        fi
        current_dir="\$(dirname "\$current_dir")"
    done
    return 1
}

function cd() {
    builtin cd "\$@"
    if _in_project_dir; then
        if [[ -f "scripts/auto-status-display.py" ]]; then
            python3 scripts/auto-status-display.py > /dev/null 2>&1 || true
        fi
        if [[ -f ".task_status" ]]; then
            echo ""
            echo "\$(cat .task_status)"
            echo ""
        fi
    fi
}

alias status='python3 scripts/auto-status-display.py --brief'
alias tasks='cat STATUS.md'
EOF
            log_success "Shell統合設定作成: $shell_file"
        fi
    done
    
    # Makefile統合
    local makefile_content='
# Task Status Management
.PHONY: status status-brief status-update tasks

status:
	@python3 scripts/auto-status-display.py --brief

status-brief:
	@cat .task_status 2>/dev/null || echo "🎯 No active tasks"

status-update:
	@python3 scripts/auto-status-display.py

tasks:
	@cat STATUS.md
'
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY-RUN] Makefile にタスクステータス関連コマンド追加"
    else
        if [[ ! -f "$PROJECT_ROOT/Makefile" ]]; then
            touch "$PROJECT_ROOT/Makefile"
        fi
        echo "$makefile_content" >> "$PROJECT_ROOT/Makefile"
        log_success "Makefile タスクステータス関連コマンド追加"
    fi
}

# 開発環境設定モジュール
setup_dev_module() {
    log_step "開発環境設定"
    
    local dev_dir="$PROJECT_ROOT/.dev"
    
    # IDE設定ディレクトリ作成
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY-RUN] 開発環境ディレクトリ作成: $dev_dir"
    else
        mkdir -p "$dev_dir"/{cursor,vscode,common}
        log_success "開発環境ディレクトリ作成: $dev_dir"
    fi
    
    # VSCode設定
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY-RUN] VSCode設定作成"
    else
        mkdir -p "$dev_dir/vscode"
        cat > "$dev_dir/vscode/settings.json" << 'EOF'
{
  "files.associations": {
    "*.md": "markdown",
    "*.sh": "shellscript"
  },
  "editor.formatOnSave": true,
  "files.insertFinalNewline": true,
  "files.trimTrailingWhitespace": true
}
EOF
        log_success "VSCode設定作成完了"
    fi
    
    # シンボリックリンク設定
    create_symlink "$dev_dir/cursor" "$PROJECT_ROOT/.cursor" "Cursor IDE"
    create_symlink "$dev_dir/vscode" "$PROJECT_ROOT/.vscode" "Visual Studio Code"
}

# ファイル検証モジュール
setup_validation_module() {
    log_step "ファイル検証システム"
    
    # pre-commit設定
    local precommit_config="$PROJECT_ROOT/.pre-commit-config.yaml"
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY-RUN] pre-commit設定作成: $precommit_config"
    else
        cat > "$precommit_config" << 'EOF'
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: check-case-conflict
      - id: check-symlinks
      - id: check-added-large-files
        args: ['--maxkb=1024']
      - id: detect-private-key
      - id: check-json
      - id: check-yaml
      - id: end-of-file-fixer
      - id: trailing-whitespace
EOF
        log_success "pre-commit設定作成完了"
    fi
    
    # pre-commitインストール
    if command -v pre-commit &> /dev/null; then
        if [[ "$DRY_RUN" == "true" ]]; then
            log_info "[DRY-RUN] pre-commit hooks インストール"
        else
            cd "$PROJECT_ROOT"
            pre-commit install
            log_success "pre-commit hooks インストール完了"
        fi
    else
        log_warning "pre-commit not found. Install with: pip install pre-commit"
    fi
}

# 定期実行設定モジュール
setup_cron_module() {
    log_step "定期実行設定（Janitor Bot）"
    
    local cron_entry="0 2 * * * cd $PROJECT_ROOT && python3 scripts/janitor-bot.py"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY-RUN] Cron設定追加: $cron_entry"
    else
        (crontab -l 2>/dev/null; echo "$cron_entry") | crontab -
        log_success "Janitor Bot 夜間実行設定完了 (毎日2:00AM)"
    fi
}

# 構造維持hooks設定モジュール
setup_structure_module() {
    log_step "構造維持hooks設定"
    
    local hooks_dir="$PROJECT_ROOT/.git/hooks"
    
    # 既存のpre-commitを拡張
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY-RUN] 構造維持チェックをpre-commitに追加"
    else
        # pre-commitに構造チェック追加
        cat >> "$hooks_dir/pre-commit" << 'EOF'

# 構造維持チェック
MAX_ROOT_DIRS=8
root_dir_count=$(find . -maxdepth 1 -type d ! -name ".git" ! -name "." | wc -l)

if [ "$root_dir_count" -gt $MAX_ROOT_DIRS ]; then
    echo "❌ 構造違反: ルートディレクトリが${root_dir_count}個 (上限${MAX_ROOT_DIRS})"
    exit 1
fi

# 禁止パターンチェック
forbidden_patterns=("ai-agents" "memory" "logs" "tmp" "data")
for pattern in "${forbidden_patterns[@]}"; do
    if [ -d "$pattern" ]; then
        echo "❌ 禁止パターン検出: $pattern/"
        exit 1
    fi
done
EOF
        chmod +x "$hooks_dir/pre-commit"
        log_success "構造維持チェック追加完了"
    fi
}

# ポータブル環境設定モジュール
setup_portable_module() {
    log_step "ポータブル環境設定"
    
    local platform=$(detect_platform)
    local pkg_manager=$(detect_package_manager)
    
    # システム情報保存
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY-RUN] システム情報保存"
    else
        cat > "$PROJECT_ROOT/system-info.json" << EOF
{
  "platform": "$platform",
  "package_manager": "$pkg_manager",
  "setup_date": "$(date -Iseconds)",
  "project_root": "$PROJECT_ROOT"
}
EOF
        log_success "システム情報保存完了: system-info.json"
    fi
    
    # 環境設定ファイル
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY-RUN] 環境設定ファイル作成"
    else
        cat > "$PROJECT_ROOT/.env.local" << EOF
# 統合環境設定
PROJECT_ROOT=$PROJECT_ROOT
PLATFORM=$platform
PACKAGE_MANAGER=$pkg_manager
EOF
        log_success "環境設定ファイル作成完了: .env.local"
    fi
}

# セットアップ完了報告
setup_complete_report() {
    log_step "セットアップ完了報告"
    
    echo -e "${GREEN}🎉 統合環境セットアップが完了しました！${NC}"
    echo ""
    echo "実行されたモジュール:"
    
    if [[ "$MODULE_HOOKS" == "true" ]]; then
        echo "  ✅ Git hooks設定"
    fi
    if [[ "$MODULE_STATUS" == "true" ]]; then
        echo "  ✅ 自動ステータス表示"
    fi
    if [[ "$MODULE_DEV" == "true" ]]; then
        echo "  ✅ 開発環境設定"
    fi
    if [[ "$MODULE_VALIDATION" == "true" ]]; then
        echo "  ✅ ファイル検証システム"
    fi
    if [[ "$MODULE_CRON" == "true" ]]; then
        echo "  ✅ 定期実行設定"
    fi
    if [[ "$MODULE_STRUCTURE" == "true" ]]; then
        echo "  ✅ 構造維持hooks"
    fi
    if [[ "$MODULE_PORTABLE" == "true" ]]; then
        echo "  ✅ ポータブル環境"
    fi
    
    echo ""
    echo -e "${BLUE}📋 次のステップ:${NC}"
    echo "1. Shell統合を有効化:"
    echo "   echo 'source $(pwd)/.shell_integration.zsh' >> ~/.zshrc"
    echo "   source ~/.zshrc"
    echo ""
    echo "2. 動作確認:"
    echo "   make status"
    echo "   git add . && git commit -m 'test: 統合環境セットアップ'"
    echo ""
    echo "3. 設定確認:"
    echo "   cat system-info.json"
    echo "   cat .env.local"
}

# ====== メイン処理 ======

# デフォルト値設定
DRY_RUN=false
QUIET=false
FORCE=false
MODULE_ALL=true
MODULE_HOOKS=false
MODULE_STATUS=false
MODULE_DEV=false
MODULE_VALIDATION=false
MODULE_CRON=false
MODULE_STRUCTURE=false
MODULE_PORTABLE=false

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
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -q|--quiet)
            QUIET=true
            shift
            ;;
        --force)
            FORCE=true
            shift
            ;;
        --all)
            MODULE_ALL=true
            shift
            ;;
        --hooks)
            MODULE_ALL=false
            MODULE_HOOKS=true
            shift
            ;;
        --status)
            MODULE_ALL=false
            MODULE_STATUS=true
            shift
            ;;
        --dev)
            MODULE_ALL=false
            MODULE_DEV=true
            shift
            ;;
        --validation)
            MODULE_ALL=false
            MODULE_VALIDATION=true
            shift
            ;;
        --cron)
            MODULE_ALL=false
            MODULE_CRON=true
            shift
            ;;
        --structure)
            MODULE_ALL=false
            MODULE_STRUCTURE=true
            shift
            ;;
        --portable)
            MODULE_ALL=false
            MODULE_PORTABLE=true
            shift
            ;;
        *)
            log_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# --all が選択されている場合、全モジュールを有効にする
if [[ "$MODULE_ALL" == "true" ]]; then
    MODULE_HOOKS=true
    MODULE_STATUS=true
    MODULE_DEV=true
    MODULE_VALIDATION=true
    MODULE_CRON=true
    MODULE_STRUCTURE=true
    MODULE_PORTABLE=true
fi

# メイン処理開始
main() {
    echo -e "${CYAN}🚀 統合環境セットアップスクリプト v$SCRIPT_VERSION${NC}"
    echo "=============================================="
    echo ""
    echo "プロジェクトルート: $PROJECT_ROOT"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        echo -e "${YELLOW}[DRY-RUN MODE] 実際の操作は実行されません${NC}"
        echo ""
    fi
    
    # 前提条件チェック
    if [[ ! -f "$PROJECT_ROOT/.claude/settings.json" ]]; then
        log_error "プロジェクトルートで実行してください（.claude/settings.json が見つかりません）"
        exit 1
    fi
    
    # モジュール実行
    if [[ "$MODULE_HOOKS" == "true" ]]; then
        setup_hooks_module
    fi
    
    if [[ "$MODULE_STATUS" == "true" ]]; then
        setup_status_module
    fi
    
    if [[ "$MODULE_DEV" == "true" ]]; then
        setup_dev_module
    fi
    
    if [[ "$MODULE_VALIDATION" == "true" ]]; then
        setup_validation_module
    fi
    
    if [[ "$MODULE_CRON" == "true" ]]; then
        setup_cron_module
    fi
    
    if [[ "$MODULE_STRUCTURE" == "true" ]]; then
        setup_structure_module
    fi
    
    if [[ "$MODULE_PORTABLE" == "true" ]]; then
        setup_portable_module
    fi
    
    # 完了報告
    setup_complete_report
    
    if [[ "$DRY_RUN" == "false" ]]; then
        # 統合完了マーク
        touch "$PROJECT_ROOT/.unified-env-configured"
        log_success "統合環境セットアップが完了しました"
    else
        log_info "DRY-RUN モードで実行されました。実際のセットアップは行われていません。"
    fi
}

# スクリプト直接実行時のみmainを実行
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi