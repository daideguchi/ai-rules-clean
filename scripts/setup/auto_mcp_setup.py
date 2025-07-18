#!/usr/bin/env python3
"""
Automated MCP Setup Tool for New Projects
新プロジェクト用MCP自動設定ツール

Usage:
    python3 scripts/setup/auto_mcp_setup.py
    python3 scripts/setup/auto_mcp_setup.py --check-only
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Tuple


class MCPSetupTool:
    def __init__(self):
        self.project_root = Path.cwd()
        self.mcp_config_path = self.project_root / ".mcp.json"
        self.claude_settings_path = Path.home() / ".claude" / "settings.json"
        self.env_file_path = self.project_root / ".env"

    def check_api_keys(self) -> Dict[str, Tuple[bool, str]]:
        """Check API key availability"""
        status = {}

        # Check OpenAI API Key
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key and openai_key.startswith('sk-'):
            status['openai'] = (True, f"✅ Set (sk-...{openai_key[-4:]})")
        else:
            status['openai'] = (False, "❌ Not configured")

        # Check Gemini API Key
        gemini_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if gemini_key:
            status['gemini'] = (True, f"✅ Set (...{gemini_key[-4:]})")
        else:
            status['gemini'] = (False, "❌ Not configured")

        return status

    def display_status(self):
        """Display current MCP and API key status"""
        print("🔧 MCP Configuration Status")
        print("=" * 40)

        # Check API Keys
        api_status = self.check_api_keys()
        print("📋 API Key Status:")
        for service, (_is_set, msg) in api_status.items():
            print(f"  • {service.upper()}: {msg}")
        print()

        # Check MCP Config Files
        print("📁 Configuration Files:")
        if self.mcp_config_path.exists():
            print("  • .mcp.json: ✅ Present")
        else:
            print("  • .mcp.json: ❌ Missing")

        if self.claude_settings_path.exists():
            print("  • ~/.claude/settings.json: ✅ Present")
        else:
            print("  • ~/.claude/settings.json: ❌ Missing")
        print()

    def create_env_template(self):
        """Create .env template file"""
        env_template = """# API Keys for MCP Services
# Copy this file to .env and fill in your actual API keys

# OpenAI API Key (for O3 and GPT models)
OPENAI_API_KEY=sk-your-openai-api-key-here

# Gemini API Key (for Google AI models)
GEMINI_API_KEY=your-gemini-api-key-here
"""

        env_example_path = self.project_root / ".env.example"
        with open(env_example_path, 'w') as f:
            f.write(env_template)
        print("✅ Created .env.example template")

    def create_mcp_config(self):
        """Create .mcp.json configuration"""
        mcp_config = {
            "mcpServers": {
                "o3": {
                    "command": "npx",
                    "args": ["o3-search-mcp"],
                    "env": {
                        "OPENAI_API_KEY": "${OPENAI_API_KEY}",
                        "SEARCH_CONTEXT_SIZE": "medium",
                        "REASONING_EFFORT": "medium"
                    }
                }
            }
        }

        with open(self.mcp_config_path, 'w') as f:
            json.dump(mcp_config, f, indent=2)
        print("✅ Created .mcp.json configuration")

    def update_claude_settings(self):
        """Update ~/.claude/settings.json with MCP configuration"""
        claude_settings_dir = self.claude_settings_path.parent
        claude_settings_dir.mkdir(exist_ok=True)

        # Load existing settings or create new
        if self.claude_settings_path.exists():
            with open(self.claude_settings_path) as f:
                settings = json.load(f)
        else:
            settings = {}

        # Ensure mcpServers section exists
        if 'mcpServers' not in settings:
            settings['mcpServers'] = {}

        # Add O3 configuration
        settings['mcpServers']['o3'] = {
            "command": "npx",
            "args": ["o3-search-mcp"],
            "env": {
                "OPENAI_API_KEY": "${OPENAI_API_KEY}",
                "SEARCH_CONTEXT_SIZE": "medium",
                "REASONING_EFFORT": "medium"
            }
        }

        # Add Gemini configuration if script exists
        gemini_script = self.project_root / "scripts" / "mcp" / "gemini_mcp_server.py"
        if gemini_script.exists():
            settings['mcpServers']['gemini'] = {
                "command": "python3",
                "args": [str(gemini_script)],
                "env": {}
            }

        with open(self.claude_settings_path, 'w') as f:
            json.dump(settings, f, indent=2)
        print("✅ Updated ~/.claude/settings.json")

    def install_npm_packages(self):
        """Install required npm packages"""
        try:
            os.system("npm list -g o3-search-mcp > /dev/null 2>&1 || npm install -g o3-search-mcp")
            print("✅ Verified o3-search-mcp package")
        except Exception as e:
            print(f"⚠️  Warning: Could not install o3-search-mcp: {e}")

    def setup_interactive(self):
        """Interactive setup for API keys"""
        print("🔧 Interactive MCP Setup")
        print("=" * 30)

        # Check if user wants to set API keys
        if not os.getenv('OPENAI_API_KEY'):
            print("\n📝 OpenAI API Key not found in environment")
            key = input("Enter your OpenAI API key (or press Enter to skip): ").strip()
            if key:
                with open(self.env_file_path, 'a') as f:
                    f.write(f"\nOPENAI_API_KEY={key}\n")
                print("✅ Added to .env file")

        if not (os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')):
            print("\n📝 Gemini API Key not found in environment")
            key = input("Enter your Gemini API key (or press Enter to skip): ").strip()
            if key:
                with open(self.env_file_path, 'a') as f:
                    f.write(f"\nGEMINI_API_KEY={key}\n")
                print("✅ Added to .env file")

    def run_full_setup(self):
        """Run complete MCP setup"""
        print("🚀 Starting Automated MCP Setup")
        print("=" * 40)

        # Install packages
        self.install_npm_packages()

        # Create configuration files
        self.create_env_template()
        self.create_mcp_config()
        self.update_claude_settings()

        print("\n🎉 MCP Setup Complete!")
        print("📋 Next Steps:")
        print("  1. Copy .env.example to .env and add your API keys")
        print("  2. Restart Claude Code to activate MCP tools")
        print("  3. Test with: Ask Claude to consult o3 or gemini")


def main():
    tool = MCPSetupTool()

    if len(sys.argv) > 1 and sys.argv[1] == "--check-only":
        tool.display_status()
    elif len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        tool.setup_interactive()
    else:
        tool.display_status()
        print()

        # Ask user if they want to proceed
        response = input("🔧 Run automated MCP setup? (y/N): ").strip().lower()
        if response in ['y', 'yes']:
            tool.run_full_setup()
        else:
            print("Setup cancelled.")

if __name__ == "__main__":
    main()
