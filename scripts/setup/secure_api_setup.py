#!/usr/bin/env python3
"""
Secure API Key Setup
APIキーを安全に環境変数として設定（ファイルにハードコードしない）
"""

import os
import sys
from pathlib import Path


class SecureAPISetup:
    """セキュアなAPIキー設定"""

    def __init__(self):
        self.home_dir = Path.home()
        self.shell_profiles = [
            self.home_dir / ".zshrc",
            self.home_dir / ".bashrc",
            self.home_dir / ".bash_profile"
        ]

    def setup_anthropic_api_key_prompt(self):
        """Anthropic APIキーの安全な設定（プロンプトベース）"""
        print("🔐 Secure Anthropic API Key Setup")
        print("=" * 40)
        print("This will add ANTHROPIC_API_KEY to your shell profile securely.")
        print("The key will NOT be stored in any repository files.")
        print()

        # 現在の設定確認
        current_key = os.environ.get('ANTHROPIC_API_KEY', '')
        if current_key:
            masked_key = f"{current_key[:15]}...{current_key[-10:]}" if len(current_key) > 25 else "***masked***"
            print(f"✅ Current session has API key: {masked_key}")

            choice = input("Do you want to persist this to shell profile? (y/n): ").lower()
            if choice == 'y':
                return self._add_to_shell_profile('ANTHROPIC_API_KEY', current_key)
            else:
                print("❌ Setup cancelled by user")
                return False
        else:
            print("❌ No ANTHROPIC_API_KEY found in current session")
            print("Please set the environment variable first:")
            print('export ANTHROPIC_API_KEY="your-api-key-here"')
            return False

    def _add_to_shell_profile(self, var_name: str, var_value: str) -> bool:
        """シェルプロファイルに環境変数を追加"""
        # 適切なシェルプロファイルを検出
        target_profile = None
        for profile in self.shell_profiles:
            if profile.exists():
                target_profile = profile
                break

        if not target_profile:
            print("❌ No shell profile found (.zshrc, .bashrc, .bash_profile)")
            return False

        print(f"📝 Adding to {target_profile}")

        # 既存の設定をチェック
        try:
            with open(target_profile) as f:
                content = f.read()

            if f'export {var_name}=' in content:
                print(f"⚠️ {var_name} already exists in {target_profile}")
                choice = input("Overwrite existing setting? (y/n): ").lower()
                if choice != 'y':
                    print("❌ Setup cancelled")
                    return False
        except Exception as e:
            print(f"❌ Error reading {target_profile}: {e}")
            return False

        # 新しい設定を追加
        try:
            with open(target_profile, 'a') as f:
                f.write('\n# Anthropic API Key (added by secure_api_setup.py)\n')
                f.write(f'export {var_name}="{var_value}"\n')

            print(f"✅ Successfully added {var_name} to {target_profile}")
            print("🔄 Please restart your terminal or run:")
            print(f"   source {target_profile}")
            return True

        except Exception as e:
            print(f"❌ Error writing to {target_profile}: {e}")
            return False

    def verify_api_key(self):
        """APIキーの動作確認"""
        api_key = os.environ.get('ANTHROPIC_API_KEY', '')
        if not api_key:
            print("❌ ANTHROPIC_API_KEY not found in environment")
            return False

        if not api_key.startswith('sk-ant-'):
            print("❌ Invalid Anthropic API key format")
            return False

        print("✅ Anthropic API key format is valid")

        # Claude Codeとの連携確認
        try:
            import subprocess
            result = subprocess.run(
                ['claude', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print("✅ Claude Code CLI is available")
                return True
            else:
                print("⚠️ Claude Code CLI not available (non-critical)")
                return True
        except Exception as e:
            print(f"⚠️ Claude Code CLI check failed: {e} (non-critical)")
            return True

    def security_check(self):
        """セキュリティチェック"""
        print("\n🔍 Security Check")
        print("-" * 20)

        # .envファイルにAPIキーがないかチェック
        env_files = [
            '.env',
            '.env.local',
            '.env.development'
        ]

        project_root = Path.cwd()
        for env_file in env_files:
            env_path = project_root / env_file
            if env_path.exists():
                try:
                    with open(env_path) as f:
                        content = f.read()
                    if 'ANTHROPIC_API_KEY' in content:
                        print(f"⚠️ Warning: ANTHROPIC_API_KEY found in {env_file}")
                        print("   Consider removing it from the file for security")
                    else:
                        print(f"✅ {env_file} is clean")
                except Exception:
                    pass

        # gitignoreの確認
        gitignore_path = project_root / '.gitignore'
        if gitignore_path.exists():
            try:
                with open(gitignore_path) as f:
                    content = f.read()
                if '.env' in content:
                    print("✅ .env files are properly gitignored")
                else:
                    print("⚠️ Consider adding .env* to .gitignore")
            except Exception:
                pass

        print("✅ Security check completed")


def main():
    """メイン実行"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python secure_api_setup.py setup   # Setup API key")
        print("  python secure_api_setup.py verify  # Verify API key")
        print("  python secure_api_setup.py check   # Security check")
        sys.exit(1)

    command = sys.argv[1]
    setup = SecureAPISetup()

    if command == "setup":
        success = setup.setup_anthropic_api_key_prompt()
        sys.exit(0 if success else 1)

    elif command == "verify":
        success = setup.verify_api_key()
        sys.exit(0 if success else 1)

    elif command == "check":
        setup.security_check()

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()