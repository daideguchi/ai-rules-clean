#!/bin/bash
set -euo pipefail
# Hooks付きプロジェクト起動

export HOOKS_ENABLED=true
export AUDIO_HOOKS_CONFIG="src/hooks/hooks-config.json"

echo "🔊 Audio Hooks System 有効化"
echo "📝 ファイル操作ログ: FILE_OPERATIONS_LOG.md"
echo "🤖 AI相互作用ログ: AI_INTERACTIONS_LOG.md"
echo ""

# プロジェクト起動
exec "$@"
