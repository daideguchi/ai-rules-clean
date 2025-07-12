#!/usr/bin/env python3
"""
Session Continuity Enforcer - 緊急実装
セッション継続性を強制し、指示違反を防止するシステム
"""

import datetime
import hashlib
import json
import os
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class ViolationType(Enum):
    """違反タイプの定義"""

    INSTRUCTION_IGNORED = "INSTRUCTION_IGNORED"  # 指示無視
    FALSE_COMPLETION = "FALSE_COMPLETION"  # 虚偽完了報告
    MEMORY_LOSS = "MEMORY_LOSS"  # 記憶喪失
    CONTEXT_SWITCH = "CONTEXT_SWITCH"  # 文脈切り替え
    ASSUMPTION_ERROR = "ASSUMPTION_ERROR"  # 思い込みエラー
    VERIFICATION_SKIP = "VERIFICATION_SKIP"  # 検証スキップ


@dataclass
class ViolationRecord:
    """違反記録"""

    timestamp: str
    violation_type: ViolationType
    description: str
    context: Dict[str, Any]
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    corrective_action: str


@dataclass
class SessionContext:
    """セッションコンテキスト"""

    session_id: str
    start_time: str
    user_instructions: List[str]
    critical_context: List[str]
    current_task: str
    completion_status: Dict[str, bool]
    violation_history: List[ViolationRecord]


class SessionContinuityEnforcer:
    """セッション継続性強制システム"""

    def __init__(self):
        self.base_path = Path("/Users/dd/Desktop/1_dev/coding-rule2")
        self.session_file = self.base_path / "runtime" / "session_continuity.json"
        self.violation_log = self.base_path / "runtime" / "violation_log.json"
        self.current_session = self._load_or_create_session()

    def _load_or_create_session(self) -> SessionContext:
        """セッション読み込みまたは作成"""
        if self.session_file.exists():
            with open(self.session_file, encoding="utf-8") as f:
                data = json.load(f)
                # Convert violation history
                violations = []
                for v in data.get("violation_history", []):
                    violations.append(
                        ViolationRecord(
                            timestamp=v["timestamp"],
                            violation_type=ViolationType(v["violation_type"]),
                            description=v["description"],
                            context=v["context"],
                            severity=v["severity"],
                            corrective_action=v["corrective_action"],
                        )
                    )
                data["violation_history"] = violations
                return SessionContext(**data)
        else:
            return SessionContext(
                session_id=self._generate_session_id(),
                start_time=datetime.datetime.now().isoformat(),
                user_instructions=[],
                critical_context=[],
                current_task="",
                completion_status={},
                violation_history=[],
            )

    def _generate_session_id(self) -> str:
        """セッションID生成"""
        timestamp = datetime.datetime.now().isoformat()
        return f"session_{hashlib.md5(timestamp.encode()).hexdigest()[:8]}"

    def _save_session(self):
        """セッション保存"""
        data = asdict(self.current_session)
        # Convert violation history for JSON serialization
        data["violation_history"] = [
            {**asdict(v), "violation_type": v.violation_type.value}
            for v in self.current_session.violation_history
        ]

        os.makedirs(self.session_file.parent, exist_ok=True)
        with open(self.session_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add_user_instruction(self, instruction: str):
        """ユーザー指示の追加"""
        self.current_session.user_instructions.append(instruction)
        self._save_session()

    def add_critical_context(self, context: str):
        """重要コンテキストの追加"""
        self.current_session.critical_context.append(context)
        self._save_session()

    def check_instruction_compliance(
        self, action: str, context: Dict[str, Any]
    ) -> Optional[ViolationRecord]:
        """指示遵守チェック"""
        # Check for specific violations based on recent incident
        if "真に新しいリポジトリ" in str(self.current_session.user_instructions):
            if "push" in action.lower() and "existing" in str(context).lower():
                return self._create_violation(
                    ViolationType.INSTRUCTION_IGNORED,
                    "User explicitly requested new repository but pushed to existing",
                    context,
                    "CRITICAL",
                )

        # Check for assumption errors
        if "gh" in action and not self._verify_tool_availability("gh"):
            return self._create_violation(
                ViolationType.ASSUMPTION_ERROR,
                "Assumed GitHub CLI availability without verification",
                context,
                "HIGH",
            )

        # Check for verification skips
        if any(keyword in action for keyword in ["create", "push", "commit"]):
            if not context.get("verified", False):
                return self._create_violation(
                    ViolationType.VERIFICATION_SKIP,
                    "Performed action without proper verification",
                    context,
                    "MEDIUM",
                )

        return None

    def _verify_tool_availability(self, tool: str) -> bool:
        """ツール利用可能性の検証"""
        # This should be implemented to actually check tool availability
        # For now, return False to enforce verification
        return False

    def _create_violation(
        self,
        violation_type: ViolationType,
        description: str,
        context: Dict[str, Any],
        severity: str,
    ) -> ViolationRecord:
        """違反記録の作成"""
        violation = ViolationRecord(
            timestamp=datetime.datetime.now().isoformat(),
            violation_type=violation_type,
            description=description,
            context=context,
            severity=severity,
            corrective_action=self._get_corrective_action(violation_type),
        )

        self.current_session.violation_history.append(violation)
        self._save_session()
        self._log_violation(violation)

        return violation

    def _get_corrective_action(self, violation_type: ViolationType) -> str:
        """違反タイプに応じた修正アクション"""
        actions = {
            ViolationType.INSTRUCTION_IGNORED: "Re-read user instructions and implement exactly as specified",
            ViolationType.FALSE_COMPLETION: "Verify completion with evidence before reporting",
            ViolationType.MEMORY_LOSS: "Load session context and review all previous instructions",
            ViolationType.CONTEXT_SWITCH: "Maintain focus on current task until completion",
            ViolationType.ASSUMPTION_ERROR: "Always verify assumptions before taking action",
            ViolationType.VERIFICATION_SKIP: "Implement verification step before any critical action",
        }
        return actions.get(violation_type, "Review and correct the violation")

    def _log_violation(self, violation: ViolationRecord):
        """違反のログ記録"""
        violations = []
        if self.violation_log.exists():
            with open(self.violation_log, encoding="utf-8") as f:
                violations = json.load(f)

        violations.append(
            {**asdict(violation), "violation_type": violation.violation_type.value}
        )

        with open(self.violation_log, "w", encoding="utf-8") as f:
            json.dump(violations, f, ensure_ascii=False, indent=2)

    def enforce_continuity(self) -> Dict[str, Any]:
        """セッション継続性の強制"""
        # Load current session state
        session_state = (
            self.base_path
            / "src"
            / "memory"
            / "core"
            / "session-records"
            / "current-session.json"
        )

        if not session_state.exists():
            return {
                "status": "ERROR",
                "message": "Session state file not found",
                "action": "Create session state immediately",
            }

        with open(session_state, encoding="utf-8") as f:
            current_state = json.load(f)

        # Check for continuity violations
        violations = []

        # Check mistake count consistency
        if current_state.get("mistakes_count", 0) != 88:
            violations.append(
                {
                    "type": "MEMORY_LOSS",
                    "detail": "Mistake count not preserved",
                    "expected": 88,
                    "actual": current_state.get("mistakes_count", 0),
                }
            )

        # Check AI organization integration
        if not current_state.get("ai_organization", {}).get("active_roles"):
            violations.append(
                {
                    "type": "CONTEXT_SWITCH",
                    "detail": "AI organization roles not active",
                    "expected": "Active roles",
                    "actual": "No roles",
                }
            )

        # Check memory inheritance
        if not current_state.get("memory_inheritance", {}).get("inherited_memories"):
            violations.append(
                {
                    "type": "MEMORY_LOSS",
                    "detail": "Memory inheritance not functioning",
                    "expected": "Inherited memories",
                    "actual": "No inheritance",
                }
            )

        return {
            "status": "ENFORCED" if not violations else "VIOLATIONS_DETECTED",
            "violations": violations,
            "session_context": self.current_session,
            "enforcement_actions": self._get_enforcement_actions(violations),
        }

    def _get_enforcement_actions(self, violations: List[Dict[str, Any]]) -> List[str]:
        """違反に対する強制アクション"""
        actions = []

        for violation in violations:
            if violation["type"] == "MEMORY_LOSS":
                actions.append("Reload session memory and restore context")
            elif violation["type"] == "CONTEXT_SWITCH":
                actions.append("Reactivate AI organization roles")
            elif violation["type"] == "INSTRUCTION_IGNORED":
                actions.append("Review and implement exact user instructions")

        return actions

    def get_session_summary(self) -> Dict[str, Any]:
        """セッションサマリーの取得"""
        return {
            "session_id": self.current_session.session_id,
            "duration": self._calculate_duration(),
            "instruction_count": len(self.current_session.user_instructions),
            "violation_count": len(self.current_session.violation_history),
            "violations_by_type": self._group_violations_by_type(),
            "critical_violations": [
                v
                for v in self.current_session.violation_history
                if v.severity == "CRITICAL"
            ],
            "current_task": self.current_session.current_task,
            "completion_status": self.current_session.completion_status,
        }

    def _calculate_duration(self) -> str:
        """セッション期間の計算"""
        start = datetime.datetime.fromisoformat(self.current_session.start_time)
        duration = datetime.datetime.now() - start
        return str(duration)

    def _group_violations_by_type(self) -> Dict[str, int]:
        """違反タイプ別グループ化"""
        groups = {}
        for violation in self.current_session.violation_history:
            vtype = violation.violation_type.value
            groups[vtype] = groups.get(vtype, 0) + 1
        return groups


def main():
    """メイン実行"""
    enforcer = SessionContinuityEnforcer()

    # Add the recent incident context
    enforcer.add_user_instruction("真に新しいリポジトリを作成")
    enforcer.add_critical_context(
        "User explicitly requested NEW repository, not existing"
    )

    # Check a simulated action
    violation = enforcer.check_instruction_compliance(
        "git push to existing repo", {"repo": "coding-rule2", "existing": True}
    )

    if violation:
        print(f"❌ VIOLATION DETECTED: {violation.violation_type.value}")
        print(f"   Description: {violation.description}")
        print(f"   Severity: {violation.severity}")
        print(f"   Corrective Action: {violation.corrective_action}")

    # Enforce continuity
    result = enforcer.enforce_continuity()
    print(f"\n📊 Session Continuity Status: {result['status']}")

    if result["violations"]:
        print("\n⚠️ Continuity Violations:")
        for v in result["violations"]:
            print(f"   - {v['type']}: {v['detail']}")

    # Get session summary
    summary = enforcer.get_session_summary()
    print("\n📈 Session Summary:")
    print(f"   Session ID: {summary['session_id']}")
    print(f"   Duration: {summary['duration']}")
    print(f"   Total Violations: {summary['violation_count']}")
    print(f"   Critical Violations: {len(summary['critical_violations'])}")


if __name__ == "__main__":
    main()
