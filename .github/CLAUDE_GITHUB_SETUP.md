# Claude Code GitHub Actions セットアップガイド

## 🚀 概要

このプロジェクトはClaude Code GitHub Actions統合を含んでいます。GitHub上で `@claude` と記載するだけで、AIがコード分析、PR作成、バグ修正などを自動で行います。

## 📋 セットアップ手順

### 1. GitHub App インストール（推奨）
```
https://github.com/apps/claude
```
上記URLから Claude GitHub App をインストールしてください。

### 2. API キー設定
リポジトリの Settings > Secrets and variables > Actions で以下を設定：

```
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### 3. ワークフロー確認
以下のファイルが自動的に設定されています：
- `.github/workflows/claude-code.yml` - 基本的なClaude統合
- `.github/workflows/claude-pr-review.yml` - PR自動レビュー
- `.github/scripts/claude-handler.py` - Claude処理ハンドラー
- `.github/scripts/claude-pr-reviewer.py` - PR レビューアー

## 🎯 使用方法

### 基本的な使用
Issue またはPRのコメントで `@claude` を記載：

```
@claude この機能を実装してください
```

```
@claude このバグを修正してください
```

```
@claude コードレビューをお願いします
```

### PR自動レビュー
PRの説明に `@claude-review` を追加すると自動レビューが実行されます：

```
@claude-review このPRをレビューしてください
```

## 🛡️ AI安全ガバナンス対応

このテンプレートは AI Safety Governance システムに特化した設定を含んでいます：

### 自動チェック項目
- ✅ PRESIDENT宣言システムの整合性
- ✅ tmux設定の標準準拠
- ✅ フックシステムの機能性
- ✅ 記憶継承システムの一貫性
- ✅ Constitutional AIの準拠性
- ✅ セキュリティ・安全基準

### プロジェクト固有の理解
Claude は以下を自動認識します：
- プロジェクトの CLAUDE.md 設定
- AI安全ガバナンステンプレートの特徴
- PRESIDENT宣言システムの重要性
- tmux ワーカー制御システムの標準

## 📊 機能一覧

### Issue 処理
- 自動的な実装提案
- バグ修正の手順提示
- コード例の生成
- プロジェクト標準への準拠確認

### PR レビュー
- コード品質チェック
- セキュリティ分析
- パフォーマンス評価
- AI安全ガバナンス準拠確認
- プロジェクト標準との整合性チェック

### 自動化機能
- Issue → PR変換
- 実装ガイダンス
- バグ修正提案
- ドキュメント更新

## ⚙️ 設定カスタマイズ

### タイムアウト設定
`.github/workflows/claude-code.yml` で調整：
```yaml
env:
  CLAUDE_TIMEOUT: 300  # 5分
  CLAUDE_MAX_TOKENS: 4000
```

### モデル設定
`.github/scripts/claude-handler.py` で変更：
```python
model="claude-3-sonnet-20240229"  # または claude-3-opus-20240229
```

### レビュー範囲設定
`.github/scripts/claude-pr-reviewer.py` で調整：
```python
max_files = 10  # レビューする最大ファイル数
max_diff_chars = 3000  # 分析する最大diff文字数
```

## 🔒 セキュリティ考慮事項

### API キー管理
- ✅ GitHub Secrets で安全に管理
- ✅ 環境変数での受け渡し
- ❌ コードに直接記載しない

### アクセス権限
```yaml
permissions:
  contents: write
  pull-requests: write
  issues: write
```

### 制限事項
- プライベートリポジトリでのみ使用推奨
- 機密情報を含むPRでは手動確認必須
- 本番環境への直接デプロイは避ける

## 🎯 テンプレート化対応

### 新プロジェクトでの使用
1. このディレクトリ構造をコピー
2. `ANTHROPIC_API_KEY` を設定
3. CLAUDE.md をプロジェクト用に調整
4. ワークフローをテスト

### カスタマイズポイント
- プロジェクト固有のチェック項目
- コーディング標準の追加
- レビュー基準の調整
- 通知設定の変更

## 🔧 トラブルシューティング

### よくある問題

#### API キーエラー
```
Error: ANTHROPIC_API_KEY environment variable is required
```
→ GitHub Secrets で `ANTHROPIC_API_KEY` を設定

#### 権限エラー
```
Error: Resource not accessible by integration
```
→ ワークフローの `permissions` を確認

#### Claude応答なし
- API制限を確認
- トークン数制限を確認
- ネットワーク接続を確認

### ログ確認
GitHub Actions の Logs タブで詳細確認可能

## 📚 関連ドキュメント

- [Claude Code GitHub Actions 公式ドキュメント](https://docs.anthropic.com/ja/docs/claude-code/github-actions)
- [GitHub Actions ワークフロー構文](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [Anthropic API ドキュメント](https://docs.anthropic.com/claude/reference)

---

**🎉 Claude Code GitHub Actions 統合完了 - テンプレート対応済み**