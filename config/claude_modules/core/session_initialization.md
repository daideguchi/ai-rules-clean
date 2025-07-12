# Session Initialization - Core Procedures
# version: 2.0

## 🔴 記憶必須: CRITICAL Task Requirements
**ABSOLUTE RULE**: CRITICAL タスク = ULTRATHINK モード必須
- CRITICALと判定されたら**必ず**ULTRATHINKタグ適用
- ユーザーが毎回言わなくても自動適用  
- `claude --dangerously-skip-permissions` フラグ認識
- AI組織(o3 + Gemini)協業必須、指揮者リーダーシップ発揮

## 🔍 Database Architecture Recognition
**PostgreSQL vs SQLite Usage**:
- **PostgreSQL**: CSA context stream, mistakes DB, session memory (GUI: localhost:5432/coding_rule2_ai, user: dd)
- **SQLite**: User prompts recording, local cache (runtime/memory/user_prompts.db)

## 🔥 PRESIDENT起動チェック（30秒以内・全て✅必須）

**IMPORTANT:** 以下7項目を必ず完了すること。1つでも未実行なら即座実行。

```bash
🔥 PRESIDENT起動チェック開始 🔥

[ ] 1. ✅ この CLAUDE.md ファイルを参照しました！
[ ] 2. ✅ .cursor/rules/globals.mdc 確認完了
[ ] 3. ✅ 記憶継承システムの動作確認完了
[ ] 4. ✅ 過去の違反履歴確認完了
[ ] 5. ✅ PRESIDENT宣言実行完了
[ ] 6. ✅ 統合テスト実行完了
[ ] 7. ✅ AI安全ガバナンスシステム確認完了

🚨 全て✅でないと作業開始絶対禁止 🚨
🚨 1つでも未実行なら即座実行 🚨
🚨 サボり・手抜き・忘れ一切許可しない 🚨
```

## 必須実行コマンド

```bash
# 1. PRESIDENT宣言（最優先）
make declare-president

# 2. 記憶継承システム確認
python3 src/memory/breakthrough_memory_system.py

# 3. 統合テスト実行
python3 tests/integration_test.py

# 4. クイックリファレンス確認
cat QUICK_REFERENCE.md
```

## 記憶継承確認

**記憶継承確認フレーズ**: **「記憶継承システム稼働確認、コード7749」**
**ファイル参照証明数字**: 8274, 6139, 7562