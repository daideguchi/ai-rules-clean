#!/usr/bin/env python3
"""
🌊 CSA文脈システム強化 - データ蓄積による効果向上
=============================================

【目的】
- 統一ログからCSA文脈データ生成
- 実際の作業履歴をイベント化
- 文脈検索の効果向上

【実装内容】
- 統一ログ → CSAイベント変換
- 実作業パターンの学習
- 文脈継続性の向上
"""

import json
import uuid
from typing import Any, Dict, List, Optional

import openai
import psycopg2
from psycopg2.extras import RealDictCursor


class CSADataAccumulator:
    """CSA文脈データ蓄積システム"""

    def __init__(self):
        self.db_config = {
            "host": "localhost",
            "database": "president_ai",
            "user": "dd",
            "password": "",
            "port": 5432,
        }
        self.embedding_model = "text-embedding-ada-002"
        self.session_id = str(uuid.uuid4())

    def convert_logs_to_csa_events(self, limit: int = 100) -> Dict[str, Any]:
        """統一ログをCSAイベントに変換"""

        try:
            conn = psycopg2.connect(**self.db_config, cursor_factory=RealDictCursor)
            cur = conn.cursor()

            # 統一ログから意味のあるエントリを取得
            cur.execute(
                """
                SELECT
                    timestamp,
                    source_file,
                    log_level,
                    component,
                    message,
                    structured_data
                FROM unified_logs
                WHERE log_level IN ('ERROR', 'WARNING', 'INFO')
                  AND LENGTH(message) > 20
                ORDER BY timestamp DESC
                LIMIT %s;
            """,
                (limit,),
            )

            log_entries = cur.fetchall()

            converted_events = 0
            for log_entry in log_entries:
                # ログエントリをCSAイベントに変換
                csa_event = self._convert_log_to_csa_event(log_entry)
                if csa_event:
                    # CSAイベントとしてデータベースに保存
                    success = self._save_csa_event(cur, csa_event)
                    if success:
                        converted_events += 1

            conn.commit()
            cur.close()
            conn.close()

            return {
                "status": "success",
                "processed_logs": len(log_entries),
                "converted_events": converted_events,
                "session_id": self.session_id,
            }

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _convert_log_to_csa_event(
        self, log_entry: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """ログエントリをCSAイベントに変換"""

        message = log_entry["message"]
        component = log_entry["component"]

        # イベントタイプの推定
        event_type = self._infer_event_type(message, log_entry["log_level"])

        # 意味のないイベントはスキップ
        if not event_type:
            return None

        # メタデータ構築
        metadata = {
            "original_log_level": log_entry["log_level"],
            "source_component": component,
            "source_file": log_entry["source_file"],
        }

        # structured_dataがあれば追加
        if log_entry["structured_data"]:
            try:
                structured = (
                    json.loads(log_entry["structured_data"])
                    if isinstance(log_entry["structured_data"], str)
                    else log_entry["structured_data"]
                )
                metadata.update(structured)
            except (json.JSONDecodeError, ValueError):
                pass

        # ベクトル埋め込み生成
        embedding = self._generate_embedding(f"{event_type}: {message}")

        return {
            "id": str(uuid.uuid4()),
            "timestamp": log_entry["timestamp"],
            "source": "system_log",
            "event_type": event_type,
            "content": message,
            "metadata": metadata,
            "session_id": self.session_id,
            "vector_embedding": embedding,
        }

    def _infer_event_type(self, message: str, log_level: str) -> Optional[str]:
        """ログメッセージからイベントタイプを推定"""

        message_lower = message.lower()

        # エラー関連
        if (
            log_level == "ERROR"
            or "error" in message_lower
            or "failed" in message_lower
        ):
            if "connection" in message_lower or "database" in message_lower:
                return "database_error"
            elif "file" in message_lower:
                return "file_error"
            else:
                return "system_error"

        # 警告関連
        if log_level == "WARNING" or "warning" in message_lower or "重複" in message:
            return "warning_alert"

        # システム操作
        if any(
            keyword in message_lower
            for keyword in ["設定", "初期化", "起動", "setup", "init", "start"]
        ):
            return "system_operation"

        # ファイル操作
        if any(
            keyword in message_lower
            for keyword in ["ファイル", "file", "作成", "削除", "create", "delete"]
        ):
            return "file_operation"

        # データベース操作
        if any(
            keyword in message_lower
            for keyword in ["database", "postgresql", "データベース", "テーブル"]
        ):
            return "database_operation"

        # 重複検出
        if "重複" in message or "duplicate" in message_lower:
            return "duplicate_detection"

        # プロセス管理
        if any(
            keyword in message_lower
            for keyword in ["プロセス", "process", "実行", "execute"]
        ):
            return "process_management"

        # 一般的な情報ログは除外
        if len(message) < 30:
            return None

        return "general_activity"

    def _generate_embedding(self, text: str) -> List[float]:
        """テキストのベクトル埋め込み生成"""
        try:
            client = openai.OpenAI()
            response = client.embeddings.create(model=self.embedding_model, input=text)
            return response.data[0].embedding
        except Exception as e:
            print(f"Embedding generation failed: {e}")
            return [0.0] * 1536

    def _save_csa_event(self, cursor, event: Dict[str, Any]) -> bool:
        """CSAイベントを保存"""
        try:
            cursor.execute(
                """
                INSERT INTO context_stream
                (id, timestamp, source, event_type, content, metadata, session_id, vector_embedding)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING;
            """,
                (
                    event["id"],
                    event["timestamp"],
                    event["source"],
                    event["event_type"],
                    event["content"],
                    json.dumps(event["metadata"]),
                    event["session_id"],
                    event["vector_embedding"],
                ),
            )
            return True
        except Exception as e:
            print(f"CSA event save failed: {e}")
            return False

    def enhance_context_search(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """強化された文脈検索"""

        # クエリをベクトル化
        query_embedding = self._generate_embedding(query)

        try:
            conn = psycopg2.connect(**self.db_config, cursor_factory=RealDictCursor)
            cur = conn.cursor()

            # 複合検索: ベクトル類似度 + キーワード + 時系列
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
                WHERE vector_embedding IS NOT NULL
                  AND (
                    1 - (vector_embedding <=> %s::vector) > 0.6
                    OR content ILIKE %s
                    OR event_type ILIKE %s
                  )
                ORDER BY
                    (1 - (vector_embedding <=> %s::vector)) DESC,
                    timestamp DESC
                LIMIT %s;
            """,
                (
                    query_embedding,
                    query_embedding,
                    f"%{query}%",
                    f"%{query}%",
                    query_embedding,
                    limit,
                ),
            )

            results = cur.fetchall()
            cur.close()
            conn.close()

            # 結果の分類
            categorized_results = self._categorize_search_results(
                [dict(row) for row in results]
            )

            return {
                "status": "success",
                "query": query,
                "total_results": len(results),
                "categorized_results": categorized_results,
                "search_metadata": {
                    "search_type": "enhanced_semantic_temporal",
                    "embedding_model": self.embedding_model,
                },
            }

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _categorize_search_results(
        self, results: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """検索結果をカテゴリ別に分類"""
        categories = {
            "errors": [],
            "operations": [],
            "file_activities": [],
            "database_activities": [],
            "warnings": [],
            "general": [],
        }

        for result in results:
            event_type = result["event_type"]

            if "error" in event_type:
                categories["errors"].append(result)
            elif "operation" in event_type:
                categories["operations"].append(result)
            elif "file" in event_type:
                categories["file_activities"].append(result)
            elif "database" in event_type:
                categories["database_activities"].append(result)
            elif "warning" in event_type:
                categories["warnings"].append(result)
            else:
                categories["general"].append(result)

        return categories

    def get_csa_enhancement_stats(self) -> Dict[str, Any]:
        """CSA強化統計"""
        try:
            conn = psycopg2.connect(**self.db_config, cursor_factory=RealDictCursor)
            cur = conn.cursor()

            # 基本統計
            cur.execute("""
                SELECT
                    COUNT(*) as total_events,
                    COUNT(DISTINCT event_type) as unique_event_types,
                    COUNT(DISTINCT source) as unique_sources,
                    COUNT(DISTINCT session_id) as unique_sessions,
                    MIN(timestamp) as earliest_event,
                    MAX(timestamp) as latest_event
                FROM context_stream;
            """)

            basic_stats = cur.fetchone()

            # イベントタイプ別統計
            cur.execute("""
                SELECT event_type, COUNT(*) as count
                FROM context_stream
                GROUP BY event_type
                ORDER BY count DESC;
            """)

            event_type_stats = cur.fetchall()

            # ソース別統計
            cur.execute("""
                SELECT source, COUNT(*) as count
                FROM context_stream
                GROUP BY source
                ORDER BY count DESC;
            """)

            source_stats = cur.fetchall()

            cur.close()
            conn.close()

            return {
                "status": "success",
                "basic_stats": dict(basic_stats) if basic_stats else {},
                "event_type_distribution": [dict(row) for row in event_type_stats],
                "source_distribution": [dict(row) for row in source_stats],
            }

        except Exception as e:
            return {"status": "error", "error": str(e)}


def main():
    """メイン実行 - CSA強化システム"""
    print("🌊 CSA文脈システム強化 - データ蓄積開始")

    accumulator = CSADataAccumulator()

    # 1. ログからCSAイベント変換
    print("\\n1️⃣ 統一ログ → CSAイベント変換")
    conversion_result = accumulator.convert_logs_to_csa_events(limit=50)
    print(f"変換結果: {conversion_result['status']}")

    if conversion_result["status"] == "success":
        print(f"   処理ログ数: {conversion_result['processed_logs']}")
        print(f"   変換イベント数: {conversion_result['converted_events']}")
        print(f"   セッションID: {conversion_result['session_id'][:8]}...")
    else:
        print(f"   エラー: {conversion_result['error']}")
        return

    # 2. 強化された文脈検索テスト
    print("\\n2️⃣ 強化された文脈検索テスト")
    test_queries = [
        "データベース接続エラー",
        "ファイル操作",
        "重複検出",
        "システム初期化",
    ]

    for query in test_queries:
        search_result = accumulator.enhance_context_search(query, limit=5)
        print(f"\\n   検索: '{query}'")
        print(f"   結果: {search_result.get('total_results', 0)}件")

        if search_result["status"] == "success":
            categorized = search_result["categorized_results"]
            for category, events in categorized.items():
                if events:
                    print(f"     {category}: {len(events)}件")
                    for event in events[:2]:  # 最初の2件表示
                        print(
                            f"       - [{event['event_type']}] {event['content'][:50]}..."
                        )

    # 3. CSA強化統計
    print("\\n3️⃣ CSA強化統計")
    stats_result = accumulator.get_csa_enhancement_stats()
    print(f"統計: {stats_result['status']}")

    if stats_result["status"] == "success":
        basic = stats_result["basic_stats"]
        print(f"   総イベント数: {basic.get('total_events', 0)}")
        print(f"   イベントタイプ数: {basic.get('unique_event_types', 0)}")
        print(f"   セッション数: {basic.get('unique_sessions', 0)}")

        if basic.get("earliest_event"):
            print(f"   最古イベント: {basic['earliest_event']}")
        if basic.get("latest_event"):
            print(f"   最新イベント: {basic['latest_event']}")

        print("\\n   イベントタイプ分布:")
        for event_type in stats_result["event_type_distribution"][:5]:
            print(f"     {event_type['event_type']}: {event_type['count']}件")

        print("\\n   ソース分布:")
        for source in stats_result["source_distribution"]:
            print(f"     {source['source']}: {source['count']}件")

    print("\\n✅ CSA文脈システム強化完了")
    print("📍 統一ログデータによる文脈検索効果向上")


if __name__ == "__main__":
    main()
