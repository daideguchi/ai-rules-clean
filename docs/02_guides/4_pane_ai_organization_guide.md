# 4ペインAI組織運用ガイド

## 概要
AI組織は4画面ペイン展開での並列化を前提とした4役職固定システムです。
Claude Code 4つの同時立ち上げにより、効率的な並列処理を実現します。

## 4役職システム設計

### CRITICAL タスク時の4役職
1. **CriticalAnalyst** (ペイン1)
   - 緊急状況分析
   - リスク評価
   - 根本原因特定

2. **SecurityDesigner** (ペイン2)
   - セキュリティ設計
   - 安全性確保
   - 脆弱性対策

3. **SystemImplementer** (ペイン3)
   - システム実装
   - コア機能開発
   - インフラ構築

4. **QualityValidator** (ペイン4)
   - 品質検証
   - テスト実行
   - 最終検査

### HIGH タスク時の4役職
1. **DeepAnalyst** (ペイン1)
   - 詳細分析
   - 要件定義
   - 仕様策定

2. **ArchitectDesigner** (ペイン2)
   - アーキテクチャ設計
   - システム設計
   - 技術選定

3. **CoreImplementer** (ペイン3)
   - 中核実装
   - 機能開発
   - 統合作業

4. **PerformanceValidator** (ペイン4)
   - パフォーマンス検証
   - 性能テスト
   - 最適化

## 4画面ペイン配置

```
┌─────────────────┬─────────────────┐
│   ペイン1       │   ペイン2       │
│   Analyst       │   Designer      │
│   (分析・要件)   │   (設計・計画)   │
├─────────────────┼─────────────────┤
│   ペイン3       │   ペイン4       │
│   Implementer   │   Validator     │
│   (実装・構築)   │   (検証・品質)   │
└─────────────────┴─────────────────┘
```

## Claude Code並列起動方法

```bash
# ペイン1: 分析担当
claude --session-id="analyst-session" --role="analyst"

# ペイン2: 設計担当  
claude --session-id="designer-session" --role="designer"

# ペイン3: 実装担当
claude --session-id="implementer-session" --role="implementer"

# ペイン4: 検証担当
claude --session-id="validator-session" --role="validator"
```

## 役職間連携フロー

### 1. タスク開始時
- PRESIDENT が4役職にタスク分割・配布
- 各役職が並列で作業開始

### 2. 進行中
- 定期的な進捗同期
- 必要に応じた役職間情報交換
- PRESIDENT による統括監視

### 3. 完了時
- 各役職の成果物統合
- QualityValidator による最終検証
- PRESIDENT による完了承認

## メリット

### 効率性
- **並列処理**: 4つの異なる観点から同時作業
- **専門性**: 各役職の特化による品質向上
- **速度**: 分業による処理時間短縮

### 管理性
- **固定構造**: 4ペイン展開との完全一致
- **予測可能性**: 常に4役職での一貫した運用
- **視覚的明確性**: 画面配置とロール配置の一対一対応

### 拡張性
- **タスクレベル対応**: CRITICAL/HIGH/MEDIUM/LOW各レベル最適化
- **柔軟な役職定義**: タスク内容に応じた役職カスタマイズ
- **品質スケーリング**: タスクレベルに応じた品質基準調整

## 注意事項

- 4役職を超える展開は行わない（画面制約）
- 各ペインは独立したClaude Codeセッション
- PRESIDENT は全体統括を行うメタロール
- 役職名はタスクレベルに応じて動的変更

## トラブルシューティング

### セッション同期エラー
```bash
# セッション状態確認
claude session status

# セッション再初期化
claude session reset --role="analyst"
```

### 役職間通信エラー
- 各ペインでのプロンプト再実行
- PRESIDENT による再統括指示
- 必要に応じてセッション再起動

## 関連ドキュメント

- [PRESIDENT機能ガイド](../src/enforcement/functional_president.py)
- [処理フロー強制システム](../src/enforcement/mandatory_flow_enforcer.py)
- [AI安全ガバナンス](../claude_modules/system/ai_safety_governance.md)