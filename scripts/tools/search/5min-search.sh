#!/bin/bash
set -euo pipefail

# 5分検索スクリプト - 推測回答根絶ツール

KEYWORD="$1"

if [ -z "$KEYWORD" ]; then
    echo "使用方法: ./5min-search.sh [キーワード]"
    exit 1
fi

echo "🔍 5分検索開始: $KEYWORD"
echo "===================="
echo "開始時刻: $(date)"
echo ""

# Phase 1: Index確認 (1分)
echo "📋 Phase 1: Index.md検索 (1分)"
echo "------------------------------"
if [ -f "Index.md" ]; then
    grep -i "$KEYWORD" Index.md || echo "❌ Index.mdに該当なし"
else
    echo "❌ Index.md not found"
fi
echo ""

# Phase 2: ドキュメント検索 (2分)  
echo "📚 Phase 2: ドキュメント検索 (2分)"
echo "--------------------------------"
echo "関連ドキュメント:"
find docs/ -name "*.md" -exec grep -l "$KEYWORD" {} \; 2>/dev/null || echo "❌ 関連ドキュメントなし"

echo ""
echo "docs/00_INDEX/README.md の内容:"
if [ -f "docs/00_INDEX/README.md" ]; then
    head -20 docs/00_INDEX/README.md
else
    echo "❌ docs index not found"
fi
echo ""

# Phase 3: スクリプト・コード検索 (1分)
echo "🔧 Phase 3: スクリプト・コード検索 (1分)"
echo "---------------------------------------"
echo "関連スクリプト:"
find scripts/ -name "*$KEYWORD*" 2>/dev/null || echo "❌ 関連スクリプトなし"

echo ""
echo "関連ソースコード:"
find src/ -name "*.py" -exec grep -l "$KEYWORD" {} \; 2>/dev/null || echo "❌ 関連ソースコードなし"
echo ""

# Phase 4: 実行時データ確認 (1分)
echo "📊 Phase 4: 実行時データ確認 (1分)"
echo "--------------------------------"
echo "関連ログ・データ:"
find runtime/ -name "*$KEYWORD*" -o -name "*.log" 2>/dev/null | head -3 || echo "❌ 関連データなし"

echo ""
echo "最新の実行時データ:"
ls -lat runtime/ 2>/dev/null | head -5 || echo "❌ runtimeディレクトリなし"

echo ""
echo "===================="
echo "✅ 5分検索完了"
echo "終了時刻: $(date)"
echo ""

# 結果評価
echo "🎯 検索結果評価:"
FOUND_DOCS=$(find docs/ -name "*.md" -exec grep -l "$KEYWORD" {} \; 2>/dev/null | wc -l)
FOUND_SCRIPTS=$(find scripts/ -name "*$KEYWORD*" 2>/dev/null | wc -l)
FOUND_CODE=$(find src/ -name "*.py" -exec grep -l "$KEYWORD" {} \; 2>/dev/null | wc -l)

echo "- 関連ドキュメント: ${FOUND_DOCS}個"
echo "- 関連スクリプト: ${FOUND_SCRIPTS}個"  
echo "- 関連ソースコード: ${FOUND_CODE}個"

TOTAL_FOUND=$((FOUND_DOCS + FOUND_SCRIPTS + FOUND_CODE))

if [ $TOTAL_FOUND -ge 3 ]; then
    echo "✅ 回答可能 - 十分な情報が見つかりました"
else
    echo "⚠️  情報不足 - 推測回答禁止、追加調査が必要"
fi

echo "===================="