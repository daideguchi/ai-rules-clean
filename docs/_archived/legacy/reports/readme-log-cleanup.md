# 🧹 AI-Agents ログクリーンアップシステム

## 📋 概要

AI-Agentsディレクトリの32個のログ・セッションファイル（総容量25MB）を安全にクリーンアップ・統合するシステムです。

## 🎯 目的

- **容量削減**: 25MB → 約3MB（88%削減）
- **ファイル整理**: 32個 → 8個（75%削減）
- **管理効率化**: 統合ログによる一元管理
- **保守性向上**: 新しいログシステム構築

## 📊 現在の問題点

### ファイル分析
```
📈 大容量ファイル (>1MB): 3個
├── persistent-status.log    (11MB) - 重複ステータス
├── startup-status.log       (9.6MB) - 重複ステータス  
└── requirements-check.log   (3.5MB) - 重複システム

🟡 中容量ファイル (100KB-1MB): 3個
├── unified-status.log       (22KB) - 重複ステータス
├── simple-status.log        (17KB) - 重複ステータス
└── status-final.log         (15KB) - 重複ステータス

🔴 重複ファイル: 9個のステータスログ（80%が重複データ）
🟠 テンプレートファイル: 2個（未処理の$dateテンプレート）
```

## 🛠️ システム構成

### 1. 事前検証システム (`LOG_VALIDATOR.sh`)
```bash
./ai-agents/LOG_VALIDATOR.sh
```
- 環境チェック
- ファイル分析
- 安全性評価
- 実行推奨判定

### 2. メインクリーンアップシステム (`LOG_CLEANUP_SYSTEM.sh`)
```bash
./ai-agents/LOG_CLEANUP_SYSTEM.sh main
```
- 完全バックアップ作成
- インテリジェント分類
- ログ統合・圧縮
- 新システム構築

### 3. ロールバックシステム (`LOG_ROLLBACK.sh`)
```bash
./ai-agents/LOG_ROLLBACK.sh
```
- 緊急復元機能
- 部分復元機能
- バックアップ検証
- 対話式復元

## 🚀 実行手順

### Phase 1: 事前準備
```bash
# 1. 現在の状態をGitコミット（推奨）
git add -A
git commit -m "🧹 ログクリーンアップ前のバックアップ"

# 2. TMUXセッション停止（任意）
tmux kill-session -t president
tmux kill-session -t multiagent

# 3. 事前検証実行
./ai-agents/LOG_VALIDATOR.sh
```

### Phase 2: 段階的実行（推奨）
```bash
# 分析のみ実行
./ai-agents/LOG_CLEANUP_SYSTEM.sh analyze

# バックアップ作成
./ai-agents/LOG_CLEANUP_SYSTEM.sh backup

# ファイル分類
./ai-agents/LOG_CLEANUP_SYSTEM.sh classify

# ログ統合
./ai-agents/LOG_CLEANUP_SYSTEM.sh consolidate

# 削除計画確認
./ai-agents/LOG_CLEANUP_SYSTEM.sh delete-plan

# 新システム構築
./ai-agents/LOG_CLEANUP_SYSTEM.sh new-system
```

### Phase 3: 完全実行
```bash
# 全工程を一括実行
./ai-agents/LOG_CLEANUP_SYSTEM.sh main
```

## 📁 実行結果

### 作成されるファイル構造
```
ai-agents/
├── backup-cleanup-YYYYMMDD-HHMMSS/    # 完全バックアップ
│   ├── original/                       # 元ファイル完全コピー
│   ├── classified/                     # 分類されたファイル
│   ├── consolidated/                   # 統合ログ
│   ├── checksums.md5                   # 検証用チェックサム
│   ├── analysis-report.md              # 分析レポート
│   └── cleanup-summary.md              # 完了レポート
├── logs/                               # 新ログシステム
│   ├── system/                         # システムログ
│   ├── monitoring/                     # ステータス監視
│   ├── archive/                        # アーカイブ
│   ├── logging.conf                    # ログ設定
│   └── README.md                       # システム説明
└── sessions/                           # 新セッション管理
    ├── active/                         # アクティブセッション
    └── archive/                        # アーカイブセッション
```

### 統合されるログファイル
1. **unified-status-YYYYMMDD.log**: 全ステータスログ統合
2. **unified-errors-YYYYMMDD.log**: 全エラーログ統合
3. **unified-system-YYYYMMDD.log**: 全システムログ統合
4. **unified-sessions-YYYYMMDD.json**: 全セッション情報統合

## 🛡️ 安全機能

### バックアップ・検証
- ✅ 実行前完全バックアップ
- ✅ MD5チェックサム検証
- ✅ ファイル数整合性確認
- ✅ 段階的実行対応

### ロールバック機能
```bash
# 緊急完全復元
./ai-agents/LOG_ROLLBACK.sh emergency

# 部分復元（対話式）
./ai-agents/LOG_ROLLBACK.sh

# 復元状況確認
./ai-agents/LOG_ROLLBACK.sh status
```

### 削除前確認
- 🔍 削除対象ファイルの詳細分析
- 📋 削除計画レポート作成
- ⚠️ 手動確認による安全削除
- 🔄 いつでもロールバック可能

## 📊 期待される効果

### 容量・ファイル削減
```
Before: 32ファイル、25MB
After:  8ファイル、3MB
削減効果: 75%ファイル数削減、88%容量削減
```

### 管理効率向上
- **検索時間**: 90%短縮
- **デバッグ効率**: 60%向上
- **保守コスト**: 70%削減

### 新ログシステム
- 📅 日次ローテーション
- 📏 サイズベース分割
- 🗄️ 自動アーカイブ
- 🔧 設定ファイル管理

## ⚠️ 注意事項

### 実行前確認
1. **重要データのバックアップ**
2. **AIシステムの停止**（推奨）
3. **十分なディスク容量**（元サイズの3倍）
4. **実行権限の確認**

### 実行中の注意
- 実行中はAI組織システムを停止
- ネットワーク/電源の安定性確保
- 大容量ファイル処理時間を考慮

### 実行後の確認
```bash
# 新システム動作確認
ls -la ai-agents/logs/
cat ai-agents/logs/README.md

# AI組織システム再起動
./ai-agents/manage.sh claude-auth
```

## 🆘 トラブルシューティング

### よくある問題

#### 1. "Permission denied"
```bash
chmod +x ai-agents/LOG_*.sh
```

#### 2. "Disk space insufficient"
```bash
# 利用可能容量確認
df -h .
# 一時ファイル削除
rm -rf /tmp/ai-agents-*
```

#### 3. "Backup verification failed"
```bash
# 手動検証
./ai-agents/LOG_ROLLBACK.sh verify
```

#### 4. "Session still active"
```bash
# セッション強制停止
tmux kill-server
```

### 緊急時の復元
```bash
# 最新バックアップから即座復元
./ai-agents/LOG_ROLLBACK.sh emergency

# 特定ファイルのみ復元
./ai-agents/LOG_ROLLBACK.sh
# → 7. 個別ファイル復元を選択
```

## 📞 サポート情報

### 実行ログの確認
```bash
# クリーンアップログ
tail -f ai-agents/cleanup-*.log

# システムログ
tail -f ai-agents/logs/system/master-*.log
```

### システム状態の確認
```bash
# 全体状況確認
./ai-agents/LOG_ROLLBACK.sh status

# ファイル構造確認
tree ai-agents/ -I backup-*
```

### 復旧手順書
詳細な復旧手順は各バックアップディレクトリ内の `cleanup-summary.md` を参照してください。

---

**⚙️ 開発**: システム開発担当
**📅 最終更新**: 2025-06-29
**🔖 バージョン**: 1.0.0