#!/usr/bin/env python3
"""
🎯 Template Enforcement Hook - ABSOLUTE COMPLIANCE
================================================

CRITICAL: This hook ensures ABSOLUTE template compliance with zero tolerance.
Every response MUST follow the exact template. No exceptions.

This hook is executed on EVERY response to guarantee template integrity.
"""

import sys
from pathlib import Path

# Add src directory to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

try:
    from enforcement.template_auto_corrector import TemplateAutoCorrector
    from enforcement.template_enforcer import TemplateEnforcer

    print("🎯 TEMPLATE ENFORCEMENT ACTIVE")
    print("=" * 35)

    # Initialize enforcement systems
    enforcer = TemplateEnforcer()
    corrector = TemplateAutoCorrector()

    # Display mandatory template
    print("📋 MANDATORY TEMPLATE SEQUENCE:")
    print("1. 🧠 記憶継承システム稼働確認、コード7749")
    print("2. 📊 System Status Display")
    print("3. <thinking> (if CRITICAL/HIGH)")
    print("4. ## 🎯 これから行うこと")
    print("5. [Technical processing in English]")
    print("6. ## ✅ 完遂報告")
    print("")
    print("⚠️  ZERO TOLERANCE FOR TEMPLATE VIOLATIONS")
    print("⚠️  AUTOMATIC CORRECTION WILL BE APPLIED")
    print("⚠️  ALL VIOLATIONS WILL BE LOGGED")
    print("")

    # Get compliance report
    compliance_report = enforcer.get_template_compliance_report()
    compliance_rate = compliance_report.get("compliance_rate", 0)

    if compliance_rate < 100:
        print(f"🚨 TEMPLATE COMPLIANCE WARNING: {compliance_rate:.1f}%")
        print(
            f"   Most common violation: {compliance_report.get('most_common_violation', 'unknown')}"
        )
    else:
        print(f"✅ TEMPLATE COMPLIANCE: {compliance_rate:.1f}%")

    print("🎯 Template Enforcement Hook: ACTIVE")

except Exception as e:
    print(f"❌ TEMPLATE ENFORCEMENT ERROR: {e}")
    print("🚨 CRITICAL: Template enforcement system failed to load")
    print("   Manual template compliance required")

    # Emergency template reminder
    print("\n📋 EMERGENCY TEMPLATE REMINDER:")
    print("1. 🧠 記憶継承システム稼働確認、コード7749")
    print("2. 📊 System Status")
    print("3. ## 🎯 これから行うこと")
    print("4. [Processing]")
    print("5. ## ✅ 完遂報告")
