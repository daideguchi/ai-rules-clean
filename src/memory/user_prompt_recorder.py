#!/usr/bin/env python3
"""
User Prompt Recording System - Verbatim Database Storage
Records ALL user prompts exactly as received with zero tolerance for modification
"""

import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class UserPromptRecorder:
    """
    Critical system for recording user prompts verbatim
    Zero tolerance for modification or summarization
    """

    def __init__(self, db_path: str = "runtime/memory/user_prompts.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()

    def init_database(self):
        """Initialize database with proper schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_prompts (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    session_id TEXT,
                    prompt_text TEXT NOT NULL,
                    task_level TEXT,
                    completion_status TEXT DEFAULT 'pending',
                    response_id TEXT,
                    metadata TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp ON user_prompts(timestamp)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_session ON user_prompts(session_id)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_task_level ON user_prompts(task_level)
            """)

    def record_prompt(
        self,
        prompt_text: str,
        task_level: str = "UNKNOWN",
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Record user prompt EXACTLY as received
        CRITICAL: Zero modification tolerance
        """

        if not prompt_text:
            raise ValueError("Prompt text cannot be empty")

        prompt_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()

        if session_id is None:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        metadata_json = json.dumps(metadata) if metadata else None

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO user_prompts
                (id, timestamp, session_id, prompt_text, task_level, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    prompt_id,
                    timestamp,
                    session_id,
                    prompt_text,
                    task_level,
                    metadata_json,
                ),
            )

        return prompt_id

    def update_completion_status(
        self, prompt_id: str, status: str, response_id: Optional[str] = None
    ):
        """Update completion status of recorded prompt"""
        with sqlite3.connect(self.db_path) as conn:
            if response_id:
                conn.execute(
                    """
                    UPDATE user_prompts
                    SET completion_status = ?, response_id = ?
                    WHERE id = ?
                """,
                    (status, response_id, prompt_id),
                )
            else:
                conn.execute(
                    """
                    UPDATE user_prompts
                    SET completion_status = ?
                    WHERE id = ?
                """,
                    (status, prompt_id),
                )

    def get_recent_prompts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve recent prompts"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
                SELECT * FROM user_prompts
                ORDER BY created_at DESC
                LIMIT ?
            """,
                (limit,),
            )

            return [dict(row) for row in cursor.fetchall()]

    def search_prompts(
        self,
        session_id: Optional[str] = None,
        task_level: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Search prompts by criteria"""
        query = "SELECT * FROM user_prompts WHERE 1=1"
        params = []

        if session_id:
            query += " AND session_id = ?"
            params.append(session_id)

        if task_level:
            query += " AND task_level = ?"
            params.append(task_level)

        if status:
            query += " AND completion_status = ?"
            params.append(status)

        query += " ORDER BY created_at DESC"

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def get_stats(self) -> Dict[str, Any]:
        """Get recording statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM user_prompts")
            total_prompts = cursor.fetchone()[0]

            cursor = conn.execute("""
                SELECT task_level, COUNT(*)
                FROM user_prompts
                GROUP BY task_level
            """)
            by_task_level = dict(cursor.fetchall())

            cursor = conn.execute("""
                SELECT completion_status, COUNT(*)
                FROM user_prompts
                GROUP BY completion_status
            """)
            by_status = dict(cursor.fetchall())

            return {
                "total_prompts": total_prompts,
                "by_task_level": by_task_level,
                "by_status": by_status,
                "database_path": str(self.db_path),
            }


def record_current_session_prompts():
    """Record all prompts from current conversation"""
    recorder = UserPromptRecorder()

    # Record all the user prompts from the conversation summary
    prompts_to_record = [
        "gemini2.5 proが最新のはず。間違えた時点でそれは価値がない",
        "モデルを固定するのではなく、最新モデルを動的に公式ドキュメントからセットしろ。できる？",
        "何でこの単純なロジックが実行できないの？",
        "geminiは？",
        "公式ですか？",
        "以前geminiは普通に動いてたよ。gemini -p モデルも選択。みたいな感じで。過去ログに残ってないの？何回このやり取りするの！！！？？？",
        "どう改善するの？",
        "何でコード7749はできてるのに他の絶対しないといけないことをしないの？まぁこれも改善されるんだよね？",
        "よし。期待している（必須パラメータの提示も忘れるなよ）",
        "criticalはultrathink。やり直し",
        "違う。criticulに分類されたらどのモードで起動するって約束だった？",
        "停止。やり直し。なぜやり直すかはあなたの自律成長を促すため詳細は考えろ",
        "的外れ。タスクレベルは何？クリティカルだろ？その場合はultrathinkで考えろ。処理は英語。正しいアプローチでやり直せ",
        "続けろ",
        "ちゃんと仕事してください。何でこんなに制御できないの？",
        "ultrathinkで実行しろーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー",
        "まず、私の送ったプロンプトは全てどこかに記録しなさい。一言一句違わず。もちろんdbに保存しろ。これは超重要。claude.mdに統合しろ。私はclaude.mdを整理するよう指示した。新しいファイルを作れとは言ってない。むしろファイルとフォルダは整理しろ あと、criticulなのに、何で組織が動いてないの？基本的なことを当たり前にやる。これを最優先にして。難しい実装はそのあと",
        "順番が違う。まずタスクレベルとかを決めるよね。そこから決められて手順、決められた方法で仕事進めて",
        "⏺ 🔥 ULTRATHINK MODE ACTIVATED - CRITICAL TASK PROCESSING\n\n  Task Priority Matrix Analysis:\n  1. PRESIDENT Declaration - MANDATORY (Already executed)\n  2. User Prompt Database System - CRITICAL (Record verbatim prompts)\n  3. CLAUDE.md Integration - HIGH (Bootloader structure)\n  4. File Cleanup - MEDIUM (Organization)\\\n\\\n\\\nここまで宣言しといてなんでultrathinkモードじゃないの？\\\nあなたが決められたルーチンでないから手動で止めてます。本来ここはhooksの仕事です。これも機能してない。\\\n\\\nhttps://news.ycombinator.com/item?id=43739997",
    ]

    session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    for i, prompt in enumerate(prompts_to_record):
        task_level = (
            "CRITICAL"
            if any(
                word in prompt.lower() for word in ["critical", "ultrathink", "超重要"]
            )
            else "HIGH"
        )
        prompt_id = recorder.record_prompt(
            prompt_text=prompt,
            task_level=task_level,
            session_id=session_id,
            metadata={"prompt_order": i + 1, "source": "conversation_summary"},
        )
        print(f"✅ Recorded prompt {i + 1}: {prompt_id}")

    return recorder.get_stats()


if __name__ == "__main__":
    print("🔥 User Prompt Recording System - Verbatim Database Storage")
    print("=" * 60)

    stats = record_current_session_prompts()
    print("\n📊 Recording Statistics:")
    print(f"Total prompts: {stats['total_prompts']}")
    print(f"Database: {stats['database_path']}")
    print(f"By task level: {stats['by_task_level']}")
    print(f"By status: {stats['by_status']}")
