#!/usr/bin/env python3
"""
🧠 Meta-Cognitive Monitoring System
==================================

自己監視・自己制御システム - 1ヶ月間の系統的失敗を防止

根本原因: 自分が作ったルール・システムを自分で守らない
解決策: 強制的な自己監視システム
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


class MetaCognitiveMonitor:
    """
    自己認知監視システム

    目的: 自分自身の処理プロセスを監視・制御
    - 既存システム確認の強制
    - 処理フロー遵守の確認
    - ルール遵守の監視
    - 現実性テストの強制
    """

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.monitor_log = self.project_root / "runtime" / "meta_cognitive_monitor.log"
        self.violations_log = self.project_root / "runtime" / "self_violations.log"

        # 自己監視ルール
        self.self_rules = {
            "search_existing_before_create": True,
            "test_in_real_environment": True,
            "follow_own_process_flow": True,
            "use_japanese_for_reports": True,
            "implement_thinking_tags_for_critical": True,
            "integrate_dont_duplicate": True,
        }

        self.session_violations = []

    def pre_work_check(self, task_description: str) -> Dict[str, Any]:
        """
        作業前必須チェック - 1ヶ月間の失敗パターン防止
        """
        print("🧠 META-COGNITIVE PRE-WORK CHECK")
        print("=" * 50)

        check_results = {
            "task": task_description,
            "timestamp": datetime.now().isoformat(),
            "checks": {},
            "allowed_to_proceed": True,
            "violations": [],
        }

        # Check 1: 既存システム検索済みか
        existing_check = self._check_existing_systems(task_description)
        check_results["checks"]["existing_systems"] = existing_check
        if not existing_check["searched"]:
            check_results["violations"].append("既存システム検索未実行")
            check_results["allowed_to_proceed"] = False

        # Check 2: 処理フロー確認済みか
        flow_check = self._check_process_flow_compliance()
        check_results["checks"]["process_flow"] = flow_check
        if not flow_check["compliant"]:
            check_results["violations"].append("処理フロー未遵守")

        # Check 3: タスクレベルと思考モードの一致確認
        thinking_check = self._check_thinking_mode_requirement(task_description)
        check_results["checks"]["thinking_mode"] = thinking_check
        if thinking_check["required"] and not thinking_check["implemented"]:
            check_results["violations"].append("必要な思考モード未実装")
            check_results["allowed_to_proceed"] = False

        # Check 4: 言語ルール確認
        language_check = self._check_language_compliance()
        check_results["checks"]["language"] = language_check

        # 結果記録
        self._log_check_results(check_results)

        if check_results["violations"]:
            print("❌ META-COGNITIVE VIOLATIONS DETECTED:")
            for violation in check_results["violations"]:
                print(f"   - {violation}")
            print("\n🚫 WORK BLOCKED - Fix violations first")
        else:
            print("✅ META-COGNITIVE CHECKS PASSED")
            print("🎯 Proceeding with work...")

        return check_results

    def _check_existing_systems(self, task: str) -> Dict[str, Any]:
        """既存システム確認チェック"""

        # 起動関連タスクの場合、既存起動システムをチェック
        if any(
            keyword in task.lower()
            for keyword in ["start", "launch", "startup", "起動"]
        ):
            existing_startup_files = list(self.project_root.glob("**/*start*"))
            existing_startup_files.extend(list(self.project_root.glob("scripts/bin/*")))

            return {
                "searched": len(existing_startup_files) > 0,
                "found_systems": [str(f) for f in existing_startup_files[:5]],
                "recommendation": "Use scripts/bin/start-president instead of creating new system",
            }

        return {"searched": True, "found_systems": [], "recommendation": "None"}

    def _check_process_flow_compliance(self) -> Dict[str, Any]:
        """処理フロー遵守確認"""

        # フローエンフォーサーが存在するかチェック
        flow_enforcer = (
            self.project_root / "src" / "enforcement" / "mandatory_flow_enforcer.py"
        )

        return {
            "compliant": flow_enforcer.exists(),
            "flow_enforcer_exists": flow_enforcer.exists(),
            "should_use_enforcer": True,
            "recommendation": "Use MandatoryFlowEnforcer.process_instruction()",
        }

    def _check_thinking_mode_requirement(self, task: str) -> Dict[str, Any]:
        """思考モード要件確認"""

        # CRITICALタスクの判定
        critical_keywords = [
            "critical",
            "failure",
            "root cause",
            "systematic",
            "1ヶ月",
            "month",
        ]
        is_critical = any(keyword in task.lower() for keyword in critical_keywords)

        return {
            "task_level": "CRITICAL" if is_critical else "NORMAL",
            "required": is_critical,
            "thinking_tags_needed": is_critical,
            "implemented": False,  # 実装状況は外部から設定
            "recommendation": "Use <thinking> tags for CRITICAL tasks",
        }

    def _check_language_compliance(self) -> Dict[str, Any]:
        """言語ルール遵守確認"""

        return {
            "rule": "報告は日本語",
            "compliant": True,  # 現在は日本語で実装中
            "recommendation": "Continue using Japanese for reports",
        }

    def _log_check_results(self, results: Dict[str, Any]):
        """チェック結果をログに記録"""

        self.monitor_log.parent.mkdir(exist_ok=True)

        log_entry = {
            "timestamp": results["timestamp"],
            "task": results["task"],
            "violations": results["violations"],
            "allowed": results["allowed_to_proceed"],
        }

        with open(self.monitor_log, "a") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

        # 違反がある場合は違反ログにも記録
        if results["violations"]:
            with open(self.violations_log, "a") as f:
                f.write(f"{results['timestamp']}: {', '.join(results['violations'])}\n")

    def post_work_check(
        self, task: str, implementation_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """作業後検証チェック"""

        print("\n🧠 META-COGNITIVE POST-WORK CHECK")
        print("=" * 50)

        # 実環境テスト確認
        real_env_tested = implementation_details.get("real_environment_tested", False)
        user_confirmed = implementation_details.get("user_confirmed_working", False)

        post_check = {
            "task": task,
            "real_environment_tested": real_env_tested,
            "user_confirmed": user_confirmed,
            "integration_completed": implementation_details.get(
                "integrated_with_existing", False
            ),
            "violations": [],
        }

        if not real_env_tested:
            post_check["violations"].append("実環境テスト未実行")

        if not user_confirmed:
            post_check["violations"].append("ユーザー確認未取得")

        # 結果表示
        if post_check["violations"]:
            print("❌ POST-WORK VIOLATIONS:")
            for violation in post_check["violations"]:
                print(f"   - {violation}")
        else:
            print("✅ POST-WORK CHECKS PASSED")

        return post_check


def demonstrate_meta_cognitive_monitoring():
    """メタ認知監視システムのデモンストレーション"""

    monitor = MetaCognitiveMonitor()

    # 典型的な失敗タスクでテスト
    test_task = "AI organization startup system implementation"

    # 作業前チェック
    pre_check = monitor.pre_work_check(test_task)

    if pre_check["allowed_to_proceed"]:
        print("\n🎯 Simulating work implementation...")

        # 作業後チェック
        post_check = monitor.post_work_check(
            test_task,
            {
                "real_environment_tested": False,  # 典型的な失敗パターン
                "user_confirmed_working": False,
                "integrated_with_existing": False,
            },
        )

    return pre_check, post_check


if __name__ == "__main__":
    demonstrate_meta_cognitive_monitoring()
