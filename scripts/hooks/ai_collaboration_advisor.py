#!/usr/bin/env python3
"""
AI Collaboration Advisor Hook
Automatic detection when AI collaboration is needed and routing to multiagent system
"""

import subprocess
import sys
from pathlib import Path

# Import task complexity classifier
sys.path.append(str(Path(__file__).resolve().parents[2] / "src"))
from ai.task_complexity_classifier import TaskComplexityClassifier


def get_last_user_message():
    """Extract last user message from Claude Code context"""
    try:
        # This would be replaced with actual Claude Code API integration
        # For now, return a placeholder
        return "Task analysis request"
    except Exception:
        return None


def send_collaboration_request(task_description: str, complexity_info: dict):
    """Send collaboration request to multiagent system"""
    try:
        # Send to BOSS1 for coordination
        collaboration_msg = f"""
🤝 AI協業要請

タスク: {task_description}
複雑度: {complexity_info.get("level", "unknown")}
理由: {complexity_info.get("reasoning", "Complex task requiring expertise")}

専門的な見解・アドバイスをお願いします。
特に以下の観点から検討してください：
1. 実装アプローチの最適性
2. 潜在的なリスク・問題点
3. 代替案・改善提案
4. セキュリティ・パフォーマンス考慮事項

協議結果を待機しています。
        """

        # Send message to multiagent BOSS1
        subprocess.run(
            ["tmux", "send-keys", "-t", "multiagent:0.0", collaboration_msg, "C-m"],
            check=True,
        )

        print("✅ Collaboration request sent to AI organization")
        print(f"📋 Task: {task_description[:50]}...")
        print(f"🎯 Complexity: {complexity_info.get('level', 'unknown')}")

        return True

    except Exception as e:
        print(f"❌ Failed to send collaboration request: {e}")
        return False


def check_collaboration_need(task_description: str = None) -> bool:
    """Check if AI collaboration is needed based on task complexity"""
    try:
        if not task_description:
            task_description = get_last_user_message()

        if not task_description:
            return False

        # Use task complexity classifier
        classifier = TaskComplexityClassifier()
        classification = classifier.classify_task(task_description)

        # Check if collaboration is needed
        collaboration_needed = classification.ai_collaboration_needed

        # Additional checks for collaboration triggers
        collaboration_triggers = [
            "統合",
            "integration",
            "architecture",
            "アーキテクチャ",
            "security",
            "セキュリティ",
            "performance",
            "パフォーマンス",
            "複数システム",
            "multiple systems",
            "破綻",
            "critical",
        ]

        if any(
            trigger in task_description.lower() for trigger in collaboration_triggers
        ):
            collaboration_needed = True

        if collaboration_needed:
            complexity_info = {
                "level": classification.level.name,
                "confidence": classification.confidence,
                "reasoning": classification.reasoning,
                "required_files": classification.required_files,
            }

            send_collaboration_request(task_description, complexity_info)

        return collaboration_needed

    except Exception as e:
        print(f"⚠️ Collaboration check failed: {e}")
        return False


def main():
    """Main hook execution"""
    try:
        # Check if multiagent session exists
        try:
            subprocess.run(
                ["tmux", "has-session", "-t", "multiagent"],
                capture_output=True,
                check=True,
            )
        except subprocess.CalledProcessError:
            print("ℹ️ Multiagent session not available - skipping collaboration check")
            return

        # Get task from command line args if provided
        task_description = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None

        # Check collaboration need
        collaboration_needed = check_collaboration_need(task_description)

        if collaboration_needed:
            print("🤝 AI collaboration initiated")
        else:
            print("✅ Task can be handled independently")

    except Exception as e:
        print(f"❌ AI collaboration advisor failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
