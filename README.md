# 🚀 coding-rule2: Universal Project Template

**Comprehensive Project Template with Strict File Organization & AI Integration**

[![Template Ready](https://img.shields.io/badge/Template-Ready-brightgreen)](docs/TEMPLATE_USAGE.md)
[![File Organization](https://img.shields.io/badge/File%20Organization-Automatic-blue)](docs/04_reference/STRICT_FILE_ORGANIZATION_RULES.md)
[![Project Types](https://img.shields.io/badge/Project%20Types-4%20Supported-green)](scripts/setup/)
[![AI Integration](https://img.shields.io/badge/AI%20Integration-Claude%20%7C%20MCP-purple)](CLAUDE.md)
[![One Command Setup](https://img.shields.io/badge/Setup-One%20Command-orange)](scripts/setup/quick_project_setup.sh)

## 🎯 Template Overview

**coding-rule2** is a universal project template featuring automatic file organization, AI integration, and multi-project-type support. Copy this template to start any new project with best practices built-in.

### 🌟 Key Features

- **📁 Strict File Organization**: Automatic enforcement with 12-20 file root limits
- **🚀 One-Command Setup**: `bash scripts/setup/quick_project_setup.sh`
- **🎯 Multiple Project Types**: Web, Python, AI/ML, Custom projects
- **🤖 AI Integration**: Claude Code, MCP, o3 support built-in
- **⚡ Pre-commit Hooks**: Automatic file organization enforcement
- **🔧 Template Customization**: Adapts to your project type automatically

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

### 2. Interactive Setup
```bash
# One command setup with interactive prompts
bash scripts/setup/quick_project_setup.sh
```

### 3. Manual Project Type Setup
```bash
make init-web-project      # For web projects (React/Vue/Angular)
make init-python-project   # For Python libraries/packages
make init-ai-project       # For AI/ML projects
make init-custom-project   # For custom projects
```

## 📁 Project Types Supported

| Type | Root File Limit | Key Features |
|------|-----------------|-------------|
| **🌐 Web** | 15 files | React/Vue/Angular, Node.js, npm support |
| **🐍 Python** | 12 files | pip, setuptools, pytest integration |
| **🤖 AI/ML** | 12 files | Claude Code, MCP, AI organization |
| **⚙️ Custom** | 20 files | Flexible structure, customizable |

## 🔒 File Organization System

### Automatic Enforcement
- **Root directory limits**: 12-20 files maximum (varies by project type)
- **Pre-commit hooks**: Prevent commits when rules are violated
- **Automatic placement**: Files moved to appropriate directories
- **Real-time validation**: `make check-file-organization`

### Folder Structure
```
PROJECT_ROOT/
├── .cursor/          # Cursor editor workspace (stays in root)
├── config/           # Configuration files
├── docs/             # Documentation
├── scripts/          # Executable scripts
├── src/              # Source code
├── tests/            # Test files
└── [project-specific folders]
```

## 🔧 Available Commands

### File Organization
```bash
make check-file-organization   # Check compliance status
make enforce-file-organization # Force compliance
make root-audit               # Quick file count check
make dry-run-organization     # Preview changes
```

### Project Setup
```bash
make mcp-setup     # Setup MCP integration
make api-setup     # Configure API keys
make install       # Install dependencies
make test          # Run tests
```

### Template Management
```bash
# For new projects using this template
bash scripts/setup/quick_project_setup.sh  # Interactive setup
```

## 🤖 AI Integration Features

### Claude Code Integration
- **CLAUDE.md**: AI behavior configuration
- **MCP support**: Model Context Protocol for enhanced AI capabilities
- **Memory system**: Persistent AI memory across sessions

### Supported AI Tools
- **Claude**: Advanced AI assistant integration
- **o3**: OpenAI's reasoning AI model
- **Gemini**: Google AI model support

### Quick MCP Setup
```bash
# One command MCP setup for new projects
make mcp-setup

# Check MCP status
make mcp-status
```

## 📋 Template Usage Guide

For complete template usage instructions, see **[TEMPLATE_USAGE.md](docs/TEMPLATE_USAGE.md)**

### Key Documentation
- **[TEMPLATE_USAGE.md](docs/TEMPLATE_USAGE.md)** - Complete template guide
- **[docs/04_reference/STRICT_FILE_ORGANIZATION_RULES.md](docs/04_reference/STRICT_FILE_ORGANIZATION_RULES.md)** - File organization rules
- **[CLAUDE.md](CLAUDE.md)** - AI integration settings (for AI projects)

## 🛡️ Protection Features

### File Organization Protection
- **Pre-commit hooks**: Automatic file organization enforcement
- **Real-time validation**: Continuous compliance checking
- **Automatic placement**: Files moved to correct directories
- **Project-specific rules**: Customized for each project type

### Template Protection
- **Project detection**: Rules only apply to specific projects
- **Template integrity**: Original template structure preserved
- **Customizable rules**: Adapt to your project needs

## 🎉 Success Stories

This template is optimized for:
- ✅ **Clean project structure** with automatic maintenance
- ✅ **Rapid development** with one-command setup
- ✅ **Team collaboration** with shared organization rules
- ✅ **AI-enhanced development** (for AI projects)
- ✅ **Production-ready** structure from day one

### Verified Features
- ✅ **File organization enforcement**: Pre-commit hooks prevent violations
- ✅ **Multi-project type support**: Web, Python, AI, Custom
- ✅ **Template customization**: Automatic adaptation to project needs
- ✅ **AI integration**: Claude Code, MCP, o3 support
- ✅ **One-command setup**: Interactive project initialization

## 🎯 Command Reference

### Essential Template Commands
```bash
bash scripts/setup/quick_project_setup.sh  # Interactive project setup
make check-file-organization              # Check file organization
make enforce-file-organization            # Fix file organization
make help                                 # Show all commands
```

### Project Initialization
```bash
make init-web-project      # Initialize as web project
make init-python-project   # Initialize as Python project
make init-ai-project       # Initialize as AI project
make init-custom-project   # Initialize as custom project
```

### MCP & AI Setup (for AI projects)
```bash
make mcp-setup     # Complete MCP setup
make api-setup     # Configure API keys
make mcp-status    # Check MCP status
```

### Development Commands
```bash
make install       # Install dependencies
make test          # Run tests
make setup-hooks   # Configure git hooks
make lint          # Run code linting
```

## 🔧 Customization

### Project Structure (Template)
```
coding-rule2/
├── .cursor/                   # Cursor editor workspace (stays in root)
├── config/                    # Configuration files
├── docs/                      # Documentation
├── scripts/                   # Executable scripts
│   ├── automation/           # File organization automation
│   └── setup/               # Project setup scripts
├── src/                      # Source code
├── tests/                    # Test files
└── [12 root files maximum]   # Enforced by pre-commit hooks
```

### Customizing for Your Project

1. **Copy template**: Clone coding-rule2 to your new project directory
2. **Run setup**: `bash scripts/setup/quick_project_setup.sh`
3. **Customize rules**: Edit `scripts/automation/strict-file-organizer.py`
4. **Update documentation**: Modify `docs/04_reference/STRICT_FILE_ORGANIZATION_RULES.md`

### Template Features
- **Automatic file placement**: Files moved to correct directories
- **Pre-commit hooks**: Prevent commits when rules are violated
- **Project type detection**: Rules adapt automatically
- **Customizable limits**: Adjust file limits per project type

## 📚 Documentation

### Template Usage
- **[TEMPLATE_USAGE.md](docs/TEMPLATE_USAGE.md)** - Complete template usage guide
- **[docs/04_reference/STRICT_FILE_ORGANIZATION_RULES.md](docs/04_reference/STRICT_FILE_ORGANIZATION_RULES.md)** - File organization rules

### AI Integration (for AI projects)
- **[CLAUDE.md](CLAUDE.md)** - AI behavior configuration
- **[Index.md](Index.md)** - Project overview (AI projects)

### Development
- **[docs/02_guides/](docs/02_guides/)** - Development guides
- **[docs/04_reference/](docs/04_reference/)** - Technical specifications

## 🛡️ Security & Best Practices

### File Organization Security
- **Pre-commit hooks**: Prevent unauthorized file placements
- **Automatic enforcement**: Rules cannot be bypassed accidentally
- **Template protection**: Original structure preserved

### API Key Management (for AI projects)
- **Environment variables**: Store in `.env` files (excluded from git)
- **MCP integration**: Secure API key handling
- **No hardcoding**: Keys never committed to repository

### Recommended Setup
```bash
# API key configuration (AI projects)
echo "OPENAI_API_KEY=your_key_here" > .env
echo "ANTHROPIC_API_KEY=your_key_here" >> .env
```

## 🎉 Using This Template

This project is designed as a universal template. Use it for any new project:

1. **Copy the template**: Clone to your new project directory
2. **Run setup**: `bash scripts/setup/quick_project_setup.sh`
3. **Customize**: Adapt file organization rules to your needs
4. **Start developing**: Clean, organized structure from day one

### Contributing to the Template

To improve the template itself:
1. Fork this repository
2. Make improvements to template features
3. Test with different project types
4. Submit pull request

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details

## 🔗 Related Links

- **Template Usage Guide**: [TEMPLATE_USAGE.md](docs/TEMPLATE_USAGE.md)
- **File Organization Rules**: [docs/04_reference/STRICT_FILE_ORGANIZATION_RULES.md](docs/04_reference/STRICT_FILE_ORGANIZATION_RULES.md)
- **Claude Code Integration**: [CLAUDE.md](CLAUDE.md) (AI projects)

---

**🚀 coding-rule2: The Universal Project Template**

**Clean, organized, and AI-enhanced development from day one** ✨