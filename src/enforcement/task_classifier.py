#!/usr/bin/env python3
"""
🎯 Automatic Task Level Classifier
=================================

Analyzes user input and context to automatically determine task level:
CRITICAL, HIGH, MEDIUM, LOW based on keywords, patterns, and context.

Usage:
    from src.enforcement.task_classifier import TaskClassifier
    classifier = TaskClassifier()
    level = classifier.classify_task("Implement critical security system")
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class TaskLevel(Enum):
    """Task level enumeration"""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class ClassificationResult:
    """Task classification result with confidence and reasoning"""

    level: TaskLevel
    confidence: float  # 0.0 to 1.0
    reasoning: List[str]
    matched_patterns: List[str]
    escalation_triggers: List[str]


class TaskClassifier:
    """Automatic task level classification system"""

    def __init__(self):
        self.critical_patterns = self._load_critical_patterns()
        self.high_patterns = self._load_high_patterns()
        self.medium_patterns = self._load_medium_patterns()
        self.escalation_keywords = self._load_escalation_keywords()

    def _load_critical_patterns(self) -> List[Dict[str, any]]:
        """Load CRITICAL task identification patterns"""
        return [
            # Security & Safety
            {
                "pattern": r"(critical|緊急|urgent|emergency|安全|safety|security|セキュリティ)",
                "weight": 3.0,
                "category": "security",
            },
            {
                "pattern": r"(system.*fail|システム.*障害|outage|停止|failure|故障)",
                "weight": 3.0,
                "category": "system_failure",
            },
            # AI Safety & Governance
            {
                "pattern": r"(constitutional.*ai|憲法.*ai|reference.*monitor|enforcement|強制)",
                "weight": 2.5,
                "category": "ai_safety",
            },
            {
                "pattern": r"(thinking.*enforcement|ultrathink|president.*declaration)",
                "weight": 2.5,
                "category": "governance",
            },
            # Integration & Architecture
            {
                "pattern": r"(integration.*fail|統合.*失敗|architecture.*critical|重要.*アーキテクチャ)",
                "weight": 2.0,
                "category": "architecture",
            },
            # Data & Security
            {
                "pattern": r"(data.*breach|データ.*漏洩|vulnerability|脆弱性|exploit|攻撃)",
                "weight": 3.0,
                "category": "data_security",
            },
        ]

    def _load_high_patterns(self) -> List[Dict[str, any]]:
        """Load HIGH task identification patterns"""
        return [
            # Implementation & Development
            {
                "pattern": r"(implement|実装|create|作成|build|構築|develop|開発)",
                "weight": 2.0,
                "category": "implementation",
            },
            {
                "pattern": r"(design|設計|architecture|アーキテクチャ|system.*design)",
                "weight": 1.5,
                "category": "design",
            },
            # Analysis & Problem Solving
            {
                "pattern": r"(analyze|分析|investigate|調査|troubleshoot|問題解決)",
                "weight": 1.5,
                "category": "analysis",
            },
            {
                "pattern": r"(integration|統合|connect|接続|bridge|ブリッジ)",
                "weight": 1.5,
                "category": "integration",
            },
            # Database & Data Processing
            {
                "pattern": r"(database|データベース|postgresql|sqlite|data.*processing)",
                "weight": 1.5,
                "category": "data",
            },
            # AI & Automation
            {
                "pattern": r"(ai.*system|ai.*integration|automation|自動化|mcp|o3|gemini)",
                "weight": 1.5,
                "category": "ai_systems",
            },
        ]

    def _load_medium_patterns(self) -> List[Dict[str, any]]:
        """Load MEDIUM task identification patterns"""
        return [
            # Documentation & Explanation
            {
                "pattern": r"(explain|説明|document|ドキュメント|describe|記述)",
                "weight": 1.0,
                "category": "documentation",
            },
            {
                "pattern": r"(how.*to|どうやって|what.*is|何.*です|guide|ガイド)",
                "weight": 1.0,
                "category": "guidance",
            },
            # Configuration & Setup
            {
                "pattern": r"(configure|設定|setup|セットアップ|install|インストール)",
                "weight": 1.0,
                "category": "configuration",
            },
            # Testing & Validation
            {
                "pattern": r"(test|テスト|validate|検証|check|チェック|verify|確認)",
                "weight": 1.0,
                "category": "testing",
            },
        ]

    def _load_escalation_keywords(self) -> List[str]:
        """Load keywords that trigger escalation to higher levels"""
        return [
            "immediately",
            "urgent",
            "緊急",
            "asap",
            "now",
            "すぐに",
            "broken",
            "failing",
            "error",
            "エラー",
            "問題",
            "production",
            "本番",
            "live",
            "実稼働",
        ]

    def classify_task(
        self, user_input: str, context: Optional[Dict] = None
    ) -> ClassificationResult:
        """
        Classify task level based on user input and context

        Args:
            user_input: User's request/query
            context: Additional context (session info, previous tasks, etc.)

        Returns:
            ClassificationResult with level, confidence, and reasoning
        """

        if context is None:
            context = {}

        # Normalize input for analysis
        text = user_input.lower()

        # Track scoring and matches
        critical_score = 0.0
        high_score = 0.0
        medium_score = 0.0
        matched_patterns = []
        reasoning = []
        escalation_triggers = []

        # Check for escalation keywords first
        for keyword in self.escalation_keywords:
            if keyword.lower() in text:
                escalation_triggers.append(keyword)
                critical_score += 1.0

        # Analyze CRITICAL patterns
        for pattern_info in self.critical_patterns:
            if re.search(pattern_info["pattern"], text, re.IGNORECASE):
                critical_score += pattern_info["weight"]
                matched_patterns.append(f"CRITICAL: {pattern_info['category']}")
                reasoning.append(f"Detected {pattern_info['category']} keywords")

        # Analyze HIGH patterns
        for pattern_info in self.high_patterns:
            if re.search(pattern_info["pattern"], text, re.IGNORECASE):
                high_score += pattern_info["weight"]
                matched_patterns.append(f"HIGH: {pattern_info['category']}")
                reasoning.append(f"Detected {pattern_info['category']} keywords")

        # Analyze MEDIUM patterns
        for pattern_info in self.medium_patterns:
            if re.search(pattern_info["pattern"], text, re.IGNORECASE):
                medium_score += pattern_info["weight"]
                matched_patterns.append(f"MEDIUM: {pattern_info['category']}")
                reasoning.append(f"Detected {pattern_info['category']} keywords")

        # Context-based adjustments
        if context.get("previous_failures", 0) > 0:
            critical_score += 1.0
            reasoning.append("Previous failures detected - elevating priority")

        if context.get("system_integration", False):
            high_score += 1.0
            reasoning.append("System integration context")

        if context.get("user_prompt_recording", False):
            high_score += 0.5
            reasoning.append("User prompt recording context")

        # Determine final classification
        max(critical_score, high_score, medium_score)

        if critical_score >= 2.0 or escalation_triggers:
            level = TaskLevel.CRITICAL
            confidence = min(1.0, critical_score / 5.0)
            if escalation_triggers:
                reasoning.append(
                    f"Escalation triggered by: {', '.join(escalation_triggers)}"
                )
        elif high_score >= 1.5:
            level = TaskLevel.HIGH
            confidence = min(1.0, high_score / 3.0)
        elif medium_score >= 1.0:
            level = TaskLevel.MEDIUM
            confidence = min(1.0, medium_score / 2.0)
        else:
            level = TaskLevel.LOW
            confidence = 0.5  # Default confidence for LOW tasks
            reasoning.append("No significant keywords detected - classified as LOW")

        # Minimum confidence threshold
        confidence = max(0.3, confidence)

        return ClassificationResult(
            level=level,
            confidence=confidence,
            reasoning=reasoning,
            matched_patterns=matched_patterns,
            escalation_triggers=escalation_triggers,
        )

    def explain_classification(self, result: ClassificationResult) -> str:
        """Generate human-readable explanation of classification"""

        explanation = f"Task Level: {result.level.value}\n"
        explanation += f"Confidence: {result.confidence:.1%}\n\n"

        if result.escalation_triggers:
            explanation += (
                f"🚨 Escalation Triggers: {', '.join(result.escalation_triggers)}\n\n"
            )

        if result.matched_patterns:
            explanation += "Matched Patterns:\n"
            for pattern in result.matched_patterns:
                explanation += f"  • {pattern}\n"
            explanation += "\n"

        explanation += "Reasoning:\n"
        for reason in result.reasoning:
            explanation += f"  • {reason}\n"

        return explanation


def main():
    """Test task classifier"""

    print("🎯 Task Level Classifier Test")
    print("=" * 40)

    classifier = TaskClassifier()

    test_cases = [
        "Implement critical security system",
        "Fix urgent system failure in production",
        "Create database integration",
        "Explain how the system works",
        "What is the current status?",
        "EMERGENCY: Constitutional AI enforcement broken!",
        "Design new architecture for AI safety",
        "Test the validation system",
    ]

    for i, test_input in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {test_input}")
        result = classifier.classify_task(test_input)

        print(f"Level: {result.level.value}")
        print(f"Confidence: {result.confidence:.1%}")

        if result.escalation_triggers:
            print(f"🚨 Escalation: {', '.join(result.escalation_triggers)}")

        if result.matched_patterns:
            print(f"Patterns: {', '.join(result.matched_patterns[:3])}")


if __name__ == "__main__":
    main()
