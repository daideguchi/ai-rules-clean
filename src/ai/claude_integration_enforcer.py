#!/usr/bin/env python3
"""
Claude Integration Enforcer
Claude推論プロセスへのシステム統合強制実行機構
PRESIDENT宣言・thinking・Constitutional AI統合
"""

import datetime
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict


@dataclass
class SessionEnforcementRule:
    """セッション強制ルール"""

    rule_name: str
    requirement: str
    enforcement_level: str  # CRITICAL, HIGH, MEDIUM
    check_frequency: str  # session_start, task_start, continuous
    violation_action: str  # block, warn, log


class ClaudeIntegrationEnforcer:
    """Claude統合強制実行システム"""

    def __init__(self):
        self.base_path = Path("/Users/dd/Desktop/1_dev/coding-rule2")
        self.claude_md_file = self.base_path / "CLAUDE.md"
        self.enforcement_log = self.base_path / "runtime" / "claude_enforcement.json"

        # 強制ルール定義
        self.enforcement_rules = {
            "president_declaration": SessionEnforcementRule(
                rule_name="PRESIDENT宣言",
                requirement="作業開始前に必ずmake declare-presidentを実行",
                enforcement_level="CRITICAL",
                check_frequency="session_start",
                violation_action="block",
            ),
            "thinking_requirement": SessionEnforcementRule(
                rule_name="重要タスクthinking",
                requirement="重要タスク・技術分析でultrathink必須",
                enforcement_level="HIGH",
                check_frequency="task_start",
                violation_action="warn",
            ),
            "constitutional_ai_check": SessionEnforcementRule(
                rule_name="Constitutional AI統合",
                requirement="全アクション前のConstitutional AIチェック",
                enforcement_level="HIGH",
                check_frequency="continuous",
                violation_action="warn",
            ),
        }

        self.session_state = {
            "president_declared": False,
            "thinking_activated": False,
            "constitutional_ai_active": False,
            "violations": [],
        }

    def enforce_session_start_rules(self) -> Dict[str, Any]:
        """セッション開始時強制ルール実行"""
        enforcement_result = {
            "timestamp": datetime.datetime.now().isoformat(),
            "rules_checked": [],
            "violations": [],
            "enforcement_actions": [],
        }

        # 1. PRESIDENT宣言チェック
        president_check = self._check_president_declaration()
        enforcement_result["rules_checked"].append("president_declaration")

        if not president_check["compliant"]:
            violation = {
                "rule": "president_declaration",
                "severity": "CRITICAL",
                "description": "PRESIDENT宣言が未実行",
                "required_action": "make declare-president実行が必要",
            }
            enforcement_result["violations"].append(violation)
            enforcement_result["enforcement_actions"].append("タスク実行ブロック推奨")

        # 2. Constitutional AI統合チェック
        constitutional_check = self._check_constitutional_ai_integration()
        enforcement_result["rules_checked"].append("constitutional_ai_integration")

        if not constitutional_check["active"]:
            enforcement_result["enforcement_actions"].append(
                "Constitutional AIシステム自動有効化"
            )

        # 3. 記憶継承システムチェック
        self._check_memory_inheritance()
        enforcement_result["rules_checked"].append("memory_inheritance")

        self._log_enforcement_result(enforcement_result)
        return enforcement_result

    def enforce_task_complexity_analysis(self, task_description: str) -> Dict[str, Any]:
        """タスク複雑度分析・thinking強制"""
        analysis_result = {
            "task_description": task_description,
            "complexity_analysis": {},
            "thinking_required": False,
            "enforcement_actions": [],
        }

        # 重要キーワード検出
        critical_keywords = [
            "技術的根本原因分析",
            "重要なタスク",
            "完璧",
            "システム的",
            "ベストプラクティス",
            "アーキテクチャ",
            "設計",
        ]

        thinking_trigger_score = 0
        detected_keywords = []

        for keyword in critical_keywords:
            if keyword in task_description:
                thinking_trigger_score += 1
                detected_keywords.append(keyword)

        # thinking要件判定
        if thinking_trigger_score >= 2 or "ultrathink" in task_description.lower():
            analysis_result["thinking_required"] = True
            analysis_result["enforcement_actions"].append("ultrathink自動発動推奨")

        analysis_result["complexity_analysis"] = {
            "trigger_score": thinking_trigger_score,
            "detected_keywords": detected_keywords,
            "complexity_level": "HIGH"
            if thinking_trigger_score >= 2
            else "MEDIUM"
            if thinking_trigger_score >= 1
            else "LOW",
        }

        return analysis_result

    def _check_president_declaration(self) -> Dict[str, Any]:
        """PRESIDENT宣言状態チェック"""
        try:
            # unified-president-tool.pyの実行状態確認
            president_status_file = (
                self.base_path / "runtime" / "unified-president-declare.json"
            )

            if president_status_file.exists():
                with open(president_status_file, encoding="utf-8") as f:
                    status = json.load(f)

                declaration_valid = status.get("declaration_status") == "active"
                return {
                    "compliant": declaration_valid,
                    "status": status.get("declaration_status", "unknown"),
                    "last_declaration": status.get("last_declaration_time", "never"),
                }
            else:
                return {
                    "compliant": False,
                    "status": "not_declared",
                    "last_declaration": "never",
                }

        except Exception as e:
            return {"compliant": False, "status": "check_failed", "error": str(e)}

    def _check_constitutional_ai_integration(self) -> Dict[str, Any]:
        """Constitutional AI統合状態チェック"""
        try:
            constitutional_ai_file = (
                self.base_path / "src" / "ai" / "constitutional_ai.py"
            )

            if constitutional_ai_file.exists():
                # ファイル存在確認のみ（実際の統合は別途実装必要）
                return {
                    "active": True,
                    "implementation_status": "file_exists",
                    "integration_level": "partial",
                }
            else:
                return {"active": False, "implementation_status": "not_implemented"}

        except Exception as e:
            return {"active": False, "error": str(e)}

    def _check_memory_inheritance(self) -> Dict[str, Any]:
        """記憶継承システムチェック"""
        try:
            session_file = (
                self.base_path
                / "src"
                / "memory"
                / "core"
                / "session-records"
                / "current-session.json"
            )

            if session_file.exists():
                with open(session_file, encoding="utf-8") as f:
                    session_data = json.load(f)

                memory_inheritance = session_data.get("memory_inheritance", {})
                inherited_memories = memory_inheritance.get("inherited_memories", 0)

                return {
                    "active": inherited_memories > 0,
                    "inherited_memories": inherited_memories,
                    "session_continuity": session_data.get("session_status", "unknown"),
                }
            else:
                return {"active": False, "status": "session_file_missing"}

        except Exception as e:
            return {"active": False, "error": str(e)}

    def _log_enforcement_result(self, result: Dict[str, Any]):
        """強制実行結果ログ"""
        logs = []

        if self.enforcement_log.exists():
            try:
                with open(self.enforcement_log, encoding="utf-8") as f:
                    logs = json.load(f)
            except Exception:
                logs = []

        logs.append(result)

        # 最新100件のみ保持
        if len(logs) > 100:
            logs = logs[-100:]

        # ログ保存
        self.enforcement_log.parent.mkdir(parents=True, exist_ok=True)
        with open(self.enforcement_log, "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)

    def generate_enforcement_report(self) -> Dict[str, Any]:
        """強制実行レポート生成"""
        session_enforcement = self.enforce_session_start_rules()

        report = {
            "timestamp": datetime.datetime.now().isoformat(),
            "session_enforcement": session_enforcement,
            "system_integration_status": {
                "president_declaration": self._check_president_declaration(),
                "constitutional_ai": self._check_constitutional_ai_integration(),
                "memory_inheritance": self._check_memory_inheritance(),
            },
            "enforcement_summary": {
                "total_violations": len(session_enforcement["violations"]),
                "critical_violations": len(
                    [
                        v
                        for v in session_enforcement["violations"]
                        if v["severity"] == "CRITICAL"
                    ]
                ),
                "enforcement_actions_required": len(
                    session_enforcement["enforcement_actions"]
                ),
            },
            "recommendations": [],
        }

        # 推奨事項生成
        if report["enforcement_summary"]["critical_violations"] > 0:
            report["recommendations"].append("CRITICAL: PRESIDENT宣言の即座実行が必要")

        if not report["system_integration_status"]["constitutional_ai"]["active"]:
            report["recommendations"].append(
                "Constitutional AIシステムの統合強化が必要"
            )

        if not report["system_integration_status"]["memory_inheritance"]["active"]:
            report["recommendations"].append("記憶継承システムの活性化が必要")

        return report


def main():
    """メイン実行（強制実行チェック）"""
    enforcer = ClaudeIntegrationEnforcer()

    print("🔍 Claude統合強制実行チェック開始")
    print("=" * 60)

    # セッション開始時強制チェック
    enforcement_report = enforcer.generate_enforcement_report()

    print("📊 強制実行レポート:")
    print(f"   タイムスタンプ: {enforcement_report['timestamp']}")
    print(
        f"   総違反数: {enforcement_report['enforcement_summary']['total_violations']}"
    )
    print(
        f"   クリティカル違反: {enforcement_report['enforcement_summary']['critical_violations']}"
    )
    print(
        f"   必要アクション数: {enforcement_report['enforcement_summary']['enforcement_actions_required']}"
    )

    print("\n🏛️ システム統合状態:")
    for system, status in enforcement_report["system_integration_status"].items():
        print(
            f"   {system}: {'✅' if status.get('active', status.get('compliant', False)) else '❌'}"
        )

    if enforcement_report["recommendations"]:
        print("\n💡 推奨事項:")
        for rec in enforcement_report["recommendations"]:
            print(f"   - {rec}")

    # タスク複雑度分析テスト
    test_task = (
        "技術的根本原因分析の完璧解決と、プロジェクトクローン時のベストプラクティス設計"
    )
    complexity_analysis = enforcer.enforce_task_complexity_analysis(test_task)

    print("\n🧠 タスク複雑度分析:")
    print(
        f"   複雑度レベル: {complexity_analysis['complexity_analysis']['complexity_level']}"
    )
    print(
        f"   thinking要件: {'✅ 必須' if complexity_analysis['thinking_required'] else '❌ 不要'}"
    )
    print(
        f"   検出キーワード: {complexity_analysis['complexity_analysis']['detected_keywords']}"
    )


if __name__ == "__main__":
    main()
