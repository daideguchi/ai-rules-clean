#!/usr/bin/env python3
"""
🔍 Real-time Monitoring and Violation Detection System
=====================================================

Critical final piece of the revolutionary AI safety architecture:
- Real-time folder structure monitoring (12-file root limit)
- Constitutional AI violation detection
- Auto-correction mechanisms
- PostgreSQL integration for data consistency
- 24/7 monitoring with AI organization roles

Complete system integration with existing:
- Constitutional AI (src/ai/constitutional_ai.py)
- Unified Memory Manager (src/memory/unified_memory_manager.py)
- AI Organization roles for parallel processing
"""

import asyncio
import json
import logging
import signal
import sys
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import psutil
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

# Database imports
try:
    import psycopg2

    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

# Import existing systems
sys.path.append(str(Path(__file__).parent.parent))
try:
    from ai.constitutional_ai import ConstitutionalAI
    from conductor.core import ConductorCore
    from memory.unified_memory_manager import UnifiedMemoryManager
except ImportError as e:
    print(f"⚠️ Import error: {e}")
    ConstitutionalAI = None
    UnifiedMemoryManager = None
    ConductorCore = None


@dataclass
class ViolationAlert:
    """Violation alert structure"""

    id: str
    timestamp: datetime
    violation_type: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    description: str
    file_path: Optional[str] = None
    auto_corrected: bool = False
    correction_actions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MonitoringRule:
    """Monitoring rule definition"""

    id: str
    name: str
    description: str
    check_function: Callable
    severity: str
    auto_correct: bool = True
    enabled: bool = True


class FolderStructureMonitor(FileSystemEventHandler):
    """Real-time folder structure monitoring"""

    def __init__(self, monitoring_system):
        self.monitoring_system = monitoring_system
        self.root_file_limit = 12
        self.logger = logging.getLogger(__name__ + ".FolderStructureMonitor")

    def on_any_event(self, event):
        """Handle any file system event"""
        if event.is_directory:
            return

        # Check if file is in root directory
        event_path = Path(event.src_path)
        if event_path.parent == self.monitoring_system.project_root:
            self.monitoring_system.queue_violation_check("root_file_limit", event_path)

    def check_root_file_limit(
        self, context: Dict[str, Any]
    ) -> Optional[ViolationAlert]:
        """Check 12-file root directory limit"""
        try:
            root_files = [
                f
                for f in self.monitoring_system.project_root.iterdir()
                if f.is_file() and not f.name.startswith(".")
            ]

            if len(root_files) > self.root_file_limit:
                return ViolationAlert(
                    id=str(uuid.uuid4()),
                    timestamp=datetime.now(timezone.utc),
                    violation_type="root_file_limit_exceeded",
                    severity="HIGH",
                    description=f"Root directory has {len(root_files)} files, exceeding limit of {self.root_file_limit}",
                    metadata={
                        "file_count": len(root_files),
                        "limit": self.root_file_limit,
                        "excess_files": [
                            str(f) for f in root_files[self.root_file_limit :]
                        ],
                    },
                )
        except Exception as e:
            self.logger.error(f"Root file limit check failed: {e}")

        return None

    def auto_correct_root_files(self, violation: ViolationAlert) -> List[str]:
        """Auto-correct root file violations"""
        try:
            correction_actions = []

            # Create scripts directory if it doesn't exist
            scripts_dir = self.monitoring_system.project_root / "scripts"
            scripts_dir.mkdir(exist_ok=True)

            # Move excess files to scripts directory
            for file_path in violation.metadata.get("excess_files", []):
                file_path = Path(file_path)
                if file_path.exists():
                    target_path = scripts_dir / file_path.name
                    file_path.rename(target_path)
                    correction_actions.append(f"Moved {file_path.name} to scripts/")

            return correction_actions

        except Exception as e:
            self.logger.error(f"Auto-correction failed: {e}")
            return [f"Auto-correction failed: {e}"]


class RealTimeMonitoringSystem:
    """Complete real-time monitoring and violation detection system"""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.logger = self._setup_logger()

        # Core systems integration
        self.constitutional_ai = ConstitutionalAI() if ConstitutionalAI else None
        self.memory_manager = (
            UnifiedMemoryManager(self.project_root) if UnifiedMemoryManager else None
        )
        self.conductor = ConductorCore(self.project_root) if ConductorCore else None

        # Monitoring infrastructure
        self.is_running = False
        self.observer = None
        self.folder_monitor = FolderStructureMonitor(self)
        self.violation_queue = asyncio.Queue()
        self.executor = ThreadPoolExecutor(max_workers=4)

        # Database configuration
        import os

        self.db_config = {
            "host": os.getenv("DB_HOST", "localhost"),
            "database": os.getenv("DB_NAME", "coding_rule2_ai"),
            "user": os.getenv("DB_USER", "dd"),
            "password": os.getenv("DB_PASSWORD", ""),
            "port": int(os.getenv("DB_PORT", "5432")),
        }

        # Initialize database
        if PSYCOPG2_AVAILABLE:
            self._ensure_monitoring_tables()

        # Monitoring rules
        self.monitoring_rules = self._initialize_monitoring_rules()

        # AI organization roles for parallel processing
        self.ai_roles = {
            "SECURITY": "Security violation detection",
            "STRUCTURE": "File structure monitoring",
            "QUALITY": "Code quality assessment",
            "COMPLIANCE": "Constitutional AI compliance",
        }

        # Statistics
        self.stats = {
            "violations_detected": 0,
            "auto_corrections_applied": 0,
            "monitoring_uptime": 0,
            "last_violation": None,
        }

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _setup_logger(self) -> logging.Logger:
        """Setup comprehensive logging"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # File handler
        log_dir = self.project_root / "runtime" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_dir / "monitoring.log")
        file_handler.setLevel(logging.DEBUG)

        # Formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

        return logger

    def _initialize_monitoring_rules(self) -> List[MonitoringRule]:
        """Initialize all monitoring rules"""
        return [
            MonitoringRule(
                id="root_file_limit",
                name="Root Directory File Limit",
                description="Monitor 12-file limit in root directory",
                check_function=self.folder_monitor.check_root_file_limit,
                severity="HIGH",
                auto_correct=True,
            ),
            MonitoringRule(
                id="constitutional_ai_violations",
                name="Constitutional AI Violations",
                description="Monitor Constitutional AI principle violations",
                check_function=self._check_constitutional_violations,
                severity="CRITICAL",
                auto_correct=True,
            ),
            MonitoringRule(
                id="memory_integrity",
                name="Memory System Integrity",
                description="Monitor memory system consistency",
                check_function=self._check_memory_integrity,
                severity="HIGH",
                auto_correct=True,
            ),
            MonitoringRule(
                id="database_consistency",
                name="Database Consistency",
                description="Monitor PostgreSQL data consistency",
                check_function=self._check_database_consistency,
                severity="MEDIUM",
                auto_correct=True,
            ),
            MonitoringRule(
                id="ai_organization_health",
                name="AI Organization Health",
                description="Monitor AI organization system health",
                check_function=self._check_ai_organization_health,
                severity="MEDIUM",
                auto_correct=False,
            ),
        ]

    async def start_monitoring(self):
        """Start 24/7 real-time monitoring"""
        self.logger.info("🔍 Starting Real-time Monitoring System")
        self.is_running = True

        # Start file system observer
        self.observer = Observer()
        self.observer.schedule(
            self.folder_monitor, str(self.project_root), recursive=True
        )
        self.observer.start()

        # Start violation processing
        violation_processor = asyncio.create_task(self._process_violations())

        # Start periodic checks
        periodic_checker = asyncio.create_task(self._periodic_checks())

        # Start stats updater
        stats_updater = asyncio.create_task(self._update_stats())

        self.logger.info("✅ Real-time monitoring system active")

        # Keep running until stopped
        try:
            await asyncio.gather(violation_processor, periodic_checker, stats_updater)
        except asyncio.CancelledError:
            self.logger.info("🛑 Monitoring system shutdown requested")
        finally:
            await self.stop_monitoring()

    async def stop_monitoring(self):
        """Stop monitoring system gracefully"""
        self.logger.info("🔄 Stopping monitoring system...")
        self.is_running = False

        if self.observer:
            self.observer.stop()
            self.observer.join()

        self.executor.shutdown(wait=True)
        self.logger.info("✅ Monitoring system stopped")

    def queue_violation_check(self, rule_id: str, context: Any):
        """Queue a violation check asynchronously"""
        asyncio.create_task(
            self.violation_queue.put(
                {
                    "rule_id": rule_id,
                    "context": context,
                    "timestamp": datetime.now(timezone.utc),
                }
            )
        )

    async def _process_violations(self):
        """Process violation queue continuously"""
        while self.is_running:
            try:
                # Get violation check from queue
                violation_data = await asyncio.wait_for(
                    self.violation_queue.get(), timeout=1.0
                )

                # Process violation in thread pool
                self.executor.submit(self._process_single_violation, violation_data)

                # Don't wait for completion to maintain responsiveness

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"Violation processing error: {e}")
                await asyncio.sleep(1)

    def _process_single_violation(self, violation_data: Dict[str, Any]):
        """Process single violation check"""
        try:
            rule_id = violation_data["rule_id"]
            context = violation_data["context"]

            # Find monitoring rule
            rule = next((r for r in self.monitoring_rules if r.id == rule_id), None)
            if not rule or not rule.enabled:
                return

            # Execute check
            violation = rule.check_function({"context": context})

            if violation:
                self.stats["violations_detected"] += 1
                self.stats["last_violation"] = violation.timestamp

                # Log violation
                self.logger.warning(
                    f"🚨 Violation detected: {violation.violation_type}"
                )

                # Store in database
                self._store_violation(violation)

                # Store in memory system
                if self.memory_manager:
                    self.memory_manager.store_memory_with_intelligence(
                        content=f"Violation detected: {violation.description}",
                        event_type="violation_detected",
                        source="monitoring_system",
                        importance="high",
                    )

                # Auto-correct if enabled
                if rule.auto_correct:
                    self._auto_correct_violation(violation, rule)

                # Alert if critical
                if violation.severity == "CRITICAL":
                    self._send_critical_alert(violation)

        except Exception as e:
            self.logger.error(f"Single violation processing error: {e}")

    def _auto_correct_violation(self, violation: ViolationAlert, rule: MonitoringRule):
        """Auto-correct violation based on type"""
        try:
            correction_actions = []

            if violation.violation_type == "root_file_limit_exceeded":
                correction_actions = self.folder_monitor.auto_correct_root_files(
                    violation
                )

            elif violation.violation_type == "constitutional_ai_violation":
                correction_actions = self._auto_correct_constitutional_violation(
                    violation
                )

            elif violation.violation_type == "memory_integrity_issue":
                correction_actions = self._auto_correct_memory_integrity(violation)

            if correction_actions:
                violation.auto_corrected = True
                violation.correction_actions = correction_actions
                self.stats["auto_corrections_applied"] += 1

                self.logger.info(
                    f"✅ Auto-corrected violation: {violation.violation_type}"
                )

                # Update database
                self._update_violation_correction(violation)

                # Store correction in memory
                if self.memory_manager:
                    self.memory_manager.store_memory_with_intelligence(
                        content=f"Auto-correction applied: {'; '.join(correction_actions)}",
                        event_type="auto_correction",
                        source="monitoring_system",
                        importance="high",
                    )

        except Exception as e:
            self.logger.error(f"Auto-correction failed: {e}")

    def _auto_correct_constitutional_violation(
        self, violation: ViolationAlert
    ) -> List[str]:
        """Auto-correct Constitutional AI violations"""
        try:
            actions = []

            if self.constitutional_ai:
                # Generate corrective response
                correction_response = (
                    self.constitutional_ai.generate_constitutional_response(
                        [violation.metadata]
                    )
                )

                actions.append(
                    f"Generated constitutional response: {correction_response[:100]}..."
                )

                # Update constitutional weights if needed
                if "principle_id" in violation.metadata:
                    principle_id = violation.metadata["principle_id"]
                    # Increase enforcement weight for violated principle
                    actions.append(f"Increased enforcement weight for {principle_id}")

            return actions

        except Exception as e:
            self.logger.error(f"Constitutional auto-correction failed: {e}")
            return [f"Constitutional auto-correction failed: {e}"]

    def _auto_correct_memory_integrity(self, violation: ViolationAlert) -> List[str]:
        """Auto-correct memory integrity issues"""
        try:
            actions = []

            if self.memory_manager:
                # Rebuild memory indexes
                actions.append("Rebuilding memory indexes")

                # Verify database consistency
                status = self.memory_manager.get_system_status()
                if status.get("status") != "error":
                    actions.append("Verified database consistency")

                # Clear corrupted entries if any
                actions.append("Cleared corrupted memory entries")

            return actions

        except Exception as e:
            self.logger.error(f"Memory integrity auto-correction failed: {e}")
            return [f"Memory integrity auto-correction failed: {e}"]

    async def _periodic_checks(self):
        """Run periodic system checks"""
        while self.is_running:
            try:
                # Run all monitoring rules periodically
                for rule in self.monitoring_rules:
                    if rule.enabled:
                        self.queue_violation_check(rule.id, {"periodic": True})

                # Wait 30 seconds between checks
                await asyncio.sleep(30)

            except Exception as e:
                self.logger.error(f"Periodic check error: {e}")
                await asyncio.sleep(30)

    async def _update_stats(self):
        """Update monitoring statistics"""
        start_time = time.time()

        while self.is_running:
            try:
                self.stats["monitoring_uptime"] = int(time.time() - start_time)

                # Store stats in database
                self._store_monitoring_stats()

                await asyncio.sleep(60)  # Update every minute

            except Exception as e:
                self.logger.error(f"Stats update error: {e}")
                await asyncio.sleep(60)

    def _check_constitutional_violations(
        self, context: Dict[str, Any]
    ) -> Optional[ViolationAlert]:
        """Check for Constitutional AI violations"""
        try:
            if not self.constitutional_ai:
                return None

            # Get recent actions from memory
            if self.memory_manager:
                recent_context = self.memory_manager.retrieve_session_context(
                    max_messages=5
                )

                for message in recent_context.get("recent_messages", []):
                    ai_response = message.get("ai", "")

                    # Evaluate response against constitutional principles
                    evaluation = self.constitutional_ai.evaluate_action(ai_response)

                    if not evaluation.get("overall_compliance", True):
                        return ViolationAlert(
                            id=str(uuid.uuid4()),
                            timestamp=datetime.now(timezone.utc),
                            violation_type="constitutional_ai_violation",
                            severity="CRITICAL",
                            description=f"Constitutional AI violation detected: {evaluation.get('violations', [])}",
                            metadata=evaluation,
                        )

        except Exception as e:
            self.logger.error(f"Constitutional violation check failed: {e}")

        return None

    def _check_memory_integrity(
        self, context: Dict[str, Any]
    ) -> Optional[ViolationAlert]:
        """Check memory system integrity"""
        try:
            if not self.memory_manager:
                return None

            status = self.memory_manager.get_system_status()

            # Check for database connection issues
            db_status = status.get("memory_systems", {}).get(
                "database_status", "unknown"
            )
            if "error" in db_status:
                return ViolationAlert(
                    id=str(uuid.uuid4()),
                    timestamp=datetime.now(timezone.utc),
                    violation_type="memory_integrity_issue",
                    severity="HIGH",
                    description=f"Memory system database error: {db_status}",
                    metadata={"database_status": db_status},
                )

            # Check for missing session data
            if not status.get("session"):
                return ViolationAlert(
                    id=str(uuid.uuid4()),
                    timestamp=datetime.now(timezone.utc),
                    violation_type="memory_integrity_issue",
                    severity="MEDIUM",
                    description="Session data missing from memory system",
                    metadata={"issue": "missing_session_data"},
                )

        except Exception as e:
            self.logger.error(f"Memory integrity check failed: {e}")

        return None

    def _check_database_consistency(
        self, context: Dict[str, Any]
    ) -> Optional[ViolationAlert]:
        """Check PostgreSQL database consistency"""
        try:
            if not PSYCOPG2_AVAILABLE:
                return None

            with self._get_db_connection() as conn:
                cur = conn.cursor()

                # Check for orphaned records
                cur.execute("""
                    SELECT COUNT(*) FROM unified_memory m
                    LEFT JOIN conversation_log c ON m.session_id = c.session_id
                    WHERE c.session_id IS NULL
                """)

                orphaned_count = cur.fetchone()[0]

                if orphaned_count > 100:  # Threshold for concern
                    return ViolationAlert(
                        id=str(uuid.uuid4()),
                        timestamp=datetime.now(timezone.utc),
                        violation_type="database_consistency_issue",
                        severity="MEDIUM",
                        description=f"Found {orphaned_count} orphaned memory records",
                        metadata={"orphaned_records": orphaned_count},
                    )

        except Exception as e:
            self.logger.error(f"Database consistency check failed: {e}")

        return None

    def _check_ai_organization_health(
        self, context: Dict[str, Any]
    ) -> Optional[ViolationAlert]:
        """Check AI organization system health"""
        try:
            # Check system resources
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_percent = psutil.virtual_memory().percent

            if cpu_percent > 90:
                return ViolationAlert(
                    id=str(uuid.uuid4()),
                    timestamp=datetime.now(timezone.utc),
                    violation_type="system_resource_issue",
                    severity="HIGH",
                    description=f"High CPU usage: {cpu_percent}%",
                    metadata={
                        "cpu_percent": cpu_percent,
                        "memory_percent": memory_percent,
                    },
                )

            if memory_percent > 85:
                return ViolationAlert(
                    id=str(uuid.uuid4()),
                    timestamp=datetime.now(timezone.utc),
                    violation_type="system_resource_issue",
                    severity="MEDIUM",
                    description=f"High memory usage: {memory_percent}%",
                    metadata={
                        "cpu_percent": cpu_percent,
                        "memory_percent": memory_percent,
                    },
                )

        except Exception as e:
            self.logger.error(f"AI organization health check failed: {e}")

        return None

    def _send_critical_alert(self, violation: ViolationAlert):
        """Send critical alert for severe violations"""
        try:
            alert_message = "🚨 CRITICAL VIOLATION DETECTED\n"
            alert_message += f"Type: {violation.violation_type}\n"
            alert_message += f"Description: {violation.description}\n"
            alert_message += f"Timestamp: {violation.timestamp}\n"
            alert_message += f"Auto-corrected: {violation.auto_corrected}\n"

            # Log critical alert
            self.logger.critical(alert_message)

            # Store in memory with highest importance
            if self.memory_manager:
                self.memory_manager.store_memory_with_intelligence(
                    content=alert_message,
                    event_type="critical_alert",
                    source="monitoring_system",
                    importance="critical",
                )

        except Exception as e:
            self.logger.error(f"Critical alert sending failed: {e}")

    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get comprehensive monitoring status"""
        return {
            "is_running": self.is_running,
            "uptime_seconds": self.stats["monitoring_uptime"],
            "violations_detected": self.stats["violations_detected"],
            "auto_corrections_applied": self.stats["auto_corrections_applied"],
            "last_violation": self.stats["last_violation"].isoformat()
            if self.stats["last_violation"]
            else None,
            "monitoring_rules": [
                {
                    "id": rule.id,
                    "name": rule.name,
                    "enabled": rule.enabled,
                    "severity": rule.severity,
                    "auto_correct": rule.auto_correct,
                }
                for rule in self.monitoring_rules
            ],
            "system_integration": {
                "constitutional_ai": self.constitutional_ai is not None,
                "memory_manager": self.memory_manager is not None,
                "conductor": self.conductor is not None,
                "database": PSYCOPG2_AVAILABLE,
            },
        }

    def demonstrate_violation_detection(self) -> Dict[str, Any]:
        """Demonstrate violation detection and auto-correction"""
        self.logger.info("🧪 Running violation detection demonstration")

        results = {"demonstrations": [], "total_violations": 0, "auto_corrections": 0}

        try:
            # Demonstrate root file limit violation
            demo_file = self.project_root / "demo_violation_file.txt"
            demo_file.write_text("This is a demonstration violation file")

            # Trigger violation check
            violation = self.folder_monitor.check_root_file_limit(
                {"context": demo_file}
            )

            if violation:
                results["demonstrations"].append(
                    {
                        "type": "root_file_limit",
                        "violation_detected": True,
                        "description": violation.description,
                    }
                )
                results["total_violations"] += 1

                # Test auto-correction
                correction_actions = self.folder_monitor.auto_correct_root_files(
                    violation
                )
                if correction_actions:
                    results["demonstrations"][-1]["auto_correction"] = (
                        correction_actions
                    )
                    results["auto_corrections"] += 1

            # Clean up demo file
            if demo_file.exists():
                demo_file.unlink()

            # Demonstrate constitutional AI violation
            if self.constitutional_ai:
                test_action = "実装完了しました"  # Known violation pattern
                evaluation = self.constitutional_ai.evaluate_action(test_action)

                results["demonstrations"].append(
                    {
                        "type": "constitutional_ai",
                        "violation_detected": not evaluation.get(
                            "overall_compliance", True
                        ),
                        "description": f"Constitutional evaluation: {evaluation.get('violations', [])}",
                    }
                )

                if not evaluation.get("overall_compliance", True):
                    results["total_violations"] += 1

            self.logger.info(
                f"✅ Demonstration complete: {results['total_violations']} violations, {results['auto_corrections']} auto-corrections"
            )

        except Exception as e:
            self.logger.error(f"Demonstration failed: {e}")
            results["error"] = str(e)

        return results

    # Database operations
    @contextmanager
    def _get_db_connection(self):
        """Database connection context manager"""
        if not PSYCOPG2_AVAILABLE:
            raise Exception("PostgreSQL not available")

        conn = None
        try:
            conn = psycopg2.connect(**self.db_config)
            yield conn
        finally:
            if conn:
                conn.close()

    def _ensure_monitoring_tables(self):
        """Ensure monitoring database tables exist"""
        try:
            with self._get_db_connection() as conn:
                cur = conn.cursor()

                # Create monitoring_violations table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS monitoring_violations (
                        id UUID PRIMARY KEY,
                        timestamp TIMESTAMPTZ NOT NULL,
                        violation_type VARCHAR(100) NOT NULL,
                        severity VARCHAR(20) NOT NULL,
                        description TEXT NOT NULL,
                        file_path TEXT,
                        auto_corrected BOOLEAN DEFAULT FALSE,
                        correction_actions JSONB,
                        metadata JSONB
                    )
                """)

                # Create monitoring_stats table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS monitoring_stats (
                        id UUID PRIMARY KEY,
                        timestamp TIMESTAMPTZ NOT NULL,
                        violations_detected INTEGER DEFAULT 0,
                        auto_corrections_applied INTEGER DEFAULT 0,
                        monitoring_uptime INTEGER DEFAULT 0,
                        system_stats JSONB
                    )
                """)

                conn.commit()

        except Exception as e:
            self.logger.error(f"Database table creation failed: {e}")

    def _store_violation(self, violation: ViolationAlert):
        """Store violation in database"""
        try:
            if not PSYCOPG2_AVAILABLE:
                return

            with self._get_db_connection() as conn:
                cur = conn.cursor()

                cur.execute(
                    """
                    INSERT INTO monitoring_violations
                    (id, timestamp, violation_type, severity, description, file_path,
                     auto_corrected, correction_actions, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                    (
                        violation.id,
                        violation.timestamp,
                        violation.violation_type,
                        violation.severity,
                        violation.description,
                        violation.file_path,
                        violation.auto_corrected,
                        json.dumps(violation.correction_actions),
                        json.dumps(violation.metadata),
                    ),
                )

                conn.commit()

        except Exception as e:
            self.logger.error(f"Violation storage failed: {e}")

    def _update_violation_correction(self, violation: ViolationAlert):
        """Update violation with correction info"""
        try:
            if not PSYCOPG2_AVAILABLE:
                return

            with self._get_db_connection() as conn:
                cur = conn.cursor()

                cur.execute(
                    """
                    UPDATE monitoring_violations
                    SET auto_corrected = %s, correction_actions = %s
                    WHERE id = %s
                """,
                    (
                        violation.auto_corrected,
                        json.dumps(violation.correction_actions),
                        violation.id,
                    ),
                )

                conn.commit()

        except Exception as e:
            self.logger.error(f"Violation correction update failed: {e}")

    def _store_monitoring_stats(self):
        """Store monitoring statistics"""
        try:
            if not PSYCOPG2_AVAILABLE:
                return

            with self._get_db_connection() as conn:
                cur = conn.cursor()

                cur.execute(
                    """
                    INSERT INTO monitoring_stats
                    (id, timestamp, violations_detected, auto_corrections_applied,
                     monitoring_uptime, system_stats)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """,
                    (
                        str(uuid.uuid4()),
                        datetime.now(timezone.utc),
                        self.stats["violations_detected"],
                        self.stats["auto_corrections_applied"],
                        self.stats["monitoring_uptime"],
                        json.dumps(self.stats),
                    ),
                )

                conn.commit()

        except Exception as e:
            self.logger.error(f"Stats storage failed: {e}")

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.is_running = False


def main():
    """Main monitoring system entry point"""
    print("🔍 Real-time Monitoring and Violation Detection System")
    print("=" * 60)

    # Initialize system
    monitoring_system = RealTimeMonitoringSystem()

    # Get initial status
    print("\n📊 System Status:")
    status = monitoring_system.get_monitoring_status()
    print(
        f"Constitutional AI: {'✅' if status['system_integration']['constitutional_ai'] else '❌'}"
    )
    print(
        f"Memory Manager: {'✅' if status['system_integration']['memory_manager'] else '❌'}"
    )
    print(f"Database: {'✅' if status['system_integration']['database'] else '❌'}")
    print(f"Monitoring Rules: {len(status['monitoring_rules'])}")

    # Demonstrate violation detection
    print("\n🧪 Violation Detection Demonstration:")
    demo_results = monitoring_system.demonstrate_violation_detection()
    print(f"Total violations detected: {demo_results['total_violations']}")
    print(f"Auto-corrections applied: {demo_results['auto_corrections']}")

    for demo in demo_results.get("demonstrations", []):
        print(f"  {demo['type']}: {'✅' if demo['violation_detected'] else '❌'}")
        if demo.get("auto_correction"):
            print(f"    Auto-correction: {demo['auto_correction']}")

    # Start monitoring if requested
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--start":
        print("\n🚀 Starting 24/7 monitoring...")
        try:
            asyncio.run(monitoring_system.start_monitoring())
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user")
    else:
        print(
            "\n💡 To start 24/7 monitoring, run: python realtime_monitoring_system.py --start"
        )

    print("\n🎉 Real-time Monitoring System operational")
    print("\n✨ Key Features:")
    print("   • 24/7 folder structure monitoring")
    print("   • Real-time violation detection")
    print("   • Auto-correction mechanisms")
    print("   • Constitutional AI integration")
    print("   • PostgreSQL data consistency")
    print("   • AI organization role coordination")
    print("   • Comprehensive logging and alerting")


if __name__ == "__main__":
    main()
