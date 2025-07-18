#!/usr/bin/env python3
"""
PostgreSQL直接接続ログシステム構築
===============================

Docker/Supabaseが使えない環境でも動作する
PostgreSQL直接接続によるログ管理システム
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    import psycopg2
    import psycopg2.extras
except ImportError as e:
    print(f"❌ PostgreSQL driver not installed: {e}")
    print("Run: pip install psycopg2-binary")
    sys.exit(1)


class PostgreSQLLogSystem:
    """PostgreSQL直接接続ログシステム"""

    def __init__(self):
        self.project_root = project_root
        self.db_config = {
            "host": "localhost",
            "port": 5432,
            "database": "coding_rule2_ai",
            "user": "dd",
            "password": "",
        }
        self.connection = None

    def connect(self) -> bool:
        """PostgreSQLに接続"""
        try:
            self.connection = psycopg2.connect(**self.db_config)
            self.connection.autocommit = False
            print("✅ PostgreSQL接続成功")
            return True
        except Exception as e:
            print(f"❌ PostgreSQL接続失敗: {e}")
            return False

    def create_tables(self) -> bool:
        """ログテーブル作成"""
        try:
            with self.connection.cursor() as cursor:
                # AI performance log table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS ai_performance_log (
                        id SERIAL PRIMARY KEY,
                        session_id TEXT NOT NULL,
                        timestamp TIMESTAMPTZ DEFAULT NOW(),
                        task_success BOOLEAN NOT NULL DEFAULT FALSE,
                        execution_time NUMERIC(10,3) DEFAULT 0,
                        tool_calls_count INTEGER DEFAULT 0,
                        tool_calls JSONB DEFAULT '[]',
                        error_count INTEGER DEFAULT 0,
                        thinking_tag_used BOOLEAN DEFAULT FALSE,
                        todo_tracking BOOLEAN DEFAULT FALSE,
                        task_complexity TEXT DEFAULT 'simple',
                        learning_score NUMERIC(5,2) DEFAULT 0,
                        success_patterns JSONB DEFAULT '[]',
                        failure_patterns JSONB DEFAULT '[]',
                        user_feedback TEXT,
                        log_source TEXT DEFAULT 'direct',
                        created_at TIMESTAMPTZ DEFAULT NOW()
                    );
                """
                )

                # AI learning patterns table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS ai_learning_patterns (
                        id SERIAL PRIMARY KEY,
                        timestamp TIMESTAMPTZ DEFAULT NOW(),
                        pattern_type TEXT NOT NULL,
                        patterns JSONB NOT NULL DEFAULT '[]',
                        effectiveness_score NUMERIC(5,2) DEFAULT 0,
                        session_id TEXT,
                        frequency INTEGER DEFAULT 1,
                        created_at TIMESTAMPTZ DEFAULT NOW()
                    );
                """
                )

                # System events log table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS system_events_log (
                        id SERIAL PRIMARY KEY,
                        timestamp TIMESTAMPTZ DEFAULT NOW(),
                        event_type TEXT NOT NULL,
                        event_data JSONB NOT NULL DEFAULT '{}',
                        severity TEXT DEFAULT 'info',
                        session_id TEXT,
                        source_file TEXT,
                        created_at TIMESTAMPTZ DEFAULT NOW()
                    );
                """
                )

                # Create indexes
                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_performance_session
                    ON ai_performance_log(session_id);
                """
                )
                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_performance_timestamp
                    ON ai_performance_log(timestamp);
                """
                )
                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_system_events_timestamp
                    ON system_events_log(timestamp);
                """
                )
                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_system_events_type
                    ON system_events_log(event_type);
                """
                )

                self.connection.commit()
                print("✅ ログテーブル作成完了")
                return True

        except Exception as e:
            print(f"❌ テーブル作成失敗: {e}")
            self.connection.rollback()
            return False

    def create_log_functions(self) -> bool:
        """ログ記録用関数作成"""
        try:
            with self.connection.cursor() as cursor:
                # Performance log function
                cursor.execute(
                    """
                    CREATE OR REPLACE FUNCTION log_performance(
                        p_session_id TEXT,
                        p_task_success BOOLEAN DEFAULT FALSE,
                        p_execution_time NUMERIC DEFAULT 0,
                        p_tool_calls_count INTEGER DEFAULT 0,
                        p_tool_calls JSONB DEFAULT '[]',
                        p_error_count INTEGER DEFAULT 0,
                        p_thinking_tag_used BOOLEAN DEFAULT FALSE,
                        p_todo_tracking BOOLEAN DEFAULT FALSE,
                        p_task_complexity TEXT DEFAULT 'simple',
                        p_learning_score NUMERIC DEFAULT 0,
                        p_success_patterns JSONB DEFAULT '[]',
                        p_failure_patterns JSONB DEFAULT '[]',
                        p_user_feedback TEXT DEFAULT '',
                        p_log_source TEXT DEFAULT 'direct'
                    ) RETURNS INTEGER AS $$
                    DECLARE
                        new_id INTEGER;
                    BEGIN
                        INSERT INTO ai_performance_log (
                            session_id, task_success, execution_time, tool_calls_count,
                            tool_calls, error_count, thinking_tag_used, todo_tracking,
                            task_complexity, learning_score, success_patterns,
                            failure_patterns, user_feedback, log_source
                        ) VALUES (
                            p_session_id, p_task_success, p_execution_time, p_tool_calls_count,
                            p_tool_calls, p_error_count, p_thinking_tag_used, p_todo_tracking,
                            p_task_complexity, p_learning_score, p_success_patterns,
                            p_failure_patterns, p_user_feedback, p_log_source
                        ) RETURNING id INTO new_id;

                        RETURN new_id;
                    END;
                    $$ LANGUAGE plpgsql;
                """
                )

                # System event log function
                cursor.execute(
                    """
                    CREATE OR REPLACE FUNCTION log_system_event(
                        p_event_type TEXT,
                        p_event_data JSONB DEFAULT '{}',
                        p_severity TEXT DEFAULT 'info',
                        p_session_id TEXT DEFAULT NULL,
                        p_source_file TEXT DEFAULT NULL
                    ) RETURNS INTEGER AS $$
                    DECLARE
                        new_id INTEGER;
                    BEGIN
                        INSERT INTO system_events_log (
                            event_type, event_data, severity, session_id, source_file
                        ) VALUES (
                            p_event_type, p_event_data, p_severity, p_session_id, p_source_file
                        ) RETURNING id INTO new_id;

                        RETURN new_id;
                    END;
                    $$ LANGUAGE plpgsql;
                """
                )

                self.connection.commit()
                print("✅ ログ関数作成完了")
                return True

        except Exception as e:
            print(f"❌ ログ関数作成失敗: {e}")
            self.connection.rollback()
            return False

    def setup_logging_system(self) -> bool:
        """ログシステムセットアップ"""
        print("🚀 PostgreSQL直接接続ログシステム構築開始")
        print("=" * 50)

        if not self.connect():
            return False

        if not self.create_tables():
            return False

        if not self.create_log_functions():
            return False

        # Test logging
        if not self.test_logging():
            return False

        print("\n✅ ログシステム構築完了")
        return True

    def test_logging(self) -> bool:
        """ログシステムテスト"""
        try:
            with self.connection.cursor() as cursor:
                # Test performance log
                cursor.execute(
                    """
                    SELECT log_performance(
                        'test_session',
                        true,
                        1.5,
                        3,
                        '["read_file", "write_file", "bash_command"]'::jsonb,
                        0,
                        true,
                        true,
                        'medium',
                        8.5,
                        '["successful_file_operation"]'::jsonb,
                        '[]'::jsonb,
                        'Test log entry',
                        'setup_test'
                    )
                """
                )

                result = cursor.fetchone()
                log_id = result[0]

                # Test system event log
                cursor.execute(
                    """
                    SELECT log_system_event(
                        'system_setup',
                        '{"component": "log_system", "status": "initialized"}'::jsonb,
                        'info',
                        'test_session',
                        'setup_log_system.py'
                    )
                """
                )

                result = cursor.fetchone()
                event_id = result[0]

                self.connection.commit()

                print(
                    f"✅ テストログ記録完了 (performance_id: {log_id}, event_id: {event_id})"
                )
                return True

        except Exception as e:
            print(f"❌ ログテスト失敗: {e}")
            self.connection.rollback()
            return False

    def get_log_stats(self) -> Dict:
        """ログ統計取得"""
        try:
            with self.connection.cursor(
                cursor_factory=psycopg2.extras.RealDictCursor
            ) as cursor:
                # Performance log stats
                cursor.execute(
                    """
                    SELECT
                        COUNT(*) as total_entries,
                        COUNT(DISTINCT session_id) as unique_sessions,
                        AVG(execution_time) as avg_execution_time,
                        SUM(CASE WHEN task_success THEN 1 ELSE 0 END) as successful_tasks,
                        SUM(error_count) as total_errors
                    FROM ai_performance_log
                """
                )

                performance_stats = cursor.fetchone()

                # System events stats
                cursor.execute(
                    """
                    SELECT
                        COUNT(*) as total_events,
                        COUNT(DISTINCT event_type) as unique_event_types,
                        COUNT(DISTINCT session_id) as unique_sessions
                    FROM system_events_log
                """
                )

                event_stats = cursor.fetchone()

                return {
                    "performance_log": dict(performance_stats),
                    "system_events": dict(event_stats),
                    "timestamp": datetime.now().isoformat(),
                }

        except Exception as e:
            print(f"❌ 統計取得失敗: {e}")
            return {}

    def close(self):
        """接続終了"""
        if self.connection:
            self.connection.close()
            print("✅ PostgreSQL接続終了")


def main():
    """メイン実行"""
    log_system = PostgreSQLLogSystem()

    try:
        if log_system.setup_logging_system():
            # 統計表示
            stats = log_system.get_log_stats()
            if stats:
                print("\n📊 ログシステム統計:")
                print(
                    f"  Performance Logs: {stats['performance_log']['total_entries']}件"
                )
                print(f"  System Events: {stats['system_events']['total_events']}件")
                print(
                    f"  Unique Sessions: {stats['performance_log']['unique_sessions']}件"
                )

                # 統計を保存
                stats_file = project_root / "runtime" / "log_system_stats.json"
                stats_file.parent.mkdir(parents=True, exist_ok=True)
                with open(stats_file, "w") as f:
                    json.dump(stats, f, indent=2)

                print(f"\n📝 統計保存: {stats_file}")

            print("\n🎉 PostgreSQL直接接続ログシステム構築完了！")
            print("💡 今後はすべてのログがPostgreSQLに記録されます")

        else:
            print("\n❌ ログシステム構築失敗")
            return 1

    except KeyboardInterrupt:
        print("\n⚠️ ユーザーによって中断されました")
        return 1
    except Exception as e:
        print(f"\n❌ 構築中にエラーが発生: {e}")
        return 1
    finally:
        log_system.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
