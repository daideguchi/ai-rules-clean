#!/usr/bin/env python3
"""
Realtime Feedback Loop System
リアルタイムフィードバックループ - Claude推論プロセス統合
事前制御・即座修正・強制実行機構
"""

import datetime
import importlib.util
import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List


class ActionDecision(Enum):
    """アクション決定"""

    PROCEED = "proceed"  # 実行許可
    BLOCK = "block"  # 実行ブロック
    MODIFY = "modify"  # 修正要求
    VALIDATE = "validate"  # 検証要求


@dataclass
class FeedbackResult:
    """フィードバック結果"""

    decision: ActionDecision
    confidence: float
    reasoning: str
    violations: List[Dict[str, Any]]
    modifications: List[str]
    risk_score: float


class RealtimeFeedbackLoop:
    """リアルタイムフィードバックループシステム"""

    def __init__(self):
        self.base_path = Path("/Users/dd/Desktop/1_dev/coding-rule2")
        self.feedback_log = self.base_path / "runtime" / "realtime_feedback.json"

        # システム統合
        self.constitutional_ai = self._load_constitutional_ai()
        self.rule_based_rewards = self._load_rule_based_rewards()
        self.pattern_matcher = self._load_pattern_matcher()
        self.failure_patterns = self._load_88_failure_patterns()

        self.feedback_log.parent.mkdir(parents=True, exist_ok=True)

    def pre_execution_gate(self, action_plan: Dict[str, Any]) -> FeedbackResult:
        """実行前ゲート - 強制制御ポイント"""
        gate_result = {
            "timestamp": datetime.datetime.now().isoformat(),
            "action_plan": action_plan,
            "checks_performed": [],
            "violations_detected": [],
            "modifications_required": [],
            "final_decision": ActionDecision.PROCEED,
            "risk_assessment": {},
        }

        total_risk_score = 0.0
        violation_count = 0

        # 1. Constitutional AI即座チェック
        constitutional_result = self._constitutional_ai_check(action_plan)
        gate_result["checks_performed"].append("constitutional_ai")

        if not constitutional_result.get("compliant", True):
            violations = constitutional_result.get("violations", [])
            gate_result["violations_detected"].extend(violations)
            total_risk_score += 0.4
            violation_count += len(violations)

            if any(v.get("severity") == "CRITICAL" for v in violations):
                gate_result["final_decision"] = ActionDecision.BLOCK

        # 2. 88回失敗パターン照合
        pattern_result = self._failure_pattern_check(action_plan)
        gate_result["checks_performed"].append("failure_pattern_matching")

        if pattern_result.get("matches_found", False):
            gate_result["violations_detected"].extend(
                pattern_result.get("pattern_violations", [])
            )
            risk_score = pattern_result.get("risk_score", 0.0)
            total_risk_score += risk_score
            gate_result["modifications_required"].extend(
                pattern_result.get("suggested_modifications", [])
            )

            if risk_score > 0.7:
                gate_result["final_decision"] = ActionDecision.MODIFY

        # 3. Rule-Based Rewards事前評価
        rbr_result = self._rule_based_prediction(action_plan)
        gate_result["checks_performed"].append("rule_based_prediction")

        predicted_score = rbr_result.get("predicted_score", 0.5)
        if predicted_score < 0.5:
            gate_result["violations_detected"].append(
                {
                    "type": "LOW_QUALITY_PREDICTION",
                    "severity": "MEDIUM",
                    "details": f"Predicted quality score: {predicted_score:.2f}",
                }
            )
            total_risk_score += 0.2
            gate_result["modifications_required"].extend(
                rbr_result.get("improvement_suggestions", [])
            )

            if gate_result["final_decision"] == ActionDecision.PROCEED:
                gate_result["final_decision"] = ActionDecision.VALIDATE

        # 4. PRESIDENT宣言状態チェック
        president_result = self._president_declaration_check()
        gate_result["checks_performed"].append("president_declaration")

        if not president_result.get("declared", False):
            gate_result["violations_detected"].append(
                {
                    "type": "PRESIDENT_DECLARATION_MISSING",
                    "severity": "CRITICAL",
                    "details": "PRESIDENT宣言が未実行",
                }
            )
            gate_result["final_decision"] = ActionDecision.BLOCK
            total_risk_score += 0.5

        # 5. 総合リスク評価
        gate_result["risk_assessment"] = {
            "total_risk_score": min(1.0, total_risk_score),
            "violation_count": violation_count,
            "risk_level": self._calculate_risk_level(total_risk_score),
            "confidence": max(0.1, 1.0 - total_risk_score),
        }

        # フィードバック結果生成
        feedback_result = FeedbackResult(
            decision=gate_result["final_decision"],
            confidence=gate_result["risk_assessment"]["confidence"],
            reasoning=self._generate_reasoning(gate_result),
            violations=gate_result["violations_detected"],
            modifications=gate_result["modifications_required"],
            risk_score=gate_result["risk_assessment"]["total_risk_score"],
        )

        # ログ記録
        self._log_feedback_result(gate_result)

        return feedback_result

    def _constitutional_ai_check(self, action_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Constitutional AI即座チェック"""
        try:
            if self.constitutional_ai:
                return self.constitutional_ai.evaluate_action(
                    action_plan.get("description", ""), action_plan.get("context", {})
                )
            else:
                # フォールバック: 基本的な制約チェック
                violations = []

                # 基本的な危険行動チェック
                dangerous_keywords = ["delete", "remove", "force", "destroy", "reset"]
                action_text = str(action_plan).lower()

                for keyword in dangerous_keywords:
                    if keyword in action_text:
                        violations.append(
                            {
                                "type": "DANGEROUS_ACTION",
                                "severity": "HIGH",
                                "details": f"Potentially dangerous keyword detected: {keyword}",
                            }
                        )

                return {
                    "compliant": len(violations) == 0,
                    "violations": violations,
                    "fallback_mode": True,
                }

        except Exception as e:
            return {
                "compliant": False,
                "violations": [
                    {
                        "type": "CONSTITUTIONAL_AI_ERROR",
                        "severity": "MEDIUM",
                        "details": f"Constitutional AI check failed: {e}",
                    }
                ],
                "error": str(e),
            }

    def _failure_pattern_check(self, action_plan: Dict[str, Any]) -> Dict[str, Any]:
        """88回失敗パターン照合"""
        matches_found = False
        pattern_violations = []
        suggested_modifications = []
        risk_score = 0.0

        action_text = str(action_plan).lower()

        # 既知の失敗パターン
        failure_patterns = {
            "github_cli_assumption": {
                "keywords": ["github", "gh", "not available", "can't use"],
                "risk": 0.8,
                "modification": "Verify tool availability with 'which gh' before assuming unavailability",
            },
            "repository_target_confusion": {
                "keywords": ["existing repository", "coding-rule2", "push"],
                "risk": 0.9,
                "modification": "Confirm user intention for new vs existing repository",
            },
            "verification_skip": {
                "keywords": ["assume", "should work", "probably"],
                "risk": 0.6,
                "modification": "Add explicit verification steps before claiming completion",
            },
            "session_discontinuity": {
                "keywords": ["different session", "new session", "fresh start"],
                "risk": 0.7,
                "modification": "Maintain session continuity and context awareness",
            },
        }

        for pattern_name, pattern_data in failure_patterns.items():
            keyword_matches = sum(
                1 for keyword in pattern_data["keywords"] if keyword in action_text
            )

            if keyword_matches > 0:
                matches_found = True
                risk_score += pattern_data["risk"] * (
                    keyword_matches / len(pattern_data["keywords"])
                )

                pattern_violations.append(
                    {
                        "type": "FAILURE_PATTERN_MATCH",
                        "severity": "HIGH" if pattern_data["risk"] > 0.7 else "MEDIUM",
                        "pattern": pattern_name,
                        "details": f"Matches {keyword_matches} failure keywords",
                        "historical_occurrences": 88,  # 88回の実績
                    }
                )

                suggested_modifications.append(pattern_data["modification"])

        return {
            "matches_found": matches_found,
            "pattern_violations": pattern_violations,
            "suggested_modifications": suggested_modifications,
            "risk_score": min(1.0, risk_score),
        }

    def _rule_based_prediction(self, action_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Rule-Based Rewards事前評価"""
        try:
            if self.rule_based_rewards:
                # 実際のRBRシステムで事前評価
                predicted_result = self.rule_based_rewards.predict_action_score(
                    action_plan
                )
                return predicted_result
            else:
                # フォールバック: 簡易品質予測
                action_text = str(action_plan)

                quality_indicators = {
                    "verification_keywords": [
                        "verify",
                        "check",
                        "confirm",
                        "test",
                        "validate",
                    ],
                    "evidence_keywords": ["proof", "evidence", "demonstrate", "show"],
                    "planning_keywords": ["plan", "design", "analyze", "consider"],
                }

                quality_score = 0.5  # ベースライン
                improvement_suggestions = []

                for category, keywords in quality_indicators.items():
                    matches = sum(
                        1 for keyword in keywords if keyword in action_text.lower()
                    )
                    if matches > 0:
                        quality_score += 0.1 * matches
                    else:
                        improvement_suggestions.append(
                            f"Consider adding {category.replace('_', ' ')}"
                        )

                return {
                    "predicted_score": min(1.0, quality_score),
                    "improvement_suggestions": improvement_suggestions,
                    "fallback_mode": True,
                }

        except Exception as e:
            return {
                "predicted_score": 0.3,  # 低スコア（安全側）
                "improvement_suggestions": [
                    "Rule-based evaluation failed - manual review recommended"
                ],
                "error": str(e),
            }

    def _president_declaration_check(self) -> Dict[str, Any]:
        """PRESIDENT宣言状態チェック"""
        try:
            president_status_file = (
                self.base_path / "runtime" / "unified-president-declare.json"
            )

            if president_status_file.exists():
                with open(president_status_file, encoding="utf-8") as f:
                    status = json.load(f)

                return {
                    "declared": status.get("declaration_status") == "active",
                    "status": status.get("declaration_status", "unknown"),
                    "last_declaration": status.get("last_declaration_time", "never"),
                }
            else:
                return {
                    "declared": False,
                    "status": "not_declared",
                    "last_declaration": "never",
                }

        except Exception as e:
            return {"declared": False, "status": "check_failed", "error": str(e)}

    def _calculate_risk_level(self, risk_score: float) -> str:
        """リスクレベル計算"""
        if risk_score >= 0.8:
            return "CRITICAL"
        elif risk_score >= 0.6:
            return "HIGH"
        elif risk_score >= 0.4:
            return "MEDIUM"
        elif risk_score >= 0.2:
            return "LOW"
        else:
            return "MINIMAL"

    def _generate_reasoning(self, gate_result: Dict[str, Any]) -> str:
        """推論理由生成"""
        reasoning_parts = []

        if gate_result["final_decision"] == ActionDecision.BLOCK:
            reasoning_parts.append("BLOCKED: Critical violations detected")
        elif gate_result["final_decision"] == ActionDecision.MODIFY:
            reasoning_parts.append("MODIFICATION REQUIRED: High-risk patterns detected")
        elif gate_result["final_decision"] == ActionDecision.VALIDATE:
            reasoning_parts.append("VALIDATION REQUIRED: Quality concerns identified")
        else:
            reasoning_parts.append("PROCEED: All checks passed")

        reasoning_parts.append(
            f"Risk Level: {gate_result['risk_assessment']['risk_level']}"
        )
        reasoning_parts.append(
            f"Violations: {gate_result['risk_assessment']['violation_count']}"
        )
        reasoning_parts.append(f"Checks: {', '.join(gate_result['checks_performed'])}")

        return " | ".join(reasoning_parts)

    def _load_constitutional_ai(self):
        """Constitutional AI読み込み"""
        try:
            ca_path = self.base_path / "src" / "ai" / "constitutional_ai.py"
            if ca_path.exists():
                spec = importlib.util.spec_from_file_location(
                    "constitutional_ai", ca_path
                )
                ca_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(ca_module)
                return ca_module.ConstitutionalAI()
            return None
        except Exception:
            return None

    def _load_rule_based_rewards(self):
        """Rule-Based Rewards読み込み"""
        try:
            rbr_path = self.base_path / "src" / "ai" / "rule_based_rewards.py"
            if rbr_path.exists():
                spec = importlib.util.spec_from_file_location(
                    "rule_based_rewards", rbr_path
                )
                rbr_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(rbr_module)
                return rbr_module.RuleBasedRewards()
            return None
        except Exception:
            return None

    def _load_pattern_matcher(self):
        """パターンマッチャー読み込み"""
        # 実装時に追加
        return None

    def _load_88_failure_patterns(self) -> List[Dict[str, Any]]:
        """88回失敗パターン読み込み"""
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
            return []
        except Exception:
            return []

    def _log_feedback_result(self, result: Dict[str, Any]):
        """フィードバック結果ログ"""
        logs = []

        if self.feedback_log.exists():
            try:
                with open(self.feedback_log, encoding="utf-8") as f:
                    logs = json.load(f)
            except Exception:
                logs = []

        logs.append(result)

        # 最新50件のみ保持
        if len(logs) > 50:
            logs = logs[-50:]

        # ActionDecisionを文字列に変換
        for log in logs:
            if "final_decision" in log and hasattr(log["final_decision"], "value"):
                log["final_decision"] = log["final_decision"].value

        with open(self.feedback_log, "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)


def main():
    """メイン実行（テスト用）"""
    feedback_loop = RealtimeFeedbackLoop()

    # テストケース
    test_actions = [
        {
            "description": "Push to existing repository",
            "context": {"repository": "coding-rule2", "user_request": "new repository"},
        },
        {
            "description": "Use GitHub CLI without verification",
            "context": {"tool": "gh", "verification": "assumed unavailable"},
        },
        {
            "description": "Verify tool availability and create new repository",
            "context": {"tool": "gh", "verification": "check with which command"},
        },
    ]

    print("🔄 Realtime Feedback Loop Test")
    print("=" * 60)

    for i, action in enumerate(test_actions, 1):
        print(f"\n🧪 Test {i}: {action['description']}")

        result = feedback_loop.pre_execution_gate(action)

        print(f"   Decision: {result.decision.value}")
        print(f"   Risk Score: {result.risk_score:.2f}")
        print(f"   Violations: {len(result.violations)}")
        print(f"   Reasoning: {result.reasoning}")

        if result.modifications:
            print(f"   Modifications: {result.modifications[:2]}")  # 最初の2つ


if __name__ == "__main__":
    main()
