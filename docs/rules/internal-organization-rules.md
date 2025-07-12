# 📋 内部組織ルール - ディレクトリ内整理規約

**最終更新**: 2025-07-05  
**適用範囲**: 全ディレクトリ内部構造  
**優先度**: 必須（0-ROOT.yml準拠）

## 🎯 基本原則

### 1. **単一責任の原則**
- 各ディレクトリは明確な単一目的を持つ
- 混在は厳禁（例: scripts/にドキュメント配置禁止）

### 2. **階層制限の原則** 
- **最大5階層**まで（`a/b/c/d/e/file.ext`）
- 6階層以上は強制的にリファクタリング対象

### 3. **命名統一の原則**
- **kebab-case必須**: `file-name.ext`
- **小文字必須**: 大文字混在禁止
- **特殊文字禁止**: スペース、記号（.-_以外）

## 📁 ディレクトリ別整理ルール

### **scripts/** - 実行スクリプト専用
```
scripts/
├── setup/              # セットアップ関連
├── deployment/         # デプロイ関連  
├── maintenance/        # メンテナンス
├── analysis/          # 分析ツール
└── template/          # テンプレート生成
```

**配置ルール**:
- ✅ 実行可能な.sh, .pyファイルのみ
- ❌ ドキュメント、設定ファイル配置禁止
- ❌ src/内のスクリプト（ライブラリ除く）

### **docs/** - ドキュメント統合管理
```
docs/
├── enduser/           # エンドユーザー向け
├── developer/         # 開発者向け
├── operator/          # 運用者向け
├── rules/            # ルール・ポリシー
├── reports/          # レポート・ログ
└── misc/             # その他ドキュメント
```

**配置ルール**:
- ✅ .md, .txt, .rst ファイル
- ✅ 図表、画像ファイル
- ❌ 実行可能ファイル
- ❌ 設定ファイル

### **config/** - 設定ファイル専用
```
config/
├── system/           # システム設定
├── agents/           # エージェント設定
├── integrations/     # 外部連携設定
└── environments/     # 環境別設定
```

**配置ルール**:
- ✅ .json, .yml, .yaml, .toml, .env
- ✅ 設定テンプレート
- ❌ ドキュメント、実行ファイル

### **src/** - ソースコード専用
```
src/
├── api/             # API実装
├── ai/              # AI関連ロジック
├── integrations/    # 外部システム連携
├── tests/           # ユニット・統合テスト
└── notebooks/       # Jupyter notebook
```

**配置ルール**:
- ✅ .py, .js, .ts ソースコード
- ✅ ライブラリ、モジュール
- ❌ 実行用スクリプト（scripts/へ）
- ❌ ドキュメント（docs/へ）

### **runtime/** - 実行時データ専用
```
runtime/
├── cache/           # キャッシュデータ
├── logs/           # ログファイル
├── tmp/            # 一時ファイル
└── data/           # 処理済みデータ
```

**配置ルール**:
- ✅ .log, .json, .csv データファイル
- ✅ 一時的・揮発性ファイル
- ❌ 永続的ドキュメント（docs/へ）
- ❌ 設定ファイル（config/へ）

## 🔧 命名規則詳細

### **ファイル命名**
```bash
# ✅ 正しい例
user-management.py
api-client.js
database-config.yml
setup-environment.sh

# ❌ 間違った例  
UserManagement.py      # PascalCase禁止
API_Client.js          # snake_case + 大文字禁止
database config.yml    # スペース禁止
setup&deploy.sh        # 特殊文字禁止
```

### **ディレクトリ命名**
```bash
# ✅ 正しい例
user-management/
api-clients/
database-configs/

# ❌ 間違った例
UserManagement/        # PascalCase禁止
API_Clients/          # 大文字禁止
database configs/     # スペース禁止
```

## 🚫 禁止パターン

### **絶対禁止**
1. **混在配置**: scripts/にREADME.md
2. **深すぎる階層**: `a/b/c/d/e/f/file.ext`
3. **重複ファイル**: 同じ内容の複数ファイル
4. **命名違反**: 大文字、スペース、特殊文字

### **即座削除対象**
```bash
# 空ディレクトリ
find . -type d -empty -delete

# 一時ファイル
rm -f **/*.tmp **/*.temp **/*~

# 重複ファイル  
# 分析後に手動確認して削除
```

## 🔄 整理フロー

### **Phase 1: 分析**
```bash
# 現状分析実行
python3 scripts/analyze-internal-structure.py
```

### **Phase 2: 自動修正**
```bash
# 命名規則適用
python3 scripts/apply-naming-rules.py

# ファイル移動
python3 scripts/reorganize-internal-files.py
```

### **Phase 3: 手動確認**
```bash
# 重複ファイル確認
python3 scripts/review-duplicates.py

# 構造検証
python3 scripts/validate-internal-structure.py
```

## 📊 品質指標

### **目標値**
- **散在ドキュメント**: 0個
- **命名違反**: 0個  
- **重複ファイル**: 0組
- **最大階層深度**: 5以下
- **空ディレクトリ**: 0個

### **監視指標**
- **週次チェック**: 新規違反の早期発見
- **月次レビュー**: 構造最適化の検討
- **四半期監査**: 大幅リファクタリング判断

## ⚖️ 例外ルール

### **許可される例外**
1. **legacy/ディレクトリ**: 移行中の旧ファイル（期限付き）
2. **vendor/ディレクトリ**: サードパーティファイル
3. **node_modules/**: NPMパッケージ（除外対象）

### **例外申請プロセス**
1. **docs/rules/exceptions.md**に記録
2. **期限設定必須**（最大3ヶ月）
3. **定期レビュー**で再評価

---

**🎯 このルールにより、内部構造の一貫性と保守性を確保します**

**📋 遵守チェック**: 毎週金曜日に自動実行**