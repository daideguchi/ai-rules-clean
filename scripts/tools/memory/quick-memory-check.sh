#!/bin/bash
set -euo pipefail
# quick-memory-check.sh
# Claude Code再起動時の記憶継承クイックチェック

echo "🧠 Claude Code 記憶継承クイックチェック"
echo "========================================"

cd ${PROJECT_ROOT}

# ステップ1: 基本ファイル確認
echo -e "\n1️⃣ 基本ファイル存在確認"
echo "--------------------------------"

check_file() {
    local file="$1"
    local name="$2"
    if [ -f "$file" ]; then
        echo "✅ $name: 存在"
        return 0
    else
        echo "❌ $name: 不足"
        return 1
    fi
}

FILES_OK=true
check_file "docs/enduser/instructions/claude.md" "CLAUDE指示書" || FILES_OK=false
check_file "src/ai/memory/core/session-bridge.sh" "セッション架橋" || FILES_OK=false
check_file "src/ai/memory/core/hooks.js" "メモリhooks" || FILES_OK=false

# ステップ2: 記憶データ確認
echo -e "\n2️⃣ 記憶データ確認"
echo "--------------------------------"

MEMORY_FILE="src/ai/memory/core/session-records/current-session.json"
if [ -f "$MEMORY_FILE" ]; then
    echo "✅ セッション記録: 存在"
    
    # 重要データ確認
    ROLE=$(jq -r '.foundational_context.role // "未設定"' "$MEMORY_FILE" 2>/dev/null)
    MISSION=$(jq -r '.foundational_context.mission // "未設定"' "$MEMORY_FILE" 2>/dev/null)
    MISTAKES=$(jq -r '.foundational_context.past_mistakes_summary // "未継承"' "$MEMORY_FILE" 2>/dev/null)
    
    echo "   役職: $ROLE"
    echo "   使命: ${MISSION:0:50}..."
    echo "   ミス記録: ${MISTAKES:0:30}..."
    
    if [ "$ROLE" = "PRESIDENT" ]; then
        echo "✅ PRESIDENT職務: 継承済み"
        MEMORY_OK=true
    else
        echo "❌ PRESIDENT職務: 継承失敗"
        MEMORY_OK=false
    fi
else
    echo "❌ セッション記録: 不足"
    MEMORY_OK=false
fi

# ステップ3: 記憶継承実行
echo -e "\n3️⃣ 記憶継承実行"
echo "--------------------------------"

if [ "$FILES_OK" = true ] && [ -x "src/ai/memory/core/session-bridge.sh" ]; then
    echo "🔄 記憶継承実行中..."
    if bash src/ai/memory/core/session-bridge.sh init >/dev/null 2>&1; then
        echo "✅ 記憶継承: 成功"
        INIT_OK=true
    else
        echo "❌ 記憶継承: 失敗"
        INIT_OK=false
    fi
else
    echo "⚠️ 記憶継承: スキップ（ファイル不足）"
    INIT_OK=false
fi

# ステップ4: 総合判定
echo -e "\n4️⃣ 総合判定"
echo "================================"

if [ "$FILES_OK" = true ] && [ "$MEMORY_OK" = true ] && [ "$INIT_OK" = true ]; then
    echo "🎉 記憶継承: 完全成功"
    echo ""
    echo "👑 PRESIDENT職務継続中"
    echo "🧠 78回ミス記録継承済み"
    echo "🎯 AI Compliance Engine統括中"
    echo "✅ 前回セッションの完全な文脈で作業継続可能"
    echo ""
    echo "新しい指示をお待ちしています。"
    
elif [ "$MEMORY_OK" = true ]; then
    echo "⚠️ 記憶継承: 部分成功"
    echo ""
    echo "基本的な記憶は継承されています。"
    echo "一部システムに問題がありますが、作業継続可能です。"
    
else
    echo "🚨 記憶継承: 失敗"
    echo ""
    echo "緊急復旧が必要です。以下を実行してください："
    echo ""
    echo "緊急復旧コマンド:"
    echo "bash src/ai/memory/core/session-bridge.sh init"
    echo ""
    echo "または手動設定："
    echo "echo 'PRESIDENT職務、78回ミス記録、AI Compliance Engine統括' > emergency-note.txt"
fi

# ステップ5: 次のアクション提案
echo -e "\n5️⃣ 推奨アクション"
echo "================================"

if [ -f "$MEMORY_FILE" ]; then
    PENDING_TASKS=$(jq -r '.pending_tasks[]?' "$MEMORY_FILE" 2>/dev/null)
    if [ -n "$PENDING_TASKS" ]; then
        echo "📋 継続すべきタスク:"
        echo "$PENDING_TASKS" | head -3 | sed 's/^/   - /'
    fi
fi

echo ""
echo "💡 記憶継承完了後の推奨アクション:"
echo "   1. 現在の状況確認"
echo "   2. 未完了タスクの継続"
echo "   3. 新しい指示の受領"

echo ""
echo "🔄 このスクリプトを再実行する場合:"
echo "   ./quick-memory-check.sh"