"""
QualityGateSystem Tests
品質ゲートシステムのテスト
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import sys

sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent / "src"))

from session_management.infrastructure.quality.quality_gate_system import (
    QualityGateSystem,
    QualityGateConfiguration,
    QualityChecker,
    QualityCheckType,
    QualityStatus,
    GatePolicy,
    QualityCheckResult,
    QualityMetrics
)


class TestQualityMetrics:
    """QualityMetricsのテスト"""

    def test_calculate_overall_score(self):
        """総合品質スコア計算"""
        metrics = QualityMetrics(
            test_coverage_percentage=90.0,
            test_pass_rate=0.95,
            linting_issues=5,
            security_vulnerabilities=0,
            performance_score=80.0,
            documentation_coverage=70.0
        )

        score = metrics.calculate_overall_score()

        # スコアが妥当な範囲内であることを確認
        assert 0 <= score <= 100
        assert score > 80  # 良好な指標なので高スコアを期待


class TestQualityCheckResult:
    """QualityCheckResultのテスト"""

    def test_success_completion(self):
        """成功完了"""
        result = QualityCheckResult(
            check_type=QualityCheckType.UNIT_TESTS,
            status=QualityStatus.RUNNING,
            start_time=datetime.now()
        )

        result.complete_with_success("Tests passed", {"passed": 10, "failed": 0})

        assert result.is_success()
        assert result.status == QualityStatus.PASSED
        assert result.exit_code == 0
        assert result.metrics["passed"] == 10

    def test_failure_completion(self):
        """失敗完了"""
        result = QualityCheckResult(
            check_type=QualityCheckType.LINTING,
            status=QualityStatus.RUNNING,
            start_time=datetime.now()
        )

        result.complete_with_failure("Linting failed", "Error output", 1)

        assert result.is_failure()
        assert result.status == QualityStatus.FAILED
        assert result.exit_code == 1
        assert "Error output" in result.error_output


class TestQualityChecker:
    """QualityCheckerのテスト"""

    def setup_method(self):
        """テストセットアップ"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.checker = QualityChecker(self.temp_dir)

    @patch('subprocess.run')
    def test_run_unit_tests_success(self, mock_subprocess):
        """単体テスト実行（成功）"""
        mock_subprocess.return_value = Mock(
            returncode=0,
            stdout="10 passed in 1.23s",
            stderr=""
        )

        result = self.checker.run_unit_tests()

        assert result.is_success()
        assert result.check_type == QualityCheckType.UNIT_TESTS
        assert "10 passed" in result.output

    @patch('subprocess.run')
    def test_run_unit_tests_failure(self, mock_subprocess):
        """単体テスト実行（失敗）"""
        mock_subprocess.return_value = Mock(
            returncode=1,
            stdout="5 passed, 2 failed",
            stderr="AssertionError: Test failed"
        )

        result = self.checker.run_unit_tests()

        assert result.is_failure()
        assert "AssertionError" in result.error_output

    @patch('subprocess.run')
    def test_run_linting_check(self, mock_subprocess):
        """リントチェック実行"""
        mock_subprocess.return_value = Mock(
            returncode=0,
            stdout="",
            stderr="src/test.py:10:80: E501 line too long\nsrc/test.py:15:20: W291 trailing whitespace\nsrc/test.py:20:1: F401 unused import\nsrc/test.py:25:5: E302 expected 2 blank lines\nsrc/test.py:30:10: W292 no newline at end of file"
        )

        result = self.checker.run_linting_check()

        assert result.check_type == QualityCheckType.LINTING
        assert result.metrics["total_issues"] == 5

    def test_parse_pytest_output(self):
        """pytest出力解析"""
        output = "test_file.py::test_function PASSED\n================= 10 passed, 2 failed in 5.23s =================="

        metrics = self.checker._parse_pytest_output(output)

        assert metrics["passed"] == 10
        assert metrics["failed"] == 2
        assert metrics["total_tests"] == 12

    def test_parse_flake8_output(self):
        """flake8出力解析"""
        output = """
        src/test.py:10:80: E501 line too long
        src/test.py:15:20: W291 trailing whitespace
        src/test.py:20:1: F401 unused import
        """

        metrics = self.checker._parse_flake8_output(output, "")

        assert metrics["total_issues"] == 3
        assert "E501" in metrics["issue_types"]
        assert "W291" in metrics["issue_types"]
        assert "F401" in metrics["issue_types"]


class TestQualityGateConfiguration:
    """QualityGateConfigurationのテスト"""

    def test_default_configuration(self):
        """デフォルト設定"""
        config = QualityGateConfiguration(
            gate_name="test_gate",
            policy=GatePolicy.MODERATE,
            enabled_checks={QualityCheckType.UNIT_TESTS, QualityCheckType.LINTING}
        )

        assert config.gate_name == "test_gate"
        assert config.policy == GatePolicy.MODERATE
        assert config.minimum_test_coverage == 80.0
        assert config.timeout_seconds == 300
        assert config.parallel_execution is True


class TestQualityGateSystem:
    """QualityGateSystemのテスト"""

    def setup_method(self):
        """テストセットアップ"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config = QualityGateConfiguration(
            gate_name="test_gate",
            policy=GatePolicy.LENIENT,
            enabled_checks={QualityCheckType.UNIT_TESTS, QualityCheckType.LINTING},
            parallel_execution=False  # テスト用に順次実行
        )
        self.logger = Mock()
        self.system = QualityGateSystem(self.config, self.temp_dir, self.logger)

    def test_system_initialization(self):
        """システム初期化"""
        assert self.system.config == self.config
        assert self.system.project_root == self.temp_dir
        assert self.system.logger == self.logger
        assert self.system.checker is not None
        assert len(self.system.execution_history) == 0

    @patch.object(QualityChecker, 'run_unit_tests')
    @patch.object(QualityChecker, 'run_linting_check')
    def test_execute_quality_gate_success(self, mock_linting, mock_unit_tests):
        """品質ゲート実行（成功）"""
        # モック設定
        mock_unit_tests.return_value = QualityCheckResult(
            check_type=QualityCheckType.UNIT_TESTS,
            status=QualityStatus.PASSED,
            start_time=datetime.now(),
            metrics={"total_tests": 10, "pass_rate": 1.0}
        )
        mock_unit_tests.return_value.complete_with_success("Tests passed")

        mock_linting.return_value = QualityCheckResult(
            check_type=QualityCheckType.LINTING,
            status=QualityStatus.PASSED,
            start_time=datetime.now(),
            metrics={"total_issues": 0}
        )
        mock_linting.return_value.complete_with_success("No linting issues")

        # 実行
        result = self.system.execute_quality_gate()

        # 検証
        assert result["passed"] is True
        assert "execution_id" in result
        assert "results" in result
        assert "metrics" in result
        assert len(self.system.execution_history) == 1

    @patch.object(QualityChecker, 'run_unit_tests')
    def test_execute_quality_gate_failure(self, mock_unit_tests):
        """品質ゲート実行（失敗）"""
        # モック設定（テスト失敗）
        mock_unit_tests.return_value = QualityCheckResult(
            check_type=QualityCheckType.UNIT_TESTS,
            status=QualityStatus.FAILED,
            start_time=datetime.now()
        )
        mock_unit_tests.return_value.complete_with_failure("Tests failed")

        # 実行
        result = self.system.execute_quality_gate()

        # 検証
        assert result["passed"] is False
        # 結果の構造を確認して適切にアクセス
        if "results" in result and QualityCheckType.UNIT_TESTS in result["results"]:
            assert result["results"][QualityCheckType.UNIT_TESTS]["status"] == "FAILED"
        elif "results" in result and QualityCheckType.UNIT_TESTS.value in result["results"]:
            assert result["results"][QualityCheckType.UNIT_TESTS.value]["status"] == "FAILED"

    def test_evaluate_results_strict_policy(self):
        """結果評価（STRICT ポリシー）"""
        self.system.config = QualityGateConfiguration(
            gate_name="strict_gate",
            policy=GatePolicy.STRICT,
            enabled_checks={QualityCheckType.UNIT_TESTS, QualityCheckType.LINTING}
        )

        # 全て成功
        results = {
            QualityCheckType.UNIT_TESTS: QualityCheckResult(
                check_type=QualityCheckType.UNIT_TESTS,
                status=QualityStatus.PASSED,
                start_time=datetime.now()
            ),
            QualityCheckType.LINTING: QualityCheckResult(
                check_type=QualityCheckType.LINTING,
                status=QualityStatus.PASSED,
                start_time=datetime.now()
            )
        }

        passed, metrics = self.system._evaluate_results(results)
        assert passed is True

        # 一つでも失敗
        results[QualityCheckType.LINTING].status = QualityStatus.FAILED
        passed, metrics = self.system._evaluate_results(results)
        assert passed is False

    def test_evaluate_results_moderate_policy(self):
        """結果評価（MODERATE ポリシー）"""
        self.system.config = QualityGateConfiguration(
            gate_name="moderate_gate",
            policy=GatePolicy.MODERATE,
            enabled_checks={QualityCheckType.UNIT_TESTS, QualityCheckType.LINTING}
        )

        # テストは成功、リントは失敗
        results = {
            QualityCheckType.UNIT_TESTS: QualityCheckResult(
                check_type=QualityCheckType.UNIT_TESTS,
                status=QualityStatus.PASSED,
                start_time=datetime.now()
            ),
            QualityCheckType.LINTING: QualityCheckResult(
                check_type=QualityCheckType.LINTING,
                status=QualityStatus.FAILED,
                start_time=datetime.now()
            )
        }

        # 重要チェック（テスト）が成功していれば合格
        passed, metrics = self.system._evaluate_results(results)
        assert passed is True

    def test_custom_rules_application(self):
        """カスタムルール適用"""
        metrics = QualityMetrics(
            test_coverage_percentage=85.0,
            test_pass_rate=0.97,
            linting_issues=5
        )

        results = {}

        # 全ルール満足
        passed = self.system._apply_custom_rules(results, metrics)
        assert passed is True

        # カバレッジ不足
        metrics.test_coverage_percentage = 70.0
        passed = self.system._apply_custom_rules(results, metrics)
        assert passed is False

    def test_generate_summary(self):
        """サマリー生成"""
        results = {
            QualityCheckType.UNIT_TESTS: QualityCheckResult(
                check_type=QualityCheckType.UNIT_TESTS,
                status=QualityStatus.PASSED,
                start_time=datetime.now(),
                duration_seconds=2.5
            ),
            QualityCheckType.LINTING: QualityCheckResult(
                check_type=QualityCheckType.LINTING,
                status=QualityStatus.FAILED,
                start_time=datetime.now(),
                duration_seconds=1.2
            )
        }

        summary = self.system._generate_summary(results, False)

        assert summary["overall_status"] == "FAILED"
        assert summary["total_checks"] == 2
        assert summary["passed_checks"] == 1
        assert summary["failed_checks"] == 1
        assert summary["total_duration_seconds"] == 3.7

    def test_get_execution_history(self):
        """実行履歴取得"""
        # 初期状態
        history = self.system.get_execution_history()
        assert len(history) == 0

        # 履歴追加
        self.system.execution_history.append({
            "execution_id": "test_1",
            "status": "completed",
            "overall_passed": True
        })

        history = self.system.get_execution_history()
        assert len(history) == 1
        assert history[0]["execution_id"] == "test_1"

    def test_get_current_status(self):
        """現在の実行状況取得"""
        # 実行前
        status = self.system.get_current_status()
        assert status is None

        # 実行中状態をシミュレート
        self.system.current_execution = {
            "execution_id": "current_test",
            "status": "running",
            "start_time": datetime.now()
        }

        status = self.system.get_current_status()
        assert status is not None
        assert status["status"] == "running"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])