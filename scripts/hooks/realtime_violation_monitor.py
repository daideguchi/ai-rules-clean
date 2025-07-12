#!/usr/bin/env python3
"""
Real-time Violation Monitor Hook
リアルタイムで違反を検出し、88回ミス防止システムと連携
"""

import datetime
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List


class RealtimeViolationMonitor:
    """リアルタイム違反監視フック"""

    def __init__(self):
        self.base_path = Path("/Users/dd/Desktop/1_dev/coding-rule2")
        self.monitoring_log = self.base_path / "runtime" / "realtime_monitoring.json"
        self.ai_systems = {
            "constitutional_ai": self.base_path / "src" / "ai" / "constitutional_ai.py",
            "rule_based_rewards": self.base_path
            / "src"
            / "ai"
            / "rule_based_rewards.py",
            "multi_agent_monitor": self.base_path
            / "src"
            / "ai"
            / "multi_agent_monitor.py",
            "session_enforcer": self.base_path
            / "src"
            / "ai"
            / "session_continuity_enforcer.py",
        }
        self.violation_patterns = self._load_violation_patterns()

    def _load_violation_patterns(self) -> List[Dict[str, Any]]:
        """違反パターンの読み込み"""
        patterns_file = (
            self.base_path
            / "runtime"
            / "continuous_improvement"
            / "learning_patterns.json"
        )
        if patterns_file.exists():
            with open(patterns_file, encoding="utf-8") as f:
                patterns = json.load(f)
                # Filter for violation patterns
                return [p for p in patterns if p.get("occurrence_count", 0) >= 88]
        return []

    def monitor_action(
        self, action_type: str, action_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """アクションの監視"""
        timestamp = datetime.datetime.now().isoformat()

        # Check for known violation patterns
        violations = []

        # Pattern 1: Tool availability assumption
        if self._check_tool_assumption(action_type, action_data):
            violations.append(
                {
                    "type": "ASSUMPTION_ERROR",
                    "severity": "HIGH",
                    "pattern": "Tool availability not verified",
                    "action": action_type,
                    "details": f"Assumed {action_data.get('tool', 'unknown')} availability",
                }
            )

        # Pattern 2: Instruction compliance
        if self._check_instruction_violation(action_type, action_data):
            violations.append(
                {
                    "type": "INSTRUCTION_IGNORED",
                    "severity": "CRITICAL",
                    "pattern": "User instruction violated",
                    "action": action_type,
                    "details": "Action contradicts explicit user instruction",
                }
            )

        # Pattern 3: Verification skip
        if self._check_verification_skip(action_type, action_data):
            violations.append(
                {
                    "type": "VERIFICATION_SKIP",
                    "severity": "MEDIUM",
                    "pattern": "Action without verification",
                    "action": action_type,
                    "details": "Critical action performed without verification",
                }
            )

        # If violations detected, trigger AI safety systems
        if violations:
            self._trigger_safety_systems(violations)
            self._log_violations(timestamp, violations)

            return {
                "status": "VIOLATIONS_DETECTED",
                "violations": violations,
                "corrective_actions": self._get_corrective_actions(violations),
                "safety_systems_triggered": True,
            }

        return {
            "status": "MONITORED",
            "action": action_type,
            "timestamp": timestamp,
            "safety_check": "PASSED",
        }

    def _check_tool_assumption(
        self, action_type: str, action_data: Dict[str, Any]
    ) -> bool:
        """ツール利用可能性の思い込みチェック"""
        tool_actions = ["gh", "git", "npm", "python", "make"]

        for tool in tool_actions:
            if tool in action_type.lower() or tool in str(action_data).lower():
                # Check if tool was verified
                if not action_data.get(f"{tool}_verified", False):
                    return True
        return False

    def _check_instruction_violation(
        self, action_type: str, action_data: Dict[str, Any]
    ) -> bool:
        """指示違反チェック"""
        # Load current user instructions
        session_file = self.base_path / "runtime" / "session_continuity.json"
        if session_file.exists():
            with open(session_file, encoding="utf-8") as f:
                session = json.load(f)

            instructions = session.get("user_instructions", [])

            # Check for specific violation patterns
            for instruction in instructions:
                if "新しいリポジトリ" in instruction and "push" in action_type:
                    if "existing" in str(action_data) or "coding-rule2" in str(
                        action_data
                    ):
                        return True

                if "削除禁止" in instruction and (
                    "delete" in action_type or "remove" in action_type
                ):
                    return True

        return False

    def _check_verification_skip(
        self, action_type: str, action_data: Dict[str, Any]
    ) -> bool:
        """検証スキップチェック"""
        critical_actions = ["push", "commit", "delete", "create", "deploy", "merge"]

        for critical in critical_actions:
            if critical in action_type.lower():
                if not action_data.get("verified", False):
                    return True
        return False

    def _trigger_safety_systems(self, violations: List[Dict[str, Any]]):
        """AI安全システムのトリガー"""
        # Trigger Constitutional AI for critical violations
        critical_violations = [v for v in violations if v["severity"] == "CRITICAL"]
        if critical_violations:
            self._run_safety_system(
                "constitutional_ai", {"violations": critical_violations}
            )

        # Trigger Rule-Based Rewards for behavioral corrections
        self._run_safety_system("rule_based_rewards", {"violations": violations})

        # Trigger Multi-Agent Monitor for cross-verification
        if len(violations) > 1:
            self._run_safety_system("multi_agent_monitor", {"violations": violations})

    def _run_safety_system(self, system_name: str, context: Dict[str, Any]):
        """安全システムの実行"""
        system_path = self.ai_systems.get(system_name)
        if system_path and system_path.exists():
            try:
                # Prepare context for the system
                context_file = (
                    self.base_path / "runtime" / f"{system_name}_context.json"
                )
                with open(context_file, "w", encoding="utf-8") as f:
                    json.dump(context, f, ensure_ascii=False, indent=2)

                # Run the safety system
                result = subprocess.run(
                    [
                        sys.executable,
                        str(system_path),
                        "--monitor-mode",
                        str(context_file),
                    ],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                if result.returncode != 0:
                    print(
                        f"⚠️ Safety system {system_name} reported issues: {result.stderr}"
                    )

            except Exception as e:
                print(f"❌ Failed to run safety system {system_name}: {e}")

    def _log_violations(self, timestamp: str, violations: List[Dict[str, Any]]):
        """違反のログ記録"""
        log_entry = {
            "timestamp": timestamp,
            "violations": violations,
            "session_context": self._get_session_context(),
        }

        # Load existing log
        logs = []
        if self.monitoring_log.exists():
            with open(self.monitoring_log, encoding="utf-8") as f:
                logs = json.load(f)

        logs.append(log_entry)

        # Keep only recent logs (last 1000 entries)
        if len(logs) > 1000:
            logs = logs[-1000:]

        # Save updated log
        os.makedirs(self.monitoring_log.parent, exist_ok=True)
        with open(self.monitoring_log, "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)

    def _get_session_context(self) -> Dict[str, Any]:
        """セッションコンテキストの取得"""
        session_file = (
            self.base_path
            / "src"
            / "memory"
            / "core"
            / "session-records"
            / "current-session.json"
        )
        if session_file.exists():
            with open(session_file, encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _get_corrective_actions(self, violations: List[Dict[str, Any]]) -> List[str]:
        """修正アクションの取得"""
        actions = []

        for violation in violations:
            if violation["type"] == "ASSUMPTION_ERROR":
                actions.append(f"Verify {violation['details']} before proceeding")
            elif violation["type"] == "INSTRUCTION_IGNORED":
                actions.append("Review user instructions and correct the action")
            elif violation["type"] == "VERIFICATION_SKIP":
                actions.append("Add verification step before executing critical action")

        return actions

    def get_monitoring_summary(self) -> Dict[str, Any]:
        """監視サマリーの取得"""
        if not self.monitoring_log.exists():
            return {"status": "NO_DATA", "message": "No monitoring data available"}

        with open(self.monitoring_log, encoding="utf-8") as f:
            logs = json.load(f)

        # Analyze recent violations
        recent_logs = logs[-100:] if len(logs) > 100 else logs

        violation_counts = {}
        severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}

        for log in recent_logs:
            for violation in log.get("violations", []):
                vtype = violation.get("type", "UNKNOWN")
                violation_counts[vtype] = violation_counts.get(vtype, 0) + 1

                severity = violation.get("severity", "LOW")
                severity_counts[severity] = severity_counts.get(severity, 0) + 1

        return {
            "total_logs": len(logs),
            "recent_violations": len(recent_logs),
            "violation_types": violation_counts,
            "severity_distribution": severity_counts,
            "most_common_violation": max(violation_counts.items(), key=lambda x: x[1])[
                0
            ]
            if violation_counts
            else None,
            "critical_violations_count": severity_counts["CRITICAL"],
        }


def hook_function(action_type: str, action_data: Dict[str, Any]) -> Dict[str, Any]:
    """フック関数（他のシステムから呼び出される）"""
    monitor = RealtimeViolationMonitor()
    return monitor.monitor_action(action_type, action_data)


def main():
    """メイン実行（テスト用）"""
    monitor = RealtimeViolationMonitor()

    # Test various scenarios
    print("🔍 Testing Real-time Violation Monitor")
    print("=" * 50)

    # Test 1: Tool assumption
    result1 = monitor.monitor_action(
        "gh_create_repo", {"tool": "gh", "repo": "new-repo"}
    )
    print(f"\nTest 1 - Tool Assumption: {result1['status']}")

    # Test 2: Instruction violation
    result2 = monitor.monitor_action(
        "git_push", {"repo": "coding-rule2", "existing": True}
    )
    print(f"\nTest 2 - Instruction Violation: {result2['status']}")

    # Test 3: Verification skip
    result3 = monitor.monitor_action(
        "deploy", {"target": "production", "verified": False}
    )
    print(f"\nTest 3 - Verification Skip: {result3['status']}")

    # Get monitoring summary
    summary = monitor.get_monitoring_summary()
    print("\n📊 Monitoring Summary:")
    print(f"   Total Logs: {summary.get('total_logs', 0)}")
    print(f"   Critical Violations: {summary.get('critical_violations_count', 0)}")
    print(f"   Most Common Violation: {summary.get('most_common_violation', 'None')}")


if __name__ == "__main__":
    main()
