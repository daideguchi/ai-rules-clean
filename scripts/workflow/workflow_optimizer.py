#!/usr/bin/env python3
"""
⚡ Workflow Optimizer
====================
Quick script to show workflow optimization recommendations
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.workflow.command_validator import CommandValidator


def main():
    """Main function"""
    print("⚡ Workflow Optimization Analysis...")

    try:
        validator = CommandValidator()
        recommendations = validator.get_recommended_next_commands()

        print("💡 Recommended Next Commands:")
        for i, cmd in enumerate(recommendations, 1):
            dep = validator.dependencies.get(cmd, None)
            desc = dep.description if dep else "No description"
            print(f"  {i}. {cmd} - {desc}")

        if not recommendations:
            print("✅ No specific recommendations - system appears to be in good state!")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
