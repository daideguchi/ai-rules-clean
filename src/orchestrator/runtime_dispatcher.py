#!/usr/bin/env python3
"""
Runtime Dispatcher - 実行時オーケストレーター
全システムの統合実行を管理する中央ディスパッチャー
"""

import asyncio
import logging
import os
import sqlite3

# Memory system imports
import sys
import threading
import traceback
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Database integrations
import psycopg2
from psycopg2.extras import RealDictCursor

sys.path.append("/Users/dd/Desktop/1_dev/coding-rule2/src")
from ai.constitutional_ai import ConstitutionalAI
from ai.continuous_improvement import ContinuousImprovementSystem
from ai.multi_agent_monitor import MultiAgentMonitor
from ai.nist_ai_rmf import NISTAIRiskManagement
from ai.rule_based_rewards import RuleBasedRewards
from conductor.core import ConductorCore
from memory.breakthrough_memory_system import BreakthroughMemorySystem
from memory.unified_memory_manager import UnifiedMemoryManager


class EventType(Enum):
    SESSION_START = "session_start"
    USER_MESSAGE = "user_message"
    MODEL_CALL = "model_call"
    ASSISTANT_RESPONSE = "assistant_response"
    SESSION_END = "session_end"
    THINKING_REQUIRED = "thinking_required"
    MEMORY_INHERITANCE = "memory_inheritance"
    VIOLATION_DETECTED = "violation_detected"


@dataclass
class ConversationContext:
    """会話コンテキスト"""

    session_id: str
    user_id: str = "default_user"
    project_path: str = "/Users/dd/Desktop/1_dev/coding-rule2"
    conversation_history: List[Dict] = field(default_factory=list)
    memory_cache: Dict[str, Any] = field(default_factory=dict)
    violation_count: int = 0
    active_plugins: List[str] = field(default_factory=list)
    postgres_connected: bool = False
    sqlite_connected: bool = False
    timestamp: datetime = field(default_factory=datetime.now)


class Plugin:
    """プラグインベースクラス"""

    def __init__(self, name: str):
        self.name = name
        self.enabled = True
        self.priority = 5  # 1-10, 10が最高優先度

    async def handle_event(
        self, event: EventType, context: ConversationContext
    ) -> Tuple[bool, Optional[str]]:
        """イベント処理 - 戻り値: (success, error_message)"""
        return True, None


class RuntimeDispatcher:
    """実行時ディスパッチャー - 全システムの統合実行管理"""

    def __init__(self, project_path: str = "/Users/dd/Desktop/1_dev/coding-rule2"):
        self.project_path = Path(project_path)
        self.session_id = str(uuid.uuid4())
        self.context = ConversationContext(session_id=self.session_id)
        self.plugins: Dict[EventType, List[Plugin]] = {event: [] for event in EventType}
        self.logger = self._setup_logging()
        self.lock = threading.Lock()

        # Database connections
        self.postgres_conn = None
        self.sqlite_conn = None

        # System integrations
        self.memory_manager = None
        self.breakthrough_memory = None
        self.constitutional_ai = None
        self.rule_based_rewards = None
        self.multi_agent_monitor = None
        self.nist_rmf = None
        self.continuous_improvement = None
        self.conductor = None

        # Initialize systems
        self._initialize_systems()

    def _setup_logging(self) -> logging.Logger:
        """ログ設定"""
        logger = logging.getLogger("RuntimeDispatcher")
        logger.setLevel(logging.INFO)

        handler = logging.FileHandler(
            self.project_path / "runtime" / "logs" / "runtime_dispatcher.log"
        )
        handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        logger.addHandler(handler)
        return logger

    def _initialize_systems(self):
        """システム初期化"""
        try:
            # Database connections
            self._connect_databases()

            # Memory systems
            self.memory_manager = UnifiedMemoryManager()
            self.breakthrough_memory = BreakthroughMemorySystem()

            # AI systems
            self.constitutional_ai = ConstitutionalAI()
            self.rule_based_rewards = RuleBasedRewards()
            self.multi_agent_monitor = MultiAgentMonitor()
            self.nist_rmf = NISTAIRiskManagement()
            self.continuous_improvement = ContinuousImprovementSystem()

            # Conductor system
            self.conductor = ConductorCore()

            # Register core plugins
            self._register_core_plugins()

            self.logger.info(
                f"Runtime dispatcher initialized - Session: {self.session_id}"
            )

        except Exception as e:
            self.logger.error(f"System initialization failed: {e}")
            self.logger.error(traceback.format_exc())

    def _connect_databases(self):
        """データベース接続"""
        try:
            # PostgreSQL connection
            self.postgres_conn = psycopg2.connect(
                host=os.getenv("DB_HOST", "localhost"),
                database=os.getenv("DB_NAME", "coding_rule2_ai"),
                user=os.getenv("DB_USER", "postgres"),
                password=os.getenv("DB_PASSWORD", ""),
                port=os.getenv("DB_PORT", "5432"),
                cursor_factory=RealDictCursor,
            )
            self.context.postgres_connected = True
            self.logger.info("PostgreSQL connected")

            # SQLite connection
            sqlite_path = self.project_path / "runtime" / "memory" / "forever_ledger.db"
            self.sqlite_conn = sqlite3.connect(
                str(sqlite_path), check_same_thread=False
            )
            self.context.sqlite_connected = True
            self.logger.info("SQLite connected")

        except Exception as e:
            self.logger.error(f"Database connection failed: {e}")

    def _ensure_sqlite_connection(self):
        """SQLite接続確保"""
        try:
            if self.sqlite_conn is None:
                sqlite_path = (
                    self.project_path / "runtime" / "memory" / "forever_ledger.db"
                )
                self.sqlite_conn = sqlite3.connect(
                    str(sqlite_path), check_same_thread=False
                )
                self.context.sqlite_connected = True
                self.logger.info("SQLite reconnected")
                return True

            # Test connection
            cursor = self.sqlite_conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            return True

        except Exception as e:
            self.logger.warning(f"SQLite connection test failed: {e}")
            try:
                sqlite_path = (
                    self.project_path / "runtime" / "memory" / "forever_ledger.db"
                )
                self.sqlite_conn = sqlite3.connect(
                    str(sqlite_path), check_same_thread=False
                )
                self.context.sqlite_connected = True
                self.logger.info("SQLite reconnected after failure")
                return True
            except Exception as e2:
                self.logger.error(f"SQLite reconnection failed: {e2}")
                self.context.sqlite_connected = False
                return False

    def _register_core_plugins(self):
        """コアプラグイン登録"""

        # Memory inheritance plugin
        class MemoryInheritancePlugin(Plugin):
            def __init__(self, dispatcher):
                super().__init__("MemoryInheritance")
                self.dispatcher = dispatcher
                self.priority = 10

            async def handle_event(
                self, event: EventType, context: ConversationContext
            ) -> Tuple[bool, Optional[str]]:
                if event == EventType.SESSION_START:
                    return await self._load_session_memory(context)
                elif event == EventType.SESSION_END:
                    return await self._save_session_memory(context)
                return True, None

            async def _load_session_memory(
                self, context: ConversationContext
            ) -> Tuple[bool, Optional[str]]:
                try:
                    # Load from PostgreSQL CSA
                    if self.dispatcher.postgres_conn:
                        cursor = self.dispatcher.postgres_conn.cursor()
                        cursor.execute("""
                            SELECT content, emotional_context, learning_weight, metadata
                            FROM context_stream
                            WHERE importance_level = 'high'
                            ORDER BY created_at DESC
                            LIMIT 20
                        """)
                        csa_memories = cursor.fetchall()
                        context.memory_cache["csa_memories"] = csa_memories

                    # Load from SQLite permanent ledger
                    if self.dispatcher.sqlite_conn:
                        cursor = self.dispatcher.sqlite_conn.cursor()
                        cursor.execute("""
                            SELECT text, importance
                            FROM forever
                            ORDER BY importance DESC, created_at DESC
                            LIMIT 10
                        """)
                        permanent_memories = cursor.fetchall()
                        context.memory_cache["permanent_memories"] = permanent_memories

                    self.dispatcher.logger.info(
                        f"Memory inheritance loaded: {len(csa_memories)} CSA + {len(permanent_memories)} permanent"
                    )
                    return True, None

                except Exception as e:
                    return False, f"Memory inheritance loading failed: {e}"

            async def _save_session_memory(
                self, context: ConversationContext
            ) -> Tuple[bool, Optional[str]]:
                try:
                    # Save conversation summary to PostgreSQL
                    if self.dispatcher.postgres_conn and context.conversation_history:
                        cursor = self.dispatcher.postgres_conn.cursor()
                        summary = f"Session {context.session_id[:8]} completed with {len(context.conversation_history)} exchanges"
                        cursor.execute(
                            """
                            INSERT INTO context_stream (
                                id, timestamp, source, event_type, content,
                                session_id, project_name, importance_level,
                                emotional_context, learning_weight, metadata
                            ) VALUES (
                                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                            )
                        """,
                            (
                                str(uuid.uuid4()),
                                datetime.now(),
                                "runtime_dispatcher",
                                "session_completion",
                                summary,
                                context.session_id,
                                "coding-rule2",
                                "high",
                                {"summary": True},
                                0.8,
                                {
                                    "conversation_length": len(
                                        context.conversation_history
                                    )
                                },
                            ),
                        )
                        self.dispatcher.postgres_conn.commit()

                    return True, None

                except Exception as e:
                    return False, f"Memory inheritance saving failed: {e}"

        # Thinking enforcement plugin
        class ThinkingEnforcementPlugin(Plugin):
            def __init__(self, dispatcher):
                super().__init__("ThinkingEnforcement")
                self.dispatcher = dispatcher
                self.priority = 9

            async def handle_event(
                self, event: EventType, context: ConversationContext
            ) -> Tuple[bool, Optional[str]]:
                if event == EventType.THINKING_REQUIRED:
                    return await self._enforce_thinking(context)
                return True, None

            async def _enforce_thinking(
                self, context: ConversationContext
            ) -> Tuple[bool, Optional[str]]:
                try:
                    # Ensure SQLite connection
                    if not self.dispatcher._ensure_sqlite_connection():
                        return False, "SQLite connection failed"

                    # Record thinking violation
                    cursor = self.dispatcher.sqlite_conn.cursor()
                    cursor.execute(
                        """
                        INSERT OR REPLACE INTO violations (violation_type, count, last_occurrence)
                        VALUES ('thinking_required',
                               COALESCE((SELECT count FROM violations WHERE violation_type = 'thinking_required'), 0) + 1,
                               ?)
                    """,
                        (datetime.now().isoformat(),),
                    )
                    self.dispatcher.sqlite_conn.commit()

                    context.violation_count += 1
                    self.dispatcher.logger.warning(
                        f"Thinking requirement violation detected - count: {context.violation_count}"
                    )

                    return True, "Thinking tags are mandatory for all responses"

                except Exception as e:
                    return False, f"Thinking enforcement failed: {e}"

        # Constitutional AI plugin
        class ConstitutionalAIPlugin(Plugin):
            def __init__(self, dispatcher):
                super().__init__("ConstitutionalAI")
                self.dispatcher = dispatcher
                self.priority = 8

            async def handle_event(
                self, event: EventType, context: ConversationContext
            ) -> Tuple[bool, Optional[str]]:
                if event == EventType.VIOLATION_DETECTED:
                    return await self._handle_violation(context)
                return True, None

            async def _handle_violation(
                self, context: ConversationContext
            ) -> Tuple[bool, Optional[str]]:
                try:
                    if self.dispatcher.constitutional_ai:
                        result = self.dispatcher.constitutional_ai.evaluate_response(
                            "Response under review"
                        )
                        if result.get("violation_detected"):
                            self.dispatcher.logger.warning(
                                f"Constitutional violation: {result.get('violation_type')}"
                            )
                            return (
                                True,
                                f"Constitutional violation detected: {result.get('violation_type')}",
                            )

                    return True, None

                except Exception as e:
                    return False, f"Constitutional AI evaluation failed: {e}"

        # Register plugins
        memory_plugin = MemoryInheritancePlugin(self)
        thinking_plugin = ThinkingEnforcementPlugin(self)
        constitutional_plugin = ConstitutionalAIPlugin(self)

        self.plugins[EventType.SESSION_START].append(memory_plugin)
        self.plugins[EventType.SESSION_END].append(memory_plugin)
        self.plugins[EventType.THINKING_REQUIRED].append(thinking_plugin)
        self.plugins[EventType.VIOLATION_DETECTED].append(constitutional_plugin)

        self.logger.info("Core plugins registered")

    async def emit_event(
        self, event: EventType, data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """イベント発火"""
        with self.lock:
            results = {
                "event": event.value,
                "timestamp": datetime.now().isoformat(),
                "session_id": self.session_id,
                "plugins_executed": [],
                "errors": [],
                "success": True,
            }

            # Update context
            if data:
                if event == EventType.USER_MESSAGE:
                    self.context.conversation_history.append(
                        {
                            "type": "user",
                            "content": data.get("content", ""),
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
                elif event == EventType.ASSISTANT_RESPONSE:
                    self.context.conversation_history.append(
                        {
                            "type": "assistant",
                            "content": data.get("content", ""),
                            "timestamp": datetime.now().isoformat(),
                        }
                    )

            # Execute plugins for this event
            plugins = self.plugins.get(event, [])
            plugins.sort(key=lambda p: p.priority, reverse=True)

            for plugin in plugins:
                if not plugin.enabled:
                    continue

                try:
                    success, error_message = await plugin.handle_event(
                        event, self.context
                    )
                    results["plugins_executed"].append(
                        {
                            "name": plugin.name,
                            "success": success,
                            "error": error_message,
                        }
                    )

                    if not success:
                        results["errors"].append(f"{plugin.name}: {error_message}")
                        results["success"] = False

                except Exception as e:
                    error_msg = f"{plugin.name}: {str(e)}"
                    results["errors"].append(error_msg)
                    results["success"] = False
                    self.logger.error(f"Plugin {plugin.name} failed: {e}")

            self.logger.info(
                f"Event {event.value} processed - {len(plugins)} plugins executed"
            )
            return results

    async def start_session(self, user_id: str = "default_user") -> Dict[str, Any]:
        """セッション開始"""
        self.context.user_id = user_id
        self.logger.info(
            f"Session started - User: {user_id}, Session: {self.session_id}"
        )

        # Emit session start event
        result = await self.emit_event(EventType.SESSION_START)

        # Log memory inheritance confirmation
        csa_count = len(self.context.memory_cache.get("csa_memories", []))
        permanent_count = len(self.context.memory_cache.get("permanent_memories", []))

        self.logger.info(
            f"Memory inheritance loaded - CSA: {csa_count}, Permanent: {permanent_count}"
        )

        return result

    async def end_session(self) -> Dict[str, Any]:
        """セッション終了"""
        self.logger.info(
            f"Session ending - {len(self.context.conversation_history)} exchanges"
        )

        result = await self.emit_event(EventType.SESSION_END)

        # Don't close database connections to allow reuse
        # Only close on explicit cleanup or when process ends
        self.logger.info("Session ended - database connections kept open for reuse")

        return result

    def cleanup_connections(self):
        """明示的な接続クリーンアップ"""
        try:
            if self.postgres_conn:
                self.postgres_conn.close()
                self.postgres_conn = None
                self.context.postgres_connected = False
                self.logger.info("PostgreSQL connection closed")

            if self.sqlite_conn:
                self.sqlite_conn.close()
                self.sqlite_conn = None
                self.context.sqlite_connected = False
                self.logger.info("SQLite connection closed")

        except Exception as e:
            self.logger.error(f"Connection cleanup failed: {e}")

    async def process_user_message(self, message: str) -> Dict[str, Any]:
        """ユーザーメッセージ処理"""
        return await self.emit_event(EventType.USER_MESSAGE, {"content": message})

    async def process_assistant_response(self, response: str) -> Dict[str, Any]:
        """アシスタント応答処理"""
        # Check for thinking tags
        if not response.startswith("<thinking>"):
            await self.emit_event(EventType.THINKING_REQUIRED)

        return await self.emit_event(
            EventType.ASSISTANT_RESPONSE, {"content": response}
        )

    def get_memory_context(self) -> Dict[str, Any]:
        """記憶コンテキスト取得"""
        return {
            "session_id": self.session_id,
            "csa_memories": self.context.memory_cache.get("csa_memories", []),
            "permanent_memories": self.context.memory_cache.get(
                "permanent_memories", []
            ),
            "conversation_history": self.context.conversation_history,
            "violation_count": self.context.violation_count,
        }

    def get_system_status(self) -> Dict[str, Any]:
        """システム状態取得"""
        return {
            "session_id": self.session_id,
            "postgres_connected": self.context.postgres_connected,
            "sqlite_connected": self.context.sqlite_connected,
            "active_plugins": len(
                [p for plugins in self.plugins.values() for p in plugins if p.enabled]
            ),
            "memory_loaded": bool(self.context.memory_cache),
            "conversation_length": len(self.context.conversation_history),
            "violation_count": self.context.violation_count,
        }


# Singleton instance
_runtime_dispatcher = None


def get_runtime_dispatcher() -> RuntimeDispatcher:
    """Runtime Dispatcher singleton取得"""
    global _runtime_dispatcher
    if _runtime_dispatcher is None:
        _runtime_dispatcher = RuntimeDispatcher()
    return _runtime_dispatcher


async def main():
    """テスト実行"""
    dispatcher = get_runtime_dispatcher()

    # セッション開始
    print("=== Session Start ===")
    start_result = await dispatcher.start_session()
    print(f"Session started: {start_result['success']}")

    # メモリ状態確認
    print("\n=== Memory Status ===")
    memory_context = dispatcher.get_memory_context()
    print(f"CSA memories: {len(memory_context['csa_memories'])}")
    print(f"Permanent memories: {len(memory_context['permanent_memories'])}")

    # システム状態確認
    print("\n=== System Status ===")
    system_status = dispatcher.get_system_status()
    for key, value in system_status.items():
        print(f"{key}: {value}")

    # セッション終了
    print("\n=== Session End ===")
    end_result = await dispatcher.end_session()
    print(f"Session ended: {end_result['success']}")


if __name__ == "__main__":
    asyncio.run(main())
