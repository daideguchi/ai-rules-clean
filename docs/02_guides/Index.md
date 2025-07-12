# CODING-RULE2 Project Index - 全体マップ

**最終更新**: 2025-07-07
**目的**: 全ファイル・ディレクトリの用途と参照関係を明確化

## 🗂️ ディレクトリ構造 & 責務

### 📋 設定・メタ情報
```
├── .claude/           # Claude Code設定
├── .cursor/           # Cursor Editor設定
├── .github/           # GitHub Actions、Issue templates
├── config/            # プロジェクト設定ファイル群
│   ├── Makefile       # ビルド・タスク定義
│   ├── mcp 2/         # MCP関連設定
│   └── pyproject.toml # Python設定
```

### 📚 ドキュメント
```
├── docs/              # 目的別分類実行中
│   ├── 00_INDEX/      # ドキュメント全体案内
│   ├── 01_concepts/   # 設計思想・アーキテクチャ
│   ├── 02_guides/     # セットアップ・操作ガイド
│   ├── 03_processes/  # 運用手順・チェックリスト
│   ├── 04_reference/  # 技術仕様・APIリファレンス
│   └── _archive/      # 過去ログ・レポート
```

### 💻 ソースコード
```
├── src/               # メインソースコード
│   ├── agents/        # AI Agent実装
│   │   ├── executive/ # PRESIDENT/BOSS roles
│   │   ├── workers/   # WORKER roles & scripts
│   │   └── integrations/ # Gemini/O3統合
│   ├── memory/        # 記憶・学習システム
│   ├── hooks/         # フック実装
│   └── runtime/       # 実行時データ・状態管理
```

### 🔧 スクリプト・自動化
```
├── scripts/           # 実行スクリプト群
│   ├── automation/    # 自動化スクリプト
│   ├── cleanup/       # メンテナンス・整理
│   ├── hooks/         # Git hooks実装
│   ├── memory-tools/  # 記憶システム用ツール
│   ├── startup/       # 起動・初期化
│   ├── utilities/     # 汎用ユーティリティ
│   └── validation/    # 検証・テスト
```

### 🧪 テスト・検証
```
├── tests/             # テストファイル群
└── runtime/           # 実行時データ・ログ・状態
```

## 🚀 クイックスタート（使用頻度順）

### 1. セッション開始
```bash
# 必須チェックリスト実行
cat startup_checklist.md

# PRESIDENT起動
make run-president
```

### 2. 主要タスク
```bash
# システム全体状態確認
make status

# 整理整頓実行
make cleanup

# フック設定更新
make setup-hooks
```

### 3. 開発・メンテナンス
```bash
# テスト実行
make test

# ドキュメント更新
make docs
```

## 📖 重要ドキュメント（参照優先度順）

### 【最優先】
1. [`startup_checklist.md`](startup_checklist.md) - セッション開始必須チェック
2. [`README.md`](README.md) - プロジェクト概要
3. [`docs/03_processes/5min-search-rule.md`](docs/03_processes/5min-search-rule.md) - 推測回答根絶

### 【システム理解】
4. [`docs/_archive/logs/session-handover.md`](docs/_archive/logs/session-handover.md) - 前回セッション重要事項
5. [`docs/_archive/logs/autonomous-growth-detailed-log.md`](docs/_archive/logs/autonomous-growth-detailed-log.md) - 学習システム詳細
6. [`docs/_archive/logs/president-honesty-system.md`](docs/_archive/logs/president-honesty-system.md) - 誠実性システム

### 【技術詳細】
7. [`docs/architecture/hooks-system-design.md`](docs/architecture/hooks-system-design.md) - フックシステム設計
8. [`src/agents/executive/roles/president.md`](src/agents/executive/roles/president.md) - PRESIDENT役割定義

## 🔍 検索・参照ルール

### ファイル検索手順
1. **このIndex.mdを確認** - 目的のファイル種別特定
2. **該当ディレクトリ内検索** - Glob/Grep使用
3. **関連ドキュメント確認** - 設計・仕様理解
4. **実行前に必ず仕様確認** - 推測禁止

### 緊急時参照
- **フック問題**: [`docs/_archive/logs/session-handover.md`](docs/_archive/logs/session-handover.md)
- **ミス防止**: [`docs/_archive/logs/mistake-prevention-system.md`](docs/_archive/logs/mistake-prevention-system.md)
- **役割忘れ**: [`startup_checklist.md`](startup_checklist.md)

## ⚠️ 現在の問題 & 改革進行中

### 🔥 緊急改革事項
- [x] docs/misc/ 26ファイルの目的別分類完了
- [x] Makefile完全実装完了
- [x] README.md完全書き換え完了
- [ ] 重複ディレクトリ整理（reports/reports-main統合）

### 📊 改革進捗
- ✅ Index.md作成完了
- ✅ startup_checklist.md作成完了
- ✅ ルート散乱ファイル整理完了
- ✅ docs再構築完了
- ✅ 5分検索ルール実装完了

---

**このファイルは全体の起点です。迷ったら必ずここに戻ってください。**
