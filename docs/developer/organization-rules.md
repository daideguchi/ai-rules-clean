# 📁 **PROJECT ORGANIZATION RULES**
**coding-rule2 ディレクトリ構造・ファイル振り分けルール**

## 🎯 **基本原則**

### 1. **機能別分離**
- 機能ごとに明確にディレクトリを分離
- 関連ファイルは同一ディレクトリに配置

### 2. **階層の最適化**
- 深すぎる階層（4階層以上）を避ける
- アクセス頻度の高いファイルは浅い階層に

### 3. **命名規則統一**
- 小文字ケバブケース推奨: `file-name.ext`
- 日付形式統一: `YYYY-MM-DD-HHMMSS`
- スペース完全禁止

## 📂 **ディレクトリ構造ルール**

### **🏠 ルートレベル (Level 0)**
```
coding-rule2/
├── ai-team.sh              ✅ メインエントリーポイント
├── README.md               ✅ プロジェクト説明
├── requirements.txt        ✅ 依存関係
└── ORGANIZATION_RULES.md   ✅ このファイル
```

**配置ルール**:
- **メインスクリプト**: `ai-team.sh` (統合管理)
- **プロジェクト文書**: `README.md`, `LICENSE`, `CHANGELOG.md`
- **設定ファイル**: `requirements.txt`, `.gitignore`

### **🤖 AI組織システム (Level 1)**
```
ai-agents/
├── manage.sh               ✅ AI組織専用管理スクリプト
├── README.md               ✅ AI組織システム説明
├── configs/                ✅ 設定ファイル統合
├── scripts/                ✅ スクリプト統合
├── instructions/           ✅ AI役割定義
├── logs/                   ✅ AI組織ログ
└── reports/                ✅ AI組織レポート
```

### **⚙️ 設定管理 (Level 2)**
```
configs/
├── agents.json             ✅ エージェント設定
├── system.json             ✅ システム設定
├── integrations/           ✅ 外部連携設定
└── environments/           ✅ 環境別設定
```

### **🔧 スクリプト管理 (Level 2)**
```
scripts/
├── core/                   ✅ コアシステム
├── automation/             ✅ 自動化ツール
├── utilities/              ✅ ユーティリティ
├── load-config.sh          ✅ 設定ローダー
└── validate-system.sh      ✅ システム検証
```

### **🔗 外部連携 (Level 1)**
```
integrations/
├── gemini/                 ✅ Gemini連携
├── mcp/                    ✅ MCP統合
└── apis/                   ✅ API連携
```

### **📊 ログ・レポート管理 (Level 1)**
```
logs/
├── system/                 ✅ システムログ
├── agents/                 ✅ エージェントログ
├── integrations/           ✅ 連携ログ
└── archive/                ✅ アーカイブ
```

### **📚 ドキュメント管理 (Level 1)**
```
docs/
├── guides/                 ✅ ガイド
├── api/                    ✅ API文書
├── architecture/           ✅ アーキテクチャ
└── troubleshooting/        ✅ トラブルシューティング
```

## 🚫 **禁止パターン**

### 1. **重複ファイル**
- `filename 2.ext` は即座に削除
- `.bak`, `.backup` は定期削除

### 2. **深すぎる階層**
- 4階層を超える配置は禁止
- 例: `./a/b/c/d/file.ext` ❌

### 3. **不適切な命名**
- スペースを含むファイル名 ❌
- 大文字小文字混在の混乱 ❌
- 特殊文字の使用 ❌

### 4. **一時ファイルの放置**
- `nohup.out`, `*.tmp` は即座に削除
- `node_modules` の重複配置禁止

## ✅ **ベストプラクティス**

### 1. **ファイルサイズ制限**
- **スクリプト**: 50KB以下推奨
- **設定ファイル**: 10KB以下推奨
- **ログファイル**: 定期ローテーション

### 2. **権限管理**
- **実行ファイル**: `755` (`rwxr-xr-x`)
- **設定ファイル**: `644` (`rw-r--r--`)
- **機密ファイル**: `600` (`rw-------`)

### 3. **定期メンテナンス**
- **週次**: 不要ファイル削除
- **月次**: ログアーカイブ
- **四半期**: 構造レビュー

## 🔄 **移行・整理プロセス**

### 1. **現状分析**
```bash
# 重複ファイル検出
find . -name "* 2.*" -type f

# 空ディレクトリ検出
find . -type d -empty

# 大容量ファイル検出
find . -size +10M -type f
```

### 2. **自動クリーンアップ**
```bash
# 重複削除
find . -name "* 2.*" -type f -delete

# バックアップ削除
find . -name "*.bak" -o -name "*.backup" -type f -delete

# 空ディレクトリ削除
find . -type d -empty -delete
```

### 3. **構造検証**
```bash
# システム検証実行
./ai-agents/scripts/validate-system.sh

# 設定妥当性確認
./ai-agents/scripts/load-config.sh validate
```

## 📈 **継続的改善**

### 1. **監視指標**
- ディレクトリ階層の深さ
- 重複ファイル数
- 未使用ファイル数
- 総ファイルサイズ

### 2. **自動化ツール**
- 定期クリーンアップスクリプト
- 構造検証の自動実行
- レポート生成

### 3. **レビュープロセス**
- 新規ファイル追加時の配置確認
- 月次の構造レビュー
- 四半期の大幅見直し

---

**このルールに従うことで、プロジェクトは常に整理された状態を維持し、開発効率を最大化できます。**