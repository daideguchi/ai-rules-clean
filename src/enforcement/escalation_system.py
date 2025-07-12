#!/usr/bin/env python3
"""
📈 Dynamic Task Escalation System
================================

Handles automatic escalation and de-escalation of task levels based on:
- Context changes
- Failure patterns
- System state
- User behavior

Usage:
    from src.enforcement.escalation_system import EscalationSystem
    escalator = EscalationSystem()
    new_level = escalator.evaluate_escalation(current_level, context)
"""

import json
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.enforcement.task_classifier import TaskClassifier, TaskLevel  # noqa: E402


@dataclass
class EscalationTrigger:
    """Escalation trigger event"""

    trigger_type: str
    severity: float  # 0.0 to 1.0
    description: str
    timestamp: datetime
    context: Dict[str, Any]


@dataclass
class EscalationDecision:
    """Escalation decision result"""

    original_level: TaskLevel
    new_level: TaskLevel
    escalated: bool
    confidence: float
    triggers: List[EscalationTrigger]
    reasoning: List[str]


class EscalationSystem:
    """Dynamic task level escalation system"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.escalation_log = self.project_root / "runtime" / "escalation_log.json"
        self.classifier = TaskClassifier()

        # Escalation thresholds
        self.escalation_thresholds = {
            "failure_count": 3,  # Escalate after 3 failures
            "error_rate": 0.5,  # Escalate if >50% error rate
            "response_time": 30.0,  # Escalate if >30s response time
            "system_load": 0.8,  # Escalate if >80% system load
        }

        # Recent events tracking (in-memory)
        self.recent_events: List[Dict[str, Any]] = []
        self.max_events = 100

        # Initialize log
        self.escalation_log.parent.mkdir(parents=True, exist_ok=True)

    def evaluate_escalation(
        self, current_level: TaskLevel, context: Dict[str, Any]
    ) -> EscalationDecision:
        """
        Evaluate if task level should be escalated or de-escalated

        Args:
            current_level: Current task level
            context: Context including user input, system state, history

        Returns:
            EscalationDecision with new level and reasoning
        """

        triggers = []
        reasoning = []
        escalation_score = 0.0

        # Analyze failure patterns
        failure_triggers = self._analyze_failure_patterns(context)
        triggers.extend(failure_triggers)

        # Analyze system state
        system_triggers = self._analyze_system_state(context)
        triggers.extend(system_triggers)

        # Analyze user behavior
        user_triggers = self._analyze_user_behavior(context)
        triggers.extend(user_triggers)

        # Analyze temporal patterns
        temporal_triggers = self._analyze_temporal_patterns(context)
        triggers.extend(temporal_triggers)

        # Calculate escalation score
        for trigger in triggers:
            escalation_score += trigger.severity

        # Determine new level
        new_level = self._calculate_new_level(current_level, escalation_score, triggers)

        # Generate reasoning
        reasoning = self._generate_reasoning(current_level, new_level, triggers)

        # Calculate confidence
        confidence = min(1.0, escalation_score) if triggers else 0.5

        decision = EscalationDecision(
            original_level=current_level,
            new_level=new_level,
            escalated=(new_level.value != current_level.value),
            confidence=confidence,
            triggers=triggers,
            reasoning=reasoning,
        )

        # Log decision
        self._log_escalation_decision(decision, context)

        return decision

    def _analyze_failure_patterns(
        self, context: Dict[str, Any]
    ) -> List[EscalationTrigger]:
        """Analyze recent failure patterns for escalation triggers"""

        triggers = []

        # Check for repeated failures
        failure_count = context.get("recent_failures", 0)
        if failure_count >= self.escalation_thresholds["failure_count"]:
            triggers.append(
                EscalationTrigger(
                    trigger_type="repeated_failures",
                    severity=min(1.0, failure_count / 5.0),
                    description=f"{failure_count} recent failures detected",
                    timestamp=datetime.now(),
                    context={"failure_count": failure_count},
                )
            )

        # Check error rate
        error_rate = context.get("error_rate", 0.0)
        if error_rate > self.escalation_thresholds["error_rate"]:
            triggers.append(
                EscalationTrigger(
                    trigger_type="high_error_rate",
                    severity=error_rate,
                    description=f"High error rate: {error_rate:.1%}",
                    timestamp=datetime.now(),
                    context={"error_rate": error_rate},
                )
            )

        # Check for critical system components
        if context.get("affects_critical_systems", False):
            triggers.append(
                EscalationTrigger(
                    trigger_type="critical_system_impact",
                    severity=0.8,
                    description="Task affects critical system components",
                    timestamp=datetime.now(),
                    context={"critical_systems": True},
                )
            )

        return triggers

    def _analyze_system_state(self, context: Dict[str, Any]) -> List[EscalationTrigger]:
        """Analyze current system state for escalation triggers"""

        triggers = []

        # Check system load
        system_load = context.get("system_load", 0.0)
        if system_load > self.escalation_thresholds["system_load"]:
            triggers.append(
                EscalationTrigger(
                    trigger_type="high_system_load",
                    severity=system_load,
                    description=f"High system load: {system_load:.1%}",
                    timestamp=datetime.now(),
                    context={"system_load": system_load},
                )
            )

        # Check if PRESIDENT declaration is expired/missing
        president_status = context.get("president_valid", True)
        if not president_status:
            triggers.append(
                EscalationTrigger(
                    trigger_type="president_declaration_invalid",
                    severity=0.9,
                    description="PRESIDENT declaration invalid or expired",
                    timestamp=datetime.now(),
                    context={"president_valid": False},
                )
            )

        # Check database connectivity
        db_status = context.get("database_connectivity", True)
        if not db_status:
            triggers.append(
                EscalationTrigger(
                    trigger_type="database_connectivity_issue",
                    severity=0.7,
                    description="Database connectivity issues detected",
                    timestamp=datetime.now(),
                    context={"database_connectivity": False},
                )
            )

        return triggers

    def _analyze_user_behavior(
        self, context: Dict[str, Any]
    ) -> List[EscalationTrigger]:
        """Analyze user behavior patterns for escalation triggers"""

        triggers = []

        # Check for urgency indicators in user input
        user_input = context.get("user_input", "").lower()
        urgency_keywords = [
            "urgent",
            "emergency",
            "critical",
            "asap",
            "immediately",
            "緊急",
            "すぐに",
        ]

        for keyword in urgency_keywords:
            if keyword in user_input:
                triggers.append(
                    EscalationTrigger(
                        trigger_type="user_urgency_indicator",
                        severity=0.6,
                        description=f"User urgency keyword detected: {keyword}",
                        timestamp=datetime.now(),
                        context={"urgency_keyword": keyword},
                    )
                )
                break  # Only trigger once per urgency detection

        # Check for user frustration indicators
        frustration_indicators = [
            "why",
            "how many times",
            "again",
            "still",
            "何回",
            "まだ",
        ]
        for indicator in frustration_indicators:
            if indicator in user_input:
                triggers.append(
                    EscalationTrigger(
                        trigger_type="user_frustration",
                        severity=0.4,
                        description=f"User frustration indicator: {indicator}",
                        timestamp=datetime.now(),
                        context={"frustration_indicator": indicator},
                    )
                )
                break

        # Check for repeated requests
        request_count = context.get("repeated_request_count", 0)
        if request_count > 2:
            triggers.append(
                EscalationTrigger(
                    trigger_type="repeated_request",
                    severity=min(1.0, request_count / 5.0),
                    description=f"Request repeated {request_count} times",
                    timestamp=datetime.now(),
                    context={"request_count": request_count},
                )
            )

        return triggers

    def _analyze_temporal_patterns(
        self, context: Dict[str, Any]
    ) -> List[EscalationTrigger]:
        """Analyze temporal patterns for escalation triggers"""

        triggers = []

        # Check response time
        response_time = context.get("response_time", 0.0)
        if response_time > self.escalation_thresholds["response_time"]:
            triggers.append(
                EscalationTrigger(
                    trigger_type="slow_response_time",
                    severity=min(1.0, response_time / 60.0),
                    description=f"Slow response time: {response_time:.1f}s",
                    timestamp=datetime.now(),
                    context={"response_time": response_time},
                )
            )

        # Check if during business hours (higher priority)
        current_hour = datetime.now().hour
        if 9 <= current_hour <= 17:  # Business hours
            triggers.append(
                EscalationTrigger(
                    trigger_type="business_hours",
                    severity=0.2,
                    description="Task during business hours",
                    timestamp=datetime.now(),
                    context={"business_hours": True},
                )
            )

        return triggers

    def _calculate_new_level(
        self,
        current_level: TaskLevel,
        escalation_score: float,
        triggers: List[EscalationTrigger],
    ) -> TaskLevel:
        """Calculate new task level based on escalation score and triggers"""

        # Define escalation matrix
        escalation_matrix = {
            TaskLevel.LOW: {
                0.3: TaskLevel.MEDIUM,
                0.7: TaskLevel.HIGH,
                1.0: TaskLevel.CRITICAL,
            },
            TaskLevel.MEDIUM: {0.5: TaskLevel.HIGH, 0.8: TaskLevel.CRITICAL},
            TaskLevel.HIGH: {0.6: TaskLevel.CRITICAL},
            TaskLevel.CRITICAL: {},  # Already at max level
        }

        # Check for specific trigger types that force escalation
        critical_triggers = ["president_declaration_invalid", "critical_system_impact"]
        for trigger in triggers:
            if trigger.trigger_type in critical_triggers:
                return TaskLevel.CRITICAL

        # Apply escalation matrix
        if current_level in escalation_matrix:
            thresholds = escalation_matrix[current_level]
            for threshold, new_level in sorted(thresholds.items()):
                if escalation_score >= threshold:
                    return new_level

        # No escalation needed
        return current_level

    def _generate_reasoning(
        self,
        original_level: TaskLevel,
        new_level: TaskLevel,
        triggers: List[EscalationTrigger],
    ) -> List[str]:
        """Generate human-readable reasoning for escalation decision"""

        reasoning = []

        if new_level != original_level:
            reasoning.append(
                f"Escalated from {original_level.value} to {new_level.value}"
            )

            # Group triggers by type
            trigger_summary = {}
            for trigger in triggers:
                if trigger.trigger_type not in trigger_summary:
                    trigger_summary[trigger.trigger_type] = []
                trigger_summary[trigger.trigger_type].append(trigger)

            # Add reasoning for each trigger type
            for trigger_type, trigger_list in trigger_summary.items():
                if len(trigger_list) == 1:
                    reasoning.append(trigger_list[0].description)
                else:
                    reasoning.append(
                        f"{len(trigger_list)} {trigger_type} triggers detected"
                    )
        else:
            reasoning.append(
                f"No escalation needed - maintaining {original_level.value} level"
            )

        return reasoning

    def _log_escalation_decision(
        self, decision: EscalationDecision, context: Dict[str, Any]
    ):
        """Log escalation decision for monitoring and analysis"""

        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "original_level": decision.original_level.value,
                "new_level": decision.new_level.value,
                "escalated": decision.escalated,
                "confidence": decision.confidence,
                "trigger_count": len(decision.triggers),
                "triggers": [
                    {
                        "type": t.trigger_type,
                        "severity": t.severity,
                        "description": t.description,
                    }
                    for t in decision.triggers
                ],
                "reasoning": decision.reasoning,
                "context_keys": list(context.keys()),
            }

            # Load existing log
            if self.escalation_log.exists():
                with open(self.escalation_log) as f:
                    log_data = json.load(f)
            else:
                log_data = {"escalation_decisions": []}

            # Add new entry
            log_data["escalation_decisions"].append(log_entry)

            # Keep only recent entries (last 1000)
            if len(log_data["escalation_decisions"]) > 1000:
                log_data["escalation_decisions"] = log_data["escalation_decisions"][
                    -1000:
                ]

            # Save log
            with open(self.escalation_log, "w") as f:
                json.dump(log_data, f, indent=2)

        except Exception:
            # Logging failure is non-critical
            pass


def main():
    """Test escalation system"""

    print("📈 Dynamic Task Escalation System Test")
    print("=" * 45)

    escalator = EscalationSystem()

    test_scenarios = [
        {
            "name": "Normal operation",
            "level": TaskLevel.MEDIUM,
            "context": {"user_input": "Create a simple function"},
        },
        {
            "name": "User urgency",
            "level": TaskLevel.MEDIUM,
            "context": {"user_input": "URGENT: Fix this immediately!"},
        },
        {
            "name": "System failures",
            "level": TaskLevel.HIGH,
            "context": {
                "user_input": "Fix the database",
                "recent_failures": 4,
                "error_rate": 0.7,
            },
        },
        {
            "name": "Critical system impact",
            "level": TaskLevel.HIGH,
            "context": {
                "user_input": "Update security system",
                "affects_critical_systems": True,
                "president_valid": False,
            },
        },
        {
            "name": "Repeated request",
            "level": TaskLevel.LOW,
            "context": {
                "user_input": "Why isn't this working again?",
                "repeated_request_count": 3,
            },
        },
    ]

    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n🧪 Scenario {i}: {scenario['name']}")
        print(f"   Original Level: {scenario['level'].value}")

        decision = escalator.evaluate_escalation(scenario["level"], scenario["context"])

        print(f"   New Level: {decision.new_level.value}")
        print(f"   Escalated: {'✅ YES' if decision.escalated else '❌ NO'}")
        print(f"   Confidence: {decision.confidence:.1%}")

        if decision.triggers:
            print(f"   Triggers: {len(decision.triggers)}")
            for trigger in decision.triggers[:2]:  # Show first 2 triggers
                print(f"     • {trigger.description}")

        if decision.reasoning:
            print(f"   Reasoning: {decision.reasoning[0]}")


if __name__ == "__main__":
    main()
