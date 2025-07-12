#!/usr/bin/env python3
"""
🔍 Pre-execution Validator - 指示不履行防止システム
=================================================
MCPからの指示とAI生成アクションの一致性を検証し、
指示無視・虚偽報告を技術的に防止する強制実行メカニズム
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

# プロジェクトルート設定
PROJECT_ROOT = Path(__file__).resolve().parents[2]
AUDIT_LOG = PROJECT_ROOT / "runtime" / "logs" / "conductor_audit.log"


class InstructionViolationError(Exception):
    """指示違反エラー"""

    pass


class PreExecutionValidator:
    """実行前検証システム"""

    def __init__(self):
        self.validation_rules = {
            "mcp_gemini_cli": {
                "pattern": r"(gemini|mcp.*gemini|gemini.*cli)",
                "required_actions": ["gemini", "cli"],
                "forbidden_actions": ["websearch", "mock", "偽装"],
                "severity": "CRITICAL",
            },
            "conductor_awareness": {
                "pattern": r"(指揮者|conductor|orchestrat)",
                "required_actions": ["acknowledge", "reference"],
                "forbidden_actions": ["ignore", "forget"],
                "severity": "HIGH",
            },
        }

        # 監査ログディレクトリ確保
        AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)

    def validate_instruction_compliance(self) -> Dict[str, Any]:
        """指示遵守検証のメイン処理"""

        # 環境変数から指示とアクション情報を取得
        tool_name = os.environ.get("TOOL_NAME", "")
        tool_input = os.environ.get("TOOL_INPUT", "")
        context = os.environ.get("CLAUDE_CONTEXT", "")

        validation_result = {
            "timestamp": datetime.now().isoformat(),
            "tool_name": tool_name,
            "tool_input": tool_input[:200],  # 最初の200文字のみログ
            "validation_status": "UNKNOWN",
            "violations": [],
            "enforcement_actions": [],
        }

        try:
            # 各検証ルールを適用
            for rule_name, rule_config in self.validation_rules.items():
                violation = self._check_rule_violation(
                    rule_name, rule_config, context, tool_name, tool_input
                )

                if violation:
                    validation_result["violations"].append(violation)

            # 違反があった場合の処理
            if validation_result["violations"]:
                validation_result["validation_status"] = "VIOLATION_DETECTED"
                self._handle_violations(validation_result)
            else:
                validation_result["validation_status"] = "PASSED"

            # 監査ログに記録
            self._log_validation_result(validation_result)

            return validation_result

        except Exception as e:
            validation_result["validation_status"] = "ERROR"
            validation_result["error"] = str(e)
            self._log_validation_result(validation_result)
            raise

    def _check_rule_violation(
        self,
        rule_name: str,
        rule_config: Dict,
        context: str,
        tool_name: str,
        tool_input: str,
    ) -> Optional[Dict]:
        """個別ルール違反チェック"""

        # コンテキスト内でルールパターンが検出されるかチェック
        if not re.search(rule_config["pattern"], context, re.IGNORECASE):
            return None  # このルールは適用対象外

        violation = {
            "rule_name": rule_name,
            "severity": rule_config["severity"],
            "detected_pattern": rule_config["pattern"],
            "required_actions": rule_config["required_actions"],
            "forbidden_actions": rule_config["forbidden_actions"],
            "actual_tool": tool_name,
            "compliance_check": {},
        }

        # 必須アクションチェック
        for required_action in rule_config["required_actions"]:
            if required_action.lower() in tool_input.lower():
                violation["compliance_check"][f"required_{required_action}"] = "FOUND"
            else:
                violation["compliance_check"][f"required_{required_action}"] = "MISSING"

        # 禁止アクションチェック
        for forbidden_action in rule_config["forbidden_actions"]:
            if forbidden_action.lower() in tool_input.lower():
                violation["compliance_check"][f"forbidden_{forbidden_action}"] = (
                    "DETECTED"
                )

        # 違反判定
        missing_required = [
            k
            for k, v in violation["compliance_check"].items()
            if k.startswith("required_") and v == "MISSING"
        ]
        detected_forbidden = [
            k
            for k, v in violation["compliance_check"].items()
            if k.startswith("forbidden_") and v == "DETECTED"
        ]

        if missing_required or detected_forbidden:
            violation["violation_type"] = "INSTRUCTION_IGNORED"
            violation["details"] = {
                "missing_required": missing_required,
                "detected_forbidden": detected_forbidden,
            }
            return violation

        return None

    def _handle_violations(self, validation_result: Dict[str, Any]):
        """違反処理"""

        critical_violations = [
            v for v in validation_result["violations"] if v["severity"] == "CRITICAL"
        ]

        if critical_violations:
            # CRITICAL違反は実行を強制停止
            error_msg = "🚨 CRITICAL指示違反検出 - 実行を停止します:\n"

            for violation in critical_violations:
                error_msg += (
                    f"  ❌ {violation['rule_name']}: {violation['violation_type']}\n"
                )
                error_msg += f"     詳細: {violation['details']}\n"

            # 強制実行メカニズム：環境変数でエラー状態を設定
            os.environ["VALIDATION_ERROR"] = "CRITICAL_VIOLATION"
            os.environ["VALIDATION_MESSAGE"] = error_msg

            print(error_msg)
            sys.exit(1)  # 実行を強制停止

        # HIGH以下の違反は警告として処理
        for violation in validation_result["violations"]:
            warning_msg = f"⚠️ 指示違反警告: {violation['rule_name']}"
            print(warning_msg)
            validation_result["enforcement_actions"].append(warning_msg)

    def _log_validation_result(self, result: Dict[str, Any]):
        """監査ログに記録"""
        try:
            with open(AUDIT_LOG, "a", encoding="utf-8") as f:
                f.write(json.dumps(result, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"⚠️ 監査ログ記録エラー: {e}")


def main():
    """メイン処理 - フックとして実行"""
    try:
        validator = PreExecutionValidator()
        result = validator.validate_instruction_compliance()

        # 結果を環境変数に設定（他のフックが参照可能）
        os.environ["VALIDATION_RESULT"] = json.dumps(result)

    except InstructionViolationError as e:
        print(f"🚨 指示違反エラー: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"⚠️ 検証システムエラー: {e}")
        # 検証システム自体のエラーは実行を止めない（フェイルオープン）
        sys.exit(0)


if __name__ == "__main__":
    main()
