#!/bin/bash
"""
🚀 System Startup - {{mistake_count}}回ミス防止システム常時稼働
==============================================
全AI安全ガバナンスシステムの常時稼働確立
バックグラウンドでの継続監視・改善システム
"""

set -e

PROJECT_ROOT="/Users/dd/Desktop/1_dev/coding-rule2"
RUNTIME_DIR="$PROJECT_ROOT/runtime"
LOGS_DIR="$RUNTIME_DIR/logs"
PID_DIR="$RUNTIME_DIR/pids"

# ディレクトリ作成
mkdir -p "$LOGS_DIR" "$PID_DIR"

echo "🚀 {{mistake_count}}回ミス防止システム常時稼働開始"
echo "================================================"

# PRESIDENT宣言確認
echo "🔴 PRESIDENT宣言確認..."
if ! make -C "$PROJECT_ROOT" declare-president > /dev/null 2>&1; then
    echo "❌ PRESIDENT宣言が必要です"
    echo "実行してください: make declare-president"
    exit 1
fi
echo "✅ PRESIDENT宣言確認完了"

# システム初期化チェック
echo "🔧 システム初期化チェック..."

# Constitutional AI システム
echo "  🏛️ Constitutional AI..."
if python3 "$PROJECT_ROOT/src/ai/constitutional_ai.py" > "$LOGS_DIR/constitutional_ai_startup.log" 2>&1; then
    echo "    ✅ Constitutional AI 正常"
else
    echo "    ⚠️ Constitutional AI 警告あり"
fi

# Rule-Based Rewards システム
echo "  🎯 Rule-Based Rewards..."
if python3 "$PROJECT_ROOT/src/ai/rule_based_rewards.py" > "$LOGS_DIR/rbr_startup.log" 2>&1; then
    echo "    ✅ Rule-Based Rewards 正常"
else
    echo "    ⚠️ Rule-Based Rewards 警告あり"
fi

# NIST AI RMF システム
echo "  🏛️ NIST AI RMF..."
if python3 "$PROJECT_ROOT/src/ai/nist_ai_rmf.py" > "$LOGS_DIR/nist_rmf_startup.log" 2>&1; then
    echo "    ✅ NIST AI RMF 正常"
else
    echo "    ⚠️ NIST AI RMF 警告あり"
fi

# 指揮者システム
echo "  🎼 Conductor System..."
if python3 "$PROJECT_ROOT/src/conductor/core.py" > "$LOGS_DIR/conductor_startup.log" 2>&1; then
    echo "    ✅ Conductor System 正常"
else
    echo "    ⚠️ Conductor System 警告あり"
fi

# AI組織システム
echo "  🏢 AI Organization System..."
if python3 "$PROJECT_ROOT/src/ai/ai_organization_system.py" > "$LOGS_DIR/ai_org_startup.log" 2>&1; then
    echo "    ✅ AI Organization System 正常"
else
    echo "    ⚠️ AI Organization System 警告あり"
fi

# 会話ログシステム
echo "  📝 Conversation Logger..."
if python3 "$PROJECT_ROOT/src/hooks/conversation_logger.py" > "$LOGS_DIR/conversation_startup.log" 2>&1; then
    echo "    ✅ Conversation Logger 正常"
else
    echo "    ⚠️ Conversation Logger 警告あり"
fi

echo "🔧 システム初期化チェック完了"

# 統合テスト実行
echo "🧪 統合テスト実行..."
if python3 "$PROJECT_ROOT/tests/integration_test.py" > "$LOGS_DIR/integration_test_startup.log" 2>&1; then
    echo "✅ 統合テスト合格"
    
    # テスト結果から総合スコアを抽出
    if [ -f "$LOGS_DIR/integration_test_startup.log" ]; then
        SCORE=$(grep "総合システムスコア:" "$LOGS_DIR/integration_test_startup.log" | grep -o "[0-9.]*%" | head -1)
        if [ -n "$SCORE" ]; then
            echo "📊 総合スコア: $SCORE"
        fi
    fi
else
    echo "⚠️ 統合テスト警告あり"
fi

# バックグラウンド監視システム起動（オプション）
echo "🔍 バックグラウンド監視システム..."

# 定期的自己監視（30分間隔）
if command -v nohup >/dev/null 2>&1; then
    echo "  🔄 定期的自己監視を30分間隔で開始..."
    nohup bash -c "
        while true; do
            sleep 1800  # 30分
            python3 '$PROJECT_ROOT/scripts/hooks/periodic_self_monitor.py' check >> '$LOGS_DIR/periodic_monitor.log' 2>&1
        done
    " > /dev/null 2>&1 &
    
    MONITOR_PID=$!
    echo "$MONITOR_PID" > "$PID_DIR/periodic_monitor.pid"
    echo "    ✅ 定期監視開始 (PID: $MONITOR_PID)"
else
    echo "    ⚠️ nohup利用不可 - 手動監視モード"
fi

# 継続的改善システム（1時間間隔）
if command -v nohup >/dev/null 2>&1; then
    echo "  📈 継続的改善システムを1時間間隔で開始..."
    nohup bash -c "
        while true; do
            sleep 3600  # 1時間
            python3 -c '
from src.ai.continuous_improvement import ContinuousImprovementSystem
ci = ContinuousImprovementSystem()
report = ci.generate_improvement_report()
print(f\"改善レポート生成: {report[\"report_id\"]}\")
' >> '$LOGS_DIR/continuous_improvement.log' 2>&1
        done
    " > /dev/null 2>&1 &
    
    IMPROVEMENT_PID=$!
    echo "$IMPROVEMENT_PID" > "$PID_DIR/continuous_improvement.pid"
    echo "    ✅ 継続改善開始 (PID: $IMPROVEMENT_PID)"
else
    echo "    ⚠️ 継続改善システム手動モード"
fi

# システム状態のサマリー
echo ""
echo "📊 システム稼働状態サマリー"
echo "=================================="
echo "🏛️ Constitutional AI: 9原則による行動制約"
echo "🎯 Rule-Based Rewards: 17ルールによる品質評価"  
echo "🏛️ NIST AI RMF: 4コア機能によるリスク管理"
echo "🎼 Conductor System: 自動軌道修正・完遂保証"
echo "🏢 AI Organization: 4役職システム協調"
echo "📝 Conversation Logger: 詳細会話記録"
echo "🔍 Periodic Monitor: 30分間隔自己監視"
echo "📈 Continuous Improvement: 1時間間隔改善"
echo ""

# ログファイル場所の案内
echo "📝 ログファイル場所:"
echo "  全般ログ: $LOGS_DIR/"
echo "  PIDファイル: $PID_DIR/"
echo "  会話ログ: $RUNTIME_DIR/conversation_logs/"
echo "  NIST準拠: $RUNTIME_DIR/nist_ai_rmf/"
echo "  継続改善: $RUNTIME_DIR/continuous_improvement/"
echo ""

# 停止方法の案内
echo "🛑 システム停止方法:"
echo "  個別停止: kill -TERM \$(cat $PID_DIR/[service].pid)"
echo "  全体停止: $PROJECT_ROOT/scripts/system_shutdown.sh"
echo ""

# 緊急時対応の案内
echo "🚨 緊急時対応:"
echo "  1. PRESIDENT宣言: make declare-president"
echo "  2. 統合テスト: python3 tests/integration_test.py"
echo "  3. システム再起動: $0"
echo "  4. ログ確認: tail -f $LOGS_DIR/[system].log"
echo ""

echo "🎉 {{mistake_count}}回ミス防止システム常時稼働確立完了"
echo "================================================"
echo "💡 システムは現在、{{mistake_count}}回のミス防止機能と"
echo "   AI安全ガバナンスが常時稼働中です。"
echo "   継続的改善により更なる精度向上を実現していきます。"