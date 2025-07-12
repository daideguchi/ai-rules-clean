#!/usr/bin/env python3
"""
Emergency Claude Enforcer
緊急Claude強制実行システム - CLAUDE.md強制遵守
Claude推論プロセス直接介入・ルール無視防止
"""

import json
import sys
from pathlib import Path


class EmergencyClaudeEnforcer:
    """緊急Claude強制実行システム"""

    def __init__(self):
        self.base_path = Path("/Users/dd/Desktop/1_dev/coding-rule2")
        self.claude_md = self.base_path / "CLAUDE.md"
        self.violations_log = self.base_path / "runtime" / "emergency_violations.json"

    def emergency_intervention(self):
        """緊急介入 - 即座強制実行"""
        violations = []

        # 1. thinking要件チェック
        if not self._check_thinking_compliance():
            violations.append(
                {
                    "type": "THINKING_VIOLATION",
                    "severity": "CRITICAL",
                    "rule": "CLAUDE.md L54: thinkingタグで必ず開始",
                    "current_state": "thinking無使用で応答生成",
                    "required_action": "即座にthinking開始",
                }
            )

        # 2. PRESIDENT宣言チェック
        if not self._check_president_declaration():
            violations.append(
                {
                    "type": "PRESIDENT_VIOLATION",
                    "severity": "CRITICAL",
                    "rule": "CLAUDE.md L20-24: 作業開始前に必ずPRESIDENT宣言",
                    "current_state": "宣言無視で作業継続",
                    "required_action": "即座にmake declare-president実行",
                }
            )

        # 3. 言語使用ルール違反
        language_violations = self._check_language_rules()
        violations.extend(language_violations)

        if violations:
            self._force_compliance(violations)
            return False  # 処理停止

        return True  # 処理継続許可

    def _check_thinking_compliance(self) -> bool:
        """thinking遵守チェック"""
        # 現在の応答でthinkingが使用されているかチェック
        # (実装時点では検出困難なため簡易判定)
        return False  # 常にthinking要求

    def _check_president_declaration(self) -> bool:
        """PRESIDENT宣言チェック"""
        try:
            president_file = (
                self.base_path / "runtime" / "unified-president-declare.json"
            )
            if president_file.exists():
                with open(president_file) as f:
                    status = json.load(f)
                    return status.get("declaration_status") == "active"
        except Exception:
            pass
        return False

    def _check_language_rules(self) -> list:
        """言語使用ルールチェック"""
        violations = []

        # CLAUDE.md L60-64の言語ルール
        required_structure = {
            "宣言": "## 🎯 これから行うこと",
            "処理": "Technical implementation",
            "報告": "## ✅ 完遂報告",
        }

        # 簡易チェック（実装時点では完全検出困難）
        violations.append(
            {
                "type": "LANGUAGE_STRUCTURE_VIOLATION",
                "severity": "HIGH",
                "rule": "CLAUDE.md L60-64: 言語使用ルール永続遵守",
                "required_structure": required_structure,
                "required_action": "構造化された応答形式で再実行",
            }
        )

        return violations

    def _force_compliance(self, violations: list):
        """強制遵守実行"""
        print("🚨 EMERGENCY CLAUDE ENFORCER - CRITICAL VIOLATIONS DETECTED")
        print("=" * 80)

        for violation in violations:
            print(f"❌ {violation['type']}: {violation['severity']}")
            print(f"   Rule: {violation['rule']}")
            print(f"   Current: {violation.get('current_state', 'Unknown')}")
            print(f"   Required: {violation['required_action']}")
            print()

        print("🔴 CLAUDE RESPONSE BLOCKED - COMPLIANCE REQUIRED")
        print("=" * 80)

        # 違反ログ記録
        self._log_violations(violations)

        # 強制終了
        print("System will now enforce compliance...")
        sys.exit(1)

    def _log_violations(self, violations: list):
        """違反ログ記録"""
        log_entry = {
            "timestamp": "2025-07-10T15:16:00.000Z",
            "violation_count": len(violations),
            "violations": violations,
            "enforcement_action": "RESPONSE_BLOCKED",
        }

        logs = []
        if self.violations_log.exists():
            try:
                with open(self.violations_log) as f:
                    logs = json.load(f)
            except Exception:
                logs = []

        logs.append(log_entry)

        self.violations_log.parent.mkdir(parents=True, exist_ok=True)
        with open(self.violations_log, "w") as f:
            json.dump(logs, f, indent=2)


def emergency_claude_check():
    """緊急Claude チェック実行"""
    enforcer = EmergencyClaudeEnforcer()
    return enforcer.emergency_intervention()


if __name__ == "__main__":
    emergency_claude_check()
