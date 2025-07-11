# Operational Workflows & Standard Procedures

## 📋 必須実行項目

### セッション開始時に必ず実行
```bash
# 1. PRESIDENT宣言（存在する場合）
if [ -f "Makefile" ] && grep -q "declare-president" Makefile; then
  make declare-president
fi

# 2. 記憶継承確認
if [ -f "runtime/thinking_violations.json" ]; then
  echo "過去の違反履歴:"
  cat runtime/thinking_violations.json | grep -E "(violation_count|NO_SPECSTORY|THINKING_MANDATORY)"
fi

# 3. 重要ドキュメント確認
if [ -f "CLAUDE.md" ]; then
  echo "プロジェクト固有設定を確認"
fi
```

### Task Classification Workflow
1. **Task Level Analysis**: CRITICAL/HIGH/MEDIUM/LOW
2. **Protocol Selection**: 
   - CRITICAL → ULTRATHINK Mode + AI Organization
   - HIGH → Standard Protocol + Monitoring
   - MEDIUM/LOW → Basic Execution
3. **Execution Method**: Based on classification
4. **Verification**: Post-execution validation

### File Management Workflow
```bash
# 重要ファイルの固定パス（findを使わない）
# 違反記録
runtime/thinking_violations.json
runtime/memory/violations.json
runtime/mistake_prevention/mistakes_ledger.json

# 記憶システム
src/memory/breakthrough_memory_system.py
runtime/memory/forever_ledger.db
runtime/memory/session_logs.json

# AIシステム
src/ai/constitutional_ai.py
src/ai/rule_based_rewards.py
src/conductor/core.py

# ドキュメント
docs/04_reference/CLAUDE_CODE_MEMORY_SYSTEM.md
CLAUDE.md
```

## 基本ルール

### 1. フォルダ管理
- .specstoryフォルダは変更しない

### 2. 応答形式
- 必ず<thinking>タグで思考プロセスを開始

### 3. システム設計
- 動的役職システムを使用
- 4分割ペイン構成
- 実データのみ使用

### 4. ファイル管理
- 重要ファイルの削除・移動は慎重に
- ユーザーの許可なく勝手に移動しない
- 特にルートディレクトリのファイルは要注意

## プロジェクト開始時の確認
1. PRESIDENT宣言の実行
2. CLAUDE.mdファイルの確認

## 記憶継承の仕組み
- ユーザーメモリ: `~/.claude/CLAUDE.md`（全プロジェクト共通）
- プロジェクトメモリ: `./CLAUDE.md`（プロジェクト固有）
- 両方が自動的に読み込まれる