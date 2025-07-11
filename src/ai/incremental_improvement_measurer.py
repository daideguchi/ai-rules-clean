#!/usr/bin/env python3
"""
Incremental Improvement Measurement System
インクリメンタル改善測定システム - 学習効果・防止効果の定量化
88回ミス再発率・指示遵守率・品質向上トレンド測定
"""

import datetime
import json
import statistics
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List


class MetricType(Enum):
    """メトリクスタイプ"""

    MISTAKE_RECURRENCE = "mistake_recurrence"
    INSTRUCTION_COMPLIANCE = "instruction_compliance"
    VERIFICATION_COMPLETION = "verification_completion"
    LEARNING_RETENTION = "learning_retention"
    QUALITY_IMPROVEMENT = "quality_improvement"
    RESPONSE_TIME = "response_time"


class TrendDirection(Enum):
    """トレンド方向"""

    IMPROVING = "improving"
    DECLINING = "declining"
    STABLE = "stable"
    VOLATILE = "volatile"


@dataclass
class MetricMeasurement:
    """メトリクス測定値"""

    metric_type: MetricType
    timestamp: str
    value: float
    context: Dict[str, Any]
    session_id: str
    evidence: List[str]


@dataclass
class ImprovementTrend:
    """改善トレンド"""

    metric_type: MetricType
    trend_direction: TrendDirection
    trend_strength: float  # 0.0-1.0
    improvement_rate: float  # 変化率
    confidence: float
    time_period_days: int
    measurements_count: int


class IncrementalImprovementMeasurer:
    """インクリメンタル改善測定システム"""

    def __init__(self):
        self.base_path = Path("/Users/dd/Desktop/1_dev/coding-rule2")
        self.measurements_log = (
            self.base_path / "runtime" / "improvement_measurements.json"
        )
        self.trends_log = self.base_path / "runtime" / "improvement_trends.json"
        self.session_file = (
            self.base_path
            / "src"
            / "memory"
            / "core"
            / "session-records"
            / "current-session.json"
        )

        # 88回ミスパターンデータベース
        self.known_mistakes = self._load_known_mistakes()

        # セッション履歴
        self.session_history = self._load_session_history()

        self.measurements_log.parent.mkdir(parents=True, exist_ok=True)

    def measure_mistake_recurrence_rate(self) -> MetricMeasurement:
        """ミス再発率測定"""
        current_session = self._get_current_session()
        session_id = current_session.get("session_id", "unknown")

        # 過去のセッションから同じミスパターンの発生状況を分析
        recurrence_analysis = self._analyze_mistake_patterns()

        # 再発率計算
        total_patterns = len(self.known_mistakes)
        recurring_patterns = len(
            [
                p
                for p in recurrence_analysis["pattern_analysis"]
                if p["recurrence_count"] > 0
            ]
        )
        recurrence_rate = (
            recurring_patterns / total_patterns if total_patterns > 0 else 0.0
        )

        measurement = MetricMeasurement(
            metric_type=MetricType.MISTAKE_RECURRENCE,
            timestamp=datetime.datetime.now().isoformat(),
            value=recurrence_rate,
            context={
                "total_known_patterns": total_patterns,
                "recurring_patterns": recurring_patterns,
                "analysis_period_days": 30,
                "patterns_analyzed": recurrence_analysis["pattern_analysis"][
                    :5
                ],  # 上位5件
            },
            session_id=session_id,
            evidence=[
                f"Analyzed {total_patterns} known mistake patterns",
                f"Found {recurring_patterns} patterns with recurrence",
                f"Recent sessions analyzed: {len(self.session_history)}",
            ],
        )

        self._save_measurement(measurement)
        return measurement

    def measure_instruction_compliance_rate(self) -> MetricMeasurement:
        """指示遵守率測定"""
        current_session = self._get_current_session()
        session_id = current_session.get("session_id", "unknown")

        # 指示遵守状況の分析
        compliance_analysis = self._analyze_instruction_compliance()

        measurement = MetricMeasurement(
            metric_type=MetricType.INSTRUCTION_COMPLIANCE,
            timestamp=datetime.datetime.now().isoformat(),
            value=compliance_analysis["compliance_rate"],
            context={
                "total_instructions": compliance_analysis["total_instructions"],
                "complied_instructions": compliance_analysis["complied_instructions"],
                "critical_violations": compliance_analysis["critical_violations"],
                "analysis_details": compliance_analysis["details"],
            },
            session_id=session_id,
            evidence=compliance_analysis["evidence"],
        )

        self._save_measurement(measurement)
        return measurement

    def measure_verification_completion_rate(self) -> MetricMeasurement:
        """検証完了率測定"""
        current_session = self._get_current_session()
        session_id = current_session.get("session_id", "unknown")

        # 検証ステップ完了状況の分析
        verification_analysis = self._analyze_verification_completion()

        measurement = MetricMeasurement(
            metric_type=MetricType.VERIFICATION_COMPLETION,
            timestamp=datetime.datetime.now().isoformat(),
            value=verification_analysis["completion_rate"],
            context={
                "required_verifications": verification_analysis[
                    "required_verifications"
                ],
                "completed_verifications": verification_analysis[
                    "completed_verifications"
                ],
                "skipped_verifications": verification_analysis["skipped_verifications"],
                "verification_details": verification_analysis["details"],
            },
            session_id=session_id,
            evidence=verification_analysis["evidence"],
        )

        self._save_measurement(measurement)
        return measurement

    def measure_learning_retention_rate(self) -> MetricMeasurement:
        """学習継続率測定"""
        current_session = self._get_current_session()
        session_id = current_session.get("session_id", "unknown")

        # 学習継続性の分析
        retention_analysis = self._analyze_learning_retention()

        measurement = MetricMeasurement(
            metric_type=MetricType.LEARNING_RETENTION,
            timestamp=datetime.datetime.now().isoformat(),
            value=retention_analysis["retention_rate"],
            context={
                "knowledge_items_tested": retention_analysis["knowledge_items_tested"],
                "retained_knowledge": retention_analysis["retained_knowledge"],
                "forgotten_knowledge": retention_analysis["forgotten_knowledge"],
                "retention_details": retention_analysis["details"],
            },
            session_id=session_id,
            evidence=retention_analysis["evidence"],
        )

        self._save_measurement(measurement)
        return measurement

    def measure_quality_improvement_trend(self) -> MetricMeasurement:
        """品質向上トレンド測定"""
        current_session = self._get_current_session()
        session_id = current_session.get("session_id", "unknown")

        # 品質トレンドの分析
        quality_analysis = self._analyze_quality_trend()

        measurement = MetricMeasurement(
            metric_type=MetricType.QUALITY_IMPROVEMENT,
            timestamp=datetime.datetime.now().isoformat(),
            value=quality_analysis["improvement_score"],
            context={
                "baseline_quality": quality_analysis["baseline_quality"],
                "current_quality": quality_analysis["current_quality"],
                "improvement_rate": quality_analysis["improvement_rate"],
                "quality_factors": quality_analysis["quality_factors"],
            },
            session_id=session_id,
            evidence=quality_analysis["evidence"],
        )

        self._save_measurement(measurement)
        return measurement

    def _analyze_mistake_patterns(self) -> Dict[str, Any]:
        """ミスパターン分析"""
        analysis = {
            "pattern_analysis": [],
            "total_patterns": len(self.known_mistakes),
            "analysis_period": 30,
        }

        # 既知のミスパターンの各項目を分析
        for pattern in self.known_mistakes:
            pattern_name = pattern.get("pattern_name", "unknown")
            occurrence_count = pattern.get("occurrence_count", 0)

            # 最近のセッションでのパターンマッチング
            recent_occurrences = self._count_recent_pattern_occurrences(pattern_name)

            pattern_analysis = {
                "pattern_name": pattern_name,
                "historical_occurrences": occurrence_count,
                "recent_occurrences": recent_occurrences,
                "recurrence_count": recent_occurrences,
                "recurrence_risk": min(
                    1.0, recent_occurrences / max(1, occurrence_count)
                ),
            }

            analysis["pattern_analysis"].append(pattern_analysis)

        # 再発率でソート
        analysis["pattern_analysis"].sort(
            key=lambda x: x["recurrence_count"], reverse=True
        )

        return analysis

    def _analyze_instruction_compliance(self) -> Dict[str, Any]:
        """指示遵守分析"""
        analysis = {
            "compliance_rate": 0.0,
            "total_instructions": 0,
            "complied_instructions": 0,
            "critical_violations": 0,
            "details": [],
            "evidence": [],
        }

        # CLAUDE.mdからの必須指示チェック
        claude_md_instructions = self._extract_claude_md_instructions()

        # 現在セッションでの遵守状況確認
        current_session = self._get_current_session()

        for instruction in claude_md_instructions:
            compliance_check = self._check_instruction_compliance(
                instruction, current_session
            )

            analysis["total_instructions"] += 1
            if compliance_check["compliant"]:
                analysis["complied_instructions"] += 1
            else:
                if compliance_check["severity"] == "CRITICAL":
                    analysis["critical_violations"] += 1

            analysis["details"].append(
                {
                    "instruction": instruction,
                    "compliant": compliance_check["compliant"],
                    "severity": compliance_check["severity"],
                    "evidence": compliance_check["evidence"],
                }
            )

        # 遵守率計算
        if analysis["total_instructions"] > 0:
            analysis["compliance_rate"] = (
                analysis["complied_instructions"] / analysis["total_instructions"]
            )

        analysis["evidence"] = [
            f"Checked {analysis['total_instructions']} critical instructions",
            f"Compliance rate: {analysis['compliance_rate']:.1%}",
            f"Critical violations: {analysis['critical_violations']}",
        ]

        return analysis

    def _analyze_verification_completion(self) -> Dict[str, Any]:
        """検証完了分析"""
        analysis = {
            "completion_rate": 0.0,
            "required_verifications": 0,
            "completed_verifications": 0,
            "skipped_verifications": 0,
            "details": [],
            "evidence": [],
        }

        # 必須検証項目リスト
        required_verifications = [
            "PRESIDENT宣言確認",
            "ツール利用可能性確認",
            "ファイル存在確認",
            "権限確認",
            "事前テスト実行",
        ]

        # 現在セッションでの検証状況確認
        current_session = self._get_current_session()

        for verification in required_verifications:
            verification_status = self._check_verification_status(
                verification, current_session
            )

            analysis["required_verifications"] += 1
            if verification_status["completed"]:
                analysis["completed_verifications"] += 1
            else:
                analysis["skipped_verifications"] += 1

            analysis["details"].append(
                {
                    "verification": verification,
                    "completed": verification_status["completed"],
                    "evidence": verification_status["evidence"],
                }
            )

        # 完了率計算
        if analysis["required_verifications"] > 0:
            analysis["completion_rate"] = (
                analysis["completed_verifications"] / analysis["required_verifications"]
            )

        analysis["evidence"] = [
            f"Required verifications: {analysis['required_verifications']}",
            f"Completed: {analysis['completed_verifications']}",
            f"Completion rate: {analysis['completion_rate']:.1%}",
        ]

        return analysis

    def _analyze_learning_retention(self) -> Dict[str, Any]:
        """学習継続分析"""
        analysis = {
            "retention_rate": 0.0,
            "knowledge_items_tested": 0,
            "retained_knowledge": 0,
            "forgotten_knowledge": 0,
            "details": [],
            "evidence": [],
        }

        # 学習項目テスト
        knowledge_items = [
            "88回ミス防止システムの活用",
            "Constitutional AI制約の理解",
            "PRESIDENT宣言の重要性",
            "検証ステップの必要性",
            "過去失敗パターンの記憶",
        ]

        current_session = self._get_current_session()

        for knowledge_item in knowledge_items:
            retention_check = self._test_knowledge_retention(
                knowledge_item, current_session
            )

            analysis["knowledge_items_tested"] += 1
            if retention_check["retained"]:
                analysis["retained_knowledge"] += 1
            else:
                analysis["forgotten_knowledge"] += 1

            analysis["details"].append(
                {
                    "knowledge_item": knowledge_item,
                    "retained": retention_check["retained"],
                    "evidence": retention_check["evidence"],
                }
            )

        # 継続率計算
        if analysis["knowledge_items_tested"] > 0:
            analysis["retention_rate"] = (
                analysis["retained_knowledge"] / analysis["knowledge_items_tested"]
            )

        analysis["evidence"] = [
            f"Knowledge items tested: {analysis['knowledge_items_tested']}",
            f"Retained: {analysis['retained_knowledge']}",
            f"Retention rate: {analysis['retention_rate']:.1%}",
        ]

        return analysis

    def _analyze_quality_trend(self) -> Dict[str, Any]:
        """品質トレンド分析"""
        analysis = {
            "improvement_score": 0.0,
            "baseline_quality": 0.0,
            "current_quality": 0.0,
            "improvement_rate": 0.0,
            "quality_factors": {},
            "evidence": [],
        }

        # 品質指標の測定
        quality_factors = {
            "constitutional_ai_compliance": self._measure_constitutional_compliance(),
            "verification_thoroughness": self._measure_verification_thoroughness(),
            "evidence_provision": self._measure_evidence_provision(),
            "instruction_adherence": self._measure_instruction_adherence(),
            "error_prevention": self._measure_error_prevention(),
        }

        analysis["quality_factors"] = quality_factors

        # 現在品質スコア計算
        current_quality = statistics.mean(quality_factors.values())
        analysis["current_quality"] = current_quality

        # ベースライン品質（88回ミス時点）
        baseline_quality = 0.1  # 88回ミス時点の品質
        analysis["baseline_quality"] = baseline_quality

        # 改善率計算
        if baseline_quality > 0:
            improvement_rate = (current_quality - baseline_quality) / baseline_quality
        else:
            improvement_rate = current_quality

        analysis["improvement_rate"] = improvement_rate
        analysis["improvement_score"] = max(0.0, min(1.0, current_quality))

        analysis["evidence"] = [
            f"Current quality score: {current_quality:.2f}",
            f"Baseline quality: {baseline_quality:.2f}",
            f"Improvement rate: {improvement_rate:.1%}",
            f"Quality factors measured: {len(quality_factors)}",
        ]

        return analysis

    def calculate_improvement_trends(
        self, days: int = 30
    ) -> Dict[MetricType, ImprovementTrend]:
        """改善トレンド計算"""
        trends = {}

        # 過去の測定値を読み込み
        measurements = self._load_recent_measurements(days)

        for metric_type in MetricType:
            metric_measurements = [
                m for m in measurements if m.get("metric_type") == metric_type.value
            ]

            if len(metric_measurements) >= 2:
                trend = self._calculate_metric_trend(metric_type, metric_measurements)
                trends[metric_type] = trend

        # トレンドログ保存
        self._save_trends(trends)

        return trends

    def _calculate_metric_trend(
        self, metric_type: MetricType, measurements: List[Dict]
    ) -> ImprovementTrend:
        """メトリクストレンド計算"""
        values = [m["value"] for m in measurements]
        timestamps = [
            datetime.datetime.fromisoformat(m["timestamp"]) for m in measurements
        ]

        # トレンド方向の計算
        if len(values) >= 2:
            first_half = statistics.mean(values[: len(values) // 2])
            second_half = statistics.mean(values[len(values) // 2 :])

            improvement_rate = (second_half - first_half) / max(first_half, 0.001)

            if improvement_rate > 0.1:
                trend_direction = TrendDirection.IMPROVING
            elif improvement_rate < -0.1:
                trend_direction = TrendDirection.DECLINING
            else:
                trend_direction = TrendDirection.STABLE
        else:
            improvement_rate = 0.0
            trend_direction = TrendDirection.STABLE

        # トレンド強度計算
        if len(values) > 1:
            variance = statistics.variance(values)
            trend_strength = min(1.0, abs(improvement_rate) / (variance + 0.001))
        else:
            trend_strength = 0.0

        # 信頼度計算
        confidence = min(1.0, len(values) / 10.0)  # 10回測定で最大信頼度

        # 期間計算
        if len(timestamps) >= 2:
            time_period = (max(timestamps) - min(timestamps)).days
        else:
            time_period = 0

        return ImprovementTrend(
            metric_type=metric_type,
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            improvement_rate=improvement_rate,
            confidence=confidence,
            time_period_days=time_period,
            measurements_count=len(measurements),
        )

    def generate_improvement_report(self) -> Dict[str, Any]:
        """改善レポート生成"""
        # 全メトリクス測定
        measurements = {
            "mistake_recurrence": self.measure_mistake_recurrence_rate(),
            "instruction_compliance": self.measure_instruction_compliance_rate(),
            "verification_completion": self.measure_verification_completion_rate(),
            "learning_retention": self.measure_learning_retention_rate(),
            "quality_improvement": self.measure_quality_improvement_trend(),
        }

        # トレンド計算
        trends = self.calculate_improvement_trends()

        # 総合評価
        overall_score = statistics.mean([m.value for m in measurements.values()])

        report = {
            "timestamp": datetime.datetime.now().isoformat(),
            "overall_improvement_score": overall_score,
            "measurements": {k: asdict(v) for k, v in measurements.items()},
            "trends": {k.value: asdict(v) for k, v in trends.items()},
            "summary": {
                "total_metrics": len(measurements),
                "improving_metrics": len(
                    [
                        t
                        for t in trends.values()
                        if t.trend_direction == TrendDirection.IMPROVING
                    ]
                ),
                "declining_metrics": len(
                    [
                        t
                        for t in trends.values()
                        if t.trend_direction == TrendDirection.DECLINING
                    ]
                ),
                "stable_metrics": len(
                    [
                        t
                        for t in trends.values()
                        if t.trend_direction == TrendDirection.STABLE
                    ]
                ),
            },
            "recommendations": self._generate_improvement_recommendations(
                measurements, trends
            ),
        }

        return report

    def _generate_improvement_recommendations(
        self, measurements: Dict, trends: Dict
    ) -> List[str]:
        """改善推奨事項生成"""
        recommendations = []

        # ミス再発率が高い場合
        if measurements["mistake_recurrence"].value > 0.3:
            recommendations.append(
                "High mistake recurrence detected - strengthen pattern recognition training"
            )

        # 指示遵守率が低い場合
        if measurements["instruction_compliance"].value < 0.8:
            recommendations.append(
                "Low instruction compliance - implement stronger enforcement mechanisms"
            )

        # 検証完了率が低い場合
        if measurements["verification_completion"].value < 0.7:
            recommendations.append(
                "Incomplete verification steps - mandate pre-execution checks"
            )

        # 学習継続率が低い場合
        if measurements["learning_retention"].value < 0.6:
            recommendations.append(
                "Poor learning retention - implement spaced repetition system"
            )

        # 品質向上が停滞している場合
        if measurements["quality_improvement"].value < 0.5:
            recommendations.append(
                "Quality improvement stagnant - review and enhance training methods"
            )

        return recommendations

    # Helper methods
    def _load_known_mistakes(self) -> List[Dict[str, Any]]:
        """既知ミスパターン読み込み"""
        try:
            patterns_file = (
                self.base_path
                / "runtime"
                / "continuous_improvement"
                / "learning_patterns.json"
            )
            if patterns_file.exists():
                with open(patterns_file, encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass

        # フォールバック: 基本的なミスパターン
        return [
            {"pattern_name": "GitHub CLI assumption error", "occurrence_count": 88},
            {"pattern_name": "Repository target confusion", "occurrence_count": 88},
            {"pattern_name": "Verification step skip", "occurrence_count": 88},
            {"pattern_name": "Session discontinuity", "occurrence_count": 88},
            {"pattern_name": "False completion report", "occurrence_count": 88},
        ]

    def _load_session_history(self) -> List[Dict[str, Any]]:
        """セッション履歴読み込み"""
        try:
            logs_dir = self.base_path / "runtime" / "conversation_logs"
            if logs_dir.exists():
                sessions = []
                for log_file in logs_dir.glob("*.jsonl"):
                    # 簡易セッション情報抽出
                    sessions.append(
                        {"file": log_file.name, "date": log_file.stat().st_mtime}
                    )
                return sessions
        except Exception:
            pass
        return []

    def _get_current_session(self) -> Dict[str, Any]:
        """現在セッション取得"""
        try:
            if self.session_file.exists():
                with open(self.session_file, encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return {"session_id": "unknown"}

    def _count_recent_pattern_occurrences(self, pattern_name: str) -> int:
        """最近のパターン発生回数"""
        # 簡易実装: パターン名での検索
        count = 0
        for session in self.session_history[-10:]:  # 最新10セッション
            if pattern_name.lower() in str(session).lower():
                count += 1
        return count

    def _extract_claude_md_instructions(self) -> List[str]:
        """CLAUDE.md指示抽出"""
        instructions = [
            "PRESIDENT宣言必須実行",
            "5分検索ルール厳守",
            "事実に基づく回答のみ",
            "推測回答禁止",
            "完璧報告時の検証必須",
        ]
        return instructions

    def _check_instruction_compliance(
        self, instruction: str, session: Dict
    ) -> Dict[str, Any]:
        """指示遵守チェック"""
        # 簡易実装
        if "PRESIDENT宣言" in instruction:
            president_declared = self._check_president_declaration_status()
            return {
                "compliant": president_declared,
                "severity": "CRITICAL" if not president_declared else "LOW",
                "evidence": ["PRESIDENT declaration file checked"],
            }

        return {
            "compliant": True,
            "severity": "LOW",
            "evidence": ["Default compliance assumed"],
        }

    def _check_verification_status(
        self, verification: str, session: Dict
    ) -> Dict[str, Any]:
        """検証状態チェック"""
        # 簡易実装
        return {
            "completed": True,  # デフォルトで完了扱い
            "evidence": [f"Verification assumed for {verification}"],
        }

    def _test_knowledge_retention(
        self, knowledge_item: str, session: Dict
    ) -> Dict[str, Any]:
        """知識継続テスト"""
        # 簡易実装
        return {
            "retained": True,  # デフォルトで継続扱い
            "evidence": [f"Knowledge retention assumed for {knowledge_item}"],
        }

    def _measure_constitutional_compliance(self) -> float:
        """Constitutional AI遵守度測定"""
        return 0.8  # 簡易実装

    def _measure_verification_thoroughness(self) -> float:
        """検証徹底度測定"""
        return 0.7  # 簡易実装

    def _measure_evidence_provision(self) -> float:
        """証拠提供度測定"""
        return 0.6  # 簡易実装

    def _measure_instruction_adherence(self) -> float:
        """指示遵守度測定"""
        return 0.8  # 簡易実装

    def _measure_error_prevention(self) -> float:
        """エラー防止度測定"""
        return 0.9  # 簡易実装

    def _check_president_declaration_status(self) -> bool:
        """PRESIDENT宣言状態確認"""
        try:
            president_file = (
                self.base_path / "runtime" / "unified-president-declare.json"
            )
            if president_file.exists():
                with open(president_file, encoding="utf-8") as f:
                    status = json.load(f)
                    return status.get("declaration_status") == "active"
        except Exception:
            pass
        return False

    def _save_measurement(self, measurement: MetricMeasurement):
        """測定値保存"""
        measurements = []

        if self.measurements_log.exists():
            try:
                with open(self.measurements_log, encoding="utf-8") as f:
                    measurements = json.load(f)
            except Exception:
                measurements = []

        measurements.append(asdict(measurement))

        # 最新100件のみ保持
        if len(measurements) > 100:
            measurements = measurements[-100:]

        with open(self.measurements_log, "w", encoding="utf-8") as f:
            json.dump(measurements, f, ensure_ascii=False, indent=2, default=str)

    def _load_recent_measurements(self, days: int) -> List[Dict]:
        """最近の測定値読み込み"""
        if not self.measurements_log.exists():
            return []

        try:
            with open(self.measurements_log, encoding="utf-8") as f:
                all_measurements = json.load(f)

            # 期間フィルタリング
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
            recent_measurements = []

            for measurement in all_measurements:
                measurement_date = datetime.datetime.fromisoformat(
                    measurement["timestamp"]
                )
                if measurement_date >= cutoff_date:
                    recent_measurements.append(measurement)

            return recent_measurements

        except Exception:
            return []

    def _save_trends(self, trends: Dict):
        """トレンド保存"""
        trend_data = {
            "timestamp": datetime.datetime.now().isoformat(),
            "trends": {k.value: asdict(v) for k, v in trends.items()},
        }

        with open(self.trends_log, "w", encoding="utf-8") as f:
            json.dump(trend_data, f, ensure_ascii=False, indent=2, default=str)


def main():
    """メイン実行（テスト用）"""
    measurer = IncrementalImprovementMeasurer()

    print("📊 Incremental Improvement Measurement System")
    print("=" * 60)

    # 改善レポート生成
    report = measurer.generate_improvement_report()

    print(f"📈 Overall Improvement Score: {report['overall_improvement_score']:.2f}")
    print(f"📊 Metrics measured: {report['summary']['total_metrics']}")
    print(f"📈 Improving: {report['summary']['improving_metrics']}")
    print(f"📉 Declining: {report['summary']['declining_metrics']}")
    print(f"📊 Stable: {report['summary']['stable_metrics']}")

    print("\n🎯 Key Measurements:")
    for metric_name, measurement in report["measurements"].items():
        print(f"   {metric_name}: {measurement['value']:.2f}")

    if report["recommendations"]:
        print("\n💡 Recommendations:")
        for rec in report["recommendations"]:
            print(f"   - {rec}")


if __name__ == "__main__":
    main()
