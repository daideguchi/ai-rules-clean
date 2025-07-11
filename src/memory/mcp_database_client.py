#!/usr/bin/env python3
"""
🔗 MCP Database Client - PRESIDENT状態のMCP接続テスト
======================================================

【目的】
- PostgreSQL + pgvectorデータベースへのMCP接続確認
- Claude CodeでのDB操作テスト
- PRESIDENT状態の継続性検証

【機能】
- DB接続テスト
- PRESIDENT状態クエリ
- 78回学習検索
- MCP互換インターフェース
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import psycopg2
from psycopg2.extras import RealDictCursor


class MCPDatabaseClient:
    """MCP互換データベースクライアント"""

    def __init__(self):
        # DB設定
        self.db_config = {
            "host": "localhost",
            "database": "president_ai",
            "user": "dd",
            "password": "",
            "port": 5432,
        }
        self.project_root = Path(__file__).parent.parent

    def test_connection(self) -> Dict[str, Any]:
        """DB接続テスト"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()

            # 基本確認
            cur.execute("SELECT version();")
            version = cur.fetchone()[0]

            # pgvector確認
            cur.execute("SELECT * FROM pg_extension WHERE extname = 'vector';")
            vector_ext = cur.fetchone()

            # テーブル存在確認
            cur.execute("""
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
            """)
            tables = [row[0] for row in cur.fetchall()]

            cur.close()
            conn.close()

            return {
                "status": "success",
                "postgresql_version": version,
                "pgvector_enabled": vector_ext is not None,
                "available_tables": tables,
                "connection_info": f"Connected to {self.db_config['database']} as {self.db_config['user']}",
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "message": "Database connection failed",
            }

    def get_president_state(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """PRESIDENT状態取得"""
        try:
            conn = psycopg2.connect(**self.db_config, cursor_factory=RealDictCursor)
            cur = conn.cursor()

            if session_id:
                cur.execute(
                    """
                    SELECT * FROM president_states
                    WHERE session_id = %s;
                """,
                    (session_id,),
                )
            else:
                # 最新状態取得
                cur.execute("""
                    SELECT * FROM president_states
                    ORDER BY timestamp DESC LIMIT 1;
                """)

            result = cur.fetchone()
            cur.close()
            conn.close()

            if result:
                return {
                    "status": "found",
                    "president_state": dict(result),
                    "session_id": result["session_id"],
                    "mistake_count": result["mistake_count"],
                    "last_update": result["timestamp"].isoformat(),
                }
            else:
                return {"status": "not_found", "message": "No PRESIDENT state found"}

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def search_mistake_patterns(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """78回学習パターン検索"""
        try:
            conn = psycopg2.connect(**self.db_config, cursor_factory=RealDictCursor)
            cur = conn.cursor()

            # テキスト検索（簡易版）
            cur.execute(
                """
                SELECT
                    mistake_id,
                    description,
                    context,
                    prevention_method,
                    date
                FROM mistake_embeddings
                WHERE description ILIKE %s
                   OR context ILIKE %s
                   OR prevention_method ILIKE %s
                ORDER BY mistake_id DESC
                LIMIT %s;
            """,
                (f"%{query}%", f"%{query}%", f"%{query}%", limit),
            )

            results = cur.fetchall()
            cur.close()
            conn.close()

            return {
                "status": "success",
                "query": query,
                "found_count": len(results),
                "mistake_patterns": [dict(row) for row in results],
            }

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def get_database_stats(self) -> Dict[str, Any]:
        """データベース統計情報"""
        try:
            conn = psycopg2.connect(**self.db_config, cursor_factory=RealDictCursor)
            cur = conn.cursor()

            # 統計取得
            stats = {}

            # ミス学習数
            cur.execute("SELECT COUNT(*) FROM mistake_embeddings;")
            stats["total_mistakes"] = cur.fetchone()[0]

            # PRESIDENT状態数
            cur.execute("SELECT COUNT(*) FROM president_states;")
            stats["president_sessions"] = cur.fetchone()[0]

            # 最新ミス
            cur.execute("""
                SELECT mistake_id, LEFT(description, 100) as description, date
                FROM mistake_embeddings
                ORDER BY mistake_id DESC LIMIT 3;
            """)
            stats["latest_mistakes"] = [dict(row) for row in cur.fetchall()]

            # データベースサイズ
            cur.execute("""
                SELECT pg_size_pretty(pg_database_size('president_ai')) as db_size;
            """)
            stats["database_size"] = cur.fetchone()[0]

            cur.close()
            conn.close()

            return {
                "status": "success",
                "statistics": stats,
                "generated_at": datetime.now().isoformat(),
            }

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def execute_query(self, sql: str, params: Optional[tuple] = None) -> Dict[str, Any]:
        """カスタムクエリ実行（読み取り専用）"""
        # セキュリティ: SELECT文のみ許可
        if not sql.strip().upper().startswith("SELECT"):
            return {"status": "error", "error": "Only SELECT queries are allowed"}

        try:
            conn = psycopg2.connect(**self.db_config, cursor_factory=RealDictCursor)
            cur = conn.cursor()

            if params:
                cur.execute(sql, params)
            else:
                cur.execute(sql)

            results = cur.fetchall()
            cur.close()
            conn.close()

            return {
                "status": "success",
                "query": sql,
                "row_count": len(results),
                "results": [dict(row) for row in results],
            }

        except Exception as e:
            return {"status": "error", "error": str(e), "query": sql}


def main():
    """メイン実行 - MCP Database Client テスト"""
    print("🔗 MCP Database Client - 接続テスト開始")

    client = MCPDatabaseClient()

    # 1. 接続テスト
    print("\\n1️⃣ データベース接続テスト")
    connection_result = client.test_connection()
    print(f"接続状況: {connection_result['status']}")
    if connection_result["status"] == "success":
        print(f"   PostgreSQL: {connection_result['postgresql_version'][:50]}...")
        print(f"   pgvector: {'✅' if connection_result['pgvector_enabled'] else '❌'}")
        print(f"   テーブル: {connection_result['available_tables']}")
    else:
        print(f"   エラー: {connection_result['error']}")
        return

    # 2. PRESIDENT状態確認
    print("\\n2️⃣ PRESIDENT状態確認")
    state_result = client.get_president_state()
    print(f"状態: {state_result['status']}")
    if state_result["status"] == "found":
        print(f"   セッションID: {state_result['session_id']}")
        print(f"   学習回数: {state_result['mistake_count']}")
        print(f"   最終更新: {state_result['last_update']}")

    # 3. 78回学習検索テスト
    print("\\n3️⃣ 78回学習パターン検索")
    search_queries = ["ファイル", "憶測", "確認不足"]

    for query in search_queries:
        search_result = client.search_mistake_patterns(query, limit=3)
        print(f"\\n   検索語: '{query}'")
        print(f"   結果: {search_result['found_count']}件")

        if search_result["status"] == "success":
            for mistake in search_result["mistake_patterns"]:
                print(
                    f"     - ミス#{mistake['mistake_id']}: {mistake['description'][:60]}..."
                )

    # 4. データベース統計
    print("\\n4️⃣ データベース統計情報")
    stats_result = client.get_database_stats()
    if stats_result["status"] == "success":
        stats = stats_result["statistics"]
        print(f"   総ミス学習数: {stats['total_mistakes']}")
        print(f"   PRESIDENT セッション数: {stats['president_sessions']}")
        print(f"   データベースサイズ: {stats['database_size']}")
        print("   最新ミス:")
        for mistake in stats["latest_mistakes"]:
            print(f"     - ミス#{mistake['mistake_id']}: {mistake['description']}")

    # 5. カスタムクエリテスト
    print("\\n5️⃣ カスタムクエリテスト")
    test_queries = [
        "SELECT COUNT(*) as total FROM mistake_embeddings",
        "SELECT mistake_id, date FROM mistake_embeddings ORDER BY mistake_id DESC LIMIT 3",
    ]

    for sql in test_queries:
        query_result = client.execute_query(sql)
        print(f"\\n   クエリ: {sql}")
        print(f"   結果: {query_result['status']}")
        if query_result["status"] == "success":
            print(f"   行数: {query_result['row_count']}")
            for row in query_result["results"]:
                print(f"     {row}")

    print("\\n✅ MCP Database Client テスト完了")
    print("📍 Claude Code からのDB操作準備完了")


if __name__ == "__main__":
    main()
