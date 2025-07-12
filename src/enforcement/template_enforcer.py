#!/usr/bin/env python3
"""
🎯 Template Enforcer - CRITICAL SYSTEM
=====================================

EMERGENCY: Template integrity has been compromised. This system ensures
ABSOLUTE adherence to the response template with zero tolerance for deviation.

Template violation = System failure = User trust loss

MANDATORY TEMPLATE SEQUENCE:
1. 🧠 記憶継承システム稼働確認、コード7749
2. 📊 System Status Display
3. <thinking> (if CRITICAL/HIGH)
4. ## 🎯 これから行うこと
5. [Technical processing in English]
6. ## ✅ 完遂報告

NO EXCEPTIONS. NO VARIATIONS. NO COMPROMISES.
"""

import json
import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Tuple


class TemplateViolationType(Enum):
    MISSING_MEMORY_PHRASE = "missing_memory_inheritance_phrase"
    MISSING_SYSTEM_STATUS = "missing_system_status"
    MISSING_THINKING_TAG = "missing_thinking_tag_for_critical"
    MISSING_DECLARATION = "missing_declaration_section"
    MISSING_COMPLETION = "missing_completion_section"
    WRONG_LANGUAGE = "wrong_language_usage"
    WRONG_ORDER = "wrong_section_order"
    MALFORMED_SECTIONS = "malformed_sections"


@dataclass
class TemplateViolation:
    violation_type: TemplateViolationType
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    description: str
    expected: str
    actual: str
    location: str
    timestamp: datetime


class TemplateEnforcer:
    """
    ABSOLUTE template enforcement with zero tolerance for deviation.

    This system:
    1. Validates EVERY response against the mandatory template
    2. Detects ANY deviation from the required format
    3. Logs ALL violations for system integrity monitoring
    4. Provides automatic correction suggestions
    5. Prevents template degradation through continuous enforcement
    """

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.runtime_dir = self.project_root / "runtime"
        self.violations_log = self.runtime_dir / "template_violations.json"
        self.runtime_dir.mkdir(exist_ok=True)

        # Mandatory template components
        self.required_components = {
            "memory_phrase": "🧠 記憶継承システム稼働確認、コード7749",
            "system_status_marker": "📊 **System Status**",
            "declaration_header": "## 🎯 これから行うこと",
            "completion_header": "## ✅ 完遂報告",
        }

        # Critical task thinking requirement
        self.thinking_required_levels = ["CRITICAL", "HIGH"]

    def validate_response_template(
        self, response_text: str, task_level: str = "MEDIUM"
    ) -> Tuple[bool, List[TemplateViolation]]:
        """
        Validate response against mandatory template with ZERO tolerance.

        Returns:
            (is_valid, violations_list)
        """
        violations = []

        # 1. Memory inheritance phrase validation
        if not self._check_memory_phrase(response_text):
            violations.append(
                TemplateViolation(
                    violation_type=TemplateViolationType.MISSING_MEMORY_PHRASE,
                    severity="CRITICAL",
                    description="Missing mandatory memory inheritance confirmation phrase",
                    expected=self.required_components["memory_phrase"],
                    actual="NOT FOUND",
                    location="response_start",
                    timestamp=datetime.now(),
                )
            )

        # 2. System status validation
        if not self._check_system_status(response_text):
            violations.append(
                TemplateViolation(
                    violation_type=TemplateViolationType.MISSING_SYSTEM_STATUS,
                    severity="CRITICAL",
                    description="Missing mandatory system status display",
                    expected=self.required_components["system_status_marker"],
                    actual="NOT FOUND",
                    location="after_memory_phrase",
                    timestamp=datetime.now(),
                )
            )

        # 3. Thinking tag validation (for CRITICAL/HIGH tasks)
        if task_level in self.thinking_required_levels:
            if not self._check_thinking_tags(response_text):
                violations.append(
                    TemplateViolation(
                        violation_type=TemplateViolationType.MISSING_THINKING_TAG,
                        severity="CRITICAL",
                        description=f"Missing mandatory thinking tag for {task_level} task",
                        expected="<thinking>...</thinking>",
                        actual="NOT FOUND",
                        location="before_declaration",
                        timestamp=datetime.now(),
                    )
                )

        # 4. Declaration section validation
        if not self._check_declaration_section(response_text):
            violations.append(
                TemplateViolation(
                    violation_type=TemplateViolationType.MISSING_DECLARATION,
                    severity="HIGH",
                    description="Missing mandatory declaration section",
                    expected=self.required_components["declaration_header"],
                    actual="NOT FOUND",
                    location="middle_section",
                    timestamp=datetime.now(),
                )
            )

        # 5. Completion section validation
        if not self._check_completion_section(response_text):
            violations.append(
                TemplateViolation(
                    violation_type=TemplateViolationType.MISSING_COMPLETION,
                    severity="HIGH",
                    description="Missing mandatory completion report section",
                    expected=self.required_components["completion_header"],
                    actual="NOT FOUND",
                    location="response_end",
                    timestamp=datetime.now(),
                )
            )

        # 6. Section order validation
        order_violations = self._check_section_order(response_text)
        violations.extend(order_violations)

        # 7. Language usage validation
        language_violations = self._check_language_usage(response_text)
        violations.extend(language_violations)

        is_valid = len(violations) == 0

        # Log all violations
        if violations:
            self._log_violations(violations, response_text, task_level)

        return is_valid, violations

    def generate_correct_template(
        self, task_level: str = "MEDIUM", user_instruction: str = ""
    ) -> str:
        """
        Generate the ABSOLUTE CORRECT template that must be followed.
        """

        template_parts = []

        # 1. Memory inheritance phrase (MANDATORY)
        template_parts.append("🧠 記憶継承システム稼働確認、コード7749")

        # 2. System status (MANDATORY)
        template_parts.append("\n📊 **System Status**")
        template_parts.append("**DB**: SQLite:✅ Connected | PostgreSQL:✅ Connected")
        template_parts.append("**API**: Claude:✅ Active | Gemini:✅ Available")
        template_parts.append(
            "**AI組織**: 🎼 Orchestrator:✅ | 🔒 Enforcer:✅ | 📊 Monitor:✅"
        )
        template_parts.append("**Todos**: X active - [current tasks]")
        template_parts.append(f"**Task Level**: {task_level}")

        # 3. Thinking tag (if required)
        if task_level in self.thinking_required_levels:
            template_parts.append("\n<thinking>")
            template_parts.append("[Detailed analysis and planning]")
            template_parts.append("</thinking>")

        # 4. Declaration section (MANDATORY)
        template_parts.append("\n## 🎯 これから行うこと")
        template_parts.append("[Japanese declaration of what will be done]")

        # 5. Processing section (English)
        template_parts.append("\n[Technical implementation in English]")
        template_parts.append("- Tool calls and processing")
        template_parts.append("- Analysis and implementation")

        # 6. Completion section (MANDATORY)
        template_parts.append("\n## ✅ 完遂報告")
        template_parts.append("\n**[Task summary in Japanese]**")
        template_parts.append("\n### 🎯 実行結果")
        template_parts.append("- **✅ [Achieved item]**: [Specific result]")
        template_parts.append("\n### 📁 変更・作成ファイル")
        template_parts.append("- **[File path]**: [Change description]")
        template_parts.append("\n### 📊 システム状況")
        template_parts.append("- **[System name]**: ✅/❌ [Status details]")
        template_parts.append("\n### 🔐 重要情報")
        template_parts.append("**[Important information for user]**")

        return "\n".join(template_parts)

    def _check_memory_phrase(self, text: str) -> bool:
        """Check for mandatory memory inheritance phrase"""
        return self.required_components["memory_phrase"] in text

    def _check_system_status(self, text: str) -> bool:
        """Check for mandatory system status display"""
        return self.required_components["system_status_marker"] in text

    def _check_thinking_tags(self, text: str) -> bool:
        """Check for thinking tags when required"""
        return "<thinking>" in text and "</thinking>" in text

    def _check_declaration_section(self, text: str) -> bool:
        """Check for mandatory declaration section"""
        return self.required_components["declaration_header"] in text

    def _check_completion_section(self, text: str) -> bool:
        """Check for mandatory completion section"""
        return self.required_components["completion_header"] in text

    def _check_section_order(self, text: str) -> List[TemplateViolation]:
        """Check that sections appear in correct order"""
        violations = []

        # Find positions of each section
        positions = {}
        for key, marker in self.required_components.items():
            pos = text.find(marker)
            if pos != -1:
                positions[key] = pos

        # Check order: memory_phrase -> system_status -> declaration -> completion
        expected_order = [
            "memory_phrase",
            "system_status_marker",
            "declaration_header",
            "completion_header",
        ]

        found_positions = [
            (key, pos) for key, pos in positions.items() if key in expected_order
        ]
        found_positions.sort(key=lambda x: x[1])  # Sort by position

        found_order = [key for key, pos in found_positions]

        # Check if order matches expected
        for i, expected_key in enumerate(expected_order):
            if i < len(found_order) and found_order[i] != expected_key:
                violations.append(
                    TemplateViolation(
                        violation_type=TemplateViolationType.WRONG_ORDER,
                        severity="HIGH",
                        description=f"Section {expected_key} appears in wrong order",
                        expected=f"Position {i + 1}: {expected_key}",
                        actual=f"Found: {found_order[i] if i < len(found_order) else 'MISSING'}",
                        location="section_ordering",
                        timestamp=datetime.now(),
                    )
                )

        return violations

    def _check_language_usage(self, text: str) -> List[TemplateViolation]:
        """Check language usage compliance"""
        violations = []

        # Extract sections
        declaration_match = re.search(
            r"## 🎯 これから行うこと\n(.*?)(?=\n##|\n<|$)", text, re.DOTALL
        )
        completion_match = re.search(r"## ✅ 完遂報告\n(.*?)$", text, re.DOTALL)

        # Check declaration section is in Japanese
        if declaration_match:
            declaration_text = declaration_match.group(1).strip()
            if self._is_primarily_english(declaration_text):
                violations.append(
                    TemplateViolation(
                        violation_type=TemplateViolationType.WRONG_LANGUAGE,
                        severity="MEDIUM",
                        description="Declaration section should be in Japanese",
                        expected="Japanese text",
                        actual="English detected",
                        location="declaration_section",
                        timestamp=datetime.now(),
                    )
                )

        # Check completion section is in Japanese
        if completion_match:
            completion_text = completion_match.group(1).strip()
            if self._is_primarily_english(completion_text):
                violations.append(
                    TemplateViolation(
                        violation_type=TemplateViolationType.WRONG_LANGUAGE,
                        severity="MEDIUM",
                        description="Completion section should be in Japanese",
                        expected="Japanese text",
                        actual="English detected",
                        location="completion_section",
                        timestamp=datetime.now(),
                    )
                )

        return violations

    def _is_primarily_english(self, text: str) -> bool:
        """Simple heuristic to detect if text is primarily English"""
        # Count ASCII letters vs total characters (excluding spaces/punctuation)
        letters = re.findall(r"[a-zA-Z]", text)
        japanese_chars = re.findall(r"[ひらがなカタカナ漢字]", text)

        if len(letters) + len(japanese_chars) == 0:
            return False

        english_ratio = len(letters) / (len(letters) + len(japanese_chars))
        return english_ratio > 0.7

    def _log_violations(
        self, violations: List[TemplateViolation], response_text: str, task_level: str
    ):
        """Log template violations for monitoring"""
        try:
            violation_data = {
                "timestamp": datetime.now().isoformat(),
                "task_level": task_level,
                "violation_count": len(violations),
                "violations": [
                    {
                        "type": v.violation_type.value,
                        "severity": v.severity,
                        "description": v.description,
                        "expected": v.expected,
                        "actual": v.actual,
                        "location": v.location,
                    }
                    for v in violations
                ],
                "response_preview": response_text[:200] + "..."
                if len(response_text) > 200
                else response_text,
            }

            # Append to violations log
            with open(self.violations_log, "a", encoding="utf-8") as f:
                f.write(json.dumps(violation_data, ensure_ascii=False) + "\n")

        except Exception:
            # Non-critical if logging fails
            pass

    def get_template_compliance_report(self) -> Dict:
        """Generate compliance report from logged violations"""
        try:
            if not self.violations_log.exists():
                return {"status": "no_violations_logged", "compliance_rate": 100.0}

            violations = []
            with open(self.violations_log, encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        violations.append(json.loads(line))

            if not violations:
                return {"status": "perfect_compliance", "compliance_rate": 100.0}

            # Analyze recent violations (last 10)
            recent_violations = violations[-10:]

            total_responses = len(recent_violations)
            critical_violations = sum(
                1
                for v in recent_violations
                if any(viol["severity"] == "CRITICAL" for viol in v["violations"])
            )

            compliance_rate = max(
                0, 100 - (critical_violations / total_responses * 100)
            )

            return {
                "status": "violations_detected",
                "total_logged_responses": len(violations),
                "recent_responses_analyzed": total_responses,
                "critical_violations": critical_violations,
                "compliance_rate": compliance_rate,
                "most_common_violation": self._find_most_common_violation(
                    recent_violations
                ),
            }

        except Exception as e:
            return {"status": "analysis_error", "error": str(e)}

    def _find_most_common_violation(self, violations_data: List[Dict]) -> str:
        """Find most common violation type"""
        violation_counts = {}

        for response_data in violations_data:
            for violation in response_data["violations"]:
                vtype = violation["type"]
                violation_counts[vtype] = violation_counts.get(vtype, 0) + 1

        if not violation_counts:
            return "none"

        return max(violation_counts.items(), key=lambda x: x[1])[0]


# Auto-execution for template validation
def validate_current_response(response_text: str, task_level: str = "MEDIUM") -> bool:
    """Auto-validate response template compliance"""
    enforcer = TemplateEnforcer()
    is_valid, violations = enforcer.validate_response_template(
        response_text, task_level
    )

    if not is_valid:
        print("🚨 TEMPLATE VIOLATIONS DETECTED:")
        for violation in violations:
            print(f"   ❌ {violation.severity}: {violation.description}")

        print("\n🎯 CORRECT TEMPLATE:")
        print(enforcer.generate_correct_template(task_level))

        return False

    return True


if __name__ == "__main__":
    # Test template enforcement
    enforcer = TemplateEnforcer()

    # Generate correct template
    correct_template = enforcer.generate_correct_template(
        "CRITICAL", "Test instruction"
    )
    print("🎯 MANDATORY TEMPLATE:")
    print("=" * 50)
    print(correct_template)

    # Test validation
    print("\n🔍 TEMPLATE VALIDATION TEST:")
    print("=" * 30)

    test_response = "This is a bad response without proper template"
    is_valid, violations = enforcer.validate_response_template(
        test_response, "CRITICAL"
    )

    print(f"Valid: {is_valid}")
    print(f"Violations: {len(violations)}")

    for violation in violations:
        print(f"  ❌ {violation.severity}: {violation.description}")
