#!/usr/bin/env python3
"""
🎯 AI Organization UI - Main Launcher and Integration System
============================================================

Complete UI system launcher that integrates:
- Visual Dashboard with real-time monitoring
- Interactive Command Interface
- Worker management and task assignment
- System metrics and performance tracking
- Integration with existing AI organization system
"""

import argparse
import asyncio
import signal
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


# Rich imports for CLI styling
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Confirm, Prompt
    from rich.table import Table
    from rich.text import Text

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from ai.ai_organization_system import DynamicAIOrganizationSystem
    from conductor.core import ConductorCore
    from memory.unified_memory_manager import UnifiedMemoryManager
    from ui.command_interface import InteractiveCommandInterface
    from ui.visual_dashboard import (
        VisualDashboard,
        cmd_assign_task,
        cmd_dashboard,
        cmd_system_metrics,
        cmd_worker_status,
    )
except ImportError as e:
    print(f"⚠️ Import error: {e}")
    VisualDashboard = None
    InteractiveCommandInterface = None
    DynamicAIOrganizationSystem = None
    UnifiedMemoryManager = None
    ConductorCore = None


class AIOrganizationUI:
    """Main UI controller for AI organization system"""

    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None
        self.project_root = Path(__file__).parent.parent.parent

        # Initialize core systems
        self.dashboard = None
        self.command_interface = None
        self.ai_org_system = None
        self.memory_manager = None
        self.conductor = None

        # UI state
        self.is_running = False
        self.current_mode = "menu"  # menu, dashboard, command, worker

        # Initialize systems
        self._initialize_systems()

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _initialize_systems(self):
        """Initialize all UI and backend systems"""
        try:
            # Initialize dashboard
            if VisualDashboard:
                self.dashboard = VisualDashboard()
                print("✅ Visual Dashboard initialized")

            # Initialize command interface
            if InteractiveCommandInterface:
                self.command_interface = InteractiveCommandInterface()
                print("✅ Command Interface initialized")

            # Initialize AI organization system
            if DynamicAIOrganizationSystem:
                self.ai_org_system = DynamicAIOrganizationSystem()
                print("✅ AI Organization System initialized")

            # Initialize memory manager
            if UnifiedMemoryManager:
                self.memory_manager = UnifiedMemoryManager(self.project_root)
                print("✅ Memory Manager initialized")

            # Initialize conductor
            if ConductorCore:
                self.conductor = ConductorCore(self.project_root)
                print("✅ Conductor System initialized")

        except Exception as e:
            print(f"⚠️ System initialization warning: {e}")

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n🛑 Received signal {signum}, shutting down...")
        self.is_running = False
        sys.exit(0)

    def _create_main_menu(self) -> Panel:
        """Create main menu interface"""
        menu_items = [
            "🎯 AI Organization UI System",
            "=" * 40,
            "",
            "📊 [1] Visual Dashboard - Real-time monitoring",
            "🎮 [2] Interactive Command Interface",
            "👥 [3] Worker Management",
            "📋 [4] Task Assignment",
            "📈 [5] System Metrics",
            "🔧 [6] System Status",
            "❓ [7] Help & Documentation",
            "🚪 [q] Quit",
            "",
            "💡 Select an option by number or letter",
        ]

        content = Text("\n".join(menu_items))
        return Panel(content, title="AI Organization UI", border_style="blue")

    def _show_system_status(self):
        """Show comprehensive system status"""
        if not self.console:
            print("❌ Rich console not available")
            return

        # Create system status table
        table = Table(title="System Status")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details", style="dim")

        components = [
            (
                "Visual Dashboard",
                self.dashboard is not None,
                "Real-time monitoring interface",
            ),
            (
                "Command Interface",
                self.command_interface is not None,
                "Interactive command system",
            ),
            (
                "AI Organization",
                self.ai_org_system is not None,
                "Dynamic role management",
            ),
            (
                "Memory Manager",
                self.memory_manager is not None,
                "Unified memory system",
            ),
            ("Conductor", self.conductor is not None, "Task execution system"),
            ("Rich Console", RICH_AVAILABLE, "Terminal UI library"),
        ]

        for name, available, description in components:
            status = "✅ Available" if available else "❌ Not Available"
            table.add_row(name, status, description)

        self.console.print(table)

        # Show worker status if available
        if self.dashboard:
            self.console.print("\n📊 Worker Status Summary:")
            status = self.dashboard.get_system_status()
            metrics = status["system_metrics"]

            summary = [
                f"Active Workers: {metrics['active_workers']}/8",
                f"Completed Tasks: {metrics['completed_tasks']}",
                f"System Uptime: {metrics['uptime']}",
                f"Error Rate: {metrics['error_rate']:.1f}%",
            ]

            for item in summary:
                self.console.print(f"  • {item}")

    def _show_help(self):
        """Show help and documentation"""
        if not self.console:
            print("❌ Rich console not available")
            return

        help_content = [
            "🎯 AI Organization UI System Help",
            "=" * 40,
            "",
            "📊 Visual Dashboard:",
            "  • Real-time monitoring of 8 AI workers",
            "  • Color-coded status indicators",
            "  • Performance metrics and system health",
            "  • Task queue visualization",
            "",
            "🎮 Interactive Command Interface:",
            "  • Type commands to control workers",
            "  • Assign tasks and manage queues",
            "  • View detailed worker information",
            "  • Command history and shortcuts",
            "",
            "👥 Worker Management:",
            "  • View all workers and their status",
            "  • Select and control individual workers",
            "  • Reset worker states",
            "  • Monitor performance metrics",
            "",
            "📋 Task Assignment:",
            "  • Assign tasks to specific workers",
            "  • View task queues and progress",
            "  • Cancel or complete tasks",
            "  • Track task completion rates",
            "",
            "🔧 Common Commands:",
            "  • workers - Show all worker status",
            "  • select <worker_id> - Select a worker",
            "  • assign <worker_id> <task> - Assign task",
            "  • metrics - Show system metrics",
            "  • help - Show command help",
            "",
            "🚪 Press Enter to return to main menu",
        ]

        content = Text("\n".join(help_content))
        panel = Panel(content, title="Help & Documentation", border_style="yellow")
        self.console.print(panel)

        input()  # Wait for user input

    def _run_dashboard(self):
        """Launch the visual dashboard"""
        if not self.dashboard:
            print("❌ Visual Dashboard not available")
            return

        try:
            print("🚀 Launching Visual Dashboard...")
            print("Press Ctrl+C to return to menu")
            asyncio.run(self.dashboard.run_dashboard())
        except KeyboardInterrupt:
            print("\n🔄 Returning to main menu...")
        except Exception as e:
            print(f"❌ Dashboard error: {e}")

    def _run_command_interface(self):
        """Launch the interactive command interface"""
        if not self.command_interface:
            print("❌ Command Interface not available")
            return

        try:
            print("🎮 Launching Command Interface...")
            print("Type 'help' for commands, 'quit' to return to menu")
            self.command_interface.run()
        except KeyboardInterrupt:
            print("\n🔄 Returning to main menu...")
        except Exception as e:
            print(f"❌ Command Interface error: {e}")

    def _run_worker_management(self):
        """Launch worker management interface"""
        if not self.dashboard:
            print("❌ Worker management not available")
            return

        if not self.console:
            print("❌ Rich console not available")
            return

        while True:
            try:
                # Show worker status
                cmd_worker_status()

                # Worker management menu
                menu_options = [
                    "Worker Management Options:",
                    "1. View worker details",
                    "2. Reset worker state",
                    "3. Assign task to worker",
                    "4. View task queues",
                    "5. Return to main menu",
                ]

                self.console.print("\n" + "\n".join(menu_options))

                choice = Prompt.ask("Select option", choices=["1", "2", "3", "4", "5"])

                if choice == "1":
                    worker_id = Prompt.ask("Enter worker ID")
                    cmd_worker_status(worker_id)

                elif choice == "2":
                    worker_id = Prompt.ask("Enter worker ID")
                    if self.dashboard and worker_id in self.dashboard.workers:
                        if Confirm.ask(f"Reset worker {worker_id}?"):
                            worker = self.dashboard.workers[worker_id]
                            worker.status = self.dashboard.WorkerStatus.IDLE
                            worker.current_task = None
                            worker.task_queue.clear()
                            self.console.print(
                                f"✅ Worker {worker_id} reset", style="green"
                            )
                    else:
                        self.console.print("❌ Worker not found", style="red")

                elif choice == "3":
                    worker_id = Prompt.ask("Enter worker ID")
                    task = Prompt.ask("Enter task description")
                    cmd_assign_task(worker_id, task)

                elif choice == "4":
                    if self.dashboard:
                        has_tasks = False
                        for _worker_id, worker in self.dashboard.workers.items():
                            if worker.task_queue or worker.current_task:
                                has_tasks = True
                                self.console.print(
                                    f"\n{worker.icon} {worker.display_name}:",
                                    style="bold",
                                )

                                if worker.current_task:
                                    self.console.print(
                                        f"  🔄 Current: {worker.current_task}",
                                        style="yellow",
                                    )

                                if worker.task_queue:
                                    self.console.print(
                                        f"  📋 Queue ({len(worker.task_queue)}):",
                                        style="blue",
                                    )
                                    for i, task in enumerate(worker.task_queue, 1):
                                        self.console.print(
                                            f"    {i}. {task}", style="dim"
                                        )

                        if not has_tasks:
                            self.console.print(
                                "📭 No active tasks or queues", style="dim"
                            )

                elif choice == "5":
                    break

                input("\nPress Enter to continue...")

            except KeyboardInterrupt:
                break
            except Exception as e:
                self.console.print(f"❌ Error: {e}", style="red")

    def run(self):
        """Run the main UI system"""
        if not RICH_AVAILABLE:
            print("❌ Rich library not available. Install with: pip install rich")
            return

        self.is_running = True

        try:
            while self.is_running:
                self.console.clear()
                self.console.print(self._create_main_menu())

                choice = Prompt.ask(
                    "Select option", choices=["1", "2", "3", "4", "5", "6", "7", "q"]
                )

                if choice == "1":
                    self._run_dashboard()

                elif choice == "2":
                    self._run_command_interface()

                elif choice == "3":
                    self._run_worker_management()

                elif choice == "4":
                    # Task assignment interface
                    if self.dashboard:
                        worker_id = Prompt.ask("Enter worker ID")
                        task = Prompt.ask("Enter task description")
                        cmd_assign_task(worker_id, task)
                        input("Press Enter to continue...")
                    else:
                        print("❌ Task assignment not available")

                elif choice == "5":
                    cmd_system_metrics()
                    input("Press Enter to continue...")

                elif choice == "6":
                    self._show_system_status()
                    input("Press Enter to continue...")

                elif choice == "7":
                    self._show_help()

                elif choice == "q":
                    if Confirm.ask("Are you sure you want to quit?"):
                        self.is_running = False

        except KeyboardInterrupt:
            print("\n🛑 Interrupted by user")
        except Exception as e:
            print(f"❌ UI System error: {e}")

        finally:
            print("👋 AI Organization UI closed")


def main():
    """Main entry point with argument parsing"""
    parser = argparse.ArgumentParser(description="AI Organization UI System")
    parser.add_argument(
        "--mode",
        choices=["menu", "dashboard", "command", "worker"],
        default="menu",
        help="Launch mode (default: menu)",
    )
    parser.add_argument("--worker-id", help="Worker ID for worker-specific commands")
    parser.add_argument("--task", help="Task description for assignment")

    args = parser.parse_args()

    # Direct mode launches
    if args.mode == "dashboard":
        cmd_dashboard()
        return

    elif args.mode == "command":
        if InteractiveCommandInterface:
            interface = InteractiveCommandInterface()
            interface.run()
        else:
            print("❌ Command interface not available")
        return

    elif args.mode == "worker":
        if args.worker_id:
            cmd_worker_status(args.worker_id)
        else:
            cmd_worker_status()

        if args.task and args.worker_id:
            cmd_assign_task(args.worker_id, args.task)
        return

    # Default: run main menu
    ui = AIOrganizationUI()
    ui.run()


if __name__ == "__main__":
    main()
