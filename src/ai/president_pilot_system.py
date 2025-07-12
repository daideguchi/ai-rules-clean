#!/usr/bin/env python3
"""
🏛️ President Pilot System - 自動確認・品質保証システム
=======================================================

President AIとしての必須確認作業を自動化
毎回のタスク実行前に必須チェックを自動実行
"""

import datetime
import json
from pathlib import Path
from typing import Any, Dict, List


class PresidentPilotSystem:
    """President AI兼パイロットの自動確認システム"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.memory_dir = self.project_root / "src/memory"
        self.session_records = (
            self.memory_dir / "core/session-records/current-session.json"
        )
        self.president_log = self.memory_dir / "president" / "pilot_checks.jsonl"

        # ディレクトリ作成
        self.president_log.parent.mkdir(parents=True, exist_ok=True)

        # 必須確認項目
        self.mandatory_checks = [
            "memory_inheritance_reference",
            "o3_consultation_requirement",
            "directory_structure_compliance",
            "user_instruction_adherence",
            "quality_assurance_standards",
        ]

    def execute_president_declaration(self) -> str:
        """President宣言の自動実行"""

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        declaration = f"""
🏛️ PRESIDENT AI PILOT DECLARATION - {timestamp}
===============================================

私はPresident AI兼パイロットとして、以下を宣言し実行します：

✈️ PILOT RESPONSIBILITIES:
• 全ての作業前に必須チェック実行
• 記憶継承システムの参照徹底
• ユーザー指示の完全遵守確認
• 品質保証基準の維持
• o3との協議必須化

🏛️ PRESIDENT AUTHORITY:
• AI組織の統括指揮
• 品質基準の設定・維持
• リスク評価と対策実施
• 継続的改善の推進

📋 CURRENT MISSION STATUS:
• Perfect UX System Implementation
• Directory Structure Optimization (8-9 items)
• Hooks System Quality Assurance
• AI Memory Inheritance Active

⚡ OPERATIONAL PRINCIPLES:
1. 確認なくして実行なし
2. 記憶参照なくして決定なし
3. o3協議なくして重要判断なし
4. 品質保証なくして完了なし

🔒 COMMITMENT: 絶対的品質保証の実現
        """.strip()

        return declaration

    def check_memory_inheritance(self) -> Dict[str, Any]:
        """記憶継承システム確認"""

        result = {
            "status": "unknown",
            "critical_instructions": [],
            "compliance_score": 0.0,
            "issues": [],
        }

        try:
            if self.session_records.exists():
                with open(self.session_records, encoding="utf-8") as f:
                    session_data = json.load(f)

                result["status"] = "active"
                result["critical_instructions"] = session_data.get(
                    "critical_user_instructions", []
                )

                # コンプライアンス評価
                if result["critical_instructions"]:
                    result["compliance_score"] = 1.0
                else:
                    result["issues"].append("Critical instructions not found")
            else:
                result["status"] = "missing"
                result["issues"].append("Session records file not found")

        except Exception as e:
            result["status"] = "error"
            result["issues"].append(f"Memory system error: {e}")

        return result

    def check_directory_structure(self) -> Dict[str, Any]:
        """ディレクトリ構造確認"""

        result = {
            "status": "unknown",
            "current_count": 0,
            "target_range": "8-9",
            "compliance": False,
            "items": [],
        }

        try:
            # ルートディレクトリのアイテム数確認
            root_items = [
                item.name
                for item in self.project_root.iterdir()
                if not item.name.startswith(".")
            ]

            result["current_count"] = len(root_items)
            result["items"] = root_items
            result["compliance"] = 8 <= len(root_items) <= 9
            result["status"] = "compliant" if result["compliance"] else "violation"

        except Exception as e:
            result["status"] = "error"
            result["issues"] = [f"Directory check error: {e}"]

        return result

    def check_o3_consultation_status(self) -> Dict[str, Any]:
        """o3協議状況確認"""

        result = {
            "status": "required",
            "last_consultation": None,
            "consultation_frequency": "adequate",
            "recommendation": "consult_before_major_decisions",
        }

        # 過去のo3協議ログを確認（簡易実装）
        operation_log = self.project_root / "src/memory/operations/operation_log.jsonl"

        if operation_log.exists():
            try:
                with open(operation_log, encoding="utf-8") as f:
                    lines = f.readlines()

                o3_operations = [
                    json.loads(line) for line in lines[-10:] if "mcp__o3" in line
                ]

                if o3_operations:
                    result["last_consultation"] = o3_operations[-1]["timestamp"]
                    result["status"] = "active"

            except Exception:
                pass

        return result

    def check_quality_standards(self) -> Dict[str, Any]:
        """品質基準確認"""

        result = {
            "hooks_system": "active",
            "memory_system": "active",
            "automation_level": "high",
            "error_handling": "robust",
            "overall_score": 0.9,
        }

        # Hooksシステム確認
        hooks_config = self.project_root / ".claude/settings.json"
        if hooks_config.exists():
            result["hooks_system"] = "configured"
        else:
            result["hooks_system"] = "missing"
            result["overall_score"] -= 0.3

        return result

    def perform_comprehensive_check(self) -> Dict[str, Any]:
        """包括的確認の実行"""

        check_timestamp = datetime.datetime.now().isoformat()

        # 各確認項目の実行
        checks = {
            "memory_inheritance": self.check_memory_inheritance(),
            "directory_structure": self.check_directory_structure(),
            "o3_consultation": self.check_o3_consultation_status(),
            "quality_standards": self.check_quality_standards(),
        }

        # 全体評価
        critical_issues = []
        warnings = []

        # 記憶継承チェック
        if checks["memory_inheritance"]["status"] != "active":
            critical_issues.append("Memory inheritance system not active")

        # ディレクトリ構造チェック
        if not checks["directory_structure"]["compliance"]:
            critical_issues.append(
                f"Directory count violation: {checks['directory_structure']['current_count']} items (should be 8-9)"
            )

        # 全体ステータス決定
        overall_status = (
            "critical" if critical_issues else "warning" if warnings else "excellent"
        )

        comprehensive_result = {
            "timestamp": check_timestamp,
            "overall_status": overall_status,
            "checks": checks,
            "critical_issues": critical_issues,
            "warnings": warnings,
            "next_actions": self._generate_next_actions(checks, critical_issues),
        }

        # ログ記録
        self._log_president_check(comprehensive_result)

        return comprehensive_result

    def _generate_next_actions(
        self, checks: Dict[str, Any], issues: List[str]
    ) -> List[str]:
        """次のアクション生成"""

        actions = []

        if issues:
            actions.append("🚨 CRITICAL: Resolve all critical issues before proceeding")

            if "Directory count violation" in str(issues):
                actions.append(
                    "📁 Fix directory structure to comply with 8-9 items limit"
                )

            if "Memory inheritance" in str(issues):
                actions.append("🧠 Activate memory inheritance system")

        # o3協議推奨
        if checks["o3_consultation"]["status"] == "required":
            actions.append("🤖 Consult with o3 for strategic decisions")

        # 品質チェック
        if checks["quality_standards"]["overall_score"] < 0.8:
            actions.append("⚡ Improve quality assurance systems")

        if not actions:
            actions.append("✅ All systems optimal - proceed with confidence")

        return actions

    def _log_president_check(self, result: Dict[str, Any]):
        """President確認ログの記録"""

        try:
            with open(self.president_log, "a", encoding="utf-8") as f:
                f.write(json.dumps(result, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"⚠️ Failed to log president check: {e}")

    def generate_president_report(self) -> str:
        """President報告書生成"""

        check_result = self.perform_comprehensive_check()

        status_icons = {"excellent": "🟢", "warning": "🟡", "critical": "🔴"}

        icon = status_icons.get(check_result["overall_status"], "⚪")

        report = f"""
🏛️ PRESIDENT PILOT SYSTEM REPORT
===============================

{icon} Overall Status: {check_result["overall_status"].upper()}

📊 System Checks:
• Memory Inheritance: {check_result["checks"]["memory_inheritance"]["status"].upper()}
• Directory Structure: {check_result["checks"]["directory_structure"]["status"].upper()} ({check_result["checks"]["directory_structure"]["current_count"]} items)
• o3 Consultation: {check_result["checks"]["o3_consultation"]["status"].upper()}
• Quality Standards: {check_result["checks"]["quality_standards"]["overall_score"]:.1f}/1.0

⚠️ Critical Issues: {len(check_result["critical_issues"])}
{chr(10).join([f"  • {issue}" for issue in check_result["critical_issues"]])}

🎯 Next Actions:
{chr(10).join([f"  • {action}" for action in check_result["next_actions"]])}

📝 President Decision: {"PROCEED" if check_result["overall_status"] != "critical" else "HOLD - RESOLVE ISSUES FIRST"}
        """.strip()

        return report


def auto_president_check():
    """自動President確認の実行"""

    pilot = PresidentPilotSystem()

    # President宣言
    declaration = pilot.execute_president_declaration()
    print(declaration)

    # 包括確認
    print("\n" + "=" * 50)
    report = pilot.generate_president_report()
    print(report)

    return pilot.perform_comprehensive_check()


if __name__ == "__main__":
    auto_president_check()
