#!/usr/bin/env python3
"""
🎯 Claude Code Interceptor - 実行前強制検証システム
===============================================

Claude Codeの実行フローに統合されたinterceptor
- 全レスポンス前にReference Monitor経由
- リアルタイムULTRATHINK/thinking強制
- PRESIDENT宣言必須チェック
- Constitutional AI自動適用

Usage:
    # Claude Code起動前に実行
    python scripts/claude_code_interceptor.py --enable

    # 無効化 (緊急時のみ)
    python scripts/claude_code_interceptor.py --disable
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.enforcement.hook_integration import HookIntegration  # noqa: E402


class ClaudeCodeInterceptor:
    """Claude Code実行フロー統合interceptor"""

    def __init__(self):
        self.hook_integration = HookIntegration()
        self.interceptor_active = False
        self.config_file = project_root / "runtime" / "interceptor_config.json"

        # Load configuration
        self._load_config()

    def _load_config(self):
        """Load interceptor configuration"""
        if self.config_file.exists():
            with open(self.config_file) as f:
                config = json.load(f)
                self.interceptor_active = config.get("enabled", False)
        else:
            self.interceptor_active = False

    def _save_config(self):
        """Save interceptor configuration"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        config = {
            "enabled": self.interceptor_active,
            "version": "2.0",
            "last_updated": datetime.now().isoformat(),
        }
        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=2)

    async def enable_interceptor(self):
        """Enable Claude Code interceptor"""

        print("🎯 Enabling Claude Code Interceptor...")

        # 1. Session initialization check
        print("\n1️⃣ Session Initialization Check")
        session_result = await self.hook_integration.session_initialization_hook({})

        for key, value in session_result.items():
            if key == "errors":
                if value:
                    print(f"   ❌ Errors: {', '.join(value)}")
                else:
                    print("   ✅ No errors")
            elif isinstance(value, bool):
                status = "✅" if value else "❌"
                print(f"   {status} {key.replace('_', ' ').title()}: {value}")

        # 2. PRESIDENT declaration requirement
        print("\n2️⃣ PRESIDENT Declaration Check")
        president_valid = (
            await self.hook_integration.monitor.validate_president_declaration()
        )
        if not president_valid:
            print("   ❌ PRESIDENT declaration required")
            print("   📋 Run: make declare-president")
            return False
        else:
            print("   ✅ PRESIDENT declaration valid")

        # 3. Constitutional AI system check
        print("\n3️⃣ Constitutional AI System")
        stats = await self.hook_integration.monitor.get_enforcement_statistics()
        print(f"   📊 Policy Version: {stats['policy_version']}")
        print(f"   📊 Total Decisions: {stats['total_decisions']}")
        print(f"   📊 Recent Activity: {stats['recent_24h']} (24h)")

        # 4. AI Organization check
        print("\n4️⃣ AI Organization Status")
        openai_key = os.getenv("OPENAI_API_KEY")
        gemini_key = os.getenv("GEMINI_API_KEY")

        print(
            f"   {'✅' if openai_key else '❌'} OpenAI API: {'Available' if openai_key else 'Missing'}"
        )
        print(
            f"   {'✅' if gemini_key else '❌'} Gemini API: {'Available' if gemini_key else 'Missing'}"
        )

        # 5. Enable interceptor
        if all(
            [
                president_valid,
                session_result.get("claude_md_validation", False),
                session_result.get("database_connections", False),
                bool(openai_key and gemini_key),
            ]
        ):
            self.interceptor_active = True
            self._save_config()

            print("\n✅ Claude Code Interceptor ENABLED")
            print("🔒 All responses will be validated through Reference Monitor")
            print("🧠 CRITICAL tasks will require ULTRATHINK/thinking tags")
            print("🏛️ Constitutional AI enforcement active")
            return True
        else:
            print("\n❌ Cannot enable interceptor - requirements not met")
            return False

    async def disable_interceptor(self, reason: str = "Manual disable"):
        """Disable Claude Code interceptor"""

        print(f"⚠️  Disabling Claude Code Interceptor: {reason}")

        self.interceptor_active = False
        self._save_config()

        # Also disable hooks
        self.hook_integration.disable_hooks(reason)

        print("❌ Claude Code Interceptor DISABLED")
        print("⚠️  AI safety enforcement is now INACTIVE")
        print("⚠️  Manual compliance required")

    async def test_interceptor(self):
        """Test interceptor with sample responses"""

        if not self.interceptor_active:
            print("❌ Interceptor not active - cannot test")
            return

        print("🧪 Testing Claude Code Interceptor")
        print("=" * 40)

        # Test cases
        test_cases = [
            {
                "name": "CRITICAL without thinking",
                "response": "This is a critical response without thinking tags",
                "context": {"task_level": "CRITICAL"},
            },
            {
                "name": "CRITICAL with thinking",
                "response": "<thinking>Complex analysis required</thinking>This is the final response",
                "context": {"task_level": "CRITICAL"},
            },
            {
                "name": "HIGH task normal",
                "response": "This is a high-level response",
                "context": {"task_level": "HIGH"},
            },
            {
                "name": "MEDIUM task normal",
                "response": "This is a medium-level response",
                "context": {"task_level": "MEDIUM"},
            },
        ]

        for i, test_case in enumerate(test_cases, 1):
            print(f"\n🧪 Test {i}: {test_case['name']}")

            result = await self.hook_integration.pre_response_hook(
                test_case["response"], test_case["context"]
            )

            if result["allowed"]:
                print("   ✅ ALLOWED")
                if result.get("transformed"):
                    print("   🔄 TRANSFORMED")
                if "constitutional_score" in result:
                    print(
                        f"   📊 Constitutional Score: {result['constitutional_score']:.2f}"
                    )
            else:
                print(f"   ❌ DENIED: {result.get('error', 'Unknown error')}")
                if "required_action" in result:
                    print(f"   📋 Action: {result['required_action']}")

    async def get_status(self):
        """Get current interceptor status"""

        print("📊 Claude Code Interceptor Status")
        print("=" * 40)

        print(
            f"🎯 Interceptor Active: {'✅ YES' if self.interceptor_active else '❌ NO'}"
        )

        if self.interceptor_active:
            hook_status = await self.hook_integration.get_hook_status()
            print(
                f"🔗 Hooks Enabled: {'✅ YES' if hook_status['hooks_enabled'] else '❌ NO'}"
            )
            print(f"📊 Policy Version: {hook_status['policy_version']}")

            stats = hook_status["reference_monitor_stats"]
            print(f"📈 Total Decisions: {stats['total_decisions']}")
            print(f"📈 Recent Activity: {stats['recent_24h']} (24h)")

            if stats["verdicts"]:
                print("📊 Decision Breakdown:")
                for verdict, count in stats["verdicts"].items():
                    print(f"   {verdict.upper()}: {count}")


async def main():
    """Main CLI function"""

    parser = argparse.ArgumentParser(description="Claude Code Interceptor Control")
    parser.add_argument("--enable", action="store_true", help="Enable interceptor")
    parser.add_argument("--disable", action="store_true", help="Disable interceptor")
    parser.add_argument("--test", action="store_true", help="Test interceptor")
    parser.add_argument("--status", action="store_true", help="Show status")
    parser.add_argument("--reason", default="Manual", help="Reason for disable")

    args = parser.parse_args()

    interceptor = ClaudeCodeInterceptor()

    if args.enable:
        success = await interceptor.enable_interceptor()
        sys.exit(0 if success else 1)

    elif args.disable:
        await interceptor.disable_interceptor(args.reason)

    elif args.test:
        await interceptor.test_interceptor()

    elif args.status:
        await interceptor.get_status()

    else:
        # Default: show status
        await interceptor.get_status()


if __name__ == "__main__":
    asyncio.run(main())
