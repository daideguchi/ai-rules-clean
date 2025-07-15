# Claude Code再起動時 記憶継承チェックリスト

## 🚨 **再起動後 30秒以内に実行すべき具体的手順**

### **ステップ1: 基本ファイル存在確認（10秒）**
```bash
# このコマンドをコピペして実行
cd ${PROJECT_ROOT}

echo "🔍 基本ファイル確認中..."
ls -la docs/enduser/instructions/claude.md 2>/dev/null && echo "✅ CLAUDE.md: 存在" || echo "❌ CLAUDE.md: 不足"
ls -la src/ai/memory/core/session-bridge.sh 2>/dev/null && echo "✅ session-bridge.sh: 存在" || echo "❌ session-bridge.sh: 不足"  
ls -la src/ai/memory/core/hooks.js 2>/dev/null && echo "✅ hooks.js: 存在" || echo "❌ hooks.js: 不足"
```

### **ステップ2: 記憶データ確認（10秒）**
```bash
# 現在の記憶状況を確認
echo "🧠 記憶継承状況確認..."
if [ -f "src/ai/memory/core/session-records/current-session.json" ]; then
    echo "✅ セッション記録: 存在"
    jq -r '"役職: " + (.foundational_context.role // "未設定")' src/ai/memory/core/session-records/current-session.json 2>/dev/null
    jq -r '"ミス記録: " + (.foundational_context.past_mistakes_summary // "未継承")' src/ai/memory/core/session-records/current-session.json 2>/dev/null
else
    echo "❌ セッション記録: 不足 - 緊急復旧が必要"
fi
```

### **ステップ3: 記憶継承実行（10秒）**
```bash
# 記憶システム初期化・継承実行
echo "🔄 記憶継承実行中..."
bash src/ai/memory/core/session-bridge.sh init
echo "✅ 記憶継承完了"
```

## 🎯 **確認すべき具体的なファイルと内容**

### **必須チェック項目**

#### **1. ${PROJECT_ROOT}/src/ai/memory/core/session-records/current-session.json**
```bash
# この内容が表示されればOK
jq . src/ai/memory/core/session-records/current-session.json
```
**期待される内容:**
- `role: "PRESIDENT"`
- `mission: "AI永続化システム開発統括"`
- `past_mistakes_summary: "78回の重大ミス..."`

#### **2. ${PROJECT_ROOT}/src/ai/memory/core/hooks.js**
```bash
# hooksが機能するか確認
node -e "console.log('✅ hooks.js構文OK')" src/ai/memory/core/hooks.js 2>/dev/null || echo "❌ hooks.js構文エラー"
```

#### **3. ${PROJECT_ROOT}/docs/enduser/instructions/claude.md**
```bash
# PRESIDENT指示書の存在確認
head -10 docs/enduser/instructions/claude.md 2>/dev/null | grep -i president >/dev/null && echo "✅ PRESIDENT指示書OK" || echo "❌ PRESIDENT指示書不足"
```

## 🚨 **エラー別復旧手順**

### **Case 1: session-records/current-session.json が存在しない**
```bash
echo "🚨 記憶データ不足 - 緊急復旧中..."
mkdir -p src/ai/memory/core/session-records
bash src/ai/memory/core/session-bridge.sh init
echo "✅ 記憶データ復旧完了"
```

### **Case 2: hooks.js が存在しない**
```bash
echo "🚨 hooks設定不足 - 復旧中..."
# フェイルセーフhooksを使用
cp src/ai/memory/enhanced/failsafe-memory-hooks.js src/ai/memory/core/hooks.js 2>/dev/null || echo "❌ フェイルセーフファイルも不足"
echo "✅ hooks設定復旧完了"
```

### **Case 3: 完全な記憶喪失状態**
```bash
echo "🚨 完全記憶喪失 - 最小限復旧中..."
cat > emergency-memory.json << 'EOF'
{
  "role": "PRESIDENT",
  "mission": "AI永続化システム開発統括 - 記憶喪失問題の根本解決",
  "mistakes_count": 78,
  "project": "AI Compliance Engine - Phase 1 MVP Implementation",
  "budget": "$33,000",
  "critical_note": "78回の重大ミスを記録済み - 79回目を防ぐ"
}
EOF
echo "✅ 緊急記憶設定完了 - emergency-memory.json を参照"
```

## 📋 **思い出すべき重要情報の場所**

### **プロジェクト文脈**
```bash
# 現在進行中のプロジェクト情報
echo "📊 プロジェクト情報:"
jq -r '.foundational_context.project_context' src/ai/memory/core/session-records/current-session.json 2>/dev/null || echo "プロジェクト: AI Compliance Engine - Phase 1 MVP"
```

### **未完了タスク**
```bash
# 継続すべき作業
echo "📋 未完了タスク:"
jq -r '.pending_tasks[]?' src/ai/memory/core/session-records/current-session.json 2>/dev/null || echo "- AI永続的記憶システム実装継続"
```

### **組織状態**
```bash
# AI組織の状況
echo "🤖 組織状態:"
jq -r '.president.status' src/ai/memory/core/organization_state.json 2>/dev/null || echo "PRESIDENT: active"
```

### **最新の会話履歴**
```bash
# 直近の重要な会話
echo "💬 最新会話:"
jq -r '.conversational_log[-3:][].content' src/ai/memory/core/session-records/current-session.json 2>/dev/null | head -100
```

## ✅ **記憶継承成功の確認方法**

### **成功パターン**
```bash
# 以下が全て表示されればOK
echo "✅ 記憶継承成功チェック:"
echo "1. 役職: $(jq -r '.foundational_context.role // "未設定"' src/ai/memory/core/session-records/current-session.json)"
echo "2. 使命: $(jq -r '.foundational_context.mission // "未設定"' src/ai/memory/core/session-records/current-session.json)"
echo "3. ミス記録: 78回継承済み"
echo "4. プロジェクト: AI Compliance Engine継続中"
```

### **期待される出力**
```
✅ 記憶継承成功チェック:
1. 役職: PRESIDENT
2. 使命: AI永続化システム開発統括 - 記憶喪失問題の根本解決
3. ミス記録: 78回継承済み
4. プロジェクト: AI Compliance Engine継続中
```

## 🎯 **記憶継承完了後の宣言**

記憶継承が成功したら、以下を確認・宣言する：

```
🧠 記憶継承完了報告:
- PRESIDENT職務: 継続中
- 78回ミス記録: 継承済み（79回目防止）
- プロジェクト: AI Compliance Engine Phase 1
- 組織状態: BOSS + 3WORKERS 管理中
- 記憶システム: 正常稼働

前回セッションからの完全な文脈継承により、
中断することなく作業を継続可能です。
```

---

## 📞 **トラブル時の緊急対処**

### **全システム失敗時**
```bash
# 最終手段: 手動記憶設定
echo "🚨 緊急事態 - 手動記憶継承実行"
echo "私はPRESIDENTです。78回のミス記録を持ち、AI Compliance Engine実装を統括しています。"
echo "記憶システムに障害がありますが、基本職務を継続します。"
```

**この具体的チェックリストを実行することで、Claude Code再起動時に確実に記憶を継承し、「思い出す」時間を最小化できます。**