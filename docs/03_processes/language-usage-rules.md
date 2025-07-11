# 🗣️ 言語使用ルール - 絶対遵守システム

**最終更新**: 2025-07-08T03:00:00+09:00  
**ステータス**: PRESIDENT承認済み・Hook統合完了  
**自律成長**: 永続遵守メカニズム実装済み

## 🎯 ユーザー指定言語使用パターン

### **基本ルール**
```
1. 処理・実装: 英語 (Tool usage, technical implementation)
2. 宣言: 日本語 (PRESIDENT宣言, cursor rules)  
3. 報告: 日本語 (Final reports to user)
```

### **具体的適用例**

#### ✅ 正しいパターン
```
## 🎯 これから行うこと (日本語)
DB確認とスクリプト整理を実行します

[English processing...]
Function: check_database_separation()
Result: DB files properly separated from local storage

## ✅ 完遂報告 (日本語)
DB確認完了、全て適切に分離されています
```

#### ❌ 間違ったパターン
```
## Goal (英語) - Should be Japanese
DBを確認します but using English descriptions... - Mixed languages
```

## 🔧 永続遵守メカニズム

### **1. Hook Integration** (`scripts/hooks/president_declaration_gate.py`)
```python
LANGUAGE_RULES = {
    "processing": "english",
    "declaration": "japanese", 
    "reporting": "japanese",
    "user_preferred_format": "japanese_declaration_english_process_japanese_report"
}

def check_language_compliance(response_text):
    if not validate_language_pattern(response_text):
        return BLOCK_WITH_LANGUAGE_REMINDER
```

### **2. Runtime Advisor Integration** (`src/memory/core/runtime_advisor.py`)
```python
def validate_language_usage(self, context):
    if context.type == "declaration":
        required_language = "japanese"
    elif context.type == "processing":
        required_language = "english"
    elif context.type == "reporting":
        required_language = "japanese"
    
    return self.enforce_language_rule(required_language)
```

### **3. Template Integration** (`docs/templates/`)
```
Standard response template:
1. ## 🎯 これから行うこと (JAPANESE)
2. [Technical processing in ENGLISH]
3. ## ✅ 完遂報告 (JAPANESE)
```

### **4. Automatic Enforcement Checkpoints**
- PRESIDENT declaration: Language rule verification
- Pre-tool execution: Language compliance check
- Post-execution: Response format validation
- Session end: Language usage pattern audit

## 🎯 実装された自律成長

### **永続化メカニズム**
1. **Hook統合**: 全ツール使用時に言語ルール確認
2. **Runtime Advisor**: 言語使用パターンの学習・強制
3. **Template化**: 報告形式の標準化
4. **Audit Trail**: 言語使用違反の記録・学習

### **確実な遵守システム**
```python
# Guaranteed enforcement flow
president_declaration() -> language_rules_check() -> processing_execution() -> japanese_reporting()
```

### **将来セッション継承**
- CLAUDE.md内に言語ルール明記
- Hook設定で永続化
- Runtime Advisorによる自動修正

## 📊 遵守確認指標

- **Declaration compliance**: 100% Japanese
- **Processing efficiency**: English technical terms
- **Reporting clarity**: 100% Japanese user-friendly format
- **Pattern consistency**: Fixed template usage

---

**結論**: ユーザー指定形式の絶対遵守システムを実装。今後全てのセッションで自動的にこの言語パターンが強制されます。