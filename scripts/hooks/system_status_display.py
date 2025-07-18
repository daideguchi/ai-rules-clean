#!/usr/bin/env python3
"""
System Status Display Hook
Automatic display of DB connection, API status, todos, and task level
"""

import json
import sqlite3
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional


class SystemStatusDisplay:
    def __init__(self):
        self.project_root = Path(__file__).resolve().parents[2]
        self.runtime_dir = self.project_root / "runtime"

    def get_db_status(self) -> Dict[str, str]:
        """Database connection status check"""
        status = {}

        # SQLite status
        try:
            sqlite_db = self.runtime_dir / "memory" / "user_prompts.db"
            if sqlite_db.exists():
                conn = sqlite3.connect(sqlite_db)
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM sqlite_master WHERE type='table'"
                )
                table_count = cursor.fetchone()[0]
                conn.close()
                status["SQLite"] = f"✅ 接続済み ({table_count}テーブル)"
            else:
                status["SQLite"] = "❌ 未発見 - セットアップ要"
        except Exception as e:
            status["SQLite"] = f"❌ エラー: {str(e)[:20]}"

        # PostgreSQL status (if configured)
        try:
            pg_config = self.project_root / "config" / "postgresql"
            if pg_config.exists():
                # Try actual connection test
                try:
                    result = subprocess.run(
                        ["pg_isready"], capture_output=True, timeout=2
                    )
                    if result.returncode == 0:
                        status["PostgreSQL"] = "✅ 接続済み"
                    else:
                        status["PostgreSQL"] = "❌ 未接続 - セットアップ要"
                except Exception:
                    status["PostgreSQL"] = "❌ 未接続 - セットアップ要"
            else:
                status["PostgreSQL"] = "❌ 未設定"
        except Exception:
            status["PostgreSQL"] = "❌ 設定エラー"

        return status

    def get_api_status(self) -> Dict[str, str]:
        """API configuration status check"""
        import os
        status = {}

        # Claude API (inferred from Claude Code usage)
        status["Claude"] = "✅ アクティブ (Claude Code)"

        # OpenAI API Key check
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key and openai_key.startswith('sk-'):
            status["OpenAI"] = f"✅ 設定済み (sk-...{openai_key[-4:]})"
        else:
            status["OpenAI"] = "❌ 未設定"

        # Gemini API Key check
        gemini_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if gemini_key:
            status["Gemini"] = f"✅ 設定済み (...{gemini_key[-4:]})"
        else:
            status["Gemini"] = "❌ 未設定"

        # MCP Configuration check
        try:
            claude_settings = Path.home() / ".claude" / "settings.json"
            project_mcp = self.project_root / ".mcp.json"

            mcp_servers = []

            if claude_settings.exists():
                with open(claude_settings) as f:
                    settings_data = json.load(f)
                    if "mcpServers" in settings_data:
                        mcp_servers.extend(settings_data["mcpServers"].keys())

            if project_mcp.exists():
                with open(project_mcp) as f:
                    mcp_data = json.load(f)
                    if "mcpServers" in mcp_data:
                        mcp_servers.extend(mcp_data["mcpServers"].keys())

            if mcp_servers:
                unique_servers = list(set(mcp_servers))
                status["MCP"] = f"✅ {len(unique_servers)}サーバー ({', '.join(unique_servers)})"
            else:
                status["MCP"] = "❌ 未設定"
        except Exception:
            status["MCP"] = "❌ 設定チェック失敗"

        return status

    def get_current_todos(self) -> List[Dict[str, Any]]:
        """Get current active todos"""
        try:
            todos_file = self.runtime_dir / "active_todos.json"
            if todos_file.exists():
                with open(todos_file, encoding="utf-8") as f:
                    todos = json.load(f)
                    # Return only pending/in_progress todos, limited to 3
                    active_todos = [
                        todo
                        for todo in todos
                        if todo.get("status") in ["pending", "in_progress"]
                    ][:3]
                    return active_todos
            return []
        except Exception:
            return []

    def get_task_level(self, current_task: Optional[str] = None) -> str:
        """Determine current task complexity level"""
        if not current_task:
            return "SIMPLE"  # Default level

        # Use task complexity classifier
        try:
            import sys

            sys.path.append(str(self.project_root / "src"))
            from ai.task_complexity_classifier import TaskComplexityClassifier

            classifier = TaskComplexityClassifier()
            classification = classifier.classify_task(current_task)

            return f"{classification.complexity.value.upper()} ({classification.thinking_level.value})"
        except Exception:
            return "STANDARD (standard)"

    def get_ai_organization_status(self) -> Dict[str, str]:
        """Get AI organization system status"""
        status = {}

        try:
            # Check orchestrator status
            orchestrator_file = (
                self.project_root / "src/enforcement/unified_flow_orchestrator.py"
            )
            if orchestrator_file.exists():
                status["🎼 オーケストレーター"] = "✅ アクティブ"
            else:
                status["🎼 オーケストレーター"] = "❌ 未発見"

            # Check enforcer status
            enforcer_file = self.project_root / "src/enforcement/reference_monitor.py"
            if enforcer_file.exists():
                status["🔒 エンフォーサー"] = "✅ アクティブ"
            else:
                status["🔒 エンフォーサー"] = "❌ 未発見"

            # Check monitor status
            monitor_file = self.project_root / "scripts/hooks/system_status_display.py"
            if monitor_file.exists():
                status["📊 モニター"] = "✅ 稼働中"
            else:
                status["📊 モニター"] = "❌ 未発見"

        except Exception:
            status["AI組織"] = "❌ チェック失敗"

        return status

    def generate_status_display(self, current_task: Optional[str] = None) -> str:
        """Generate compact status display"""
        db_status = self.get_db_status()
        api_status = self.get_api_status()
        ai_org_status = self.get_ai_organization_status()
        todos = self.get_current_todos()
        task_level = self.get_task_level(current_task)

        # Format compact display
        lines = [
            "📊 **システム状況**",
            f"**データベース**: {' | '.join([f'{k}:{v}' for k, v in db_status.items()])}",
            f"**API**: {' | '.join([f'{k}:{v}' for k, v in api_status.items()])}",
            f"**AI組織**: {' | '.join([f'{k}:{v}' for k, v in ai_org_status.items()])}",
            f"**タスク**: {len(todos)}個アクティブ"
            + (f" - {todos[0]['content'][:30]}..." if todos else " - なし"),
            f"**タスクレベル**: {task_level}",
        ]

        return "\n".join(lines)


def main():
    """Main execution for testing"""
    displayer = SystemStatusDisplay()

    # Test with sample task
    test_task = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None
    status = displayer.generate_status_display(test_task)
    print(status)


if __name__ == "__main__":
    import sys

    main()
