#!/usr/bin/env python3
"""
🎮 Interactive Command Interface - AI Organization Command System
================================================================

Advanced command interface for managing AI workers:
- Interactive worker selection
- Real-time command execution
- Keyboard shortcuts and navigation
- Context-sensitive help
- Command history and autocomplete
"""

import asyncio
import sys
import termios
import tty
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Callable, Dict, List, Tuple

# Rich library imports
try:
    from rich.columns import Columns
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Confirm, Prompt
    from rich.table import Table
    from rich.text import Text

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

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


# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from ai.ai_organization_system import DynamicAIOrganizationSystem
    from ui.visual_dashboard import VisualDashboard, WorkerStatus
except ImportError as e:
    print(f"⚠️ Import error: {e}")
    VisualDashboard = None
    DynamicAIOrganizationSystem = None


class CommandType(Enum):
    """Command types"""

    SYSTEM = "system"
    WORKER = "worker"
    TASK = "task"
    VIEW = "view"
    HELP = "help"


@dataclass
class Command:
    """Command definition"""

    name: str
    description: str
    type: CommandType
    handler: Callable
    aliases: List[str] = None
    args: List[str] = None
    help_text: str = ""


class InteractiveCommandInterface:
    """Interactive command interface for AI organization"""

    def __init__(self):
        if not RICH_AVAILABLE:
            raise ImportError("Rich library is required for command interface")

        self.console = Console()
        self.dashboard = VisualDashboard() if VisualDashboard else None
        self.ai_org_system = (
            DynamicAIOrganizationSystem() if DynamicAIOrganizationSystem else None
        )

        # Interface state
        self.is_running = False
        self.current_mode = "main"  # main, worker_select, task_assign
        self.selected_worker = None
        self.command_history: List[str] = []
        self.command_index = 0

        # Terminal settings
        self.old_settings = None

        # Initialize commands
        self.commands = self._initialize_commands()

        # Command shortcuts
        self.shortcuts = {
            "q": "quit",
            "h": "help",
            "w": "workers",
            "m": "metrics",
            "s": "status",
            "t": "tasks",
            "l": "logs",
            "r": "refresh",
            "c": "clear",
            "d": "dashboard",
        }

    def _initialize_commands(self) -> Dict[str, Command]:
        """Initialize all available commands"""
        return {
            # System commands
            "help": Command(
                name="help",
                description="Show help information",
                type=CommandType.HELP,
                handler=self._cmd_help,
                aliases=["h", "?"],
                help_text="Show available commands and their usage",
            ),
            "quit": Command(
                name="quit",
                description="Exit the interface",
                type=CommandType.SYSTEM,
                handler=self._cmd_quit,
                aliases=["q", "exit"],
                help_text="Exit the command interface",
            ),
            "clear": Command(
                name="clear",
                description="Clear the screen",
                type=CommandType.SYSTEM,
                handler=self._cmd_clear,
                aliases=["c", "cls"],
                help_text="Clear the terminal screen",
            ),
            "refresh": Command(
                name="refresh",
                description="Refresh dashboard data",
                type=CommandType.SYSTEM,
                handler=self._cmd_refresh,
                aliases=["r"],
                help_text="Refresh all dashboard data",
            ),
            # View commands
            "dashboard": Command(
                name="dashboard",
                description="Launch full dashboard",
                type=CommandType.VIEW,
                handler=self._cmd_dashboard,
                aliases=["d"],
                help_text="Launch the interactive dashboard",
            ),
            "workers": Command(
                name="workers",
                description="Show worker status",
                type=CommandType.VIEW,
                handler=self._cmd_workers,
                aliases=["w"],
                help_text="Display all workers and their current status",
            ),
            "metrics": Command(
                name="metrics",
                description="Show system metrics",
                type=CommandType.VIEW,
                handler=self._cmd_metrics,
                aliases=["m"],
                help_text="Display system performance metrics",
            ),
            "status": Command(
                name="status",
                description="Show overall system status",
                type=CommandType.VIEW,
                handler=self._cmd_status,
                aliases=["s"],
                help_text="Show comprehensive system status",
            ),
            "logs": Command(
                name="logs",
                description="Show activity logs",
                type=CommandType.VIEW,
                handler=self._cmd_logs,
                aliases=["l"],
                help_text="Display recent activity logs",
            ),
            # Worker commands
            "select": Command(
                name="select",
                description="Select a worker",
                type=CommandType.WORKER,
                handler=self._cmd_select,
                args=["worker_id"],
                help_text="Select a worker for detailed operations",
            ),
            "worker": Command(
                name="worker",
                description="Show worker details",
                type=CommandType.WORKER,
                handler=self._cmd_worker,
                args=["worker_id"],
                help_text="Show detailed information about a specific worker",
            ),
            "reset": Command(
                name="reset",
                description="Reset worker state",
                type=CommandType.WORKER,
                handler=self._cmd_reset,
                args=["worker_id"],
                help_text="Reset a worker's state and clear its queue",
            ),
            # Task commands
            "assign": Command(
                name="assign",
                description="Assign task to worker",
                type=CommandType.TASK,
                handler=self._cmd_assign,
                args=["worker_id", "task"],
                help_text="Assign a task to a specific worker",
            ),
            "tasks": Command(
                name="tasks",
                description="Show task queues",
                type=CommandType.TASK,
                handler=self._cmd_tasks,
                aliases=["t"],
                help_text="Display task queues for all workers",
            ),
            "complete": Command(
                name="complete",
                description="Mark task as complete",
                type=CommandType.TASK,
                handler=self._cmd_complete,
                args=["worker_id", "task_id"],
                help_text="Mark a task as completed for a worker",
            ),
            "cancel": Command(
                name="cancel",
                description="Cancel a task",
                type=CommandType.TASK,
                handler=self._cmd_cancel,
                args=["worker_id", "task_id"],
                help_text="Cancel a pending task",
            ),
        }

    def _setup_terminal(self):
        """Setup terminal for interactive input"""
        if sys.platform != "win32":
            self.old_settings = termios.tcgetattr(sys.stdin)

    def _restore_terminal(self):
        """Restore terminal settings"""
        if self.old_settings and sys.platform != "win32":
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)

    def _get_key(self) -> str:
        """Get a single key press"""
        if sys.platform == "win32":
            import msvcrt

            return msvcrt.getch().decode("utf-8")
        else:
            tty.setraw(sys.stdin.fileno())
            key = sys.stdin.read(1)
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)
            return key

    def _parse_command(self, input_text: str) -> Tuple[str, List[str]]:
        """Parse command input"""
        parts = input_text.strip().split()
        if not parts:
            return "", []

        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []

        # Check for shortcuts
        if command in self.shortcuts:
            command = self.shortcuts[command]

        # Check for aliases
        for cmd_name, cmd_obj in self.commands.items():
            if cmd_obj.aliases and command in cmd_obj.aliases:
                command = cmd_name
                break

        return command, args

    def _execute_command(self, command: str, args: List[str]) -> bool:
        """Execute a command"""
        if command not in self.commands:
            self.console.print(f"❌ Unknown command: {command}", style="red")
            self.console.print("Type 'help' for available commands", style="dim")
            return True

        cmd_obj = self.commands[command]

        # Check argument count
        if cmd_obj.args and len(args) < len(cmd_obj.args):
            self.console.print(
                f"❌ Command '{command}' requires {len(cmd_obj.args)} arguments",
                style="red",
            )
            self.console.print(
                f"Usage: {command} {' '.join(cmd_obj.args)}", style="dim"
            )
            return True

        try:
            return cmd_obj.handler(args)
        except Exception as e:
            self.console.print(f"❌ Command execution failed: {e}", style="red")
            return True

    def _create_header(self) -> Panel:
        """Create interface header"""
        title = Text("🎮 AI Organization Command Interface", style="bold blue")

        status_parts = []
        if self.selected_worker:
            status_parts.append(f"Selected: {self.selected_worker}")
        status_parts.append(f"Mode: {self.current_mode}")

        status_text = " | ".join(status_parts)

        header_content = Columns([title, Text(status_text, style="dim")])

        return Panel(header_content, style="bold")

    def _create_prompt(self) -> str:
        """Create command prompt"""
        prompt = "ai-org"
        if self.selected_worker:
            prompt += f":{self.selected_worker}"
        prompt += "$ "
        return prompt

    # Command handlers
    def _cmd_help(self, args: List[str]) -> bool:
        """Show help information"""
        if args:
            # Show help for specific command
            command = args[0]
            if command in self.commands:
                cmd = self.commands[command]
                table = Table(title=f"Help: {cmd.name}")
                table.add_column("Property", style="cyan")
                table.add_column("Value", style="green")

                table.add_row("Name", cmd.name)
                table.add_row("Description", cmd.description)
                table.add_row("Type", cmd.type.value)
                table.add_row(
                    "Aliases", ", ".join(cmd.aliases) if cmd.aliases else "None"
                )
                table.add_row("Arguments", ", ".join(cmd.args) if cmd.args else "None")
                table.add_row("Help", cmd.help_text)

                self.console.print(table)
            else:
                self.console.print(f"❌ Unknown command: {command}", style="red")
        else:
            # Show all commands
            table = Table(title="Available Commands")
            table.add_column("Command", style="cyan")
            table.add_column("Description", style="green")
            table.add_column("Type", style="yellow")
            table.add_column("Aliases", style="dim")

            for cmd_name, cmd in self.commands.items():
                aliases = ", ".join(cmd.aliases) if cmd.aliases else ""
                table.add_row(cmd_name, cmd.description, cmd.type.value, aliases)

            self.console.print(table)

            # Show shortcuts
            self.console.print("\n📌 Quick Shortcuts:", style="bold")
            for shortcut, command in self.shortcuts.items():
                self.console.print(f"  {shortcut} → {command}", style="dim")

        return True

    def _cmd_quit(self, args: List[str]) -> bool:
        """Quit the interface"""
        if Confirm.ask("Are you sure you want to quit?"):
            return False
        return True

    def _cmd_clear(self, args: List[str]) -> bool:
        """Clear the screen"""
        self.console.clear()
        return True

    def _cmd_refresh(self, args: List[str]) -> bool:
        """Refresh dashboard data"""
        self.console.print("🔄 Refreshing data...", style="yellow")
        # Trigger dashboard refresh if available
        if self.dashboard:
            self.dashboard._update_system_metrics()
        self.console.print("✅ Data refreshed", style="green")
        return True

    def _cmd_dashboard(self, args: List[str]) -> bool:
        """Launch full dashboard"""
        if not self.dashboard:
            self.console.print("❌ Dashboard not available", style="red")
            return True

        self.console.print("🚀 Launching dashboard...", style="yellow")
        try:
            asyncio.run(self.dashboard.run_dashboard())
        except KeyboardInterrupt:
            self.console.print("\n🛑 Dashboard stopped", style="dim")
        except Exception as e:
            self.console.print(f"❌ Dashboard error: {e}", style="red")

        return True

    def _cmd_workers(self, args: List[str]) -> bool:
        """Show worker status"""
        if not self.dashboard:
            self.console.print("❌ Dashboard not available", style="red")
            return True

        status = self.dashboard.get_system_status()

        table = Table(title="Worker Status")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("Tasks", style="blue")
        table.add_column("Errors", style="red")
        table.add_column("Queue", style="magenta")

        for worker_id, worker_data in status["workers"].items():
            worker_details = self.dashboard.get_worker_details(worker_id)

            # Status styling
            status_style = "green" if worker_data["status"] == "active" else "yellow"

            table.add_row(
                worker_id,
                f"{worker_details['icon']} {worker_details['display_name']}",
                f"[{status_style}]{worker_data['status'].upper()}[/]",
                str(worker_data["tasks_completed"]),
                str(worker_data["error_count"]),
                str(worker_data["queue_length"]),
            )

        self.console.print(table)
        return True

    def _cmd_metrics(self, args: List[str]) -> bool:
        """Show system metrics"""
        if not self.dashboard:
            self.console.print("❌ Dashboard not available", style="red")
            return True

        status = self.dashboard.get_system_status()
        metrics = status["system_metrics"]

        table = Table(title="System Metrics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        for key, value in metrics.items():
            display_key = key.replace("_", " ").title()
            if isinstance(value, float):
                display_value = (
                    f"{value:.1f}{'%' if 'usage' in key or 'rate' in key else ''}"
                )
            else:
                display_value = str(value)

            table.add_row(display_key, display_value)

        self.console.print(table)
        return True

    def _cmd_status(self, args: List[str]) -> bool:
        """Show overall system status"""
        if not self.dashboard:
            self.console.print("❌ Dashboard not available", style="red")
            return True

        status = self.dashboard.get_system_status()

        # System overview
        self.console.print("🎯 System Status Overview", style="bold blue")
        self.console.print(f"Running: {'✅' if status['is_running'] else '❌'}")
        self.console.print(
            f"Active Workers: {status['system_metrics']['active_workers']}/8"
        )
        self.console.print(
            f"Completed Tasks: {status['system_metrics']['completed_tasks']}"
        )
        self.console.print(f"Error Rate: {status['system_metrics']['error_rate']:.1f}%")

        # Quick worker summary
        active_workers = []
        for worker_id, worker_data in status["workers"].items():
            if worker_data["status"] == "active":
                worker_details = self.dashboard.get_worker_details(worker_id)
                active_workers.append(
                    f"{worker_details['icon']} {worker_details['display_name']}"
                )

        if active_workers:
            self.console.print(f"\n🔄 Active Workers: {', '.join(active_workers)}")

        return True

    def _cmd_logs(self, args: List[str]) -> bool:
        """Show activity logs"""
        if not self.dashboard:
            self.console.print("❌ Dashboard not available", style="red")
            return True

        # Get recent logs from dashboard
        logs = (
            self.dashboard.command_history[-20:]
            if self.dashboard.command_history
            else ["No recent activity"]
        )

        self.console.print("📋 Recent Activity Logs", style="bold blue")
        for i, log in enumerate(logs, 1):
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.console.print(f"[dim]{i:2d}.[/] [{timestamp}] {log}")

        return True

    def _cmd_select(self, args: List[str]) -> bool:
        """Select a worker"""
        if not args:
            self.console.print("❌ Worker ID required", style="red")
            return True

        worker_id = args[0]

        if not self.dashboard:
            self.console.print("❌ Dashboard not available", style="red")
            return True

        details = self.dashboard.get_worker_details(worker_id)
        if "error" in details:
            self.console.print(f"❌ {details['error']}", style="red")
            return True

        self.selected_worker = worker_id
        self.console.print(
            f"✅ Selected worker: {details['icon']} {details['display_name']}",
            style="green",
        )
        return True

    def _cmd_worker(self, args: List[str]) -> bool:
        """Show worker details"""
        if not args:
            if self.selected_worker:
                worker_id = self.selected_worker
            else:
                self.console.print(
                    "❌ Worker ID required or select a worker first", style="red"
                )
                return True
        else:
            worker_id = args[0]

        if not self.dashboard:
            self.console.print("❌ Dashboard not available", style="red")
            return True

        details = self.dashboard.get_worker_details(worker_id)
        if "error" in details:
            self.console.print(f"❌ {details['error']}", style="red")
            return True

        # Create detailed worker info
        table = Table(title=f"Worker Details: {details['display_name']}")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")

        for key, value in details.items():
            if key not in ["id", "collaboration_partners", "task_queue"]:
                display_key = key.replace("_", " ").title()
                if isinstance(value, float):
                    display_value = f"{value:.2f}"
                else:
                    display_value = str(value)
                table.add_row(display_key, display_value)

        self.console.print(table)

        # Show task queue if exists
        if details.get("task_queue"):
            self.console.print("\n📋 Task Queue:", style="bold")
            for i, task in enumerate(details["task_queue"], 1):
                self.console.print(f"  {i}. {task}")

        return True

    def _cmd_reset(self, args: List[str]) -> bool:
        """Reset worker state"""
        if not args:
            self.console.print("❌ Worker ID required", style="red")
            return True

        worker_id = args[0]

        if not self.dashboard:
            self.console.print("❌ Dashboard not available", style="red")
            return True

        details = self.dashboard.get_worker_details(worker_id)
        if "error" in details:
            self.console.print(f"❌ {details['error']}", style="red")
            return True

        if Confirm.ask(f"Reset worker {details['display_name']}?"):
            # Reset worker in dashboard
            if worker_id in self.dashboard.workers:
                worker = self.dashboard.workers[worker_id]
                worker.status = WorkerStatus.IDLE
                worker.current_task = None
                worker.task_queue.clear()
                worker.error_count = 0

                self.console.print(
                    f"✅ Worker {details['display_name']} reset", style="green"
                )
            else:
                self.console.print("❌ Worker not found", style="red")

        return True

    def _cmd_assign(self, args: List[str]) -> bool:
        """Assign task to worker"""
        if len(args) < 2:
            self.console.print("❌ Usage: assign <worker_id> <task>", style="red")
            return True

        worker_id = args[0]
        task = " ".join(args[1:])

        if not self.dashboard:
            self.console.print("❌ Dashboard not available", style="red")
            return True

        result = self.dashboard.assign_task_to_worker(worker_id, task)

        if "error" in result:
            self.console.print(f"❌ {result['error']}", style="red")
        else:
            self.console.print(f"✅ Task assigned to worker {worker_id}", style="green")
            if "result" in result:
                self.console.print(f"Result: {result['result']}")

        return True

    def _cmd_tasks(self, args: List[str]) -> bool:
        """Show task queues"""
        if not self.dashboard:
            self.console.print("❌ Dashboard not available", style="red")
            return True

        # Show task queues for all workers
        has_tasks = False

        for _worker_id, worker in self.dashboard.workers.items():
            if worker.task_queue or worker.current_task:
                has_tasks = True
                self.console.print(
                    f"\n{worker.icon} {worker.display_name}:", style="bold"
                )

                if worker.current_task:
                    self.console.print(
                        f"  🔄 Current: {worker.current_task}", style="yellow"
                    )

                if worker.task_queue:
                    self.console.print(
                        f"  📋 Queue ({len(worker.task_queue)}):", style="blue"
                    )
                    for i, task in enumerate(worker.task_queue, 1):
                        self.console.print(f"    {i}. {task}", style="dim")

        if not has_tasks:
            self.console.print("📭 No active tasks or queues", style="dim")

        return True

    def _cmd_complete(self, args: List[str]) -> bool:
        """Mark task as complete"""
        if len(args) < 2:
            self.console.print("❌ Usage: complete <worker_id> <task_id>", style="red")
            return True

        worker_id = args[0]
        task_id = args[1]

        if not self.dashboard:
            self.console.print("❌ Dashboard not available", style="red")
            return True

        if worker_id in self.dashboard.workers:
            worker = self.dashboard.workers[worker_id]

            # Complete current task
            if worker.current_task and task_id == "current":
                worker.current_task = None
                worker.status = WorkerStatus.IDLE
                worker.tasks_completed += 1
                self.console.print(
                    f"✅ Current task completed for {worker.display_name}",
                    style="green",
                )

            # Complete queued task
            elif task_id.isdigit():
                task_index = int(task_id) - 1
                if 0 <= task_index < len(worker.task_queue):
                    completed_task = worker.task_queue.pop(task_index)
                    worker.tasks_completed += 1
                    self.console.print(
                        f"✅ Task completed: {completed_task}", style="green"
                    )
                else:
                    self.console.print("❌ Invalid task ID", style="red")
            else:
                self.console.print(
                    "❌ Task ID must be 'current' or a number", style="red"
                )
        else:
            self.console.print("❌ Worker not found", style="red")

        return True

    def _cmd_cancel(self, args: List[str]) -> bool:
        """Cancel a task"""
        if len(args) < 2:
            self.console.print("❌ Usage: cancel <worker_id> <task_id>", style="red")
            return True

        worker_id = args[0]
        task_id = args[1]

        if not self.dashboard:
            self.console.print("❌ Dashboard not available", style="red")
            return True

        if worker_id in self.dashboard.workers:
            worker = self.dashboard.workers[worker_id]

            # Cancel current task
            if worker.current_task and task_id == "current":
                cancelled_task = worker.current_task
                worker.current_task = None
                worker.status = WorkerStatus.IDLE
                self.console.print(
                    f"🚫 Cancelled current task: {cancelled_task}", style="yellow"
                )

            # Cancel queued task
            elif task_id.isdigit():
                task_index = int(task_id) - 1
                if 0 <= task_index < len(worker.task_queue):
                    cancelled_task = worker.task_queue.pop(task_index)
                    self.console.print(
                        f"🚫 Cancelled task: {cancelled_task}", style="yellow"
                    )
                else:
                    self.console.print("❌ Invalid task ID", style="red")
            else:
                self.console.print(
                    "❌ Task ID must be 'current' or a number", style="red"
                )
        else:
            self.console.print("❌ Worker not found", style="red")

        return True

    def run(self):
        """Run the interactive command interface"""
        self.console.clear()
        self.console.print(self._create_header())

        self.console.print("\n🎮 Interactive Command Interface", style="bold blue")
        self.console.print("Type 'help' for available commands, 'quit' to exit\n")

        self.is_running = True
        self._setup_terminal()

        try:
            while self.is_running:
                try:
                    # Get command input
                    prompt = self._create_prompt()
                    command_input = Prompt.ask(prompt)

                    if not command_input.strip():
                        continue

                    # Add to history
                    self.command_history.append(command_input)

                    # Parse and execute command
                    command, args = self._parse_command(command_input)
                    if command:
                        self.is_running = self._execute_command(command, args)

                except KeyboardInterrupt:
                    self.console.print("\n🛑 Use 'quit' to exit", style="dim")
                    continue
                except EOFError:
                    break
                except Exception as e:
                    self.console.print(f"❌ Error: {e}", style="red")

        finally:
            self._restore_terminal()
            self.console.print("\n👋 Interface closed", style="dim")


def main():
    """Main entry point"""
    try:
        interface = InteractiveCommandInterface()
        interface.run()
    except ImportError as e:
        print(f"❌ {e}")
        print("Install required dependencies: pip install rich")
    except Exception as e:
        print(f"❌ Interface error: {e}")


if __name__ == "__main__":
    main()
