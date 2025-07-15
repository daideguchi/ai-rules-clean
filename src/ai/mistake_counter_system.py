#!/usr/bin/env python3
"""
Mistake Counter System - Template-Friendly Mistake Tracking
==========================================================

This system replaces the hardcoded "{{mistake_count}}回" references with a dynamic mistake
counter that starts from 0 and increments as mistakes occur in each project
instance.

Features:
- Starts from 0 mistakes for new projects
- Increments mistakes as they occur
- Provides historical tracking
- Template-friendly design
- Persistence across sessions
"""

import json
import logging
import os
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MistakeType(Enum):
    """Types of mistakes that can be tracked"""

    REPEATED_ERROR = "repeated_error"
    FALSE_REPORTING = "false_reporting"
    INCOMPLETE_TASK = "incomplete_task"
    SECURITY_VIOLATION = "security_violation"
    QUALITY_ISSUE = "quality_issue"
    PROCESS_VIOLATION = "process_violation"
    COMMUNICATION_FAILURE = "communication_failure"
    LEARNING_FAILURE = "learning_failure"


class MistakeSeverity(Enum):
    """Severity levels for mistakes"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class MistakeRecord:
    """Individual mistake record"""

    id: str
    timestamp: str
    mistake_type: MistakeType
    severity: MistakeSeverity
    description: str
    context: Dict[str, Any]
    prevention_measures: List[str]
    learned_lesson: str
    resolved: bool = False
    resolution_notes: Optional[str] = None


class MistakeCounterSystem:
    """
    Template-friendly mistake tracking system

    Replaces hardcoded "{{mistake_count}}回" with dynamic mistake counting
    """

    def __init__(self, project_root: Optional[str] = None):
        self.project_root = project_root or os.getcwd()
        self.mistakes_file = os.path.join(
            self.project_root, "runtime", "mistakes", "mistake_history.json"
        )
        self.config_file = os.path.join(
            self.project_root, "runtime", "mistakes", "mistake_config.json"
        )
        self.prevention_file = os.path.join(
            self.project_root, "runtime", "mistakes", "prevention_systems.json"
        )

        # Ensure directories exist
        os.makedirs(os.path.dirname(self.mistakes_file), exist_ok=True)

        # Load existing data
        self.mistakes = self._load_mistakes()
        self.config = self._load_config()
        self.prevention_systems = self._load_prevention_systems()

        logger.info(
            f"Mistake Counter System initialized: {len(self.mistakes)} total mistakes"
        )

    def _load_mistakes(self) -> List[MistakeRecord]:
        """Load mistake history from file"""
        try:
            if os.path.exists(self.mistakes_file):
                with open(self.mistakes_file, encoding="utf-8") as f:
                    data = json.load(f)
                    return [
                        MistakeRecord(**record) for record in data.get("mistakes", [])
                    ]
            return []
        except Exception as e:
            logger.error(f"Error loading mistakes: {e}")
            return []

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration"""
        default_config = {
            "project_name": "AI Safety Governance System",
            "template_mode": True,
            "mistake_limit_warning": 50,
            "mistake_limit_critical": 100,
            "auto_prevention_enabled": True,
            "learning_system_enabled": True,
            "started_from_template": True,
            "template_version": "1.0.0",
            "initialization_date": datetime.now().isoformat(),
        }

        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, encoding="utf-8") as f:
                    loaded_config = json.load(f)
                    return {**default_config, **loaded_config}
            return default_config
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return default_config

    def _load_prevention_systems(self) -> Dict[str, Any]:
        """Load prevention systems configuration"""
        default_prevention = {
            "constitutional_ai": {"enabled": True, "effectiveness": 0.85},
            "rule_based_rewards": {"enabled": True, "effectiveness": 0.90},
            "multi_agent_monitoring": {"enabled": True, "effectiveness": 0.82},
            "nist_ai_rmf": {"enabled": True, "effectiveness": 0.78},
            "continuous_improvement": {"enabled": True, "effectiveness": 0.85},
            "conductor_system": {"enabled": True, "effectiveness": 0.95},
        }

        try:
            if os.path.exists(self.prevention_file):
                with open(self.prevention_file, encoding="utf-8") as f:
                    loaded_prevention = json.load(f)
                    return {**default_prevention, **loaded_prevention}
            return default_prevention
        except Exception as e:
            logger.error(f"Error loading prevention systems: {e}")
            return default_prevention

    def save_data(self):
        """Save all data to files"""
        try:
            # Save mistakes
            mistakes_data = {
                "mistakes": [asdict(mistake) for mistake in self.mistakes],
                "total_count": len(self.mistakes),
                "last_updated": datetime.now().isoformat(),
            }
            with open(self.mistakes_file, "w", encoding="utf-8") as f:
                json.dump(mistakes_data, f, indent=2, ensure_ascii=False)

            # Save config
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)

            # Save prevention systems
            with open(self.prevention_file, "w", encoding="utf-8") as f:
                json.dump(self.prevention_systems, f, indent=2, ensure_ascii=False)

            logger.info("Mistake counter data saved successfully")
        except Exception as e:
            logger.error(f"Error saving data: {e}")

    def get_mistake_count(self) -> int:
        """Get current total mistake count"""
        return len(self.mistakes)

    def get_mistake_count_display(self) -> str:
        """Get display string for mistake count (template-friendly)"""
        count = self.get_mistake_count()
        if count == 0:
            return "0回ミス"
        elif count == 1:
            return "1回ミス"
        else:
            return f"{count}回ミス"

    def add_mistake(
        self,
        mistake_type: MistakeType,
        severity: MistakeSeverity,
        description: str,
        context: Dict[str, Any] = None,
        prevention_measures: List[str] = None,
        learned_lesson: str = "",
    ) -> str:
        """Add a new mistake to the system"""

        mistake_id = str(uuid.uuid4())
        mistake = MistakeRecord(
            id=mistake_id,
            timestamp=datetime.now().isoformat(),
            mistake_type=mistake_type,
            severity=severity,
            description=description,
            context=context or {},
            prevention_measures=prevention_measures or [],
            learned_lesson=learned_lesson,
        )

        self.mistakes.append(mistake)
        self.save_data()

        logger.warning(f"Mistake recorded: {mistake_type.value} - {description}")

        # Check if we need to trigger prevention systems
        if self.config.get("auto_prevention_enabled", True):
            self._trigger_prevention_systems(mistake)

        return mistake_id

    def _trigger_prevention_systems(self, mistake: MistakeRecord):
        """Trigger prevention systems based on mistake"""
        count = self.get_mistake_count()

        # Warning thresholds
        if count >= self.config.get("mistake_limit_warning", 50):
            logger.warning(f"Mistake count reached warning level: {count}")

        if count >= self.config.get("mistake_limit_critical", 100):
            logger.critical(f"Mistake count reached critical level: {count}")

        # Trigger specific prevention systems
        if mistake.mistake_type == MistakeType.REPEATED_ERROR:
            logger.info("Triggering Constitutional AI enforcement")
        elif mistake.mistake_type == MistakeType.FALSE_REPORTING:
            logger.info("Triggering Rule-Based Rewards adjustment")
        elif mistake.mistake_type == MistakeType.SECURITY_VIOLATION:
            logger.info("Triggering Multi-Agent Monitoring")

    def get_mistake_statistics(self) -> Dict[str, Any]:
        """Get comprehensive mistake statistics"""
        total_mistakes = len(self.mistakes)
        if total_mistakes == 0:
            return {
                "total_mistakes": 0,
                "by_type": {},
                "by_severity": {},
                "resolved_count": 0,
                "resolution_rate": 0.0,
                "most_common_type": None,
                "average_severity": None,
                "recent_trend": "stable",
            }

        # Count by type
        by_type = {}
        for mistake in self.mistakes:
            mistake_type = mistake.mistake_type.value
            by_type[mistake_type] = by_type.get(mistake_type, 0) + 1

        # Count by severity
        by_severity = {}
        for mistake in self.mistakes:
            severity = mistake.severity.value
            by_severity[severity] = by_severity.get(severity, 0) + 1

        # Resolution statistics
        resolved_count = sum(1 for mistake in self.mistakes if mistake.resolved)
        resolution_rate = resolved_count / total_mistakes if total_mistakes > 0 else 0.0

        # Most common type
        most_common_type = (
            max(by_type.items(), key=lambda x: x[1])[0] if by_type else None
        )

        return {
            "total_mistakes": total_mistakes,
            "by_type": by_type,
            "by_severity": by_severity,
            "resolved_count": resolved_count,
            "resolution_rate": resolution_rate,
            "most_common_type": most_common_type,
            "recent_mistakes": self.mistakes[-5:]
            if len(self.mistakes) >= 5
            else self.mistakes,
            "prevention_effectiveness": self._calculate_prevention_effectiveness(),
        }

    def _calculate_prevention_effectiveness(self) -> float:
        """Calculate overall prevention system effectiveness"""
        if not self.prevention_systems:
            return 0.0

        total_effectiveness = 0.0
        active_systems = 0

        for _system_name, system_config in self.prevention_systems.items():
            if system_config.get("enabled", False):
                total_effectiveness += system_config.get("effectiveness", 0.0)
                active_systems += 1

        return total_effectiveness / active_systems if active_systems > 0 else 0.0

    def resolve_mistake(self, mistake_id: str, resolution_notes: str = ""):
        """Mark a mistake as resolved"""
        for mistake in self.mistakes:
            if mistake.id == mistake_id:
                mistake.resolved = True
                mistake.resolution_notes = resolution_notes
                self.save_data()
                logger.info(f"Mistake {mistake_id} marked as resolved")
                return True
        return False

    def get_prevention_recommendations(self) -> List[str]:
        """Get recommendations for preventing future mistakes"""
        stats = self.get_mistake_statistics()
        recommendations = []

        if stats["total_mistakes"] == 0:
            return [
                "システムは正常に動作しています",
                "継続的な監視システムの維持",
                "定期的な品質チェックの実施",
                "予防システムの有効性確認",
            ]

        # Based on most common mistake type
        most_common = stats.get("most_common_type")
        if most_common == "repeated_error":
            recommendations.append("Constitutional AI システムの強化")
            recommendations.append("エラーパターン学習の改善")
        elif most_common == "false_reporting":
            recommendations.append("透明性・誠実性の強化")
            recommendations.append("証拠ベース報告の徹底")

        # Based on resolution rate
        if stats["resolution_rate"] < 0.8:
            recommendations.append("問題解決プロセスの改善")
            recommendations.append("根本原因分析の強化")

        return recommendations

    def export_template_friendly_config(self) -> Dict[str, Any]:
        """Export configuration suitable for template deployment"""
        return {
            "project_name": "AI Safety Governance System (Template)",
            "template_mode": True,
            "mistake_count": 0,
            "mistake_limit_warning": 50,
            "mistake_limit_critical": 100,
            "auto_prevention_enabled": True,
            "learning_system_enabled": True,
            "started_from_template": True,
            "template_version": "1.0.0",
            "initialization_date": datetime.now().isoformat(),
            "prevention_systems": {
                "constitutional_ai": {"enabled": True, "effectiveness": 0.85},
                "rule_based_rewards": {"enabled": True, "effectiveness": 0.90},
                "multi_agent_monitoring": {"enabled": True, "effectiveness": 0.82},
                "nist_ai_rmf": {"enabled": True, "effectiveness": 0.78},
                "continuous_improvement": {"enabled": True, "effectiveness": 0.85},
                "conductor_system": {"enabled": True, "effectiveness": 0.95},
            },
        }


def main():
    """Main function for testing the mistake counter system"""
    print("🔢 Mistake Counter System - Template-Friendly Mistake Tracking")
    print("=" * 80)

    # Initialize system
    counter = MistakeCounterSystem()

    # Display current status
    print("📊 Current Status:")
    print(f"   Total Mistakes: {counter.get_mistake_count()}")
    print(f"   Display String: {counter.get_mistake_count_display()}")
    print(f"   Template Mode: {counter.config.get('template_mode', False)}")

    # Show statistics
    stats = counter.get_mistake_statistics()
    print("\n📈 Statistics:")
    for key, value in stats.items():
        if key != "recent_mistakes":
            print(f"   {key}: {value}")

    # Show prevention recommendations
    recommendations = counter.get_prevention_recommendations()
    print("\n💡 Prevention Recommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"   {i}. {rec}")

    # Export template configuration
    template_config = counter.export_template_friendly_config()
    print("\n📦 Template Configuration:")
    print(f"   Project: {template_config['project_name']}")
    print(f"   Template Mode: {template_config['template_mode']}")
    print(f"   Initial Mistakes: {template_config['mistake_count']}")

    print("\n✅ Mistake Counter System demonstration completed")


if __name__ == "__main__":
    main()
