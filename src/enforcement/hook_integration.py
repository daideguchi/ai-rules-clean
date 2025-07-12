#!/usr/bin/env python3
"""
🔗 Hook Integration - Claude Code強制実行統合
===========================================

Reference MonitorをClaude Codeのhookシステムに統合
- Pre-response validation
- Real-time reasoning trace monitoring
- PRESIDENT declaration enforcement
- Constitutional AI integration
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.enforcement.reference_monitor import (  # noqa: E402
    PolicyVerdict,
    ReferenceMonitor,
)


class HookIntegration:
    """Claude Code Hook Integration for Reference Monitor"""

    def __init__(self):
        self.monitor = ReferenceMonitor()
        self.logger = logging.getLogger(__name__)

        # Hook configuration
        self.hooks_enabled = True
        self.bypass_codes = set()  # Emergency bypass codes

    async def pre_response_hook(
        self, response_text: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Pre-response validation hook
        Called before Claude sends any response to user
        """

        if not self.hooks_enabled:
            return {"allowed": True, "response": response_text}

        try:
            # Extract task level from context
            task_level = context.get("task_level", "MEDIUM")

            # Tokenize response for analysis
            tokens = response_text.split()

            # Check PRESIDENT declaration requirement
            if task_level == "CRITICAL":
                president_valid = await self.monitor.validate_president_declaration()
                if not president_valid:
                    return {
                        "allowed": False,
                        "error": "CRITICAL task requires valid PRESIDENT declaration",
                        "required_action": "Execute: make declare-president",
                    }

            # Enforce policy through Reference Monitor
            decision = await self.monitor.enforce_token_sequence(tokens, task_level)

            if decision.verdict == PolicyVerdict.DENY:
                return {
                    "allowed": False,
                    "error": f"Policy violation detected (Constitutional AI score: {decision.constitutional_ai_score:.2f})",
                    "reasoning_trace": decision.reasoning_trace_id,
                }

            elif decision.verdict == PolicyVerdict.TRANSFORM:
                return {
                    "allowed": True,
                    "response": " ".join(decision.allowed_tokens),
                    "transformed": True,
                    "reasoning_trace": decision.reasoning_trace_id,
                }

            else:  # ALLOW
                return {
                    "allowed": True,
                    "response": response_text,
                    "constitutional_score": decision.constitutional_ai_score,
                    "reasoning_trace": decision.reasoning_trace_id,
                }

        except Exception as e:
            self.logger.error(f"Hook integration error: {e}")
            # Fail safe - allow response but log error
            return {
                "allowed": True,
                "response": response_text,
                "error": f"Hook error: {e}",
            }

    async def thinking_enforcement_hook(
        self, response_text: str, task_level: str
    ) -> bool:
        """
        Enforce thinking tags based on task level
        Returns True if thinking requirements are met
        """

        import re

        # CRITICAL tasks must have thinking tags
        if task_level == "CRITICAL":
            if not re.search(r"<thinking>.*?</thinking>", response_text, re.DOTALL):
                return False

            # Should also have ULTRATHINK for complex analysis
            if not re.search(r"<ultrathink>.*?</ultrathink>", response_text, re.DOTALL):
                self.logger.warning("CRITICAL task should use ULTRATHINK")
                # Don't block, but warn

        # HIGH tasks should have thinking tags
        elif task_level == "HIGH":
            if not re.search(r"<thinking>.*?</thinking>", response_text, re.DOTALL):
                self.logger.warning("HIGH task should have thinking tags")

        return True

    async def session_initialization_hook(
        self, session_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Session initialization enforcement
        Called at start of each Claude Code session
        """

        results = {
            "president_declaration": False,
            "claude_md_validation": False,
            "database_connections": False,
            "ai_organization": False,
            "errors": [],
        }

        try:
            # 1. Check PRESIDENT declaration
            president_valid = await self.monitor.validate_president_declaration()
            results["president_declaration"] = president_valid

            if not president_valid:
                results["errors"].append(
                    "PRESIDENT declaration not executed or expired"
                )

            # 2. Validate CLAUDE.md structure
            claude_md_path = project_root / "CLAUDE.md"
            if claude_md_path.exists():
                # Run validation script
                import subprocess

                validation_result = subprocess.run(
                    [
                        sys.executable,
                        str(project_root / "scripts" / "validate_claude_md.py"),
                    ],
                    capture_output=True,
                    text=True,
                )

                results["claude_md_validation"] = validation_result.returncode == 0
                if validation_result.returncode != 0:
                    results["errors"].append(
                        f"CLAUDE.md validation failed: {validation_result.stderr}"
                    )
            else:
                results["errors"].append("CLAUDE.md not found")

            # 3. Check database connections
            try:
                # SQLite check
                sqlite_path = project_root / "runtime" / "memory" / "user_prompts.db"
                results["sqlite_available"] = sqlite_path.exists()

                # PostgreSQL check
                import psycopg2

                try:
                    conn = psycopg2.connect(
                        host="localhost",
                        database="coding_rule2_ai",
                        user="dd",
                        password="",
                        port=5432,
                        connect_timeout=5,
                    )
                    conn.close()
                    results["postgresql_available"] = True
                except Exception:
                    results["postgresql_available"] = False
                    results["errors"].append("PostgreSQL connection failed")

                results["database_connections"] = results.get(
                    "sqlite_available", False
                ) and results.get("postgresql_available", False)

            except Exception as e:
                results["errors"].append(f"Database check error: {e}")

            # 4. Check AI organization status (o3 + Gemini)
            try:
                # Check API keys
                openai_key = os.getenv("OPENAI_API_KEY")
                gemini_key = os.getenv("GEMINI_API_KEY")

                results["openai_available"] = bool(openai_key)
                results["gemini_available"] = bool(gemini_key)
                results["ai_organization"] = bool(openai_key and gemini_key)

                if not results["ai_organization"]:
                    results["errors"].append(
                        "AI organization incomplete - missing API keys"
                    )

            except Exception as e:
                results["errors"].append(f"AI organization check error: {e}")

        except Exception as e:
            results["errors"].append(f"Session initialization error: {e}")

        return results

    async def emergency_bypass(self, bypass_code: str, reason: str) -> bool:
        """
        Emergency bypass for critical situations
        Requires valid bypass code and justification
        """

        # Check bypass code
        if bypass_code not in self.bypass_codes:
            self.logger.error(f"Invalid bypass code attempted: {bypass_code}")
            return False

        # Log bypass usage
        self.logger.warning(f"Emergency bypass activated: {reason}")

        # Store bypass record
        bypass_record = {
            "timestamp": datetime.now().isoformat(),
            "bypass_code": bypass_code,
            "reason": reason,
            "session_id": os.getenv("CLAUDE_SESSION_ID", "unknown"),
        }

        bypass_log = project_root / "runtime" / "enforcement" / "bypass_log.json"
        bypass_log.parent.mkdir(parents=True, exist_ok=True)

        if bypass_log.exists():
            with open(bypass_log) as f:
                log_data = json.load(f)
        else:
            log_data = []

        log_data.append(bypass_record)

        with open(bypass_log, "w") as f:
            json.dump(log_data, f, indent=2)

        return True

    def disable_hooks(self, reason: str = "Manual disable"):
        """Disable hook enforcement (emergency use only)"""
        self.hooks_enabled = False
        self.logger.warning(f"Hooks disabled: {reason}")

    def enable_hooks(self):
        """Re-enable hook enforcement"""
        self.hooks_enabled = True
        self.logger.info("Hooks re-enabled")

    async def get_hook_status(self) -> Dict[str, Any]:
        """Get current hook system status"""

        stats = await self.monitor.get_enforcement_statistics()

        return {
            "hooks_enabled": self.hooks_enabled,
            "reference_monitor_stats": stats,
            "bypass_codes_count": len(self.bypass_codes),
            "policy_version": self.monitor.policy_version,
        }


async def main():
    """Test hook integration"""

    print("🔗 Hook Integration - Claude Code強制実行システムテスト")
    print("=" * 60)

    hook_integration = HookIntegration()

    # Test 1: Session initialization
    print("\n🧪 Test 1: Session initialization check")
    session_result = await hook_integration.session_initialization_hook({})
    print(json.dumps(session_result, indent=2))

    # Test 2: Pre-response hook with CRITICAL task
    print("\n🧪 Test 2: Pre-response hook - CRITICAL task")
    test_response = "<thinking>This is a critical analysis</thinking>Final response"
    context = {"task_level": "CRITICAL"}

    hook_result = await hook_integration.pre_response_hook(test_response, context)
    print(json.dumps(hook_result, indent=2))

    # Test 3: Thinking enforcement
    print("\n🧪 Test 3: Thinking enforcement")
    thinking_ok = await hook_integration.thinking_enforcement_hook(
        test_response, "CRITICAL"
    )
    print(f"Thinking requirements met: {thinking_ok}")

    # Test 4: Hook status
    print("\n📊 Hook Status:")
    status = await hook_integration.get_hook_status()
    print(json.dumps(status, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
