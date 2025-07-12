# 🔒 厳格ファイル・フォルダ作成ルール

**最終更新**: 2025-07-05  
**適用範囲**: 全新規ファイル・フォルダ作成  
**優先度**: 必須（production-grade enforcement）  
**準拠基準**: Enterprise Best Practices 2024-2025

## 🎯 基本原則

### 1. **Fail-Fast Policy（高速失敗原則）**
- 作成前検証で問題を即座に検出
- ローカル環境で失敗させ、CIは安全網として機能

### 2. **Policy as Code（ポリシーのコード化）**
- 全ルールはコードで定義・自動実行
- 手動チェックは一切不要

### 3. **Cross-Platform Safety（クロスプラットフォーム安全性）**
- Windows, macOS, Linux, クラウドストレージ対応
- 大文字小文字の違いによる衝突防止

## 📋 作成前検証チェックリスト

### **Phase 1: 命名検証**
```yaml
naming_validation:
  # 文字セット検証
  allowed_chars: "^[a-z0-9]+(-[a-z0-9]+)*$"
  
  # 長さ制限
  max_length:
    file_name: 50
    folder_name: 40
    full_path: 240
  
  # 禁止パターン
  forbidden_patterns:
    - "^[0-9]"          # 数字開始禁止
    - "--"              # 連続ハイフン禁止
    - "-$"              # ハイフン終了禁止
    - "^-"              # ハイフン開始禁止
  
  # OS予約語
  reserved_words:
    windows: ["con", "prn", "aux", "nul", "com1-9", "lpt1-9"]
    unix: [".", "..", "~"]
    
  # 拡張子ルール
  extension_rules:
    multiple_dots: false  # file.test.js 禁止
    max_extension_length: 10
```

### **Phase 2: 構造検証**
```yaml
structure_validation:
  # 階層深度チェック
  max_depth: 5
  
  # ディレクトリ配置ルール
  placement_rules:
    scripts: 
      allowed: [".sh", ".py"]
      forbidden: [".md", ".txt", ".json"]
    docs:
      allowed: [".md", ".txt", ".rst"]
      forbidden: [".sh", ".py", ".js"]
    config:
      allowed: [".json", ".yml", ".yaml", ".toml", ".env"]
      forbidden: [".sh", ".py", ".md"]
    src:
      allowed: [".py", ".js", ".ts", ".jsx", ".tsx"]
      forbidden: [".sh", ".md"]
```

### **Phase 3: セキュリティ検証**
```yaml
security_validation:
  # 機密情報パターン検出
  sensitive_patterns:
    filenames: ["secret", "key", "password", "token", "credential"]
    content_scan: true
    
  # PII/データ分類
  data_classification:
    required_tags: ["-public", "-internal", "-confidential"]
    tag_position: "suffix"
    
  # アクセス制御
  access_control:
    production_paths: ["prod/", "production/"]
    restricted_to: ["svc-prod-deploy", "admin-role"]
```

### **Phase 4: メタデータ要件**
```yaml
metadata_requirements:
  # 必須メタデータ
  required_fields:
    - owner         # 所有者/チーム
    - purpose       # 目的
    - created_date  # 作成日時（UTC）
    - expires       # 有効期限（一時ファイルの場合）
    
  # タイムスタンプ形式
  timestamp_format: "yyyymmddThhmmssZ"  # 20250705T164500Z
  
  # ドキュメント要件
  documentation:
    readme_required: true  # 新規ディレクトリ
    changelog_required: true  # 変更履歴
```

## 🤖 自動実行メカニズム

### **1. Pre-Creation Hook**
```bash
#!/bin/bash
# .githooks/pre-create-validate.sh

validate_name() {
    local name="$1"
    local type="$2"  # file or folder
    
    # 文字セット検証
    if ! [[ "$name" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
        echo "❌ Invalid $type name: $name"
        echo "   Must use only lowercase letters, numbers, and hyphens"
        return 1
    fi
    
    # 長さ検証
    if [ "$type" = "file" ] && [ ${#name} -gt 50 ]; then
        echo "❌ File name too long: ${#name} chars (max: 50)"
        return 1
    fi
    
    # 予約語チェック
    if is_reserved_word "$name"; then
        echo "❌ Reserved word detected: $name"
        return 1
    fi
    
    return 0
}

validate_placement() {
    local file_path="$1"
    local dir=$(dirname "$file_path")
    local ext="${file_path##*.}"
    
    # ディレクトリ別配置ルール適用
    case "$dir" in
        */scripts/*)
            if [[ "$ext" =~ ^(md|txt|json)$ ]]; then
                echo "❌ Document files not allowed in scripts/"
                return 1
            fi
            ;;
        */docs/*)
            if [[ "$ext" =~ ^(sh|py|js)$ ]]; then
                echo "❌ Executable files not allowed in docs/"
                return 1
            fi
            ;;
    esac
    
    return 0
}

# メイン検証フロー
main() {
    local target_path="$1"
    local name=$(basename "$target_path")
    local type="file"
    
    [ -d "$target_path" ] && type="folder"
    
    # 全検証実行
    validate_name "$name" "$type" || exit 1
    validate_placement "$target_path" || exit 1
    validate_security "$target_path" || exit 1
    create_metadata "$target_path" || exit 1
    
    echo "✅ All validations passed for: $target_path"
}

main "$@"
```

### **2. IDE統合（VSCode設定例）**
```json
{
  "files.participants": [
    {
      "id": "file-creation-validator",
      "onWillCreateFiles": {
        "command": "validateFileCreation",
        "arguments": ["${file}"]
      }
    }
  ],
  "validateFileCreation.rules": {
    "namingPattern": "^[a-z0-9]+(-[a-z0-9]+)*$",
    "maxLength": 50,
    "autoFix": true
  }
}
```

### **3. CI/CDパイプライン統合**
```yaml
# .github/workflows/file-validation.yml
name: File Structure Validation

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Validate File Names
        run: |
          python3 scripts/validate-file-structure.py --strict
          
      - name: Check Placement Rules
        run: |
          python3 scripts/check-placement-rules.py
          
      - name: Security Scan
        run: |
          gitleaks detect --source . --verbose
          
      - name: Generate Compliance Report
        if: always()
        run: |
          python3 scripts/generate-compliance-report.py > compliance.sarif
          
      - uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: compliance.sarif
```

## 📊 実装優先順位

### **Phase 1: 即座実装（Day 1）**
1. 命名規則検証
2. 文字セット制限
3. 長さ制限
4. Pre-commitフック

### **Phase 2: 短期実装（Week 1）**
1. ディレクトリ配置ルール
2. 予約語ブロック
3. IDE統合
4. 基本セキュリティスキャン

### **Phase 3: 中期実装（Month 1）**
1. メタデータ自動生成
2. アクセス制御統合
3. 完全CI/CD統合
4. コンプライアンスレポート

## 🔍 検証例

### ✅ 正しい例
```bash
# ファイル作成
src/user-management/auth-service.py
docs/api/user-guide.md
config/environments/production.yml
scripts/deploy-app.sh

# フォルダ作成
src/payment-processing/
tests/integration/
docs/architecture/
```

### ❌ 間違った例
```bash
# 違反例と理由
src/UserManagement/       # 大文字禁止
scripts/README.md         # ドキュメントは docs/ へ
config/prod_settings.yml  # アンダースコア禁止
src/api/test.sh          # 実行スクリプトは scripts/ へ
docs/api-key.txt         # 機密情報パターン検出
```

## 🚀 自動修正機能

```python
# scripts/auto-fix-naming.py
import re
from pathlib import Path

class FileNameAutoFixer:
    def fix_name(self, name: str) -> str:
        """不正な名前を自動修正"""
        # 大文字を小文字に
        name = name.lower()
        
        # 特殊文字をハイフンに
        name = re.sub(r'[^a-z0-9\-\.]', '-', name)
        
        # 連続ハイフンを単一に
        name = re.sub(r'-+', '-', name)
        
        # 先頭末尾のハイフンを削除
        name = name.strip('-')
        
        # 長さ制限
        if len(name) > 50:
            name = name[:47] + '...'
            
        return name
```

## 📈 コンプライアンス指標

### **追跡メトリクス**
- Pre-commit失敗率（目標: < 5%）
- 命名規則違反数/週（目標: 0）
- 自動修正成功率（目標: > 90%）
- ポリシー準拠率（目標: 100%）

### **監査ログ**
```json
{
  "timestamp": "2025-07-05T16:45:00Z",
  "action": "file_created",
  "path": "src/auth/login-service.py",
  "validations": {
    "naming": "passed",
    "placement": "passed",
    "security": "passed",
    "metadata": "generated"
  },
  "user": "dev-user-123",
  "auto_fixed": false
}
```

---

**🔒 このルールにより、エンタープライズグレードのファイル作成標準を確保します**

**⚡ 全検証は自動化され、開発者の生産性を損なうことなく品質を保証します**