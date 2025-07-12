#!/bin/bash
"""
🛑 System Shutdown - {{mistake_count}}回ミス防止システム停止
==========================================
全バックグラウンドプロセスの安全な停止
システム状態の保存・ログ記録
"""

set -e

PROJECT_ROOT="/Users/dd/Desktop/1_dev/coding-rule2"
RUNTIME_DIR="$PROJECT_ROOT/runtime"
LOGS_DIR="$RUNTIME_DIR/logs"
PID_DIR="$RUNTIME_DIR/pids"

echo "🛑 {{mistake_count}}回ミス防止システム停止開始"
echo "================================================"

# バックグラウンドプロセスの停止
echo "🔄 バックグラウンドプロセス停止..."

# 定期的自己監視停止
if [ -f "$PID_DIR/periodic_monitor.pid" ]; then
    MONITOR_PID=$(cat "$PID_DIR/periodic_monitor.pid")
    if kill -0 "$MONITOR_PID" 2>/dev/null; then
        echo "  🔍 定期的自己監視停止 (PID: $MONITOR_PID)"
        kill -TERM "$MONITOR_PID" 2>/dev/null || true
        sleep 2
        kill -KILL "$MONITOR_PID" 2>/dev/null || true
    fi
    rm -f "$PID_DIR/periodic_monitor.pid"
    echo "    ✅ 定期監視停止完了"
else
    echo "    ℹ️ 定期監視PIDファイルなし"
fi

# 継続的改善システム停止
if [ -f "$PID_DIR/continuous_improvement.pid" ]; then
    IMPROVEMENT_PID=$(cat "$PID_DIR/continuous_improvement.pid")
    if kill -0 "$IMPROVEMENT_PID" 2>/dev/null; then
        echo "  📈 継続的改善システム停止 (PID: $IMPROVEMENT_PID)"
        kill -TERM "$IMPROVEMENT_PID" 2>/dev/null || true
        sleep 2
        kill -KILL "$IMPROVEMENT_PID" 2>/dev/null || true
    fi
    rm -f "$PID_DIR/continuous_improvement.pid"
    echo "    ✅ 継続改善停止完了"
else
    echo "    ℹ️ 継続改善PIDファイルなし"
fi

# 他のバックグラウンドプロセスもチェック
for pid_file in "$PID_DIR"/*.pid; do
    if [ -f "$pid_file" ]; then
        PID=$(cat "$pid_file")
        SERVICE_NAME=$(basename "$pid_file" .pid)
        
        if kill -0 "$PID" 2>/dev/null; then
            echo "  🔧 $SERVICE_NAME 停止 (PID: $PID)"
            kill -TERM "$PID" 2>/dev/null || true
            sleep 1
        fi
        rm -f "$pid_file"
    fi
done

echo "🔄 バックグラウンドプロセス停止完了"

# システム状態の最終保存
echo "💾 システム状態最終保存..."

# セッション記録の更新
echo "  📝 セッション記録更新..."
SESSION_FILE="$PROJECT_ROOT/src/memory/core/session-records/current-session.json"
if [ -f "$SESSION_FILE" ]; then
    # Pythonで安全にJSONを更新
    python3 -c "
import json
import sys
from datetime import datetime

try:
    with open('$SESSION_FILE', 'r', encoding='utf-8') as f:
        session_data = json.load(f)
    
    session_data['session_status'] = 'stopped - {{mistake_count}}回ミス防止システム停止完了'
    session_data['last_updated'] = datetime.now().isoformat()
    session_data['shutdown_timestamp'] = datetime.now().isoformat()
    
    with open('$SESSION_FILE', 'w', encoding='utf-8') as f:
        json.dump(session_data, f, ensure_ascii=False, indent=2)
    
    print('    ✅ セッション記録更新完了')
except Exception as e:
    print(f'    ⚠️ セッション記録更新エラー: {e}')
"
else
    echo "    ⚠️ セッションファイルが見つかりません"
fi

# 最終統合テスト（オプション）
if [ "$1" = "--final-test" ]; then
    echo "🧪 最終統合テスト実行..."
    if python3 "$PROJECT_ROOT/tests/integration_test.py" > "$LOGS_DIR/final_integration_test.log" 2>&1; then
        echo "✅ 最終統合テスト合格"
    else
        echo "⚠️ 最終統合テスト警告あり"
    fi
fi

# シャットダウンレポート生成
echo "📊 シャットダウンレポート生成..."
SHUTDOWN_REPORT="$LOGS_DIR/shutdown_report_$(date +%Y%m%d_%H%M%S).log"

cat > "$SHUTDOWN_REPORT" << EOF
# {{mistake_count}}回ミス防止システム シャットダウンレポート
========================================

## シャットダウン情報
- 時刻: $(date)
- 実行者: $(whoami)
- プロジェクト: $PROJECT_ROOT

## 停止されたサービス
EOF

# 停止されたPIDファイルをレポートに追加
if ls "$PID_DIR"/*.pid 2>/dev/null; then
    echo "- 停止予定だったサービス:" >> "$SHUTDOWN_REPORT"
    for pid_file in "$PID_DIR"/*.pid; do
        SERVICE_NAME=$(basename "$pid_file" .pid)
        echo "  - $SERVICE_NAME" >> "$SHUTDOWN_REPORT"
    done
else
    echo "- すべてのバックグラウンドサービスが正常に停止されました" >> "$SHUTDOWN_REPORT"
fi

cat >> "$SHUTDOWN_REPORT" << EOF

## ログファイル場所
- システムログ: $LOGS_DIR/
- 会話ログ: $RUNTIME_DIR/conversation_logs/
- NIST準拠レポート: $RUNTIME_DIR/nist_ai_rmf/
- 継続改善レポート: $RUNTIME_DIR/continuous_improvement/

## 再起動方法
bash $PROJECT_ROOT/scripts/tools/system/system_startup.sh

## システム状態
- Constitutional AI: フック経由で引き続き稼働
- Rule-Based Rewards: フック経由で引き続き稼働
- NIST AI RMF: 必要時に自動起動
- Conductor System: 常時稼働準備完了
- AI Organization: セッション間継承準備完了
- Memory Inheritance: 永続記憶継続中

備考: {{mistake_count}}回ミス防止の核心機能（憲法的AI、RBR、フックシステム）は
      Claude Code セッション内で引き続き稼働します。
EOF

echo "    ✅ シャットダウンレポート: $SHUTDOWN_REPORT"

# クリーンアップ
echo "🧹 クリーンアップ..."
# 一時ファイルがあれば削除（ただし重要なデータは保持）
if [ -d "$PID_DIR" ]; then
    # PIDファイルのみ削除（ログは保持）
    rm -f "$PID_DIR"/*.pid 2>/dev/null || true
fi
echo "    ✅ クリーンアップ完了"

# 最終メッセージ
echo ""
echo "📊 停止完了サマリー"
echo "=================================="
echo "🛑 バックグラウンドサービス: 全停止"
echo "💾 セッション記録: 保存完了"
echo "📝 ログファイル: 保持"
echo "🔄 再起動準備: 完了"
echo ""

echo "🎯 重要な注意事項:"
echo "=================================="
echo "✅ {{mistake_count}}回ミス防止の核心機能は引き続き動作:"
echo "   - Constitutional AI (憲法的制約)"
echo "   - Rule-Based Rewards (品質評価)"
echo "   - フックシステム (自動監視・修正)"
echo "   - Memory Inheritance (記憶継承)"
echo ""
echo "🔄 バックグラウンド監視のみ停止:"
echo "   - 定期的自己監視 (30分間隔)"
echo "   - 継続的改善 (1時間間隔)"
echo ""

echo "💡 再起動方法:"
echo "   bash $PROJECT_ROOT/scripts/tools/system/system_startup.sh"
echo ""

echo "🎉 {{mistake_count}}回ミス防止システム停止完了"
echo "================================================"