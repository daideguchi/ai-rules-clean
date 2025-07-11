#!/usr/bin/env python3
"""
AI Organization Tmux Bridge - 統合オーケストレーター
========================================================
Bridges the gap between:
- Individual AI systems (Constitutional AI, Rule-Based Rewards, Memory Inheritance)
- Tmux multi-agent implementation (ai-team.sh)

Provides unified governance across distributed Claude instances.
"""

import json
import logging
import sqlite3
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path for imports
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from src.ai.constitutional_ai import ConstitutionalAI  # noqa: E402
from src.ai.rule_based_rewards import RuleBasedRewards  # noqa: E402
from src.memory.unified_memory_manager import UnifiedMemoryManager  # noqa: E402


@dataclass
class TmuxPaneState:
    """Tmux pane state representation"""

    session: str
    pane_id: str
    role: str  # PRESIDENT, BOSS1, WORKER1, WORKER2, WORKER3
    status: str  # active, idle, processing, error
    last_activity: datetime
    current_task: Optional[str] = None
    violations: List[str] = None

    def __post_init__(self):
        if self.violations is None:
            self.violations = []


@dataclass
class OrganizationState:
    """Overall AI organization state"""

    total_panes: int
    active_panes: int
    current_president: Optional[str]
    distributed_tasks: Dict[str, str]
    governance_status: Dict[str, Any]
    last_sync: datetime


class AIOrganizationTmuxBridge:
    """Unified orchestrator for AI systems and tmux implementation"""

    def __init__(self, project_root: str = None):
        self.project_root = (
            Path(project_root) if project_root else Path(__file__).resolve().parents[2]
        )
        self.runtime_dir = self.project_root / "runtime"
        self.orchestrator_db = self.runtime_dir / "ai_organization_bridge.db"
        self.sync_interval = 5  # seconds
        self.running = False

        # Initialize AI systems
        self.constitutional_ai = ConstitutionalAI()
        self.rule_based_rewards = RuleBasedRewards()
        self.memory_manager = UnifiedMemoryManager()

        # Tmux configuration
        self.tmux_sessions = {
            "president": {"panes": ["0"], "roles": ["PRESIDENT"]},
            "multiagent": {
                "panes": ["0.0", "0.1", "0.2", "0.3"],
                "roles": ["BOSS1", "WORKER1", "WORKER2", "WORKER3"],
            },
        }

        # State management
        self.pane_states: Dict[str, TmuxPaneState] = {}
        self.organization_state = OrganizationState(
            total_panes=5,
            active_panes=0,
            current_president=None,
            distributed_tasks={},
            governance_status={},
            last_sync=datetime.now(),
        )

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(
                    self.runtime_dir / "logs" / "ai_organization_bridge.log"
                ),
                logging.StreamHandler(),
            ],
        )
        self.logger = logging.getLogger("ai-org-bridge")

        # Initialize database
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database for state persistence"""
        self.orchestrator_db.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.orchestrator_db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pane_states (
                    pane_id TEXT PRIMARY KEY,
                    session TEXT,
                    role TEXT,
                    status TEXT,
                    last_activity TEXT,
                    current_task TEXT,
                    violations TEXT
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS governance_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    event_type TEXT,
                    pane_id TEXT,
                    details TEXT
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS distributed_tasks (
                    task_id TEXT PRIMARY KEY,
                    assigned_pane TEXT,
                    task_description TEXT,
                    status TEXT,
                    created_at TEXT,
                    completed_at TEXT
                )
            """)

    def detect_tmux_sessions(self) -> Dict[str, bool]:
        """Detect active tmux sessions"""
        try:
            result = subprocess.run(
                ["tmux", "list-sessions"], capture_output=True, text=True, check=True
            )
            active_sessions = {}

            for line in result.stdout.strip().split("\n"):
                if line:
                    session_name = line.split(":")[0]
                    active_sessions[session_name] = True

            return {
                "president": active_sessions.get("president", False),
                "multiagent": active_sessions.get("multiagent", False),
            }

        except subprocess.CalledProcessError:
            self.logger.warning("No tmux sessions found or tmux not available")
            return {"president": False, "multiagent": False}

    def get_pane_content(self, session: str, pane: str) -> str:
        """Get content from specific tmux pane"""
        try:
            result = subprocess.run(
                ["tmux", "capture-pane", "-t", f"{session}:{pane}", "-p"],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to capture pane {session}:{pane}: {e}")
            return ""

    def send_to_pane(self, session: str, pane: str, message: str):
        """Send message to specific tmux pane"""
        try:
            subprocess.run(
                ["tmux", "send-keys", "-t", f"{session}:{pane}", message, "C-m"],
                check=True,
            )
            self.logger.info(f"Sent message to {session}:{pane}")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to send to pane {session}:{pane}: {e}")

    def analyze_pane_activity(
        self, session: str, pane: str, role: str
    ) -> TmuxPaneState:
        """Analyze individual pane activity and apply governance"""
        content = self.get_pane_content(session, pane)

        # Determine pane status
        status = "idle"
        current_task = None
        violations = []

        if "How can I help" in content:
            status = "active"
        elif "Processing..." in content or "Working on" in content:
            status = "processing"
            # Extract current task if available
            lines = content.split("\n")
            for line in lines[-10:]:  # Check last 10 lines
                if "Task:" in line:
                    current_task = line.split("Task:")[-1].strip()
                    break
        elif "Error" in content or "Failed" in content:
            status = "error"

        # Apply Constitutional AI rules
        try:
            constitutional_result = self.constitutional_ai.evaluate_action(content)
            if (
                hasattr(constitutional_result, "violations")
                and constitutional_result.violations
            ):
                violations.extend(
                    [
                        v.get("description", str(v))
                        for v in constitutional_result.violations
                    ]
                )
        except Exception as e:
            self.logger.error(
                f"Constitutional AI evaluation failed for {session}:{pane}: {e}"
            )

        # Apply Rule-Based Rewards
        try:
            rbr_result = self.rule_based_rewards.evaluate_action(content)
            if hasattr(rbr_result, "total_score") and rbr_result.total_score < 0:
                violations.append(f"Negative RBR score: {rbr_result.total_score}")
        except Exception as e:
            self.logger.error(
                f"Rule-Based Rewards evaluation failed for {session}:{pane}: {e}"
            )

        return TmuxPaneState(
            session=session,
            pane_id=f"{session}:{pane}",
            role=role,
            status=status,
            last_activity=datetime.now(),
            current_task=current_task,
            violations=violations,
        )

    def enforce_governance_rules(self, pane_state: TmuxPaneState):
        """Enforce governance rules on specific pane"""
        if pane_state.violations:
            self.logger.warning(
                f"Violations detected in {pane_state.pane_id}: {pane_state.violations}"
            )

            # Send corrective message
            correction_message = (
                f"> GOVERNANCE ALERT: {', '.join(pane_state.violations)}"
            )
            session, pane = pane_state.pane_id.split(":")
            self.send_to_pane(session, pane, correction_message)

            # Log governance event
            self._log_governance_event(
                "violation_detected",
                pane_state.pane_id,
                {"violations": pane_state.violations},
            )

    def _log_governance_event(self, event_type: str, pane_id: str, details: Dict):
        """Log governance event to database"""
        with sqlite3.connect(self.orchestrator_db) as conn:
            conn.execute(
                """
                INSERT INTO governance_events (timestamp, event_type, pane_id, details)
                VALUES (?, ?, ?, ?)
            """,
                (datetime.now().isoformat(), event_type, pane_id, json.dumps(details)),
            )

    def sync_organization_state(self):
        """Synchronize overall organization state"""
        sessions_status = self.detect_tmux_sessions()
        active_panes = 0

        # Analyze each configured pane
        for session_name, session_config in self.tmux_sessions.items():
            if sessions_status.get(session_name, False):
                for i, pane in enumerate(session_config["panes"]):
                    role = session_config["roles"][i]
                    pane_state = self.analyze_pane_activity(session_name, pane, role)

                    # Store state
                    self.pane_states[pane_state.pane_id] = pane_state

                    # Apply governance
                    self.enforce_governance_rules(pane_state)

                    if pane_state.status in ["active", "processing"]:
                        active_panes += 1

                    # Persist to database
                    self._persist_pane_state(pane_state)

        # Update organization state
        self.organization_state.active_panes = active_panes
        self.organization_state.last_sync = datetime.now()

        # Update memory system with current state
        try:
            {
                "event_type": "organization_sync",
                "timestamp": datetime.now().isoformat(),
                "active_panes": active_panes,
                "total_panes": self.organization_state.total_panes,
                "pane_states": {k: asdict(v) for k, v in self.pane_states.items()},
            }
            self.memory_manager.store_memory_with_intelligence(
                content=f"AI Organization Sync: {active_panes} active panes"
            )
        except Exception as e:
            self.logger.error(f"Failed to update memory system: {e}")

    def _persist_pane_state(self, pane_state: TmuxPaneState):
        """Persist pane state to database"""
        with sqlite3.connect(self.orchestrator_db) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO pane_states
                (pane_id, session, role, status, last_activity, current_task, violations)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    pane_state.pane_id,
                    pane_state.session,
                    pane_state.role,
                    pane_state.status,
                    pane_state.last_activity.isoformat(),
                    pane_state.current_task,
                    json.dumps(pane_state.violations),
                ),
            )

    def start_orchestration(self):
        """Start continuous orchestration process"""
        self.logger.info("Starting AI Organization Tmux Bridge orchestration")
        self.running = True

        while self.running:
            try:
                self.sync_organization_state()
                time.sleep(self.sync_interval)
            except KeyboardInterrupt:
                self.logger.info("Orchestration stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Orchestration error: {e}")
                time.sleep(self.sync_interval)

    def stop_orchestration(self):
        """Stop orchestration process"""
        self.running = False
        self.logger.info("Orchestration stopped")

    def get_organization_status(self) -> Dict[str, Any]:
        """Get current organization status"""
        return {
            "organization_state": asdict(self.organization_state),
            "pane_states": {k: asdict(v) for k, v in self.pane_states.items()},
            "sessions_status": self.detect_tmux_sessions(),
            "governance_active": True,
            "bridge_version": "1.0.0",
        }

    def launch_integrated_ai_organization(self):
        """Launch tmux AI organization with integrated governance"""
        self.logger.info("Launching integrated AI organization with tmux")

        # First launch tmux system
        ai_team_script = (
            self.project_root / "scripts" / "tools" / "system" / "ai-team.sh"
        )
        if ai_team_script.exists():
            try:
                subprocess.run([str(ai_team_script), "start"], check=True)
                self.logger.info("Tmux AI organization launched")

                # Wait for initialization
                time.sleep(10)

                # Start orchestration
                self.start_orchestration()

            except subprocess.CalledProcessError as e:
                self.logger.error(f"Failed to launch tmux AI organization: {e}")
        else:
            self.logger.error(f"AI team script not found: {ai_team_script}")


def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(description="AI Organization Tmux Bridge")
    parser.add_argument(
        "action",
        choices=["start", "status", "stop", "launch"],
        help="Action to perform",
    )
    parser.add_argument("--project-root", help="Project root directory")

    args = parser.parse_args()

    bridge = AIOrganizationTmuxBridge(args.project_root)

    if args.action == "start":
        bridge.start_orchestration()
    elif args.action == "status":
        status = bridge.get_organization_status()
        print(json.dumps(status, indent=2, default=str))
    elif args.action == "stop":
        bridge.stop_orchestration()
    elif args.action == "launch":
        bridge.launch_integrated_ai_organization()


if __name__ == "__main__":
    main()
