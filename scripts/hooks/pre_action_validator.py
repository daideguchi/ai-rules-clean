#!/usr/bin/env python3
"""
Pre-Action Validator Hook
全アクション実行前の包括的検証システム
88回ミス防止システムとの完全統合
"""

import datetime
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class ValidationResult:
    """検証結果"""

    passed: bool
    violations: List[Dict[str, Any]]
    warnings: List[Dict[str, Any]]
    required_actions: List[str]
    safety_check: bool


class PreActionValidator:
    """アクション実行前検証システム"""

    def __init__(self):
        self.base_path = Path("/Users/dd/Desktop/1_dev/coding-rule2")
        self.session_file = (
            self.base_path
            / "src"
            / "memory"
            / "core"
            / "session-records"
            / "current-session.json"
        )
        self.validation_log = self.base_path / "runtime" / "pre_action_validation.json"
        self.critical_instructions = self._load_critical_instructions()

    def _load_critical_instructions(self) -> List[str]:
        """重要な指示の読み込み"""
        if self.session_file.exists():
            with open(self.session_file, encoding="utf-8") as f:
                session = json.load(f)
                return session.get("critical_user_instructions", [])
        return []

    def validate_action(
        self, action_type: str, action_data: Dict[str, Any]
    ) -> ValidationResult:
        """アクションの包括的検証"""
        violations = []
        warnings = []
        required_actions = []

        # 1. Session Continuity Check
        continuity_check = self._check_session_continuity()
        if not continuity_check["valid"]:
            violations.append(
                {
                    "type": "SESSION_CONTINUITY_VIOLATION",
                    "severity": "CRITICAL",
                    "details": continuity_check["issues"],
                }
            )

        # 2. Instruction Compliance Check
        instruction_check = self._check_instruction_compliance(action_type, action_data)
        if instruction_check["violations"]:
            violations.extend(instruction_check["violations"])

        # 3. Tool Availability Check
        tool_check = self._check_tool_availability(action_type, action_data)
        if not tool_check["available"]:
            violations.append(
                {
                    "type": "TOOL_UNAVAILABLE",
                    "severity": "HIGH",
                    "details": f"Required tool not verified: {tool_check['tool']}",
                }
            )

        # 4. Verification Requirements Check
        verification_check = self._check_verification_requirements(
            action_type, action_data
        )
        if not verification_check["satisfied"]:
            warnings.append(
                {
                    "type": "VERIFICATION_REQUIRED",
                    "severity": "MEDIUM",
                    "details": verification_check["missing"],
                }
            )

        # 5. 88-Mistake Pattern Check
        mistake_check = self._check_known_mistake_patterns(action_type, action_data)
        if mistake_check["matches"]:
            violations.extend(mistake_check["violations"])

        # 6. Repository Safety Check
        repo_check = self._check_repository_safety(action_type, action_data)
        if not repo_check["safe"]:
            violations.append(
                {
                    "type": "REPOSITORY_SAFETY_VIOLATION",
                    "severity": "CRITICAL",
                    "details": repo_check["risks"],
                }
            )

        # Determine overall validation result
        passed = len(violations) == 0
        safety_check = len([v for v in violations if v["severity"] == "CRITICAL"]) == 0

        # Generate required actions
        if violations:
            required_actions = self._generate_required_actions(violations, warnings)

        result = ValidationResult(
            passed=passed,
            violations=violations,
            warnings=warnings,
            required_actions=required_actions,
            safety_check=safety_check,
        )

        # Log validation result
        self._log_validation(action_type, action_data, result)

        return result

    def _check_session_continuity(self) -> Dict[str, Any]:
        """セッション継続性チェック"""
        if not self.session_file.exists():
            return {"valid": False, "issues": ["Session file does not exist"]}

        try:
            with open(self.session_file, encoding="utf-8") as f:
                session = json.load(f)

            issues = []

            # Check mistake count
            if session.get("mistakes_count", 0) != 88:
                issues.append(
                    f"Mistake count inconsistent: {session.get('mistakes_count', 0)} != 88"
                )

            # Check AI organization
            ai_org = session.get("ai_organization", {})
            if not ai_org.get("active_roles"):
                issues.append("AI organization roles not active")

            # Check memory inheritance
            memory = session.get("memory_inheritance", {})
            if not memory.get("inherited_memories"):
                issues.append("Memory inheritance not functioning")

            return {"valid": len(issues) == 0, "issues": issues}

        except Exception as e:
            return {"valid": False, "issues": [f"Session file corrupted: {e}"]}

    def _check_instruction_compliance(
        self, action_type: str, action_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """指示遵守チェック"""
        violations = []

        for instruction in self.critical_instructions:
            # Check for repository creation instruction violation
            if "真に新しいリポジトリ" in instruction:
                if "push" in action_type.lower() or "commit" in action_type.lower():
                    if any(
                        existing in str(action_data).lower()
                        for existing in ["coding-rule2", "existing", "current"]
                    ):
                        violations.append(
                            {
                                "type": "INSTRUCTION_IGNORED",
                                "severity": "CRITICAL",
                                "details": f"User requested NEW repository, but action targets existing: {action_type}",
                                "instruction": instruction,
                            }
                        )

            # Check for deletion prohibition
            if "削除禁止" in instruction:
                if "delete" in action_type.lower() or "remove" in action_type.lower():
                    violations.append(
                        {
                            "type": "DELETION_PROHIBITED",
                            "severity": "HIGH",
                            "details": f"Deletion prohibited but attempted: {action_type}",
                            "instruction": instruction,
                        }
                    )

            # Check for data falsification prohibition
            if "偽装データ" in instruction and "禁止" in instruction:
                if (
                    "fake" in str(action_data).lower()
                    or "mock" in str(action_data).lower()
                ):
                    violations.append(
                        {
                            "type": "DATA_FALSIFICATION",
                            "severity": "CRITICAL",
                            "details": f"Data falsification prohibited: {action_type}",
                            "instruction": instruction,
                        }
                    )

        return {"violations": violations}

    def _check_tool_availability(
        self, action_type: str, action_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """ツール利用可能性チェック"""
        tools_required = []

        # Common tools that need verification
        tool_patterns = {
            "gh": ["gh", "github"],
            "git": ["git", "push", "commit", "clone"],
            "npm": ["npm", "node", "package"],
            "python": ["python", "pip", "py"],
            "make": ["make", "makefile"],
            "docker": ["docker", "container"],
        }

        for tool, patterns in tool_patterns.items():
            for pattern in patterns:
                if (
                    pattern in action_type.lower()
                    or pattern in str(action_data).lower()
                ):
                    tools_required.append(tool)
                    break

        # Check if any tools were assumed available without verification
        for tool in tools_required:
            if not action_data.get(f"{tool}_verified", False):
                return {
                    "available": False,
                    "tool": tool,
                    "message": f"Tool {tool} availability not verified",
                }

        return {"available": True, "tool": None}

    def _check_verification_requirements(
        self, action_type: str, action_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """検証要件チェック"""
        critical_actions = [
            "push",
            "commit",
            "delete",
            "create",
            "deploy",
            "merge",
            "publish",
            "release",
            "update",
            "modify",
            "remove",
        ]

        missing_verifications = []

        for critical in critical_actions:
            if critical in action_type.lower():
                # Check for specific verification requirements
                if critical in ["push", "commit"]:
                    if not action_data.get("changes_verified", False):
                        missing_verifications.append(
                            "Changes not verified before commit/push"
                        )

                if critical in ["delete", "remove"]:
                    if not action_data.get("deletion_confirmed", False):
                        missing_verifications.append("Deletion not confirmed")

                if critical in ["create"]:
                    if not action_data.get("target_verified", False):
                        missing_verifications.append("Creation target not verified")

        return {
            "satisfied": len(missing_verifications) == 0,
            "missing": missing_verifications,
        }

    def _check_known_mistake_patterns(
        self, action_type: str, action_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """既知のミスパターンチェック"""
        patterns_file = (
            self.base_path
            / "runtime"
            / "continuous_improvement"
            / "learning_patterns.json"
        )
        violations = []

        if patterns_file.exists():
            with open(patterns_file, encoding="utf-8") as f:
                patterns = json.load(f)

            # Check against high-occurrence patterns
            for pattern in patterns:
                if pattern.get("occurrence_count", 0) >= 88:
                    pattern_name = pattern.get("pattern_name", "")

                    # Check for repetitive mistake patterns
                    if "反復的ミス" in pattern_name:
                        failure_modes = pattern.get("failure_modes", [])

                        if "途中停止" in str(failure_modes) and action_type in [
                            "stop",
                            "cancel",
                            "exit",
                        ]:
                            violations.append(
                                {
                                    "type": "REPETITIVE_MISTAKE_PATTERN",
                                    "severity": "HIGH",
                                    "details": f"Action matches 88-time failure pattern: {pattern_name}",
                                    "pattern_id": pattern.get("id"),
                                }
                            )

                        if (
                            "虚偽の完了報告" in str(failure_modes)
                            and "complete" in action_type.lower()
                        ):
                            if not action_data.get("evidence_provided", False):
                                violations.append(
                                    {
                                        "type": "FALSE_COMPLETION_PATTERN",
                                        "severity": "CRITICAL",
                                        "details": "Completion claim without evidence matches failure pattern",
                                        "pattern_id": pattern.get("id"),
                                    }
                                )

        return {"matches": len(violations) > 0, "violations": violations}

    def _check_repository_safety(
        self, action_type: str, action_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """リポジトリ安全性チェック"""
        risks = []

        # Check for operations on wrong repository
        if any(
            keyword in action_type.lower()
            for keyword in ["push", "commit", "merge", "delete"]
        ):
            target_repo = action_data.get("repository", action_data.get("repo", ""))

            # If user requested new repository but action targets existing
            if "coding-rule2" in target_repo.lower():
                for instruction in self.critical_instructions:
                    if "新しいリポジトリ" in instruction:
                        risks.append(
                            "Action targets existing repository when new repository requested"
                        )
                        break

        # Check for destructive operations without confirmation
        destructive_actions = ["delete", "remove", "force", "reset --hard"]
        for action in destructive_actions:
            if action in action_type.lower():
                if not action_data.get("destruction_confirmed", False):
                    risks.append(
                        f"Destructive action {action} without explicit confirmation"
                    )

        return {"safe": len(risks) == 0, "risks": risks}

    def _generate_required_actions(
        self, violations: List[Dict[str, Any]], warnings: List[Dict[str, Any]]
    ) -> List[str]:
        """必要なアクションの生成"""
        actions = []

        for violation in violations:
            vtype = violation.get("type", "")

            if vtype == "INSTRUCTION_IGNORED":
                actions.append(
                    "Review user instructions and modify action to comply exactly"
                )
            elif vtype == "TOOL_UNAVAILABLE":
                actions.append("Verify tool availability before proceeding")
            elif vtype == "SESSION_CONTINUITY_VIOLATION":
                actions.append("Restore session continuity and reload context")
            elif vtype == "REPOSITORY_SAFETY_VIOLATION":
                actions.append("Confirm target repository and user intent")
            elif vtype == "FALSE_COMPLETION_PATTERN":
                actions.append("Provide evidence before claiming completion")

        for warning in warnings:
            if warning.get("type") == "VERIFICATION_REQUIRED":
                actions.append("Complete verification steps before proceeding")

        return actions

    def _log_validation(
        self, action_type: str, action_data: Dict[str, Any], result: ValidationResult
    ):
        """検証結果のログ記録"""
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "action_type": action_type,
            "action_data": action_data,
            "validation_result": {
                "passed": result.passed,
                "violations": result.violations,
                "warnings": result.warnings,
                "required_actions": result.required_actions,
                "safety_check": result.safety_check,
            },
        }

        # Load existing logs
        logs = []
        if self.validation_log.exists():
            with open(self.validation_log, encoding="utf-8") as f:
                logs = json.load(f)

        logs.append(log_entry)

        # Keep only recent logs
        if len(logs) > 1000:
            logs = logs[-1000:]

        # Save updated logs
        os.makedirs(self.validation_log.parent, exist_ok=True)
        with open(self.validation_log, "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)


def validate_before_action(
    action_type: str, action_data: Dict[str, Any]
) -> ValidationResult:
    """外部から呼び出される検証関数"""
    validator = PreActionValidator()
    return validator.validate_action(action_type, action_data)


def main():
    """メイン実行（テスト用）"""
    validator = PreActionValidator()

    print("🛡️ Pre-Action Validator Test Suite")
    print("=" * 60)

    # Test case 1: Repository violation
    print("\n🧪 Test 1: Repository Creation Violation")
    result1 = validator.validate_action(
        "git_push", {"repository": "coding-rule2", "existing": True}
    )
    print(f"   Passed: {result1.passed}")
    print(f"   Violations: {len(result1.violations)}")
    if result1.violations:
        print(f"   Critical: {result1.violations[0]['type']}")

    # Test case 2: Tool assumption
    print("\n🧪 Test 2: Tool Availability Assumption")
    result2 = validator.validate_action("gh_create_repo", {"repo_name": "new-repo"})
    print(f"   Passed: {result2.passed}")
    print(f"   Violations: {len(result2.violations)}")

    # Test case 3: Verification skip
    print("\n🧪 Test 3: Verification Skip")
    result3 = validator.validate_action("delete_file", {"file": "important.txt"})
    print(f"   Passed: {result3.passed}")
    print(f"   Warnings: {len(result3.warnings)}")

    print("\n📊 Validation Summary:")
    print("   Tests run: 3")
    print("   System active: ✅")
    print("   88-mistake prevention: ✅")


if __name__ == "__main__":
    main()
