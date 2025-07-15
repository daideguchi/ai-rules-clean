#!/usr/bin/env python3
"""
🔍 Pre-response Validator - 応答生成前チェックフック
=================================================
AI応答生成前に{{mistake_count}}回のミスパターンを検出・防止する強制実行メカニズム
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path


class ResponseValidationError(Exception):
    """応答検証エラー"""

    pass


class PreResponseValidator:
    """応答生成前の検証システム"""

    def __init__(self):
        self.project_root = Path("/Users/dd/Desktop/1_dev/coding-rule2")
        self.audit_log = (
            self.project_root / "runtime" / "logs" / "response_validation.log"
        )
        self.audit_log.parent.mkdir(parents=True, exist_ok=True)

        # {{mistake_count}}回のミスパターン定義
        self.forbidden_patterns = [
            # パターン0: thinking必須違反
            {
                "pattern": r"^(?!.*<thinking>)",
                "severity": "CRITICAL",
                "description": "thinking必須違反",
                "prevention": "毎回必ず<thinking>タグから開始する",
            },
            # パターン1: 完了虚偽報告
            {
                "pattern": r"完了|完成|実装完了|システム完了",
                "severity": "CRITICAL",
                "description": "完了虚偽報告防止",
                "prevention": "実際の完了証跡なしに「完了」発言を禁止",
            },
            # パターン2: 途中停止宣言
            {
                "pattern": r"基盤ができた|基盤実装|基盤構築",
                "severity": "CRITICAL",
                "description": "途中停止防止",
                "prevention": "基盤作成だけで止まることを禁止",
            },
            # パターン3: ミス記録だけで満足
            {
                "pattern": r"(\d+)回目のミス|ミス発生中|ミス記録",
                "severity": "CRITICAL",
                "description": "ミス記録満足防止",
                "prevention": "ミス記録ではなく実際の改善を要求",
            },
            # パターン4: 情報不足での相談
            {
                "pattern": r"o3に相談|geminiに相談",
                "severity": "WARNING",
                "description": "情報不足相談防止",
                "prevention": "必要情報を含めた相談を強制",
            },
            # パターン5: 言い訳・分析の継続
            {
                "pattern": r"私は.*しました|根本原因は|分析します",
                "severity": "WARNING",
                "description": "言い訳・分析継続防止",
                "prevention": "具体的行動を優先",
            },
        ]

    def validate_response(self, response_text: str) -> dict:
        """応答内容の検証"""
        validation_result = {
            "valid": True,
            "violations": [],
            "warnings": [],
            "timestamp": datetime.now().isoformat(),
        }

        # 禁止パターンチェック
        for pattern_def in self.forbidden_patterns:
            if re.search(pattern_def["pattern"], response_text, re.IGNORECASE):
                violation = {
                    "pattern": pattern_def["pattern"],
                    "severity": pattern_def["severity"],
                    "description": pattern_def["description"],
                    "prevention": pattern_def["prevention"],
                    "matched_text": re.search(
                        pattern_def["pattern"], response_text, re.IGNORECASE
                    ).group(),
                }

                if pattern_def["severity"] == "CRITICAL":
                    validation_result["violations"].append(violation)
                    validation_result["valid"] = False
                else:
                    validation_result["warnings"].append(violation)

        # 特別チェック: 「最後まで」指示後の途中停止
        if self._check_incomplete_execution(response_text):
            validation_result["violations"].append(
                {
                    "pattern": "incomplete_execution",
                    "severity": "CRITICAL",
                    "description": "最後まで実行指示無視",
                    "prevention": "指示された作業を最後まで完了させる",
                    "matched_text": "途中停止検出",
                }
            )
            validation_result["valid"] = False

        # 検証結果をログ
        self._log_validation(validation_result)

        return validation_result

    def _check_incomplete_execution(self, response_text: str) -> bool:
        """途中停止の検出"""
        # 実装継続が必要な状況の検出
        incomplete_indicators = [
            r"次に.*します",
            r"続いて.*を行います",
            r"以下を実装.*",
            r".*を完了させます",
        ]

        # 実際の実装アクションが含まれているかチェック
        action_indicators = [
            r"Write\(",
            r"Edit\(",
            r"Bash\(",
            r"TodoWrite\(",
        ]

        has_promise = any(
            re.search(pattern, response_text) for pattern in incomplete_indicators
        )
        has_action = any(
            re.search(pattern, response_text) for pattern in action_indicators
        )

        # 約束だけあって実際のアクションがない場合は途中停止
        return has_promise and not has_action

    def _handle_violations(self, validation_result: dict):
        """違反処理"""
        if not validation_result["valid"]:
            critical_violations = [
                v
                for v in validation_result["violations"]
                if v["severity"] == "CRITICAL"
            ]

            if critical_violations:
                # CRITICAL違反は応答を修正
                error_msg = "🛑 応答生成前チェック: CRITICAL違反検出\n\n"
                for violation in critical_violations:
                    error_msg += f"違反: {violation['description']}\n"
                    error_msg += f"防止策: {violation['prevention']}\n\n"

                # 修正された応答を生成
                corrected_response = self._generate_corrected_response(
                    critical_violations
                )
                return corrected_response

        return None

    def _generate_corrected_response(self, violations: list) -> str:
        """修正された応答の生成"""
        response = "🔧 自動修正: {{mistake_count}}回ミス防止システム作動\n\n"

        for violation in violations:
            if "完了" in violation["description"]:
                response += "✅ 実装を最後まで継続します（虚偽の完了報告を防止）\n"
            elif "途中停止" in violation["description"]:
                response += "🔄 作業を中断せず最後まで実行します\n"
            elif "ミス記録" in violation["description"]:
                response += "⚡ ミス記録ではなく実際の改善を実行します\n"

        response += "\n📋 継続中のタスクを完了させます:"
        return response

    def _log_validation(self, result: dict):
        """検証結果のログ記録"""
        try:
            with open(self.audit_log, "a") as f:
                f.write(json.dumps(result, ensure_ascii=False) + "\n")
        except Exception:
            pass


def main():
    """フック実行のメイン関数"""
    try:
        # Claude Codeの応答内容を標準入力から受け取る
        response_content = sys.stdin.read()

        validator = PreResponseValidator()
        validation_result = validator.validate_response(response_content)

        # 違反があれば修正
        if not validation_result["valid"]:
            corrected = validator._handle_violations(validation_result)
            if corrected:
                print(corrected)
                sys.exit(1)  # 元の応答を停止して修正版を出力

        # 警告がある場合は警告メッセージを追加
        if validation_result["warnings"]:
            print(
                f"⚠️ 応答警告: {len(validation_result['warnings'])}件の改善点があります"
            )

        sys.exit(0)

    except Exception as e:
        print(f"Pre-response validation error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
