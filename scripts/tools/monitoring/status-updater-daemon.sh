#!/bin/bash

# =============================================================================
# [LEGACY WRAPPER] status-updater-daemon.sh
# 
# このスクリプトは unified-monitoring-tool.py に統合されました。
# Phase 4 統合完了 - レガシー互換性のためのwrapperスクリプト
# 
# 新しい使用方法:
#   scripts/tools/unified-monitoring-tool.py daemon start
#   scripts/tools/unified-monitoring-tool.py daemon stop
#   scripts/tools/unified-monitoring-tool.py daemon status
# =============================================================================

echo "⚠️  [LEGACY] status-updater-daemon.sh は統合されました"
echo "📦 unified-monitoring-tool.py daemon に移行してください"
echo ""
echo "🔄 自動転送中..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 引数なしの場合はstartと見なす
action="${1:-start}"
shift || true

exec python3 "$SCRIPT_DIR/../unified-monitoring-tool.py" daemon "$action" "$@"

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOCK_FILE="$PROJECT_ROOT/runtime/status-updater.lock"
PID_FILE="$PROJECT_ROOT/runtime/status-updater.pid"

# Check if already running
if [[ -f "$PID_FILE" ]] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
    echo "Status updater already running (PID: $(cat "$PID_FILE"))"
    exit 1
fi

# Create lock and PID files
echo $$ > "$PID_FILE"
touch "$LOCK_FILE"

# Cleanup on exit
cleanup() {
    rm -f "$LOCK_FILE" "$PID_FILE"
    exit 0
}
trap cleanup EXIT INT TERM

echo "🔄 Status updater daemon started (PID: $$)"

cd "$PROJECT_ROOT"

# Update every 5 minutes while files are being modified
while true; do
    if [[ -f "scripts/auto-status-display.py" ]]; then
        # Check if any relevant files changed in last 5 minutes
        if find runtime/ scripts/ docs/ src/ -name "*.json" -o -name "*.py" -o -name "*.md" -newer "$LOCK_FILE" -print -quit | grep -q .; then
            python3 scripts/auto-status-display.py > /dev/null 2>&1 || true
            touch "$LOCK_FILE"
        fi
    fi
    
    sleep 300  # 5 minutes
done
