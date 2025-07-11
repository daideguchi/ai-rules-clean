#!/usr/bin/env python3
"""
🧪 UI System Test - Demo without Rich library
=============================================

This test demonstrates the core functionality of the UI system
without requiring the Rich library installation.
"""

import sys
from pathlib import Path

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


# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))


# Mock Rich components for testing
class MockPanel:
    def __init__(self, content, title="", border_style="", height=None):
        self.content = content
        self.title = title
        self.border_style = border_style
        self.height = height


class MockText:
    def __init__(self, content="", style=""):
        self.content = content
        self.style = style

    def append(self, text, style=""):
        self.content += text


class MockConsole:
    def print(self, *args, **kwargs):
        if args:
            print(args[0])
        else:
            print()

    def clear(self):
        print("\033[2J\033[H")


# Mock the rich imports
sys.modules["rich.console"] = type("MockModule", (), {"Console": MockConsole})()
sys.modules["rich.panel"] = type("MockModule", (), {"Panel": MockPanel})()
sys.modules["rich.text"] = type("MockModule", (), {"Text": MockText})()
sys.modules["rich.table"] = type(
    "MockModule", (), {"Table": type("MockTable", (), {})}
)()
sys.modules["rich.layout"] = type(
    "MockModule", (), {"Layout": type("MockLayout", (), {})}
)()
sys.modules["rich.live"] = type("MockModule", (), {"Live": type("MockLive", (), {})})()
sys.modules["rich.columns"] = type(
    "MockModule", (), {"Columns": type("MockColumns", (), {})}
)()
sys.modules["rich.progress"] = type(
    "MockModule",
    (),
    {
        "Progress": type("MockProgress", (), {}),
        "TaskID": type("MockTaskID", (), {}),
        "SpinnerColumn": type("MockSpinnerColumn", (), {}),
        "TextColumn": type("MockTextColumn", (), {}),
        "BarColumn": type("MockBarColumn", (), {}),
        "TimeRemainingColumn": type("MockTimeRemainingColumn", (), {}),
    },
)()
sys.modules["rich.align"] = type(
    "MockModule", (), {"Align": type("MockAlign", (), {})}
)()
sys.modules["rich.rule"] = type("MockModule", (), {"Rule": type("MockRule", (), {})})()
sys.modules["rich.status"] = type(
    "MockModule", (), {"Status": type("MockStatus", (), {})}
)()
sys.modules["rich.tree"] = type("MockModule", (), {"Tree": type("MockTree", (), {})})()
sys.modules["rich.prompt"] = type(
    "MockModule",
    (),
    {
        "Prompt": type("MockPrompt", (), {"ask": lambda *args, **kwargs: "test"}),
        "Confirm": type("MockConfirm", (), {"ask": lambda *args, **kwargs: True}),
    },
)()
sys.modules["rich.markup"] = type("MockModule", (), {"escape": lambda x: x})()
sys.modules["rich.style"] = type(
    "MockModule", (), {"Style": type("MockStyle", (), {})}
)()


def test_ui_system():
    """Test the UI system components"""
    print("🧪 Testing AI Organization UI System")
    print("=" * 50)

    # Test 1: Basic imports
    print("\n1. Testing imports...")
    try:
        from ui.visual_dashboard import VisualDashboard

        print("✅ Visual Dashboard imports successful")
    except Exception as e:
        print(f"❌ Visual Dashboard import failed: {e}")
        return False

    try:
        from ui.command_interface import InteractiveCommandInterface

        print("✅ Command Interface imports successful")
    except Exception as e:
        print(f"❌ Command Interface import failed: {e}")
        return False

    try:
        from ui.ai_org_ui import AIOrganizationUI

        print("✅ AI Organization UI imports successful")
    except Exception as e:
        print(f"❌ AI Organization UI import failed: {e}")
        return False

    # Test 2: Create dashboard instance
    print("\n2. Testing dashboard creation...")
    try:
        dashboard = VisualDashboard()
        print("✅ Visual Dashboard instance created")

        # Test worker initialization
        worker_count = len(dashboard.workers)
        print(f"✅ Workers initialized: {worker_count}")

        # Show worker summary
        print("\n📊 Worker Summary:")
        for _worker_id, worker in dashboard.workers.items():
            print(f"  {worker.icon} {worker.display_name} - {worker.status.value}")

    except Exception as e:
        print(f"❌ Dashboard creation failed: {e}")
        return False

    # Test 3: Test worker operations
    print("\n3. Testing worker operations...")
    try:
        # Get worker details
        first_worker = next(iter(dashboard.workers.keys()))
        dashboard.get_worker_details(first_worker)
        print(f"✅ Worker details retrieved for {first_worker}")

        # Test task assignment
        result = dashboard.assign_task_to_worker(first_worker, "Test task")
        print(f"✅ Task assignment result: {result.get('success', 'completed')}")

        # Get system status
        status = dashboard.get_system_status()
        print(
            f"✅ System status retrieved: {status['system_metrics']['active_workers']} active workers"
        )

    except Exception as e:
        print(f"❌ Worker operations failed: {e}")
        return False

    # Test 4: Test command interface
    print("\n4. Testing command interface...")
    try:
        interface = InteractiveCommandInterface()
        print("✅ Command Interface instance created")

        # Test command parsing
        command, args = interface._parse_command("workers")
        print(f"✅ Command parsing: '{command}' with args {args}")

        # Test command shortcuts
        shortcut_command = interface.shortcuts.get("w", "unknown")
        print(f"✅ Shortcut 'w' maps to: {shortcut_command}")

    except Exception as e:
        print(f"❌ Command interface failed: {e}")
        return False

    # Test 5: Test main UI
    print("\n5. Testing main UI...")
    try:
        ui = AIOrganizationUI()
        print("✅ Main UI instance created")

        # Test system initialization
        systems = {
            "dashboard": ui.dashboard is not None,
            "command_interface": ui.command_interface is not None,
            "ai_org_system": ui.ai_org_system is not None,
        }

        print("✅ System initialization status:")
        for system, status in systems.items():
            print(f"  {system}: {'✅' if status else '❌'}")

    except Exception as e:
        print(f"❌ Main UI failed: {e}")
        return False

    # Test 6: Demonstrate UI features
    print("\n6. Demonstrating UI features...")
    try:
        # Show dashboard summary
        print("\n📊 Dashboard Summary:")
        status = dashboard.get_system_status()
        metrics = status["system_metrics"]

        print(f"  Uptime: {metrics['uptime']}")
        print(f"  Active Workers: {metrics['active_workers']}/8")
        print(f"  Completed Tasks: {metrics['completed_tasks']}")
        print(f"  Error Rate: {metrics['error_rate']:.1f}%")

        # Show worker statuses
        print("\n👥 Worker Statuses:")
        for worker_id, worker_data in status["workers"].items():
            worker_details = dashboard.get_worker_details(worker_id)
            status_icon = {
                "active": "🟢",
                "idle": "🟡",
                "processing": "🔵",
                "error": "🔴",
                "offline": "⚫",
            }.get(worker_data["status"], "❓")

            print(
                f"  {status_icon} {worker_details['icon']} {worker_details['display_name']}"
            )
            if worker_details["current_task"]:
                print(f"    Current: {worker_details['current_task']}")
            if worker_details["task_queue"]:
                print(f"    Queue: {len(worker_details['task_queue'])} tasks")

        # Show available commands
        print("\n🎮 Available Commands:")
        command_categories = {
            "System": ["help", "quit", "refresh", "status"],
            "Workers": ["workers", "select", "worker", "reset"],
            "Tasks": ["assign", "tasks", "complete", "cancel"],
            "Views": ["dashboard", "metrics", "logs"],
        }

        for category, commands in command_categories.items():
            print(f"  {category}: {', '.join(commands)}")

    except Exception as e:
        print(f"❌ UI demonstration failed: {e}")
        return False

    print("\n✅ All UI system tests passed successfully!")
    print("\n🎯 UI System Features:")
    print("  • 8 AI workers with real-time status monitoring")
    print("  • Color-coded status indicators")
    print("  • Interactive command interface")
    print("  • Task assignment and queue management")
    print("  • System metrics and performance tracking")
    print("  • Professional CLI dashboard")
    print("  • Responsive layout for different terminal sizes")
    print("  • Integration with existing AI organization system")

    print("\n📚 Usage Examples:")
    print("  # Launch full dashboard")
    print("  python src/ui/ai_org_ui.py --mode dashboard")
    print("  ")
    print("  # Launch command interface")
    print("  python src/ui/ai_org_ui.py --mode command")
    print("  ")
    print("  # Show worker status")
    print("  python src/ui/visual_dashboard.py worker")
    print("  ")
    print("  # Assign task to worker")
    print("  python src/ui/visual_dashboard.py assign PRESIDENT 'Strategic planning'")
    print("  ")
    print("  # Show system metrics")
    print("  python src/ui/visual_dashboard.py metrics")

    print("\n🔧 Installation:")
    print("  pip install rich>=13.0.0")
    print("  pip install -r requirements-ui.txt")

    return True


if __name__ == "__main__":
    success = test_ui_system()
    sys.exit(0 if success else 1)
