#!/usr/bin/env python3
"""
🎼 Unified Enforcement Hook - Real-time Claude Code Integration
==============================================================

Integrates the unified enforcement system into Claude Code execution flow:
- Automatic task level classification from user input
- PRESIDENT validation for CRITICAL tasks
- Constitutional AI enforcement
- Real-time ULTRATHINK detection and enforcement
- User prompt recording

This hook executes at PreToolUse and provides actual blocking capability.
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.enforcement.unified_flow_orchestrator import UnifiedFlowOrchestrator
    from src.memory.user_prompt_recorder import UserPromptRecorder
except ImportError:
    # Graceful fallback if enforcement system not available
    UnifiedFlowOrchestrator = None
    UserPromptRecorder = None


def read_hook_input():
    """Read JSON input from stdin (Claude Code hook standard)"""
    try:
        input_data = json.load(sys.stdin)
        return input_data
    except Exception:
        return {}


def respond_with_decision(allow=True, error_message=None, transform_message=None):
    """Send decision back to Claude Code"""

    if not allow:
        response = {
            "decision": "block",
            "message": error_message or "Request blocked by enforcement system",
        }
    elif transform_message:
        response = {"decision": "continue", "message": transform_message}
    else:
        response = {"decision": "continue"}

    print(json.dumps(response))


async def main():
    """Main hook function"""

    try:
        # Read input from Claude Code
        hook_input = read_hook_input()

        # Extract user input and tool information
        user_input = hook_input.get("user_input", "")
        tool_name = hook_input.get("tool", {}).get("name", "unknown")

        if not user_input:
            # No user input to enforce
            respond_with_decision(allow=True)
            return

        # Apply unified enforcement if available
        if UnifiedFlowOrchestrator:
            orchestrator = UnifiedFlowOrchestrator()

            # Build context
            context = {
                "tool_name": tool_name,
                "claude_code_hook": True,
                "real_time_enforcement": True,
                "session_id": hook_input.get("session_id", "unknown"),
            }

            # Process through unified enforcement
            result = await orchestrator.process_request(user_input, context)

            # Record user prompt
            if UserPromptRecorder:
                try:
                    recorder = UserPromptRecorder()
                    recorder.record_prompt(
                        user_input,
                        task_level=result.final_task_level.value,
                        metadata={
                            "tool_name": tool_name,
                            "enforcement_result": result.allowed,
                            "constitutional_score": result.enforcement_decision.constitutional_ai_score,
                        },
                    )
                except Exception:
                    pass  # Non-critical - continue if recording fails

            # Make enforcement decision
            if not result.allowed:
                # Block execution
                error_msg = f"""🎼 UNIFIED ENFORCEMENT BLOCK

Task Level: {result.final_task_level.value}
Constitutional AI Score: {result.enforcement_decision.constitutional_ai_score:.3f}

{result.response}

Required: Execute tasks with proper thinking tags and PRESIDENT declaration."""

                respond_with_decision(allow=False, error_message=error_msg)
                return

            # Check for ULTRATHINK requirement
            if (
                result.final_task_level.value == "CRITICAL"
                and "thinking" not in user_input.lower()
            ):
                transform_msg = f"""🔥 CRITICAL TASK DETECTED - ULTRATHINK REQUIRED

Task Level: {result.final_task_level.value}
Processing Time: {result.processing_time_ms:.1f}ms

This CRITICAL task requires <thinking> tags for proper analysis.
Constitutional AI Score: {result.enforcement_decision.constitutional_ai_score:.3f}

Please restart with proper thinking tags."""

                respond_with_decision(allow=True, transform_message=transform_msg)
                return

            # Allow with note
            if result.final_task_level.value != "LOW":
                note_msg = f"""✅ Unified Enforcement: ALLOWED
Task Level: {result.final_task_level.value} | Score: {result.enforcement_decision.constitutional_ai_score:.3f} | Time: {result.processing_time_ms:.1f}ms"""
                respond_with_decision(allow=True, transform_message=note_msg)
            else:
                respond_with_decision(allow=True)

        else:
            # Enforcement system not available - allow with warning
            respond_with_decision(
                allow=True,
                transform_message="⚠️ Unified enforcement system not available",
            )

    except Exception as e:
        # Fail securely - allow execution but log error
        error_log = project_root / "runtime" / "hook_errors.log"
        try:
            with open(error_log, "a") as f:
                f.write(
                    f"{datetime.now().isoformat()}: Unified enforcement hook error: {e}\n"
                )
        except Exception:
            pass

        respond_with_decision(
            allow=True, transform_message=f"⚠️ Enforcement hook error: {e}"
        )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception:
        # Final fallback - allow execution
        respond_with_decision(allow=True)
