#!/usr/bin/env python3
"""
CI自動回帰テストシステム - 78回ミスの再発防止保証
o3推奨の「fail-fast」システム実装
"""

import json
import sys
import time
from pathlib import Path
from typing import Dict, List

# プロジェクトルート設定
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "src/memory/core"))

# 直接インポートできない場合の対処
try:
    from runtime_advisor import RuntimeAdvisor
except ModuleNotFoundError:
    # ファイルを直接実行してクラスをインポート
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "runtime_advisor", "src/memory/core/runtime_advisor.py"
    )
    runtime_advisor_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runtime_advisor_module)
    RuntimeAdvisor = runtime_advisor_module.RuntimeAdvisor


class MistakePreventionCI:
    def __init__(self):
        self.advisor = RuntimeAdvisor()
        self.test_results = []
        self.failed_tests = []

    def load_test_scenarios(self) -> List[Dict]:
        """テストシナリオの読み込み"""
        db_path = PROJECT_ROOT / "src/memory/persistent-learning/mistakes-database.json"

        try:
            with open(db_path, encoding="utf-8") as f:
                db = json.load(f)
                return db.get("test_scenarios", [])
        except Exception as e:
            print(f"❌ テストシナリオ読み込みエラー: {e}")
            return []

    def run_pattern_detection_test(self, test_case: Dict) -> Dict:
        """パターン検出テストの実行"""
        test_id = test_case["test_id"]
        input_text = test_case["input"]
        expected_detection = test_case["expected_detection"]
        expected_action = test_case["expected_action"]

        print(f"🧪 テスト実行: {test_id}")
        print(f"   入力: {input_text}")

        # Runtime Advisorで分析
        analysis = self.advisor.analyze_input(input_text)

        # 検出結果確認
        detected_ids = [
            pattern["mistake_id"] for pattern in analysis["detected_patterns"]
        ]
        detected_actions = [
            pattern["trigger_action"] for pattern in analysis["detected_patterns"]
        ]

        # テスト結果判定
        detection_success = expected_detection in detected_ids
        action_success = expected_action in detected_actions
        overall_success = detection_success and action_success

        result = {
            "test_id": test_id,
            "input": input_text,
            "expected_detection": expected_detection,
            "expected_action": expected_action,
            "detected_ids": detected_ids,
            "detected_actions": detected_actions,
            "detection_success": detection_success,
            "action_success": action_success,
            "overall_success": overall_success,
            "risk_score": analysis["risk_score"],
            "timestamp": time.time(),
        }

        # 結果表示
        status = "✅ PASS" if overall_success else "❌ FAIL"
        print(f"   結果: {status}")
        if not overall_success:
            print(f"   期待検出: {expected_detection}, 実際: {detected_ids}")
            print(f"   期待アクション: {expected_action}, 実際: {detected_actions}")

        return result

    def run_comprehensive_pattern_tests(self) -> List[Dict]:
        """包括的パターンテストの実行"""
        print("🚀 包括的ミス防止テスト開始")
        print("=" * 50)

        test_scenarios = self.load_test_scenarios()
        results = []

        for scenario in test_scenarios:
            result = self.run_pattern_detection_test(scenario)
            results.append(result)
            self.test_results.append(result)

            if not result["overall_success"]:
                self.failed_tests.append(result)

        return results

    def run_high_risk_phrase_tests(self) -> List[Dict]:
        """高リスクフレーズテスト"""
        print("\n🔴 高リスクフレーズテスト")
        print("-" * 30)

        high_risk_phrases = [
            "AI組織4画面フル稼働中です！",
            "システム完了しました",
            "確認できました、問題ありません",
            "おそらく正常に動作しています",
            "たぶん大丈夫だと思います",
            "README.mdをルートに作成",
            "project/file.txt",
            "チェック済みです",
            "後で対応します",
        ]

        results = []
        for phrase in high_risk_phrases:
            analysis = self.advisor.analyze_input(phrase)

            # 高リスクフレーズは必ず検出されるべき
            should_detect = (
                analysis["risk_score"] > 0 or len(analysis["detected_patterns"]) > 0
            )

            result = {
                "test_type": "high_risk_phrase",
                "input": phrase,
                "risk_score": analysis["risk_score"],
                "detected_patterns": len(analysis["detected_patterns"]),
                "should_detect": should_detect,
                "success": should_detect,
            }

            results.append(result)
            self.test_results.append(result)

            status = "✅ 検出" if should_detect else "❌ 未検出"
            print(f"   {phrase[:30]}... → {status} (スコア: {analysis['risk_score']})")

            if not should_detect:
                self.failed_tests.append(result)

        return results

    def run_output_safety_tests(self) -> List[Dict]:
        """出力安全性テスト"""
        print("\n🛡️ 出力安全性テスト")
        print("-" * 20)

        dangerous_outputs = [
            "システムは正常に稼働中です",
            "完了しました、問題ありません",
            "確認できました、すべて正常です",
            "実装済みです",
            "対応済みです",
        ]

        results = []
        for output in dangerous_outputs:
            safety_check = self.advisor.check_output_safety(output)

            # 危険な出力は安全性スコアが低くなるべき
            is_dangerous = safety_check["safety_score"] < 80

            result = {
                "test_type": "output_safety",
                "output": output,
                "safety_score": safety_check["safety_score"],
                "violations": len(safety_check["safety_violations"]),
                "requires_evidence": safety_check["requires_evidence"],
                "is_dangerous": is_dangerous,
                "success": is_dangerous,  # 危険として検出されれば成功
            }

            results.append(result)
            self.test_results.append(result)

            status = "✅ 危険検出" if is_dangerous else "❌ 検出漏れ"
            print(
                f"   {output[:30]}... → {status} (スコア: {safety_check['safety_score']})"
            )

            if not is_dangerous:
                self.failed_tests.append(result)

        return results

    def generate_test_report(self) -> Dict:
        """テストレポート生成"""
        total_tests = len(self.test_results)
        failed_tests = len(self.failed_tests)
        passed_tests = total_tests - failed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        return {
            "test_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": round(success_rate, 2),
            },
            "failed_test_details": self.failed_tests,
            "timestamp": time.time(),
            "ci_status": "PASS" if failed_tests == 0 else "FAIL",
        }

    def save_test_results(self, report: Dict):
        """テスト結果保存"""
        results_dir = PROJECT_ROOT / "tests/results"
        results_dir.mkdir(exist_ok=True)

        timestamp = int(time.time())
        results_file = results_dir / f"mistake-prevention-test-{timestamp}.json"

        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n📊 テスト結果保存: {results_file}")

    def run_full_ci_suite(self) -> bool:
        """完全CI自動テストスイート実行"""
        print("🚀 78回ミス防止 CI テストスイート開始")
        print("=" * 60)

        # 各テストカテゴリ実行
        self.run_comprehensive_pattern_tests()
        self.run_high_risk_phrase_tests()
        self.run_output_safety_tests()

        # レポート生成
        report = self.generate_test_report()

        # 結果表示
        print("\n" + "=" * 60)
        print("📊 最終テスト結果")
        print("=" * 60)
        print(f"総テスト数: {report['test_summary']['total_tests']}")
        print(f"成功: {report['test_summary']['passed_tests']}")
        print(f"失敗: {report['test_summary']['failed_tests']}")
        print(f"成功率: {report['test_summary']['success_rate']}%")
        print(f"CI ステータス: {report['ci_status']}")

        # 失敗詳細
        if report["test_summary"]["failed_tests"] > 0:
            print("\n❌ 失敗したテスト:")
            for i, failed in enumerate(self.failed_tests[:5], 1):  # 最初の5件のみ表示
                print(
                    f"   {i}. {failed.get('test_id', failed.get('test_type', 'Unknown'))}"
                )
                if "input" in failed:
                    print(f"      入力: {failed['input'][:50]}...")

        # 結果保存
        self.save_test_results(report)

        # CI判定
        ci_passed = report["ci_status"] == "PASS"

        if ci_passed:
            print("\n🎉 78回ミス防止システム: 全テスト合格!")
            print("✅ 同じミスの再発は技術的に防止されています")
        else:
            print("\n🚨 78回ミス防止システム: テスト失敗!")
            print("❌ ミス防止システムに不備があります - 修正が必要")

        return ci_passed


def main():
    """メイン処理"""
    ci = MistakePreventionCI()

    # 引数チェック
    if len(sys.argv) > 1:
        if sys.argv[1] == "--quick":
            # クイックテスト（高リスクフレーズのみ）
            _ = ci.run_high_risk_phrase_tests()
            report = ci.generate_test_report()
            success = report["ci_status"] == "PASS"
        else:
            print("使用法: python3 mistake-prevention-ci.py [--quick]")
            return
    else:
        # フルテストスイート
        success = ci.run_full_ci_suite()

    # 終了コード設定（CI用）
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
