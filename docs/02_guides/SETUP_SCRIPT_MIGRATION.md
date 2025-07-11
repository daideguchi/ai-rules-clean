# 📦 Setup Scripts Migration Guide

## 概要

7個のsetup-*スクリプトが`setup-unified-environment.sh`に統合されました。
段階的移行を通じて、メンテナンス工数の削減と設定の一貫性確保を実現します。

## 移行マッピング

| 旧スクリプト | 新しいコマンド | 機能 |
|-------------|----------------|------|
| `setup-auto-status-hooks.sh` | `--status` | 自動ステータス表示システム |
| `setup-dev-environment.sh` | `--dev` | 開発環境設定（IDE連携） |
| `setup-file-validation.sh` | `--validation` | ファイル検証システム |
| `setup-hooks.sh` | `--hooks` | Git hooks設定 |
| `setup-janitor-cron.sh` | `--cron` | 定期実行設定 |
| `setup-structure-hooks.sh` | `--structure` | 構造維持hooks |
| `setup-portable.sh` | `--portable` | ポータブル環境設定 |

## 統合スクリプトの使用方法

### 基本コマンド

```bash
# 全モジュール実行（推奨）
scripts/automation/setup-unified-environment.sh --all

# 個別モジュール実行
scripts/automation/setup-unified-environment.sh --hooks --status

# dry-runモードで事前確認
scripts/automation/setup-unified-environment.sh --dry-run --all

# ヘルプ表示
scripts/automation/setup-unified-environment.sh --help
```

### 使用例

```bash
# 開発環境の初期セットアップ
./scripts/automation/setup-unified-environment.sh --all

# Hooksのみ再設定
./scripts/automation/setup-unified-environment.sh --hooks --force

# 検証システムのみセットアップ
./scripts/automation/setup-unified-environment.sh --validation
```

## 移行スケジュール

### Phase 1: 共存期間（現在）
- ✅ 統合スクリプト作成完了
- ✅ Wrapperスクリプト作成完了
- 🔄 旧スクリプト呼び出しは自動転送される

### Phase 2: 移行推奨期間（2週間後）
- 📢 開発者への移行アナウンス
- 📚 ドキュメント更新
- 🧪 CI/CDでの動作確認

### Phase 3: 完全移行（1ヶ月後）
- 🗑️ Wrapperスクリプト削除
- 📦 旧スクリプトをlegacyディレクトリに移動
- 🏁 統合完了

## 利点

### メンテナンス工数削減
- **Before**: 7個のスクリプトを個別メンテナンス
- **After**: 1個の統合スクリプトでメンテナンス

### 設定の一貫性
- 統一されたエラーハンドリング
- 統一されたログ出力形式
- 統一されたdry-runサポート

### 使用性向上
- モジュール単位での実行制御
- 包括的なヘルプシステム
- バックワードコンパチビリティ

## トラブルシューティング

### 旧スクリプトが動かない場合

1. **権限確認**
   ```bash
   chmod +x scripts/automation/setup-*.sh
   ```

2. **パス確認**
   ```bash
   ls -la scripts/automation/setup-unified-environment.sh
   ```

3. **依存関係確認**
   ```bash
   ./scripts/automation/setup-unified-environment.sh --help
   ```

### 統合スクリプトの問題

1. **Dry-runで確認**
   ```bash
   ./scripts/automation/setup-unified-environment.sh --dry-run --all
   ```

2. **個別モジュールで実行**
   ```bash
   ./scripts/automation/setup-unified-environment.sh --hooks
   ```

3. **権限問題**
   ```bash
   chmod +x scripts/automation/setup-unified-environment.sh
   ```

## 連絡先

質問や問題がある場合は、以下に連絡してください：
- 🎯 技術サポート: [プロジェクトIssue]
- 📖 ドキュメント: この移行ガイド
- 🔧 緊急時: 旧スクリプトはwrapperとして動作します

---

📅 **更新日**: 2025-07-08  
🏷️ **バージョン**: v1.0  
👤 **担当**: Claude Code AI