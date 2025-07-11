#!/usr/bin/env python3
"""
🔴 Mandatory Process Enforcer
============================

Enforces CLAUDE.md directives as absolute requirements.
"""

import json
from pathlib import Path


class ProcessEnforcer:
    """Enforces mandatory processes from CLAUDE.md"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.claude_md = self.project_root / "CLAUDE.md"
        self.violations = []

    def enforce_president_declaration(self) -> bool:
        """Enforce PRESIDENT declaration requirement"""
        president_file = (
            self.project_root / "runtime" / "unified-president-declare.json"
        )

        if not president_file.exists():
            self.violations.append("PRESIDENT declaration missing")
            return False

        try:
            with open(president_file) as f:
                data = json.load(f)
                if data.get("status") != "success":
                    self.violations.append("PRESIDENT declaration failed")
                    return False
        except Exception as e:
            self.violations.append(f"PRESIDENT declaration invalid: {e}")
            return False

        return True

    def enforce_technical_response_only(self, response_text: str) -> bool:
        """Enforce technical response only protocol"""

        # Banned phrases (excuse-making language)
        banned_phrases = [
            "申し訳ありませんでした",
            "理由を考えると",
            "私が指示を正確に理解していなかった",
            "実装時に簡略化してしまった",
            "要求を見落とした",
            "技術的制約があると思い込んだ",
            "私の思考が",
            "私は実装中に",
            "記憶に頼って",
        ]

        for phrase in banned_phrases:
            if phrase in response_text:
                self.violations.append(f"Banned excuse phrase: {phrase}")
                return False

        return True

    def get_violations(self) -> list:
        """Get current violations"""
        return self.violations

    def clear_violations(self):
        """Clear violation list"""
        self.violations = []


def main():
    """Test enforcement"""
    enforcer = ProcessEnforcer()

    print("🔴 Process Enforcement Check")
    print("=" * 30)

    # Check PRESIDENT
    president_ok = enforcer.enforce_president_declaration()
    print(f"PRESIDENT Declaration: {'✅' if president_ok else '❌'}")

    # Show violations
    violations = enforcer.get_violations()
    if violations:
        print("\n❌ Violations:")
        for v in violations:
            print(f"  • {v}")
    else:
        print("✅ All processes compliant")


if __name__ == "__main__":
    main()
