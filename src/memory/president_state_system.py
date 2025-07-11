#!/usr/bin/env python3
"""
🧠 PRESIDENT状態永続化システム - 78回学習ベクトル化
=======================================================

【目的】
- セッション間でのPRESIDENT状態完全継続
- 78回学習をベクトル検索可能な形式で永続化
- 同じミスの反復防止機能

【技術スタック】
- PostgreSQL + pgvector (ベクトル検索)
- OpenAI Embeddings (text-embedding-ada-002)
- MCP接続 (Claude Code統合)

【評価向上】
- 現在: C-評価 (78回学習が機能しない)
- 目標: A級評価 (完全な自律成長実現)
"""

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import openai
import psycopg2
from psycopg2.extras import RealDictCursor


@dataclass
class MistakeRecord:
    """78回学習の個別ミス記録"""

    id: int
    date: str
    category: str
    description: str
    context: str
    prevention_method: str
    embedding: Optional[List[float]] = None
    similarity_threshold: float = 0.18


@dataclass
class PresidentState:
    """PRESIDENT完全状態記録"""

    session_id: str
    timestamp: str
    mistake_count: int
    learning_embeddings: List[MistakeRecord]
    current_context: Dict[str, Any]
    session_memory: Dict[str, Any]
    policy_version: str = "v2.0"


class PresidentStateManager:
    """PRESIDENT状態管理 - 完全永続化システム"""

    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
        self.embedding_model = "text-embedding-ada-002"
        self.project_root = Path(__file__).parent.parent

    def init_database(self):
        """PostgreSQL + pgvector初期設定"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()

            # pgvector拡張有効化
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

            # PRESIDENT状態テーブル
            cur.execute("""
                CREATE TABLE IF NOT EXISTS president_states (
                    session_id VARCHAR(255) PRIMARY KEY,
                    timestamp TIMESTAMPTZ DEFAULT NOW(),
                    mistake_count INTEGER,
                    current_context JSONB,
                    session_memory JSONB,
                    policy_version VARCHAR(50)
                );
            """)

            # 78回学習ベクトルテーブル
            cur.execute("""
                CREATE TABLE IF NOT EXISTS mistake_embeddings (
                    id SERIAL PRIMARY KEY,
                    mistake_id INTEGER UNIQUE,
                    date DATE,
                    category VARCHAR(100),
                    description TEXT,
                    context TEXT,
                    prevention_method TEXT,
                    embedding vector(1536),
                    similarity_threshold REAL DEFAULT 0.18,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );
            """)

            # ベクトル検索用インデックス
            cur.execute("""
                CREATE INDEX IF NOT EXISTS mistake_embedding_idx
                ON mistake_embeddings USING ivfflat (embedding vector_cosine_ops);
            """)

            conn.commit()
            cur.close()
            conn.close()

            return {"status": "success", "message": "Database initialized"}

        except Exception as e:
            return {"status": "error", "message": f"DB initialization failed: {str(e)}"}

    def load_mistakes_from_markdown(self) -> List[MistakeRecord]:
        """既存の78回学習をMarkdownから読み込み"""
        mistakes_file = self.project_root / "docs/misc/president-mistakes.md"

        if not mistakes_file.exists():
            return []

        mistakes = []
        with open(mistakes_file, encoding="utf-8") as f:
            content = f.read()

        # Markdownパース（簡易版）
        lines = content.split("\n")
        current_mistake = None

        for line in lines:
            # ### 数字. で始まる行がミス記録の開始
            if line.strip().startswith("###") and any(char.isdigit() for char in line):
                if current_mistake:
                    mistakes.append(current_mistake)

                # ミス番号抽出
                mistake_id = "".join(filter(str.isdigit, line.split(".")[0]))
                if mistake_id:
                    current_mistake = MistakeRecord(
                        id=int(mistake_id),
                        date=datetime.now().isoformat()[:10],
                        category="legacy_import",
                        description=line.strip(),
                        context="",
                        prevention_method="",
                    )
            elif current_mistake and line.strip():
                # 説明文を追加
                if line.startswith("**"):
                    current_mistake.context += line + "\n"
                else:
                    current_mistake.description += " " + line.strip()

        if current_mistake:
            mistakes.append(current_mistake)

        return mistakes[:78]  # 78回まで

    def generate_embedding(self, text: str) -> List[float]:
        """OpenAI Embeddingsでテキストをベクトル化"""
        try:
            client = openai.OpenAI()
            response = client.embeddings.create(model=self.embedding_model, input=text)
            return response.data[0].embedding
        except Exception as e:
            print(f"Embedding generation failed: {e}")
            return [0.0] * 1536  # デフォルトベクトル

    def save_mistakes_to_db(self, mistakes: List[MistakeRecord]):
        """78回学習をベクトル化してDBに保存"""
        conn = psycopg2.connect(**self.db_config)
        cur = conn.cursor()

        for mistake in mistakes:
            # テキスト結合してベクトル化
            full_text = (
                f"{mistake.description} {mistake.context} {mistake.prevention_method}"
            )
            embedding = self.generate_embedding(full_text)
            mistake.embedding = embedding

            # DB挿入
            cur.execute(
                """
                INSERT INTO mistake_embeddings
                (mistake_id, date, category, description, context, prevention_method, embedding)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (mistake_id) DO UPDATE SET
                    description = EXCLUDED.description,
                    context = EXCLUDED.context,
                    embedding = EXCLUDED.embedding;
            """,
                (
                    mistake.id,
                    mistake.date,
                    mistake.category,
                    mistake.description,
                    mistake.context,
                    mistake.prevention_method,
                    embedding,
                ),
            )

        conn.commit()
        cur.close()
        conn.close()

        return len(mistakes)

    def search_similar_mistakes(
        self, current_action: str, top_k: int = 3
    ) -> List[Dict]:
        """現在の行動に類似した過去のミスを検索"""
        action_embedding = self.generate_embedding(current_action)

        conn = psycopg2.connect(**self.db_config, cursor_factory=RealDictCursor)
        cur = conn.cursor()

        cur.execute(
            """
            SELECT
                mistake_id,
                description,
                context,
                prevention_method,
                1 - (embedding <=> %s::vector) as similarity
            FROM mistake_embeddings
            WHERE 1 - (embedding <=> %s::vector) > similarity_threshold
            ORDER BY embedding <=> %s::vector
            LIMIT %s;
        """,
            (action_embedding, action_embedding, action_embedding, top_k),
        )

        results = cur.fetchall()
        cur.close()
        conn.close()

        return [dict(row) for row in results]

    def save_current_state(self, session_id: str, context: Dict, memory: Dict):
        """現在のPRESIDENT状態を永続化"""
        conn = psycopg2.connect(**self.db_config)
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO president_states
            (session_id, mistake_count, current_context, session_memory, policy_version)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (session_id) DO UPDATE SET
                timestamp = NOW(),
                current_context = EXCLUDED.current_context,
                session_memory = EXCLUDED.session_memory;
        """,
            (
                session_id,
                78,  # 現在の学習回数
                json.dumps(context),
                json.dumps(memory),
                "v2.0",
            ),
        )

        conn.commit()
        cur.close()
        conn.close()

    def restore_previous_state(
        self, session_id: Optional[str] = None
    ) -> Optional[PresidentState]:
        """前回セッションのPRESIDENT状態を復元"""
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
            # 最新のセッション状態を取得
            cur.execute("""
                SELECT * FROM president_states
                ORDER BY timestamp DESC LIMIT 1;
            """)

        result = cur.fetchone()
        cur.close()
        conn.close()

        if result:
            return PresidentState(
                session_id=result["session_id"],
                timestamp=result["timestamp"].isoformat(),
                mistake_count=result["mistake_count"],
                learning_embeddings=[],  # 必要に応じて別途ロード
                current_context=result["current_context"],
                session_memory=result["session_memory"],
                policy_version=result["policy_version"],
            )
        return None

    def prevent_mistake_repetition(self, current_action: str) -> Dict[str, Any]:
        """ミス反復防止機能 - 実行前チェック"""
        similar_mistakes = self.search_similar_mistakes(current_action)

        if similar_mistakes:
            return {
                "warning": True,
                "similar_mistakes": similar_mistakes,
                "recommendation": "過去の類似ミスが検出されました。実行前に確認してください。",
                "should_proceed": False,
            }

        return {
            "warning": False,
            "should_proceed": True,
            "message": "過去の類似ミスは検出されませんでした。",
        }


def main():
    """メイン実行 - システム初期化とテスト"""
    # DB設定（環境変数から取得想定）
    db_config = {
        "host": "localhost",
        "database": "president_ai",
        "user": "dd",  # PostgreSQLデフォルトユーザー
        "password": "",  # ローカルはパスワード不要
        "port": 5432,
    }

    manager = PresidentStateManager(db_config)

    # 1. データベース初期化
    init_result = manager.init_database()
    print(f"DB初期化: {init_result}")

    # 2. 既存の78回学習をインポート
    mistakes = manager.load_mistakes_from_markdown()
    print(f"Markdown読み込み: {len(mistakes)}件のミス")

    # 3. ベクトル化してDB保存
    if mistakes:
        saved_count = manager.save_mistakes_to_db(mistakes)
        print(f"DB保存完了: {saved_count}件")

    # 4. テスト: 類似ミス検索
    test_action = "憶測でファイルの内容を作成する"
    similar = manager.search_similar_mistakes(test_action)
    print(f"類似ミス検索: {len(similar)}件")

    for mistake in similar:
        print(
            f"  - ミス#{mistake['mistake_id']}: {mistake['description'][:50]}... (類似度: {mistake['similarity']:.3f})"
        )


if __name__ == "__main__":
    main()
