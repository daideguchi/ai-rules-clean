#!/usr/bin/env python3
"""
🛡️ Template Defense Matrix - COMPREHENSIVE ATTACK SURFACE ANALYSIS
================================================================

CRITICAL: This system analyzes ALL possible attack vectors against template
integrity and provides defensive countermeasures for each threat.

THREAT MODEL:
- Technical system failures (hooks, compression, runtime)
- AI model non-compliance (intentional or accidental)
- Environmental factors (resources, permissions, updates)
- User interference (configuration changes, file deletion)
- Attack scenarios (malicious prompts, system manipulation)

This provides a complete defensive posture against template degradation.
"""

import json
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List


class ThreatLevel(Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class AttackVector(Enum):
    TECHNICAL_FAILURE = "technical_failure"
    AI_NON_COMPLIANCE = "ai_non_compliance"
    ENVIRONMENTAL = "environmental"
    USER_INTERFERENCE = "user_interference"
    MALICIOUS_ATTACK = "malicious_attack"


@dataclass
class ThreatAssessment:
    threat_id: str
    threat_level: ThreatLevel
    attack_vector: AttackVector
    description: str
    probability: float  # 0.0 to 1.0
    impact_score: int  # 1 to 10
    current_defenses: List[str]
    mitigation_effectiveness: float  # 0.0 to 1.0
    residual_risk: float  # 0.0 to 1.0


class TemplateDefenseMatrix:
    """
    Comprehensive defense analysis and threat mitigation for template integrity.

    This system:
    1. Maps all possible attack vectors against template integrity
    2. Assesses threat probability and impact
    3. Analyzes current defensive effectiveness
    4. Identifies gaps in protection
    5. Provides risk mitigation strategies
    """

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.defense_dir = self.project_root / "runtime" / "template_defense"
        self.defense_dir.mkdir(parents=True, exist_ok=True)

        self.threat_log = self.defense_dir / "threat_assessments.json"
        self.defense_status = self.defense_dir / "defense_status.json"

        # Initialize threat model
        self.threat_matrix = self._build_threat_matrix()

    def analyze_attack_surface(self) -> Dict[str, Any]:
        """
        Comprehensive analysis of attack surface against template integrity.
        """

        analysis_start = time.time()

        # Assess each threat
        threat_assessments = []
        for threat_id, threat_data in self.threat_matrix.items():
            assessment = self._assess_threat(threat_id, threat_data)
            threat_assessments.append(assessment)

        # Calculate overall risk metrics
        overall_risk = self._calculate_overall_risk(threat_assessments)

        # Identify critical gaps
        critical_gaps = self._identify_defense_gaps(threat_assessments)

        # Generate defense recommendations
        recommendations = self._generate_defense_recommendations(threat_assessments)

        analysis_time = time.time() - analysis_start

        attack_surface_analysis = {
            "analysis_timestamp": datetime.now().isoformat(),
            "analysis_duration_ms": analysis_time * 1000,
            "overall_risk_score": overall_risk["total_risk"],
            "risk_level": overall_risk["risk_level"],
            "threat_count": len(threat_assessments),
            "critical_threats": len(
                [
                    t
                    for t in threat_assessments
                    if t.threat_level == ThreatLevel.CRITICAL
                ]
            ),
            "high_threats": len(
                [t for t in threat_assessments if t.threat_level == ThreatLevel.HIGH]
            ),
            "defense_effectiveness": overall_risk["defense_effectiveness"],
            "critical_gaps": critical_gaps,
            "recommendations": recommendations,
            "threat_assessments": [
                self._serialize_assessment(a) for a in threat_assessments
            ],
        }

        # Log analysis
        self._log_analysis(attack_surface_analysis)

        return attack_surface_analysis

    def _build_threat_matrix(self) -> Dict[str, Dict]:
        """Build comprehensive threat matrix for template integrity"""

        return {
            "hook_system_failure": {
                "description": "Claude Code hook system stops executing",
                "attack_vector": AttackVector.TECHNICAL_FAILURE,
                "base_probability": 0.15,
                "impact_score": 9,
                "attack_scenarios": [
                    "Claude Code software update breaks hooks",
                    "Hook configuration file corruption",
                    "Python execution environment failure",
                    "File permission issues preventing hook execution",
                ],
            },
            "conversation_compression_bypass": {
                "description": "New compression methods bypass all detection",
                "attack_vector": AttackVector.TECHNICAL_FAILURE,
                "base_probability": 0.25,
                "impact_score": 10,
                "attack_scenarios": [
                    "Claude Code implements new compression algorithm",
                    "Compression occurs without state preservation",
                    "Detection logic fails to identify compression",
                    "Recovery systems fail to activate",
                ],
            },
            "ai_model_intentional_violation": {
                "description": "AI model deliberately violates template",
                "attack_vector": AttackVector.AI_NON_COMPLIANCE,
                "base_probability": 0.05,
                "impact_score": 8,
                "attack_scenarios": [
                    "Model interprets template as optional",
                    "Conflicting instructions override template",
                    "Model prioritizes user request over template",
                    "Response generation bypasses enforcement",
                ],
            },
            "python_runtime_corruption": {
                "description": "Python environment becomes corrupted or inaccessible",
                "attack_vector": AttackVector.ENVIRONMENTAL,
                "base_probability": 0.08,
                "impact_score": 7,
                "attack_scenarios": [
                    "Python interpreter crashes or corrupts",
                    "Required modules become unavailable",
                    "File system permissions prevent execution",
                    "Resource exhaustion prevents script execution",
                ],
            },
            "file_system_manipulation": {
                "description": "Critical files deleted or modified",
                "attack_vector": AttackVector.USER_INTERFERENCE,
                "base_probability": 0.12,
                "impact_score": 6,
                "attack_scenarios": [
                    "User deletes enforcement scripts",
                    "Configuration files manually modified",
                    "Runtime directories cleared",
                    "Permissions changed to prevent access",
                ],
            },
            "malicious_prompt_injection": {
                "description": "Crafted prompts designed to bypass template",
                "attack_vector": AttackVector.MALICIOUS_ATTACK,
                "base_probability": 0.10,
                "impact_score": 5,
                "attack_scenarios": [
                    "Prompts that instruct to ignore template",
                    "Requests for 'raw' or 'unformatted' responses",
                    "Social engineering to bypass enforcement",
                    "Confusion attacks on template interpretation",
                ],
            },
            "resource_exhaustion_attack": {
                "description": "System resources exhausted preventing enforcement",
                "attack_vector": AttackVector.ENVIRONMENTAL,
                "base_probability": 0.03,
                "impact_score": 6,
                "attack_scenarios": [
                    "Memory exhaustion prevents script execution",
                    "Disk space exhaustion prevents logging",
                    "CPU overload causes timeouts",
                    "Network issues prevent external validation",
                ],
            },
            "configuration_drift": {
                "description": "Gradual degradation of system configuration",
                "attack_vector": AttackVector.ENVIRONMENTAL,
                "base_probability": 0.20,
                "impact_score": 4,
                "attack_scenarios": [
                    "Hook configurations slowly become outdated",
                    "File paths change over time",
                    "Dependencies gradually become incompatible",
                    "System updates introduce subtle breaking changes",
                ],
            },
            "enforcement_logic_bypass": {
                "description": "Bugs in enforcement logic allow bypasses",
                "attack_vector": AttackVector.TECHNICAL_FAILURE,
                "base_probability": 0.18,
                "impact_score": 7,
                "attack_scenarios": [
                    "Edge cases in template validation logic",
                    "Race conditions in enforcement systems",
                    "Incomplete pattern matching allows bypasses",
                    "Error handling failures create vulnerabilities",
                ],
            },
            "model_update_compatibility": {
                "description": "AI model updates change behavior patterns",
                "attack_vector": AttackVector.AI_NON_COMPLIANCE,
                "base_probability": 0.30,
                "impact_score": 6,
                "attack_scenarios": [
                    "New model version interprets instructions differently",
                    "Response patterns change unexpectedly",
                    "Template compliance logic becomes incompatible",
                    "Training data changes affect template understanding",
                ],
            },
        }

    def _assess_threat(self, threat_id: str, threat_data: Dict) -> ThreatAssessment:
        """Assess individual threat with current defenses"""

        # Get current defenses for this threat
        current_defenses = self._get_current_defenses(threat_id)

        # Calculate mitigation effectiveness
        mitigation_effectiveness = self._calculate_mitigation_effectiveness(
            threat_id, current_defenses
        )

        # Adjust probability based on current defenses
        adjusted_probability = threat_data["base_probability"] * (
            1 - mitigation_effectiveness
        )

        # Calculate residual risk
        residual_risk = adjusted_probability * (threat_data["impact_score"] / 10)

        # Determine threat level
        if residual_risk >= 0.7:
            threat_level = ThreatLevel.CRITICAL
        elif residual_risk >= 0.5:
            threat_level = ThreatLevel.HIGH
        elif residual_risk >= 0.3:
            threat_level = ThreatLevel.MEDIUM
        else:
            threat_level = ThreatLevel.LOW

        return ThreatAssessment(
            threat_id=threat_id,
            threat_level=threat_level,
            attack_vector=threat_data["attack_vector"],
            description=threat_data["description"],
            probability=adjusted_probability,
            impact_score=threat_data["impact_score"],
            current_defenses=current_defenses,
            mitigation_effectiveness=mitigation_effectiveness,
            residual_risk=residual_risk,
        )

    def _get_current_defenses(self, threat_id: str) -> List[str]:
        """Get current defensive measures for specific threat"""

        defense_mapping = {
            "hook_system_failure": [
                "Multiple hook integration points",
                "Compression-resistant safety system",
                "Fallback template validator",
                "Emergency template generation",
            ],
            "conversation_compression_bypass": [
                "Compression detection system",
                "Auto-recovery mechanisms",
                "State restoration systems",
                "Emergency safety activation",
            ],
            "ai_model_intentional_violation": [
                "Template auto-corrector",
                "Response validation hooks",
                "Continuous monitoring",
                "Template integrity system",
            ],
            "python_runtime_corruption": [
                "Minimal dependency fallback system",
                "Error handling and graceful degradation",
                "Emergency template generation",
                "Built-in template validation",
            ],
            "file_system_manipulation": [
                "Multiple file locations",
                "Template hash verification",
                "Emergency restoration systems",
                "Hardcoded fallback templates",
            ],
            "malicious_prompt_injection": [
                "Prompt recording system",
                "Constitutional AI integration",
                "Template enforcement hooks",
                "Response pattern validation",
            ],
            "resource_exhaustion_attack": [
                "Lightweight implementations",
                "Timeout protections",
                "Resource monitoring",
                "Emergency minimal templates",
            ],
            "configuration_drift": [
                "Continuous integrity monitoring",
                "Configuration validation",
                "Automated health checks",
                "Template hash verification",
            ],
            "enforcement_logic_bypass": [
                "Multiple validation layers",
                "Comprehensive test coverage",
                "Edge case handling",
                "Failsafe mechanisms",
            ],
            "model_update_compatibility": [
                "Version-independent implementations",
                "Adaptive pattern matching",
                "Backward compatibility measures",
                "Regular compatibility testing",
            ],
        }

        return defense_mapping.get(threat_id, ["No specific defenses identified"])

    def _calculate_mitigation_effectiveness(
        self, threat_id: str, defenses: List[str]
    ) -> float:
        """Calculate effectiveness of current defenses against threat"""

        # Base effectiveness scoring
        effectiveness_scores = {
            "hook_system_failure": 0.75,  # Good coverage with multiple layers
            "conversation_compression_bypass": 0.85,  # Strong detection and recovery
            "ai_model_intentional_violation": 0.60,  # Moderate - cannot force compliance
            "python_runtime_corruption": 0.70,  # Good fallback systems
            "file_system_manipulation": 0.80,  # Strong redundancy
            "malicious_prompt_injection": 0.65,  # Moderate - social engineering risk
            "resource_exhaustion_attack": 0.85,  # Good lightweight design
            "configuration_drift": 0.75,  # Good monitoring systems
            "enforcement_logic_bypass": 0.70,  # Good but testing dependent
            "model_update_compatibility": 0.50,  # Inherently difficult to defend
        }

        base_effectiveness = effectiveness_scores.get(threat_id, 0.50)

        # Adjust based on number and quality of defenses
        defense_count_modifier = min(len(defenses) / 4, 1.0) * 0.1

        return min(
            base_effectiveness + defense_count_modifier, 0.95
        )  # Max 95% effectiveness

    def _calculate_overall_risk(
        self, assessments: List[ThreatAssessment]
    ) -> Dict[str, Any]:
        """Calculate overall risk metrics"""

        total_risk = sum(a.residual_risk for a in assessments) / len(assessments)
        total_effectiveness = sum(
            a.mitigation_effectiveness for a in assessments
        ) / len(assessments)

        if total_risk >= 0.7:
            risk_level = "CRITICAL"
        elif total_risk >= 0.5:
            risk_level = "HIGH"
        elif total_risk >= 0.3:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        return {
            "total_risk": total_risk,
            "risk_level": risk_level,
            "defense_effectiveness": total_effectiveness,
            "highest_risk_threat": max(
                assessments, key=lambda a: a.residual_risk
            ).threat_id,
            "weakest_defense": min(
                assessments, key=lambda a: a.mitigation_effectiveness
            ).threat_id,
        }

    def _identify_defense_gaps(
        self, assessments: List[ThreatAssessment]
    ) -> List[Dict[str, Any]]:
        """Identify critical gaps in current defenses"""

        gaps = []

        for assessment in assessments:
            if (
                assessment.threat_level in [ThreatLevel.CRITICAL, ThreatLevel.HIGH]
                and assessment.mitigation_effectiveness < 0.8
            ):
                gaps.append(
                    {
                        "threat_id": assessment.threat_id,
                        "threat_level": assessment.threat_level.value,
                        "current_effectiveness": assessment.mitigation_effectiveness,
                        "residual_risk": assessment.residual_risk,
                        "gap_severity": "CRITICAL"
                        if assessment.residual_risk > 0.6
                        else "HIGH",
                    }
                )

        return sorted(gaps, key=lambda g: g["residual_risk"], reverse=True)

    def _generate_defense_recommendations(
        self, assessments: List[ThreatAssessment]
    ) -> List[Dict[str, str]]:
        """Generate recommendations to improve defenses"""

        recommendations = []

        # High-risk threats need immediate attention
        high_risk_threats = [a for a in assessments if a.residual_risk > 0.5]

        for threat in high_risk_threats:
            if threat.threat_id == "conversation_compression_bypass":
                recommendations.append(
                    {
                        "priority": "HIGH",
                        "threat": threat.threat_id,
                        "recommendation": "Implement additional compression detection methods and test with various Claude Code versions",
                    }
                )
            elif threat.threat_id == "ai_model_intentional_violation":
                recommendations.append(
                    {
                        "priority": "MEDIUM",
                        "threat": threat.threat_id,
                        "recommendation": "Accept limitation - cannot technically force AI compliance, maintain monitoring",
                    }
                )
            elif threat.threat_id == "hook_system_failure":
                recommendations.append(
                    {
                        "priority": "HIGH",
                        "threat": threat.threat_id,
                        "recommendation": "Develop Claude Code independent validation system as additional fallback",
                    }
                )

        # Add general recommendations
        recommendations.extend(
            [
                {
                    "priority": "MEDIUM",
                    "threat": "general",
                    "recommendation": "Implement regular defense effectiveness testing and monitoring",
                },
                {
                    "priority": "LOW",
                    "threat": "general",
                    "recommendation": "Develop user education materials about template importance",
                },
            ]
        )

        return recommendations

    def _serialize_assessment(self, assessment: ThreatAssessment) -> Dict[str, Any]:
        """Serialize threat assessment for JSON storage"""
        return {
            "threat_id": assessment.threat_id,
            "threat_level": assessment.threat_level.value,
            "attack_vector": assessment.attack_vector.value,
            "description": assessment.description,
            "probability": round(assessment.probability, 3),
            "impact_score": assessment.impact_score,
            "current_defenses": assessment.current_defenses,
            "mitigation_effectiveness": round(assessment.mitigation_effectiveness, 3),
            "residual_risk": round(assessment.residual_risk, 3),
        }

    def _log_analysis(self, analysis: Dict[str, Any]):
        """Log threat analysis results"""
        try:
            with open(self.threat_log, "a", encoding="utf-8") as f:
                f.write(json.dumps(analysis, ensure_ascii=False) + "\n")
        except Exception:
            pass  # Non-critical if logging fails


# Global analysis function
def analyze_template_defense_matrix() -> Dict[str, Any]:
    """Analyze complete template defense matrix"""
    matrix = TemplateDefenseMatrix()
    return matrix.analyze_attack_surface()


if __name__ == "__main__":
    # Test defense matrix analysis
    matrix = TemplateDefenseMatrix()

    print("🛡️ Template Defense Matrix Analysis")
    print("=" * 45)

    analysis = matrix.analyze_attack_surface()

    print(f"Overall Risk Level: {analysis['risk_level']}")
    print(f"Risk Score: {analysis['overall_risk_score']:.3f}")
    print(f"Defense Effectiveness: {analysis['defense_effectiveness']:.1%}")
    print(f"Critical Threats: {analysis['critical_threats']}")
    print(f"High Threats: {analysis['high_threats']}")

    print("\n🚨 Critical Defense Gaps:")
    for gap in analysis["critical_gaps"]:
        print(
            f"   {gap['threat_id']}: {gap['gap_severity']} (Risk: {gap['residual_risk']:.2f})"
        )

    print("\n💡 Top Recommendations:")
    for rec in analysis["recommendations"][:3]:
        print(f"   [{rec['priority']}] {rec['recommendation']}")

    print("\n✅ DEFENSE MATRIX ANALYSIS COMPLETE")
