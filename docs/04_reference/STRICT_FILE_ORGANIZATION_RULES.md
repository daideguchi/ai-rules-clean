# Strict File Organization Rules - 絶対遵守システム (coding-rule2専用)

⚠️ **重要**: これらのルールは`coding-rule2`プロジェクト専用に設計されています。
新しいプロジェクトにテンプレートとして使用する場合は、そのプロジェクトの要件に合わせてカスタマイズしてください。

## 🔴 ROOT DIRECTORY ABSOLUTE LIMITS (coding-rule2専用)

### MAXIMUM 12 FILES IN ROOT - NO EXCEPTIONS
**絶対最大ファイル数**: 12個まで  
**超過時**: 自動強制移動または拒否

### ROOT DIRECTORY WHITELIST (絶対固定)
```
✅ ALLOWED FILES (8 files maximum):
1. README.md          # Project overview
2. Makefile          # Build commands  
3. pyproject.toml    # Python project config
4. requirements.txt  # Dependencies
5. LICENSE           # License file
6. CLAUDE.md         # AI system config
7. Index.md          # Project navigation
8. .gitignore        # Git ignore rules

🟡 CONDITIONAL FILES (4 files maximum):
9.  .env             # Environment variables (if needed)
10. .mcp.json        # MCP configuration (if MCP used)
11. .mypy.ini        # Type checking config (if typing strict)
12. docker-compose.yml # Container orchestration (if Docker used)

❌ FORBIDDEN IN ROOT:
- .env.example       → scripts/setup/.env.example
- .claude-project    → config/editor/
- .cursorrules       → config/editor/
- .cursorignore      → config/editor/
- .cursorindexignore → config/editor/
- .forbidden-move    → config/editor/
- .gitattributes     → config/git/
- .pre-commit-config.yaml → config/git/
- .shell_integration.zsh → config/shell/
- startup_checklist.md → docs/02_guides/
```

## 📁 FOLDER STRUCTURE ABSOLUTE RULES

### MANDATORY DIRECTORIES
```
📁 ROOT/
├── 📁 .cursor/          # Cursor editor workspace (MUST stay in root)
├── 📁 config/           # All configuration files
│   ├── 📁 editor/       # Editor-specific configs (.cursorrules, etc.)
│   ├── 📁 git/          # Git configuration (.gitattributes, hooks)
│   ├── 📁 docker/       # Container configurations
│   ├── 📁 database/     # Database configurations
│   ├── 📁 integrations/ # Third-party integrations
│   └── 📁 security/     # Security configurations
├── 📁 docs/             # All documentation
│   ├── 📁 01_architecture/ # System design docs
│   ├── 📁 02_guides/       # User guides
│   ├── 📁 03_development/  # Development docs
│   └── 📁 04_reference/    # Reference materials
├── 📁 scripts/          # All executable scripts
│   ├── 📁 setup/        # Installation & setup
│   ├── 📁 tools/        # Utility tools
│   ├── 📁 hooks/        # Git/CI hooks
│   └── 📁 automation/   # Automated tasks
├── 📁 src/              # Source code
├── 📁 tests/            # Test files
├── 📁 data/             # Data files
└── 📁 runtime/          # Runtime generated files
```

## 🔒 FILE PLACEMENT ENFORCEMENT RULES

### 1. FILE TYPE CLASSIFICATION
```yaml
BUILD_FILES:
  - "Makefile"
  - "pyproject.toml"
  - "requirements.txt"
  - "package.json"
  - "Cargo.toml"
  - "setup.py"
  → LOCATION: ROOT (mandatory)

DOCUMENTATION:
  - "*.md" (except README.md, CLAUDE.md, Index.md)
  - "*.rst"
  - "*.txt" (except requirements.txt)
  → LOCATION: docs/

CONFIGURATION:
  - ".cursorrules"
  - ".claude-project"
  - ".gitattributes"
  - ".pre-commit-config.yaml"
  - "*.json" (config files)
  - "*.yaml", "*.yml" (config files)
  → LOCATION: config/

SCRIPTS:
  - "*.sh"
  - "*.py" (executable)
  - "*.js" (executable)
  → LOCATION: scripts/

SOURCE_CODE:
  - "*.py" (modules)
  - "*.js" (modules)
  - "*.ts"
  - "*.go"
  - "*.rs"
  → LOCATION: src/
```

### 2. DOTFILE CONSOLIDATION RULES
```bash
# Editor configurations → config/editor/
.cursorrules → config/editor/.cursorrules
.claude-project → config/editor/.claude-project
.cursorignore → config/editor/.cursorignore
.cursorindexignore → config/editor/.cursorindexignore

# Git configurations → config/git/
.gitattributes → config/git/.gitattributes
.pre-commit-config.yaml → config/git/.pre-commit-config.yaml

# Development tools → config/dev/
.mypy.ini → config/dev/.mypy.ini
.pylintrc → config/dev/.pylintrc
.flake8 → config/dev/.flake8

# Environment → keep in root (but only .env, not .env.example)
.env → ROOT (keep)
.env.example → scripts/setup/.env.example
```

## ⚡ AUTOMATIC ENFORCEMENT SYSTEM

### 1. Pre-commit Hook
```bash
#!/bin/bash
# Check root directory file count
ROOT_FILES=$(ls -la | grep "^-" | wc -l)
if [ $ROOT_FILES -gt 12 ]; then
  echo "❌ ROOT DIRECTORY LIMIT EXCEEDED: $ROOT_FILES/12 files"
  echo "🔧 Run: make enforce-file-organization"
  exit 1
fi
```

### 2. File Watcher System
```python
# Automatically move misplaced files
WATCH_PATTERNS = {
    "*.md": "docs/",
    ".cursor*": "config/editor/",
    "*.config.*": "config/",
    "setup_*.py": "scripts/setup/",
    "*_test.py": "tests/",
}
```

### 3. Makefile Enforcement Commands
```makefile
enforce-file-organization: ## Force file organization compliance
	@python3 scripts/automation/strict-file-organizer.py --force

check-file-organization: ## Check file organization compliance  
	@python3 scripts/automation/strict-file-organizer.py --check-only

root-file-audit: ## Audit root directory compliance
	@scripts/automation/root-directory-auditor.sh
```

## 🚨 VIOLATION PENALTIES

### SEVERITY LEVELS
```
🟢 LEVEL 1 - WARNING: 10-12 files in root
   → Automated notification

🟡 LEVEL 2 - ENFORCEMENT: 13-15 files in root  
   → Automatic file movement

🔴 LEVEL 3 - BLOCKING: 16+ files in root
   → Block git commits, require manual cleanup
```

### AUTOMATIC ACTIONS
```bash
# Level 1: Warning
echo "⚠️  ROOT DIRECTORY WARNING: $COUNT/12 files"

# Level 2: Auto-move
mv misplaced_file.md docs/
echo "🔧 MOVED: misplaced_file.md → docs/"

# Level 3: Block operations
echo "❌ BLOCKED: Too many root files ($COUNT/12)"
echo "🔧 Required: make enforce-file-organization"
exit 1
```

## 📊 MONITORING & REPORTING

### Daily Compliance Report
```bash
# Generate compliance metrics
ROOT_COUNT=$(ls -1 | wc -l)
VIOLATIONS=$(find . -maxdepth 1 -name "*.md" ! -name "README.md" ! -name "CLAUDE.md" ! -name "Index.md")
MISPLACED_CONFIGS=$(find . -maxdepth 1 -name ".cursor*" -o -name ".*config*")

echo "📊 FILE ORGANIZATION COMPLIANCE REPORT"
echo "Root files: $ROOT_COUNT/12"
echo "Violations: $(echo $VIOLATIONS | wc -w)"
echo "Misplaced configs: $(echo $MISPLACED_CONFIGS | wc -w)"
```

## 🎯 IMPLEMENTATION PRIORITY

### Phase 1: Immediate (HIGH)
1. ✅ Create strict rules documentation
2. ⏳ Move all dotfiles to config/
3. ⏳ Implement root directory limit (12 files)
4. ⏳ Create automated enforcement script

### Phase 2: Enforcement (MEDIUM)  
1. ⏳ Add pre-commit hooks
2. ⏳ Implement file watcher
3. ⏳ Add Makefile commands
4. ⏳ Create violation reporting

### Phase 3: Monitoring (LOW)
1. ⏳ Daily compliance reports
2. ⏳ Trend analysis
3. ⏳ Performance metrics
4. ⏳ Continuous improvement

---

## 🎯 新しいプロジェクトでの使用方法

### Template Customization for New Projects
When using coding-rule2 as a template for new projects:

1. **Customize file organization rules**:
   ```bash
   # Edit scripts/automation/strict-file-organizer.py
   # Update ALLOWED_ROOT_FILES for your project needs
   # Update ALLOWED_ROOT_DIRS for your project structure
   ```

2. **Adjust folder structure**:
   - Keep core folders: `src/`, `docs/`, `tests/`, `scripts/`
   - Add project-specific folders as needed
   - Modify config/ structure based on your tech stack

3. **Update enforcement rules**:
   ```bash
   # Edit scripts/hooks/pre-commit-file-organization.sh
   # Customize violation checks for your project
   ```

4. **Set appropriate file limits**:
   - Default: 12 files max in root
   - Adjust ROOT_FILE_LIMIT based on project complexity
   - Consider your project's specific needs

### Example for Web Project:
```python
ALLOWED_ROOT_FILES = {
    'README.md', 'package.json', 'package-lock.json',
    'index.html', 'vite.config.js', '.gitignore',
    'LICENSE', 'tsconfig.json', '.env'
}

ALLOWED_ROOT_DIRS = {
    'src', 'public', 'docs', 'tests', 'node_modules', 'dist'
}
```

### Example for Python Library:
```python
ALLOWED_ROOT_FILES = {
    'README.md', 'setup.py', 'pyproject.toml', 'requirements.txt',
    'LICENSE', '.gitignore', 'MANIFEST.in', 'tox.ini'
}

ALLOWED_ROOT_DIRS = {
    'src', 'docs', 'tests', 'examples', '.tox', 'dist'
}
```

---

**FOR CODING-RULE2 PROJECT**: These rules are ABSOLUTE and NON-NEGOTIABLE.  
Any violation triggers automatic enforcement.
**NO EXCEPTIONS. NO COMPROMISES.**

**FOR OTHER PROJECTS**: Customize these rules to fit your project's needs while maintaining organization principles.