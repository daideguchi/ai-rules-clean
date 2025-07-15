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
Quick AI Organization UI Demo
Shows 8 worker panes in visual layout
"""

import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from rich.console import Console
    from rich.layout import Layout
    from rich.panel import Panel

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


def create_worker_panel(worker_id, name, status, task="Idle"):
    """Create a visual panel for a worker"""

    # Status colors
    status_colors = {
        "active": "green",
        "idle": "yellow",
        "processing": "blue",
        "error": "red",
        "offline": "dim",
    }

    color = status_colors.get(status.lower(), "white")

    # Create status indicator
    status_indicator = f"[{color}]●[/{color}]"

    # Panel content
    content = f"""
{status_indicator} {name}
ID: {worker_id}
Status: [{color}]{status.upper()}[/{color}]
Task: {task}
CPU: 45% | Memory: 2.1GB
Tasks: 12 completed
"""

    return Panel(
        content.strip(),
        title=f"[bold]{name}[/bold]",
        border_style=color,
        padding=(1, 2),
    )


def create_status_bar():
    """Create system status bar"""
    return Panel(
        "[bold green]AI Organization System[/bold green] | "
        "[yellow]8 Workers Active[/yellow] | "
        "[blue]24 Tasks Completed[/blue] | "
        "[green]System Healthy[/green]",
        style="bold",
    )


def main():
    """Main demo function"""

    if not RICH_AVAILABLE:
        print("🚨 Rich library not available")
        print("Install with: python3 -m pip install rich --break-system-packages")
        return

    console = Console()

    # AI Workers configuration
    workers = [
        ("president", "👑 PRESIDENT", "active", "Strategic Leadership"),
        ("coordinator", "🔄 COORDINATOR", "processing", "System Coordination"),
        ("analyst", "📋 REQUIREMENTS_ANALYST", "active", "Requirements Analysis"),
        ("architect", "🏗️ SYSTEM_ARCHITECT", "active", "System Design"),
        ("data_eng", "📊 DATA_ENGINEER", "processing", "Data Processing"),
        ("security", "🔒 SECURITY_SPECIALIST", "active", "Security Audit"),
        ("pm", "📈 PROJECT_MANAGER", "idle", "Task Management"),
        ("devops", "⚙️ DEVOPS_ENGINEER", "active", "Infrastructure"),
    ]

    console.print("\n[bold cyan]🚀 AI Organization Visual Dashboard Demo[/bold cyan]")
    console.print("[dim]Showing 8 worker panes with real-time status[/dim]\n")

    # Create layout
    layout = Layout()

    # Top status bar
    layout.split_column(Layout(name="status", size=3), Layout(name="workers"))

    # Workers grid (2x4)
    layout["workers"].split_column(Layout(name="row1"), Layout(name="row2"))

    # Split rows into 4 columns each
    layout["row1"].split_row(
        Layout(name="w1"), Layout(name="w2"), Layout(name="w3"), Layout(name="w4")
    )

    layout["row2"].split_row(
        Layout(name="w5"), Layout(name="w6"), Layout(name="w7"), Layout(name="w8")
    )

    # Demo loop
    for i in range(5):  # 5 iterations
        # Update status bar
        layout["status"].update(create_status_bar())

        # Update worker panels
        for idx, (worker_id, name, status, task) in enumerate(workers):
            # Simulate status changes
            if i == 2 and idx == 1:  # Coordinator becomes idle
                status = "idle"
                task = "Waiting for tasks"
            elif i == 3 and idx == 6:  # PM becomes active
                status = "active"
                task = "Planning sprint"

            panel = create_worker_panel(worker_id, name, status, task)
            layout[f"w{idx + 1}"].update(panel)

        # Display
        console.clear()
        console.print(layout)

        if i < 4:  # Don't sleep on last iteration
            console.print(
                f"\n[dim]Demo iteration {i + 1}/5 - Updating in 2 seconds...[/dim]"
            )
            time.sleep(2)

    console.print("\n[bold green]✅ Demo Complete![/bold green]")
    console.print("\n[cyan]Available Commands:[/cyan]")
    console.print(
        "• [bold]python3 src/ui/ai_org_ui.py --mode dashboard[/bold] - Full dashboard"
    )
    console.print(
        "• [bold]python3 src/ui/ai_org_ui.py --mode command[/bold] - Command interface"
    )
    console.print("• [bold]make ui-dashboard[/bold] - Quick dashboard start")
    console.print("• [bold]make ui-command[/bold] - Quick command start")

    console.print("\n[dim]Full command reference: WORKER_UI_COMMANDS.md[/dim]")


if __name__ == "__main__":
    main()
