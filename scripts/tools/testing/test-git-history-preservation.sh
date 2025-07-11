#!/bin/bash

# =============================================================================
# [DEPRECATED] test-git-history-preservation.sh
# 
# このスクリプトは unified-test-suite.sh に統合されました。
# 段階的移行のためのwrapperスクリプトです。
# 
# 新しい使用方法:
#   scripts/tools/testing/unified-test-suite.sh --git-history
# =============================================================================

echo "⚠️  [DEPRECATED] test-git-history-preservation.sh は非推奨です"
echo "📦 unified-test-suite.sh --git-history に移行してください"
echo ""
echo "🔄 自動転送中..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/unified-test-suite.sh" --git-history "$@"