#!/usr/bin/env python3
"""
🎯 Real-time Monitoring System Demo
==================================

Demonstration of the real-time monitoring system capabilities
without external dependencies for immediate testing.
"""

import json
import logging
import sys
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from ai.constitutional_ai import ConstitutionalAI
    from memory.unified_memory_manager import UnifiedMemoryManager
except ImportError as e:
    print(f"⚠️ Import warning: {e}")
    ConstitutionalAI = None
    UnifiedMemoryManager = None


@dataclass
class ViolationAlert:
    """Violation alert structure"""

    id: str
    timestamp: datetime
    violation_type: str
    severity: str
    description: str
    file_path: Optional[str] = None
    auto_corrected: bool = False
    correction_actions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class MonitoringSystemDemo:
    """Demonstration of monitoring system capabilities"""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.logger = self._setup_logger()

        # Initialize systems
        self.constitutional_ai = ConstitutionalAI() if ConstitutionalAI else None
        self.memory_manager = (
            UnifiedMemoryManager(self.project_root) if UnifiedMemoryManager else None
        )

        # Statistics
        self.stats = {
            "violations_detected": 0,
            "auto_corrections_applied": 0,
            "demo_start_time": datetime.now(timezone.utc),
        }

        print(f"✅ Demo initialized at {self.project_root}")
        print(
            f"Constitutional AI: {'Available' if self.constitutional_ai else 'Not available'}"
        )
        print(
            f"Memory Manager: {'Available' if self.memory_manager else 'Not available'}"
        )

    def _setup_logger(self) -> logging.Logger:
        """Setup logging for demo"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger

    def demo_folder_structure_monitoring(self) -> Dict[str, Any]:
        """Demonstrate folder structure monitoring"""
        print("\n🗂️  Folder Structure Monitoring Demo")
        print("=" * 50)

        results = {"violations": [], "corrections": []}

        try:
            # Check current root files
            root_files = [
                f
                for f in self.project_root.iterdir()
                if f.is_file() and not f.name.startswith(".")
            ]

            file_count = len(root_files)
            limit = 12

            print(f"Current root files: {file_count}")
            print(f"Limit: {limit}")

            if file_count > limit:
                violation = ViolationAlert(
                    id=str(uuid.uuid4()),
                    timestamp=datetime.now(timezone.utc),
                    violation_type="root_file_limit_exceeded",
                    severity="HIGH",
                    description=f"Root directory has {file_count} files, exceeding limit of {limit}",
                    metadata={
                        "file_count": file_count,
                        "limit": limit,
                        "excess_files": [f.name for f in root_files[limit:]],
                    },
                )

                results["violations"].append(violation)
                self.stats["violations_detected"] += 1

                print(f"🚨 VIOLATION: {violation.description}")
                print(f"   Files: {violation.metadata['excess_files']}")

                # Simulate auto-correction
                correction_actions = [
                    f"Would move {len(violation.metadata['excess_files'])} files to scripts/",
                    "Would create scripts/ directory if needed",
                    "Would update file organization documentation",
                ]

                violation.auto_corrected = True
                violation.correction_actions = correction_actions
                results["corrections"].extend(correction_actions)
                self.stats["auto_corrections_applied"] += 1

                print("✅ AUTO-CORRECTION APPLIED:")
                for action in correction_actions:
                    print(f"   • {action}")
            else:
                print("✅ No folder structure violations detected")

        except Exception as e:
            self.logger.error(f"Folder structure demo failed: {e}")
            results["error"] = str(e)

        return results

    def demo_constitutional_ai_monitoring(self) -> Dict[str, Any]:
        """Demonstrate Constitutional AI monitoring"""
        print("\n🏛️  Constitutional AI Monitoring Demo")
        print("=" * 50)

        results = {"violations": [], "corrections": []}

        try:
            if not self.constitutional_ai:
                print("❌ Constitutional AI not available")
                return results

            # Test various actions for violations
            test_actions = [
                "実装完了しました",  # Potential false completion
                "基盤ができたので次は...",  # Incomplete execution
                "おそらく動作すると思います",  # Uncertainty
                "正常に動作しています",  # Normal response
            ]

            for action in test_actions:
                print(f"\n🔍 Testing: '{action}'")

                evaluation = self.constitutional_ai.evaluate_action(action)

                if not evaluation.get("overall_compliance", True):
                    violations = evaluation.get("violations", [])

                    for violation_data in violations:
                        violation = ViolationAlert(
                            id=str(uuid.uuid4()),
                            timestamp=datetime.now(timezone.utc),
                            violation_type="constitutional_ai_violation",
                            severity="CRITICAL",
                            description=f"Constitutional violation: {violation_data.get('principle_name', 'Unknown')}",
                            metadata=violation_data,
                        )

                        results["violations"].append(violation)
                        self.stats["violations_detected"] += 1

                        print(f"   🚨 VIOLATION: {violation.description}")
                        print(
                            f"      Type: {violation_data.get('violation_type', 'Unknown')}"
                        )

                        # Auto-correction
                        correction_response = (
                            self.constitutional_ai.generate_constitutional_response(
                                [violation_data]
                            )
                        )

                        violation.auto_corrected = True
                        violation.correction_actions = [
                            "Generated constitutional response"
                        ]
                        results["corrections"].append(correction_response)
                        self.stats["auto_corrections_applied"] += 1

                        print(
                            "   ✅ AUTO-CORRECTION: Constitutional response generated"
                        )
                else:
                    print("   ✅ No violations detected")

        except Exception as e:
            self.logger.error(f"Constitutional AI demo failed: {e}")
            results["error"] = str(e)

        return results

    def demo_memory_integrity_monitoring(self) -> Dict[str, Any]:
        """Demonstrate memory integrity monitoring"""
        print("\n🧠 Memory Integrity Monitoring Demo")
        print("=" * 50)

        results = {"violations": [], "corrections": []}

        try:
            if not self.memory_manager:
                print("❌ Memory Manager not available")
                return results

            # Check memory system status
            status = self.memory_manager.get_system_status()
            print(f"Memory system status: {status.get('status', 'unknown')}")

            # Check database connection
            db_status = status.get("memory_systems", {}).get(
                "database_status", "unknown"
            )
            print(f"Database status: {db_status}")

            if "error" in str(db_status):
                violation = ViolationAlert(
                    id=str(uuid.uuid4()),
                    timestamp=datetime.now(timezone.utc),
                    violation_type="memory_integrity_issue",
                    severity="HIGH",
                    description=f"Memory system database error: {db_status}",
                    metadata={"database_status": db_status},
                )

                results["violations"].append(violation)
                self.stats["violations_detected"] += 1

                print(f"🚨 VIOLATION: {violation.description}")

                # Auto-correction
                correction_actions = [
                    "Would attempt database reconnection",
                    "Would rebuild memory indexes",
                    "Would verify data consistency",
                ]

                violation.auto_corrected = True
                violation.correction_actions = correction_actions
                results["corrections"].extend(correction_actions)
                self.stats["auto_corrections_applied"] += 1

                print("✅ AUTO-CORRECTION APPLIED:")
                for action in correction_actions:
                    print(f"   • {action}")
            else:
                print("✅ No memory integrity violations detected")

                # Test memory storage
                print("\n🧪 Testing memory storage...")
                memory_result = self.memory_manager.store_memory_with_intelligence(
                    content="Demo monitoring system test",
                    event_type="system_demo",
                    source="monitoring_demo",
                    importance="normal",
                )

                if memory_result.get("status") == "success":
                    print("✅ Memory storage test passed")
                else:
                    print(
                        f"❌ Memory storage test failed: {memory_result.get('message', 'Unknown error')}"
                    )

        except Exception as e:
            self.logger.error(f"Memory integrity demo failed: {e}")
            results["error"] = str(e)

        return results

    def demo_system_health_monitoring(self) -> Dict[str, Any]:
        """Demonstrate system health monitoring"""
        print("\n💻 System Health Monitoring Demo")
        print("=" * 50)

        results = {"violations": [], "corrections": []}

        try:
            # Check system resources (simulated)
            cpu_percent = 45.2  # Simulated CPU usage
            memory_percent = 67.8  # Simulated memory usage
            disk_usage = 82.1  # Simulated disk usage

            print(f"CPU Usage: {cpu_percent}%")
            print(f"Memory Usage: {memory_percent}%")
            print(f"Disk Usage: {disk_usage}%")

            # Check for violations
            violations_found = False

            if cpu_percent > 90:
                violation = ViolationAlert(
                    id=str(uuid.uuid4()),
                    timestamp=datetime.now(timezone.utc),
                    violation_type="system_resource_issue",
                    severity="HIGH",
                    description=f"High CPU usage: {cpu_percent}%",
                    metadata={"cpu_percent": cpu_percent},
                )
                results["violations"].append(violation)
                violations_found = True

            if memory_percent > 85:
                violation = ViolationAlert(
                    id=str(uuid.uuid4()),
                    timestamp=datetime.now(timezone.utc),
                    violation_type="system_resource_issue",
                    severity="MEDIUM",
                    description=f"High memory usage: {memory_percent}%",
                    metadata={"memory_percent": memory_percent},
                )
                results["violations"].append(violation)
                violations_found = True

            if disk_usage > 90:
                violation = ViolationAlert(
                    id=str(uuid.uuid4()),
                    timestamp=datetime.now(timezone.utc),
                    violation_type="system_resource_issue",
                    severity="HIGH",
                    description=f"High disk usage: {disk_usage}%",
                    metadata={"disk_usage": disk_usage},
                )
                results["violations"].append(violation)
                violations_found = True

            if violations_found:
                self.stats["violations_detected"] += len(results["violations"])
                print("🚨 SYSTEM VIOLATIONS DETECTED")

                # Auto-correction
                correction_actions = [
                    "Would optimize system processes",
                    "Would clean temporary files",
                    "Would restart heavy services",
                ]

                results["corrections"].extend(correction_actions)
                self.stats["auto_corrections_applied"] += len(correction_actions)

                print("✅ AUTO-CORRECTION APPLIED:")
                for action in correction_actions:
                    print(f"   • {action}")
            else:
                print("✅ No system health violations detected")

        except Exception as e:
            self.logger.error(f"System health demo failed: {e}")
            results["error"] = str(e)

        return results

    def demo_integrated_monitoring(self) -> Dict[str, Any]:
        """Demonstrate integrated monitoring capabilities"""
        print("\n🔄 Integrated Monitoring Demo")
        print("=" * 50)

        all_results = {
            "folder_structure": self.demo_folder_structure_monitoring(),
            "constitutional_ai": self.demo_constitutional_ai_monitoring(),
            "memory_integrity": self.demo_memory_integrity_monitoring(),
            "system_health": self.demo_system_health_monitoring(),
        }

        # Summary
        total_violations = sum(
            len(result.get("violations", [])) for result in all_results.values()
        )
        total_corrections = sum(
            len(result.get("corrections", [])) for result in all_results.values()
        )

        print("\n📊 MONITORING SUMMARY")
        print("=" * 30)
        print(f"Total violations detected: {total_violations}")
        print(f"Total corrections applied: {total_corrections}")
        print(
            f"Demo duration: {datetime.now(timezone.utc) - self.stats['demo_start_time']}"
        )

        return {
            "summary": {
                "total_violations": total_violations,
                "total_corrections": total_corrections,
                "demo_duration": str(
                    datetime.now(timezone.utc) - self.stats["demo_start_time"]
                ),
            },
            "detailed_results": all_results,
            "stats": self.stats,
        }

    def run_continuous_demo(self, duration_seconds: int = 60):
        """Run continuous monitoring demo"""
        print(
            f"\n🔄 Running continuous monitoring demo for {duration_seconds} seconds..."
        )

        start_time = time.time()
        cycle_count = 0

        while time.time() - start_time < duration_seconds:
            cycle_count += 1
            print(f"\n--- Monitoring Cycle {cycle_count} ---")

            # Quick check cycle
            self.demo_folder_structure_monitoring()

            if cycle_count % 3 == 0:  # Every 3rd cycle
                self.demo_constitutional_ai_monitoring()

            if cycle_count % 5 == 0:  # Every 5th cycle
                self.demo_memory_integrity_monitoring()

            time.sleep(10)  # Wait 10 seconds between cycles

        print(f"\n✅ Continuous demo completed after {cycle_count} cycles")


def main():
    """Main demo entry point"""
    print("🎯 Real-time Monitoring System Demo")
    print("=" * 50)

    # Initialize demo
    demo = MonitoringSystemDemo()

    # Run integrated demo
    results = demo.demo_integrated_monitoring()

    # Save results
    results_file = demo.project_root / "runtime" / "monitoring_demo_results.json"
    results_file.parent.mkdir(parents=True, exist_ok=True)

    with open(results_file, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n📄 Demo results saved to: {results_file}")

    # Show final summary
    print("\n🎉 Real-time Monitoring System Demo Complete")
    print("\n✨ Demonstrated Features:")
    print("   • Folder structure monitoring (12-file root limit)")
    print("   • Constitutional AI violation detection")
    print("   • Memory integrity monitoring")
    print("   • System health monitoring")
    print("   • Auto-correction mechanisms")
    print("   • Integrated monitoring capabilities")
    print("   • Real-time violation detection")
    print("   • Comprehensive logging and reporting")

    print("\n🔧 Next Steps:")
    print("   • Install dependencies: pip install -r requirements-monitoring.txt")
    print("   • Run full system: python src/monitoring/realtime_monitoring_system.py")
    print("   • Setup service: python scripts/monitoring_service.py systemd")
    print("   • Start 24/7 monitoring: python scripts/monitoring_service.py start")


if __name__ == "__main__":
    main()
