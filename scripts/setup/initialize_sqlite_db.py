#!/usr/bin/env python3
"""
SQLite Database Initialization - SQLiteデータベース初期化
必要なテーブルの作成と既存データの保持
"""

import sqlite3
import sys
from datetime import datetime
from pathlib import Path


def initialize_sqlite_database():
    """SQLiteデータベース初期化"""
    project_path = Path(__file__).parent.parent.parent
    db_path = project_path / "runtime" / "memory" / "forever_ledger.db"

    print(f"Initializing SQLite database: {db_path}")

    # Ensure directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Check existing tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [row[0] for row in cursor.fetchall()]
        print(f"Existing tables: {existing_tables}")

        # Create violations table if not exists
        if "violations" not in existing_tables:
            print("Creating violations table...")
            cursor.execute("""
                CREATE TABLE violations (
                    violation_type TEXT PRIMARY KEY,
                    count INTEGER DEFAULT 0,
                    last_occurrence TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Insert initial thinking violation record
            cursor.execute(
                """
                INSERT INTO violations (violation_type, count, last_occurrence, created_at)
                VALUES ('thinking_required', 0, NULL, ?)
            """,
                (datetime.now().isoformat(),),
            )

            print("✅ violations table created")

        # Create sessions table if not exists
        if "sessions" not in existing_tables:
            print("Creating sessions table...")
            cursor.execute("""
                CREATE TABLE sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    start_time TEXT,
                    end_time TEXT,
                    conversation_count INTEGER DEFAULT 0,
                    memory_loaded BOOLEAN DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("✅ sessions table created")

        # Create memory_events table if not exists
        if "memory_events" not in existing_tables:
            print("Creating memory_events table...")
            cursor.execute("""
                CREATE TABLE memory_events (
                    id TEXT PRIMARY KEY,
                    session_id TEXT,
                    event_type TEXT,
                    content TEXT,
                    metadata TEXT,
                    timestamp TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(session_id) REFERENCES sessions(session_id)
                )
            """)
            print("✅ memory_events table created")

        # Create thinking_logs table if not exists
        if "thinking_logs" not in existing_tables:
            print("Creating thinking_logs table...")
            cursor.execute("""
                CREATE TABLE thinking_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    response_id TEXT,
                    has_thinking_tags BOOLEAN,
                    violation_detected BOOLEAN,
                    enforcement_triggered BOOLEAN,
                    timestamp TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("✅ thinking_logs table created")

        # Ensure forever table has proper structure
        cursor.execute("PRAGMA table_info(forever)")
        forever_columns = [row[1] for row in cursor.fetchall()]

        if "importance" not in forever_columns:
            print("Adding importance column to forever table...")
            cursor.execute(
                "ALTER TABLE forever ADD COLUMN importance INTEGER DEFAULT 10"
            )
            print("✅ forever table updated")

        # Create indexes for performance
        print("Creating indexes...")

        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_violations_type ON violations(violation_type)",
            "CREATE INDEX IF NOT EXISTS idx_sessions_start_time ON sessions(start_time)",
            "CREATE INDEX IF NOT EXISTS idx_memory_events_session ON memory_events(session_id)",
            "CREATE INDEX IF NOT EXISTS idx_memory_events_timestamp ON memory_events(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_thinking_logs_session ON thinking_logs(session_id)",
            "CREATE INDEX IF NOT EXISTS idx_thinking_logs_timestamp ON thinking_logs(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_forever_importance ON forever(importance)",
            "CREATE INDEX IF NOT EXISTS idx_forever_created_at ON forever(created_at)",
        ]

        for index_sql in indexes:
            cursor.execute(index_sql)

        print("✅ indexes created")

        # Commit changes
        conn.commit()

        # Verify all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        final_tables = [row[0] for row in cursor.fetchall()]
        print(f"Final tables: {final_tables}")

        # Check data counts
        for table in final_tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  {table}: {count} records")

        conn.close()
        print("✅ SQLite database initialization completed successfully")
        return True

    except Exception as e:
        print(f"❌ SQLite database initialization failed: {e}")
        return False


if __name__ == "__main__":
    success = initialize_sqlite_database()
    sys.exit(0 if success else 1)
