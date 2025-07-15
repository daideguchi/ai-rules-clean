#!/bin/bash

# =============================================================================
# [DEPRECATED] complete-system-test.sh
# 
# このスクリプトは unified-test-suite.sh に統合されました。
# 段階的移行のためのwrapperスクリプトです。
# 
# 新しい使用方法:
#   scripts/tools/testing/unified-test-suite.sh --system
# =============================================================================

echo "⚠️  [DEPRECATED] complete-system-test.sh は非推奨です"
echo "📦 unified-test-suite.sh --system に移行してください"
echo ""
echo "🔄 自動転送中..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/unified-test-suite.sh" --system "$@"