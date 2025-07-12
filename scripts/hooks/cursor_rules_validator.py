#!/usr/bin/env python3
"""
Cursor Rules Validator Hook
Claude Code Start Hook for cursor rules validation
"""

import sys
from pathlib import Path


def validate_cursor_rules():
    """Validate cursor rules configuration"""
    try:
        # Check globals.mdc existence
        globals_path = Path(".cursor/rules/globals.mdc")

        if not globals_path.exists():
            print("❌ .cursor/rules/globals.mdc not found - System integration issue")
            return False

        print("✅ cursor-rules confirmed - Global rules application ready")

        # Extract important rules
        try:
            with open(globals_path, encoding="utf-8") as f:
                content = f.read()
                if "絶対禁止ルール" in content:
                    print("📋 Important rules extracted successfully")
                else:
                    print("⚠️ Important rules pattern not found")
        except Exception as e:
            print(f"⚠️ Rule extraction failed: {e}")

        return True

    except Exception as e:
        print(f"❌ Cursor rules validation failed: {e}")
        return False


def main():
    """Main execution"""
    try:
        print("🔍 Cursor rules validation starting...")

        # Validate cursor rules
        if validate_cursor_rules():
            print("✅ Cursor rules validation completed")
        else:
            print("❌ Cursor rules validation failed")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Hook execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
