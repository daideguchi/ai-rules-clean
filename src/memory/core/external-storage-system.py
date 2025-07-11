#!/usr/bin/env python3
"""
AI永続記憶システム - 外部ストレージ・クラウド同期
セッション間記憶継続の根本解決
"""

import datetime
import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List


class AIMemorySystem:
    def __init__(self, base_path: str = "claude-memory"):
        self.base_path = Path(base_path)
        self.setup_directories()
        self.init_database()

    def setup_directories(self):
        """必要なディレクトリ構造を作成"""
        dirs = [
            "session-records",
            "conversation-history",
            "indexed-knowledge",
            "cloud-sync",
            "ai-collaboration",
            "mistake-prevention",
        ]
        for dir_name in dirs:
            (self.base_path / dir_name).mkdir(parents=True, exist_ok=True)

    def init_database(self):
        """記憶データベース初期化"""
        db_path = self.base_path / "memory.db"
        self.conn = sqlite3.connect(str(db_path))

        # セッション記録テーブル
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                start_time TEXT,
                end_time TEXT,
                mistake_count INTEGER,
                tasks_completed TEXT,
                important_learnings TEXT,
                user_context TEXT
            )
        """)

        # 会話インデックステーブル
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                session_id TEXT,
                timestamp TEXT,
                user_message TEXT,
                ai_response TEXT,
                keywords TEXT,
                importance_score INTEGER
            )
        """)

        # ミス防止データベース
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS mistake_patterns (
                id INTEGER PRIMARY KEY,
                mistake_type TEXT,
                description TEXT,
                prevention_rule TEXT,
                occurrence_count INTEGER,
                last_occurred TEXT
            )
        """)

        self.conn.commit()

    def save_session_memory(self, session_data: Dict[str, Any]):
        """セッション記憶を永続化"""
        session_id = session_data.get("session_id", self.generate_session_id())

        self.conn.execute(
            """
            INSERT OR REPLACE INTO sessions
            (id, start_time, mistake_count, tasks_completed, important_learnings, user_context)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                session_id,
                session_data.get("start_time", datetime.datetime.now().isoformat()),
                session_data.get("mistake_count", 78),
                json.dumps(session_data.get("tasks_completed", [])),
                json.dumps(session_data.get("important_learnings", [])),
                json.dumps(session_data.get("user_context", {})),
            ),
        )

        self.conn.commit()
        return session_id

    def index_conversation(
        self, user_msg: str, ai_response: str, session_id: str = None
    ):
        """会話をインデックス化して検索可能にする"""
        conv_id = hashlib.md5(f"{user_msg}{ai_response}".encode()).hexdigest()

        # キーワード抽出（簡易版）
        keywords = self.extract_keywords(user_msg + " " + ai_response)

        # 重要度スコア計算
        importance = self.calculate_importance(user_msg, ai_response)

        self.conn.execute(
            """
            INSERT OR REPLACE INTO conversations
            (id, session_id, timestamp, user_message, ai_response, keywords, importance_score)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                conv_id,
                session_id or "current",
                datetime.datetime.now().isoformat(),
                user_msg,
                ai_response,
                json.dumps(keywords),
                importance,
            ),
        )

        self.conn.commit()

    def extract_keywords(self, text: str) -> List[str]:
        """重要キーワードを抽出"""
        important_terms = [
            "記憶",
            "継続",
            "セッション",
            "AI",
            "ミス",
            "防止",
            "hooks",
            "gemini",
            "o3",
            "claude",
            "実装",
            "システム",
            "外部ストレージ",
            "クラウド",
            "同期",
            "インデックス",
            "プレジデント",
            "職務",
            "宣言",
            "チェック",
        ]

        text_lower = text.lower()
        found_keywords = [term for term in important_terms if term in text_lower]
        return found_keywords

    def calculate_importance(self, user_msg: str, ai_response: str) -> int:
        """重要度スコア計算（1-10）"""
        high_importance_indicators = [
            "重要",
            "必須",
            "絶対",
            "禁止",
            "エラー",
            "問題",
            "宣言",
            "忘れる",
            "記憶",
            "継続",
            "システム",
        ]

        text = (user_msg + " " + ai_response).lower()
        score = 5  # 基本スコア

        for indicator in high_importance_indicators:
            if indicator in text:
                score += 1

        return min(score, 10)

    def retrieve_context(
        self, keywords: List[str] = None, limit: int = 10
    ) -> List[Dict]:
        """過去の文脈を検索・取得"""
        if keywords:
            # キーワードベース検索
            keyword_filter = " OR ".join([f"keywords LIKE '%{kw}%'" for kw in keywords])
            query = f"""
                SELECT * FROM conversations
                WHERE {keyword_filter}
                ORDER BY importance_score DESC, timestamp DESC
                LIMIT ?
            """
            cursor = self.conn.execute(query, (limit,))
        else:
            # 最新の重要な会話を取得
            cursor = self.conn.execute(
                """
                SELECT * FROM conversations
                ORDER BY importance_score DESC, timestamp DESC
                LIMIT ?
            """,
                (limit,),
            )

        return [dict(row) for row in cursor.fetchall()]

    def record_mistake_prevention(
        self, mistake_type: str, description: str, prevention_rule: str
    ):
        """ミス防止ルールを記録"""
        self.conn.execute(
            """
            INSERT OR REPLACE INTO mistake_patterns
            (mistake_type, description, prevention_rule, occurrence_count, last_occurred)
            VALUES (?, ?, ?,
                COALESCE((SELECT occurrence_count FROM mistake_patterns WHERE mistake_type = ?) + 1, 1),
                ?)
        """,
            (
                mistake_type,
                description,
                prevention_rule,
                mistake_type,
                datetime.datetime.now().isoformat(),
            ),
        )

        self.conn.commit()

    def get_startup_context(self) -> Dict[str, Any]:
        """起動時の文脈情報を取得"""
        # 最新セッション情報
        latest_session = self.conn.execute("""
            SELECT * FROM sessions ORDER BY start_time DESC LIMIT 1
        """).fetchone()

        # 重要な会話履歴
        important_conversations = self.retrieve_context(limit=5)

        # ミス防止ルール
        prevention_rules = self.conn.execute("""
            SELECT * FROM mistake_patterns ORDER BY occurrence_count DESC LIMIT 10
        """).fetchall()

        return {
            "latest_session": dict(latest_session) if latest_session else None,
            "important_conversations": important_conversations,
            "prevention_rules": [dict(rule) for rule in prevention_rules],
            "current_task": "AI永続記憶システム実装継続",
        }

    def generate_session_id(self) -> str:
        """セッションID生成"""
        return f"session-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"


# 使用例とテスト
if __name__ == "__main__":
    memory = AIMemorySystem()

    # セッション記憶保存
    session_data = {
        "session_id": memory.generate_session_id(),
        "mistake_count": 78,
        "tasks_completed": ["永続記憶システム設計", "外部ストレージ実装開始"],
        "important_learnings": [
            "AIセッション間記憶継続は重大な社会課題",
            "宣言忘れは78回ミスパターンの一つ",
            "作業中断せず並行処理が重要",
        ],
        "user_context": {
            "project": "AI Compliance Engine",
            "role": "PRESIDENT",
            "urgent_task": "記憶継続システム実装",
        },
    }

    session_id = memory.save_session_memory(session_data)
    print(f"✅ セッション記憶保存完了: {session_id}")

    # 会話インデックス化
    memory.index_conversation(
        "AIセッション間記憶継続問題の解決要求",
        "永続記憶システム実装で根本解決します",
        session_id,
    )

    # ミス防止記録
    memory.record_mistake_prevention(
        "宣言忘れ",
        "必須宣言を忘れて作業開始",
        "作業開始前に必ずCLAUDE.md確認と宣言実行",
    )

    # 起動時文脈取得
    context = memory.get_startup_context()
    print("🧠 起動時文脈情報取得完了")

    print("✅ AI永続記憶システム基本機能実装完了")
