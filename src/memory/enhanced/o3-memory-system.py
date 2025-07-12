#!/usr/bin/env python3
"""
o3 Enhanced Memory System - セッション間記憶引き継ぎシステム
最適化されたセッション記憶継続システム with o3 API integration
"""

import asyncio
import hashlib
import json
import logging
import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import openai
from sklearn.feature_extraction.text import TfidfVectorizer

# ログ設定
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MemoryImportance(Enum):
    """記憶の重要度レベル"""

    CRITICAL = 5  # 必須継承（78回ミス記録、職務宣言等）
    HIGH = 4  # 重要タスク・プロジェクト文脈
    MEDIUM = 3  # 一般的作業履歴
    LOW = 2  # 参考情報
    ARCHIVE = 1  # アーカイブ候補


@dataclass
class MemoryRecord:
    """記憶レコード構造"""

    id: str
    session_id: str
    timestamp: datetime
    content: str
    importance: MemoryImportance
    keywords: List[str]
    context_type: str  # 'task', 'conversation', 'mistake', 'directive'
    embedding: Optional[List[float]] = None
    ai_source: str = "claude"  # 'claude', 'gemini', 'o3'


class O3EnhancedMemorySystem:
    """o3 API統合記憶システム"""

    def __init__(
        self,
        base_path: str = "${PROJECT_ROOT}/memory/enhanced",
        openai_api_key: Optional[str] = None,
    ):
        self.base_path = Path(base_path)
        self.openai_client = openai.AsyncOpenAI(
            api_key=openai_api_key or os.getenv("OPENAI_API_KEY")
        )
        self.setup_directories()
        self.init_database()
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words="english")

        # 重要度別記憶容量制限
        self.memory_limits = {
            MemoryImportance.CRITICAL: 1000,  # 無制限に近い
            MemoryImportance.HIGH: 500,
            MemoryImportance.MEDIUM: 200,
            MemoryImportance.LOW: 100,
            MemoryImportance.ARCHIVE: 50,
        }

    def setup_directories(self):
        """ディレクトリ構造設定"""
        dirs = [
            "session-records",
            "memory-vectors",
            "ai-collaboration",
            "context-summaries",
            "mistake-prevention",
            "priority-cache",
            "o3-insights",
        ]
        for dir_name in dirs:
            (self.base_path / dir_name).mkdir(parents=True, exist_ok=True)

    def init_database(self):
        """拡張データベース初期化"""
        db_path = self.base_path / "enhanced_memory.db"
        self.conn = sqlite3.connect(str(db_path), check_same_thread=False)

        # 拡張記憶テーブル
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS enhanced_memories (
                id TEXT PRIMARY KEY,
                session_id TEXT,
                timestamp TEXT,
                content TEXT,
                importance INTEGER,
                keywords TEXT,
                context_type TEXT,
                embedding BLOB,
                ai_source TEXT,
                access_count INTEGER DEFAULT 0,
                last_accessed TEXT,
                relevance_score REAL DEFAULT 0.0
            )
        """)

        # セッション継承テーブル
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS session_inheritance (
                id TEXT PRIMARY KEY,
                previous_session_id TEXT,
                current_session_id TEXT,
                inherited_memories TEXT,
                inheritance_timestamp TEXT,
                inheritance_score REAL
            )
        """)

        # AI連携記録テーブル
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS ai_collaborations (
                id TEXT PRIMARY KEY,
                session_id TEXT,
                ai_source TEXT,
                interaction_type TEXT,
                input_query TEXT,
                output_result TEXT,
                timestamp TEXT,
                usefulness_score REAL
            )
        """)

        # 重要度学習テーブル
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS importance_learning (
                id TEXT PRIMARY KEY,
                content_pattern TEXT,
                learned_importance INTEGER,
                confidence_score REAL,
                learning_timestamp TEXT
            )
        """)

        self.conn.commit()

    async def save_memory_with_o3_enhancement(
        self,
        content: str,
        session_id: str,
        context_type: str = "conversation",
        ai_source: str = "claude",
    ) -> str:
        """o3強化記憶保存"""

        # 1. 基本記憶レコード作成
        memory_id = hashlib.md5(
            f"{content}{datetime.now().isoformat()}".encode()
        ).hexdigest()

        # 2. o3による重要度・キーワード分析
        importance, keywords = await self._analyze_with_o3(content, context_type)

        # 3. 埋め込みベクトル生成
        embedding = await self._generate_embedding(content)

        # 4. 記憶レコード保存
        memory_record = MemoryRecord(
            id=memory_id,
            session_id=session_id,
            timestamp=datetime.now(),
            content=content,
            importance=importance,
            keywords=keywords,
            context_type=context_type,
            embedding=embedding,
            ai_source=ai_source,
        )

        self._save_memory_record(memory_record)

        logger.info(
            f"Memory saved with o3 enhancement: {memory_id} (importance: {importance.name})"
        )
        return memory_id

    async def _analyze_with_o3(
        self, content: str, context_type: str
    ) -> Tuple[MemoryImportance, List[str]]:
        """o3による内容分析"""
        try:
            analysis_prompt = f"""
            Analyze the following content and provide:
            1. Importance level (1-5 scale)
            2. Key keywords (max 10)

            Content: {content}
            Context: {context_type}

            Consider:
            - Mission-critical information (mistakes, directives) = 5
            - Project tasks and decisions = 4
            - General work progress = 3
            - Reference information = 2
            - Archive candidates = 1

            Respond in JSON format:
            {{
                "importance": number,
                "keywords": ["keyword1", "keyword2", ...],
                "reasoning": "brief explanation"
            }}
            """

            response = await self.openai_client.chat.completions.create(
                model="o3-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at analyzing content importance for AI memory systems.",
                    },
                    {"role": "user", "content": analysis_prompt},
                ],
                max_tokens=300,
            )

            analysis = json.loads(response.choices[0].message.content)
            importance = MemoryImportance(analysis.get("importance", 3))
            keywords = analysis.get("keywords", [])

            return importance, keywords

        except Exception as e:
            logger.error(f"o3 analysis failed: {e}")
            # フォールバック: 基本分析
            return self._fallback_analysis(content, context_type)

    def _fallback_analysis(
        self, content: str, context_type: str
    ) -> Tuple[MemoryImportance, List[str]]:
        """o3失敗時のフォールバック分析"""
        # 重要キーワード検出
        critical_keywords = [
            "ミス",
            "mistake",
            "error",
            "宣言",
            "directive",
            "禁止",
            "必須",
        ]
        high_keywords = ["実装", "システム", "プロジェクト", "タスク", "完了"]

        content_lower = content.lower()

        # 重要度判定
        if any(kw in content_lower for kw in critical_keywords):
            importance = MemoryImportance.CRITICAL
        elif any(kw in content_lower for kw in high_keywords):
            importance = MemoryImportance.HIGH
        else:
            importance = MemoryImportance.MEDIUM

        # 簡易キーワード抽出
        keywords = [
            kw for kw in critical_keywords + high_keywords if kw in content_lower
        ]

        return importance, keywords

    async def _generate_embedding(self, content: str) -> List[float]:
        """埋め込みベクトル生成"""
        try:
            response = await self.openai_client.embeddings.create(
                model="text-embedding-3-small", input=content
            )
            return list(response.data[0].embedding)
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return []

    def _save_memory_record(self, memory_record: MemoryRecord):
        """記憶レコードDB保存"""
        embedding_blob = (
            json.dumps(memory_record.embedding) if memory_record.embedding else None
        )

        self.conn.execute(
            """
            INSERT OR REPLACE INTO enhanced_memories
            (id, session_id, timestamp, content, importance, keywords, context_type, embedding, ai_source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                memory_record.id,
                memory_record.session_id,
                memory_record.timestamp.isoformat(),
                memory_record.content,
                memory_record.importance.value,
                json.dumps(memory_record.keywords),
                memory_record.context_type,
                embedding_blob,
                memory_record.ai_source,
            ),
        )
        self.conn.commit()

    async def inherit_session_memory(
        self, previous_session_id: str, current_session_id: str
    ) -> Dict[str, Any]:
        """セッション記憶継承"""
        logger.info(
            f"Inheriting memory from {previous_session_id} to {current_session_id}"
        )

        # 1. 前回セッションの重要記憶取得
        critical_memories = self._get_memories_by_importance(
            previous_session_id, [MemoryImportance.CRITICAL, MemoryImportance.HIGH]
        )

        # 2. o3による記憶要約・再構成
        memory_summary = await self._generate_memory_summary(critical_memories)

        # 3. 継承記録作成
        inheritance_id = hashlib.md5(
            f"{previous_session_id}-{current_session_id}".encode(),
            usedforsecurity=False,
        ).hexdigest()

        self.conn.execute(
            """
            INSERT INTO session_inheritance
            (id, previous_session_id, current_session_id, inherited_memories, inheritance_timestamp, inheritance_score)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                inheritance_id,
                previous_session_id,
                current_session_id,
                json.dumps([m.id for m in critical_memories]),
                datetime.now().isoformat(),
                len(critical_memories) / 10.0,  # 正規化スコア
            ),
        )
        self.conn.commit()

        # 4. 継承コンテキスト構築
        inheritance_context = {
            "previous_session_id": previous_session_id,
            "inherited_memories_count": len(critical_memories),
            "memory_summary": memory_summary,
            "critical_directives": [
                m.content
                for m in critical_memories
                if m.importance == MemoryImportance.CRITICAL
            ],
            "high_priority_tasks": [
                m.content
                for m in critical_memories
                if m.importance == MemoryImportance.HIGH
            ],
            "continuation_points": await self._identify_continuation_points(
                critical_memories
            ),
        }

        logger.info(
            f"Session inheritance completed: {len(critical_memories)} memories inherited"
        )
        return inheritance_context

    def _get_memories_by_importance(
        self, session_id: str, importance_levels: List[MemoryImportance]
    ) -> List[MemoryRecord]:
        """重要度別記憶取得"""
        importance_values = [imp.value for imp in importance_levels]
        placeholders = ",".join(["?"] * len(importance_values))

        cursor = self.conn.execute(
            f"""
            SELECT * FROM enhanced_memories
            WHERE session_id = ? AND importance IN ({placeholders})
            ORDER BY importance DESC, timestamp DESC
        """,
            [session_id] + importance_values,
        )

        memories = []
        for row in cursor.fetchall():
            memories.append(
                MemoryRecord(
                    id=row[0],
                    session_id=row[1],
                    timestamp=datetime.fromisoformat(row[2]),
                    content=row[3],
                    importance=MemoryImportance(row[4]),
                    keywords=json.loads(row[5]),
                    context_type=row[6],
                    embedding=json.loads(row[7]) if row[7] else None,
                    ai_source=row[8],
                )
            )

        return memories

    async def _generate_memory_summary(self, memories: List[MemoryRecord]) -> str:
        """記憶要約生成"""
        if not memories:
            return "前回セッションからの継承記憶なし"

        try:
            content_summary = "\n".join(
                [f"- {m.content[:200]}..." for m in memories[:10]]
            )

            summary_prompt = f"""
            以下の記憶内容から、次のセッションで必要な要約を作成してください：

            {content_summary}

            要約要件：
            1. 重要な指示・禁止事項
            2. 未完了タスクの継続点
            3. 重要な学習・決定事項
            4. 避けるべきミスパターン

            簡潔で実用的な要約を提供してください。
            """

            response = await self.openai_client.chat.completions.create(
                model="o3-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at creating concise, actionable memory summaries for AI systems.",
                    },
                    {"role": "user", "content": summary_prompt},
                ],
                max_tokens=500,
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Memory summary generation failed: {e}")
            return "要約生成エラー - 手動確認が必要"

    async def _identify_continuation_points(
        self, memories: List[MemoryRecord]
    ) -> List[str]:
        """作業継続点の特定"""
        task_memories = [m for m in memories if m.context_type == "task"]
        if not task_memories:
            return []

        try:
            task_content = "\n".join([f"- {m.content}" for m in task_memories])

            continuation_prompt = f"""
            以下のタスク履歴から、次のセッションで継続すべき作業点を特定してください：

            {task_content}

            特定項目：
            1. 未完了タスク
            2. 中断点
            3. 次のステップ
            4. 確認が必要な事項

            JSON形式で回答してください：
            {{
                "continuation_points": ["point1", "point2", ...],
                "next_actions": ["action1", "action2", ...],
                "verification_needed": ["item1", "item2", ...]
            }}
            """

            response = await self.openai_client.chat.completions.create(
                model="o3-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at identifying task continuation points.",
                    },
                    {"role": "user", "content": continuation_prompt},
                ],
                max_tokens=400,
            )

            continuation_data = json.loads(response.choices[0].message.content)
            return continuation_data.get("continuation_points", [])

        except Exception as e:
            logger.error(f"Continuation point identification failed: {e}")
            return ["継続点特定エラー - 手動確認が必要"]

    async def search_relevant_memories(
        self, query: str, session_id: str = None, limit: int = 10
    ) -> List[MemoryRecord]:
        """関連記憶検索"""
        # 1. クエリの埋め込み生成
        query_embedding = await self._generate_embedding(query)
        if not query_embedding:
            return []

        # 2. 類似記憶検索
        all_memories = self._get_all_memories(session_id)
        relevant_memories = []

        for memory in all_memories:
            if memory.embedding:
                similarity = self._calculate_similarity(
                    query_embedding, memory.embedding
                )
                if similarity > 0.7:  # 類似度閾値
                    memory.relevance_score = similarity
                    relevant_memories.append(memory)

        # 3. 重要度と類似度による並び替え
        relevant_memories.sort(
            key=lambda x: (x.importance.value, x.relevance_score), reverse=True
        )

        return relevant_memories[:limit]

    def _get_all_memories(self, session_id: str = None) -> List[MemoryRecord]:
        """全記憶取得"""
        if session_id:
            cursor = self.conn.execute(
                """
                SELECT * FROM enhanced_memories
                WHERE session_id = ?
                ORDER BY timestamp DESC
            """,
                (session_id,),
            )
        else:
            cursor = self.conn.execute("""
                SELECT * FROM enhanced_memories
                ORDER BY timestamp DESC
            """)

        memories = []
        for row in cursor.fetchall():
            memories.append(
                MemoryRecord(
                    id=row[0],
                    session_id=row[1],
                    timestamp=datetime.fromisoformat(row[2]),
                    content=row[3],
                    importance=MemoryImportance(row[4]),
                    keywords=json.loads(row[5]),
                    context_type=row[6],
                    embedding=json.loads(row[7]) if row[7] else None,
                    ai_source=row[8],
                )
            )

        return memories

    def _calculate_similarity(
        self, embedding1: List[float], embedding2: List[float]
    ) -> float:
        """コサイン類似度計算"""
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        except Exception:
            return 0.0

    async def generate_startup_context(self, current_session_id: str) -> Dict[str, Any]:
        """起動時コンテキスト生成"""
        # 1. 前回セッションの特定
        previous_session = self._get_latest_session(exclude_current=current_session_id)

        # 2. 記憶継承実行
        if previous_session:
            inheritance_context = await self.inherit_session_memory(
                previous_session, current_session_id
            )
        else:
            inheritance_context = {"message": "初回セッション"}

        # 3. 必須記憶の取得
        critical_memories = self._get_memories_by_importance(
            None, [MemoryImportance.CRITICAL]
        )

        # 4. 未完了タスクの取得
        pending_tasks = await self._get_pending_tasks()

        # 5. 起動時コンテキスト構築
        startup_context = {
            "session_id": current_session_id,
            "inheritance": inheritance_context,
            "critical_directives": [m.content for m in critical_memories],
            "pending_tasks": pending_tasks,
            "mistake_prevention_rules": self._get_mistake_prevention_rules(),
            "ai_collaboration_history": self._get_ai_collaboration_summary(),
            "startup_timestamp": datetime.now().isoformat(),
        }

        return startup_context

    def _get_latest_session(self, exclude_current: str = None) -> Optional[str]:
        """最新セッションID取得"""
        if exclude_current:
            cursor = self.conn.execute(
                """
                SELECT DISTINCT session_id FROM enhanced_memories
                WHERE session_id != ?
                ORDER BY timestamp DESC
                LIMIT 1
            """,
                (exclude_current,),
            )
        else:
            cursor = self.conn.execute("""
                SELECT DISTINCT session_id FROM enhanced_memories
                ORDER BY timestamp DESC
                LIMIT 1
            """)

        result = cursor.fetchone()
        return result[0] if result else None

    async def _get_pending_tasks(self) -> List[str]:
        """未完了タスク取得"""
        task_memories = self._get_memories_by_importance(
            None, [MemoryImportance.HIGH, MemoryImportance.MEDIUM]
        )

        # タスク関連記憶から未完了項目を抽出
        pending_tasks = []
        for memory in task_memories:
            if any(
                keyword in memory.content.lower()
                for keyword in ["未完了", "継続", "todo", "pending", "進行中"]
            ):
                pending_tasks.append(memory.content)

        return pending_tasks[:10]  # 最大10個

    def _get_mistake_prevention_rules(self) -> List[str]:
        """ミス防止ルール取得"""
        mistake_memories = [
            m for m in self._get_all_memories() if m.context_type == "mistake"
        ]

        rules = []
        for memory in mistake_memories:
            rules.append(f"【防止ルール】{memory.content}")

        return rules[:5]  # 最大5個

    def _get_ai_collaboration_summary(self) -> Dict[str, Any]:
        """AI連携履歴要約"""
        cursor = self.conn.execute("""
            SELECT ai_source, COUNT(*) as count, AVG(usefulness_score) as avg_usefulness
            FROM ai_collaborations
            GROUP BY ai_source
        """)

        collaboration_summary = {}
        for row in cursor.fetchall():
            collaboration_summary[row[0]] = {
                "interaction_count": row[1],
                "average_usefulness": row[2] or 0.0,
            }

        return collaboration_summary


# 使用例
async def main():
    """システムテスト"""
    # 環境変数からAPIキー取得
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY環境変数が設定されていません")
        return

    # システム初期化
    memory_system = O3EnhancedMemorySystem(openai_api_key=api_key)

    # テスト用セッションID
    test_session_id = f"test-session-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    # 1. 記憶保存テスト
    print("🧠 記憶保存テスト開始...")
    await memory_system.save_memory_with_o3_enhancement(
        "AI永続記憶システムの実装を開始しました。78回のミスを防ぐため、厳格な検証を実行します。",
        test_session_id,
        "task",
        "claude",
    )

    # 2. 起動時コンテキスト生成テスト
    print("🚀 起動時コンテキスト生成テスト...")
    context = await memory_system.generate_startup_context(test_session_id)
    print(f"✅ コンテキスト生成完了: {len(context)} 項目")

    # 3. 関連記憶検索テスト
    print("🔍 関連記憶検索テスト...")
    relevant = await memory_system.search_relevant_memories(
        "記憶システム実装", test_session_id
    )
    print(f"✅ 関連記憶検索完了: {len(relevant)} 件")

    print("🎯 o3 Enhanced Memory System テスト完了")


if __name__ == "__main__":
    asyncio.run(main())
