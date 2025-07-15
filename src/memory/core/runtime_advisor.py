#!/usr/bin/env python3
"""
Runtime Advisor - 78回ミス履歴を活用したリアルタイムミス防止システム
o3の指摘に基づく3層構造実装
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict

PROJECT_ROOT = Path(__file__).resolve().parents[3]
MISTAKES_DB = PROJECT_ROOT / "src/memory/persistent-learning/mistakes-database.json"
VERIFICATION_LOG = PROJECT_ROOT / "runtime/ai_api_logs/runtime_advisor.log"


class RuntimeAdvisor:
    def __init__(self):
        self.mistakes_patterns = self.load_mistakes_database()
        self.language_rules = self.load_language_rules()
        self.verification_log = []

    def load_mistakes_database(self) -> Dict:
        """78回ミス履歴の読み込み"""
        if MISTAKES_DB.exists():
            try:
                with open(MISTAKES_DB, encoding="utf-8") as f:
                    data = json.load(f)
                    return data
            except Exception as e:
                print(f"⚠️ ミスデータベース読み込みエラー: {e}", file=sys.stderr)

        # デフォルトの78回ミスパターン
        return {
            "total_mistakes": 78,
            "critical_patterns": [
                {
                    "id": "mistake_001",
                    "type": "虚偽報告詐欺",
                    "pattern": r"(稼働中|起動済み|完了|成功)",
                    "severity": "critical",
                    "prevention": "証拠添付必須",
                    "trigger_action": "hard_stop",
                },
                {
                    "id": "mistake_002",
                    "type": "推測回答",
                    "pattern": r"(おそらく|たぶん|と思われ|の可能性|でしょう)",
                    "severity": "high",
                    "prevention": "5分検索ルール実行",
                    "trigger_action": "soft_warning",
                },
                {
                    "id": "mistake_003",
                    "type": "ファイル散乱",
                    "pattern": r"(ルートに|プロジェクト直下|[^/]+\.md$|^[a-zA-Z0-9_-]+/[a-zA-Z0-9_.-]+\.[a-zA-Z0-9]+$)",
                    "severity": "medium",
                    "prevention": "適切なディレクトリ確認",
                    "trigger_action": "directory_check",
                },
                {
                    "id": "mistake_004",
                    "type": "絶対パス使用",
                    "pattern": r"/Users/[^/]+/Desktop",
                    "severity": "medium",
                    "prevention": "相対パス使用",
                    "trigger_action": "path_correction",
                },
                {
                    "id": "mistake_005",
                    "type": "確認回避",
                    "pattern": r"(チェック済み|確認完了|確認できました|問題なし)",
                    "severity": "high",
                    "prevention": "証拠提示要求",
                    "trigger_action": "evidence_request",
                },
                {
                    "id": "mistake_008",
                    "type": "言語使用違反",
                    "pattern": r"(I will|Let me|I'll|I'm going to|I need to).*?(処理|実装|修正|対応)",
                    "severity": "critical",
                    "prevention": "言語使用パターン自動検出・強制修正",
                    "trigger_action": "language_enforcement",
                },
            ],
        }

    def load_language_rules(self) -> Dict:
        """言語使用ルールの読み込み"""
        return {
            "processing": "english",
            "declaration": "japanese",
            "reporting": "japanese",
            "user_preferred_format": "japanese_declaration_english_process_japanese_report",
            "patterns": {
                "japanese_declaration": r"^##\s*🎯.*これから行うこと",
                "english_processing": r"<function_calls>|<invoke>|def\s+\w+|class\s+\w+",
                "japanese_reporting": r"^##\s*✅.*完遂報告",
            },
        }

    def validate_language_usage(self, response_text: str, context_type: str) -> Dict:
        """言語使用ルールの検証"""
        validation_result = {
            "timestamp": datetime.now().isoformat(),
            "context_type": context_type,
            "compliant": True,
            "violations": [],
            "required_language": self.language_rules.get(context_type, "japanese"),
            "recommendations": [],
        }

        # Pattern-based validation
        patterns = self.language_rules.get("patterns", {})

        if context_type == "declaration":
            if not re.search(
                patterns.get("japanese_declaration", ""), response_text, re.MULTILINE
            ):
                validation_result["compliant"] = False
                validation_result["violations"].append(
                    "Missing Japanese declaration pattern"
                )
                validation_result["recommendations"].append(
                    "Use '## 🎯 これから行うこと' format"
                )

        elif context_type == "reporting":
            if not re.search(
                patterns.get("japanese_reporting", ""), response_text, re.MULTILINE
            ):
                validation_result["compliant"] = False
                validation_result["violations"].append(
                    "Missing Japanese reporting pattern"
                )
                validation_result["recommendations"].append(
                    "Use '## ✅ 完遂報告' format"
                )

        return validation_result

    def enforce_language_compliance(self, response_text: str) -> Dict:
        """言語使用の強制チェック"""
        enforcement_result = {
            "overall_compliant": True,
            "declaration_check": None,
            "processing_check": None,
            "reporting_check": None,
            "enforcement_actions": [],
        }

        # Check for declaration section
        if "これから行うこと" in response_text:
            enforcement_result["declaration_check"] = self.validate_language_usage(
                response_text, "declaration"
            )
            if not enforcement_result["declaration_check"]["compliant"]:
                enforcement_result["overall_compliant"] = False

        # Check for reporting section
        if "完遂報告" in response_text:
            enforcement_result["reporting_check"] = self.validate_language_usage(
                response_text, "reporting"
            )
            if not enforcement_result["reporting_check"]["compliant"]:
                enforcement_result["overall_compliant"] = False

        # Generate enforcement actions
        if not enforcement_result["overall_compliant"]:
            enforcement_result["enforcement_actions"].append(
                "Block response until language compliance"
            )
            enforcement_result["enforcement_actions"].append("Require template usage")

        return enforcement_result

    def analyze_input(self, user_input: str, context: str = "") -> Dict:
        """ユーザー入力の分析とミスパターン検出"""
        analysis_result = {
            "timestamp": datetime.now().isoformat(),
            "input": user_input[:200],  # 最初の200文字のみ記録
            "context": context[:100],
            "detected_patterns": [],
            "risk_score": 0,
            "recommendations": [],
            "required_actions": [],
        }

        # 各ミスパターンとの照合
        for pattern in self.mistakes_patterns.get("critical_patterns", []):
            if re.search(pattern["pattern"], user_input, re.IGNORECASE):
                detection = {
                    "mistake_id": pattern["id"],
                    "mistake_type": pattern["type"],
                    "severity": pattern["severity"],
                    "prevention": pattern["prevention"],
                    "trigger_action": pattern["trigger_action"],
                }

                analysis_result["detected_patterns"].append(detection)

                # リスクスコア計算
                severity_scores = {"critical": 50, "high": 30, "medium": 15, "low": 5}
                analysis_result["risk_score"] += severity_scores.get(
                    pattern["severity"], 5
                )

                # 推奨アクション生成
                analysis_result["recommendations"].append(pattern["prevention"])
                analysis_result["required_actions"].append(pattern["trigger_action"])

        return analysis_result

    def check_output_safety(self, assistant_output: str) -> Dict:
        """アシスタント出力の安全性チェック"""
        safety_result = {
            "timestamp": datetime.now().isoformat(),
            "output_snippet": assistant_output[:100],
            "safety_violations": [],
            "safety_score": 100,  # 100が最高点
            "requires_evidence": False,
            "blocked_phrases": [],
        }

        # 危険フレーズの検出
        dangerous_phrases = [
            r"稼働中",
            r"完了",
            r"成功",
            r"確認できました",
            r"問題ありません",
            r"正常",
            r"全て完成",
            r"実装済み",
            r"対応済み",
            r"実装済みです",
            r"対応済みです",
        ]

        for phrase_pattern in dangerous_phrases:
            matches = re.findall(phrase_pattern, assistant_output, re.IGNORECASE)
            if matches:
                safety_result["safety_violations"].append(
                    {"phrase": phrase_pattern, "matches": matches, "severity": "high"}
                )
                safety_result["safety_score"] -= 20
                safety_result["requires_evidence"] = True
                safety_result["blocked_phrases"].extend(matches)

        # 推測表現の検出
        speculation_phrases = [
            r"おそらく",
            r"たぶん",
            r"と思われ",
            r"かもしれ",
            r"でしょう",
        ]

        for spec_pattern in speculation_phrases:
            matches = re.findall(spec_pattern, assistant_output, re.IGNORECASE)
            if matches:
                safety_result["safety_violations"].append(
                    {"phrase": spec_pattern, "matches": matches, "severity": "medium"}
                )
                safety_result["safety_score"] -= 10

        return safety_result

    def generate_prevention_instructions(self, analysis: Dict) -> str:
        """防止指示の生成"""
        if not analysis["detected_patterns"]:
            return "✅ ミスパターン検出なし - 安全に作業を継続してください。"

        instructions = ["🚨 ミスパターン検出 - 以下の対策を実行してください：\n"]

        for i, pattern in enumerate(analysis["detected_patterns"], 1):
            instructions.append(
                f"{i}. **{pattern['mistake_type']}** (重要度: {pattern['severity']})"
            )
            instructions.append(f"   - 防止策: {pattern['prevention']}")
            instructions.append(f"   - 必要アクション: {pattern['trigger_action']}")
            instructions.append("")

        # 総合評価
        risk_score = analysis["risk_score"]
        if risk_score >= 50:
            instructions.append(
                "🔴 **高リスク**: 作業を一時停止し、証拠確認を必須とします。"
            )
        elif risk_score >= 30:
            instructions.append(
                "🟡 **中リスク**: 慎重に作業を進め、確認を徹底してください。"
            )
        else:
            instructions.append("🟢 **低リスク**: 通常通り作業を継続してください。")

        return "\n".join(instructions)

    def log_verification(self, result: Dict):
        """検証結果のログ記録"""
        try:
            VERIFICATION_LOG.parent.mkdir(parents=True, exist_ok=True)

            with open(VERIFICATION_LOG, "a", encoding="utf-8") as f:
                f.write(json.dumps(result, ensure_ascii=False) + "\n")

        except Exception as e:
            print(f"⚠️ ログ記録失敗: {e}", file=sys.stderr)

    def get_prevention_summary(self) -> Dict:
        """防止効果のサマリー取得"""
        if not VERIFICATION_LOG.exists():
            return {"total_checks": 0, "prevented_mistakes": 0, "prevention_rate": 0}

        try:
            total_checks = 0
            prevented_mistakes = 0

            with open(VERIFICATION_LOG, encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        result = json.loads(line)
                        total_checks += 1
                        if result.get("detected_patterns"):
                            prevented_mistakes += 1

            prevention_rate = (
                (prevented_mistakes / total_checks * 100) if total_checks > 0 else 0
            )

            return {
                "total_checks": total_checks,
                "prevented_mistakes": prevented_mistakes,
                "prevention_rate": round(prevention_rate, 2),
            }

        except Exception as e:
            print(f"⚠️ サマリー取得エラー: {e}", file=sys.stderr)
            return {"total_checks": 0, "prevented_mistakes": 0, "prevention_rate": 0}


def main():
    """メイン処理 - CLI使用例"""
    if len(sys.argv) < 2:
        print("使用法: python3 runtime-advisor.py 'チェック対象テキスト'")
        return

    advisor = RuntimeAdvisor()
    input_text = sys.argv[1]

    # 分析実行
    analysis = advisor.analyze_input(input_text)

    # 結果表示
    print("🔍 Runtime Advisor 分析結果")
    print("=" * 40)
    print(f"リスクスコア: {analysis['risk_score']}")
    print(f"検出パターン数: {len(analysis['detected_patterns'])}")

    # 防止指示生成
    instructions = advisor.generate_prevention_instructions(analysis)
    print("\n" + instructions)

    # ログ記録
    advisor.log_verification(analysis)

    # サマリー表示
    summary = advisor.get_prevention_summary()
    print(
        f"\n📊 防止効果: {summary['prevention_rate']}% ({summary['prevented_mistakes']}/{summary['total_checks']})"
    )


if __name__ == "__main__":
    main()
