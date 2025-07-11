#!/usr/bin/env python3
"""
🔄 Dynamic Mode Switcher - Flexible Thinking Mode Management
==========================================================

Enables mid-response thinking mode switching based on task level:
1. Initial response: Normal mode for task level determination
2. Task level assessment: No thinking required
3. Mode switch: Automatic transition to appropriate thinking mode
4. Execution: Continue in required mode (thinking/ultrathink)

Solves the core issue of rigid thinking mode requirements.
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple


class ThinkingMode(Enum):
    """Available thinking modes"""

    NORMAL = "normal"
    THINKING = "thinking"
    ULTRATHINK = "ultrathink"


class TaskLevel(Enum):
    """Task complexity levels"""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class ModeTransition:
    """Mode transition configuration"""

    from_mode: ThinkingMode
    to_mode: ThinkingMode
    trigger_level: TaskLevel
    transition_marker: str


class DynamicModeSwitcher:
    """Manages flexible thinking mode transitions"""

    def __init__(self):
        self.current_mode = ThinkingMode.NORMAL
        self.current_task_level = None

        # Define transition rules
        self.transition_rules = {
            TaskLevel.HIGH: ThinkingMode.THINKING,
            TaskLevel.CRITICAL: ThinkingMode.ULTRATHINK,
        }

        # Transition markers
        self.mode_markers = {
            ThinkingMode.THINKING: "<thinking>",
            ThinkingMode.ULTRATHINK: "## 🔥 ULTRATHINK MODE ACTIVATED",
        }

    def determine_task_level(self, user_input: str) -> TaskLevel:
        """Determine task level from user input (normal mode)"""

        # Critical patterns
        critical_patterns = [
            r"最重要任務",
            r"CRITICAL",
            r"critical",
            r"欠陥.*修正",
            r"システム.*再構築",
            r"緊急.*修正",
            r"重大.*問題",
        ]

        # High patterns
        high_patterns = [
            r"実装.*しろ",
            r"実装.*して",
            r"統合.*システム",
            r"フロー.*設計",
            r"アーキテクチャ",
            r"複雑.*処理",
            r"包括的.*システム",
            r"設計.*して",
            r"システム.*構築",
        ]

        # Check for critical level
        for pattern in critical_patterns:
            if re.search(pattern, user_input, re.IGNORECASE):
                return TaskLevel.CRITICAL

        # Check for high level
        for pattern in high_patterns:
            if re.search(pattern, user_input, re.IGNORECASE):
                return TaskLevel.HIGH

        # Default to medium for substantial requests
        if len(user_input.strip()) > 50:
            return TaskLevel.MEDIUM

        return TaskLevel.LOW

    def should_switch_mode(self, task_level: TaskLevel) -> Optional[ThinkingMode]:
        """Determine if mode switch is needed"""

        required_mode = self.transition_rules.get(task_level)

        if required_mode and required_mode != self.current_mode:
            return required_mode

        return None

    def generate_mode_switch_marker(
        self, target_mode: ThinkingMode, task_level: TaskLevel
    ) -> str:
        """Generate appropriate mode switch marker"""

        if target_mode == ThinkingMode.THINKING:
            return f"""
<thinking>
Task level determined: {task_level.value}
Switching to thinking mode for detailed analysis and implementation planning.
This requires systematic approach with proper consideration of system integration points.
</thinking>

**Mode Switch**: Normal → Thinking Mode for {task_level.value} task"""

        elif target_mode == ThinkingMode.ULTRATHINK:
            return f"""
## 🔥 ULTRATHINK MODE ACTIVATED - {task_level.value} SYSTEM ANALYSIS

<thinking>
Task level: {task_level.value} - Requires maximum analytical depth
Critical system modification detected - engaging comprehensive analysis mode
Multiple system integration points require careful consideration
Error prevention and system integrity are paramount
</thinking>

**Mode Switch**: Normal → ULTRATHINK Mode for {task_level.value} task"""

        return ""

    def process_user_input(self, user_input: str) -> Tuple[TaskLevel, Optional[str]]:
        """Process user input and determine mode switching"""

        # Step 1: Determine task level (normal mode)
        task_level = self.determine_task_level(user_input)
        self.current_task_level = task_level

        # Step 2: Check if mode switch needed
        target_mode = self.should_switch_mode(task_level)

        if target_mode:
            # Generate mode switch
            switch_marker = self.generate_mode_switch_marker(target_mode, task_level)
            self.current_mode = target_mode
            return task_level, switch_marker

        return task_level, None

    def get_current_mode_info(self) -> dict:
        """Get current mode information"""

        return {
            "current_mode": self.current_mode.value,
            "task_level": self.current_task_level.value
            if self.current_task_level
            else "UNKNOWN",
            "thinking_required": self.current_mode
            in [ThinkingMode.THINKING, ThinkingMode.ULTRATHINK],
        }


def main():
    """Demo dynamic mode switching"""

    switcher = DynamicModeSwitcher()

    # Test cases
    test_inputs = [
        "ファイルを読んで",  # LOW
        "システムの統合設計を実装して",  # HIGH
        "最重要任務：欠陥を修正しろ",  # CRITICAL
        "説明して",  # LOW
    ]

    for user_input in test_inputs:
        print(f"\n{'=' * 50}")
        print(f"Input: {user_input}")

        task_level, switch_marker = switcher.process_user_input(user_input)

        print(f"Task Level: {task_level.value}")
        print(f"Mode Info: {switcher.get_current_mode_info()}")

        if switch_marker:
            print("Mode Switch Generated:")
            print(switch_marker)
        else:
            print("No mode switch required")


if __name__ == "__main__":
    main()
