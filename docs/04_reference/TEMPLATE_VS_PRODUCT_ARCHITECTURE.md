# 🏗️ テンプレート vs プロダクト固有 - アーキテクチャ設計

## 明確な分離戦略

### ディレクトリ構造
```
/Users/dd/Desktop/1_dev/coding-rule2/
├── templates/                  # 固定テンプレート（バージョン管理）
│   ├── ai_systems/            # AI安全システム基盤
│   │   ├── constitutional_ai_base.py
│   │   ├── rule_based_rewards_base.py
│   │   └── monitoring_base.py
│   ├── db/                    # データベース基盤
│   │   ├── base_migrations/
│   │   ├── common_models.py
│   │   └── connection_pool.py
│   ├── ui/                    # UI基盤
│   │   ├── dashboard_base.py
│   │   ├── worker_panel_base.py
│   │   └── command_interface_base.py
│   └── utils/                 # 共通ユーティリティ
│       ├── logger.py
│       ├── config.py
│       └── validators.py
│
├── products/                  # プロダクト固有（柔軟に変化）
│   ├── coding_rule2/         # 現在のプロダクト
│   │   ├── config/
│   │   │   ├── ai_config.json
│   │   │   ├── db_config.json
│   │   │   └── ui_config.json
│   │   ├── extensions/
│   │   │   ├── custom_ai_rules.py
│   │   │   ├── project_specific_monitors.py
│   │   │   └── custom_dashboard.py
│   │   ├── migrations/
│   │   │   ├── 001_project_tables.py
│   │   │   └── 002_custom_indexes.py
│   │   └── data/
│   │       ├── project_specific_data.json
│   │       └── custom_prompts.json
│   │
│   └── future_product/       # 将来のプロダクト
│       ├── config/
│       ├── extensions/
│       └── migrations/
│
├── src/                      # 現在の実装（移行対象）
└── runtime/                  # 実行時データ
```

## 実装ルール

### 1. テンプレート（固定）
```python
# templates/ai_systems/constitutional_ai_base.py
class ConstitutionalAIBase:
    """固定基盤クラス - 修正禁止"""
    
    def __init__(self, config_path: str):
        self.config = self.load_config(config_path)
    
    def validate_response(self, response: str) -> bool:
        """基本検証ロジック"""
        # 固定実装
        pass
    
    def before_validate(self, response: str) -> str:
        """拡張ポイント"""
        return response
    
    def after_validate(self, result: bool) -> bool:
        """拡張ポイント"""
        return result
```

### 2. プロダクト固有（柔軟）
```python
# products/coding_rule2/extensions/custom_ai_rules.py
from templates.ai_systems.constitutional_ai_base import ConstitutionalAIBase

class CodingRule2AI(ConstitutionalAIBase):
    """プロダクト固有のAI拡張"""
    
    def before_validate(self, response: str) -> str:
        """プロダクト固有の前処理"""
        # {{mistake_count}}回ミス防止の特別チェック
        if "完了しました" in response and "証拠" not in response:
            return response + " [証拠不足警告]"
        return response
    
    def after_validate(self, result: bool) -> bool:
        """プロダクト固有の後処理"""
        # ログ記録など
        return result
```

## データベース設計

### 1. 共通スキーマ（テンプレート）
```sql
-- templates/db/base_migrations/001_core_tables.sql
CREATE SCHEMA IF NOT EXISTS core;

CREATE TABLE core.ai_systems (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    system_type VARCHAR(50) NOT NULL,
    version VARCHAR(20) NOT NULL,
    config JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE core.monitoring_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type VARCHAR(50) NOT NULL,
    event_data JSONB NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);
```

### 2. プロダクト固有スキーマ
```sql
-- products/coding_rule2/migrations/001_project_tables.sql
CREATE SCHEMA IF NOT EXISTS coding_rule2;

CREATE TABLE coding_rule2.mistake_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pattern_type VARCHAR(50) NOT NULL,
    pattern_data JSONB NOT NULL,
    occurrences INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE coding_rule2.conversation_context (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(100) NOT NULL,
    context_data JSONB NOT NULL,
    vector_embedding vector(1536),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

## 設定管理

### 1. テンプレート設定
```json
// templates/config/base_config.json
{
  "ai_systems": {
    "constitutional_ai": {
      "enabled": true,
      "violation_threshold": 0.8,
      "auto_correction": true
    },
    "rule_based_rewards": {
      "enabled": true,
      "scoring_algorithm": "weighted_sum"
    }
  },
  "database": {
    "connection_pool_size": 20,
    "query_timeout": 30,
    "retry_attempts": 3
  }
}
```

### 2. プロダクト固有設定
```json
// products/coding_rule2/config/ai_config.json
{
  "extends": "templates/config/base_config.json",
  "ai_systems": {
    "constitutional_ai": {
      "violation_threshold": 0.6,
      "custom_rules": [
        "prevent_false_completion",
        "enforce_evidence_requirement"
      ]
    },
    "mistake_prevention": {
      "enabled": true,
      "max_mistakes": 88,
      "learning_rate": 0.1
    }
  },
  "project_specific": {
    "coding_style": "python",
    "documentation_format": "markdown",
    "test_framework": "pytest"
  }
}
```

## 実装方針

### 1. 段階的移行
```bash
# Phase 1: テンプレート抽出
mkdir -p templates/ai_systems
cp src/ai/constitutional_ai.py templates/ai_systems/constitutional_ai_base.py

# Phase 2: プロダクト固有分離
mkdir -p products/coding_rule2/extensions
# カスタム実装を分離

# Phase 3: 設定統合
mkdir -p products/coding_rule2/config
# 設定ファイルを分離
```

### 2. CI/CD強制
```yaml
# .github/workflows/template_protection.yml
name: Template Protection
on:
  pull_request:
    paths:
      - 'templates/**'
jobs:
  protect-templates:
    runs-on: ubuntu-latest
    steps:
      - name: Check template changes
        run: |
          if [ "${{ github.actor }}" != "template-owner" ]; then
            echo "テンプレート変更は承認が必要です"
            exit 1
          fi
```

## 結論

**テンプレートは固定・バージョン管理、プロダクト固有は柔軟に進化**

1. **templates/**　- 固定、semver管理
2. **products/**　- 柔軟、継続的改善
3. **DB設計**　- スキーマ分離、マイグレーション独立
4. **設定管理**　- 継承ベース、オーバーライド可能