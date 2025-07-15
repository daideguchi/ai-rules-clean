#!/bin/bash

# =============================================================================
# [DEPRECATED] setup-structure-hooks.sh
# 
# このスクリプトは setup-unified-environment.sh に統合されました。
# 段階的移行のためのwrapperスクリプトです。
# 
# 新しい使用方法:
#   scripts/automation/setup-unified-environment.sh --structure
# =============================================================================

echo "⚠️  [DEPRECATED] setup-structure-hooks.sh は非推奨です"
echo "📦 setup-unified-environment.sh --structure に移行してください"
echo ""
echo "🔄 自動転送中..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/setup-unified-environment.sh" --structure "$@"