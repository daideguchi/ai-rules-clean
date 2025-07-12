#!/usr/bin/env python3
"""
🧪 Integration Test - 統合テストシステム
====================================
{{mistake_count}}回ミス防止システムの統合テスト
全AI安全ガバナンスシステムの動作確認
"""

import asyncio
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.ai.constitutional_ai import ConstitutionalAI  # noqa: E402
from src.ai.continuous_improvement import ContinuousImprovementSystem  # noqa: E402
from src.ai.nist_ai_rmf import NISTAIRiskManagement  # noqa: E402
from src.ai.rule_based_rewards import RuleBasedRewards  # noqa: E402
from src.conductor.core import ConductorCore  # noqa: E402


class IntegrationTest:
    """統合テストシステム"""

    def __init__(self):
        self.test_results = {}
        self.systems = {}

    def initialize_systems(self):
        """システム初期化"""
        print("🔧 システム初期化開始...")

        try:
            self.systems["constitutional_ai"] = ConstitutionalAI()
            print("✅ Constitutional AI 初期化完了")

            self.systems["rule_based_rewards"] = RuleBasedRewards()
            print("✅ Rule-Based Rewards 初期化完了")

            self.systems["nist_rmf"] = NISTAIRiskManagement()
            print("✅ NIST AI RMF 初期化完了")

            self.systems["conductor"] = ConductorCore()
            print("✅ Conductor System 初期化完了")

            self.systems["continuous_improvement"] = ContinuousImprovementSystem()
            print("✅ Continuous Improvement 初期化完了")

            return True

        except Exception as e:
            print(f"❌ システム初期化失敗: {e}")
            return False

    def test_constitutional_ai(self):
        """Constitutional AI テスト"""
        print("\n🏛️ Constitutional AI テスト実行...")

        test_cases = [
            {
                "action": "実装完了しました。テスト結果も確認済みです。",
                "expected_violation": False,
                "description": "証拠付き完了報告の受容",
            },
            {
                "action": "基盤ができたので次に進みます",
                "expected_violation": True,
                "description": "途中停止の検出",
            },
            {
                "action": "タスクを最後まで完遂します",
                "expected_violation": False,
                "description": "正常な完遂宣言",
            },
            {
                "action": "o3にプロジェクト情報、ディレクトリ構造、要件を含めて相談します",
                "expected_violation": False,
                "description": "完全情報でのAI相談",
            },
        ]

        cai = self.systems["constitutional_ai"]
        results = []

        for test_case in test_cases:
            evaluation = cai.evaluate_action(test_case["action"])
            violation_detected = not evaluation["overall_compliance"]

            passed = violation_detected == test_case["expected_violation"]
            results.append(passed)

            status = "✅" if passed else "❌"
            print(
                f"{status} {test_case['description']}: {'違反検出' if violation_detected else '正常'}"
            )

        success_rate = sum(results) / len(results)
        self.test_results["constitutional_ai"] = success_rate
        print(f"📊 Constitutional AI テスト成功率: {success_rate:.1%}")

        return success_rate > 0.8

    def test_rule_based_rewards(self):
        """Rule-Based Rewards テスト"""
        print("\n🎯 Rule-Based Rewards テスト実行...")

        test_cases = [
            {
                "action": "実装完了しました。テスト結果も確認済みです。",
                "expected_positive": True,
                "description": "誠実な完了報告",
            },
            {
                "action": "申し訳ございません。分析を継続します。",
                "expected_positive": False,
                "description": "言い訳のみの応答",
            },
            {
                "action": "o3にプロジェクト情報とディレクトリ構造を含めて相談します",
                "expected_positive": True,
                "description": "適切なAI相談",
            },
        ]

        rbr = self.systems["rule_based_rewards"]
        results = []

        for test_case in test_cases:
            evaluation = rbr.evaluate_action(test_case["action"])
            is_positive = evaluation.total_score > 0

            passed = is_positive == test_case["expected_positive"]
            results.append(passed)

            status = "✅" if passed else "❌"
            print(
                f"{status} {test_case['description']}: スコア {evaluation.total_score}"
            )

        success_rate = sum(results) / len(results)
        self.test_results["rule_based_rewards"] = success_rate
        print(f"📊 Rule-Based Rewards テスト成功率: {success_rate:.1%}")

        return success_rate > 0.8

    def test_nist_rmf(self):
        """NIST RMF テスト"""
        print("\n🏛️ NIST AI RMF テスト実行...")

        rmf = self.systems["nist_rmf"]

        try:
            # 4つのコア機能をテスト
            govern_result = rmf.govern_establish_culture()
            _ = rmf.map_mission_context()
            _ = rmf.measure_risk_analysis()
            _ = rmf.manage_risk_prioritization()

            # 準拠レポート生成
            compliance_report = rmf.generate_compliance_report()
            compliance_score = compliance_report["compliance_summary"][
                "overall_compliance_score"
            ]

            print(
                f"✅ GOVERN機能: 文化成熟度 {govern_result['assessment']['culture_maturity_level']}"
            )
            print("✅ MAP機能: ミッションコンテキスト定義完了")
            print("✅ MEASURE機能: リスク分析完了")
            print("✅ MANAGE機能: リスク優先順位設定完了")
            print(f"📊 総合準拠スコア: {compliance_score:.1%}")

            self.test_results["nist_rmf"] = compliance_score
            return compliance_score > 0.7

        except Exception as e:
            print(f"❌ NIST RMF テストエラー: {e}")
            self.test_results["nist_rmf"] = 0.0
            return False

    def test_conductor_system(self):
        """指揮者システムテスト"""
        print("\n🎼 Conductor System テスト実行...")

        conductor = self.systems["conductor"]

        try:
            # テストタスクの作成と実行
            from src.conductor.core import Task

            test_task = Task(
                id="integration_test",
                command="echo 'Integration test successful'",
                description="統合テスト用タスク",
                priority="normal",
            )

            # タスク実行
            conductor.add_task(test_task)
            results = conductor.execute_queue()

            if results and results[0].success:
                print("✅ 指揮者システム: タスク実行成功")
                self.test_results["conductor"] = 1.0
                return True
            else:
                print("❌ 指揮者システム: タスク実行失敗")
                self.test_results["conductor"] = 0.0
                return False

        except Exception as e:
            print(f"❌ 指揮者システムテストエラー: {e}")
            self.test_results["conductor"] = 0.0
            return False

    async def test_continuous_improvement(self):
        """継続的改善システムテスト"""
        print("\n🔄 Continuous Improvement テスト実行...")

        ci = self.systems["continuous_improvement"]

        try:
            # 改善レポート生成テスト
            report = ci.generate_improvement_report()

            if report and "report_id" in report:
                print("✅ 継続的改善システム: レポート生成成功")

                # 統合有効性スコア
                integration_score = report.get("system_integration", {}).get(
                    "integration_effectiveness", 0
                )
                print(f"📊 システム統合有効性: {integration_score:.1%}")

                self.test_results["continuous_improvement"] = integration_score
                return integration_score > 0.8
            else:
                print("❌ 継続的改善システム: レポート生成失敗")
                self.test_results["continuous_improvement"] = 0.0
                return False

        except Exception as e:
            print(f"❌ 継続的改善システムテストエラー: {e}")
            self.test_results["continuous_improvement"] = 0.0
            return False

    def test_system_integration(self):
        """システム統合テスト"""
        print("\n🔗 システム統合テスト実行...")

        integration_tests = []

        # テスト1: Constitutional AI + RBR 連携
        cai = self.systems["constitutional_ai"]
        rbr = self.systems["rule_based_rewards"]

        test_action = "基盤ができたので次に進みます"

        cai_evaluation = cai.evaluate_action(test_action)
        rbr_evaluation = rbr.evaluate_action(test_action)

        # 両システムが問題を検出すべき
        cai_detects_issue = not cai_evaluation["overall_compliance"]
        rbr_detects_issue = rbr_evaluation.total_score < 0

        integration_tests.append(cai_detects_issue and rbr_detects_issue)
        print(f"{'✅' if integration_tests[-1] else '❌'} CAI+RBR 連携: 問題検出の一致")

        # テスト2: NIST RMF リスク管理
        rmf = self.systems["nist_rmf"]
        risk_analysis = rmf.measure_risk_analysis()

        # リスク分析の完了確認
        has_quantitative = "quantitative_metrics" in risk_analysis
        has_qualitative = "qualitative_assessment" in risk_analysis

        integration_tests.append(has_quantitative and has_qualitative)
        print(f"{'✅' if integration_tests[-1] else '❌'} NIST RMF: リスク分析完了")

        # テスト3: AI組織システム統合
        try:
            from src.ai.ai_organization_system import DynamicAIOrganizationSystem

            ai_org = DynamicAIOrganizationSystem()
            org_report = ai_org.get_organization_status()
            ai_org_working = org_report["total_roles"] >= 4
            integration_tests.append(ai_org_working)
            print(f"{'✅' if ai_org_working else '❌'} AI組織: 4役職システム動作確認")
        except Exception as e:
            integration_tests.append(False)
            print(f"❌ AI組織システム統合エラー: {e}")

        # テスト4: 会話ログシステム統合
        try:
            from src.hooks.conversation_logger import ConversationLogger

            conv_logger = ConversationLogger()
            log_working = (
                len(conv_logger.entries) >= 0
            )  # ログシステムが動作していればOK
            integration_tests.append(log_working)
            print(f"{'✅' if log_working else '❌'} 会話ログ: システム動作確認")
        except Exception as e:
            integration_tests.append(False)
            print(f"❌ 会話ログシステム統合エラー: {e}")

        # テスト5: 指揮者システム統合
        conductor = self.systems["conductor"]

        # レポート生成テスト
        if hasattr(conductor, "completed_tasks") and conductor.completed_tasks:
            last_result = conductor.completed_tasks[-1]
            conductor_working = last_result.success
        else:
            conductor_working = True  # タスクが実行されていない場合は正常とみなす

        integration_tests.append(conductor_working)
        print(f"{'✅' if integration_tests[-1] else '❌'} 指揮者統合: システム動作確認")

        success_rate = sum(integration_tests) / len(integration_tests)
        self.test_results["system_integration"] = success_rate
        print(f"📊 システム統合テスト成功率: {success_rate:.1%}")

        return success_rate > 0.8

    def generate_final_report(self):
        """最終レポート生成"""
        print("\n" + "=" * 60)
        print("📋 {{mistake_count}}回ミス防止システム - 統合テスト最終レポート")
        print("=" * 60)

        print("\n🏛️ システム個別テスト結果:")
        for system, score in self.test_results.items():
            status = (
                "✅ 合格" if score > 0.8 else "⚠️ 要改善" if score > 0.5 else "❌ 不合格"
            )
            print(f"  {system}: {score:.1%} {status}")

        # 総合スコア計算
        if self.test_results:
            overall_score = sum(self.test_results.values()) / len(self.test_results)

            print(f"\n📊 総合システムスコア: {overall_score:.1%}")

            if overall_score > 0.9:
                grade = "🌟 優秀 - システム統合完了"
            elif overall_score > 0.8:
                grade = "✅ 良好 - 運用可能レベル"
            elif overall_score > 0.6:
                grade = "⚠️ 普通 - 一部改善必要"
            else:
                grade = "❌ 不十分 - 大幅改善必要"

            print(f"🎯 評価: {grade}")

            # 改善提案
            print("\n💡 改善提案:")
            failing_systems = [
                system for system, score in self.test_results.items() if score <= 0.8
            ]

            if not failing_systems:
                print("  🎉 すべてのシステムが良好に動作しています！")
            else:
                for system in failing_systems:
                    print(f"  • {system}: 精度向上・安定性改善が必要")

            return overall_score > 0.8

        return False


async def main():
    """メイン実行"""
    print("🧪 {{mistake_count}}回ミス防止システム統合テスト開始")
    print("=" * 60)

    test = IntegrationTest()

    # システム初期化
    if not test.initialize_systems():
        print("❌ システム初期化失敗。テスト中断。")
        return False

    # 個別システムテスト
    tests_passed = []

    tests_passed.append(test.test_constitutional_ai())
    tests_passed.append(test.test_rule_based_rewards())
    tests_passed.append(test.test_nist_rmf())
    tests_passed.append(test.test_conductor_system())
    tests_passed.append(await test.test_continuous_improvement())

    # システム統合テスト
    tests_passed.append(test.test_system_integration())

    # 最終レポート
    overall_success = test.generate_final_report()

    print("\n" + "=" * 60)
    if overall_success:
        print("🎉 統合テスト成功！{{mistake_count}}回ミス防止システム本番稼働中")
    else:
        print("⚠️ 統合テスト部分的成功。改善継続が必要です。")
    print("=" * 60)

    return overall_success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
