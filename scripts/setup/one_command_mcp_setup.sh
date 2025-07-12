#!/bin/bash
# One Command MCP Setup - 移植先プロジェクト用
# 新プロジェクトでのMCP設定を1コマンドで完了
#
# Usage:
#     bash scripts/setup/one_command_mcp_setup.sh
#     bash scripts/setup/one_command_mcp_setup.sh --quick
#     bash scripts/setup/one_command_mcp_setup.sh --check-only

set -e  # Exit on any error

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SCRIPTS_DIR="$PROJECT_ROOT/scripts"

echo "🚀 One Command MCP Setup - Starting..."
echo "📁 Project: $PROJECT_ROOT"
echo "=================================================="

# Check if this is a check-only run
if [[ "$1" == "--check-only" ]]; then
    echo "🔍 Running status check only..."
    python3 "$SCRIPTS_DIR/setup/auto_mcp_setup.py" --check-only
    python3 "$SCRIPTS_DIR/hooks/system_status_display.py"
    exit 0
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install npm packages
install_npm_packages() {
    echo "📦 Installing NPM packages..."
    
    if ! command_exists npm; then
        echo "❌ npm not found. Please install Node.js first:"
        echo "   https://nodejs.org/"
        exit 1
    fi
    
    # Install o3-search-mcp globally
    if ! npm list -g o3-search-mcp >/dev/null 2>&1; then
        echo "📥 Installing o3-search-mcp..."
        npm install -g o3-search-mcp
        echo "✅ o3-search-mcp installed"
    else
        echo "✅ o3-search-mcp already installed"
    fi
}

# Function to setup API keys
setup_api_keys() {
    echo ""
    echo "🔑 API Key Setup"
    echo "--------------------"
    
    if [[ "$1" == "--quick" ]]; then
        echo "⚡ Quick mode: Skipping interactive API key setup"
        echo "💡 Run later: python3 scripts/setup/quick_api_setup.py"
        return
    fi
    
    # Check current status
    python3 "$SCRIPTS_DIR/setup/quick_api_setup.py" --check
    echo ""
    
    read -p "🔧 Setup missing API keys interactively? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python3 "$SCRIPTS_DIR/setup/quick_api_setup.py"
    else
        echo "⚠️  Skipped API key setup"
        echo "💡 Setup later: python3 scripts/setup/quick_api_setup.py"
    fi
}

# Function to create MCP configuration
setup_mcp_config() {
    echo ""
    echo "🔧 MCP Configuration Setup"
    echo "------------------------------"
    
    python3 "$SCRIPTS_DIR/setup/auto_mcp_setup.py"
}

# Function to verify setup
verify_setup() {
    echo ""
    echo "✅ Verification"
    echo "---------------"
    
    echo "📊 Final System Status:"
    python3 "$SCRIPTS_DIR/hooks/system_status_display.py"
    
    echo ""
    echo "🔍 API Key Status:"
    python3 "$SCRIPTS_DIR/setup/quick_api_setup.py" --check
}

# Function to show completion instructions
show_completion_instructions() {
    echo ""
    echo "🎉 MCP Setup Complete!"
    echo "========================="
    echo ""
    echo "📋 Next Steps:"
    echo "  1. 🔄 Restart Claude Code to activate MCP tools"
    echo "  2. 🧪 Test O3 access: Ask Claude to 'consult o3 about...'"
    echo "  3. 🧪 Test Gemini access: Ask Claude to 'consult gemini about...'"
    echo ""
    echo "🛠️  Useful Commands:"
    echo "  • Check status: bash scripts/setup/one_command_mcp_setup.sh --check-only"
    echo "  • Update API keys: python3 scripts/setup/quick_api_setup.py"
    echo "  • Reconfigure MCP: python3 scripts/setup/auto_mcp_setup.py"
    echo ""
    echo "📖 Documentation:"
    echo "  • MCP Guide: https://modelcontextprotocol.io/introduction"
    echo "  • O3 Setup: https://zenn.dev/yoshiko/articles/claude-code-with-o3"
}

# Main execution flow
main() {
    local quick_mode=""
    if [[ "$1" == "--quick" ]]; then
        quick_mode="--quick"
        echo "⚡ Quick setup mode enabled"
    fi
    
    # Step 1: Install required packages
    install_npm_packages
    
    # Step 2: Setup API keys
    setup_api_keys "$quick_mode"
    
    # Step 3: Create MCP configuration
    setup_mcp_config
    
    # Step 4: Verify everything works
    verify_setup
    
    # Step 5: Show completion instructions
    show_completion_instructions
}

# Handle command line arguments
case "$1" in
    --help|-h)
        echo "One Command MCP Setup"
        echo ""
        echo "Usage:"
        echo "  $0                 # Interactive setup"
        echo "  $0 --quick         # Quick setup (skip API key prompts)"
        echo "  $0 --check-only    # Check status only"
        echo "  $0 --help          # Show this help"
        exit 0
        ;;
    --check-only)
        # Handled above
        ;;
    *)
        main "$1"
        ;;
esac