#!/usr/bin/env python3
"""
Session Recommendations & Todo Generator
Generate next session recommendations and pending todos
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List


class SessionRecommendations:
    def __init__(self):
        self.project_root = Path(__file__).resolve().parents[2]
        self.runtime_dir = self.project_root / "runtime"

    def get_active_todos(self) -> List[Dict[str, Any]]:
        """Get current active todos"""
        try:
            todos_file = self.runtime_dir / "active_todos.json"
            if todos_file.exists():
                with open(todos_file, encoding="utf-8") as f:
                    todos = json.load(f)
                    return [
                        todo
                        for todo in todos
                        if todo.get("status") in ["pending", "in_progress"]
                    ]
            return []
        except Exception:
            return []

    def analyze_system_status(self) -> Dict[str, Any]:
        """Analyze current system status for recommendations"""
        status = {
            "db_issues": [],
            "pending_integrations": [],
            "optimization_opportunities": [],
            "security_concerns": [],
        }

        # Check DB status
        sqlite_db = self.runtime_dir / "memory" / "forever_ledger.db"
        if not sqlite_db.exists():
            status["db_issues"].append("SQLite database initialization needed")

        # Check PostgreSQL config
        pg_config = self.project_root / "config" / "postgresql"
        if pg_config.exists():
            status["pending_integrations"].append("PostgreSQL integration testing")

        # Check system performance logs
        logs_dir = self.runtime_dir / "logs"
        if logs_dir.exists():
            log_files = list(logs_dir.glob("*.log"))
            if len(log_files) > 20:
                status["optimization_opportunities"].append(
                    "Log file cleanup and archiving"
                )

        return status

    def generate_recommendations(self) -> List[str]:
        """Generate next session recommendations"""
        recommendations = []

        # Based on system analysis
        status = self.analyze_system_status()

        if status["db_issues"]:
            recommendations.append(
                "🔧 Database Setup: Initialize missing DB connections"
            )

        if status["pending_integrations"]:
            recommendations.append(
                "🔗 Integration Testing: Verify PostgreSQL connectivity"
            )

        if status["optimization_opportunities"]:
            recommendations.append(
                "⚡ System Optimization: Clean up logs and improve performance"
            )

        # Based on active todos
        todos = self.get_active_todos()
        if len(todos) > 5:
            recommendations.append(
                f"📋 Todo Management: {len(todos)} pending tasks need prioritization"
            )

        # AI organization recommendations
        try:
            # Check if multiagent session is running
            import subprocess

            result = subprocess.run(
                ["tmux", "has-session", "-t", "multiagent"], capture_output=True
            )
            if result.returncode == 0:
                recommendations.append(
                    "🤖 AI Collaboration: Continue leveraging active AI organization"
                )
            else:
                recommendations.append(
                    "🚀 AI Organization: Consider launching for complex tasks"
                )
        except Exception:
            pass

        # Default recommendations if none generated
        if not recommendations:
            recommendations = [
                "✅ System Health: All systems operational - ready for new tasks",
                "🎯 Focus Areas: Consider code quality improvements or new features",
            ]

        return recommendations[:4]  # Limit to 4 recommendations

    def generate_session_summary(self) -> str:
        """Generate complete session ending summary"""
        todos = self.get_active_todos()
        recommendations = self.generate_recommendations()

        summary_lines = ["", "## 📋 **次回セッションへの推奨事項**"]

        for i, rec in enumerate(recommendations, 1):
            summary_lines.append(f"{i}. {rec}")

        summary_lines.extend(["", "## ✅ **現在のTodo状況**"])

        if todos:
            summary_lines.append(f"**アクティブタスク数**: {len(todos)}")
            summary_lines.append("**主要Todo**:")
            for todo in todos[:3]:  # Show top 3
                priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(
                    todo.get("priority", "medium"), "⚪"
                )
                summary_lines.append(f"- {priority_emoji} {todo['content'][:60]}...")

            if len(todos) > 3:
                summary_lines.append(f"- ... および{len(todos) - 3}件の追加タスク")
        else:
            summary_lines.append("**現在のTodo**: なし - 新しいタスクの受付準備完了")

        summary_lines.extend(
            [
                "",
                "---",
                "**次回セッション開始時**: 上記推奨事項を確認してから作業開始してください",
            ]
        )

        return "\n".join(summary_lines)


def main():
    """Main execution"""
    recommender = SessionRecommendations()

    if len(sys.argv) > 1 and sys.argv[1] == "summary":
        print(recommender.generate_session_summary())
    else:
        recommendations = recommender.generate_recommendations()
        print("📋 **Next Session Recommendations:**")
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")


if __name__ == "__main__":
    main()
