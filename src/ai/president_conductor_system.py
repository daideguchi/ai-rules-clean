#!/usr/bin/env python3
"""
President/Conductor System
PRESIDENT/指揮者による効率的タスク判定・実行制御システム
適切な手法選択によりコンテキスト効率化
"""

import datetime
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from task_complexity_classifier import (
    ExecutionMethod,
    TaskComplexity,
    TaskComplexityClassifier,
)


@dataclass
class ExecutionDecision:
    """実行決定"""

    task_description: str
    complexity: TaskComplexity
    execution_method: ExecutionMethod
    justification: str
    efficiency_score: float
    estimated_time: int
    should_use_ai_org: bool


class PresidentConductorSystem:
    """PRESIDENT/指揮者システム"""

    def __init__(self):
        self.base_path = Path("/Users/dd/Desktop/1_dev/coding-rule2")
        self.session_file = (
            self.base_path
            / "src"
            / "memory"
            / "core"
            / "session-records"
            / "current-session.json"
        )
        self.decisions_log = self.base_path / "runtime" / "president_decisions.json"
        self.classifier = TaskComplexityClassifier()

        # Create runtime directory
        self.decisions_log.parent.mkdir(exist_ok=True)

        # Efficiency thresholds
        self.ai_org_threshold = 0.7  # AI組織を使う閾値
        self.ultrathink_threshold = 0.8  # Ultrathinkを使う閾値

    def make_execution_decision(
        self, task_description: str, context: Optional[Dict[str, Any]] = None
    ) -> ExecutionDecision:
        """PRESIDENT判断による実行決定"""
        context = context or {}

        # タスク分類
        classification = self.classifier.classify_task(task_description, context)

        # 効率性分析
        efficiency_analysis = self._analyze_efficiency(
            classification, task_description, context
        )

        # AI組織使用判定
        should_use_ai_org = self._should_use_ai_organization(
            classification, efficiency_analysis, context
        )

        # 実行手法の最終決定（オーバーライド判定）
        final_method = self._determine_final_method(
            classification.execution_method, should_use_ai_org, efficiency_analysis
        )

        # 判断理由の生成
        justification = self._generate_justification(
            classification, efficiency_analysis, should_use_ai_org, final_method
        )

        decision = ExecutionDecision(
            task_description=task_description,
            complexity=classification.complexity,
            execution_method=final_method,
            justification=justification,
            efficiency_score=efficiency_analysis["efficiency_score"],
            estimated_time=classification.estimated_time,
            should_use_ai_org=should_use_ai_org,
        )

        # 決定ログ記録
        self._log_decision(decision, classification, efficiency_analysis)

        return decision

    def _analyze_efficiency(
        self, classification, task_description: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """効率性分析"""
        analysis = {"efficiency_score": 0.0, "factors": {}, "recommendations": []}

        # 基本効率性スコア（複雑度ベース）
        base_scores = {
            TaskComplexity.TRIVIAL: 0.9,  # 高効率
            TaskComplexity.SIMPLE: 0.8,  # 良好
            TaskComplexity.COMPLEX: 0.6,  # 中程度
            TaskComplexity.AI_CONSULTATION: 0.4,  # 低効率だが必要
        }
        analysis["efficiency_score"] = base_scores[classification.complexity]

        # 修正要因
        factors = analysis["factors"]

        # 1. 規模要因
        if "single" in task_description.lower() or "one" in task_description.lower():
            factors["scale_bonus"] = 0.1
            analysis["efficiency_score"] += 0.1
        elif (
            "multiple" in task_description.lower() or "many" in task_description.lower()
        ):
            factors["scale_penalty"] = -0.1
            analysis["efficiency_score"] -= 0.1

        # 2. 緊急性要因
        if context.get("urgency") == "high":
            factors["urgency_factor"] = 0.15
            analysis["efficiency_score"] += 0.15
            analysis["recommendations"].append("High urgency: prefer direct execution")

        # 3. 過去のミス履歴
        mistakes_count = context.get("previous_mistakes_count", 0)
        if mistakes_count > 0:
            penalty = min(0.2, mistakes_count * 0.01)
            factors["mistake_penalty"] = -penalty
            analysis["efficiency_score"] -= penalty
            analysis["recommendations"].append(
                "Previous mistakes detected: prefer AI consultation"
            )

        # 4. コンテキスト消費量
        if (
            "ai organization" in task_description.lower()
            or "複数ai" in task_description.lower()
        ):
            factors["context_heavy"] = -0.2
            analysis["efficiency_score"] -= 0.2
            analysis["recommendations"].append("Context-heavy task: evaluate necessity")

        # 5. 学習価値
        if "new" in task_description.lower() or "learn" in task_description.lower():
            factors["learning_value"] = 0.1
            analysis["efficiency_score"] += 0.1
            analysis["recommendations"].append(
                "Learning opportunity: consider AI consultation"
            )

        # スコア範囲制限
        analysis["efficiency_score"] = max(0.0, min(1.0, analysis["efficiency_score"]))

        return analysis

    def _should_use_ai_organization(
        self,
        classification,
        efficiency_analysis: Dict[str, Any],
        context: Dict[str, Any],
    ) -> bool:
        """AI組織使用判定"""

        # 強制AI組織使用条件
        force_ai_org_keywords = [
            "strategy",
            "architecture",
            "evaluate",
            "analyze",
            "research",
            "戦略",
            "アーキテクチャ",
            "評価",
            "分析",
            "研究",
            "調査",
        ]

        if any(
            keyword in classification.execution_method.value
            for keyword in force_ai_org_keywords
        ):
            return True

        # 複雑度ベース判定
        if classification.complexity == TaskComplexity.AI_CONSULTATION:
            return True

        # 効率性ベース判定
        if efficiency_analysis["efficiency_score"] < self.ai_org_threshold:
            # 低効率タスクでもAI組織が有効な場合
            if classification.complexity == TaskComplexity.COMPLEX:
                return True

        # 特殊条件
        # 過去のミスが多い場合
        if context.get("previous_mistakes_count", 0) >= 3:
            return True

        # クリティカルなタスク
        if context.get("critical", False):
            return True

        return False

    def _determine_final_method(
        self,
        suggested_method: ExecutionMethod,
        should_use_ai_org: bool,
        efficiency_analysis: Dict[str, Any],
    ) -> ExecutionMethod:
        """最終実行手法決定"""

        # AI組織使用が推奨される場合のオーバーライド
        if should_use_ai_org:
            if suggested_method in [ExecutionMethod.DIRECT, ExecutionMethod.PLANNED]:
                return ExecutionMethod.AI_ORGANIZATION

        # 効率性が極めて低い場合の手法変更
        if efficiency_analysis["efficiency_score"] < 0.3:
            if suggested_method == ExecutionMethod.AI_ORGANIZATION:
                return ExecutionMethod.ULTRATHINK

        # 効率性が高い場合の簡略化
        if efficiency_analysis["efficiency_score"] > 0.9:
            if suggested_method == ExecutionMethod.PLANNED:
                return ExecutionMethod.DIRECT

        return suggested_method

    def _generate_justification(
        self,
        classification,
        efficiency_analysis: Dict[str, Any],
        should_use_ai_org: bool,
        final_method: ExecutionMethod,
    ) -> str:
        """判断理由生成"""
        reasons = []

        # 基本分類理由
        reasons.append(f"Task complexity: {classification.complexity.value}")
        reasons.append(
            f"Efficiency score: {efficiency_analysis['efficiency_score']:.2f}"
        )

        # 効率性要因
        factors = efficiency_analysis.get("factors", {})
        if factors:
            factor_descriptions = []
            for factor, value in factors.items():
                if value > 0:
                    factor_descriptions.append(f"+{factor}")
                elif value < 0:
                    factor_descriptions.append(f"-{factor}")
            if factor_descriptions:
                reasons.append(f"Efficiency factors: {', '.join(factor_descriptions)}")

        # AI組織判定理由
        if should_use_ai_org:
            if final_method == ExecutionMethod.AI_ORGANIZATION:
                reasons.append("AI organization recommended for optimal results")
            elif final_method == ExecutionMethod.ULTRATHINK:
                reasons.append(
                    "Ultrathink preferred over AI organization for efficiency"
                )
        else:
            reasons.append("Direct execution sufficient for this task")

        # 推奨事項
        recommendations = efficiency_analysis.get("recommendations", [])
        if recommendations:
            reasons.append(f"Recommendations: {'; '.join(recommendations)}")

        return " | ".join(reasons)

    def _log_decision(
        self,
        decision: ExecutionDecision,
        classification,
        efficiency_analysis: Dict[str, Any],
    ):
        """決定ログ記録"""
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "task_description": decision.task_description,
            "decision": {
                "complexity": decision.complexity.value,
                "execution_method": decision.execution_method.value,
                "should_use_ai_org": decision.should_use_ai_org,
                "efficiency_score": decision.efficiency_score,
                "estimated_time": decision.estimated_time,
            },
            "analysis": {
                "classification": {
                    "confidence": classification.confidence,
                    "reasoning": classification.reasoning,
                    "required_tools": classification.required_tools,
                    "risk_level": classification.risk_level,
                },
                "efficiency": efficiency_analysis,
            },
            "justification": decision.justification,
        }

        # 既存ログ読み込み
        logs = []
        if self.decisions_log.exists():
            try:
                with open(self.decisions_log, encoding="utf-8") as f:
                    logs = json.load(f)
            except Exception:
                logs = []

        logs.append(log_entry)

        # 最新50件のみ保持
        if len(logs) > 50:
            logs = logs[-50:]

        # ログ保存
        with open(self.decisions_log, "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)

    def get_execution_guidance(
        self, task_description: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """実行ガイダンス取得"""
        decision = self.make_execution_decision(task_description, context)

        guidance = {
            "decision_summary": {
                "complexity": decision.complexity.value,
                "method": decision.execution_method.value,
                "efficiency": f"{decision.efficiency_score:.1%}",
                "time_estimate": f"{decision.estimated_time} minutes",
            },
            "execution_instructions": self._get_execution_instructions(decision),
            "efficiency_notes": self._get_efficiency_notes(decision),
            "president_recommendation": decision.justification,
        }

        return guidance

    def _get_execution_instructions(self, decision: ExecutionDecision) -> List[str]:
        """実行指示生成"""
        instructions = []

        if decision.execution_method == ExecutionMethod.DIRECT:
            instructions = [
                "✅ Proceed with direct execution",
                "🔧 Use standard tools and commands",
                "⚡ Execute immediately without additional planning",
            ]
        elif decision.execution_method == ExecutionMethod.PLANNED:
            instructions = [
                "📋 Create execution plan using TodoWrite",
                "🔄 Break task into manageable steps",
                "✅ Complete each step systematically",
            ]
        elif decision.execution_method == ExecutionMethod.AI_ORGANIZATION:
            instructions = [
                "🤖 Engage AI organization for collaborative execution",
                "💭 Use multiple perspectives for decision making",
                "🔍 Leverage specialized roles for optimal results",
            ]
        elif decision.execution_method == ExecutionMethod.ULTRATHINK:
            instructions = [
                "🧠 Apply deep thinking methodologies",
                "🔬 Consider long-term implications and alternatives",
                "📊 Perform comprehensive analysis before action",
            ]

        return instructions

    def _get_efficiency_notes(self, decision: ExecutionDecision) -> List[str]:
        """効率性ノート生成"""
        notes = []

        if decision.efficiency_score >= 0.8:
            notes.append("🟢 High efficiency task - optimal execution method selected")
        elif decision.efficiency_score >= 0.6:
            notes.append("🟡 Moderate efficiency - balanced approach")
        else:
            notes.append("🔴 Low efficiency task - careful execution required")

        if decision.should_use_ai_org:
            notes.append(
                "🤖 AI organization engagement recommended for quality assurance"
            )
        else:
            notes.append("⚡ Direct execution appropriate - minimal overhead")

        if decision.estimated_time > 60:
            notes.append("⏰ Extended task - consider breaking into smaller parts")

        return notes

    def show_decision_statistics(self) -> Dict[str, Any]:
        """決定統計表示"""
        if not self.decisions_log.exists():
            return {"message": "No decisions logged yet"}

        with open(self.decisions_log, encoding="utf-8") as f:
            logs = json.load(f)

        stats = {
            "total_decisions": len(logs),
            "method_distribution": {},
            "complexity_distribution": {},
            "average_efficiency": 0.0,
            "ai_org_usage_rate": 0.0,
        }

        if not logs:
            return stats

        # 統計計算
        methods = [log["decision"]["execution_method"] for log in logs]
        complexities = [log["decision"]["complexity"] for log in logs]
        efficiencies = [log["decision"]["efficiency_score"] for log in logs]
        ai_org_usage = [log["decision"]["should_use_ai_org"] for log in logs]

        # 分布計算
        for method in methods:
            stats["method_distribution"][method] = (
                stats["method_distribution"].get(method, 0) + 1
            )

        for complexity in complexities:
            stats["complexity_distribution"][complexity] = (
                stats["complexity_distribution"].get(complexity, 0) + 1
            )

        # 平均値計算
        stats["average_efficiency"] = sum(efficiencies) / len(efficiencies)
        stats["ai_org_usage_rate"] = sum(ai_org_usage) / len(ai_org_usage)

        return stats


def main():
    """メイン実行（テスト・デモ用）"""
    president = PresidentConductorSystem()

    test_tasks = [
        ("Show me the git status", {"urgency": "high"}),
        ("Implement a new authentication system", {"critical": True}),
        ("Edit the README file", {}),
        ("Analyze system architecture and recommend improvements", {}),
        ("Fix a simple typo in documentation", {"urgency": "low"}),
        ("Research database solutions for the project", {"previous_mistakes_count": 2}),
    ]

    print("🎯 PRESIDENT/Conductor Decision System Demo")
    print("=" * 60)

    for i, (task, context) in enumerate(test_tasks, 1):
        print(f"\n📝 Task {i}: {task}")
        print(f"🔧 Context: {context}")
        print("-" * 50)

        guidance = president.get_execution_guidance(task, context)

        print(f"🏷️  Decision: {guidance['decision_summary']}")
        print("📋 Instructions:")
        for instruction in guidance["execution_instructions"]:
            print(f"     {instruction}")
        print("📊 Efficiency Notes:")
        for note in guidance["efficiency_notes"]:
            print(f"     {note}")
        print(f"🎯 President Recommendation: {guidance['president_recommendation']}")

    # 統計表示
    print("\n📊 Decision Statistics:")
    print("=" * 30)
    stats = president.show_decision_statistics()
    print(json.dumps(stats, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
