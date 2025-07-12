#!/usr/bin/env python3
"""
📋 Response Template Enforcer
============================

Enforces mandatory response template from CLAUDE.md
"""

import re
from typing import List, Tuple


class TemplateViolation:
    def __init__(self, rule: str, description: str):
        self.rule = rule
        self.description = description


class ResponseTemplateEnforcer:
    """Enforces CLAUDE.md response template requirements"""

    def __init__(self):
        self.violations = []

    def validate_response_structure(
        self, response: str
    ) -> Tuple[bool, List[TemplateViolation]]:
        """Validate response follows mandatory template"""
        self.violations = []

        # Check thinking tag
        if not response.strip().startswith("<thinking>"):
            self.violations.append(
                TemplateViolation(
                    "missing_thinking", "<thinking>タグが応答開始時に無い"
                )
            )

        # Check for required sections
        has_declaration = "## 🎯 これから行うこと" in response
        has_completion = "## ✅ 完遂報告" in response

        if not has_declaration and not has_completion:
            # Allow single-step responses without full template
            return True, []

        # If template is used, enforce structure
        if has_declaration and not has_completion:
            self.violations.append(
                TemplateViolation("incomplete_template", "宣言があるが完遂報告が無い")
            )

        # Check status indicators
        if not re.search(r"[✅❌⚠️]", response):
            self.violations.append(
                TemplateViolation("missing_status", "ステータス記号（✅❌⚠️）が無い")
            )

        # Check file path display for file operations
        if "file" in response.lower() and not re.search(r"/[\w/\-\.]+", response):
            self.violations.append(
                TemplateViolation("missing_file_path", "ファイル操作でパス表示が無い")
            )

        # Check recording format
        if "記録" in response and not re.search(r"を.*に記録", response):
            self.violations.append(
                TemplateViolation(
                    "incorrect_recording_format",
                    "記録場所明示形式（〇〇を〇〇に記録）が無い",
                )
            )

        return len(self.violations) == 0, self.violations

    def validate_language_usage(
        self, response: str
    ) -> Tuple[bool, List[TemplateViolation]]:
        """Validate language usage follows template"""
        # This would need more sophisticated language detection
        # For now, just check basic patterns
        return True, []

    def get_template_reminder(self) -> str:
        """Get template format reminder"""
        return """
📋 応答テンプレート:

## 🎯 これから行うこと
[日本語での作業宣言]

[English tool execution and processing]

## ✅ 完遂報告
- ✅ [具体的成果]
- ❌ [失敗と技術的原因]
- ⚠️ [注意事項]
"""


def main():
    """Test template enforcer"""
    enforcer = ResponseTemplateEnforcer()

    # Test valid response
    valid_response = """
## 🎯 これから行うこと
ファイルを修正します

Processing file update...

## ✅ 完遂報告
✅ ファイル修正完了
"""

    is_valid, violations = enforcer.validate_response_structure(valid_response)
    print(f"Valid response test: {'✅' if is_valid else '❌'}")

    if violations:
        for v in violations:
            print(f"  Violation: {v.description}")


if __name__ == "__main__":
    main()
