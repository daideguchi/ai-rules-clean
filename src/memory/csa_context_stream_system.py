#!/usr/bin/env python3
"""
🌊 Context Stream Agent (CSA) システム実装
==========================================

【基づく概念】
- Note.com記事: Context Stream Agent による文脈不足解決
- o3評価: Claude Code + Cursor連携に最適な時系列+構造化アプローチ

【実装内容】
- イベントベース文脈記録 (時系列ストリーム)
- 非定型データの構造化変換
- 低レイテンシ文脈検索・要約
- Claude Code統合対応

【技術スタック】
- PostgreSQL + TimescaleDB (時系列DB)
- pgvector (ベクトル検索)
- OpenAI Embeddings (文脈ベクトル化)
"""

import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import openai
import psycopg2
from psycopg2.extras import RealDictCursor


@dataclass
class ContextEvent:
    """文脈ストリームイベント"""

    id: str
    timestamp: datetime
    source: str  # "user", "assistant", "system", "code", "cursor"
    event_type: str  # "code_change", "question", "answer", "file_edit", "error"
    content: str
    metadata: Dict[str, Any]
    session_id: str
    vector_embedding: Optional[List[float]] = None
    parent_event_id: Optional[str] = None


@dataclass
class ContextSummary:
    """文脈要約"""

    session_id: str
    time_range: str
    key_events: List[str]
    summary: str
    action_items: List[str]
    related_files: List[str]


class ContextStreamAgent:
    """Context Stream Agent - 文脈継続システム"""

    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
        self.embedding_model = "text-embedding-ada-002"
        self.current_session_id = str(uuid.uuid4())

    def init_csa_database(self):
        """CSA専用データベース初期化"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()

            # pgvector拡張のみ（TimescaleDBは無しで時系列最適化）
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

            # 文脈ストリームテーブル
            cur.execute("""
                CREATE TABLE IF NOT EXISTS context_stream (
                    id UUID PRIMARY KEY,
                    timestamp TIMESTAMPTZ NOT NULL,
                    source VARCHAR(50) NOT NULL,
                    event_type VARCHAR(100) NOT NULL,
                    content TEXT NOT NULL,
                    metadata JSONB,
                    session_id UUID NOT NULL,
                    vector_embedding vector(1536),
                    parent_event_id UUID REFERENCES context_stream(id),
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );
            """)

            # 時系列最適化インデックス（TimescaleDB無しバージョン）
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_context_timestamp
                ON context_stream (timestamp DESC);
            """)

            # 文脈要約テーブル
            cur.execute("""
                CREATE TABLE IF NOT EXISTS context_summaries (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    session_id UUID NOT NULL,
                    time_range TSTZRANGE NOT NULL,
                    key_events TEXT[],
                    summary TEXT NOT NULL,
                    action_items TEXT[],
                    related_files TEXT[],
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );
            """)

            # インデックス作成
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_context_session_time
                ON context_stream (session_id, timestamp DESC);
            """)

            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_context_vector
                ON context_stream USING ivfflat (vector_embedding vector_cosine_ops);
            """)

            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_context_event_type
                ON context_stream (event_type, timestamp DESC);
            """)

            conn.commit()
            cur.close()
            conn.close()

            return {"status": "success", "message": "CSA database initialized"}

        except Exception as e:
            return {
                "status": "error",
                "message": f"CSA DB initialization failed: {str(e)}",
            }

    def ingest_event(
        self,
        source: str,
        event_type: str,
        content: str,
        metadata: Optional[Dict] = None,
        parent_event_id: Optional[str] = None,
    ) -> str:
        """イベント取り込み（構造化変換）"""

        # イベント構造化
        event = ContextEvent(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
            source=source,
            event_type=event_type,
            content=content,
            metadata=metadata or {},
            session_id=self.current_session_id,
            parent_event_id=parent_event_id,
        )

        # ベクトル化
        try:
            client = openai.OpenAI()
            response = client.embeddings.create(
                model=self.embedding_model, input=f"{event_type}: {content}"
            )
            event.vector_embedding = response.data[0].embedding
        except Exception as e:
            print(f"Embedding failed: {e}")
            event.vector_embedding = [0.0] * 1536

        # DB保存
        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()

            cur.execute(
                """
                INSERT INTO context_stream
                (id, timestamp, source, event_type, content, metadata, session_id, vector_embedding, parent_event_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
            """,
                (
                    event.id,
                    event.timestamp,
                    event.source,
                    event.event_type,
                    event.content,
                    json.dumps(event.metadata),
                    event.session_id,
                    event.vector_embedding,
                    event.parent_event_id,
                ),
            )

            conn.commit()
            cur.close()
            conn.close()

            return event.id

        except Exception as e:
            print(f"Event ingestion failed: {e}")
            return ""

    def retrieve_context(
        self, query: str, time_window_hours: int = 24, limit: int = 10
    ) -> List[Dict]:
        """文脈検索（セマンティック + 時系列）"""

        # クエリをベクトル化
        try:
            client = openai.OpenAI()
            response = client.embeddings.create(model=self.embedding_model, input=query)
            query_vector = response.data[0].embedding
        except Exception as e:
            print(f"Query vectorization failed: {e}")
            return []

        try:
            conn = psycopg2.connect(**self.db_config, cursor_factory=RealDictCursor)
            cur = conn.cursor()

            # セマンティック + 時系列検索
            cur.execute(
                """
                SELECT
                    id,
                    timestamp,
                    source,
                    event_type,
                    content,
                    metadata,
                    1 - (vector_embedding <=> %s::vector) as similarity
                FROM context_stream
                WHERE session_id = %s
                  AND timestamp >= NOW() - INTERVAL '%s hours'
                  AND vector_embedding IS NOT NULL
                ORDER BY
                    (1 - (vector_embedding <=> %s::vector)) DESC,
                    timestamp DESC
                LIMIT %s;
            """,
                (
                    query_vector,
                    self.current_session_id,
                    time_window_hours,
                    query_vector,
                    limit,
                ),
            )

            results = cur.fetchall()
            cur.close()
            conn.close()

            return [dict(row) for row in results]

        except Exception as e:
            print(f"Context retrieval failed: {e}")
            return []

    def generate_context_summary(
        self, time_window_hours: int = 6
    ) -> Optional[ContextSummary]:
        """文脈要約生成"""

        try:
            conn = psycopg2.connect(**self.db_config, cursor_factory=RealDictCursor)
            cur = conn.cursor()

            # 指定時間範囲のイベント取得
            cur.execute(
                """
                SELECT *
                FROM context_stream
                WHERE session_id = %s
                  AND timestamp >= NOW() - INTERVAL '%s hours'
                ORDER BY timestamp ASC;
            """,
                (self.current_session_id, time_window_hours),
            )

            events = cur.fetchall()
            cur.close()
            conn.close()

            if not events:
                return None

            # 要約生成（簡易版）
            event_types = list({e["event_type"] for e in events})
            [
                e["content"][:100] + "..." if len(e["content"]) > 100 else e["content"]
                for e in events[-5:]
            ]  # 最新5件

            files_mentioned = []
            for event in events:
                if event["event_type"] in ["file_edit", "code_change"]:
                    if "file_path" in event["metadata"]:
                        files_mentioned.append(event["metadata"]["file_path"])

            summary = ContextSummary(
                session_id=self.current_session_id,
                time_range=f"Past {time_window_hours} hours",
                key_events=event_types,
                summary=f"Session with {len(events)} events: {', '.join(event_types[:3])}...",
                action_items=[],  # 実装時にAI要約を追加
                related_files=list(set(files_mentioned)),
            )

            return summary

        except Exception as e:
            print(f"Summary generation failed: {e}")
            return None

    def search_similar_contexts(
        self, current_context: str, top_k: int = 5
    ) -> List[Dict]:
        """類似文脈検索（過去セッション含む）"""

        try:
            client = openai.OpenAI()
            response = client.embeddings.create(
                model=self.embedding_model, input=current_context
            )
            context_vector = response.data[0].embedding
        except Exception as e:
            print(f"Context vectorization failed: {e}")
            return []

        try:
            conn = psycopg2.connect(**self.db_config, cursor_factory=RealDictCursor)
            cur = conn.cursor()

            # 全セッションから類似文脈検索
            cur.execute(
                """
                SELECT
                    id,
                    timestamp,
                    source,
                    event_type,
                    content,
                    session_id,
                    1 - (vector_embedding <=> %s::vector) as similarity
                FROM context_stream
                WHERE vector_embedding IS NOT NULL
                  AND 1 - (vector_embedding <=> %s::vector) > 0.7
                ORDER BY similarity DESC
                LIMIT %s;
            """,
                (context_vector, context_vector, top_k),
            )

            results = cur.fetchall()
            cur.close()
            conn.close()

            return [dict(row) for row in results]

        except Exception as e:
            print(f"Similar context search failed: {e}")
            return []

    def get_session_timeline(
        self, session_id: Optional[str] = None, limit: int = 50
    ) -> List[Dict]:
        """セッションタイムライン取得"""

        target_session = session_id or self.current_session_id

        try:
            conn = psycopg2.connect(**self.db_config, cursor_factory=RealDictCursor)
            cur = conn.cursor()

            cur.execute(
                """
                SELECT
                    id,
                    timestamp,
                    source,
                    event_type,
                    LEFT(content, 200) as content_preview,
                    metadata
                FROM context_stream
                WHERE session_id = %s
                ORDER BY timestamp DESC
                LIMIT %s;
            """,
                (target_session, limit),
            )

            results = cur.fetchall()
            cur.close()
            conn.close()

            return [dict(row) for row in results]

        except Exception as e:
            print(f"Timeline retrieval failed: {e}")
            return []


def main():
    """メイン実行 - CSAシステムテスト"""
    print("🌊 Context Stream Agent (CSA) システム初期化")

    # DB設定
    db_config = {
        "host": "localhost",
        "database": "president_ai",
        "user": "dd",
        "password": "",
        "port": 5432,
    }

    csa = ContextStreamAgent(db_config)

    # 1. データベース初期化
    print("\\n1️⃣ CSAデータベース初期化")
    init_result = csa.init_csa_database()
    print(f"初期化: {init_result['status']}")
    if init_result["status"] == "error":
        print(f"エラー: {init_result['message']}")
        return

    # 2. テストイベント取り込み
    print("\\n2️⃣ テストイベント取り込み")
    test_events = [
        (
            "user",
            "question",
            "Claude Code + Cursor連携の設定方法を教えて",
            {"priority": "high"},
        ),
        (
            "assistant",
            "answer",
            "Claude CLIをインストールして.cursor/rulesを設定してください",
            {"confidence": 0.9},
        ),
        (
            "cursor",
            "file_edit",
            "memory/president_state_system.py を編集",
            {"file_path": "memory/president_state_system.py", "lines_changed": 50},
        ),
        (
            "code",
            "error",
            "PostgreSQL connection failed",
            {"error_type": "connection", "severity": "high"},
        ),
        (
            "user",
            "code_change",
            "データベース設定を修正してPostgreSQL接続成功",
            {"file_path": "memory/president_state_system.py"},
        ),
    ]

    event_ids = []
    for source, event_type, content, metadata in test_events:
        event_id = csa.ingest_event(source, event_type, content, metadata)
        if event_id:
            event_ids.append(event_id)
            print(f"   ✅ {event_type}: {content[:50]}...")
        else:
            print(f"   ❌ {event_type}: 取り込み失敗")

    print(f"取り込み完了: {len(event_ids)}件")

    # 3. 文脈検索テスト
    print("\\n3️⃣ 文脈検索テスト")
    search_queries = ["PostgreSQL設定問題", "Cursor連携方法", "データベース接続エラー"]

    for query in search_queries:
        results = csa.retrieve_context(query, time_window_hours=1, limit=3)
        print(f"\\n   検索: '{query}'")
        print(f"   結果: {len(results)}件")
        for result in results:
            print(
                f"     - {result['event_type']}: {result['content'][:60]}... (類似度: {result['similarity']:.3f})"
            )

    # 4. 文脈要約生成
    print("\\n4️⃣ 文脈要約生成")
    summary = csa.generate_context_summary(time_window_hours=1)
    if summary:
        print(f"   期間: {summary.time_range}")
        print(f"   イベント種類: {summary.key_events}")
        print(f"   要約: {summary.summary}")
        print(f"   関連ファイル: {summary.related_files}")
    else:
        print("   要約生成失敗")

    # 5. セッションタイムライン
    print("\\n5️⃣ セッションタイムライン")
    timeline = csa.get_session_timeline(limit=10)
    print(f"   イベント数: {len(timeline)}")
    for i, event in enumerate(timeline[:5]):
        print(
            f"   {i + 1}. [{event['timestamp'].strftime('%H:%M:%S')}] {event['source']}.{event['event_type']}: {event['content_preview'][:80]}..."
        )

    print("\\n✅ CSAシステム実装・テスト完了")
    print("📍 Note.com記事のCSA概念をClaude Code + Cursor連携向けに実装")


if __name__ == "__main__":
    main()
