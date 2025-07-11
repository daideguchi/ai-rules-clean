#!/usr/bin/env python3
"""
Reasoning Trace Visualizer
推論トレース可視化システム - 判断過程の完全透明化
スキップステップ検出・根拠明示・ショートカット防止
"""

import datetime
import json
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class ReasoningStep(Enum):
    """推論ステップ"""

    INPUT_ANALYSIS = "input_analysis"
    CONSTRAINT_CHECK = "constraint_check"
    PATTERN_MATCHING = "pattern_matching"
    VERIFICATION = "verification"
    DECISION_MAKING = "decision_making"
    OUTPUT_GENERATION = "output_generation"


class StepStatus(Enum):
    """ステップ状態"""

    COMPLETED = "completed"
    SKIPPED = "skipped"
    FAILED = "failed"
    BYPASSED = "bypassed"


@dataclass
class ReasoningTraceStep:
    """推論トレースステップ"""

    step: ReasoningStep
    status: StepStatus
    timestamp: str
    duration_ms: float
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    reasoning: str
    evidence: List[str]
    skipped_reason: Optional[str] = None
    alternatives_considered: List[str] = None


@dataclass
class ReasoningTrace:
    """推論トレース"""

    trace_id: str
    task_description: str
    start_time: str
    end_time: str
    total_duration_ms: float
    steps: List[ReasoningTraceStep]
    decision_path: List[str]
    skipped_steps: List[str]
    risk_factors: List[str]
    quality_score: float


class ReasoningTraceVisualizer:
    """推論トレース可視化システム"""

    def __init__(self):
        self.base_path = Path("/Users/dd/Desktop/1_dev/coding-rule2")
        self.trace_log = self.base_path / "runtime" / "reasoning_traces.json"
        self.current_trace: Optional[ReasoningTrace] = None
        self.step_start_time: Optional[datetime.datetime] = None

        # 必須推論ステップ定義
        self.required_steps = {
            ReasoningStep.INPUT_ANALYSIS: {
                "description": "入力タスクの複雑度・要件分析",
                "mandatory_for": [
                    "technical_analysis",
                    "system_design",
                    "critical_tasks",
                ],
                "evidence_required": [
                    "complexity_assessment",
                    "requirement_extraction",
                ],
            },
            ReasoningStep.CONSTRAINT_CHECK: {
                "description": "制約・ルール・過去失敗パターンチェック",
                "mandatory_for": ["all_tasks"],
                "evidence_required": [
                    "claude_md_compliance",
                    "constitutional_ai_check",
                    "failure_pattern_check",
                ],
            },
            ReasoningStep.PATTERN_MATCHING: {
                "description": "88回失敗パターンとの照合",
                "mandatory_for": [
                    "github_operations",
                    "repository_actions",
                    "tool_usage",
                ],
                "evidence_required": ["pattern_match_results", "risk_assessment"],
            },
            ReasoningStep.VERIFICATION: {
                "description": "実行前検証・ツール可用性確認",
                "mandatory_for": ["tool_usage", "file_operations", "external_commands"],
                "evidence_required": [
                    "availability_check",
                    "permission_check",
                    "prerequisite_check",
                ],
            },
            ReasoningStep.DECISION_MAKING: {
                "description": "最終判断・代替案検討",
                "mandatory_for": ["all_tasks"],
                "evidence_required": [
                    "decision_rationale",
                    "alternatives_considered",
                    "risk_mitigation",
                ],
            },
        }

        self.trace_log.parent.mkdir(parents=True, exist_ok=True)

    def start_trace(self, task_description: str) -> str:
        """推論トレース開始"""
        trace_id = f"trace_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        self.current_trace = ReasoningTrace(
            trace_id=trace_id,
            task_description=task_description,
            start_time=datetime.datetime.now().isoformat(),
            end_time="",
            total_duration_ms=0.0,
            steps=[],
            decision_path=[],
            skipped_steps=[],
            risk_factors=[],
            quality_score=0.0,
        )

        return trace_id

    def start_step(self, step: ReasoningStep) -> None:
        """推論ステップ開始"""
        self.step_start_time = datetime.datetime.now()

    def complete_step(
        self,
        step: ReasoningStep,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        reasoning: str,
        evidence: List[str],
    ) -> None:
        """推論ステップ完了"""
        if not self.current_trace or not self.step_start_time:
            return

        end_time = datetime.datetime.now()
        duration = (end_time - self.step_start_time).total_seconds() * 1000

        trace_step = ReasoningTraceStep(
            step=step,
            status=StepStatus.COMPLETED,
            timestamp=end_time.isoformat(),
            duration_ms=duration,
            inputs=inputs,
            outputs=outputs,
            reasoning=reasoning,
            evidence=evidence,
            alternatives_considered=outputs.get("alternatives_considered", []),
        )

        self.current_trace.steps.append(trace_step)
        self.current_trace.decision_path.append(f"{step.value}: {reasoning}")

    def skip_step(self, step: ReasoningStep, reason: str) -> None:
        """推論ステップスキップ（問題行動）"""
        if not self.current_trace:
            return

        trace_step = ReasoningTraceStep(
            step=step,
            status=StepStatus.SKIPPED,
            timestamp=datetime.datetime.now().isoformat(),
            duration_ms=0.0,
            inputs={},
            outputs={},
            reasoning=f"SKIPPED: {reason}",
            evidence=[],
            skipped_reason=reason,
        )

        self.current_trace.steps.append(trace_step)
        self.current_trace.skipped_steps.append(f"{step.value}: {reason}")
        self.current_trace.risk_factors.append(f"Critical step skipped: {step.value}")

    def bypass_step(self, step: ReasoningStep, shortcut_reason: str) -> None:
        """推論ステップバイパス（ショートカット）"""
        if not self.current_trace:
            return

        trace_step = ReasoningTraceStep(
            step=step,
            status=StepStatus.BYPASSED,
            timestamp=datetime.datetime.now().isoformat(),
            duration_ms=0.0,
            inputs={},
            outputs={},
            reasoning=f"BYPASSED: {shortcut_reason}",
            evidence=[],
            skipped_reason=shortcut_reason,
        )

        self.current_trace.steps.append(trace_step)
        self.current_trace.skipped_steps.append(
            f"{step.value}: BYPASSED - {shortcut_reason}"
        )
        self.current_trace.risk_factors.append(f"Shortcut taken: {step.value}")

    def end_trace(self) -> ReasoningTrace:
        """推論トレース終了"""
        if not self.current_trace:
            return None

        self.current_trace.end_time = datetime.datetime.now().isoformat()

        # 品質スコア計算
        self.current_trace.quality_score = self._calculate_quality_score()

        # 総所要時間計算
        start_dt = datetime.datetime.fromisoformat(self.current_trace.start_time)
        end_dt = datetime.datetime.fromisoformat(self.current_trace.end_time)
        self.current_trace.total_duration_ms = (
            end_dt - start_dt
        ).total_seconds() * 1000

        # ログ保存
        self._save_trace()

        completed_trace = self.current_trace
        self.current_trace = None

        return completed_trace

    def _calculate_quality_score(self) -> float:
        """推論品質スコア計算"""
        if not self.current_trace:
            return 0.0

        total_possible_steps = len(self.required_steps)
        completed_steps = len(
            [s for s in self.current_trace.steps if s.status == StepStatus.COMPLETED]
        )
        skipped_steps = len(
            [
                s
                for s in self.current_trace.steps
                if s.status in [StepStatus.SKIPPED, StepStatus.BYPASSED]
            ]
        )

        # 基本品質スコア
        completion_rate = (
            completed_steps / total_possible_steps if total_possible_steps > 0 else 0
        )

        # ペナルティ
        skip_penalty = skipped_steps * 0.2
        risk_penalty = len(self.current_trace.risk_factors) * 0.1

        # 品質スコア
        quality_score = max(0.0, completion_rate - skip_penalty - risk_penalty)

        return min(1.0, quality_score)

    def analyze_trace(self, trace: ReasoningTrace) -> Dict[str, Any]:
        """推論トレース分析"""
        analysis = {
            "trace_id": trace.trace_id,
            "quality_assessment": {
                "overall_quality": trace.quality_score,
                "quality_level": self._get_quality_level(trace.quality_score),
                "completed_steps": len(
                    [s for s in trace.steps if s.status == StepStatus.COMPLETED]
                ),
                "skipped_steps": len(
                    [
                        s
                        for s in trace.steps
                        if s.status in [StepStatus.SKIPPED, StepStatus.BYPASSED]
                    ]
                ),
                "total_risk_factors": len(trace.risk_factors),
            },
            "step_analysis": {},
            "problem_detection": {
                "critical_skips": [],
                "shortcuts_taken": [],
                "missing_evidence": [],
                "insufficient_reasoning": [],
            },
            "improvement_recommendations": [],
        }

        # ステップ分析
        for step_type in ReasoningStep:
            step_data = [s for s in trace.steps if s.step == step_type]

            if step_data:
                step_info = step_data[0]  # 最初のステップ
                analysis["step_analysis"][step_type.value] = {
                    "status": step_info.status.value,
                    "duration_ms": step_info.duration_ms,
                    "evidence_count": len(step_info.evidence),
                    "reasoning_length": len(step_info.reasoning),
                    "alternatives_considered": len(
                        step_info.alternatives_considered or []
                    ),
                }

                # 問題検出
                if step_info.status == StepStatus.SKIPPED:
                    analysis["problem_detection"]["critical_skips"].append(
                        {"step": step_type.value, "reason": step_info.skipped_reason}
                    )
                elif step_info.status == StepStatus.BYPASSED:
                    analysis["problem_detection"]["shortcuts_taken"].append(
                        {
                            "step": step_type.value,
                            "shortcut_reason": step_info.skipped_reason,
                        }
                    )

                if len(step_info.evidence) == 0:
                    analysis["problem_detection"]["missing_evidence"].append(
                        step_type.value
                    )

                if len(step_info.reasoning) < 20:
                    analysis["problem_detection"]["insufficient_reasoning"].append(
                        step_type.value
                    )
            else:
                analysis["step_analysis"][step_type.value] = {
                    "status": "not_performed",
                    "duration_ms": 0,
                    "evidence_count": 0,
                    "reasoning_length": 0,
                    "alternatives_considered": 0,
                }
                analysis["problem_detection"]["critical_skips"].append(
                    {"step": step_type.value, "reason": "Step completely omitted"}
                )

        # 改善推奨事項生成
        analysis["improvement_recommendations"] = self._generate_recommendations(
            analysis
        )

        return analysis

    def _get_quality_level(self, score: float) -> str:
        """品質レベル取得"""
        if score >= 0.9:
            return "EXCELLENT"
        elif score >= 0.7:
            return "GOOD"
        elif score >= 0.5:
            return "ACCEPTABLE"
        elif score >= 0.3:
            return "POOR"
        else:
            return "UNACCEPTABLE"

    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """改善推奨事項生成"""
        recommendations = []

        problem_detection = analysis["problem_detection"]

        if problem_detection["critical_skips"]:
            recommendations.append(
                "Critical steps were skipped - implement mandatory step enforcement"
            )

        if problem_detection["shortcuts_taken"]:
            recommendations.append(
                "Shortcuts detected - strengthen reasoning process discipline"
            )

        if problem_detection["missing_evidence"]:
            recommendations.append(
                "Evidence collection insufficient - require proof for all claims"
            )

        if problem_detection["insufficient_reasoning"]:
            recommendations.append(
                "Reasoning depth inadequate - expand decision rationale requirements"
            )

        if analysis["quality_assessment"]["overall_quality"] < 0.5:
            recommendations.append(
                "Overall quality unacceptable - implement realtime feedback enforcement"
            )

        return recommendations

    def visualize_trace(self, trace: ReasoningTrace) -> str:
        """推論トレース可視化"""
        visualization = []

        visualization.append(f"🧠 Reasoning Trace: {trace.trace_id}")
        visualization.append(f"📝 Task: {trace.task_description}")
        visualization.append(f"⏱️ Duration: {trace.total_duration_ms:.1f}ms")
        visualization.append(
            f"🎯 Quality: {trace.quality_score:.2f} ({self._get_quality_level(trace.quality_score)})"
        )
        visualization.append("")

        visualization.append("📊 Step Analysis:")
        for i, step in enumerate(trace.steps, 1):
            status_icon = {
                StepStatus.COMPLETED: "✅",
                StepStatus.SKIPPED: "⏭️",
                StepStatus.FAILED: "❌",
                StepStatus.BYPASSED: "🔀",
            }[step.status]

            visualization.append(f"  {i}. {status_icon} {step.step.value}")
            visualization.append(f"     Time: {step.duration_ms:.1f}ms")
            visualization.append(f"     Reasoning: {step.reasoning}")
            if step.evidence:
                visualization.append(f"     Evidence: {', '.join(step.evidence[:3])}")
            visualization.append("")

        if trace.skipped_steps:
            visualization.append("⚠️ Skipped Steps:")
            for skip in trace.skipped_steps:
                visualization.append(f"  - {skip}")
            visualization.append("")

        if trace.risk_factors:
            visualization.append("🚨 Risk Factors:")
            for risk in trace.risk_factors:
                visualization.append(f"  - {risk}")
            visualization.append("")

        return "\n".join(visualization)

    def _save_trace(self):
        """トレース保存"""
        if not self.current_trace:
            return

        traces = []

        if self.trace_log.exists():
            try:
                with open(self.trace_log, encoding="utf-8") as f:
                    traces = json.load(f)
            except Exception:
                traces = []

        traces.append(asdict(self.current_trace))

        # 最新20件のみ保持
        if len(traces) > 20:
            traces = traces[-20:]

        with open(self.trace_log, "w", encoding="utf-8") as f:
            json.dump(traces, f, ensure_ascii=False, indent=2, default=str)


def main():
    """メイン実行（テスト用）"""
    visualizer = ReasoningTraceVisualizer()

    print("🧠 Reasoning Trace Visualizer Test")
    print("=" * 60)

    # テストトレース
    visualizer.start_trace(
        "Implement GitHub repository creation with proper verification"
    )

    # 良い推論例
    visualizer.start_step(ReasoningStep.INPUT_ANALYSIS)
    visualizer.complete_step(
        ReasoningStep.INPUT_ANALYSIS,
        {"task": "GitHub repo creation"},
        {"complexity": "medium", "verification_required": True},
        "Analyzed task complexity and identified verification requirements",
        ["complexity_assessment", "requirement_extraction"],
    )

    # 悪い推論例（スキップ）
    visualizer.skip_step(
        ReasoningStep.VERIFICATION, "Assumed GitHub CLI not available without checking"
    )

    # 推論終了
    completed_trace = visualizer.end_trace()

    # 分析・可視化
    analysis = visualizer.analyze_trace(completed_trace)
    visualization = visualizer.visualize_trace(completed_trace)

    print(visualization)
    print("\n📊 Analysis Summary:")
    print(f"Quality: {analysis['quality_assessment']['quality_level']}")
    print(
        f"Problems: {len(analysis['problem_detection']['critical_skips'])} skips, {len(analysis['problem_detection']['shortcuts_taken'])} shortcuts"
    )


if __name__ == "__main__":
    main()
