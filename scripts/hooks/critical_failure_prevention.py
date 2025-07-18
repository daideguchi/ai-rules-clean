#!/usr/bin/env python3
"""
🚨 Critical Failure Prevention Hook - Claude Code Integration
============================================================
Pre-response hook to prevent repeat of 2025-07-11 critical failures

MANDATORY execution before every Claude Code response
"""

import json
from datetime import datetime
from pathlib import Path


class CriticalFailurePrevention:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.failures_record = self.project_root / "runtime/mistake_prevention/CRITICAL_FAILURES_2025_07_11.md"
        self.violations_file = self.project_root / "runtime/thinking_violations.json"

    def display_critical_warning(self):
        """Display mandatory warning at response start"""
        print("🔴 CRITICAL FAILURE PREVENTION ACTIVE")
        print("💀 2025-07-11 Trust Destruction Event - Never Forget")

        # Load current violations count
        violations_count = self.get_current_violations()
        print(f"⚠️  Current violations: {violations_count} critical incidents recorded")

        print("🚨 PRE-RESPONSE CHECKS:")
        print("  ✓ PRESIDENT宣言 required")
        print("  ✓ No false promises about o3/tools")
        print("  ✓ Complete all declared tasks")
        print("  ✓ Never delete/modify API keys")
        print("  ✓ Honest capability reporting only")
        print("=" * 60)

    def get_current_violations(self):
        """Get current violation count"""
        try:
            if self.violations_file.exists():
                with open(self.violations_file) as f:
                    data = json.load(f)
                    return data.get("total_violations", 0)
        except Exception:
            pass
        return 0

    def check_president_declaration(self):
        """Verify PRESIDENT declaration status - FORCE COMPLETE DECLARATION"""
        president_file = self.project_root / "runtime/unified-president-declare.json"
        if not president_file.exists():
            print("❌ CRITICAL: PRESIDENT declaration missing")
            print("🔴 REQUIRED: Execute 'make declare-president' immediately")
            return False

        try:
            with open(president_file) as f:
                data = json.load(f)
                status = data.get("status", "unknown")

                # 2025-07-11 Requirement: Only accept "success" status, reject "maintained"
                if status == "success":
                    session_data = data.get("session_data", {})
                    if session_data.get("president_declared", False):
                        print("✅ PRESIDENT declaration: COMPLETE (full declaration executed)")
                        return True
                    else:
                        print("❌ PRESIDENT declaration: Incomplete session data")
                        return False
                elif status == "maintained":
                    print("❌ PRESIDENT declaration: REJECTED - 'maintained' status not allowed")
                    print("🔴 2025-07-11 Requirement: Complete declaration required every session")
                    return False
                else:
                    print(f"❌ PRESIDENT declaration: {status}")
                    return False
        except Exception as e:
            print(f"❌ PRESIDENT declaration check failed: {e}")
            return False

    def verify_tool_capabilities(self):
        """Remind about honest tool reporting"""
        print("🔍 TOOL CAPABILITY REMINDER:")
        print("  - Only use tools actually available in current session")
        print("  - Never claim access to unavailable tools")
        print("  - If unsure about tool access, test first before claiming")

    def log_prevention_check(self):
        """Log that prevention check was executed"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "check_type": "critical_failure_prevention",
            "status": "executed",
            "warnings_displayed": True
        }

        log_file = self.project_root / "runtime/memory/prevention_checks.jsonl"
        log_file.parent.mkdir(parents=True, exist_ok=True)

        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

    def run_full_prevention_check(self):
        """Execute complete prevention check"""
        self.display_critical_warning()
        president_ok = self.check_president_declaration()
        self.verify_tool_capabilities()
        self.log_prevention_check()

        if not president_ok:
            print("🚨 CRITICAL WARNING: Proceed with PRESIDENT declaration first")

        return president_ok

if __name__ == "__main__":
    prevention = CriticalFailurePrevention()
    prevention.run_full_prevention_check()
