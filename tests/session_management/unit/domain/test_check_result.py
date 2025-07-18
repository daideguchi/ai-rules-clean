"""
CheckResult Entity Unit Tests
テストファーストアプローチによるCheckResultエンティティテスト
"""

import pytest
from datetime import datetime
from typing import Optional, Dict, Any

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent / "src"))

from session_management.domain.entities.check_result import (
    CheckResult,
    CheckStatus,
    CheckSeverity
)


class TestCheckResult:
    """CheckResultエンティティのテスト"""

    def test_create_successful_check_result(self):
        """成功した確認結果の作成"""
        timestamp = datetime.now()
        result = CheckResult.success(
            check_name="president_status",
            message="PRESIDENT宣言済み",
            timestamp=timestamp,
            details={"session_file": "president_session.json"}
        )

        assert result.check_name == "president_status"
        assert result.status == CheckStatus.SUCCESS
        assert result.severity == CheckSeverity.INFO
        assert result.message == "PRESIDENT宣言済み"
        assert result.timestamp == timestamp
        assert result.details["session_file"] == "president_session.json"
        assert result.error is None
        assert result.is_success() is True
        assert result.is_failure() is False

    def test_create_failed_check_result(self):
        """失敗した確認結果の作成"""
        timestamp = datetime.now()
        error = Exception("ファイルが見つかりません")

        result = CheckResult.failure(
            check_name="cursor_rules",
            message="Cursor Rules確認失敗",
            error=error,
            timestamp=timestamp,
            severity=CheckSeverity.ERROR
        )

        assert result.check_name == "cursor_rules"
        assert result.status == CheckStatus.FAILURE
        assert result.severity == CheckSeverity.ERROR
        assert result.message == "Cursor Rules確認失敗"
        assert result.timestamp == timestamp
        assert result.error == error
        assert result.is_success() is False
        assert result.is_failure() is True

    def test_create_warning_check_result(self):
        """警告レベルの確認結果の作成"""
        result = CheckResult.warning(
            check_name="system_status",
            message="システム警告あり",
            details={"violations": 5}
        )

        assert result.status == CheckStatus.WARNING
        assert result.severity == CheckSeverity.WARNING
        assert result.message == "システム警告あり"
        assert result.details["violations"] == 5
        assert result.is_success() is False
        assert result.is_failure() is False

    def test_create_unknown_check_result(self):
        """不明状態の確認結果の作成"""
        result = CheckResult.unknown(
            check_name="test_check",
            message="状態不明"
        )

        assert result.status == CheckStatus.UNKNOWN
        assert result.severity == CheckSeverity.WARNING
        assert result.message == "状態不明"

    def test_check_result_equality(self):
        """CheckResult同等性テスト"""
        timestamp = datetime.now()

        result1 = CheckResult.success(
            check_name="test",
            message="success",
            timestamp=timestamp
        )

        result2 = CheckResult.success(
            check_name="test",
            message="success",
            timestamp=timestamp
        )

        result3 = CheckResult.failure(
            check_name="test",
            message="failure",
            timestamp=timestamp
        )

        assert result1 == result2
        assert result1 != result3

    def test_check_result_string_representation(self):
        """CheckResult文字列表現テスト"""
        result = CheckResult.success(
            check_name="president_status",
            message="PRESIDENT宣言済み"
        )

        str_repr = str(result)
        assert "president_status" in str_repr
        assert "SUCCESS" in str_repr
        assert "PRESIDENT宣言済み" in str_repr

    def test_check_result_serialization(self):
        """CheckResultシリアライゼーションテスト"""
        timestamp = datetime.now()
        result = CheckResult.success(
            check_name="test",
            message="test message",
            timestamp=timestamp,
            details={"key": "value"}
        )

        serialized = result.to_dict()

        assert serialized["check_name"] == "test"
        assert serialized["status"] == "SUCCESS"
        assert serialized["severity"] == "INFO"
        assert serialized["message"] == "test message"
        assert serialized["timestamp"] == timestamp.isoformat()
        assert serialized["details"] == {"key": "value"}
        assert serialized["error"] is None

    def test_check_result_deserialization(self):
        """CheckResultデシリアライゼーションテスト"""
        timestamp = datetime.now()
        data = {
            "check_name": "test",
            "status": "SUCCESS",
            "severity": "INFO",
            "message": "test message",
            "timestamp": timestamp.isoformat(),
            "details": {"key": "value"},
            "error": None
        }

        result = CheckResult.from_dict(data)

        assert result.check_name == "test"
        assert result.status == CheckStatus.SUCCESS
        assert result.severity == CheckSeverity.INFO
        assert result.message == "test message"
        assert result.timestamp == timestamp
        assert result.details == {"key": "value"}
        assert result.error is None

    def test_check_result_with_duration(self):
        """実行時間付きCheckResultテスト"""
        start_time = datetime.now()
        result = CheckResult.success(
            check_name="performance_test",
            message="性能テスト完了",
            timestamp=start_time,
            duration_ms=150
        )

        assert result.duration_ms == 150
        assert result.to_dict()["duration_ms"] == 150

    def test_invalid_check_result_creation(self):
        """不正なCheckResult作成時のエラーテスト"""
        with pytest.raises(ValueError, match="check_name cannot be empty"):
            CheckResult.success(
                check_name="",
                message="test"
            )

        with pytest.raises(ValueError, match="message cannot be empty"):
            CheckResult.success(
                check_name="test",
                message=""
            )

    def test_check_result_cache_key_generation(self):
        """CheckResultキャッシュキー生成テスト"""
        result = CheckResult.success(
            check_name="president_status",
            message="test",
            details={"state_hash": "abc123", "dependencies_hash": "def456"}
        )

        cache_key = result.generate_cache_key()
        assert "president_status" in cache_key
        assert "abc123" in cache_key
        assert "def456" in cache_key


if __name__ == "__main__":
    pytest.main([__file__, "-v"])