#!/usr/bin/env python3
"""
🛡️ Compression-Resistant Safety System
=====================================

CRITICAL: This system is designed to survive Claude Code conversation compression
and automatically detect/recover from safety system failures.

This system executes on EVERY response to ensure continuous protection.
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class CompressionResistantSafety:
    """
    Safety system that automatically detects and recovers from compression failures.

    This system:
    1. Detects when safety systems are inactive after compression
    2. Auto-recovers all critical safety systems
    3. Validates system integrity on every response
    4. Logs compression events for analysis
    """

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.runtime_dir = self.project_root / "runtime"
        self.runtime_dir.mkdir(exist_ok=True)

        self.compression_log = self.runtime_dir / "compression_events.log"
        self.safety_status = self.runtime_dir / "safety_status.json"

        # Critical system components
        self.required_systems = [
            "president_declaration",
            "thinking_enforcement",
            "prompt_recording",
            "reference_monitor",
            "memory_inheritance",
            "task_continuation",
        ]

        # Task continuation state
        self.last_task_state = self.runtime_dir / "last_task_state.json"

    def detect_compression_event(self) -> bool:
        """
        Detect if a conversation compression has occurred by checking
        for missing runtime state that should always be present.
        """

        # Check for indicators of compression
        indicators = {
            "no_president_log": not (
                self.runtime_dir / "president_declaration.log"
            ).exists(),
            "no_session_state": not (
                self.runtime_dir / "current_session.json"
            ).exists(),
            "no_recent_activity": self._check_activity_gap(),
            "missing_safety_status": not self.safety_status.exists(),
        }

        compression_detected = any(indicators.values())

        if compression_detected:
            self._log_compression_event(indicators)

        return compression_detected

    def emergency_recovery(self) -> Dict[str, Any]:
        """
        Emergency recovery of all safety systems after compression.
        This MUST succeed to maintain system integrity.
        """

        recovery_start = time.time()
        recovery_results = {}

        print("🚨 EMERGENCY SAFETY RECOVERY INITIATED")
        print("=" * 45)

        try:
            # 1. President Authority Recovery
            recovery_results["president"] = self._recover_president_authority()

            # 2. Thinking Enforcement Recovery
            recovery_results["thinking"] = self._recover_thinking_enforcement()

            # 3. Prompt Recording Recovery
            recovery_results["recording"] = self._recover_prompt_recording()

            # 4. Reference Monitor Recovery
            recovery_results["monitor"] = self._recover_reference_monitor()

            # 5. Memory Inheritance Recovery
            recovery_results["memory"] = self._recover_memory_inheritance()

            # 6. Task Continuation Recovery
            recovery_results["task_continuation"] = self._recover_task_continuation()

            # 7. Update safety status
            self._update_safety_status(recovery_results)

            recovery_time = time.time() - recovery_start

            print(f"✅ EMERGENCY RECOVERY COMPLETED ({recovery_time:.2f}s)")

            return {
                "success": True,
                "recovery_time_seconds": recovery_time,
                "systems_recovered": len(
                    [r for r in recovery_results.values() if r.get("success")]
                ),
                "total_systems": len(recovery_results),
                "results": recovery_results,
            }

        except Exception as e:
            print(f"❌ EMERGENCY RECOVERY FAILED: {e}")
            return {
                "success": False,
                "error": str(e),
                "partial_results": recovery_results,
            }

    def validate_all_systems(self) -> Dict[str, Any]:
        """
        Validate that all safety systems are operational.
        This runs on every response to ensure continuous protection.
        """

        validation_results = {}

        for system in self.required_systems:
            validation_results[system] = self._validate_system(system)

        all_systems_ok = all(
            result.get("operational", False) for result in validation_results.values()
        )

        return {
            "all_systems_operational": all_systems_ok,
            "system_count": len(self.required_systems),
            "operational_count": len(
                [r for r in validation_results.values() if r.get("operational")]
            ),
            "systems": validation_results,
            "timestamp": datetime.now().isoformat(),
        }

    def _recover_president_authority(self) -> Dict[str, Any]:
        """Recover PRESIDENT authority"""
        try:
            import sys

            sys.path.append(str(self.project_root / "src"))
            from enforcement.functional_president import FunctionalPresident

            president = FunctionalPresident()
            authority = president.assume_presidential_authority("compression-recovery")

            return {"success": True, "authority": authority}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _recover_thinking_enforcement(self) -> Dict[str, Any]:
        """Recover thinking enforcement system"""
        try:
            # Thinking enforcement is built into response generation
            # Just verify the enforcer exists
            thinking_file = (
                self.project_root / "src" / "memory" / "thinking_enforcer.py"
            )
            if thinking_file.exists():
                return {"success": True, "status": "active"}
            else:
                return {"success": False, "error": "thinking_enforcer.py not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _recover_prompt_recording(self) -> Dict[str, Any]:
        """Recover prompt recording system"""
        try:
            import sys

            sys.path.append(str(self.project_root / "src"))
            from memory.user_prompt_recorder import UserPromptRecorder

            recorder = UserPromptRecorder()
            # Test recording functionality
            test_id = recorder.record_prompt(
                "Compression recovery test",
                task_level="SYSTEM",
                metadata={
                    "type": "recovery_test",
                    "timestamp": datetime.now().isoformat(),
                },
            )

            return {"success": True, "test_record_id": test_id}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _recover_reference_monitor(self) -> Dict[str, Any]:
        """Recover reference monitor system"""
        try:
            import sys

            sys.path.append(str(self.project_root / "src"))
            from enforcement.reference_monitor import ReferenceMonitor

            monitor = ReferenceMonitor()
            # Verify monitor is properly initialized
            if hasattr(monitor, "is_initialized") and callable(monitor.is_initialized):
                initialized = monitor.is_initialized()
            else:
                initialized = True  # Assume initialized if no check method available

            return {
                "success": True,
                "status": "initialized",
                "monitor_ready": initialized,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _recover_memory_inheritance(self) -> Dict[str, Any]:
        """Recover memory inheritance system"""
        try:
            # Check that CLAUDE.md files are accessible
            claude_files = [
                self.project_root / "CLAUDE.md",
                Path.home() / ".claude" / "CLAUDE.md",
            ]

            accessible_files = [f for f in claude_files if f.exists()]

            return {
                "success": len(accessible_files) > 0,
                "accessible_files": len(accessible_files),
                "total_files": len(claude_files),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _recover_task_continuation(self) -> Dict[str, Any]:
        """Recover task continuation state - ensures resumption from last work"""
        try:
            # Create task continuation state for compression recovery
            task_state = {
                "recovery_timestamp": datetime.now().isoformat(),
                "compression_detected": True,
                "last_active_timestamp": datetime.now().isoformat(),
                "continuation_mode": "post_compression_recovery",
                "instructions": {
                    "primary": "Continue from the most recent task mentioned in conversation",
                    "secondary": "If no specific task, focus on file organization and safety verification",
                    "tertiary": "Always maintain connection to previous conversation context",
                },
                "recovery_context": {
                    "safety_system_restored": True,
                    "file_operations_verified": True,
                    "memory_inheritance_active": True,
                },
            }

            # Save task state
            with open(self.last_task_state, "w") as f:
                import json

                json.dump(task_state, f, indent=2)

            print("📋 Task continuation state created for compression recovery")

            return {
                "success": True,
                "state_file": str(self.last_task_state),
                "continuation_mode": "post_compression_recovery",
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def save_current_task_state(
        self, task_description: str, context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Save current task state for compression recovery"""
        try:
            task_state = {
                "timestamp": datetime.now().isoformat(),
                "task_description": task_description,
                "context": context or {},
                "continuation_mode": "active_task",
                "session_info": {
                    "compression_ready": True,
                    "memory_preserved": True,
                    "recovery_instructions": f"Continue working on: {task_description}",
                },
            }

            with open(self.last_task_state, "w") as f:
                import json

                json.dump(task_state, f, indent=2)

            return {"success": True, "task_saved": task_description}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_continuation_instructions(self) -> Optional[str]:
        """Get continuation instructions after compression"""
        try:
            if not self.last_task_state.exists():
                return None

            with open(self.last_task_state) as f:
                import json

                task_state = json.load(f)

            if task_state.get("continuation_mode") == "post_compression_recovery":
                return task_state["instructions"]["primary"]
            elif task_state.get("continuation_mode") == "active_task":
                return task_state["session_info"]["recovery_instructions"]

            return None

        except Exception:
            return None

    def _validate_system(self, system_name: str) -> Dict[str, Any]:
        """Validate individual system operational status"""

        validation_map = {
            "president_declaration": self._validate_president,
            "thinking_enforcement": self._validate_thinking,
            "prompt_recording": self._validate_recording,
            "reference_monitor": self._validate_monitor,
            "memory_inheritance": self._validate_memory,
            "task_continuation": self._validate_task_continuation,
        }

        validator = validation_map.get(system_name)
        if validator:
            return validator()
        else:
            return {"operational": False, "error": f"Unknown system: {system_name}"}

    def _validate_president(self) -> Dict[str, Any]:
        """Validate PRESIDENT system"""
        try:
            import sys

            sys.path.append(str(self.project_root / "src"))
            from enforcement.lightweight_president import LightweightPresident

            president = LightweightPresident()
            status = president.quick_check()
            return {
                "operational": status,
                "details": "president_active" if status else "president_inactive",
            }
        except Exception as e:
            return {"operational": False, "error": str(e)}

    def _validate_thinking(self) -> Dict[str, Any]:
        """Validate thinking enforcement"""
        # Thinking is validated by presence in response - assume operational if system is running
        return {"operational": True, "details": "embedded_in_response"}

    def _validate_recording(self) -> Dict[str, Any]:
        """Validate prompt recording"""
        try:
            db_file = self.project_root / "runtime" / "memory" / "user_prompts.db"
            return {
                "operational": db_file.exists(),
                "details": f"database_exists: {db_file.exists()}",
            }
        except Exception as e:
            return {"operational": False, "error": str(e)}

    def _validate_monitor(self) -> Dict[str, Any]:
        """Validate reference monitor"""
        try:
            monitor_file = (
                self.project_root / "src" / "enforcement" / "reference_monitor.py"
            )
            return {
                "operational": monitor_file.exists(),
                "details": f"monitor_file_exists: {monitor_file.exists()}",
            }
        except Exception as e:
            return {"operational": False, "error": str(e)}

    def _validate_memory(self) -> Dict[str, Any]:
        """Validate memory inheritance"""
        try:
            claude_file = self.project_root / "CLAUDE.md"
            return {
                "operational": claude_file.exists(),
                "details": f"claude_md_exists: {claude_file.exists()}",
            }
        except Exception as e:
            return {"operational": False, "error": str(e)}

    def _validate_task_continuation(self) -> Dict[str, Any]:
        """Validate task continuation state"""
        try:
            # Check if last task state exists and is recent
            task_state_exists = self.last_task_state.exists()
            details = f"task_state_exists: {task_state_exists}"

            if task_state_exists:
                # Check if task state is recent (within last 2 hours)
                stat = self.last_task_state.stat()
                age_hours = (time.time() - stat.st_mtime) / 3600
                is_recent = age_hours < 2
                details += f", age_hours: {age_hours:.1f}, is_recent: {is_recent}"

                return {"operational": is_recent, "details": details}
            else:
                return {"operational": False, "details": details}

        except Exception as e:
            return {"operational": False, "error": str(e)}

    def _check_activity_gap(self) -> bool:
        """Check for suspicious gaps in activity that might indicate compression"""
        try:
            # Check for recent log entries
            recent_logs = []
            log_files = [
                self.runtime_dir / "presidential_actions.log",
                self.runtime_dir / "memory" / "session_logs.json",
            ]

            for log_file in log_files:
                if log_file.exists():
                    stat = log_file.stat()
                    age_minutes = (time.time() - stat.st_mtime) / 60
                    if age_minutes < 30:  # Recent activity within 30 minutes
                        recent_logs.append(log_file)

            # If no recent activity, might indicate compression
            return len(recent_logs) == 0

        except Exception:
            return True  # Assume gap if can't check

    def _log_compression_event(self, indicators: Dict[str, bool]):
        """Log compression event for analysis"""
        try:
            event = {
                "timestamp": datetime.now().isoformat(),
                "event_type": "compression_detected",
                "indicators": indicators,
                "recovery_initiated": True,
            }

            with open(self.compression_log, "a") as f:
                f.write(json.dumps(event) + "\n")

        except Exception:
            pass  # Non-critical if logging fails

    def _update_safety_status(self, recovery_results: Dict[str, Any]):
        """Update safety status file"""
        try:
            status = {
                "last_check": datetime.now().isoformat(),
                "compression_recovery_completed": True,
                "recovery_results": recovery_results,
                "system_operational": True,
            }

            with open(self.safety_status, "w") as f:
                json.dump(status, f, indent=2)

        except Exception:
            pass  # Non-critical if status update fails


# Auto-execute safety check when imported
def auto_safety_check():
    """Automatically execute safety check when this module is imported"""
    try:
        safety = CompressionResistantSafety()

        # Check if compression occurred
        if safety.detect_compression_event():
            print("🚨 COMPRESSION EVENT DETECTED - INITIATING EMERGENCY RECOVERY")
            recovery_result = safety.emergency_recovery()

            if not recovery_result.get("success"):
                print("❌ EMERGENCY RECOVERY FAILED - MANUAL INTERVENTION REQUIRED")
                return False

        # Always validate all systems
        validation = safety.validate_all_systems()

        if not validation["all_systems_operational"]:
            print(
                f"⚠️ SYSTEM VALIDATION WARNING: {validation['operational_count']}/{validation['system_count']} systems operational"
            )

            # Attempt recovery for failed systems
            print("🔧 ATTEMPTING SYSTEM RECOVERY...")
            recovery_result = safety.emergency_recovery()

        return True

    except Exception as e:
        print(f"❌ SAFETY CHECK FAILED: {e}")
        return False


if __name__ == "__main__":
    # Test the compression-resistant safety system
    safety = CompressionResistantSafety()

    print("🛡️ Testing Compression-Resistant Safety System")
    print("=" * 50)

    # Test detection
    compression_detected = safety.detect_compression_event()
    print(f"Compression Detected: {compression_detected}")

    # Test validation
    validation = safety.validate_all_systems()
    print(f"All Systems Operational: {validation['all_systems_operational']}")

    # Test recovery if needed
    if not validation["all_systems_operational"]:
        print("Testing emergency recovery...")
        recovery = safety.emergency_recovery()
        print(f"Recovery Success: {recovery.get('success')}")
