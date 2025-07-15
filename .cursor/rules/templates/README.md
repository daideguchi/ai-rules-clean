# Cursor Rules Template System

## 📋 概要

このテンプレートシステムは、Cursor Rulesを汎用的なテンプレートとして管理し、プロジェクト固有の設定を簡単にカスタマイズできるようにします。

## 🏗️ システム構成

### Git管理される部分（テンプレート）
- `templates/` - 汎用テンプレートファイル
  - `base-rules.template.mdc` - 汎用AI開発支援ベースルール
  - `project-config.template.mdc` - プロジェクト設定テンプレート
  - `project-config.example.mdc` - 設定例（coding-rule2）
  - `README.md` - このファイル

### ローカル管理される部分（.gitignore対象）
- `local/` - プロジェクト固有設定
- `project-config.mdc` - 実際のプロジェクト設定

## 🚀 使用方法

### 1. 新規プロジェクトでの使用

```bash
# 1. テンプレートをコピー
cp .cursor/rules/templates/base-rules.template.mdc .cursor/rules/base-rules.mdc
cp .cursor/rules/templates/project-config.template.mdc .cursor/rules/project-config.mdc

# 2. プロジェクト設定をカスタマイズ
# .cursor/rules/project-config.mdc を編集して、実際のプロジェクト情報に変更

# 3. 不要なファイルを削除
rm .cursor/rules/templates/
```

### 2. 既存プロジェクトでの使用

```bash
# 1. 既存ルールのバックアップ
cp .cursor/rules/ .cursor/rules.backup/

# 2. テンプレートベースで再構築
cp .cursor/rules/templates/base-rules.template.mdc .cursor/rules/base-rules.mdc

# 3. 既存設定を project-config.mdc に統合
# 既存のルールを project-config.mdc に移行
```

## 📝 設定ファイル構成

### base-rules.mdc（汎用ルール）
- AI開発支援の基本原則
- 品質保証システム
- 作業記録・検索義務
- 継続改善システム

### project-config.mdc（プロジェクト固有設定）
- プロジェクト基本情報
- 要件定義・仕様書
- 技術スタック
- 開発環境設定
- ユーザー希望ルール

## 🎯 カスタマイズ手順

### Step 1: 基本情報設定
```
1. プロジェクト名・技術スタックを記入
2. 要件定義を具体的に記述
3. 仕様書・設計書を添付・参照
```

### Step 2: 開発ルール設定
```
1. コーディング規約を決定
2. テスト戦略を計画
3. チーム運用ルールを合意
```

### Step 3: 環境設定
```
1. 開発環境を構築
2. CI/CDパイプラインを設定
3. 品質保証ツールを導入
```

### Step 4: 検証・調整
```
1. 設定内容の妥当性確認
2. チーム内での合意形成
3. 継続的な改善・調整
```

## 🔧 技術的な設定

### YAML Front Matter
全てのルールファイルには適切なYAML Front Matterが必要です：

```yaml
---
description: "ルールの説明"
globs:
  - "**/*.{js,ts,py}"  # 適用対象ファイル
alwaysApply: true      # 常に適用するか
---
```

### ファイル除外設定
`.gitignore`に以下を追加してローカル設定を除外：

```gitignore
# Cursor rules local configuration
.cursor/rules/local/
.cursor/rules/project-config.mdc

# Local project settings (not versioned)
local-config/
project-specific/
user-settings/
```

## 📊 推奨ファイル構成

### 最小構成（6ファイル）
```
.cursor/rules/
├── base-rules.mdc          # 汎用ベースルール
├── project-config.mdc      # プロジェクト固有設定
├── dev-rules.mdc           # 開発・コーディングルール
├── testing.mdc             # テスト戦略
├── project-management.mdc  # プロジェクト管理
├── uiux.mdc               # UI/UX設計
└── performance.mdc        # パフォーマンス最適化
```

### 拡張構成（追加可能）
```
├── security.mdc           # セキュリティルール
├── ai-integration.mdc     # AI統合ルール
├── documentation.mdc      # ドキュメント作成
├── collaboration.mdc      # チーム協業
├── monitoring.mdc         # 監視・可観測性
└── deployment.mdc         # デプロイメント
```

## 🎨 プロジェクト固有の例

### Web開発プロジェクト
```
技術スタック: React + TypeScript + Node.js
要件: SPA、レスポンシブデザイン、PWA対応
特別ルール: アクセシビリティ重視、SEO最適化
```

### AI/MLプロジェクト
```
技術スタック: Python + TensorFlow + Docker
要件: モデル学習、API提供、バッチ処理
特別ルール: データ品質管理、モデル評価
```

### 企業システム
```
技術スタック: Java + Spring Boot + PostgreSQL
要件: 高可用性、セキュリティ、監査ログ
特別ルール: 法規制遵守、セキュリティ重視
```

## 🔍 トラブルシューティング

### よくある問題

1. **ルールが適用されない**
   - YAML Front Matterの確認
   - globs設定の確認
   - Cursor再起動

2. **設定が競合する**
   - ファイル優先順位の確認
   - 重複ルールの削除
   - 設定の統合

3. **カスタマイズが難しい**
   - example.mdcファイルを参考
   - 段階的な設定変更
   - テンプレートの活用

### サポートリソース
- [Cursor公式ドキュメント](https://cursor.sh/docs)
- [参考リポジトリ](https://github.com/daideguchi/cursor-rules-guide)
- プロジェクトのIssues

## 🚀 改善・拡張

### テンプレート改善
- 新しいベストプラクティスの追加
- 技術トレンドの反映
- ユーザーフィードバックの統合

### 統合システム
- 自動設定システム
- 設定検証ツール
- テンプレート更新システム

---

**このテンプレートシステムを使用することで、効率的でカスタマイズ可能なCursor Rulesを構築できます。**

**プロジェクトの要件に合わせて、適切なカスタマイズを行ってください。** 