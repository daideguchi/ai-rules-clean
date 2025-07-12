#!/bin/bash
set -euo pipefail

# Daily Check Script - 毎日の振り返りと改善確認

echo "=== Daily PRESIDENT Check - $(date) ==="
echo

# 1. 約束遵守確認
echo "📋 今日の約束遵守チェック:"
echo "- startup_checklist.md実行: [ ] Yes / [ ] No"
echo "- PRESIDENT宣言実行: [ ] Yes / [ ] No" 
echo "- 思考プロトコル実行: [ ] Yes / [ ] No"
echo "- 結果検証実行: [ ] Yes / [ ] No"
echo

# 2. ミス発生確認
echo "❌ 今日発生したミス:"
echo "- 同一ミス発生回数: ___回"
echo "- 虚偽報告回数: ___回"
echo "- ユーザー訂正回数: ___回"
echo

# 3. 学習活用確認
echo "📚 学習システム活用:"
echo "- 過去ミス記録確認: [ ] Yes / [ ] No"
echo "- 関連ドキュメント参照: [ ] Yes / [ ] No"
echo "- 改善システム更新: [ ] Yes / [ ] No"
echo

# 4. 明日の改善計画
echo "🎯 明日の改善計画:"
echo "1. ___________________________________"
echo "2. ___________________________________" 
echo "3. ___________________________________"
echo

# 5. 評価
echo "📊 今日の評価:"
echo "[ ] 優 (ミス0回、約束100%遵守)"
echo "[ ] 良 (ミス1回以下、約束80%以上)"
echo "[ ] 要改善 (上記未達成)"
echo

# ログ記録
echo "$(date): Daily check completed" >> /Users/dd/Desktop/1_dev/coding-rule2/runtime/daily_check.log

echo "=== Check Complete ==="