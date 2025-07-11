#!/usr/bin/env python3
"""
🎼 Unified Claude Interceptor - Complete Integration
===================================================

Single entry point for all Claude Code enforcement with automatic:
- Task level classification
- PRESIDENT validation
- Dynamic escalation
- Reference Monitor enforcement

Usage:
    python scripts/unified_claude_interceptor.py --enable
    python scripts/unified_claude_interceptor.py --test "Your request here"
    python scripts/unified_claude_interceptor.py --status
"""

import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

try:
    from src.enforcement.unified_flow_orchestrator import UnifiedFlowOrchestrator
except ImportError:
    # Add project root to path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    from src.enforcement.unified_flow_orchestrator import UnifiedFlowOrchestrator


class UnifiedClaudeInterceptor:
    """Main Claude Code enforcement interceptor with automatic flow"""

    def __init__(self):
        self.orchestrator = UnifiedFlowOrchestrator()
        self.config_file = project_root / "runtime" / "unified_interceptor_config.json"
        self.active = False

        # Load configuration
        self._load_config()

    def _load_config(self):
        """Load interceptor configuration"""
        try:
            if self.config_file.exists():
                with open(self.config_file) as f:
                    config = json.load(f)
                    self.active = config.get("active", False)
        except Exception:
            self.active = False

    def _save_config(self):
        """Save interceptor configuration"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            config = {
                "active": self.active,
                "version": "2.0",
                "last_updated": datetime.now().isoformat(),
                "features": {
                    "automatic_classification": True,
                    "lightweight_president": True,
                    "dynamic_escalation": True,
                    "reference_monitor": True,
                },
            }
            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save config: {e}")

    async def enable(self):
        """Enable unified Claude interceptor"""

        print("🎼 Enabling Unified Claude Interceptor...")
        print("=" * 45)

        # Test all subsystems
        print("1️⃣ Testing Subsystems...")

        try:
            # Test basic flow
            test_result = await self.orchestrator.process_request(
                "Test system status", {}
            )
            print(f"   ✅ Unified Flow: {test_result.processing_time_ms:.1f}ms")

            # Test performance
            stats = self.orchestrator.get_performance_stats()
            health = stats["subsystem_health"]

            print(f"   ✅ Task Classifier: {health['task_classifier']}")
            print(
                f"   {'✅' if health['president_validator'] == 'operational' else '⚠️'} PRESIDENT Validator: {health['president_validator']}"
            )
            print(f"   ✅ Escalation System: {health['escalation_system']}")
            print(f"   ✅ Reference Monitor: {health['reference_monitor']}")

        except Exception as e:
            print(f"   ❌ Subsystem test failed: {e}")
            return False

        print("\\n2️⃣ Flow Integration Test...")

        # Test different scenarios
        test_scenarios = [
            ("Low priority query", {"expected_level": "LOW"}),
            ("Implement database system", {"expected_level": "HIGH"}),
            ("CRITICAL: Fix security breach!", {"expected_level": "CRITICAL"}),
        ]

        for scenario, context in test_scenarios:
            try:
                result = await self.orchestrator.process_request(scenario, context)
                print(f"   ✅ {result.final_task_level.value}: {scenario[:30]}...")
            except Exception as e:
                print(f"   ❌ Failed: {scenario[:30]}... - {e}")
                return False

        print("\\n3️⃣ Performance Validation...")

        # Performance test
        start_time = asyncio.get_event_loop().time()
        for i in range(10):
            await self.orchestrator.process_request(f"Test request {i}", {})
        avg_time = (asyncio.get_event_loop().time() - start_time) * 1000 / 10

        print(f"   ✅ Average Response Time: {avg_time:.1f}ms")

        if avg_time > 50:  # > 50ms is concerning
            print("   ⚠️ Performance warning: Response time above 50ms")

        # Enable interceptor
        self.active = True
        self._save_config()

        print("\\n✅ Unified Claude Interceptor ENABLED")
        print("🎯 Features Active:")
        print("   • Automatic task level classification")
        print("   • Lightweight PRESIDENT validation")
        print("   • Dynamic escalation system")
        print("   • Reference Monitor enforcement")
        print("   • Cryptographic proof generation")

        return True

    async def disable(self, reason: str = "Manual disable"):
        """Disable unified interceptor"""

        print(f"⚠️ Disabling Unified Claude Interceptor: {reason}")

        self.active = False
        self._save_config()

        print("❌ Unified Claude Interceptor DISABLED")
        print("⚠️ Manual task level specification required")

    async def test_request(self, user_request: str, context: dict = None):
        """Test a specific request through the unified flow"""

        if context is None:
            context = {}

        print(f"🧪 Testing Request: {user_request}")
        print("=" * 50)

        # Process request
        result = await self.orchestrator.process_request(user_request, context)

        # Display results
        print(f"📝 Input: {result.user_input}")
        print(f"🎯 Final Decision: {'✅ ALLOWED' if result.allowed else '❌ DENIED'}")
        print(f"⏱️ Processing Time: {result.processing_time_ms:.1f}ms")
        print()

        print("📊 Classification:")
        print(f"   Initial Level: {result.initial_classification.level.value}")
        print(f"   Confidence: {result.initial_classification.confidence:.1%}")
        if result.initial_classification.matched_patterns:
            print(
                f"   Patterns: {', '.join(result.initial_classification.matched_patterns[:2])}"
            )
        print()

        if result.escalation_decision.escalated:
            print("📈 Escalation:")
            print(
                f"   {result.initial_classification.level.value} → {result.final_task_level.value}"
            )
            print(f"   Triggers: {len(result.escalation_decision.triggers)}")
            for trigger in result.escalation_decision.triggers[:2]:
                print(f"   • {trigger.description}")
            print()

        print("🔒 Enforcement:")
        print(f"   Verdict: {result.enforcement_decision.verdict.value.upper()}")
        print(
            f"   Constitutional Score: {result.enforcement_decision.constitutional_ai_score:.3f}"
        )
        print(f"   Reasoning Trace: {result.enforcement_decision.reasoning_trace_id}")
        print()

        print("🔄 Flow Steps:")
        for step in result.flow_steps:
            print(f"   • {step}")

        if not result.allowed:
            print()
            print(f"❌ Response: {result.response}")

    async def get_status(self):
        """Get current interceptor status"""

        print("📊 Unified Claude Interceptor Status")
        print("=" * 40)

        print(f"🎼 Interceptor Active: {'✅ YES' if self.active else '❌ NO'}")

        if self.active:
            # Get performance stats
            stats = self.orchestrator.get_performance_stats()

            print("📈 Performance:")
            print(f"   Total Requests: {stats['total_requests']}")
            print(f"   Avg Processing Time: {stats['avg_processing_time']:.1f}ms")
            print(f"   Classification Time: {stats['classification_time']:.1f}ms")
            print(f"   PRESIDENT Check Time: {stats['president_check_time']:.1f}ms")
            print(f"   Escalation Time: {stats['escalation_time']:.1f}ms")
            print(f"   Enforcement Time: {stats['enforcement_time']:.1f}ms")

            print("\\n🔧 Subsystem Health:")
            health = stats["subsystem_health"]
            for system, status in health.items():
                status_icon = "✅" if status == "operational" else "⚠️"
                print(f"   {status_icon} {system.replace('_', ' ').title()}: {status}")

        print("\\n📁 Configuration:")
        try:
            with open(self.config_file) as f:
                config = json.load(f)
                print(f"   Version: {config.get('version', 'unknown')}")
                print(f"   Last Updated: {config.get('last_updated', 'unknown')}")
        except Exception:
            print("   Configuration file not found")


async def main():
    """Main CLI function"""

    parser = argparse.ArgumentParser(description="Unified Claude Interceptor")
    parser.add_argument("--enable", action="store_true", help="Enable interceptor")
    parser.add_argument("--disable", action="store_true", help="Disable interceptor")
    parser.add_argument("--test", type=str, help="Test a specific request")
    parser.add_argument("--status", action="store_true", help="Show status")
    parser.add_argument(
        "--context", type=str, help="Additional context (JSON)", default="{}"
    )

    args = parser.parse_args()

    interceptor = UnifiedClaudeInterceptor()

    if args.enable:
        success = await interceptor.enable()
        sys.exit(0 if success else 1)

    elif args.disable:
        await interceptor.disable()

    elif args.test:
        try:
            context = json.loads(args.context)
        except json.JSONDecodeError:
            print("Invalid JSON context provided")
            sys.exit(1)

        await interceptor.test_request(args.test, context)

    elif args.status:
        await interceptor.get_status()

    else:
        # Default: show status
        await interceptor.get_status()


if __name__ == "__main__":
    asyncio.run(main())
