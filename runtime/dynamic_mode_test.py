#!/usr/bin/env python3
"""Test dynamic mode switching end-to-end"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.enforcement.dynamic_mode_switcher import DynamicModeSwitcher  # noqa: E402


def test_dynamic_switching():
    """Test the complete dynamic mode switching flow"""

    print("🔄 Dynamic Mode Switching Test")
    print("=" * 40)

    switcher = DynamicModeSwitcher()

    # Test: Normal task level determination
    print("\n1. Task Level Determination (Normal Mode)")
    test_input = "柔軟にモード変更をしてほしい！！これがおそらく答えだ！！"

    task_level, switch_marker = switcher.process_user_input(test_input)

    print(f"Input: {test_input}")
    print(f"Determined Level: {task_level.value}")
    print(f"Mode Info: {switcher.get_current_mode_info()}")

    if switch_marker:
        print("Generated Mode Switch:")
        print(switch_marker)
    else:
        print("No mode switch required")

    # Test: HIGH level task
    print("\n2. HIGH Level Task Detection")
    high_input = "システムの統合実装をして"

    switcher_high = DynamicModeSwitcher()
    task_level_high, switch_marker_high = switcher_high.process_user_input(high_input)

    print(f"Input: {high_input}")
    print(f"Determined Level: {task_level_high.value}")
    print(f"Mode Info: {switcher_high.get_current_mode_info()}")

    if switch_marker_high:
        print("Generated Mode Switch:")
        print(switch_marker_high)

    # Test: CRITICAL level task
    print("\n3. CRITICAL Level Task Detection")
    critical_input = "最重要任務：欠陥を修正しろ"

    switcher_critical = DynamicModeSwitcher()
    task_level_critical, switch_marker_critical = switcher_critical.process_user_input(critical_input)

    print(f"Input: {critical_input}")
    print(f"Determined Level: {task_level_critical.value}")
    print(f"Mode Info: {switcher_critical.get_current_mode_info()}")

    if switch_marker_critical:
        print("Generated Mode Switch:")
        print(switch_marker_critical)

    print("\n✅ Dynamic Mode Switching Test Complete")
    print("🎯 Solution: Task level determination → Flexible mode switching")

if __name__ == "__main__":
    test_dynamic_switching()
