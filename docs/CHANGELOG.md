# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [2.0.0] - 2025-07-08

### 🚀 Major Changes - スクリプト大規模統合

#### Added
- **統合スクリプト** (Command Pattern実装)
  - `scripts/utils.sh` - 5機能統合ユーティリティ
  - `scripts/verify.sh` - 5機能統合検証システム
  - `scripts/maintenance.sh` - 3機能統合メンテナンス
- **管理ドキュメント**
  - `scripts/README.md` - 完全管理ガイド
  - `scripts/DEPENDENCIES.md` - 依存関係マップ
  - `PRESIDENT_COMMAND_PROCEDURES.md` - 指揮者手順書
  - `docs/03_processes/script-management-strategy.md` - 管理戦略

#### Changed
- スクリプト総数: 139個 → 31個 (78%削減)
- エラーハンドリング: 全スクリプト`set -euo pipefail`適用
- 命名規則: `verb-noun.sh`形式に統一

#### Restored (High-Risk Scripts)
- `ai-api-check.sh` - AI API疎通確認
- `danger-pattern-detector.sh` - 危険パターン検出
- `complete-system-test.sh` - 包括システムテスト
- `duplicate-prevention-system.sh` - 重複防止システム
- `test-git-history-preservation.sh` - Git履歴保存テスト

#### Security
- APIキー管理システム実装 (`src/security/api_key_manager.py`)
- RBAC実装 (`src/security/rbac_system.py`)
- MD5脆弱性修正 (usedforsecurity=False)
- ファイル権限強化 (0o755 → 0o750/0o700)

#### Fixed
- runtime_advisor.py: "project/file.txt"パターン検出修正
- 全テスト合格 (100%成功率達成)
- .specstory/と.vscode/の.gitignore保護追加

### 📊 Impact
- **メンテナンス工数**: 80%削減見込み
- **セキュリティ**: 攻撃面積大幅削減
- **品質**: 統一されたエラーハンドリング

## [1.0.0] - 2025-07-07

### 🎯 Reform Completed - 根本的改革完遂

#### Added
- **Index.md** - プロジェクト全体マップ・起点ファイル作成
- **Makefile** - タスク抽象化（help, status, run-president等）
- **5分検索ルール** - 推測回答根絶システム実装
  - `docs/03_processes/5min-search-rule.md`
  - `scripts/utilities/5min-search.sh`
- **起動チェックリスト** - `startup_checklist.md`
- **日次チェックスクリプト** - `scripts/utilities/daily_check.sh`
- **違反記録システム** - `runtime/session_violations.log`
- **誤り防止システム** - `docs/03_processes/mistake-prevention-system.md`

#### Changed
- **README.md完全書き換え** - Single Source of Truth確立
- **docs再構築** - misc解体、目的別ディレクトリ構造確立
  - `00_INDEX/` - ドキュメント案内
  - `01_concepts/` - 設計思想・アーキテクチャ
  - `02_guides/` - セットアップ・操作ガイド
  - `03_processes/` - 運用手順・チェックリスト
  - `04_reference/` - 技術仕様・APIリファレンス
  - `_archive/` - 過去ログ・レポート

#### Removed
- **docs/misc/** - 無秩序ディレクトリを完全削除
- **docs/reports/** - archiveに移動
- **docs/reports-main/** - referenceに統合
- **ルート散乱ファイル** - 12個を適切なディレクトリに配置

#### Fixed
- **プロジェクト構造の混沌** - 体系的な整理完了
- **参照システムの不在** - Index.mdによる統一参照
- **推測回答問題** - 5分検索ルール強制実装

### 品質保証
- O3による厳格チェック実施
- Gemini 2.5 Proによる検証完了
- 全機能動作確認済み

---

このリリースにより、プロジェクトの根本的な構造改革が完了しました。
