#!/usr/bin/env bash

# =============================================================================
# [LEGACY WRAPPER] instruction-checklist-v2.sh
# 
# このスクリプトは unified-validation-tool.py に統合されました。
# Phase 6 統合完了 - レガシー互換性のためのwrapperスクリプト
# 
# 新しい使用方法:
#   scripts/tools/unified-validation-tool.py instruction-checklist
# =============================================================================

echo "⚠️  [LEGACY] instruction-checklist-v2.sh は統合されました"
echo "📦 unified-validation-tool.py instruction-checklist に移行してください"
echo ""
echo "🔄 自動転送中..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# オプション引数変換
args=()
for arg in "$@"; do
    case "$arg" in
        --timeout=*)
            timeout="${arg#*=}"
            args+=("--timeout" "$timeout")
            ;;
        *)
            args+=("$arg")
            ;;
    esac
done

exec python3 "$SCRIPT_DIR/../unified-validation-tool.py" instruction-checklist "${args[@]}"

# ----------- 設定 ------------------------------------------------------------
readonly VERSION="2.0"
readonly DEFAULT_TIMEOUT=300            # 5分検索のタイムアウト
readonly MAX_RETRY=3                   # 入力リトライ回数
readonly LOG_DIR="${LOG_DIR:-runtime/instruction_logs}"
readonly TIMESTAMP="$(date '+%Y%m%d_%H%M%S')"

# ----------- グローバル変数 -------------------------------------------------
PROJECT_ROOT=""
LOG_FILE=""
INSTRUCTION_TYPE=""
KEYWORD=""
PHASE_STATUS=()

# ----------- ヘルパ関数 ------------------------------------------------------
die() { 
    echo "💥 エラー: $*" >&2
    echo "$(date '+%Y-%m-%d %H:%M:%S'): ERROR: $*" >> "$LOG_FILE"
    exit 1
}

log() { 
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] $*"
    echo "$msg"
    [[ -n "$LOG_FILE" ]] && echo "$msg" >> "$LOG_FILE"
}

success() {
    local msg="✅ $*"
    echo "$msg"
    [[ -n "$LOG_FILE" ]] && echo "$(date '+%Y-%m-%d %H:%M:%S'): SUCCESS: $*" >> "$LOG_FILE"
}

# ----------- プロジェクトルート自動検出 --------------------------------------
detect_project_root() {
    # 1. 環境変数
    if [[ -n "${CODING_RULE2_ROOT:-}" ]]; then
        PROJECT_ROOT="$CODING_RULE2_ROOT"
    # 2. git root
    elif git rev-parse --show-toplevel &>/dev/null; then
        PROJECT_ROOT="$(git rev-parse --show-toplevel)"
    # 3. スクリプトの2階層上
    else
        PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
    fi
    
    [[ -d "$PROJECT_ROOT" ]] || die "プロジェクトルートが見つかりません"
    [[ -f "$PROJECT_ROOT/Index.md" ]] || die "Index.mdが見つかりません。正しいプロジェクトルートですか？"
}

# ----------- ログ初期化 ------------------------------------------------------
init_logging() {
    mkdir -p "$PROJECT_ROOT/$LOG_DIR"
    LOG_FILE="$PROJECT_ROOT/$LOG_DIR/checklist_${TIMESTAMP}.log"
    
    {
        echo "========================================="
        echo "指示対応チェックリスト v${VERSION}"
        echo "開始時刻: $(date)"
        echo "プロジェクト: $PROJECT_ROOT"
        echo "========================================="
    } >> "$LOG_FILE"
    
    log "ログファイル: $LOG_FILE"
}

# ----------- リトライ機能付き入力 --------------------------------------------
prompt_with_retry() {
    local prompt_msg="$1"
    local validate_regex="${2:-.*}"  # デフォルトは任意
    local value=""
    local retry=0
    
    while [[ $retry -lt $MAX_RETRY ]]; do
        read -r -p "$prompt_msg" value || true
        
        if [[ -n "$value" ]] && [[ "$value" =~ $validate_regex ]]; then
            echo "$value"
            return 0
        fi
        
        ((retry++))
        if [[ $retry -lt $MAX_RETRY ]]; then
            echo "⚠️  無効な入力です。再入力してください（残り $((MAX_RETRY - retry))回）"
        fi
    done
    
    die "有効な入力が得られませんでした: $prompt_msg"
}

# ----------- Phase 1: 指示分類 -----------------------------------------------
phase1_classify() {
    log "【Phase 1】指示分類開始"
    
    echo ""
    echo "【Phase 1】指示分類（30秒）"
    echo "----------------------------------------"
    echo "指示タイプを選択してください:"
    echo "1) 情報検索系（〜について教えて）"
    echo "2) コード修正系（〜を修正/実装）"
    echo "3) 設計系（〜の設計/アーキテクチャ）"
    echo "4) 運用系（〜を実行/セットアップ）"
    
    INSTRUCTION_TYPE=$(prompt_with_retry "選択 [1-4]: " "^[1-4]$")
    
    case $INSTRUCTION_TYPE in
        1) TYPE_NAME="情報検索系"; PRIORITY_DIR="docs" ;;
        2) TYPE_NAME="コード修正系"; PRIORITY_DIR="src" ;;
        3) TYPE_NAME="設計系"; PRIORITY_DIR="docs/01_concepts" ;;
        4) TYPE_NAME="運用系"; PRIORITY_DIR="docs/03_processes" ;;
    esac
    
    success "タイプ: $TYPE_NAME"
    PHASE_STATUS+=("Phase1: COMPLETED - $TYPE_NAME")
    log "Phase 1 完了: $TYPE_NAME"
}

# ----------- Phase 2: インベントリ確認 ---------------------------------------
phase2_inventory() {
    log "【Phase 2】インベントリ確認開始"
    
    echo ""
    echo "【Phase 2】インベントリ確認（2分）"
    echo "----------------------------------------"
    
    KEYWORD=$(prompt_with_retry "検索キーワードを入力: " ".+")
    
    echo ""
    echo "📄 Index.md確認中..."
    
    # Index.md検索（タイムアウト付き）
    if timeout 10 grep -i "$KEYWORD" "$PROJECT_ROOT/Index.md" > /tmp/index_result.txt 2>&1; then
        echo "Index.mdでの検索結果:"
        cat /tmp/index_result.txt
    else
        echo "❌ Index.mdに該当なし"
    fi
    
    # 優先ディレクトリ確認
    echo ""
    echo "📚 優先ディレクトリ確認: $PRIORITY_DIR"
    if [[ -d "$PROJECT_ROOT/$PRIORITY_DIR" ]]; then
        echo "ファイル一覧:"
        ls -la "$PROJECT_ROOT/$PRIORITY_DIR" 2>/dev/null | head -10 || echo "アクセスエラー"
    else
        echo "⚠️  優先ディレクトリが存在しません"
    fi
    
    # DB/ログ確認
    echo ""
    echo "🗄️  DB/ログ確認が必要ですか？"
    echo "キーワード: 最新/現在/統計/エラー/障害/状態/設定"
    
    local need_db=$(prompt_with_retry "DB/ログ確認が必要？ [y/n]: " "^[yn]$")
    
    if [[ "$need_db" == "y" ]]; then
        echo ""
        echo "📊 runtime/確認:"
        ls -lat "$PROJECT_ROOT/runtime/" 2>/dev/null | head -5 || echo "runtimeディレクトリなし"
        
        echo ""
        echo "最新ログ:"
        find "$PROJECT_ROOT/runtime/" -name "*.log" -mtime -1 2>/dev/null | head -3 || echo "ログなし"
    fi
    
    PHASE_STATUS+=("Phase2: COMPLETED - Keyword: $KEYWORD")
    log "Phase 2 完了: キーワード=$KEYWORD"
}

# ----------- Phase 3: 5分検索実行 --------------------------------------------
phase3_search() {
    log "【Phase 3】5分検索実行開始"
    
    echo ""
    echo "【Phase 3】5分検索実行（5分）"
    echo "----------------------------------------"
    
    local search_script="$PROJECT_ROOT/scripts/utilities/5min-search.sh"
    local search_log="/tmp/search_${TIMESTAMP}.log"
    
    if [[ ! -x "$search_script" ]]; then
        echo "⚠️  検索スクリプトが見つかりません: $search_script"
        echo "代替検索を実行..."
        
        # 代替検索実装
        {
            echo "🔍 代替検索: $KEYWORD"
            echo "ドキュメント検索:"
            find "$PROJECT_ROOT/docs" -name "*.md" -exec grep -l "$KEYWORD" {} \; 2>/dev/null | head -10
            echo ""
            echo "スクリプト検索:"
            find "$PROJECT_ROOT/scripts" -name "*.sh" -exec grep -l "$KEYWORD" {} \; 2>/dev/null | head -10
            echo ""
            echo "ソースコード検索:"
            find "$PROJECT_ROOT/src" -name "*.py" -exec grep -l "$KEYWORD" {} \; 2>/dev/null | head -10
        } | tee "$search_log"
    else
        echo "🔍 検索実行中..."
        timeout "$DEFAULT_TIMEOUT" "$search_script" "$KEYWORD" > "$search_log" 2>&1 || {
            echo "⚠️  検索タイムアウト（${DEFAULT_TIMEOUT}秒）"
        }
        cat "$search_log"
    fi
    
    # 検索結果評価
    local found_count=$(grep -E "(関連|検索結果|found)" "$search_log" 2>/dev/null | wc -l)
    
    echo ""
    echo "📊 検索結果評価:"
    if [[ $found_count -ge 3 ]]; then
        success "回答可能 - 十分な情報が見つかりました（${found_count}件）"
    else
        echo "⚠️  情報不足 - 追加調査が必要です（${found_count}件）"
    fi
    
    echo "検索結果保存先: $search_log"
    cp "$search_log" "$PROJECT_ROOT/$LOG_DIR/search_${TIMESTAMP}.log"
    
    PHASE_STATUS+=("Phase3: COMPLETED - Results: ${found_count}")
    log "Phase 3 完了: 検索結果=${found_count}件"
}

# ----------- Phase 4: 実行計画策定 -------------------------------------------
phase4_planning() {
    log "【Phase 4】実行計画策定開始"
    
    echo ""
    echo "【Phase 4】実行計画策定"
    echo "----------------------------------------"
    echo "📝 根拠情報の整理:"
    echo ""
    
    echo "1. 参照ドキュメント:"
    local ref_doc=$(prompt_with_retry "   主要参照ファイルパス: " ".*")
    
    echo ""
    echo "2. 確定事項:"
    local confirmed=$(prompt_with_retry "   確定した内容（根拠付き）: " ".*")
    
    echo ""
    echo "3. 不明事項:"
    local unknown=$(prompt_with_retry "   追加調査が必要な内容: " ".*")
    
    # 実行計画をログに記録
    {
        echo ""
        echo "=== 実行計画 ==="
        echo "参照: $ref_doc"
        echo "確定: $confirmed"
        echo "不明: $unknown"
        echo "================"
    } >> "$LOG_FILE"
    
    PHASE_STATUS+=("Phase4: COMPLETED - Plan created")
    log "Phase 4 完了: 実行計画策定"
}

# ----------- Phase 5: 検証計画 -----------------------------------------------
phase5_verification() {
    log "【Phase 5】検証計画開始"
    
    echo ""
    echo "【Phase 5】検証計画"
    echo "----------------------------------------"
    echo "実行予定の検証:"
    echo "□ make test"
    echo "□ make lint"
    echo "□ make status"
    echo "□ 手動動作確認"
    echo ""
    
    # 実際の検証実行（オプション）
    local run_verify=$(prompt_with_retry "検証を実行しますか？ [y/n]: " "^[yn]$")
    
    if [[ "$run_verify" == "y" ]]; then
        echo ""
        echo "🧪 検証実行中..."
        
        cd "$PROJECT_ROOT"
        
        # make status（エラーでも継続）
        if timeout 30 make status &>/dev/null; then
            success "make status: OK"
        else
            echo "⚠️  make status: 失敗またはタイムアウト"
        fi
    fi
    
    PHASE_STATUS+=("Phase5: COMPLETED - Verification ready")
    log "Phase 5 完了: 検証計画確認"
}

# ----------- 最終確認 --------------------------------------------------------
final_confirmation() {
    echo ""
    echo "========================================="
    echo "📊 チェックリスト完了確認"
    echo "========================================="
    
    for status in "${PHASE_STATUS[@]}"; do
        echo "✅ $status"
    done
    
    echo ""
    echo "⚠️  推測回答の防止確認:"
    local confirm=$(prompt_with_retry "すべての判断に根拠がありますか？ [y/n]: " "^[yn]$")
    
    if [[ "$confirm" != "y" ]]; then
        die "根拠不足です。追加調査を実施してください。"
    fi
    
    success "チェックリスト完了！"
    echo "ログファイル: $LOG_FILE"
    
    # サマリーログ
    {
        echo ""
        echo "=== 完了サマリー ==="
        echo "キーワード: $KEYWORD"
        echo "タイプ: $TYPE_NAME"
        echo "完了時刻: $(date)"
        echo "==================="
    } >> "$LOG_FILE"
}

# ----------- メイン処理 ------------------------------------------------------
main() {
    echo "========================================="
    echo "📋 指示対応チェックリスト v${VERSION}"
    echo "========================================="
    
    # 初期化
    detect_project_root
    init_logging
    
    # エラーハンドリング設定
    trap 'echo "⚠️  中断されました" >&2; exit 130' INT TERM
    
    # 各フェーズ実行
    phase1_classify
    phase2_inventory
    phase3_search
    phase4_planning
    phase5_verification
    final_confirmation
    
    echo "========================================="
}

# 実行
main "$@"