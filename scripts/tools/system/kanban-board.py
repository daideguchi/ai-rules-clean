#!/usr/bin/env python3
"""
WIP-Limited Kanban Board System
Implements visual task management with strict WIP limits
Based on INTEGRITY_RECOVERY_PLAN.md requirements
"""

import json
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class KanbanBoard:
    """WIP-limited Kanban board for task management"""

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.board_file = self.repo_path / "runtime" / "kanban-board.json"
        self.wip_limits = {
            "todo": 10,
            "in_progress": 2,  # Critical WIP limit
            "review": 3,
            "done": 100,  # No limit on done
        }
        self.ensure_board_exists()

    def ensure_board_exists(self):
        """Initialize board if it doesn't exist"""
        runtime_dir = self.repo_path / "runtime"
        runtime_dir.mkdir(exist_ok=True)

        if not self.board_file.exists():
            initial_board = {
                "metadata": {
                    "created": datetime.now().isoformat(),
                    "version": "1.0.0",
                    "wip_limits": self.wip_limits,
                },
                "columns": {"todo": [], "in_progress": [], "review": [], "done": []},
                "history": [],
            }

            with open(self.board_file, "w") as f:
                json.dump(initial_board, f, indent=2, ensure_ascii=False)

    def load_board(self) -> Dict:
        """Load board from file"""
        with open(self.board_file) as f:
            return json.load(f)

    def save_board(self, board: Dict):
        """Save board to file"""
        with open(self.board_file, "w") as f:
            json.dump(board, f, indent=2, ensure_ascii=False)

    def add_task(
        self,
        title: str,
        description: str,
        priority: str = "medium",
        estimated_minutes: int = 60,
    ) -> str:
        """Add new task to TODO column"""

        board = self.load_board()

        # Check WIP limit for TODO
        if len(board["columns"]["todo"]) >= self.wip_limits["todo"]:
            print(f"❌ TODO列のWIP制限超過 ({self.wip_limits['todo']})")
            return None

        task_id = str(uuid.uuid4())[:8]
        task = {
            "id": task_id,
            "title": title,
            "description": description,
            "priority": priority,
            "estimated_minutes": estimated_minutes,
            "created_at": datetime.now().isoformat(),
            "status": "todo",
            "time_tracking": {
                "started_at": None,
                "completed_at": None,
                "time_spent": 0,
            },
            "commitment_id": None,  # Link to GitHub issue if needed
        }

        board["columns"]["todo"].append(task)

        # Add to history
        board["history"].append(
            {
                "timestamp": datetime.now().isoformat(),
                "action": "task_created",
                "task_id": task_id,
                "details": {"title": title, "priority": priority},
            }
        )

        self.save_board(board)
        print(f"✅ タスク追加: {task_id} - {title}")
        return task_id

    def move_task(self, task_id: str, target_column: str) -> bool:
        """Move task between columns with WIP limit enforcement"""

        board = self.load_board()

        # Find task in current column
        current_column = None
        task = None

        for col_name, tasks in board["columns"].items():
            for t in tasks:
                if t["id"] == task_id:
                    current_column = col_name
                    task = t
                    break
            if task:
                break

        if not task:
            print(f"❌ タスクが見つかりません: {task_id}")
            return False

        # Check WIP limit for target column
        if target_column in self.wip_limits:
            current_count = len(board["columns"][target_column])
            if current_count >= self.wip_limits[target_column]:
                print(
                    f"❌ {target_column}列のWIP制限超過 ({self.wip_limits[target_column]})"
                )
                print(f"   現在のタスク数: {current_count}")
                self._show_wip_violation_help(target_column)
                return False

        # Special handling for moving to in_progress
        if target_column == "in_progress":
            task["time_tracking"]["started_at"] = datetime.now().isoformat()
            print(f"⏰ タスク開始: {task['title']}")

        # Special handling for moving to done
        if target_column == "done":
            task["time_tracking"]["completed_at"] = datetime.now().isoformat()

            # Calculate time spent
            if task["time_tracking"]["started_at"]:
                start_time = datetime.fromisoformat(task["time_tracking"]["started_at"])
                end_time = datetime.now()
                time_spent = (end_time - start_time).total_seconds() / 60
                task["time_tracking"]["time_spent"] = time_spent

                print(f"✅ タスク完了: {task['title']}")
                print(f"   所要時間: {time_spent:.1f}分")

        # Remove from current column
        board["columns"][current_column].remove(task)

        # Add to target column
        task["status"] = target_column
        board["columns"][target_column].append(task)

        # Add to history
        board["history"].append(
            {
                "timestamp": datetime.now().isoformat(),
                "action": "task_moved",
                "task_id": task_id,
                "details": {
                    "from": current_column,
                    "to": target_column,
                    "title": task["title"],
                },
            }
        )

        self.save_board(board)
        print(f"📋 タスク移動: {task['title']} ({current_column} → {target_column})")
        return True

    def _show_wip_violation_help(self, column: str):
        """Show help when WIP limit is violated"""
        print(f"\n🚨 WIP制限違反: {column}列")
        print("対処方法:")
        print("1. 既存タスクを完了させる")
        print("2. 既存タスクを他の列に移動する")
        print("3. 既存タスクを削除する")
        print("4. タスクを分割して小さくする")
        print("\n現在の{column}タスク:")

        board = self.load_board()
        for i, task in enumerate(board["columns"][column], 1):
            print(f"  {i}. {task['id']}: {task['title']}")

    def show_board(self):
        """Display current board state"""
        board = self.load_board()

        print("📋 Kanban Board")
        print("=" * 80)

        for col_name, tasks in board["columns"].items():
            limit = self.wip_limits.get(col_name, "∞")
            current_count = len(tasks)

            # Color coding for WIP violations
            if isinstance(limit, int) and current_count >= limit:
                status = "🚨"
            elif isinstance(limit, int) and current_count >= limit * 0.8:
                status = "⚠️"
            else:
                status = "✅"

            print(f"\n{status} {col_name.upper()} ({current_count}/{limit})")
            print("-" * 40)

            if not tasks:
                print("  (空)")
            else:
                for task in tasks:
                    priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(
                        task["priority"], "⚪"
                    )

                    print(f"  {priority_icon} {task['id']}: {task['title']}")
                    if task["status"] == "in_progress":
                        started = datetime.fromisoformat(
                            task["time_tracking"]["started_at"]
                        )
                        elapsed = (datetime.now() - started).total_seconds() / 60
                        print(f"      ⏱️  開始から{elapsed:.0f}分経過")

        print("\n" + "=" * 80)

    def get_active_tasks(self) -> List[Dict]:
        """Get all active tasks (not done)"""
        board = self.load_board()
        active_tasks = []

        for col_name, tasks in board["columns"].items():
            if col_name != "done":
                for task in tasks:
                    task["current_column"] = col_name
                    active_tasks.append(task)

        return active_tasks

    def check_overdue_tasks(self) -> List[Dict]:
        """Check for tasks that have been in progress too long"""
        board = self.load_board()
        overdue_tasks = []

        for task in board["columns"]["in_progress"]:
            if task["time_tracking"]["started_at"]:
                started = datetime.fromisoformat(task["time_tracking"]["started_at"])
                elapsed_hours = (datetime.now() - started).total_seconds() / 3600

                # Mark as overdue if in progress for more than 4 hours
                if elapsed_hours > 4:
                    task["overdue_hours"] = elapsed_hours
                    overdue_tasks.append(task)

        return overdue_tasks

    def generate_daily_report(self) -> Dict:
        """Generate daily productivity report"""
        board = self.load_board()

        # Tasks completed today
        today = datetime.now().date()
        completed_today = []

        for task in board["columns"]["done"]:
            if task["time_tracking"]["completed_at"]:
                completed_date = datetime.fromisoformat(
                    task["time_tracking"]["completed_at"]
                ).date()

                if completed_date == today:
                    completed_today.append(task)

        # Calculate statistics
        total_time_spent = sum(
            task["time_tracking"]["time_spent"] for task in completed_today
        )

        avg_time_per_task = (
            total_time_spent / len(completed_today) if completed_today else 0
        )

        report = {
            "date": today.isoformat(),
            "completed_tasks": len(completed_today),
            "total_time_minutes": total_time_spent,
            "average_time_per_task": avg_time_per_task,
            "active_tasks": len(self.get_active_tasks()),
            "overdue_tasks": len(self.check_overdue_tasks()),
            "completed_task_details": completed_today,
        }

        return report

    def emergency_reset(self):
        """Emergency reset for WIP violations"""
        board = self.load_board()

        # Move all in_progress tasks back to todo
        in_progress_tasks = board["columns"]["in_progress"]
        for task in in_progress_tasks:
            task["status"] = "todo"
            task["time_tracking"]["started_at"] = None
            board["columns"]["todo"].append(task)

        board["columns"]["in_progress"] = []

        # Add to history
        board["history"].append(
            {
                "timestamp": datetime.now().isoformat(),
                "action": "emergency_reset",
                "details": {"moved_tasks": len(in_progress_tasks)},
            }
        )

        self.save_board(board)
        print(f"🚨 緊急リセット完了: {len(in_progress_tasks)}タスクをTODOに戻しました")


def main():
    """CLI interface for Kanban board"""

    if len(sys.argv) < 2:
        print("Usage: python kanban-board.py <command> [args...]")
        print("Commands: add, move, show, report, check-overdue, reset")
        return

    board = KanbanBoard()
    command = sys.argv[1]

    if command == "add":
        if len(sys.argv) < 4:
            print("Usage: add <title> <description> [priority] [estimated_minutes]")
            return

        title = sys.argv[2]
        description = sys.argv[3]
        priority = sys.argv[4] if len(sys.argv) > 4 else "medium"
        estimated_minutes = int(sys.argv[5]) if len(sys.argv) > 5 else 60

        board.add_task(title, description, priority, estimated_minutes)

    elif command == "move":
        if len(sys.argv) < 4:
            print("Usage: move <task_id> <target_column>")
            print("Columns: todo, in_progress, review, done")
            return

        task_id = sys.argv[2]
        target_column = sys.argv[3]

        board.move_task(task_id, target_column)

    elif command == "show":
        board.show_board()

    elif command == "report":
        report = board.generate_daily_report()
        print(f"📊 Daily Report ({report['date']})")
        print(f"   完了タスク: {report['completed_tasks']}")
        print(f"   総作業時間: {report['total_time_minutes']:.1f}分")
        print(f"   平均時間/タスク: {report['average_time_per_task']:.1f}分")
        print(f"   アクティブタスク: {report['active_tasks']}")
        print(f"   遅延タスク: {report['overdue_tasks']}")

    elif command == "check-overdue":
        overdue = board.check_overdue_tasks()
        if overdue:
            print(f"🚨 {len(overdue)}個の遅延タスクがあります:")
            for task in overdue:
                print(
                    f"  {task['id']}: {task['title']} ({task['overdue_hours']:.1f}時間経過)"
                )
        else:
            print("✅ 遅延タスクはありません")

    elif command == "reset":
        board.emergency_reset()

    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
