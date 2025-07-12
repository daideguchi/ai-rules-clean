#!/usr/bin/env python3
"""
🎼 Mandatory Processing Flow Enforcer
===================================

ENFORCES the correct processing flow for EVERY interaction:
1. 指示 (Instruction received)
2. プレジデント確認 (PRESIDENT confirmation)
3. タスクレベル判定 (Task level determination)
4. タスクに合わせてプレジデントとして処理 (Presidential processing)

This flow is MANDATORY and CANNOT be bypassed.
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.enforcement.functional_president import (
        FunctionalPresident,
        PresidentialDecision,
        ProcessingMode,
    )
except ImportError:
    # Fallback import for development
    import os

    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from src.enforcement.functional_president import (
        FunctionalPresident,
        PresidentialDecision,
        ProcessingMode,
    )


class MandatoryFlowEnforcer:
    """
    Enforces the mandatory processing flow for every interaction.
    NO BYPASSING ALLOWED.
    """

    def __init__(self):
        self.functional_president = FunctionalPresident()
        self.flow_violations = []
        self.successful_flows = 0

    def process_instruction(
        self, user_instruction: str, context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Process instruction through MANDATORY flow.
        Returns complete processing decision or blocks execution.
        """

        print("🎼 MANDATORY PROCESSING FLOW ENFORCEMENT")
        print("=" * 50)
        print(f"📝 User Instruction: '{user_instruction}'")
        print(f"⏰ Flow Start: {datetime.now().isoformat()}")
        print()

        # STEP 1: 指示 (Instruction received) ✅
        print("📨 STEP 1: 指示 (Instruction Received)")
        print("   ✅ User instruction captured")
        print()

        # STEP 2: プレジデント確認 (PRESIDENT confirmation)
        print("👑 STEP 2: プレジデント確認 (PRESIDENT Confirmation)")
        president_status = self._enforce_president_confirmation()
        if not president_status["valid"]:
            return self._block_execution(
                "PRESIDENT confirmation failed", user_instruction
            )
        print("   ✅ PRESIDENT authority confirmed")
        print()

        # STEP 3: タスクレベル判定 (Task level determination)
        print("🎯 STEP 3: タスクレベル判定 (Task Level Determination)")
        presidential_decision = self._enforce_task_level_determination(
            user_instruction, context
        )
        print(f"   ✅ Task classified as: {presidential_decision.task_level.value}")
        print(f"   ✅ Mode determined: {presidential_decision.required_mode.value}")
        print()

        # STEP 4: タスクに合わせてプレジデントとして処理 (Presidential processing)
        print(
            "⚡ STEP 4: タスクに合わせてプレジデントとして処理 (Presidential Processing)"
        )
        execution_plan = self._enforce_presidential_processing(presidential_decision)
        print("   ✅ Presidential processing plan established")
        print()

        # FLOW COMPLETION
        self.successful_flows += 1

        result = {
            "flow_status": "COMPLETED",
            "user_instruction": user_instruction,
            "president_confirmed": True,
            "task_level": presidential_decision.task_level.value,
            "required_mode": presidential_decision.required_mode.value,
            "organization_roles": presidential_decision.organization_roles,
            "quality_checkpoints": presidential_decision.quality_checkpoints,
            "execution_authority": presidential_decision.execution_authority,
            "execution_plan": execution_plan,
            "flow_completed_at": datetime.now().isoformat(),
            "flow_id": f"flow-{self.successful_flows:04d}",
        }

        print("🎉 MANDATORY FLOW SUCCESSFULLY COMPLETED")
        print(f"📊 Flow ID: {result['flow_id']}")
        print(f"🎯 Task Level: {result['task_level']}")
        print(f"🔄 Required Mode: {result['required_mode']}")
        print(f"🏢 Organization: {len(result['organization_roles'])} roles deployed")
        print()

        return result

    def _enforce_president_confirmation(self) -> Dict[str, Any]:
        """Enforce PRESIDENT confirmation step"""

        # Try to assume presidential authority
        try:
            authority_report = self.functional_president.assume_presidential_authority()
            return {
                "valid": True,
                "authority_assumed": True,
                "session_id": authority_report["session_id"],
                "systems_active": authority_report,
            }
        except Exception as e:
            return {"valid": False, "error": str(e), "authority_assumed": False}

    def _enforce_task_level_determination(
        self, instruction: str, context: Optional[Dict]
    ) -> PresidentialDecision:
        """Enforce task level determination by PRESIDENT"""

        # Make presidential decision
        decision = self.functional_president.make_presidential_decision(
            instruction, context
        )
        return decision

    def _enforce_presidential_processing(
        self, decision: PresidentialDecision
    ) -> Dict[str, Any]:
        """Enforce presidential processing based on decision"""

        # Create execution plan based on presidential decision
        execution_plan = {
            "processing_mode": decision.required_mode.value,
            "mode_enforcement": self._get_mode_enforcement(decision.required_mode),
            "organization_deployment": {
                "roles": decision.organization_roles,
                "command_structure": "presidential",
                "coordination": "unified",
            },
            "quality_assurance": {
                "checkpoints": decision.quality_checkpoints,
                "enforcement": "mandatory",
                "oversight": "presidential",
            },
            "memory_management": decision.memory_requirements,
            "execution_authority": decision.execution_authority,
        }

        return execution_plan

    def _get_mode_enforcement(self, mode: ProcessingMode) -> Dict[str, Any]:
        """Get mode enforcement specifications"""

        if mode == ProcessingMode.ULTRATHINK:
            return {
                "thinking_tags": "MANDATORY",
                "analysis_depth": "MAXIMUM",
                "reasoning_level": "COMPREHENSIVE",
                "solution_quality": "OPTIMAL",
                "error_tolerance": "ZERO",
            }
        elif mode == ProcessingMode.THINKING:
            return {
                "thinking_tags": "REQUIRED",
                "analysis_depth": "THOROUGH",
                "reasoning_level": "DETAILED",
                "solution_quality": "HIGH",
                "error_tolerance": "MINIMAL",
            }
        else:
            return {
                "thinking_tags": "OPTIONAL",
                "analysis_depth": "STANDARD",
                "reasoning_level": "NORMAL",
                "solution_quality": "ADEQUATE",
                "error_tolerance": "ACCEPTABLE",
            }

    def _block_execution(self, reason: str, instruction: str) -> Dict[str, Any]:
        """Block execution due to flow violation"""

        violation = {
            "timestamp": datetime.now().isoformat(),
            "instruction": instruction,
            "violation_reason": reason,
            "flow_step": "BLOCKED",
        }

        self.flow_violations.append(violation)

        print(f"🚫 EXECUTION BLOCKED: {reason}")
        print("❌ MANDATORY FLOW VIOLATION")

        return {
            "flow_status": "BLOCKED",
            "reason": reason,
            "instruction": instruction,
            "violation_id": len(self.flow_violations),
        }

    def get_flow_statistics(self) -> Dict[str, Any]:
        """Get flow enforcement statistics"""
        total_attempts = self.successful_flows + len(self.flow_violations)
        success_rate = (
            (self.successful_flows / total_attempts * 100) if total_attempts > 0 else 0
        )

        return {
            "total_flow_attempts": total_attempts,
            "successful_flows": self.successful_flows,
            "flow_violations": len(self.flow_violations),
            "success_rate": f"{success_rate:.1f}%",
            "enforcement_active": True,
        }


# Demonstration function
def demonstrate_mandatory_flow():
    """Demonstrate the mandatory flow enforcement"""

    enforcer = MandatoryFlowEnforcer()

    print("🧪 MANDATORY FLOW ENFORCEMENT DEMONSTRATION")
    print("=" * 60)
    print()

    # Test the current instruction
    result = enforcer.process_instruction("ultrathinkで続けて")

    print("\n📊 FLOW ENFORCEMENT RESULTS:")
    if result["flow_status"] == "COMPLETED":
        print("✅ Flow enforcement SUCCESSFUL")
        print("✅ All 4 steps completed correctly")
        print("✅ Presidential processing established")
    else:
        print("❌ Flow enforcement FAILED")
        print(f"❌ Reason: {result.get('reason', 'Unknown')}")

    # Show statistics
    stats = enforcer.get_flow_statistics()
    print(f"\n📈 Flow Statistics: {stats['success_rate']} success rate")

    return result


if __name__ == "__main__":
    demonstrate_mandatory_flow()
