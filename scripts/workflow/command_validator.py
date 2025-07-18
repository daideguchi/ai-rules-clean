#!/usr/bin/env python3
"""
✅ Command Validator and Dependency System
==========================================
Validates command execution order and dependencies
"""

import json
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


@dataclass
class CommandDependency:
    """Command dependency definition"""
    command: str
    depends_on: List[str]
    conflicts_with: List[str]
    prerequisites: List[str]  # Environment/file prerequisites
    category: str
    priority: int  # 1=critical, 2=important, 3=optional
    estimated_time: int  # seconds
    description: str


class CommandValidator:
    """Validates command execution and dependencies"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.dependencies = self._load_dependencies()
        self.command_history = self._load_execution_history()
        self.system_state = self._check_system_state()

    def _load_dependencies(self) -> Dict[str, CommandDependency]:
        """Load command dependencies configuration"""
        dependencies = {}

        # Core system dependencies
        dependencies.update({
            "declare-president": CommandDependency(
                command="declare-president",
                depends_on=[],
                conflicts_with=[],
                prerequisites=["Makefile"],
                category="core",
                priority=1,
                estimated_time=5,
                description="Essential system rule validation"
            ),
            "install": CommandDependency(
                command="install",
                depends_on=[],
                conflicts_with=[],
                prerequisites=["requirements.txt"],
                category="core",
                priority=1,
                estimated_time=60,
                description="Install system dependencies"
            ),
            "mcp-setup": CommandDependency(
                command="mcp-setup",
                depends_on=["install"],
                conflicts_with=[],
                prerequisites=[".env"],
                category="setup",
                priority=2,
                estimated_time=30,
                description="Setup MCP servers"
            ),
            "ai-org-start": CommandDependency(
                command="ai-org-start",
                depends_on=["declare-president", "mcp-setup"],
                conflicts_with=[],
                prerequisites=["config/unified_config.json"],
                category="ai",
                priority=2,
                estimated_time=15,
                description="Start AI organization system"
            ),
            "slack-setup": CommandDependency(
                command="slack-setup",
                depends_on=["mcp-setup"],
                conflicts_with=[],
                prerequisites=[".env"],
                category="communication",
                priority=3,
                estimated_time=45,
                description="Setup Slack integration"
            ),
            "claude-code-web-ui": CommandDependency(
                command="claude-code-web-ui",
                depends_on=["install"],
                conflicts_with=[],
                prerequisites=["src/web-ui/package.json"],
                category="ui",
                priority=3,
                estimated_time=10,
                description="Start web UI server"
            ),
            "test": CommandDependency(
                command="test",
                depends_on=["install"],
                conflicts_with=[],
                prerequisites=["requirements.txt"],
                category="testing",
                priority=2,
                estimated_time=120,
                description="Run test suite"
            ),
            "cleanup": CommandDependency(
                command="cleanup",
                depends_on=[],
                conflicts_with=["ai-org-start", "claude-code-web-ui"],
                prerequisites=[],
                category="maintenance",
                priority=3,
                estimated_time=30,
                description="Clean up system resources"
            ),
            "backup-create": CommandDependency(
                command="backup-create",
                depends_on=[],
                conflicts_with=[],
                prerequisites=["runtime/"],
                category="backup",
                priority=2,
                estimated_time=60,
                description="Create system backup"
            ),
            "deploy-production": CommandDependency(
                command="deploy-production",
                depends_on=["test", "validate", "backup-create"],
                conflicts_with=[],
                prerequisites=["docker-compose.yml"],
                category="deployment",
                priority=1,
                estimated_time=300,
                description="Deploy to production"
            )
        })

        # Auto-generate dependencies for similar commands
        self._auto_generate_dependencies(dependencies)

        return dependencies

    def _auto_generate_dependencies(self, dependencies: Dict[str, CommandDependency]):
        """Auto-generate dependencies for command patterns"""
        makefile_commands = self._get_makefile_commands()

        for cmd in makefile_commands:
            if cmd in dependencies:
                continue

            # Pattern-based dependency generation
            if cmd.startswith("mcp-"):
                dependencies[cmd] = CommandDependency(
                    command=cmd,
                    depends_on=["mcp-setup"] if cmd != "mcp-setup" else [],
                    conflicts_with=[],
                    prerequisites=[],
                    category="mcp",
                    priority=2,
                    estimated_time=15,
                    description=f"MCP operation: {cmd}"
                )
            elif cmd.startswith("slack-"):
                dependencies[cmd] = CommandDependency(
                    command=cmd,
                    depends_on=["slack-setup"] if cmd != "slack-setup" else [],
                    conflicts_with=[],
                    prerequisites=[],
                    category="communication",
                    priority=3,
                    estimated_time=10,
                    description=f"Slack operation: {cmd}"
                )
            elif cmd.startswith("ai-"):
                dependencies[cmd] = CommandDependency(
                    command=cmd,
                    depends_on=["declare-president"],
                    conflicts_with=[],
                    prerequisites=[],
                    category="ai",
                    priority=2,
                    estimated_time=20,
                    description=f"AI operation: {cmd}"
                )
            elif cmd.startswith("test-"):
                dependencies[cmd] = CommandDependency(
                    command=cmd,
                    depends_on=["install"],
                    conflicts_with=[],
                    prerequisites=[],
                    category="testing",
                    priority=2,
                    estimated_time=30,
                    description=f"Test operation: {cmd}"
                )
            elif cmd.startswith("db-"):
                dependencies[cmd] = CommandDependency(
                    command=cmd,
                    depends_on=["install"],
                    conflicts_with=[],
                    prerequisites=["config/unified_config.json"],
                    category="database",
                    priority=2,
                    estimated_time=45,
                    description=f"Database operation: {cmd}"
                )

    def _get_makefile_commands(self) -> List[str]:
        """Get all commands from Makefile"""
        commands = []
        try:
            with open(self.project_root / "Makefile") as f:
                content = f.read()

            pattern = r'^([a-zA-Z][a-zA-Z0-9_-]*)\s*:'
            matches = re.findall(pattern, content, re.MULTILINE)
            commands = list(set(matches))

        except Exception as e:
            print(f"⚠️ Error reading Makefile: {e}")

        return commands

    def _load_execution_history(self) -> List[Dict]:
        """Load command execution history"""
        history_file = self.project_root / ".command_execution_history.json"
        try:
            if history_file.exists():
                with open(history_file) as f:
                    return json.load(f)
        except:
            pass
        return []

    def _save_execution_history(self):
        """Save command execution history"""
        history_file = self.project_root / ".command_execution_history.json"
        try:
            with open(history_file, 'w') as f:
                json.dump(self.command_history[-100:], f, indent=2)  # Keep last 100
        except Exception as e:
            print(f"⚠️ Could not save history: {e}")

    def _check_system_state(self) -> Dict[str, bool]:
        """Check current system state"""
        state = {}

        # Check file prerequisites
        files_to_check = [
            "Makefile",
            "requirements.txt",
            ".env",
            "config/unified_config.json",
            "src/web-ui/package.json",
            "docker-compose.yml"
        ]

        for file_path in files_to_check:
            state[file_path] = (self.project_root / file_path).exists()

        # Check directory prerequisites
        dirs_to_check = ["runtime/", "logs/", "src/"]
        for dir_path in dirs_to_check:
            state[dir_path] = (self.project_root / dir_path).exists()

        # Check running processes
        state["web_ui_running"] = self._is_process_running("node.*server.js")
        state["python_servers_running"] = self._is_process_running("python.*mcp.*server")

        return state

    def _is_process_running(self, pattern: str) -> bool:
        """Check if process matching pattern is running"""
        try:
            result = subprocess.run(
                ["pgrep", "-f", pattern],
                capture_output=True,
                text=True
            )
            return result.returncode == 0 and result.stdout.strip()
        except:
            return False

    def validate_command(self, command: str) -> Tuple[bool, List[str]]:
        """Validate if command can be executed"""
        issues = []

        if command not in self.dependencies:
            issues.append(f"⚠️ Command '{command}' not found in dependency system")
            return len(issues) == 0, issues

        dep = self.dependencies[command]

        # Check prerequisites
        for prereq in dep.prerequisites:
            if not self.system_state.get(prereq, False):
                issues.append(f"❌ Missing prerequisite: {prereq}")

        # Check dependencies
        for dependency in dep.depends_on:
            if not self._is_command_executed_recently(dependency):
                issues.append(f"🔗 Dependency not satisfied: {dependency}")

        # Check conflicts
        for conflict in dep.conflicts_with:
            if self._is_command_running(conflict):
                issues.append(f"⚠️ Conflict with running command: {conflict}")

        return len(issues) == 0, issues

    def _is_command_executed_recently(self, command: str) -> bool:
        """Check if command was executed recently"""
        recent_commands = [
            entry["command"] for entry in self.command_history[-20:]
            if entry.get("success", False)
        ]
        return command in recent_commands

    def _is_command_running(self, command: str) -> bool:
        """Check if command is currently running"""
        # This is a simplified check - in reality, you'd check process status
        return False

    def get_execution_plan(self, target_command: str) -> List[str]:
        """Get optimal execution plan for target command"""
        if target_command not in self.dependencies:
            return [target_command]

        plan = []
        visited = set()

        def add_dependencies(cmd):
            if cmd in visited:
                return
            visited.add(cmd)

            if cmd in self.dependencies:
                dep = self.dependencies[cmd]
                for dependency in dep.depends_on:
                    add_dependencies(dependency)

            if cmd not in plan:
                plan.append(cmd)

        add_dependencies(target_command)
        return plan

    def estimate_execution_time(self, commands: List[str]) -> int:
        """Estimate total execution time for commands"""
        total_time = 0
        for cmd in commands:
            if cmd in self.dependencies:
                total_time += self.dependencies[cmd].estimated_time
            else:
                total_time += 30  # Default estimate
        return total_time

    def validate_workflow(self, commands: List[str]) -> Tuple[bool, List[str]]:
        """Validate an entire workflow"""
        issues = []

        for i, cmd in enumerate(commands):
            valid, cmd_issues = self.validate_command(cmd)
            if not valid:
                issues.extend([f"Step {i+1} ({cmd}): {issue}" for issue in cmd_issues])

        return len(issues) == 0, issues

    def record_execution(self, command: str, success: bool, execution_time: int = 0):
        """Record command execution"""
        entry = {
            "command": command,
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "execution_time": execution_time
        }

        self.command_history.append(entry)
        self._save_execution_history()

    def get_recommended_next_commands(self) -> List[str]:
        """Get recommended next commands based on current state"""
        recommendations = []

        # Always recommend president declaration if not done
        if not self._is_command_executed_recently("declare-president"):
            recommendations.append("declare-president")

        # Recommend setup commands if not done
        if not self._is_command_executed_recently("install"):
            recommendations.append("install")

        if not self._is_command_executed_recently("mcp-setup"):
            recommendations.append("mcp-setup")

        # Recommend based on project state
        if self.system_state.get("requirements.txt", False) and not self._is_command_executed_recently("test"):
            recommendations.append("test")

        if self.system_state.get("src/web-ui/package.json", False) and not self.system_state.get("web_ui_running", False):
            recommendations.append("claude-code-web-ui")

        return recommendations[:5]  # Top 5 recommendations

    def generate_workflow_report(self) -> str:
        """Generate a comprehensive workflow report"""
        report = []
        report.append("📊 WORKFLOW ANALYSIS REPORT")
        report.append("=" * 50)

        # System state
        report.append("\n🔍 System State:")
        for key, value in self.system_state.items():
            status = "✅" if value else "❌"
            report.append(f"  {status} {key}")

        # Recent executions
        report.append(f"\n📜 Recent Executions ({len(self.command_history)}):")
        for entry in self.command_history[-5:]:
            status = "✅" if entry["success"] else "❌"
            report.append(f"  {status} {entry['command']} - {entry['timestamp']}")

        # Recommendations
        recommendations = self.get_recommended_next_commands()
        report.append(f"\n💡 Recommendations ({len(recommendations)}):")
        for cmd in recommendations:
            dep = self.dependencies.get(cmd, None)
            if dep:
                report.append(f"  🎯 {cmd} - {dep.description}")

        # Dependency analysis
        report.append("\n🔗 Dependency Analysis:")
        critical_commands = [cmd for cmd, dep in self.dependencies.items() if dep.priority == 1]
        report.append(f"  Critical commands: {len(critical_commands)}")
        report.append(f"  Total dependencies tracked: {len(self.dependencies)}")

        return "\n".join(report)


def main():
    """Main function for testing"""
    validator = CommandValidator()

    # Test command validation
    test_commands = ["declare-president", "mcp-setup", "ai-org-start", "deploy-production"]

    for cmd in test_commands:
        print(f"\n🔍 Validating: {cmd}")
        valid, issues = validator.validate_command(cmd)

        if valid:
            print("✅ Command is valid")
            plan = validator.get_execution_plan(cmd)
            time_estimate = validator.estimate_execution_time(plan)
            print(f"📋 Execution plan: {' → '.join(plan)}")
            print(f"⏱️ Estimated time: {time_estimate} seconds")
        else:
            print("❌ Command has issues:")
            for issue in issues:
                print(f"  {issue}")

    # Generate report
    print("\n" + validator.generate_workflow_report())


if __name__ == "__main__":
    main()
