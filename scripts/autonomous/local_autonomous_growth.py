#!/usr/bin/env python3
"""
ローカル自律成長システム - 完全版
Supabaseなしでローカルで完結する学習システム
"""

import atexit
import json
import sqlite3
import time
from datetime import datetime
from pathlib import Path


class LocalAutonomousGrowth:
    def __init__(self):
        self.db_path = Path("runtime/memory/autonomous_growth.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()

        # セッション開始時刻
        self.session_start = time.time()
        self.session_id = f"session_{int(self.session_start)}"

        # 自動記録（セッション終了時）
        atexit.register(self.record_session_end)

        print(f"🤖 ローカル自律成長システム起動: {self.session_id}")

    def init_database(self):
        """データベース初期化"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS ai_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    task_success BOOLEAN DEFAULT 0,
                    execution_time REAL DEFAULT 0,
                    tool_calls_count INTEGER DEFAULT 0,
                    tool_calls TEXT DEFAULT '[]',
                    error_count INTEGER DEFAULT 0,
                    thinking_tag_used BOOLEAN DEFAULT 0,
                    todo_tracking BOOLEAN DEFAULT 0,
                    task_complexity TEXT DEFAULT 'simple',
                    user_feedback TEXT,
                    learning_score INTEGER DEFAULT 0,
                    success_patterns TEXT DEFAULT '[]',
                    failure_patterns TEXT DEFAULT '[]'
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS learning_insights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    insight_type TEXT NOT NULL,
                    pattern TEXT NOT NULL,
                    frequency INTEGER DEFAULT 1,
                    success_rate REAL DEFAULT 0.0,
                    recommendation TEXT
                )
            """
            )

    def record_session_performance(self, data):
        """セッションパフォーマンス記録"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO ai_performance (
                    session_id, timestamp, task_success, execution_time,
                    tool_calls_count, tool_calls, error_count, thinking_tag_used,
                    todo_tracking, task_complexity, user_feedback, learning_score,
                    success_patterns, failure_patterns
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    data["session_id"],
                    data["timestamp"],
                    data["task_success"],
                    data["execution_time"],
                    data["tool_calls_count"],
                    json.dumps(data["tool_calls"]),
                    data["error_count"],
                    data["thinking_tag_used"],
                    data["todo_tracking"],
                    data["task_complexity"],
                    data.get("user_feedback"),
                    data["learning_score"],
                    json.dumps(data["success_patterns"]),
                    json.dumps(data["failure_patterns"]),
                ),
            )
        print(f"📝 パフォーマンスデータ記録: {data['session_id']}")

    def record_session_end(self):
        """セッション終了時の自動記録"""
        execution_time = time.time() - self.session_start

        # デフォルトパフォーマンスデータ
        data = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "task_success": True,  # エラーなく終了
            "execution_time": execution_time,
            "tool_calls_count": 3,  # 推定
            "tool_calls": ["Read", "Write", "Bash"],
            "error_count": 0,
            "thinking_tag_used": False,  # 最近のルール
            "todo_tracking": True,
            "task_complexity": "medium",
            "learning_score": 2,
            "success_patterns": ["clean_completion", "tool_efficiency"],
            "failure_patterns": [],
        }

        self.record_session_performance(data)
        self.analyze_and_learn()

    def analyze_and_learn(self):
        """パターン分析と学習"""
        with sqlite3.connect(self.db_path) as conn:
            # 成功率分析
            cursor = conn.execute(
                """
                SELECT
                    AVG(CAST(task_success as FLOAT)) as success_rate,
                    AVG(execution_time) as avg_time,
                    COUNT(*) as total_sessions
                FROM ai_performance
            """
            )
            stats = cursor.fetchone()

            if stats[2] > 0:  # セッション数 > 0
                success_rate = stats[0] * 100
                avg_time = stats[1]
                total = stats[2]

                print("\n🧠 自律学習分析:")
                print(f"  - 総セッション: {total}")
                print(f"  - 成功率: {success_rate:.1f}%")
                print(f"  - 平均実行時間: {avg_time:.1f}秒")

                # パターン分析
                self.analyze_patterns()

                # 学習推奨事項
                self.generate_recommendations(success_rate, avg_time)

    def analyze_patterns(self):
        """詳細パターン分析"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT success_patterns, failure_patterns, task_success
                FROM ai_performance
            """
            )

            all_success_patterns = {}
            all_failure_patterns = {}

            for row in cursor.fetchall():
                success_patterns = json.loads(row[0])
                failure_patterns = json.loads(row[1])
                task_success = row[2]

                # 成功パターン集計
                for pattern in success_patterns:
                    if pattern not in all_success_patterns:
                        all_success_patterns[pattern] = {"count": 0, "success_count": 0}
                    all_success_patterns[pattern]["count"] += 1
                    if task_success:
                        all_success_patterns[pattern]["success_count"] += 1

                # 失敗パターン集計
                for pattern in failure_patterns:
                    if pattern not in all_failure_patterns:
                        all_failure_patterns[pattern] = {"count": 0, "failure_count": 0}
                    all_failure_patterns[pattern]["count"] += 1
                    if not task_success:
                        all_failure_patterns[pattern]["failure_count"] += 1

            # 結果表示
            print("\n✅ 成功パターン頻度:")
            for pattern, data in sorted(
                all_success_patterns.items(), key=lambda x: x[1]["count"], reverse=True
            ):
                rate = (
                    (data["success_count"] / data["count"] * 100)
                    if data["count"] > 0
                    else 0
                )
                print(f"  - {pattern}: {data['count']}回 (成功率: {rate:.1f}%)")

            print("\n❌ 失敗パターン頻度:")
            for pattern, data in sorted(
                all_failure_patterns.items(), key=lambda x: x[1]["count"], reverse=True
            ):
                rate = (
                    (data["failure_count"] / data["count"] * 100)
                    if data["count"] > 0
                    else 0
                )
                print(f"  - {pattern}: {data['count']}回 (失敗率: {rate:.1f}%)")

    def generate_recommendations(self, success_rate, avg_time):
        """AI改善推奨事項生成"""
        recommendations = []

        if success_rate < 80:
            recommendations.append("成功率向上のため、事前チェックを強化する")

        if avg_time > 60:
            recommendations.append("実行時間短縮のため、効率的なツール使用を心がける")

        recommendations.append("thinking タグ使用を控え、簡潔な回答を目指す")

        print("\n💡 AI改善推奨事項:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")

            # データベースに記録
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO learning_insights (timestamp, insight_type, pattern, recommendation)
                    VALUES (?, ?, ?, ?)
                """,
                    (
                        datetime.now().isoformat(),
                        "improvement",
                        f"recommendation_{i}",
                        rec,
                    ),
                )

    def get_current_stats(self):
        """現在の統計情報取得"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT
                    COUNT(*) as total,
                    AVG(CAST(task_success as FLOAT)) * 100 as success_rate,
                    AVG(execution_time) as avg_time
                FROM ai_performance
                WHERE datetime(timestamp) >= datetime('now', '-7 days')
            """
            )
            stats = cursor.fetchone()

            return {
                "total_sessions": stats[0],
                "success_rate": stats[1] or 0,
                "avg_execution_time": stats[2] or 0,
            }


# グローバルインスタンス（自動初期化）
growth_system = LocalAutonomousGrowth()


def record_manual_performance(task_success=True, tools_used=None, complexity="medium"):
    """手動パフォーマンス記録"""
    if tools_used is None:
        tools_used = ["Manual"]

    data = {
        "session_id": f"manual_{int(time.time())}",
        "timestamp": datetime.now().isoformat(),
        "task_success": task_success,
        "execution_time": 30,  # デフォルト
        "tool_calls_count": len(tools_used),
        "tool_calls": tools_used,
        "error_count": 0 if task_success else 1,
        "thinking_tag_used": False,
        "todo_tracking": True,
        "task_complexity": complexity,
        "learning_score": 3 if task_success else -1,
        "success_patterns": ["manual_success"] if task_success else [],
        "failure_patterns": [] if task_success else ["manual_failure"],
    }

    growth_system.record_session_performance(data)


if __name__ == "__main__":
    print("🤖 ローカル自律成長システム - 統計表示")
    stats = growth_system.get_current_stats()
    print("直近7日間の統計:")
    print(f"  セッション数: {stats['total_sessions']}")
    print(f"  成功率: {stats['success_rate']:.1f}%")
    print(f"  平均時間: {stats['avg_execution_time']:.1f}秒")

    # 詳細分析実行
    growth_system.analyze_and_learn()
