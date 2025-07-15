# coding-rule2 Template Usage Guide
# テンプレート使用ガイド

## 🎯 Overview

`coding-rule2` is a comprehensive project template featuring:
- 🔒 **Strict file organization** with automatic enforcement
- 🤖 **AI/ML project optimizations** (Claude, MCP integration)
- 📋 **Multiple project type support** (Web, Python, AI, Custom)
- ⚡ **One-command setup** for new projects

## 🚀 Quick Start for New Projects

### 1. Copy Template
```bash
# Clone or download coding-rule2
git clone <repository-url> my-new-project
cd my-new-project

# Remove original git history (optional)
rm -rf .git
git init
```

### 2. Run Quick Setup
```bash
# Interactive setup (recommended)
bash scripts/setup/quick_project_setup.sh

# Or manual initialization
make init-web-project      # For web projects
make init-python-project   # For Python projects  
make init-ai-project       # For AI/ML projects
make init-custom-project   # For custom projects
```

### 3. Verify Setup
```bash
# Check file organization
make check-file-organization

# Check root directory compliance
make root-audit
```

## 📁 Project Types

### 🌐 Web Project
- **File limit**: 15 files in root
- **Structure**: `src/`, `public/`, `docs/`, `tests/`, `scripts/`
- **Files**: `package.json`, `index.html`, `vite.config.js`, etc.

### 🐍 Python Project
- **File limit**: 12 files in root
- **Structure**: `src/`, `docs/`, `tests/`, `examples/`, `scripts/`
- **Files**: `setup.py`, `pyproject.toml`, `requirements.txt`, etc.

### 🤖 AI/ML Project
- **File limit**: 12 files in root
- **Structure**: `config/`, `docs/`, `scripts/`, `src/`, `runtime/`
- **Files**: `CLAUDE.md`, `.mcp.json`, `Makefile`, etc.

### ⚙️ Custom Project
- **File limit**: 20 files in root (customizable)
- **Structure**: Basic `src/`, `docs/`, `tests/`, `scripts/`
- **Files**: `README.md`, `.gitignore`, `LICENSE`

## 🔧 Available Commands

### File Organization
```bash
make enforce-file-organization  # Force file organization compliance
make check-file-organization   # Check compliance status
make root-audit               # Quick file count check
make dry-run-organization     # Preview changes
make file-organization-report # Generate detailed report
```

### MCP & API Setup
```bash
make mcp-setup     # Complete MCP setup
make mcp-status    # Check MCP status
make api-setup     # Setup API keys
make mcp-config    # Configure MCP only
```

### Project Initialization
```bash
make init-web-project      # Initialize as web project
make init-python-project   # Initialize as Python project
make init-ai-project       # Initialize as AI project
make init-custom-project   # Initialize as custom project
```

## 📋 File Organization Rules

### Root Directory Limits
- **Maximum files**: Varies by project type (12-20)
- **Essential files only**: README, Makefile, config files
- **Automatic enforcement**: Pre-commit hooks prevent violations

### Folder Structure
```
📁 PROJECT_ROOT/
├── 📁 .cursor/          # Cursor editor workspace (if used)
├── 📁 config/           # Configuration files
├── 📁 docs/             # Documentation
├── 📁 scripts/          # Executable scripts
├── 📁 src/              # Source code
├── 📁 tests/            # Test files
└── 📁 [project-specific folders]
```

### Automatic File Placement
- **Documentation**: `*.md` → `docs/`
- **Scripts**: `*.sh`, `*.py` (executable) → `scripts/`
- **Configuration**: `*.json`, `*.yaml`, dotfiles → `config/`
- **Source Code**: `*.py` (modules), `*.js`, `*.ts` → `src/`

## 🛡️ Protection Features

### For coding-rule2 Project
- **Absolute rules**: 12 file limit, strict enforcement
- **No exceptions**: Pre-commit hooks block violations
- **AI-optimized structure**: MCP, CLAUDE.md, specialized folders

### For Template Projects
- **Customizable rules**: Adjusted per project type
- **Flexible limits**: 12-20 files based on needs
- **Project detection**: Automatic rule adaptation

## 🎯 Best Practices

### 1. Customize After Setup
```bash
# Edit file organization rules
vim scripts/automation/strict-file-organizer.py

# Update project-specific settings
vim docs/04_reference/STRICT_FILE_ORGANIZATION_RULES.md
```

### 2. Maintain Organization
```bash
# Regular compliance checks
make check-file-organization

# Fix issues automatically
make enforce-file-organization
```

### 3. Team Integration
```bash
# Pre-commit hooks are automatically installed
# They prevent commits when rules are violated

# Share rules with team
git add .git/hooks/pre-commit
```

## 🤖 AI Integration Features

### Claude Code Integration
- **CLAUDE.md**: AI behavior configuration
- **MCP support**: Model Context Protocol for AI tools
- **Memory system**: Persistent AI memory across sessions

### Available AI Tools
- **O3 integration**: Advanced reasoning AI
- **Gemini support**: Google AI model access
- **Claude enhancements**: Specialized AI workflows

## 📖 Documentation

### Key Files
- `docs/04_reference/STRICT_FILE_ORGANIZATION_RULES.md` - Complete rules
- `TEMPLATE_USAGE.md` - This guide
- `README.md` - Project overview
- `CLAUDE.md` - AI configuration (AI projects only)

### Getting Help
- Run `make help` for all available commands
- Check `docs/` folder for detailed documentation
- File organization issues: `make check-file-organization`

## 🎉 Success Stories

This template is optimized for:
- ✅ **Clean project structure** with automatic maintenance
- ✅ **AI-enhanced development** with Claude/MCP integration
- ✅ **Team collaboration** with shared organization rules
- ✅ **Rapid prototyping** with one-command setup
- ✅ **Production-ready** structure from day one

---

**Happy coding with coding-rule2! 🚀**