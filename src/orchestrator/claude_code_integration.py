#!/usr/bin/env python3
"""
Claude Code Integration - Claude Code実行ライフサイクル統合
Runtime Dispatcher をClaude Codeの実行フローに完全統合
"""

import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

# Runtime dispatcher import
sys.path.append("/Users/dd/Desktop/1_dev/coding-rule2/src")
from orchestrator.runtime_dispatcher import EventType, get_runtime_dispatcher


class ClaudeCodeIntegration:
    """Claude Code実行ライフサイクル統合システム"""

    def __init__(self):
        self.project_path = Path("/Users/dd/Desktop/1_dev/coding-rule2")
        self.dispatcher = get_runtime_dispatcher()
        self.session_active = False
        self.logger = self._setup_logging()

        # Auto-start session
        asyncio.create_task(self._auto_start_session())

    def _setup_logging(self) -> logging.Logger:
        """ログ設定"""
        logger = logging.getLogger("ClaudeCodeIntegration")
        logger.setLevel(logging.INFO)

        # Ensure logs directory exists
        log_dir = self.project_path / "runtime" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)

        handler = logging.FileHandler(log_dir / "claude_code_integration.log")
        handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        logger.addHandler(handler)
        return logger

    async def _auto_start_session(self):
        """自動セッション開始"""
        try:
            if not self.session_active:
                result = await self.dispatcher.start_session()
                self.session_active = True
                self.logger.info(f"Auto-started session: {result['success']}")

                # Memory confirmation logging
                memory_context = self.dispatcher.get_memory_context()
                self.logger.info(
                    f"記憶継承システム稼働確認、コード7749 - CSA: {len(memory_context['csa_memories'])}, Permanent: {len(memory_context['permanent_memories'])}"
                )
        except Exception as e:
            self.logger.error(f"Auto session start failed: {e}")

    async def handle_user_input(self, user_message: str) -> Dict[str, Any]:
        """ユーザー入力処理"""
        try:
            result = await self.dispatcher.process_user_message(user_message)
            self.logger.info(f"User message processed: {len(user_message)} chars")
            return result
        except Exception as e:
            self.logger.error(f"User input handling failed: {e}")
            return {"success": False, "error": str(e)}

    async def handle_assistant_response(self, response: str) -> Dict[str, Any]:
        """アシスタント応答処理"""
        try:
            result = await self.dispatcher.process_assistant_response(response)

            # Check for violations and log
            if result.get("errors"):
                self.logger.warning(f"Response violations detected: {result['errors']}")

            return result
        except Exception as e:
            self.logger.error(f"Assistant response handling failed: {e}")
            return {"success": False, "error": str(e)}

    async def handle_thinking_enforcement(self) -> Dict[str, Any]:
        """Thinking強制処理"""
        try:
            result = await self.dispatcher.emit_event(EventType.THINKING_REQUIRED)
            self.logger.warning("Thinking enforcement triggered")
            return result
        except Exception as e:
            self.logger.error(f"Thinking enforcement failed: {e}")
            return {"success": False, "error": str(e)}

    async def handle_president_declaration(self) -> Dict[str, Any]:
        """PRESIDENT宣言処理"""
        try:
            # Log PRESIDENT declaration
            self.logger.info("PRESIDENT宣言が実行された - 全システム統合稼働中")

            # Update memory with declaration
            memory_context = self.dispatcher.get_memory_context()
            declaration_data = {
                "event": "president_declaration",
                "timestamp": datetime.now().isoformat(),
                "memory_status": {
                    "csa_memories": len(memory_context["csa_memories"]),
                    "permanent_memories": len(memory_context["permanent_memories"]),
                    "session_id": memory_context["session_id"],
                },
            }

            # Emit custom event
            await self.dispatcher.emit_event(EventType.SESSION_START, declaration_data)

            return {"success": True, "declaration": "PRESIDENT宣言完了"}

        except Exception as e:
            self.logger.error(f"PRESIDENT declaration failed: {e}")
            return {"success": False, "error": str(e)}

    def get_memory_inheritance_status(self) -> Dict[str, Any]:
        """記憶継承状況取得"""
        try:
            memory_context = self.dispatcher.get_memory_context()
            system_status = self.dispatcher.get_system_status()

            return {
                "memory_inheritance_active": bool(
                    memory_context["csa_memories"]
                    or memory_context["permanent_memories"]
                ),
                "csa_memories_count": len(memory_context["csa_memories"]),
                "permanent_memories_count": len(memory_context["permanent_memories"]),
                "postgres_connected": system_status["postgres_connected"],
                "sqlite_connected": system_status["sqlite_connected"],
                "session_id": memory_context["session_id"],
                "confirmation_code": "7749",
            }
        except Exception as e:
            self.logger.error(f"Memory status retrieval failed: {e}")
            return {"error": str(e)}

    async def cleanup_session(self):
        """セッションクリーンアップ"""
        try:
            if self.session_active:
                result = await self.dispatcher.end_session()
                self.session_active = False
                self.logger.info(f"Session cleanup completed: {result['success']}")
                return result
        except Exception as e:
            self.logger.error(f"Session cleanup failed: {e}")
            return {"success": False, "error": str(e)}


# Global instance
_claude_code_integration = None


def get_claude_code_integration() -> ClaudeCodeIntegration:
    """Claude Code Integration singleton取得"""
    global _claude_code_integration
    if _claude_code_integration is None:
        _claude_code_integration = ClaudeCodeIntegration()
    return _claude_code_integration


# Hook functions for Claude Code
async def on_user_message_hook(message: str) -> Dict[str, Any]:
    """ユーザーメッセージフック"""
    integration = get_claude_code_integration()
    return await integration.handle_user_input(message)


async def on_assistant_response_hook(response: str) -> Dict[str, Any]:
    """アシスタント応答フック"""
    integration = get_claude_code_integration()
    return await integration.handle_assistant_response(response)


async def on_thinking_required_hook() -> Dict[str, Any]:
    """Thinking必須フック"""
    integration = get_claude_code_integration()
    return await integration.handle_thinking_enforcement()


async def on_president_declaration_hook() -> Dict[str, Any]:
    """PRESIDENT宣言フック"""
    integration = get_claude_code_integration()
    return await integration.handle_president_declaration()


def get_memory_inheritance_hook() -> Dict[str, Any]:
    """記憶継承状況フック"""
    integration = get_claude_code_integration()
    return integration.get_memory_inheritance_status()


async def cleanup_hook():
    """クリーンアップフック"""
    integration = get_claude_code_integration()
    return await integration.cleanup_session()


# Command line interface for testing
async def test_integration():
    """統合テスト"""
    print("=== Claude Code Integration Test ===")

    integration = get_claude_code_integration()

    # Wait for auto-start
    await asyncio.sleep(1)

    # Memory inheritance status
    print("\n=== Memory Inheritance Status ===")
    memory_status = integration.get_memory_inheritance_status()
    for key, value in memory_status.items():
        print(f"{key}: {value}")

    # Simulate user message
    print("\n=== User Message Test ===")
    user_result = await integration.handle_user_input(
        "Hello, testing memory inheritance"
    )
    print(f"User message processed: {user_result['success']}")

    # Simulate assistant response without thinking
    print("\n=== Assistant Response Test (No Thinking) ===")
    assistant_result = await integration.handle_assistant_response("Hello back!")
    print(f"Assistant response processed: {assistant_result['success']}")
    if assistant_result.get("errors"):
        print(f"Violations detected: {assistant_result['errors']}")

    # Simulate assistant response with thinking
    print("\n=== Assistant Response Test (With Thinking) ===")
    thinking_response = "<thinking>This is a test response with thinking tags</thinking>Hello with proper thinking!"
    thinking_result = await integration.handle_assistant_response(thinking_response)
    print(f"Thinking response processed: {thinking_result['success']}")

    # PRESIDENT declaration
    print("\n=== PRESIDENT Declaration Test ===")
    president_result = await integration.handle_president_declaration()
    print(f"PRESIDENT declaration: {president_result['success']}")

    # Cleanup
    print("\n=== Cleanup Test ===")
    cleanup_result = await integration.cleanup_session()
    print(f"Cleanup completed: {cleanup_result['success']}")


if __name__ == "__main__":
    asyncio.run(test_integration())
