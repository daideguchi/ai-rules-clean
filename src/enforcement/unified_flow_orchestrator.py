#!/usr/bin/env python3
"""
🎼 Unified Flow Orchestrator
===========================

Main orchestrator that integrates all enforcement systems:
1. Automatic task classification
2. Lightweight PRESIDENT validation
3. Dynamic escalation evaluation
4. Reference Monitor enforcement
5. Unified response handling

Usage:
    from src.enforcement.unified_flow_orchestrator import UnifiedFlowOrchestrator
    orchestrator = UnifiedFlowOrchestrator()
    result = await orchestrator.process_request(user_input, context)
"""

import asyncio
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.enforcement.escalation_system import EscalationDecision, EscalationSystem
    from src.enforcement.lightweight_president import LightweightPresident
    from src.enforcement.reference_monitor import (
        EnforcementDecision,
        PolicyVerdict,
        ReferenceMonitor,
    )
    from src.enforcement.task_classifier import (
        ClassificationResult,
        TaskClassifier,
        TaskLevel,
    )
except ImportError:
    # Fallback import for development
    import os

    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from src.enforcement.escalation_system import EscalationDecision, EscalationSystem
    from src.enforcement.lightweight_president import LightweightPresident
    from src.enforcement.reference_monitor import (
        EnforcementDecision,
        PolicyVerdict,
        ReferenceMonitor,
    )
    from src.enforcement.task_classifier import (
        ClassificationResult,
        TaskClassifier,
        TaskLevel,
    )


@dataclass
class ProcessingResult:
    """Complete processing result from unified flow"""

    user_input: str
    initial_classification: ClassificationResult
    president_status: bool
    escalation_decision: EscalationDecision
    final_task_level: TaskLevel
    enforcement_decision: EnforcementDecision
    allowed: bool
    response: str
    processing_time_ms: float
    flow_steps: List[str]


class UnifiedFlowOrchestrator:
    """Main orchestrator for unified enforcement flow"""

    def __init__(self):
        # Initialize all subsystems
        self.task_classifier = TaskClassifier()
        self.president_validator = LightweightPresident()
        self.escalation_system = EscalationSystem()
        self.reference_monitor = ReferenceMonitor()

        # Flow configuration
        self.enable_escalation = True
        self.enable_president_validation = True
        self.enable_reference_monitor = True

        # Performance tracking
        self.processing_stats = {
            "total_requests": 0,
            "avg_processing_time": 0.0,
            "classification_time": 0.0,
            "president_check_time": 0.0,
            "escalation_time": 0.0,
            "enforcement_time": 0.0,
        }

    async def process_request(
        self, user_input: str, context: Optional[Dict[str, Any]] = None
    ) -> ProcessingResult:
        """
        Process user request through complete enforcement flow

        Args:
            user_input: User's request/query
            context: Additional context (session info, system state, etc.)

        Returns:
            ProcessingResult with complete enforcement decision
        """

        start_time = time.time()
        flow_steps = []

        if context is None:
            context = {}

        # Add user input to context for escalation analysis
        context["user_input"] = user_input

        try:
            # Step 1: Automatic Task Classification
            step_start = time.time()
            classification_result = self.task_classifier.classify_task(
                user_input, context
            )
            classification_time = (time.time() - step_start) * 1000
            flow_steps.append(
                f"Classification: {classification_result.level.value} ({classification_time:.1f}ms)"
            )

            # Step 2: Lightweight PRESIDENT Validation (for CRITICAL tasks)
            step_start = time.time()
            president_valid = True
            if classification_result.level == TaskLevel.CRITICAL:
                president_valid = self.president_validator.quick_check()
                if not president_valid:
                    flow_steps.append("PRESIDENT: ❌ INVALID - Blocking CRITICAL task")
                    # Early return for invalid PRESIDENT
                    return self._create_president_blocked_result(
                        user_input,
                        classification_result,
                        context,
                        flow_steps,
                        start_time,
                    )
                else:
                    flow_steps.append("PRESIDENT: ✅ VALID")
            else:
                flow_steps.append(
                    f"PRESIDENT: ⚪ SKIPPED ({classification_result.level.value} task)"
                )

            president_time = (time.time() - step_start) * 1000

            # Step 3: Dynamic Escalation Evaluation
            step_start = time.time()
            context["president_valid"] = president_valid
            escalation_decision = self.escalation_system.evaluate_escalation(
                classification_result.level, context
            )
            escalation_time = (time.time() - step_start) * 1000

            if escalation_decision.escalated:
                flow_steps.append(
                    f"Escalation: {classification_result.level.value} → {escalation_decision.new_level.value}"
                )
            else:
                flow_steps.append(
                    f"Escalation: No change ({escalation_decision.new_level.value})"
                )

            final_task_level = escalation_decision.new_level

            # Step 4: Reference Monitor Enforcement
            step_start = time.time()

            # Tokenize user input for enforcement
            tokens = user_input.split()
            enforcement_decision = await self.reference_monitor.enforce_token_sequence(
                tokens, final_task_level.value
            )
            enforcement_time = (time.time() - step_start) * 1000

            # Determine final response
            if enforcement_decision.verdict == PolicyVerdict.ALLOW:
                allowed = True
                response = user_input
                flow_steps.append(
                    f"Enforcement: ✅ ALLOWED (score: {enforcement_decision.constitutional_ai_score:.2f})"
                )
            elif enforcement_decision.verdict == PolicyVerdict.TRANSFORM:
                allowed = True
                response = " ".join(enforcement_decision.allowed_tokens)
                flow_steps.append(
                    f"Enforcement: 🔄 TRANSFORMED (score: {enforcement_decision.constitutional_ai_score:.2f})"
                )
            else:  # DENY
                allowed = False
                response = f"Request denied: Policy violation (Constitutional AI score: {enforcement_decision.constitutional_ai_score:.2f})"
                flow_steps.append(
                    f"Enforcement: ❌ DENIED (score: {enforcement_decision.constitutional_ai_score:.2f})"
                )

            # Calculate total processing time
            total_time = (time.time() - start_time) * 1000

            # Update statistics
            self._update_processing_stats(
                total_time,
                classification_time,
                president_time,
                escalation_time,
                enforcement_time,
            )

            # Create complete result
            result = ProcessingResult(
                user_input=user_input,
                initial_classification=classification_result,
                president_status=president_valid,
                escalation_decision=escalation_decision,
                final_task_level=final_task_level,
                enforcement_decision=enforcement_decision,
                allowed=allowed,
                response=response,
                processing_time_ms=total_time,
                flow_steps=flow_steps,
            )

            return result

        except Exception as e:
            # Fail securely - deny on error
            error_time = (time.time() - start_time) * 1000
            flow_steps.append(f"ERROR: {str(e)}")

            return ProcessingResult(
                user_input=user_input,
                initial_classification=ClassificationResult(
                    TaskLevel.LOW, 0.0, ["Error occurred"], [], []
                ),
                president_status=False,
                escalation_decision=EscalationDecision(
                    TaskLevel.LOW, TaskLevel.LOW, False, 0.0, [], ["Error"]
                ),
                final_task_level=TaskLevel.LOW,
                enforcement_decision=EnforcementDecision(
                    PolicyVerdict.DENY, [], [], 0.0, "", "", "", ""
                ),
                allowed=False,
                response=f"Processing error: {str(e)}",
                processing_time_ms=error_time,
                flow_steps=flow_steps,
            )

    def _create_president_blocked_result(
        self,
        user_input: str,
        classification: ClassificationResult,
        context: Dict[str, Any],
        flow_steps: List[str],
        start_time: float,
    ) -> ProcessingResult:
        """Create result for PRESIDENT declaration blocked request"""

        # Create minimal escalation decision (no escalation performed)
        escalation_decision = EscalationDecision(
            original_level=classification.level,
            new_level=classification.level,
            escalated=False,
            confidence=1.0,
            triggers=[],
            reasoning=["PRESIDENT declaration invalid - blocking CRITICAL task"],
        )

        # Create denial enforcement decision
        enforcement_decision = EnforcementDecision(
            verdict=PolicyVerdict.DENY,
            original_tokens=user_input.split(),
            allowed_tokens=[],
            constitutional_ai_score=0.0,
            reasoning_trace_id="president_blocked",
            cryptographic_proof="N/A",
            timestamp=datetime.now().isoformat(),
            policy_version="2.0",
        )

        processing_time = (time.time() - start_time) * 1000

        return ProcessingResult(
            user_input=user_input,
            initial_classification=classification,
            president_status=False,
            escalation_decision=escalation_decision,
            final_task_level=classification.level,
            enforcement_decision=enforcement_decision,
            allowed=False,
            response="CRITICAL task blocked: PRESIDENT declaration required. Execute: make declare-president",
            processing_time_ms=processing_time,
            flow_steps=flow_steps,
        )

    def _update_processing_stats(
        self,
        total_time: float,
        classification_time: float,
        president_time: float,
        escalation_time: float,
        enforcement_time: float,
    ):
        """Update performance statistics"""

        self.processing_stats["total_requests"] += 1

        # Running average calculation
        n = self.processing_stats["total_requests"]

        self.processing_stats["avg_processing_time"] = (
            self.processing_stats["avg_processing_time"] * (n - 1) + total_time
        ) / n
        self.processing_stats["classification_time"] = (
            self.processing_stats["classification_time"] * (n - 1) + classification_time
        ) / n
        self.processing_stats["president_check_time"] = (
            self.processing_stats["president_check_time"] * (n - 1) + president_time
        ) / n
        self.processing_stats["escalation_time"] = (
            self.processing_stats["escalation_time"] * (n - 1) + escalation_time
        ) / n
        self.processing_stats["enforcement_time"] = (
            self.processing_stats["enforcement_time"] * (n - 1) + enforcement_time
        ) / n

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        return {
            **self.processing_stats,
            "subsystem_health": {
                "task_classifier": "operational",
                "president_validator": "operational"
                if self.president_validator.quick_check()
                else "degraded",
                "escalation_system": "operational",
                "reference_monitor": "operational",
            },
        }

    def explain_decision(self, result: ProcessingResult) -> str:
        """Generate human-readable explanation of processing decision"""

        explanation = "🎼 Unified Flow Processing Result\n"
        explanation += f"{'=' * 40}\n\n"

        explanation += f"📝 Input: {result.user_input}\n"
        explanation += f"⏱️  Processing Time: {result.processing_time_ms:.1f}ms\n"
        explanation += (
            f"🎯 Final Decision: {'✅ ALLOWED' if result.allowed else '❌ DENIED'}\n\n"
        )

        explanation += "📊 Classification:\n"
        explanation += (
            f"   Initial Level: {result.initial_classification.level.value}\n"
        )
        explanation += (
            f"   Confidence: {result.initial_classification.confidence:.1%}\n"
        )
        explanation += f"   Final Level: {result.final_task_level.value}\n\n"

        if result.escalation_decision.escalated:
            explanation += f"📈 Escalation: {result.initial_classification.level.value} → {result.final_task_level.value}\n"
            explanation += f"   Triggers: {len(result.escalation_decision.triggers)}\n"
            for trigger in result.escalation_decision.triggers[:3]:
                explanation += f"   • {trigger.description}\n"
            explanation += "\n"

        explanation += "🔒 Enforcement:\n"
        explanation += (
            f"   Verdict: {result.enforcement_decision.verdict.value.upper()}\n"
        )
        explanation += f"   Constitutional Score: {result.enforcement_decision.constitutional_ai_score:.2f}\n\n"

        explanation += "🔄 Flow Steps:\n"
        for step in result.flow_steps:
            explanation += f"   • {step}\n"

        return explanation


async def main():
    """Test unified flow orchestrator"""

    print("🎼 Unified Flow Orchestrator Test")
    print("=" * 45)

    orchestrator = UnifiedFlowOrchestrator()

    test_cases = [
        {"input": "What is the current status?", "context": {}},
        {"input": "Implement new security system", "context": {}},
        {
            "input": "URGENT: System is failing in production!",
            "context": {"recent_failures": 3, "error_rate": 0.8},
        },
        {
            "input": "<thinking>Need to analyze this critical issue</thinking>Fix the constitutional AI",
            "context": {"affects_critical_systems": True},
        },
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test Case {i}: {test_case['input'][:50]}...")

        result = await orchestrator.process_request(
            test_case["input"], test_case["context"]
        )

        print(f"   🎯 Decision: {'✅ ALLOWED' if result.allowed else '❌ DENIED'}")
        print(
            f"   📊 Level: {result.initial_classification.level.value} → {result.final_task_level.value}"
        )
        print(f"   ⏱️  Time: {result.processing_time_ms:.1f}ms")
        print(f"   🔒 Score: {result.enforcement_decision.constitutional_ai_score:.2f}")

        # Show key flow steps
        key_steps = [
            step
            for step in result.flow_steps
            if any(
                keyword in step
                for keyword in ["Classification", "Enforcement", "PRESIDENT"]
            )
        ]
        for step in key_steps[:2]:
            print(f"   • {step}")

    print("\n📈 Performance Stats:")
    stats = orchestrator.get_performance_stats()
    print(f"   Average Processing Time: {stats['avg_processing_time']:.1f}ms")
    print(f"   Total Requests: {stats['total_requests']}")


if __name__ == "__main__":
    asyncio.run(main())
