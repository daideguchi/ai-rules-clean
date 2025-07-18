#!/usr/bin/env python3
"""
Quick API Key Setup Tool
簡単APIキー設定ツール

Usage:
    python3 scripts/setup/quick_api_setup.py
    python3 scripts/setup/quick_api_setup.py --openai
    python3 scripts/setup/quick_api_setup.py --gemini
    python3 scripts/setup/quick_api_setup.py --check
"""

import getpass
import os
import sys
from pathlib import Path
from typing import Dict


class QuickAPISetup:
    def __init__(self):
        self.project_root = Path.cwd()
        self.env_file = self.project_root / ".env"

    def check_api_keys(self) -> Dict[str, str]:
        """Check current API key status"""
        status = {}

        # Check OpenAI
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key and openai_key.startswith('sk-'):
            status['OpenAI'] = f"✅ 設定済み (sk-...{openai_key[-4:]})"
        else:
            status['OpenAI'] = "❌ 未設定"

        # Check Gemini
        gemini_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if gemini_key:
            status['Gemini'] = f"✅ 設定済み (...{gemini_key[-4:]})"
        else:
            status['Gemini'] = "❌ 未設定"

        return status

    def display_status(self):
        """Display current API key status"""
        print("🔑 API Key Status")
        print("=" * 30)

        status = self.check_api_keys()
        for service, msg in status.items():
            print(f"  • {service}: {msg}")
        print()

    def setup_openai_key(self, interactive: bool = True) -> bool:
        """Setup OpenAI API key"""
        if interactive:
            print("🔧 OpenAI API Key Setup")
            print("-" * 25)
            print("📋 Where to get your API key:")
            print("   https://platform.openai.com/api-keys")
            print()

            api_key = getpass.getpass("🔑 Enter your OpenAI API key (sk-...): ").strip()
        else:
            api_key = input("OpenAI API key: ").strip()

        if not api_key:
            print("❌ No API key provided")
            return False

        if not api_key.startswith('sk-'):
            print("⚠️  Warning: OpenAI API keys typically start with 'sk-'")

        # Add to .env file
        self._add_to_env_file('OPENAI_API_KEY', api_key)
        print("✅ OpenAI API key added to .env file")

        # Update current environment
        os.environ['OPENAI_API_KEY'] = api_key
        return True

    def setup_gemini_key(self, interactive: bool = True) -> bool:
        """Setup Gemini API key"""
        if interactive:
            print("🔧 Gemini API Key Setup")
            print("-" * 22)
            print("📋 Where to get your API key:")
            print("   https://aistudio.google.com/app/apikey")
            print()

            api_key = getpass.getpass("🔑 Enter your Gemini API key: ").strip()
        else:
            api_key = input("Gemini API key: ").strip()

        if not api_key:
            print("❌ No API key provided")
            return False

        # Add to .env file
        self._add_to_env_file('GEMINI_API_KEY', api_key)
        print("✅ Gemini API key added to .env file")

        # Update current environment
        os.environ['GEMINI_API_KEY'] = api_key
        return True

    def _add_to_env_file(self, key: str, value: str):
        """Add or update key in .env file"""
        env_lines = []
        key_found = False

        # Read existing .env file if it exists
        if self.env_file.exists():
            with open(self.env_file) as f:
                env_lines = f.readlines()

        # Update or add the key
        new_lines = []
        for line in env_lines:
            if line.strip().startswith(f"{key}="):
                new_lines.append(f"{key}={value}\n")
                key_found = True
            else:
                new_lines.append(line)

        # Add key if not found
        if not key_found:
            new_lines.append(f"{key}={value}\n")

        # Write back to file
        with open(self.env_file, 'w') as f:
            f.writelines(new_lines)

    def interactive_setup(self):
        """Interactive setup for multiple API keys"""
        print("🚀 Quick API Setup Tool")
        print("=" * 25)

        self.display_status()

        # Check what needs setup
        status = self.check_api_keys()
        needs_setup = [k for k, v in status.items() if "❌" in v]

        if not needs_setup:
            print("🎉 All API keys are already configured!")
            return

        print(f"📝 Found {len(needs_setup)} API key(s) that need setup: {', '.join(needs_setup)}")
        print()

        # Setup each missing key
        for service in needs_setup:
            response = input(f"🔧 Setup {service} API key? (y/N): ").strip().lower()
            if response in ['y', 'yes']:
                if service == 'OpenAI':
                    self.setup_openai_key()
                elif service == 'Gemini':
                    self.setup_gemini_key()
                print()

        # Final status
        print("🎉 Setup Complete!")
        self.display_status()

        print("📋 Next Steps:")
        print("  1. Restart your terminal/Claude Code to load environment variables")
        print("  2. Run: python3 scripts/setup/auto_mcp_setup.py")
        print("  3. Test API access with your AI tools")

    def quick_setup_all(self):
        """Non-interactive setup for all missing keys"""
        print("🚀 Quick Setup - All Missing APIs")
        print("=" * 35)

        status = self.check_api_keys()
        needs_setup = [k for k, v in status.items() if "❌" in v]

        if not needs_setup:
            print("✅ All API keys already configured")
            return

        for service in needs_setup:
            print(f"\n🔧 Setting up {service}...")
            if service == 'OpenAI':
                if not self.setup_openai_key(interactive=False):
                    break
            elif service == 'Gemini':
                if not self.setup_gemini_key(interactive=False):
                    break

        self.display_status()


def main():
    tool = QuickAPISetup()

    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()

        if arg == "--check":
            tool.display_status()
        elif arg == "--openai":
            tool.setup_openai_key()
        elif arg == "--gemini":
            tool.setup_gemini_key()
        elif arg == "--all":
            tool.quick_setup_all()
        else:
            print("Usage: python3 quick_api_setup.py [--check|--openai|--gemini|--all]")
    else:
        tool.interactive_setup()


if __name__ == "__main__":
    main()
