#!/usr/bin/env python3
"""
🛡️ Security Framework Setup
============================
Complete security system setup and configuration
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: str, cwd: Path = None) -> bool:
    """Run a command and return success status"""
    try:
        result = subprocess.run(
            cmd, shell=True, cwd=cwd, capture_output=True, text=True
        )
        if result.returncode == 0:
            print(f"✅ {cmd}")
            return True
        else:
            print(f"❌ {cmd}")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {cmd} - Exception: {e}")
        return False


def main():
    """Main setup function"""
    project_root = Path(__file__).parent.parent.parent

    print("🛡️ SECURITY FRAMEWORK SETUP")
    print("=" * 50)

    steps = [
        "🔍 Installing security dependencies",
        "🔒 Setting up pre-commit hooks",
        "📊 Initializing secret detection",
        "🚨 Configuring security validation",
        "🧠 Updating memory system",
        "✅ Finalizing security setup",
    ]

    success_count = 0

    # 1. Install security dependencies
    print(f"\\n{steps[0]}...")
    if run_command("pip install detect-secrets pre-commit", project_root):
        success_count += 1

    # 2. Setup pre-commit hooks
    print(f"\\n{steps[1]}...")
    if run_command("pre-commit install", project_root):
        success_count += 1

    # 3. Initialize secret detection
    print(f"\\n{steps[2]}...")
    if run_command("detect-secrets scan --baseline .secrets.baseline", project_root):
        success_count += 1

    # 4. Configure security validation
    print(f"\\n{steps[3]}...")
    if run_command("python3 scripts/security/validate_secrets.py", project_root):
        success_count += 1

    # 5. Update memory system
    print(f"\\n{steps[4]}...")
    memory_cmd = '''python3 -c "
import sys
sys.path.append('.')
from src.memory.enhanced_memory_inheritance import get_memory_system
memory = get_memory_system()
memory.store_memory('SECURITY_FRAMEWORK_SETUP', 'Security framework successfully configured and activated', 10, 'security_system', ['security', 'setup', 'framework'])
print('Security framework setup recorded in memory')
"'''
    if run_command(memory_cmd, project_root):
        success_count += 1

    # 6. Final validation
    print(f"\\n{steps[5]}...")
    if run_command("python3 scripts/security/validate_secrets.py", project_root):
        success_count += 1

    print(f"\\n{'=' * 50}")
    print("🏆 SECURITY SETUP COMPLETE")
    print(f"✅ Completed: {success_count}/{len(steps)} steps")

    if success_count == len(steps):
        print("\\n🛡️ Security framework is fully operational!")
        print("🔒 All security promises are now technically enforced")

        # Show security status
        print("\\n📊 Security Status:")
        print("• ✅ Secret detection active")
        print("• ✅ Pre-commit hooks configured")
        print("• ✅ Environment variables enforced")
        print("• ✅ Memory system updated")
        print("• ✅ Validation pipeline ready")

        print("\\n🎯 Next Steps:")
        print("1. Test with: make security-check")
        print("2. Validate with: make security-validate")
        print("3. Monitor with: make security-status")

        return True
    else:
        print("\\n❌ Security setup incomplete - manual intervention required")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
