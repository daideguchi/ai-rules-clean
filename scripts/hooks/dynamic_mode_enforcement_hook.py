#!/usr/bin/env python3
"""
🔄 Dynamic Mode Enforcement Hook - Real-time Mode Switching
==========================================================

Integrates dynamic mode switching into Claude Code execution flow:
- Initial assessment in normal mode
- Automatic mode transition based on task level
- Real-time enforcement of thinking requirements
- Flexible response structure

This hook replaces rigid thinking mode requirements with intelligent switching.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.enforcement.dynamic_mode_switcher import (
        DynamicModeSwitcher,
        TaskLevel,
        ThinkingMode,
    )
except ImportError:
    # Graceful fallback
    DynamicModeSwitcher = None
    TaskLevel = None
    ThinkingMode = None


def read_hook_input():
    """Read JSON input from stdin (Claude Code hook standard)"""
    try:
        input_data = json.load(sys.stdin)
        return input_data
    except Exception:
        return {}


def respond_with_mode_decision(allow=True, mode_switch_info=None, error_message=None):
    """Send mode switching decision back to Claude Code"""

    response = {"decision": "continue"}

    if not allow:
        response = {
            "decision": "block",
            "message": error_message or "Request blocked by dynamic mode enforcement",
        }
    elif mode_switch_info:
        response["message"] = f"""🔄 Dynamic Mode Switch Detected

{mode_switch_info.get("switch_marker", "")}

Task Level: {mode_switch_info.get("task_level", "UNKNOWN")}
Mode: {mode_switch_info.get("current_mode", "normal")}
Thinking Required: {mode_switch_info.get("thinking_required", False)}

Proceeding with appropriate analysis depth..."""

    print(json.dumps(response))


def main():
    """Main dynamic mode enforcement hook"""

    try:
        # Read input from Claude Code
        hook_input = read_hook_input()

        # Extract user input
        user_input = hook_input.get("user_input", "")
        tool_name = hook_input.get("tool", {}).get("name", "unknown")

        if not user_input:
            # No user input to analyze
            respond_with_mode_decision(allow=True)
            return

        # Apply dynamic mode switching if available
        if DynamicModeSwitcher:
            switcher = DynamicModeSwitcher()

            # Process user input and determine mode switching
            task_level, switch_marker = switcher.process_user_input(user_input)

            # Get mode information
            mode_info = switcher.get_current_mode_info()

            # Log mode switching decision
            mode_log = project_root / "runtime" / "mode_switching_log.json"
            mode_log.parent.mkdir(parents=True, exist_ok=True)

            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "user_input": user_input[:100] + "..."
                if len(user_input) > 100
                else user_input,
                "task_level": task_level.value,
                "mode_switched": switch_marker is not None,
                "current_mode": mode_info["current_mode"],
                "thinking_required": mode_info["thinking_required"],
                "tool_name": tool_name,
            }

            # Update log
            if mode_log.exists():
                with open(mode_log) as f:
                    log_data = json.load(f)
            else:
                log_data = {"mode_switches": []}

            log_data["mode_switches"].append(log_entry)

            # Keep only recent entries (last 100)
            if len(log_data["mode_switches"]) > 100:
                log_data["mode_switches"] = log_data["mode_switches"][-100:]

            with open(mode_log, "w") as f:
                json.dump(log_data, f, indent=2)

            # Prepare response
            if switch_marker:
                mode_switch_info = {
                    "switch_marker": switch_marker,
                    "task_level": task_level.value,
                    "current_mode": mode_info["current_mode"],
                    "thinking_required": mode_info["thinking_required"],
                }
                respond_with_mode_decision(
                    allow=True, mode_switch_info=mode_switch_info
                )
            else:
                respond_with_mode_decision(allow=True)

        else:
            # Dynamic mode switcher not available - allow with warning
            respond_with_mode_decision(
                allow=True,
                mode_switch_info={
                    "switch_marker": "⚠️ Dynamic mode switching system not available - using default mode"
                },
            )

    except Exception as e:
        # Fail securely - allow execution but log error
        error_log = project_root / "runtime" / "mode_hook_errors.log"
        try:
            with open(error_log, "a") as f:
                f.write(f"{datetime.now().isoformat()}: Dynamic mode hook error: {e}\n")
        except Exception:
            pass

        respond_with_mode_decision(
            allow=True, error_message=f"⚠️ Mode enforcement hook error: {e}"
        )


if __name__ == "__main__":
    main()
