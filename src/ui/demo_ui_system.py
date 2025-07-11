# 🚨 偽装データ強制検出・停止システム
BANNED_FAKE_DATA = [
    "待機中",
    "処理中",
    "完了",
    "エラー",
    "テスト",
    "サンプル",
    "ダミー",
    "仮データ",
    "適当",
    "とりあえず",
    "temp",
    "dummy",
    "fake",
    "mock",
    "test",
    "sample",
    "placeholder",
    "Processing task",
    "Task completed",
    "Idle",
    "Active",
    "random",
    "lorem",
    "ipsum",
    "example",
    "demo",
]


def _enforce_no_fake_data(data):
    if isinstance(data, str):
        for banned in BANNED_FAKE_DATA:
            if banned in data:
                raise SystemExit(f"🚨 偽装データ検出で強制停止: {banned} in {data}")
    elif isinstance(data, (list, dict)):
        data_str = str(data)
        for banned in BANNED_FAKE_DATA:
            if banned in data_str:
                raise SystemExit(f"🚨 偽装データ検出で強制停止: {banned}")
    return data


# 全ての関数実行時に検証
original_print = print


def print(*args, **kwargs):
    for arg in args:
        _enforce_no_fake_data(arg)
    return original_print(*args, **kwargs)


#!/usr/bin/env python3
"""
🎯 AI Organization UI System Demo
=================================

This demo shows the complete UI system functionality without Rich dependency.
Demonstrates all features including worker management, task assignment, and metrics.
"""

import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))


def demo_ui_system():
    """Demo the complete UI system"""
    print("🎯 AI Organization UI System Demo")
    print("=" * 50)

    # Demo 1: Worker Status Display
    print("\n1. 👥 AI Worker Status Display")
    print("-" * 30)

    # Simulate 8 AI workers with different statuses
    workers = {
        "PRESIDENT": {
            "icon": "👑",
            "name": "プレジデント",
            "status": "active",
            "current_task": "Strategic planning review",
            "tasks_completed": 45,
            "error_count": 0,
            "performance": 95,
            "authority": 10,
            "specialization": "strategic_leadership",
        },
        "COORDINATOR": {
            "icon": "🔄",
            "name": "コーディネーター",
            "status": "idle",
            "current_task": None,
            "tasks_completed": 32,
            "error_count": 1,
            "performance": 88,
            "authority": 8,
            "specialization": "coordination",
        },
        "BACKEND_DEV": {
            "icon": "🔧",
            "name": "バックエンド開発者",
            "status": "processing",
            "current_task": "Database optimization",
            "tasks_completed": 78,
            "error_count": 3,
            "performance": 92,
            "authority": 7,
            "specialization": "backend_development",
        },
        "FRONTEND_DEV": {
            "icon": "💻",
            "name": "フロントエンド開発者",
            "status": "active",
            "current_task": "UI component development",
            "tasks_completed": 65,
            "error_count": 2,
            "performance": 87,
            "authority": 7,
            "specialization": "frontend_development",
        },
        "DEVOPS": {
            "icon": "⚙️",
            "name": "DevOpsエンジニア",
            "status": "error",
            "current_task": "Deployment troubleshooting",
            "tasks_completed": 41,
            "error_count": 5,
            "performance": 75,
            "authority": 8,
            "specialization": "infrastructure",
        },
        "SECURITY": {
            "icon": "🔒",
            "name": "セキュリティ専門家",
            "status": "idle",
            "current_task": None,
            "tasks_completed": 28,
            "error_count": 0,
            "performance": 98,
            "authority": 9,
            "specialization": "security",
        },
        "QA": {
            "icon": "✅",
            "name": "品質保証",
            "status": "processing",
            "current_task": "Test suite execution",
            "tasks_completed": 89,
            "error_count": 4,
            "performance": 85,
            "authority": 6,
            "specialization": "quality_assurance",
        },
        "AI_SPECIALIST": {
            "icon": "🤖",
            "name": "AI専門家",
            "status": "active",
            "current_task": "Model training optimization",
            "tasks_completed": 52,
            "error_count": 1,
            "performance": 94,
            "authority": 9,
            "specialization": "artificial_intelligence",
        },
    }

    # Display worker grid (2x4 layout)
    print("┌─────────────────────────────────────────────────────────────────────┐")
    print("│                    AI Organization Dashboard                         │")
    print("├─────────────────────────────────────────────────────────────────────┤")
    print("│  Worker Grid (2x4)                    │    System Metrics          │")
    print("│                                       │                            │")

    # Top row (first 4 workers)
    worker_list = list(workers.keys())
    for i in range(0, 4):
        if i < len(worker_list):
            worker_id = worker_list[i]
            worker = workers[worker_id]

            # Status indicator
            status_icons = {
                "active": "🟢",
                "idle": "🟡",
                "processing": "🔵",
                "error": "🔴",
                "offline": "⚫",
            }
            status_icon = status_icons.get(worker["status"], "❓")

            # Performance bar
            perf_bar = "█" * (worker["performance"] // 10)
            perf_bar += "░" * (10 - (worker["performance"] // 10))

            # Current task (truncated)
            current_task = (
                worker["current_task"][:20] + "..."
                if worker["current_task"] and len(worker["current_task"]) > 20
                else worker["current_task"] or "待機中"
            )

            print(
                f"│  {status_icon} {worker['icon']} {worker['name']:<12}      │", end=""
            )
            if i == 0:
                print("  Uptime: 02:15:23        │")
            elif i == 1:
                print("  Active: 4/8             │")
            elif i == 2:
                print("  Tasks: 430              │")
            elif i == 3:
                print("  Errors: 16              │")
            else:
                print("                            │")

            print(f"│  Task: {current_task:<20}         │", end="")
            if i == 0:
                print("  Success: 96.3%          │")
            elif i == 1:
                print("  Memory: 45.2%           │")
            elif i == 2:
                print("  CPU: 23.1%              │")
            elif i == 3:
                print("  Queue: 12 tasks         │")
            else:
                print("                            │")

            print(f"│  Perf: {perf_bar}      │", end="")
            if i == 0:
                print("                            │")
            elif i == 1:
                print("  Commands:               │")
            elif i == 2:
                print("  • w - Workers           │")
            elif i == 3:
                print("  • m - Metrics           │")
            else:
                print("                            │")

    print("│                                       │  • t - Tasks            │")
    print("│  Bottom row (next 4 workers)         │  • l - Logs             │")
    print("│                                       │  • r - Reset            │")

    # Bottom row (next 4 workers)
    for i in range(4, 8):
        if i < len(worker_list):
            worker_id = worker_list[i]
            worker = workers[worker_id]

            status_icon = status_icons.get(worker["status"], "❓")
            current_task = (
                worker["current_task"][:20] + "..."
                if worker["current_task"] and len(worker["current_task"]) > 20
                else worker["current_task"] or "待機中"
            )

            print(
                f"│  {status_icon} {worker['icon']} {worker['name']:<12}      │", end=""
            )
            if i == 4:
                print("  • q - Quit              │")
            else:
                print("                            │")

            print(f"│  Task: {current_task:<20}         │", end="")
            if i == 4:
                print("                            │")
            else:
                print("  Activity Log:           │")

            perf_bar = "█" * (worker["performance"] // 10)
            perf_bar += "░" * (10 - (worker["performance"] // 10))
            print(f"│  Perf: {perf_bar}      │", end="")
            if i == 4:
                print("                            │")
            elif i == 5:
                print("  12:53 Task assigned     │")
            elif i == 6:
                print("  12:52 Worker reset      │")
            elif i == 7:
                print("  12:51 System started    │")
            else:
                print("                            │")

    print("└─────────────────────────────────────────────────────────────────────┘")

    # Demo 2: Command Interface
    print("\n2. 🎮 Interactive Command Interface")
    print("-" * 30)

    sample_commands = [
        ("workers", "Show all worker status"),
        ("select PRESIDENT", "Select PRESIDENT for detailed operations"),
        (
            "assign BACKEND_DEV 'Database optimization'",
            "Assign task to backend developer",
        ),
        ("worker PRESIDENT", "Show detailed PRESIDENT information"),
        ("tasks", "Show task queues for all workers"),
        ("metrics", "Display system performance metrics"),
        ("reset DEVOPS", "Reset DEVOPS worker state"),
        ("help", "Show all available commands"),
    ]

    print("Available Commands:")
    for cmd, desc in sample_commands:
        print(f"  ai-org$ {cmd:<35} # {desc}")

    print("\nCommand Shortcuts:")
    shortcuts = {
        "w": "workers",
        "m": "metrics",
        "t": "tasks",
        "h": "help",
        "q": "quit",
        "s": "status",
        "r": "refresh",
    }

    for shortcut, full_cmd in shortcuts.items():
        print(f"  {shortcut} → {full_cmd}")

    # Demo 3: Worker Management
    print("\n3. 👥 Worker Management Interface")
    print("-" * 30)

    # Show detailed worker information
    worker_id = "PRESIDENT"
    worker = workers[worker_id]

    print(f"Worker Details: {worker['icon']} {worker['name']}")
    print("┌─────────────────────────────────────────────────────┐")
    print("│ Property              │ Value                       │")
    print("├─────────────────────────────────────────────────────┤")
    print(f"│ Status                │ {worker['status'].upper():<27} │")
    print(f"│ Current Task          │ {(worker['current_task'] or 'None'):<27} │")
    print(f"│ Tasks Completed       │ {worker['tasks_completed']:<27} │")
    print(f"│ Error Count           │ {worker['error_count']:<27} │")
    print(f"│ Performance Score     │ {worker['performance']}%{'':<24} │")
    print(f"│ Authority Level       │ {worker['authority']:<27} │")
    print(f"│ Specialization        │ {worker['specialization']:<27} │")
    print("└─────────────────────────────────────────────────────┘")

    # Task Queue Example
    print("\n📋 Task Queue Example:")
    task_queue = [
        "Strategic planning review",
        "Budget allocation approval",
        "Team performance evaluation",
        "System architecture assessment",
    ]

    if task_queue:
        print(f"Queue ({len(task_queue)} tasks):")
        for i, task in enumerate(task_queue, 1):
            print(f"  {i}. {task}")
    else:
        print("No tasks in queue")

    # Demo 4: System Metrics
    print("\n4. 📈 System Metrics Display")
    print("-" * 30)

    # Calculate system metrics
    active_workers = sum(1 for w in workers.values() if w["status"] == "active")
    processing_workers = sum(1 for w in workers.values() if w["status"] == "processing")
    error_workers = sum(1 for w in workers.values() if w["status"] == "error")
    total_tasks = sum(w["tasks_completed"] for w in workers.values())
    total_errors = sum(w["error_count"] for w in workers.values())
    avg_performance = sum(w["performance"] for w in workers.values()) / len(workers)
    error_rate = (total_errors / total_tasks * 100) if total_tasks > 0 else 0

    print("System Metrics:")
    print("┌─────────────────────────────────────────────────────┐")
    print("│ Metric                │ Value                       │")
    print("├─────────────────────────────────────────────────────┤")
    print("│ System Uptime         │ 02:15:23                    │")
    print(f"│ Active Workers        │ {active_workers}/8{'':<23} │")
    print(f"│ Processing Workers    │ {processing_workers:<27} │")
    print(f"│ Error Workers         │ {error_workers:<27} │")
    print(f"│ Total Tasks           │ {total_tasks:<27} │")
    print(f"│ Total Errors          │ {total_errors:<27} │")
    print(f"│ Success Rate          │ {100 - error_rate:.1f}%{'':<23} │")
    print(f"│ Avg Performance       │ {avg_performance:.1f}%{'':<23} │")
    print(f"│ Memory Usage          │ 45.2%{'':<23} │")
    print(f"│ CPU Usage             │ 23.1%{'':<23} │")
    print("└─────────────────────────────────────────────────────┘")

    # Demo 5: Task Assignment
    print("\n5. 📋 Task Assignment Demo")
    print("-" * 30)

    print("Task Assignment Examples:")

    assignments = [
        ("PRESIDENT", "Strategic planning review", "High priority strategic task"),
        ("BACKEND_DEV", "Database optimization", "Performance improvement task"),
        ("FRONTEND_DEV", "UI component development", "User interface enhancement"),
        ("AI_SPECIALIST", "Model training optimization", "Machine learning task"),
        ("SECURITY", "Security audit", "Security assessment task"),
        ("QA", "Test suite execution", "Quality assurance task"),
        ("DEVOPS", "Deployment automation", "Infrastructure task"),
        ("COORDINATOR", "Team coordination", "Management task"),
    ]

    for worker_id, task, description in assignments:
        worker = workers[worker_id]
        print(f"  {worker['icon']} {worker['name']}")
        print(f"    Task: {task}")
        print(f"    Description: {description}")
        print(f"    Authority Level: {worker['authority']}")
        print()

    # Demo 6: Real-time Updates
    print("\n6. 🔄 Real-time Updates Demo")
    print("-" * 30)

    print("Simulating real-time updates...")

    # Simulate status changes
    updates = [
        ("COORDINATOR", "idle → active", "Started new coordination task"),
        ("DEVOPS", "error → processing", "Recovered from error, resuming work"),
        ("SECURITY", "idle → processing", "Began security audit"),
        ("QA", "processing → idle", "Completed test suite execution"),
        ("AI_SPECIALIST", "active → processing", "Entered deep learning phase"),
    ]

    for worker_id, status_change, description in updates:
        worker = workers[worker_id]
        print(f"  {worker['icon']} {worker['name']}: {status_change}")
        print(f"    {description}")
        time.sleep(0.5)  # Simulate real-time delay

    # Demo 7: Integration Features
    print("\n7. 🔗 Integration Features")
    print("-" * 30)

    print("System Integration Status:")
    integrations = [
        ("AI Organization System", "✅", "Dynamic role management active"),
        ("Memory Manager", "✅", "Unified memory system integrated"),
        ("Conductor System", "✅", "Task execution system operational"),
        ("Constitutional AI", "✅", "AI safety governance active"),
        ("NIST AI RMF", "✅", "Risk management framework compliant"),
        ("Monitoring System", "✅", "Real-time monitoring operational"),
        ("PostgreSQL Database", "✅", "Data persistence available"),
        ("Rich CLI Interface", "⚠️", "Install with: pip install rich"),
    ]

    for system, status, description in integrations:
        print(f"  {status} {system}")
        print(f"    {description}")

    # Demo 8: Usage Examples
    print("\n8. 🚀 Usage Examples")
    print("-" * 30)

    print("Launch Commands:")
    launch_commands = [
        ("make ui-dashboard", "Launch full dashboard interface"),
        ("make ui-command", "Launch interactive command interface"),
        ("make ui-worker", "Launch worker management"),
        ("make ui-metrics", "Show system metrics"),
        ("./scripts/ui/launch-dashboard.sh", "Use launcher script"),
        ("python src/ui/ai_org_ui.py", "Run main UI menu"),
        ("python src/ui/visual_dashboard.py dashboard", "Direct dashboard launch"),
        ("python src/ui/command_interface.py", "Direct command interface"),
    ]

    for cmd, desc in launch_commands:
        print(f"  {cmd}")
        print(f"    {desc}")
        print()

    print("Installation:")
    print("  pip install rich>=13.0.0")
    print("  pip install -r requirements-ui.txt")
    print("  make ui-install")

    print("\n✅ UI System Demo Complete!")
    print("\n🎯 Key Features Demonstrated:")
    print("  • 8 AI workers with real-time status monitoring")
    print("  • Color-coded status indicators (Active/Idle/Processing/Error)")
    print("  • Interactive command interface with shortcuts")
    print("  • Task assignment and queue management")
    print("  • System metrics and performance tracking")
    print("  • Professional CLI dashboard layout")
    print("  • Worker management and control")
    print("  • Real-time updates and notifications")
    print("  • Integration with existing AI systems")
    print("  • Comprehensive documentation and help")

    print("\n📚 Documentation:")
    print("  See docs/ui-system-guide.md for complete usage guide")
    print("  Run 'make help' to see all available commands")

    return True


if __name__ == "__main__":
    demo_ui_system()
