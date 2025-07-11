# 🔧 スクリプト管理戦略 - ベストプラクティス実装

**作成**: 2025-07-08T01:15:00+09:00  
**権限**: PRESIDENT最高指揮権  
**目標**: 130個スクリプトの効率的管理体制確立

## 📊 現状分析

### スクリプト分布状況
- **総数**: 130個のbashスクリプト
- **分類**: 8カテゴリに分散
- **問題**: 命名規則不統一、機能重複、階層不明確

## 🎯 ベストプラクティス分類方針

### **Tier 1: コア機能（必須保持）**
```
scripts/core/
├── startup/              # システム起動関連
│   ├── start-president   # PRESIDENT単独起動
│   ├── start-ai-workers  # AI組織起動
│   └── task              # タスク管理
├── hooks/                # Git hooks（重要）
│   ├── pre-commit
│   ├── pre-push
│   └── pre-commit-duplicate-check
└── essential/            # 日常必須ツール
    ├── setup-hooks.sh
    └── check-cursor-rules
```

### **Tier 2: 機能別グループ（整理統合）**
```
scripts/automation/       # 自動化・セットアップ
scripts/validation/       # 検証・テスト
scripts/maintenance/      # メンテナンス・クリーンアップ
scripts/utilities/        # 汎用ユーティリティ
scripts/ai-workers/       # AI Worker管理
scripts/memory/           # メモリシステム
scripts/monitoring/       # 監視・ログ
```

### **Tier 3: 統合候補（削減対象）**
- 重複機能スクリプト
- 一時的テストスクリプト
- 廃止予定機能

## 🔧 管理原則

### **1. 命名規則統一**
```bash
# ❌ 悪い例
check-cursor-rules
validate-structure.sh
AI_GITHUB_MCP_INTEGRATION.sh

# ✅ 良い例
check-cursor-rules.sh
validate-project-structure.sh
ai-github-mcp-integration.sh
```

### **2. 機能統合ルール**
- **3行未満**: 削除または統合
- **同一機能**: より新しい版に統合
- **テスト用**: 専用ディレクトリに隔離

### **3. 権限管理**
```bash
# 実行権限の統一
chmod +x scripts/**/*.sh

# セキュリティレベル分離
scripts/privileged/   # sudo要求
scripts/standard/     # 通常権限
```

## 📋 段階的実行計画

### **Phase 1: 構造再編（進行中）**
1. ✅ RED削除（6個完了）
2. ✅ AMBER安全削除（3個完了）
3. 🔄 残りAMBER統合（5個予定）

### **Phase 2: カテゴリ再配置**
1. Tier 1コア機能の保護
2. Tier 2機能別グループ化
3. Tier 3統合・削減

### **Phase 3: 品質統一**
1. 命名規則適用
2. エラーハンドリング統一
3. ドキュメント整備

## 🚨 削除判定ルール

### **他AI確認必須条件**
- ファイルサイズ > 1KB
- 複数箇所から参照
- Git履歴で頻繁更新
- 名前に"setup"、"core"、"main"含む

### **即時削除可能**
- 空ファイル（< 10行）
- 明確な重複
- テスト/demo用途
- .backup、.old拡張子

## 📈 目標指標

- **最終目標**: 50-80個（40%削減）
- **コア機能**: 15-20個
- **機能別**: 30-50個
- **保守性**: メンテナンス工数50%削減

---

**次のアクション: 現在130個の詳細分析とカテゴリ再配置実行**