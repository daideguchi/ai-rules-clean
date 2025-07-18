#!/usr/bin/env python3
"""
🧠 Enhanced Memory Inheritance System v3.0
===========================================
Advanced memory inheritance system for perfect session continuity
"""

import hashlib
import json
import logging
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# For vector similarity if available
try:
    import numpy as np
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    VECTOR_AVAILABLE = True
except ImportError:
    VECTOR_AVAILABLE = False

# For PostgreSQL if available
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False


@dataclass
class MemoryEntry:
    """Enhanced memory entry with metadata"""
    key: str
    content: str
    timestamp: datetime
    importance: int  # 1-10 scale
    category: str
    tags: List[str]
    context_hash: str
    violation_count: int = 0
    last_accessed: Optional[datetime] = None
    access_count: int = 0


class EnhancedMemoryInheritance:
    """
    Enhanced Memory Inheritance System with:
    - Multi-layer memory storage
    - Intelligent context retrieval
    - Violation tracking and prevention
    - Session continuity guarantee
    - Vector similarity search
    - Automatic importance scoring
    """

    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path("/Users/dd/Desktop/1_dev/coding-rule2")
        self.memory_dir = self.project_root / "runtime" / "memory"
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        # Memory verification
        self.verification_phrase = "記憶継承システム稼働確認、コード7749"
        self.verification_numbers = [2847, 9163, 5491]

        # Initialize storage layers
        self._init_logging()
        self._init_persistent_storage()
        self._init_session_storage()
        self._init_vector_storage()

        # Load critical memories
        self._load_critical_memories()

        self.logger.info("🧠 Enhanced Memory Inheritance System v3.0 initialized")

    def _init_persistent_storage(self):
        """Initialize persistent SQLite storage"""
        self.db_path = self.memory_dir / "enhanced_memory.db"
        self.db = sqlite3.connect(str(self.db_path), isolation_level=None)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA synchronous=NORMAL")

        # Create enhanced memory table
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS memory_entries (
                key TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                importance INTEGER DEFAULT 5,
                category TEXT DEFAULT 'general',
                tags TEXT DEFAULT '[]',
                context_hash TEXT,
                violation_count INTEGER DEFAULT 0,
                last_accessed TEXT,
                access_count INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # Create indexes for fast retrieval
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_importance ON memory_entries(importance)")
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_category ON memory_entries(category)")
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_violation_count ON memory_entries(violation_count)")
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_last_accessed ON memory_entries(last_accessed)")

        # Create violation tracking table
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS violations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                violation_type TEXT NOT NULL,
                description TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                session_id TEXT,
                resolved BOOLEAN DEFAULT FALSE
            )
        """)

        # Create session continuity table
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS session_continuity (
                session_id TEXT PRIMARY KEY,
                start_time TEXT NOT NULL,
                end_time TEXT,
                memory_snapshot TEXT NOT NULL,
                critical_reminders TEXT NOT NULL,
                violation_summary TEXT DEFAULT '{}',
                status TEXT DEFAULT 'active'
            )
        """)

    def _init_session_storage(self):
        """Initialize current session storage"""
        self.session_id = str(uuid.uuid4())
        self.session_start = datetime.now(timezone.utc)
        self.session_memory = {}
        self.session_violations = []
        self.session_reminders = []

        # Load previous session if exists
        self._load_previous_session()

    def _init_vector_storage(self):
        """Initialize vector similarity search if available"""
        global VECTOR_AVAILABLE
        if VECTOR_AVAILABLE:
            try:
                self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
                self.vector_index = {}
                self.logger.info("✅ Vector similarity search enabled")
            except Exception as e:
                self.logger.warning(f"⚠️ Vector search initialization failed: {e}")
                VECTOR_AVAILABLE = False
        else:
            self.sentence_model = None
            self.vector_index = {}

    def _init_logging(self):
        """Initialize enhanced logging"""
        self.logger = logging.getLogger("enhanced_memory")
        self.logger.setLevel(logging.INFO)

        # Create log file
        log_file = self.memory_dir / "memory_inheritance.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(file_handler)

    def _load_critical_memories(self):
        """Load critical memories that must never be forgotten"""
        critical_memories = {
            "NO_SPECSTORY": {
                "content": "specstoryフォルダには絶対に触らない。1000回指示済み。",
                "importance": 10,
                "category": "critical_rule",
                "tags": ["specstory", "forbidden", "file_system"]
            },
            "THINKING_MANDATORY": {
                "content": "thinkingタグは毎回必須。例外なし。",
                "importance": 10,
                "category": "critical_rule",
                "tags": ["thinking", "mandatory", "response_format"]
            },
            "PRESIDENT_DECLARATION": {
                "content": "PRESIDENT宣言は作業開始前に必須。make declare-president",
                "importance": 10,
                "category": "critical_rule",
                "tags": ["president", "declaration", "startup"]
            },
            "DYNAMIC_ROLES": {
                "content": "動的役職システム（静的ではない）。4分割ペイン、1+4人構成。",
                "importance": 9,
                "category": "system_design",
                "tags": ["roles", "dynamic", "organization"]
            },
            "LANGUAGE_RULE": {
                "content": "言語ルール：宣言・報告は日本語、処理は英語。",
                "importance": 9,
                "category": "communication",
                "tags": ["language", "japanese", "english"]
            },
            "FILE_PROTECTION": {
                "content": "ファイル削除・移動は慎重に行う。ユーザー許可必須。",
                "importance": 9,
                "category": "file_safety",
                "tags": ["files", "deletion", "safety"]
            },
            "MEMORY_VERIFICATION": {
                "content": f"記憶継承確認フレーズ: {self.verification_phrase}",
                "importance": 10,
                "category": "memory_system",
                "tags": ["verification", "inheritance", "continuity"]
            }
        }

        for key, memory_data in critical_memories.items():
            self.store_memory(
                key=key,
                content=memory_data["content"],
                importance=memory_data["importance"],
                category=memory_data["category"],
                tags=memory_data["tags"]
            )

    def store_memory(self, key: str, content: str, importance: int = 5,
                    category: str = "general", tags: List[str] = None) -> bool:
        """Store a memory entry with enhanced metadata"""
        try:
            tags = tags or []
            now = datetime.now(timezone.utc).isoformat()
            context_hash = hashlib.md5(content.encode()).hexdigest()

            # Generate vector embedding if available
            global VECTOR_AVAILABLE
            if VECTOR_AVAILABLE and self.sentence_model:
                try:
                    embedding = self.sentence_model.encode(content)
                    self.vector_index[key] = embedding
                except Exception as e:
                    self.logger.warning(f"⚠️ Vector embedding failed for {key}: {e}")

            # Store in database
            self.db.execute("""
                INSERT OR REPLACE INTO memory_entries
                (key, content, timestamp, importance, category, tags, context_hash,
                 violation_count, last_accessed, access_count, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?, 0, ?, ?)
            """, (key, content, now, importance, category, json.dumps(tags),
                  context_hash, now, now, now))

            self.logger.info(f"📝 Memory stored: {key} (importance: {importance})")
            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to store memory {key}: {e}")
            return False

    def retrieve_memory(self, key: str, increment_access: bool = True) -> Optional[MemoryEntry]:
        """Retrieve a specific memory entry"""
        try:
            cursor = self.db.execute("""
                SELECT * FROM memory_entries WHERE key = ?
            """, (key,))

            row = cursor.fetchone()
            if not row:
                return None

            # Update access tracking
            if increment_access:
                now = datetime.now(timezone.utc).isoformat()
                self.db.execute("""
                    UPDATE memory_entries
                    SET last_accessed = ?, access_count = access_count + 1
                    WHERE key = ?
                """, (now, key))

            # Parse the row data
            memory_entry = MemoryEntry(
                key=row[0],
                content=row[1],
                timestamp=datetime.fromisoformat(row[2]),
                importance=row[3],
                category=row[4],
                tags=json.loads(row[5]) if row[5] else [],
                context_hash=row[6],
                violation_count=row[7],
                last_accessed=datetime.fromisoformat(row[8]) if row[8] else None,
                access_count=row[9]
            )

            return memory_entry

        except Exception as e:
            self.logger.error(f"❌ Failed to retrieve memory {key}: {e}")
            return None

    def search_memories(self, query: str, limit: int = 10) -> List[MemoryEntry]:
        """Search memories using text similarity and vector search"""
        results = []

        try:
            # Text-based search
            cursor = self.db.execute("""
                SELECT * FROM memory_entries
                WHERE content LIKE ? OR key LIKE ?
                ORDER BY importance DESC, access_count DESC
                LIMIT ?
            """, (f"%{query}%", f"%{query}%", limit))

            for row in cursor.fetchall():
                memory_entry = MemoryEntry(
                    key=row[0],
                    content=row[1],
                    timestamp=datetime.fromisoformat(row[2]),
                    importance=row[3],
                    category=row[4],
                    tags=json.loads(row[5]) if row[5] else [],
                    context_hash=row[6],
                    violation_count=row[7],
                    last_accessed=datetime.fromisoformat(row[8]) if row[8] else None,
                    access_count=row[9]
                )
                results.append(memory_entry)

            # Vector-based search if available
            global VECTOR_AVAILABLE
            if VECTOR_AVAILABLE and self.sentence_model and self.vector_index:
                try:
                    query_embedding = self.sentence_model.encode(query)
                    similarities = []

                    for key, embedding in self.vector_index.items():
                        similarity = cosine_similarity(
                            query_embedding.reshape(1, -1),
                            embedding.reshape(1, -1)
                        )[0][0]
                        similarities.append((key, similarity))

                    # Sort by similarity and add top results
                    similarities.sort(key=lambda x: x[1], reverse=True)
                    for key, _score in similarities[:5]:  # Top 5 vector matches
                        memory = self.retrieve_memory(key, increment_access=False)
                        if memory and memory not in results:
                            results.append(memory)

                except Exception as e:
                    self.logger.warning(f"⚠️ Vector search failed: {e}")

            return results[:limit]

        except Exception as e:
            self.logger.error(f"❌ Memory search failed: {e}")
            return []

    def get_critical_reminders(self) -> List[str]:
        """Get critical reminders that must be displayed every session"""
        reminders = []

        try:
            cursor = self.db.execute("""
                SELECT content FROM memory_entries
                WHERE importance >= 9 AND category = 'critical_rule'
                ORDER BY importance DESC
            """)

            for row in cursor.fetchall():
                reminders.append(row[0])

        except Exception as e:
            self.logger.error(f"❌ Failed to get critical reminders: {e}")

        return reminders

    def record_violation(self, violation_type: str, description: str) -> bool:
        """Record a rule violation"""
        try:
            now = datetime.now(timezone.utc).isoformat()

            # Store violation
            self.db.execute("""
                INSERT INTO violations
                (violation_type, description, timestamp, session_id)
                VALUES (?, ?, ?, ?)
            """, (violation_type, description, now, self.session_id))

            # Update memory entry violation count
            self.db.execute("""
                UPDATE memory_entries
                SET violation_count = violation_count + 1
                WHERE key = ?
            """, (violation_type,))

            self.session_violations.append({
                "type": violation_type,
                "description": description,
                "timestamp": now
            })

            self.logger.warning(f"⚠️ Violation recorded: {violation_type} - {description}")
            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to record violation: {e}")
            return False

    def get_violation_summary(self) -> Dict[str, Any]:
        """Get summary of all violations"""
        try:
            cursor = self.db.execute("""
                SELECT violation_type, COUNT(*) as count, MAX(timestamp) as last_occurrence
                FROM violations
                GROUP BY violation_type
                ORDER BY count DESC
            """)

            violations = {}
            for row in cursor.fetchall():
                violations[row[0]] = {
                    "count": row[1],
                    "last_occurrence": row[2]
                }

            return violations

        except Exception as e:
            self.logger.error(f"❌ Failed to get violation summary: {e}")
            return {}

    def save_session_snapshot(self) -> bool:
        """Save current session state for inheritance"""
        try:
            memory_snapshot = {
                "session_memory": self.session_memory,
                "critical_reminders": self.get_critical_reminders(),
                "verification_phrase": self.verification_phrase,
                "verification_numbers": self.verification_numbers
            }

            violation_summary = self.get_violation_summary()

            datetime.now(timezone.utc).isoformat()

            self.db.execute("""
                INSERT OR REPLACE INTO session_continuity
                (session_id, start_time, memory_snapshot, critical_reminders,
                 violation_summary, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (self.session_id, self.session_start.isoformat(),
                  json.dumps(memory_snapshot), json.dumps(self.get_critical_reminders()),
                  json.dumps(violation_summary), "active"))

            self.logger.info(f"📸 Session snapshot saved: {self.session_id}")
            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to save session snapshot: {e}")
            return False

    def _load_previous_session(self):
        """Load previous session for continuity"""
        try:
            cursor = self.db.execute("""
                SELECT * FROM session_continuity
                WHERE status = 'active'
                ORDER BY start_time DESC
                LIMIT 1
            """)

            row = cursor.fetchone()
            if row:
                memory_snapshot = json.loads(row[2])
                self.session_memory.update(memory_snapshot.get("session_memory", {}))
                self.session_reminders = memory_snapshot.get("critical_reminders", [])

                self.logger.info(f"🔄 Previous session loaded: {row[0]}")

        except Exception as e:
            self.logger.warning(f"⚠️ Failed to load previous session: {e}")

    def verify_memory_inheritance(self) -> Tuple[bool, str]:
        """Verify that memory inheritance is working correctly"""
        try:
            # Check critical memories
            critical_keys = ["NO_SPECSTORY", "THINKING_MANDATORY", "PRESIDENT_DECLARATION"]
            missing_memories = []

            for key in critical_keys:
                memory = self.retrieve_memory(key, increment_access=False)
                if not memory:
                    missing_memories.append(key)

            if missing_memories:
                return False, f"Missing critical memories: {missing_memories}"

            # Check violation history
            violation_summary = self.get_violation_summary()
            if violation_summary:
                return True, f"Memory inheritance verified. Violations tracked: {len(violation_summary)}"

            return True, "Memory inheritance verified successfully"

        except Exception as e:
            return False, f"Memory verification failed: {e}"

    def get_inheritance_report(self) -> str:
        """Generate comprehensive inheritance report"""
        try:
            report = []
            report.append("🧠 MEMORY INHERITANCE SYSTEM REPORT")
            report.append("=" * 50)

            # Memory statistics
            cursor = self.db.execute("SELECT COUNT(*) FROM memory_entries")
            memory_count = cursor.fetchone()[0]
            report.append(f"📊 Total Memories: {memory_count}")

            # Critical memories
            critical_reminders = self.get_critical_reminders()
            report.append(f"🔴 Critical Reminders: {len(critical_reminders)}")
            for reminder in critical_reminders:
                report.append(f"  • {reminder}")

            # Violation summary
            violations = self.get_violation_summary()
            report.append(f"\n⚠️ Violation Summary: {len(violations)} types")
            for violation_type, data in violations.items():
                report.append(f"  • {violation_type}: {data['count']} times")

            # Memory verification
            verified, message = self.verify_memory_inheritance()
            status = "✅ VERIFIED" if verified else "❌ FAILED"
            report.append(f"\n🔍 Memory Verification: {status}")
            report.append(f"📝 Details: {message}")

            # Session info
            report.append(f"\n📅 Session: {self.session_id}")
            report.append(f"🕐 Started: {self.session_start}")
            report.append("🔢 Verification Code: 7749")
            report.append(f"📍 Verification Numbers: {self.verification_numbers}")

            return "\n".join(report)

        except Exception as e:
            return f"❌ Failed to generate inheritance report: {e}"

    def cleanup_old_sessions(self, days_old: int = 30):
        """Clean up old session data"""
        try:
            from datetime import timedelta
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_old)

            self.db.execute("""
                DELETE FROM session_continuity
                WHERE start_time < ? AND status != 'active'
            """, (cutoff_date.isoformat(),))

            self.logger.info(f"🧹 Cleaned up sessions older than {days_old} days")

        except Exception as e:
            self.logger.error(f"❌ Session cleanup failed: {e}")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - save session state"""
        self.save_session_snapshot()
        if self.db:
            self.db.close()


# Utility functions
def get_memory_system() -> EnhancedMemoryInheritance:
    """Get singleton memory system instance"""
    if not hasattr(get_memory_system, '_instance'):
        get_memory_system._instance = EnhancedMemoryInheritance()
    return get_memory_system._instance


def verify_inheritance() -> str:
    """Quick verification function"""
    with EnhancedMemoryInheritance() as memory:
        return memory.get_inheritance_report()


if __name__ == "__main__":
    # Test the system
    print("🧠 Testing Enhanced Memory Inheritance System...")
    print(verify_inheritance())
