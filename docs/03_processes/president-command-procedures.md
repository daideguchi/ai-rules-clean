# 🎯 PRESIDENT指揮者 - 絶対遵守手順書

**作成**: 2025-07-08T00:50:00+09:00  
**権限**: PRESIDENT最高指揮権  
**状態**: 厳格実行必須

## 🚨 重要ファイル削除時の絶対ルール

### **削除前必須手順**
```bash
# 1. 他AI確認（必須）
gemini -p "このファイル削除して大丈夫？: [ファイルパス] - 内容確認して安全性判定"

# 2. バックアップ作成（必須）
cp [削除対象] [削除対象].backup.$(date +%Y%m%d_%H%M%S)

# 3. 削除実行
rm [削除対象]
```

## 📋 セッション開始時の絶対手順

### **1. PRESIDENT立ち上げフロー確認**
- [ ] `Index.md` - 全体マップ確認
- [ ] `startup_checklist.md` - セッション開始必須チェック  
- [ ] `docs/enduser/instructions/claude.md` - PRESIDENT指示書確認
- [ ] `.cursor/rules` - Cursor設定確認

### **2. 要件定義・仕様書確認（最重要）**
- [ ] `docs/PROJECT_STRUCTURE.md` - プロジェクト構造
- [ ] `docs/00_INDEX/README.md` - ドキュメント案内
- [ ] 該当作業の仕様書確認

### **3. 現在タスク状況確認**
- [ ] `TodoRead` - 進行中タスク確認
- [ ] `runtime/current-tasks.md` - 現在の作業状況

## 🎯 AI組織起動コマンド別処理

### **A. AI組織起動コマンド入力時**
```bash
make run-president
# または
scripts/start-ai-workers
```
**処理フロー:**
1. 4画面tmuxセッション起動
2. PRESIDENT + 3WORKER画面構成
3. 各画面に専用指示書配信
4. 連携体制確立

### **B. PRESIDENT単独起動コマンド入力時**
```bash
claude --dangerously-skip-permissions
# または  
scripts/start-president
```
**処理フロー:**
1. PRESIDENT宣言実行
2. 単独指揮体制確立
3. フック確認・有効化
4. 作業継続準備完了

### **C. 立ち上げ後準備完了まで**
1. **PRESIDENT.md確認** - 役割・権限認識
2. **Cursor Rules確認** - 開発ルール認識  
3. **現在状況把握** - 進行中タスク確認
4. **準備完了宣言** - 指揮開始可能状態

## 🔧 Gemini CLI正しい使用法

```bash
# ❌ 間違い
gemini "質問内容"

# ✅ 正しい
gemini -p "質問内容"
```

## 📊 タスク管理・フォルダ整理の絶対ルール

### **タスク管理**
- **TodoWrite/TodoRead** - 毎回状況更新
- **進捗報告** - 作業完了毎に状況記録
- **セッション引き継ぎ** - 重要情報を必ず記録

### **フォルダ整理**
- **新規ファイル作成前** - 適切な配置場所確認
- **既存ファイル確認** - 重複回避
- **Index.md更新** - 構造変更時は必ず更新

---

**この手順書を絶対に忘れず、すべての作業で厳格実行する。**