#!/usr/bin/env python3
"""
📋 Unified Task Manager - 統一タスク管理システム
============================================
分散したタスク管理を統一し、真の一元管理を実現
"""

import json
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class TaskStatus(Enum):
    """タスク状態"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """タスク優先度"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Task:
    """統一タスク構造"""

    id: str
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    created_at: str
    updated_at: str
    assigned_to: Optional[str] = None
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    dependencies: List[str] = None
    tags: List[str] = None
    session_id: Optional[str] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.tags is None:
            self.tags = []


class UnifiedTaskManager:
    """統一タスク管理システム"""

    def __init__(self):
        self.project_root = Path("/Users/dd/Desktop/1_dev/coding-rule2")
        self.task_storage = self.project_root / "runtime" / "task_management"
        self.tasks_file = self.task_storage / "tasks.json"
        self.active_session_file = self.task_storage / "active_session.json"

        # ディレクトリ作成
        self.task_storage.mkdir(parents=True, exist_ok=True)

        # タスク読み込み
        self.tasks: Dict[str, Task] = self._load_tasks()
        self.active_session = self._load_active_session()

        # 統合: 既存の分散タスクを統合
        self._integrate_existing_tasks()

    def _load_tasks(self) -> Dict[str, Task]:
        """タスク読み込み"""
        if not self.tasks_file.exists():
            return {}

        try:
            with open(self.tasks_file, encoding="utf-8") as f:
                data = json.load(f)
                return {
                    task_id: Task(**task_data) for task_id, task_data in data.items()
                }
        except Exception as e:
            print(f"⚠️ タスク読み込みエラー: {e}")
            return {}

    def _save_tasks(self):
        """タスク保存"""
        try:
            data = {task_id: asdict(task) for task_id, task in self.tasks.items()}
            with open(self.tasks_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ タスク保存エラー: {e}")

    def _load_active_session(self) -> Dict[str, Any]:
        """アクティブセッション読み込み"""
        if not self.active_session_file.exists():
            return {
                "current_task_id": None,
                "session_start": datetime.now(timezone.utc).isoformat(),
            }

        try:
            with open(self.active_session_file, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {
                "current_task_id": None,
                "session_start": datetime.now(timezone.utc).isoformat(),
            }

    def _save_active_session(self):
        """アクティブセッション保存"""
        try:
            with open(self.active_session_file, "w", encoding="utf-8") as f:
                json.dump(self.active_session, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ セッション保存エラー: {e}")

    def _integrate_existing_tasks(self):
        """既存の分散タスクを統合"""
        integrated_count = 0

        # 1. current-session.jsonからタスク統合
        session_file = (
            self.project_root / "src/memory/core/session-records/current-session.json"
        )
        if session_file.exists():
            try:
                with open(session_file, encoding="utf-8") as f:
                    session_data = json.load(f)
                    task_queue = session_data.get("ai_organization", {}).get(
                        "task_queue", []
                    )

                    for task_desc in task_queue:
                        if not any(
                            task_desc in task.description
                            for task in self.tasks.values()
                        ):
                            self.create_task(
                                title=f"Session Task: {task_desc[:50]}",
                                description=task_desc,
                                priority=TaskPriority.MEDIUM,
                                tags=["session", "legacy"],
                            )
                            integrated_count += 1
            except Exception as e:
                print(f"⚠️ セッションタスク統合エラー: {e}")

        if integrated_count > 0:
            print(f"✅ {integrated_count}個の既存タスクを統合しました")

    def create_task(
        self,
        title: str,
        description: str,
        priority: TaskPriority = TaskPriority.MEDIUM,
        assigned_to: Optional[str] = None,
        tags: List[str] = None,
    ) -> str:
        """タスク作成"""
        task_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()

        task = Task(
            id=task_id,
            title=title,
            description=description,
            status=TaskStatus.PENDING,
            priority=priority,
            created_at=timestamp,
            updated_at=timestamp,
            assigned_to=assigned_to,
            tags=tags or [],
        )

        self.tasks[task_id] = task
        self._save_tasks()

        print(f"✅ タスク作成: {title}")
        return task_id

    def update_task_status(
        self, task_id: str, status: TaskStatus, notes: Optional[str] = None
    ) -> bool:
        """タスク状態更新"""
        if task_id not in self.tasks:
            print(f"❌ タスクが見つかりません: {task_id}")
            return False

        task = self.tasks[task_id]
        task.status = status
        task.updated_at = datetime.now(timezone.utc).isoformat()

        if status == TaskStatus.IN_PROGRESS:
            self.active_session["current_task_id"] = task_id
            self._save_active_session()
        elif (
            status == TaskStatus.COMPLETED
            and self.active_session.get("current_task_id") == task_id
        ):
            self.active_session["current_task_id"] = None
            self._save_active_session()

        self._save_tasks()
        print(f"✅ タスク状態更新: {task.title} → {status.value}")
        return True

    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """状態別タスク取得"""
        return [task for task in self.tasks.values() if task.status == status]

    def get_tasks_by_priority(self, priority: TaskPriority) -> List[Task]:
        """優先度別タスク取得"""
        return [task for task in self.tasks.values() if task.priority == priority]

    def get_current_task(self) -> Optional[Task]:
        """現在のタスク取得"""
        current_id = self.active_session.get("current_task_id")
        if current_id and current_id in self.tasks:
            return self.tasks[current_id]
        return None

    def get_next_task(self) -> Optional[Task]:
        """次のタスク取得（優先度順）"""
        pending_tasks = self.get_tasks_by_status(TaskStatus.PENDING)
        if not pending_tasks:
            return None

        # 優先度順でソート
        priority_order = {
            TaskPriority.CRITICAL: 0,
            TaskPriority.HIGH: 1,
            TaskPriority.MEDIUM: 2,
            TaskPriority.LOW: 3,
        }

        pending_tasks.sort(key=lambda t: priority_order[t.priority])
        return pending_tasks[0]

    def start_next_task(self) -> Optional[Task]:
        """次のタスクを開始"""
        next_task = self.get_next_task()
        if next_task:
            self.update_task_status(next_task.id, TaskStatus.IN_PROGRESS)
            return next_task
        return None

    def get_task_summary(self) -> Dict[str, Any]:
        """タスクサマリー取得"""
        status_counts = {}
        priority_counts = {}

        for task in self.tasks.values():
            # 状態別カウント
            status = task.status.value
            status_counts[status] = status_counts.get(status, 0) + 1

            # 優先度別カウント
            priority = task.priority.value
            priority_counts[priority] = priority_counts.get(priority, 0) + 1

        current_task = self.get_current_task()
        next_task = self.get_next_task()

        return {
            "total_tasks": len(self.tasks),
            "status_breakdown": status_counts,
            "priority_breakdown": priority_counts,
            "current_task": {
                "id": current_task.id if current_task else None,
                "title": current_task.title if current_task else None,
            },
            "next_task": {
                "id": next_task.id if next_task else None,
                "title": next_task.title if next_task else None,
                "priority": next_task.priority.value if next_task else None,
            },
            "session_start": self.active_session.get("session_start"),
        }

    def list_tasks(
        self, status: Optional[TaskStatus] = None, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """タスク一覧取得"""
        tasks = list(self.tasks.values())

        if status:
            tasks = [t for t in tasks if t.status == status]

        # 更新日時でソート（新しい順）
        tasks.sort(key=lambda t: t.updated_at, reverse=True)

        return [
            {
                "id": task.id,
                "title": task.title,
                "status": task.status.value,
                "priority": task.priority.value,
                "created_at": task.created_at,
                "updated_at": task.updated_at,
                "assigned_to": task.assigned_to,
                "tags": task.tags,
            }
            for task in tasks[:limit]
        ]


def main():
    """テスト実行"""
    tm = UnifiedTaskManager()

    print("📋 Unified Task Manager Test")
    print("=" * 50)

    # サマリー表示
    summary = tm.get_task_summary()
    print("📊 タスクサマリー:")
    print(f"  総タスク数: {summary['total_tasks']}")
    print(f"  状態別: {summary['status_breakdown']}")
    print(f"  優先度別: {summary['priority_breakdown']}")

    if summary["current_task"]["title"]:
        print(f"  現在のタスク: {summary['current_task']['title']}")
    if summary["next_task"]["title"]:
        print(
            f"  次のタスク: {summary['next_task']['title']} ({summary['next_task']['priority']})"
        )

    # タスク一覧表示
    print("\n📋 最新タスク一覧:")
    tasks = tm.list_tasks(limit=5)
    for task in tasks:
        status_icon = {"pending": "⏳", "in_progress": "🔄", "completed": "✅"}.get(
            task["status"], "❓"
        )
        priority_icon = {
            "critical": "🔥",
            "high": "🔴",
            "medium": "🟡",
            "low": "🟢",
        }.get(task["priority"], "⚪")
        print(f"  {status_icon} {priority_icon} {task['title'][:60]}")


if __name__ == "__main__":
    main()
