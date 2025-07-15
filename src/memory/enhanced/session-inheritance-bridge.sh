#!/bin/bash
# 🔗 O3セッション継承ブリッジ - hooks.js 3層構造対応
# 美しいUX表示システムとの統合インターフェース

set -euo pipefail

# 設定
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MEMORY_SYSTEM_PY="${SCRIPT_DIR}/o3-memory-system.py"
UX_SYSTEM_JS="${SCRIPT_DIR}/../ui/integrated-ux-system.js"
HOOKS_JS="${SCRIPT_DIR}/../core/hooks.js"
LOG_FILE="${SCRIPT_DIR}/../../../logs/session-inheritance.log"

# ログ関数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "${LOG_FILE}"
}

# 美しいバナー表示
display_banner() {
    echo ""
    echo "════════════════════════════════════════════════════════════════════════════════"
    echo "🧠 O3セッション継承ブリッジシステム"
    echo "hooks.js 3層アーキテクチャ完全統合"
    echo "════════════════════════════════════════════════════════════════════════════════"
    echo ""
}

# hooks.jsシステム状態確認
check_hooks_integration() {
    log "🔍 hooks.jsシステム連携確認..."
    
    if [[ -f "${HOOKS_JS}" ]]; then
        # hooks.jsのO3システム状態を確認
        local hooks_status
        hooks_status=$(cd "$(dirname "${HOOKS_JS}")" && node -e "
            const hooks = require('./hooks.js');
            hooks.getO3SystemStatus().then(status => {
                console.log(JSON.stringify(status, null, 2));
            }).catch(err => {
                console.log(JSON.stringify({success: false, error: err.message}, null, 2));
            });
        " 2>/dev/null || echo '{"success": false, "error": "hooks.js execution failed"}')
        
        echo "${hooks_status}"
        return 0
    else
        log "❌ hooks.js未検出: ${HOOKS_JS}"
        return 1
    fi
}

# 統合UXシステム起動
launch_integrated_ux() {
    log "🎨 統合UXシステム起動..."
    
    if [[ -f "${UX_SYSTEM_JS}" ]]; then
        if node "${UX_SYSTEM_JS}" --no-interactive 2>&1; then
            log "✅ 統合UXシステム起動成功"
            return 0
        else
            log "❌ 統合UXシステム起動失敗"
            return 1
        fi
    else
        log "⚠️ 統合UXシステム未検出、フォールバック表示"
        return 1
    fi
}

# O3記憶システム起動
initialize_o3_memory() {
    log "🧠 O3記憶システム初期化..."
    
    if [[ -f "${MEMORY_SYSTEM_PY}" ]]; then
        local session_id="${1:-$(date +%s)}"
        
        # Python O3記憶システム呼び出し
        if python3 -c "
import sys
sys.path.append('$(dirname "${MEMORY_SYSTEM_PY}")')
from o3_memory_system import O3EnhancedMemorySystem
import asyncio
import json

async def startup_memory():
    try:
        system = O3EnhancedMemorySystem()
        context = await system.generate_startup_context('${session_id}')
        print(json.dumps(context, indent=2, ensure_ascii=False))
        return True
    except Exception as e:
        print(json.dumps({'error': str(e)}, ensure_ascii=False))
        return False

asyncio.run(startup_memory())
        " 2>/dev/null; then
            log "✅ O3記憶システム初期化成功"
            return 0
        else
            log "❌ O3記憶システム初期化失敗"
            return 1
        fi
    else
        log "⚠️ O3記憶システム未検出: ${MEMORY_SYSTEM_PY}"
        return 1
    fi
}

# フォールバック継承表示
display_fallback_inheritance() {
    log "🔄 フォールバック記憶継承表示..."
    
    cat << EOF

╔════════════════════════════════════════════════════════════════════════════════╗
║                    🧠 記憶継承システム (フォールバックモード)                    ║
╚════════════════════════════════════════════════════════════════════════════════╝

📋 セッション情報
├── 🕒 開始時刻: $(date '+%Y/%m/%d %H:%M:%S')
├── 🆔 セッションID: fallback-$(date +%s)
└── 🔄 継承モード: フォールバック

🚨 必須記憶事項
⚠️  78回のミス記録を継承し、79回目を防ぐ
⚠️  PRESIDENT役割を継続維持  
⚠️  セキュリティ関連は慎重に実装する
⚠️  ファイル作成前に必ず既存ファイルを確認する

🎯 プロジェクト継続事項
📝 AI永続記憶システム実装統括
💰 予算: \$33,000 (Phase 1)
⚙️  技術: PostgreSQL + pgvector + hooks.js
🤝 AI連携: Claude + Gemini + o3

╔════════════════════════════════════════════════════════════════════════════════╗
║                         ✅ 記憶継承準備完了                                    ║
╚════════════════════════════════════════════════════════════════════════════════╝

EOF
}

# システム診断実行
run_system_diagnostics() {
    log "🔍 システム診断実行..."
    
    echo "🔧 システム診断結果:"
    echo "├── Node.js: $(node --version 2>/dev/null || echo '未検出')"
    echo "├── Python3: $(python3 --version 2>/dev/null || echo '未検出')"
    echo "├── hooks.js: $(test -f "${HOOKS_JS}" && echo '✅ 検出済み' || echo '❌ 未検出')"
    echo "├── O3記憶システム: $(test -f "${MEMORY_SYSTEM_PY}" && echo '✅ 検出済み' || echo '❌ 未検出')"
    echo "├── 統合UXシステム: $(test -f "${UX_SYSTEM_JS}" && echo '✅ 検出済み' || echo '❌ 未検出')"
    echo "└── ログディレクトリ: $(test -d "$(dirname "${LOG_FILE}")" && echo '✅ 利用可能' || echo '❌ 未作成')"
}

# メイン実行
main() {
    local command="${1:-startup}"
    local session_id="${2:-$(date +%s)}"
    
    # ログディレクトリ作成
    mkdir -p "$(dirname "${LOG_FILE}")"
    
    log "🚀 O3セッション継承ブリッジ開始: ${command}"
    
    case "${command}" in
        "startup")
            display_banner
            
            # システム診断
            run_system_diagnostics
            echo ""
            
            # hooks.js統合確認
            if check_hooks_integration >/dev/null 2>&1; then
                log "✅ hooks.js統合確認成功"
            else
                log "⚠️ hooks.js統合失敗、フォールバックモード"
            fi
            
            # 統合UXシステム起動試行
            if launch_integrated_ux; then
                log "🎨 統合UXシステム起動成功"
            else
                log "🔄 フォールバック表示実行"
                display_fallback_inheritance
            fi
            
            # O3記憶システム初期化
            initialize_o3_memory "${session_id}" >/dev/null
            
            log "✅ セッション継承完了: ${session_id}"
            ;;
            
        "test")
            echo "🧪 システム統合テスト実行"
            run_system_diagnostics
            ;;
            
        "status")
            echo "📊 システム状態確認"
            check_hooks_integration | python3 -m json.tool 2>/dev/null || echo "hooks.js状態取得失敗"
            ;;
            
        "ux-only")
            echo "🎨 UXシステム単体起動"
            launch_integrated_ux
            ;;
            
        *)
            echo "❌ 未知のコマンド: ${command}"
            echo "利用可能: startup, test, status, ux-only"
            exit 1
            ;;
    esac
}

# 実行
main "$@"