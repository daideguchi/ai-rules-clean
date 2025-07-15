#!/bin/bash
# Quick Project Setup Script
# 新プロジェクト用クイックセットアップスクリプト

set -e

echo "🚀 coding-rule2 Template Quick Setup"
echo "===================================="
echo ""

# Check if this is a new project (not coding-rule2 itself)
if [[ "$(basename "$(pwd)")" == "coding-rule2" ]] && [[ -f "CLAUDE.md" ]] && grep -q "AI Safety Governance" README.md 2>/dev/null; then
    echo "❌ You're running this in the original coding-rule2 project!"
    echo "💡 This script is for NEW projects using coding-rule2 as a template."
    echo "💡 Copy this template to a new directory first."
    exit 1
fi

echo "📋 Step 1: Project Information"
echo "------------------------------"
read -p "🏷️  Enter your project name: " PROJECT_NAME
if [[ -z "$PROJECT_NAME" ]]; then
    echo "❌ Project name is required!"
    exit 1
fi

echo ""
echo "📂 Step 2: Select Project Type"
echo "------------------------------"
echo "1) 🌐 Web Project (React/Vue/Angular)"
echo "2) 🐍 Python Library/Package"
echo "3) 🤖 AI/ML Project"
echo "4) ⚙️  Custom Project"
echo ""
read -p "Choose project type (1-4): " PROJECT_TYPE

case $PROJECT_TYPE in
    1) TYPE_NAME="web" ;;
    2) TYPE_NAME="python" ;;
    3) TYPE_NAME="ai-project" ;;
    4) TYPE_NAME="custom" ;;
    *) echo "❌ Invalid choice!"; exit 1 ;;
esac

echo ""
echo "🔧 Step 3: Initialize Project"
echo "-----------------------------"
echo "Initializing '$PROJECT_NAME' as $TYPE_NAME project..."

# Run initialization
if python3 scripts/setup/initialize_new_project.py "$PROJECT_NAME" --type "$TYPE_NAME"; then
    echo "✅ Project initialization completed!"
else
    echo "❌ Project initialization failed!"
    exit 1
fi

echo ""
echo "🔑 Step 4: Setup API Keys (Optional)"
echo "-----------------------------------"
read -p "Do you want to setup API keys now? (y/N): " SETUP_APIS

if [[ "$SETUP_APIS" =~ ^[Yy]$ ]]; then
    echo "Setting up API keys..."
    python3 scripts/setup/quick_api_setup.py || echo "⚠️ API setup can be done later with 'make api-setup'"
fi

echo ""
echo "📦 Step 5: Install Dependencies"
echo "-------------------------------"
if [[ -f "requirements.txt" ]]; then
    read -p "Install Python dependencies? (y/N): " INSTALL_DEPS
    if [[ "$INSTALL_DEPS" =~ ^[Yy]$ ]]; then
        pip install -r requirements.txt || echo "⚠️ Install dependencies manually later"
    fi
elif [[ -f "package.json" ]]; then
    read -p "Install Node.js dependencies? (y/N): " INSTALL_DEPS
    if [[ "$INSTALL_DEPS" =~ ^[Yy]$ ]]; then
        npm install || echo "⚠️ Install dependencies manually later"
    fi
fi

echo ""
echo "🎯 Step 6: Verify Setup"
echo "----------------------"
echo "Running file organization check..."
make check-file-organization || echo "⚠️ File organization issues detected - see above"

echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo ""
echo "📋 Your project '$PROJECT_NAME' is ready!"
echo ""
echo "🔧 Available commands:"
echo "  make check-file-organization  - Check file organization"
echo "  make enforce-file-organization - Fix file organization"
echo "  make api-setup               - Setup API keys"
echo "  make mcp-setup               - Setup MCP integration"
echo ""
echo "📖 Documentation:"
echo "  docs/04_reference/STRICT_FILE_ORGANIZATION_RULES.md"
echo ""
echo "🚀 Next steps:"
echo "  1. Review project structure in docs/"
echo "  2. Customize file organization rules if needed"
echo "  3. Start developing your project!"
echo ""
echo "✨ Happy coding!"