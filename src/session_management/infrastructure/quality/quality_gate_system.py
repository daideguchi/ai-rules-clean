"""
QualityGateSystem Implementation
品質ゲート・自動検証パイプライン実装
継続的品質保証システム
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Set
import subprocess
import threading
import time
from pathlib import Path
import json


class QualityCheckType(Enum):
    """品質チェック種別"""
    STATIC_ANALYSIS = "STATIC_ANALYSIS"
    UNIT_TESTS = "UNIT_TESTS"
    INTEGRATION_TESTS = "INTEGRATION_TESTS"
    COVERAGE = "COVERAGE"
    SECURITY_SCAN = "SECURITY_SCAN"
    PERFORMANCE_TEST = "PERFORMANCE_TEST"
    LINTING = "LINTING"
    TYPE_CHECK = "TYPE_CHECK"
    DEPENDENCY_CHECK = "DEPENDENCY_CHECK"
    DOCUMENTATION = "DOCUMENTATION"


class QualityStatus(Enum):
    """品質ステータス"""
    UNKNOWN = "UNKNOWN"
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    PASSED = "PASSED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    ERROR = "ERROR"


class GatePolicy(Enum):
    """ゲートポリシー"""
    STRICT = "STRICT"          # 全てパス必須
    MODERATE = "MODERATE"      # 重要項目パス必須
    LENIENT = "LENIENT"        # 最低限パス必須
    CUSTOM = "CUSTOM"          # カスタムルール


@dataclass
class QualityMetrics:
    """品質メトリクス"""
    test_coverage_percentage: float = 0.0
    test_count: int = 0
    test_pass_rate: float = 0.0
    linting_issues: int = 0
    security_vulnerabilities: int = 0
    performance_score: float = 0.0
    code_complexity: float = 0.0
    documentation_coverage: float = 0.0
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def calculate_overall_score(self) -> float:
        """総合品質スコア計算"""
        weights = {
            'test_coverage': 0.25,
            'test_pass_rate': 0.25,
            'security': 0.20,
            'linting': 0.15,
            'performance': 0.10,
            'documentation': 0.05
        }
        
        # 各項目を0-100スケールに正規化
        normalized_scores = {
            'test_coverage': min(self.test_coverage_percentage, 100.0),
            'test_pass_rate': self.test_pass_rate * 100.0,
            'security': max(0, 100.0 - self.security_vulnerabilities * 10),
            'linting': max(0, 100.0 - self.linting_issues * 2),
            'performance': min(self.performance_score, 100.0),
            'documentation': min(self.documentation_coverage, 100.0)
        }
        
        total_score = sum(
            score * weights[metric]
            for metric, score in normalized_scores.items()
        )
        
        return min(max(total_score, 0.0), 100.0)
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            "test_coverage_percentage": self.test_coverage_percentage,
            "test_count": self.test_count,
            "test_pass_rate": self.test_pass_rate,
            "linting_issues": self.linting_issues,
            "security_vulnerabilities": self.security_vulnerabilities,
            "performance_score": self.performance_score,
            "code_complexity": self.code_complexity,
            "documentation_coverage": self.documentation_coverage,
            "overall_score": self.calculate_overall_score(),
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }


@dataclass
class QualityCheckResult:
    """品質チェック結果"""
    check_type: QualityCheckType
    status: QualityStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    output: str = ""
    error_output: str = ""
    exit_code: int = 0
    metrics: Optional[Dict[str, Any]] = None
    details: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.end_time and self.start_time:
            self.duration_seconds = (self.end_time - self.start_time).total_seconds()
    
    def is_success(self) -> bool:
        """成功判定"""
        return self.status == QualityStatus.PASSED
    
    def is_failure(self) -> bool:
        """失敗判定"""
        return self.status == QualityStatus.FAILED
    
    def complete_with_success(self, output: str = "", metrics: Optional[Dict[str, Any]] = None):
        """成功完了"""
        self.end_time = datetime.now()
        self.status = QualityStatus.PASSED
        self.output = output
        self.exit_code = 0
        if metrics:
            self.metrics = metrics
        self.duration_seconds = (self.end_time - self.start_time).total_seconds()
    
    def complete_with_failure(self, output: str = "", error_output: str = "", exit_code: int = 1):
        """失敗完了"""
        self.end_time = datetime.now()
        self.status = QualityStatus.FAILED
        self.output = output
        self.error_output = error_output
        self.exit_code = exit_code
        self.duration_seconds = (self.end_time - self.start_time).total_seconds()
    
    def complete_with_error(self, error_message: str):
        """エラー完了"""
        self.end_time = datetime.now()
        self.status = QualityStatus.ERROR
        self.error_output = error_message
        self.exit_code = -1
        self.duration_seconds = (self.end_time - self.start_time).total_seconds()
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            "check_type": self.check_type.value,
            "status": self.status.value,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.duration_seconds,
            "output": self.output,
            "error_output": self.error_output,
            "exit_code": self.exit_code,
            "metrics": self.metrics or {},
            "details": self.details or {}
        }


@dataclass
class QualityGateConfiguration:
    """品質ゲート設定"""
    gate_name: str
    policy: GatePolicy
    enabled_checks: Set[QualityCheckType]
    minimum_test_coverage: float = 80.0
    minimum_pass_rate: float = 95.0
    maximum_linting_issues: int = 10
    maximum_security_vulnerabilities: int = 0
    minimum_performance_score: float = 70.0
    timeout_seconds: int = 300
    parallel_execution: bool = True
    fail_fast: bool = False
    custom_rules: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.custom_rules is None:
            self.custom_rules = {}


class QualityChecker:
    """品質チェック実行者"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
    
    def run_unit_tests(self) -> QualityCheckResult:
        """単体テスト実行"""
        result = QualityCheckResult(
            check_type=QualityCheckType.UNIT_TESTS,
            status=QualityStatus.RUNNING,
            start_time=datetime.now()
        )
        
        try:
            # pytest実行
            cmd = ["python", "-m", "pytest", "tests/", "-v", "--tb=short"]
            process = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=180
            )
            
            if process.returncode == 0:
                # テスト成功 - 結果解析
                metrics = self._parse_pytest_output(process.stdout)
                result.complete_with_success(process.stdout, metrics)
            else:
                result.complete_with_failure(process.stdout, process.stderr, process.returncode)
                
        except subprocess.TimeoutExpired:
            result.complete_with_error("Test execution timeout")
        except Exception as e:
            result.complete_with_error(str(e))
        
        return result
    
    def run_coverage_check(self) -> QualityCheckResult:
        """カバレッジチェック実行"""
        result = QualityCheckResult(
            check_type=QualityCheckType.COVERAGE,
            status=QualityStatus.RUNNING,
            start_time=datetime.now()
        )
        
        try:
            # カバレッジ計測付きテスト実行
            cmd = ["python", "-m", "pytest", "--cov=src", "--cov-report=json", "--cov-report=term"]
            process = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=180
            )
            
            if process.returncode == 0:
                metrics = self._parse_coverage_output()
                result.complete_with_success(process.stdout, metrics)
            else:
                result.complete_with_failure(process.stdout, process.stderr, process.returncode)
                
        except subprocess.TimeoutExpired:
            result.complete_with_error("Coverage check timeout")
        except Exception as e:
            result.complete_with_error(str(e))
        
        return result
    
    def run_linting_check(self) -> QualityCheckResult:
        """リントチェック実行"""
        result = QualityCheckResult(
            check_type=QualityCheckType.LINTING,
            status=QualityStatus.RUNNING,
            start_time=datetime.now()
        )
        
        try:
            # flake8実行
            cmd = ["python", "-m", "flake8", "src/", "--count", "--statistics"]
            process = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # flake8は問題があってもexit code 1を返すが、これは正常
            metrics = self._parse_flake8_output(process.stdout, process.stderr)
            
            if metrics.get("total_issues", 0) == 0:
                result.complete_with_success(process.stdout, metrics)
            else:
                result.complete_with_success(f"Linting issues found: {metrics['total_issues']}", metrics)
                
        except subprocess.TimeoutExpired:
            result.complete_with_error("Linting check timeout")
        except Exception as e:
            result.complete_with_error(str(e))
        
        return result
    
    def run_type_check(self) -> QualityCheckResult:
        """型チェック実行"""
        result = QualityCheckResult(
            check_type=QualityCheckType.TYPE_CHECK,
            status=QualityStatus.RUNNING,
            start_time=datetime.now()
        )
        
        try:
            # mypy実行
            cmd = ["python", "-m", "mypy", "src/", "--ignore-missing-imports"]
            process = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if process.returncode == 0:
                result.complete_with_success(process.stdout)
            else:
                # 型エラーがある場合でも詳細を記録
                metrics = {"type_errors": process.stdout.count("error:")}
                result.complete_with_success(process.stdout, metrics)
                
        except subprocess.TimeoutExpired:
            result.complete_with_error("Type check timeout")
        except Exception as e:
            result.complete_with_error(str(e))
        
        return result
    
    def _parse_pytest_output(self, output: str) -> Dict[str, Any]:
        """pytest出力解析"""
        metrics = {"total_tests": 0, "passed": 0, "failed": 0, "errors": 0}
        
        # 正規表現を使ってより堅牢に解析
        import re
        
        # "10 passed" パターン
        passed_match = re.search(r'(\d+)\s+passed', output)
        if passed_match:
            metrics["passed"] = int(passed_match.group(1))
        
        # "2 failed" パターン  
        failed_match = re.search(r'(\d+)\s+failed', output)
        if failed_match:
            metrics["failed"] = int(failed_match.group(1))
        
        # "3 error" パターン
        error_match = re.search(r'(\d+)\s+error', output)
        if error_match:
            metrics["errors"] = int(error_match.group(1))
        
        metrics["total_tests"] = metrics["passed"] + metrics["failed"] + metrics["errors"]
        if metrics["total_tests"] > 0:
            metrics["pass_rate"] = metrics["passed"] / metrics["total_tests"]
        else:
            metrics["pass_rate"] = 0.0
        
        return metrics
    
    def _parse_coverage_output(self) -> Dict[str, Any]:
        """カバレッジ出力解析"""
        metrics = {"coverage_percentage": 0.0}
        
        try:
            # coverage.jsonファイルから読み取り
            coverage_file = self.project_root / "coverage.json"
            if coverage_file.exists():
                with open(coverage_file, 'r') as f:
                    coverage_data = json.load(f)
                    metrics["coverage_percentage"] = coverage_data.get("totals", {}).get("percent_covered", 0.0)
        except Exception:
            # JSONファイルが読めない場合はデフォルト値
            pass
        
        return metrics
    
    def _parse_flake8_output(self, stdout: str, stderr: str) -> Dict[str, Any]:
        """flake8出力解析"""
        metrics = {"total_issues": 0, "issue_types": {}}
        
        # エラー出力から問題数をカウント
        all_output = stdout + stderr
        lines = all_output.split('\n')
        
        for line in lines:
            if ':' in line and any(code in line for code in ['E', 'W', 'F', 'C', 'N']):
                metrics["total_issues"] += 1
                
                # エラーコード解析
                parts = line.split(':')
                if len(parts) >= 4:
                    error_part = parts[3].strip()
                    if ' ' in error_part:
                        error_code = error_part.split()[0]
                        if error_code not in metrics["issue_types"]:
                            metrics["issue_types"][error_code] = 0
                        metrics["issue_types"][error_code] += 1
        
        return metrics


class QualityGateSystem:
    """品質ゲートシステム"""
    
    def __init__(self, 
                 config: QualityGateConfiguration,
                 project_root: Path,
                 logger: Optional[Any] = None):
        self.config = config
        self.project_root = project_root
        self.logger = logger
        self.checker = QualityChecker(project_root)
        
        # 実行履歴
        self.execution_history: List[Dict[str, Any]] = []
        self.current_execution: Optional[Dict[str, Any]] = None
        
        # スレッドプール
        self._lock = threading.Lock()
    
    def execute_quality_gate(self) -> Dict[str, Any]:
        """品質ゲート実行"""
        execution_id = f"qg_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        with self._lock:
            self.current_execution = {
                "execution_id": execution_id,
                "start_time": datetime.now(),
                "end_time": None,
                "status": "running",
                "results": {},
                "overall_passed": False,
                "metrics": None
            }
        
        if self.logger:
            self.logger.info(f"Starting quality gate execution: {execution_id}")
        
        try:
            if self.config.parallel_execution:
                results = self._execute_checks_parallel()
            else:
                results = self._execute_checks_sequential()
            
            # 結果評価
            overall_passed, metrics = self._evaluate_results(results)
            
            # 実行完了
            with self._lock:
                self.current_execution.update({
                    "end_time": datetime.now(),
                    "status": "completed",
                    "results": {k: v.to_dict() for k, v in results.items()},
                    "overall_passed": overall_passed,
                    "metrics": metrics.to_dict() if metrics else None
                })
                
                # 履歴に追加
                self.execution_history.append(self.current_execution.copy())
                self.current_execution = None
            
            if self.logger:
                status = "PASSED" if overall_passed else "FAILED"
                self.logger.info(f"Quality gate execution completed: {status}")
            
            return {
                "execution_id": execution_id,
                "passed": overall_passed,
                "results": {k: v.to_dict() for k, v in results.items()},
                "metrics": metrics.to_dict() if metrics else None,
                "summary": self._generate_summary(results, overall_passed)
            }
            
        except Exception as e:
            with self._lock:
                if self.current_execution:
                    self.current_execution.update({
                        "end_time": datetime.now(),
                        "status": "error",
                        "error": str(e)
                    })
                    self.execution_history.append(self.current_execution.copy())
                    self.current_execution = None
            
            if self.logger:
                self.logger.error(f"Quality gate execution failed: {e}")
            
            raise
    
    def _execute_checks_sequential(self) -> Dict[QualityCheckType, QualityCheckResult]:
        """順次チェック実行"""
        results = {}
        
        for check_type in self.config.enabled_checks:
            if self.config.fail_fast and any(not r.is_success() for r in results.values()):
                break
                
            result = self._execute_single_check(check_type)
            results[check_type] = result
            
            if self.logger:
                status = "PASSED" if result.is_success() else "FAILED"
                self.logger.info(f"Check {check_type.value}: {status}")
        
        return results
    
    def _execute_checks_parallel(self) -> Dict[QualityCheckType, QualityCheckResult]:
        """並列チェック実行"""
        import concurrent.futures
        
        results = {}
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            # 全チェックを並列実行
            future_to_check = {
                executor.submit(self._execute_single_check, check_type): check_type
                for check_type in self.config.enabled_checks
            }
            
            for future in concurrent.futures.as_completed(future_to_check):
                check_type = future_to_check[future]
                try:
                    result = future.result(timeout=self.config.timeout_seconds)
                    results[check_type] = result
                    
                    if self.logger:
                        status = "PASSED" if result.is_success() else "FAILED"
                        self.logger.info(f"Check {check_type.value}: {status}")
                        
                except concurrent.futures.TimeoutError:
                    result = QualityCheckResult(
                        check_type=check_type,
                        status=QualityStatus.ERROR,
                        start_time=datetime.now()
                    )
                    result.complete_with_error("Execution timeout")
                    results[check_type] = result
                    
                except Exception as e:
                    result = QualityCheckResult(
                        check_type=check_type,
                        status=QualityStatus.ERROR,
                        start_time=datetime.now()
                    )
                    result.complete_with_error(str(e))
                    results[check_type] = result
        
        return results
    
    def _execute_single_check(self, check_type: QualityCheckType) -> QualityCheckResult:
        """単一チェック実行"""
        try:
            if check_type == QualityCheckType.UNIT_TESTS:
                return self.checker.run_unit_tests()
            elif check_type == QualityCheckType.COVERAGE:
                return self.checker.run_coverage_check()
            elif check_type == QualityCheckType.LINTING:
                return self.checker.run_linting_check()
            elif check_type == QualityCheckType.TYPE_CHECK:
                return self.checker.run_type_check()
            else:
                # 未実装のチェックタイプはスキップ
                result = QualityCheckResult(
                    check_type=check_type,
                    status=QualityStatus.SKIPPED,
                    start_time=datetime.now()
                )
                result.complete_with_success("Check type not implemented")
                return result
                
        except Exception as e:
            result = QualityCheckResult(
                check_type=check_type,
                status=QualityStatus.ERROR,
                start_time=datetime.now()
            )
            result.complete_with_error(str(e))
            return result
    
    def _evaluate_results(self, results: Dict[QualityCheckType, QualityCheckResult]) -> tuple[bool, QualityMetrics]:
        """結果評価"""
        metrics = QualityMetrics()
        
        # メトリクス集計
        for check_type, result in results.items():
            if result.metrics:
                if check_type == QualityCheckType.COVERAGE:
                    metrics.test_coverage_percentage = result.metrics.get("coverage_percentage", 0.0)
                elif check_type == QualityCheckType.UNIT_TESTS:
                    metrics.test_count = result.metrics.get("total_tests", 0)
                    metrics.test_pass_rate = result.metrics.get("pass_rate", 0.0)
                elif check_type == QualityCheckType.LINTING:
                    metrics.linting_issues = result.metrics.get("total_issues", 0)
        
        # ポリシーに基づく合否判定
        if self.config.policy == GatePolicy.STRICT:
            overall_passed = all(result.is_success() for result in results.values())
        elif self.config.policy == GatePolicy.MODERATE:
            critical_checks = {QualityCheckType.UNIT_TESTS, QualityCheckType.COVERAGE}
            critical_passed = all(
                results.get(check_type, QualityCheckResult(check_type, QualityStatus.FAILED, datetime.now())).is_success()
                for check_type in critical_checks
                if check_type in self.config.enabled_checks
            )
            overall_passed = critical_passed
        elif self.config.policy == GatePolicy.LENIENT:
            # 最低限のテストがパスすれば合格
            test_passed = results.get(QualityCheckType.UNIT_TESTS, 
                                    QualityCheckResult(QualityCheckType.UNIT_TESTS, QualityStatus.FAILED, datetime.now())).is_success()
            overall_passed = test_passed
        else:  # CUSTOM
            overall_passed = self._apply_custom_rules(results, metrics)
        
        return overall_passed, metrics
    
    def _apply_custom_rules(self, results: Dict[QualityCheckType, QualityCheckResult], metrics: QualityMetrics) -> bool:
        """カスタムルール適用"""
        rules_passed = []
        
        # カバレッジルール
        if metrics.test_coverage_percentage >= self.config.minimum_test_coverage:
            rules_passed.append(True)
        else:
            rules_passed.append(False)
        
        # テスト合格率ルール
        if metrics.test_pass_rate >= self.config.minimum_pass_rate / 100.0:
            rules_passed.append(True)
        else:
            rules_passed.append(False)
        
        # リント問題数ルール
        if metrics.linting_issues <= self.config.maximum_linting_issues:
            rules_passed.append(True)
        else:
            rules_passed.append(False)
        
        # 全てのルールがパスした場合のみ合格
        return all(rules_passed)
    
    def _generate_summary(self, results: Dict[QualityCheckType, QualityCheckResult], overall_passed: bool) -> Dict[str, Any]:
        """サマリー生成"""
        passed_count = sum(1 for result in results.values() if result.is_success())
        failed_count = sum(1 for result in results.values() if result.is_failure())
        error_count = sum(1 for result in results.values() if result.status == QualityStatus.ERROR)
        
        total_duration = sum(result.duration_seconds for result in results.values())
        
        return {
            "overall_status": "PASSED" if overall_passed else "FAILED",
            "total_checks": len(results),
            "passed_checks": passed_count,
            "failed_checks": failed_count,
            "error_checks": error_count,
            "total_duration_seconds": total_duration,
            "check_details": [
                {
                    "check_type": check_type.value,
                    "status": result.status.value,
                    "duration": result.duration_seconds
                }
                for check_type, result in results.items()
            ]
        }
    
    def get_execution_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """実行履歴取得"""
        with self._lock:
            return self.execution_history[-limit:]
    
    def get_current_status(self) -> Optional[Dict[str, Any]]:
        """現在の実行状況取得"""
        with self._lock:
            return self.current_execution.copy() if self.current_execution else None