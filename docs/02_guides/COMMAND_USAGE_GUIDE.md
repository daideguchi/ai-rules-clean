# 🎯 Command Usage Guide - AI Safety Governance System

## Quick Start (新規ユーザー向け)

### 1. 初回セットアップ
```bash
make startup          # 完全システム起動
make help            # コマンド一覧確認
```

### 2. 日常の使用
```bash
make declare-president    # セッション開始時（必須）
make ai-org-start        # AI組織起動
make integration-test    # システム確認
```

### 3. 問題発生時
```bash
make status              # システム状態確認
make cleanup            # システムクリーンアップ
make validate           # 構造検証
```

## コマンド分類

### 🚀 Essential Quick Start
必須コマンド - 基本操作に必要

### Essential Quick Start
- `make startup` - 完全システム起動（社長+AI組織+DB+記憶）
- `make quick-start` - 高速起動（必須システムのみ）

### Daily Operations
- `make declare-president` - セキュアPRESIDENT宣言必須実行
- `make ai-org-start` - AI組織システム起動
- `make memory-recall` - 記憶思い出し・継承確認
- `make integration-test` - 統合テスト実行

### System Management
- `make check-root` - Check root directory file limit compliance

### Development & Testing
- `make evaluate` - 包括的システム評価
- `make metrics` - メトリクス確認

### Advanced Features
- `make ui-install` - Install UI system dependencies
- `make ui-dashboard` - Launch AI organization dashboard
- `make ui-command` - Launch interactive command interface
- `make ui-worker` - Launch worker management interface
- `make ui-metrics` - Show system metrics
- `make ui-demo` - Run UI system demonstration
- `make ui-test` - Test UI system components
- `make full-startup` - フル起動＋評価システム

## 使用頻度別推奨

### 毎日使用
- `make startup` - システム起動
- `make declare-president` - セッション開始
- `make status` - 状態確認

### 週1回程度
- `make cleanup` - システムクリーンアップ
- `make integration-test` - 統合テスト
- `make evaluate` - システム評価

### 必要に応じて
- `make install` - 依存関係インストール
- `make setup-hooks` - Git フック設定
- `make template-init` - テンプレート初期化

## トラブルシューティング

### よくある問題と解決法
1. **PRESIDENT宣言失敗** → `make declare-president`
2. **AI組織起動失敗** → `make ai-org-start`
3. **データベース接続失敗** → `make db-connect`
4. **統合テスト失敗** → `make integration-test`

### 緊急時
```bash
make cleanup         # 全体クリーンアップ
make validate        # 構造検証
make startup         # システム再起動
```
