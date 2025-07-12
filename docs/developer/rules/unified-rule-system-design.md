# 🎯 統合ルールシステム設計書

**日付**: 2025-07-05  
**設計者**: PRESIDENT AI + O3分析  
**目標**: エンタープライズグレード統合ルール体系の確立  
**適用範囲**: プロジェクト全体（チーム拡大対応）

## 🏗️ 設計概要

### **現在の問題**
- **500行超のルール散在**: globals.mdc (180行) + CLAUDE.md (192行) + 個別.mdc
- **重複・矛盾**: 作業記録ルールが複数ファイルに重複記載
- **優先順位不明**: ルール衝突時の解決手順未定義
- **検索困難**: 必要なルールの所在が不明確

### **解決方針**
1. **Single Source of Truth**: 階層化されたYAML形式のルール体系
2. **自動化優先**: CI/CDでルール違反を自動検出
3. **優先順位明示**: 数字プレフィックスで強制的な優先順位
4. **変更管理**: semantic versioningでルール変更追跡

## 📁 新ルール体系構造

### **ディレクトリ構造**
```
docs/rules/
├── 0-ROOT.yml              # 最上位ポリシー（変更には全員合意必要）
├── 1-GLOBAL.yml            # チーム横断の一般規約
├── 2-DOMAIN/               # ドメイン別詳細ルール
│   ├── ai-memory.yml       # AI記憶システム専用
│   ├── cursor-ide.yml      # Cursor IDE連携
│   ├── claude-code.yml     # Claude Code専用
│   ├── testing.yml         # テスト関連
│   ├── documentation.yml   # ドキュメント作成
│   └── security.yml        # セキュリティ関連
├── 3-LOCAL/                # 実験・一時的ルール
│   ├── experiments/        # 実験的機能
│   └── deprecated/         # 廃止予定ルール
├── templates/              # ファイル作成テンプレート
│   ├── code/              # ソースコードテンプレート
│   ├── docs/              # ドキュメントテンプレート
│   └── tests/             # テストテンプレート
├── flows/                  # 意思決定フロー
│   ├── file-creation.drawio # ファイル作成決定木
│   └── rule-conflict.drawio # ルール衝突解決フロー
└── legacy/                 # 移行前の旧ルール（参考用）
    ├── globals.mdc.backup
    └── CLAUDE.md.backup
```

### **優先順位システム**
```yaml
# 優先順位: 数字プレフィックスで明示（小さい数字 = 高優先）
0-ROOT.yml      # 最高優先（プロジェクト憲法レベル）
1-GLOBAL.yml    # 高優先（チーム標準）
2-DOMAIN/*.yml  # 中優先（専門分野）
3-LOCAL/*.yml   # 低優先（実験・一時的）

# ルール衝突時の解決:
# 1. 上位数字のルールが勝つ
# 2. 同レベルなら新しいルールが勝つ
# 3. 解決不能なら Issue起票 → 48h以内解決
```

## 📄 ルールファイル設計

### **0-ROOT.yml（プロジェクト憲法）**
```yaml
version: "1.0.0"
last_updated: "2025-07-05"
scope: "entire_project"
change_policy: "unanimous_consensus"

core_principles:
  - id: "integrity"
    rule: "証拠なき報告は絶対禁止"
    enforcement: "automatic"
  
  - id: "responsibility" 
    rule: "職務放棄は重大違反"
    enforcement: "manual_review"
  
  - id: "documentation"
    rule: "全作業は記録必須"
    enforcement: "git_hooks"

file_naming:
  pattern: "^[a-z0-9_-]+\\.(py|md|yml|sh)$"
  forbidden: ["tmp", "temp", "test123"]
  
directory_structure:
  max_root_dirs: 9
  required_dirs: ["src", "docs", "tests"]
  forbidden_at_root: ["logs", "tmp", "data"]
```

### **1-GLOBAL.yml（チーム標準）**
```yaml
version: "1.0.0"
inherits: ["0-ROOT.yml"]
scope: "team_wide"

coding_standards:
  python:
    formatter: "black"
    linter: "ruff"
    max_line_length: 88
  
  markdown:
    formatter: "prettier"
    max_line_length: 100

git_workflow:
  branch_naming: "feature/|fix/|docs/"
  commit_message: "conventional_commits"
  require_issue_reference: true

review_process:
  min_reviewers: 1
  require_tests: true
  require_docs_update: true
```

### **2-DOMAIN/claude-code.yml（Claude Code専用）**
```yaml
version: "1.0.0"
inherits: ["1-GLOBAL.yml"]
scope: "claude_code_interactions"

startup_sequence:
  phase_0_checks:
    - "cursor_rules_validation"
    - "claude_md_confirmation" 
    - "memory_system_status"
  
  required_files:
    - ".cursor/rules/globals.mdc"
    - "docs/instructions/CLAUDE.md"
    - "src/ai/memory/core/session-bridge.sh"

response_patterns:
  confidence_thresholds:
    high: 0.95    # 断定表現許可
    medium: 0.8   # 「推定では」表現
    low: 0.6      # 「おそらく」表現

failure_recording:
  location: "docs/memory/failures/"
  format: "FAIL-XXX_YYYY-MM-DD.md"
  required_sections: ["経緯", "原因", "対策", "防止策"]
```

## 🔄 自動化システム設計

### **1. ルール違反検出**
```yaml
# .github/workflows/rule-validation.yml
name: Rule Validation
on: [push, pull_request]

jobs:
  validate_rules:
    runs-on: ubuntu-latest
    steps:
      - name: Check file naming
        run: python scripts/validate-file-names.py
      
      - name: Check directory structure  
        run: python scripts/validate-directory.py
      
      - name: Check rule conflicts
        run: python scripts/check-rule-conflicts.py
      
      - name: Generate rule documentation
        run: make generate-docs
```

### **2. 知識重複検出**
```python
# scripts/detect-knowledge-duplicates.py
def weekly_duplicate_scan():
    """週次で知識重複をスキャン"""
    findings = []
    
    # docs/以下のMarkdownファイル解析
    for doc_file in Path("docs").rglob("*.md"):
        content_hash = hash_semantic_content(doc_file)
        if content_hash in content_database:
            findings.append({
                'duplicate': doc_file,
                'original': content_database[content_hash],
                'similarity': calculate_similarity(doc_file, original)
            })
    
    # Issue自動起票
    if findings:
        create_github_issue("Knowledge Duplication Detected", findings)
```

### **3. ファイル作成支援**
```bash
# scripts/create-file-with-rules.sh
#!/bin/bash
# ルールに従った新ファイル作成支援

file_path="$1"
file_type="$2"

# ルール適用順序の確認
echo "🔍 適用ルール確認中..."
python scripts/get-applicable-rules.py "$file_path" "$file_type"

# テンプレート選択
template=$(python scripts/select-template.py "$file_type")
echo "📄 テンプレート: $template"

# ファイル生成
cp "docs/rules/templates/$template" "$file_path"

# 自動検証
python scripts/validate-new-file.py "$file_path"
echo "✅ ファイル作成完了: $file_path"
```

## 📊 移行計画

### **Phase 1: 基盤構築（今日）**
1. ✅ docs/rules/ディレクトリ構造作成
2. ✅ 重複分析スクリプト作成
3. ✅ 0-ROOT.yml基本版作成
4. ✅ レガシーファイルのバックアップ

### **Phase 2: コア移行（1週間）**
1. 🔄 globals.mdcとCLAUDE.mdをYAML化
2. 🔄 ドメイン別ルールファイル作成
3. 🔄 テンプレートシステム構築
4. 🔄 基本的な自動検証スクリプト

### **Phase 3: 自動化（1ヶ月）**
1. 🔄 CI/CD統合
2. 🔄 GitHub Issue連携
3. 🔄 週次重複検出システム
4. 🔄 ルール変更通知システム

## 🎯 成功指標

### **定量指標**
- **ルール検索時間**: 30秒 → 5秒以下
- **ルール違反検出**: 手動 → 100%自動化
- **ナレッジ重複**: 現在推定20% → 5%以下
- **新人オンボーディング**: 3日 → 1日

### **定性指標**
- **一貫性**: 全チームメンバーが同じルールを参照
- **透明性**: ルール変更理由と影響範囲が明確
- **拡張性**: チーム拡大時も運用コストが線形増加しない
- **保守性**: ルール更新が容易で影響分析が自動化

## 🔮 将来展望

### **AI活用の拡張**
1. **自動ルール生成**: 頻繁な手動修正パターンからルール自動提案
2. **自然言語クエリ**: 「Python関数命名規則は？」→ 該当ルール即座表示
3. **予測的ガイダンス**: ファイル作成時に必要になるルール事前提示

### **メトリクス・分析**
1. **ルール遵守率**: チーム・個人別のコンプライアンススコア
2. **生産性影響**: ルール自動化による開発速度向上測定
3. **品質相関**: ルール遵守度とバグ率の相関分析

---

**📍 この統合ルールシステムにより、エンタープライズレベルの一貫性と自動化を実現し、チーム拡大時も安定した品質を維持できます。**

**🎯 目標**: ルール管理の完全自動化と、開発者の認知負荷ゼロでの高品質開発環境の実現