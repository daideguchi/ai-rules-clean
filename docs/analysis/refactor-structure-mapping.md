# プロジェクト構造リファクタリングマッピング

## 現在のルートディレクトリ分析（20個以上）

### 移動先マッピング戦略

#### 1. **src/** - すべてのソースコード
```
現在 → 新構造
├── src/ai/ → src/ai/
├── src/hooks/ → src/hooks/
├── src/integrations/ → src/integrations/
├── src/logs/ → runtime/logs/
└── scripts/ → src/scripts/
```

#### 2. **docs/** - 統合されたドキュメント
```
現在 → 新構造
├── docs/ → docs/
├── README.md → docs/README.md
├── README_backup.md → docs/legacy/README_backup.md
├── AI_INTERACTIONS_LOG.md → docs/logs/AI_INTERACTIONS_LOG.md
├── FILE_OPERATIONS_LOG.md → docs/logs/FILE_OPERATIONS_LOG.md
└── MISTAKE_79_PREVENTION_REPORT.md → docs/reports/MISTAKE_79_PREVENTION_REPORT.md
```

#### 3. **config/** - システム設定とエージェント設定
```
現在 → 新構造
├── config/ → config/
├── .mcp.json → config/mcp.json
├── pyproject.toml → config/pyproject.toml
├── memory/core/memory-env.conf → config/memory/memory-env.conf
└── src/ai/memory/core/hooks.js → config/memory/hooks.js
```

#### 4. **runtime/** - 実行時データとログ
```
現在 → 新構造
├── runtime/ → runtime/
├── src/logs/ → runtime/logs/
├── src/ai/memory/core/session-records/ → runtime/memory/sessions/
└── src/ai/memory/core/locks/ → runtime/memory/locks/
```

#### 5. **ops/** - インフラストラクチャとDevOps
```
現在 → 新構造
├── ops/ → ops/
├── scripts/deploy.sh → ops/deploy/deploy.sh
├── scripts/setup-dev-environment.sh → ops/setup/setup-dev-environment.sh
└── scripts/setup-portable.sh → ops/setup/setup-portable.sh
```

#### 6. **assets/** - 静的リソース
```
現在 → 新構造
├── assets/ → assets/
└── src/integrations/gemini/gemini_chat_ui.html → assets/ui/gemini_chat_ui.html
```

#### 7. **scripts/** - 自動化スクリプト（統合）
```
現在 → 新構造
├── scripts/ → scripts/
├── quick-memory-check.sh → scripts/memory/quick-memory-check.sh
├── start-with-hooks.sh → scripts/startup/start-with-hooks.sh
└── test-memory-inheritance.sh → scripts/test/test-memory-inheritance.sh
```

#### 8. **tests/** - テストとQAファイル
```
現在 → 新構造
├── src/ai/memory/enhanced/test-plan.md → tests/memory/test-plan.md
├── claude-restart-checklist.md → tests/checklists/claude-restart-checklist.md
└── refactor-strategy-o3-analysis.md → tests/analysis/refactor-strategy-o3-analysis.md
```

## Git履歴保持戦略

### 1. 段階的移動（1日1カテゴリ）
```bash
# Day 1: src/ 統合
git mv scripts/ai-* src/scripts/
git mv scripts/claude-* src/scripts/
git commit -m "refactor: consolidate AI scripts into src/scripts/"

# Day 2: docs/ 統合
git mv *.md docs/legacy/
git commit -m "refactor: consolidate documentation into docs/"

# Day 3-8: 残りのカテゴリ
```

### 2. 並行作業ブランチ戦略
```bash
# 複数のClaude Codeセッションで並行作業
git worktree add ../temp-src feature/restructure-src
git worktree add ../temp-docs feature/restructure-docs
git worktree add ../temp-config feature/restructure-config
```

### 3. 自動化スクリプトによる段階的移動
```bash
# 移動前バックアップ
cp -r . ../backup-$(date +%Y%m%d-%H%M%S)

# 移動履歴追跡
git log --follow --name-status > move-history.log
```

## システム稼働継続保証

### 1. 重要システムファイル優先保護
- `src/ai/memory/core/hooks.js`
- `src/ai/memory/enhanced/session-inheritance-bridge.sh`
- `runtime/system-state.json`

### 2. シンボリックリンクによる互換性維持
```bash
# 移動後に古いパスからのシンボリックリンク作成
ln -s src/scripts/ai-team.sh ai-team.sh
ln -s config/memory/memory-env.conf memory/core/memory-env.conf
```

### 3. 段階的テスト実行
```bash
# 各段階後にシステムテスト実行
./scripts/test/validate-structure.sh
./scripts/startup/start-with-hooks.sh --test-mode
```

## 自動化継続システム設計

### 1. ファイル作成監視システム
```python
# scripts/structure-monitor.py
import watchdog
from pathlib import Path

class StructureMonitor:
    def __init__(self):
        self.max_root_dirs = 8
        self.allowed_roots = ['src', 'docs', 'config', 'runtime', 'ops', 'assets', 'scripts', 'tests']
    
    def monitor_structure(self):
        # 新しいルートディレクトリ作成を監視
        # 8個制限を超えた場合、適切な場所に自動移動
        pass
```

### 2. 継続的整理フック
```bash
# .git/hooks/pre-commit
#!/bin/bash
# 構造違反チェック
./scripts/validate-structure.sh || exit 1
```

### 3. 自動分類AI
```python
# scripts/auto-categorize.py
# 新しいファイルを適切なカテゴリに自動分類
def categorize_file(file_path):
    # AI-based file categorization
    pass
```