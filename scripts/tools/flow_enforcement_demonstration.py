#!/usr/bin/env python3
"""
🎼 Real-Time Flow Enforcement Demonstration
===========================================

Demonstrates the correct processing flow for actual user instructions.
"""

import sys
import time
from datetime import datetime
from pathlib import Path

try:
    from src.enforcement.task_classifier import TaskLevel
    from src.enforcement.unified_flow_orchestrator import UnifiedFlowOrchestrator
except ImportError:
    # Add project root to path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    from src.enforcement.task_classifier import TaskLevel
    from src.enforcement.unified_flow_orchestrator import UnifiedFlowOrchestrator


class FlowEnforcementDemo:
    """Demonstrates real-time flow enforcement"""

    def __init__(self):
        self.orchestrator = UnifiedFlowOrchestrator()
        self.session_start = datetime.now()

    async def process_user_instruction(self, instruction: str):
        """Process actual user instruction through correct flow"""

        print("🔥 PROCESSING FLOW DEMONSTRATION")
        print("=" * 50)
        print(f"📝 User Instruction: '{instruction}'")
        print(f"⏰ Timestamp: {datetime.now().isoformat()}")
        print()

        # Step 1: Instruction received
        print("📨 STEP 1: Instruction Received ✅")

        # Step 2: PRESIDENT confirmation (lightweight)
        print("👑 STEP 2: PRESIDENT Confirmation...")
        president_status = self.orchestrator.president_validator.quick_check()
        if president_status:
            print("   ✅ PRESIDENT status: VALID")
        else:
            print("   ❌ PRESIDENT status: INVALID - Declaration required")
            return self._block_execution("PRESIDENT declaration required")

        # Step 3: Task level classification
        print("🎯 STEP 3: Task Level Classification...")
        start_time = time.time()
        classification = await self.orchestrator.task_classifier.classify_task(
            instruction
        )
        class_time = (time.time() - start_time) * 1000

        print(f"   📊 Classification Result: {classification.task_level.value}")
        print(f"   🔢 Confidence: {classification.confidence:.2f}")
        print(f"   ⏱️  Time: {class_time:.1f}ms")

        # Step 4: Mode determination based on task level
        print("🔄 STEP 4: Mode Determination...")
        if classification.task_level == TaskLevel.CRITICAL:
            required_mode = "ULTRATHINK"
            print("   🧠 Required Mode: ULTRATHINK")
        elif classification.task_level == TaskLevel.HIGH:
            required_mode = "THINKING"
            print("   💭 Required Mode: THINKING")
        else:
            required_mode = "NORMAL"
            print("   ⚪ Required Mode: NORMAL")

        # Step 5: Execute in appropriate mode
        print(f"⚡ STEP 5: Execution in {required_mode} Mode...")

        if required_mode == "ULTRATHINK":
            print("   🔥 ULTRATHINK MODE ACTIVATED")
            print("   🎯 Deep analysis and comprehensive solution")
            print("   🔬 Enhanced reasoning capabilities enabled")
            result = "ULTRATHINK mode successfully executed"
        elif required_mode == "THINKING":
            print("   💭 THINKING MODE ACTIVATED")
            print("   🤔 Analytical thinking process enabled")
            result = "THINKING mode successfully executed"
        else:
            print("   ⚪ NORMAL MODE EXECUTION")
            result = "Normal processing completed"

        # Summary
        print()
        print("📋 FLOW EXECUTION SUMMARY:")
        print(f"   📝 Input: {instruction}")
        print(f"   👑 PRESIDENT: {'✅ Valid' if president_status else '❌ Invalid'}")
        print(f"   🎯 Task Level: {classification.task_level.value}")
        print(f"   🔄 Mode: {required_mode}")
        print(f"   ✅ Result: {result}")
        print(f"   ⏰ Total Time: {(time.time() - start_time) * 1000:.1f}ms")

        return {
            "instruction": instruction,
            "president_valid": president_status,
            "task_level": classification.task_level.value,
            "required_mode": required_mode,
            "result": result,
            "success": True,
        }

    def _block_execution(self, reason: str):
        """Block execution with reason"""
        print(f"🚫 EXECUTION BLOCKED: {reason}")
        return {"instruction": "blocked", "reason": reason, "success": False}


async def main():
    """Demonstrate real flow enforcement"""
    demo = FlowEnforcementDemo()

    # Process actual user instruction
    result = await demo.process_user_instruction("ultrathink")

    if result["success"]:
        print("\n🎉 DEMONSTRATION COMPLETE: Flow correctly enforced!")
    else:
        print(f"\n❌ EXECUTION BLOCKED: {result['reason']}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
