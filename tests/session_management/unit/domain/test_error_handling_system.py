"""
ErrorHandlingSystem Unit Tests
包括的エラーハンドリング・回復システムのテスト
"""

import json
import logging
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock

import pytest

sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent / "src"))

from session_management.domain.services.error_handling_system import (
    ErrorCategory,
    ErrorContext,
    ErrorHandlingSystem,
    ErrorInfo,
    ErrorSeverity,
    ErrorStatistics,
    IntegrationErrorHandler,
    NetworkErrorHandler,
    RecoveryAction,
    RecoveryStrategy,
    SystemErrorHandler,
    ValidationErrorHandler,
)


class CustomTestException(Exception):
    """テスト用カスタム例外"""
    pass


class TestErrorContext:
    """ErrorContextのテスト"""

    def test_create_error_context(self):
        """エラーコンテキスト作成"""
        context = ErrorContext(
            component_name="test_component",
            operation_name="test_operation",
            session_id="session_123",
            user_id="user_456",
            correlation_id="corr_789",
            metadata={"key": "value"}
        )

        assert context.component_name == "test_component"
        assert context.operation_name == "test_operation"
        assert context.session_id == "session_123"
        assert context.user_id == "user_456"
        assert context.correlation_id == "corr_789"
        assert context.metadata["key"] == "value"

    def test_error_context_to_dict(self):
        """エラーコンテキスト辞書変換"""
        context = ErrorContext(
            component_name="test_component",
            operation_name="test_operation"
        )

        result = context.to_dict()

        assert result["component_name"] == "test_component"
        assert result["operation_name"] == "test_operation"
        assert result["session_id"] is None
        assert result["metadata"] == {}


class TestErrorInfo:
    """ErrorInfoのテスト"""

    def test_create_error_info_from_exception(self):
        """例外からErrorInfo作成"""
        exception = ValueError("Test error message")
        context = ErrorContext("test_component", "test_operation")

        error_info = ErrorInfo.from_exception(
            exception=exception,
            context=context,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.VALIDATION
        )

        assert error_info.error_type == "ValueError"
        assert error_info.error_message == "Test error message"
        assert error_info.severity == ErrorSeverity.HIGH
        assert error_info.category == ErrorCategory.VALIDATION
        assert error_info.context == context
        assert error_info.original_exception == exception
        assert error_info.traceback_info is not None
        assert len(error_info.error_id) == 16  # SHA256[:16]

    def test_error_info_retry_logic(self):
        """エラー情報リトライロジック"""
        context = ErrorContext("test_component", "test_operation")

        # リトライ可能なエラー
        retryable_error = ErrorInfo(
            error_id="test_id",
            error_type="ConnectionError",
            error_message="Network timeout",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.NETWORK,
            context=context,
            timestamp=datetime.now(),
            retry_count=1,
            max_retries=3
        )

        assert retryable_error.can_retry() is True
        assert retryable_error.should_fail_fast() is False

        # 致命的エラー
        fatal_error = ErrorInfo(
            error_id="test_id_2",
            error_type="SystemError",
            error_message="Critical system failure",
            severity=ErrorSeverity.FATAL,
            category=ErrorCategory.SYSTEM,
            context=context,
            timestamp=datetime.now()
        )

        assert fatal_error.can_retry() is False
        assert fatal_error.should_fail_fast() is True

    def test_error_info_serialization(self):
        """エラー情報シリアライゼーション"""
        context = ErrorContext("test_component", "test_operation")
        error_info = ErrorInfo(
            error_id="test_id",
            error_type="TestError",
            error_message="Test message",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.SYSTEM,
            context=context,
            timestamp=datetime.now()
        )

        serialized = error_info.to_dict()

        assert serialized["error_id"] == "test_id"
        assert serialized["error_type"] == "TestError"
        assert serialized["severity"] == "HIGH"
        assert serialized["category"] == "SYSTEM"
        assert "context" in serialized
        assert "timestamp" in serialized


class TestRecoveryAction:
    """RecoveryActionのテスト"""

    def test_recovery_action_execution(self):
        """回復アクション実行"""
        executed = False

        def test_action(error_info):
            nonlocal executed
            executed = True
            return True

        action = RecoveryAction(
            strategy=RecoveryStrategy.RETRY,
            action_name="test_retry",
            description="Test retry action",
            executable=test_action
        )

        context = ErrorContext("test_component", "test_operation")
        error_info = ErrorInfo(
            error_id="test_id",
            error_type="TestError",
            error_message="Test",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.SYSTEM,
            context=context,
            timestamp=datetime.now()
        )

        result = action.execute(error_info)

        assert result is True
        assert executed is True

    def test_recovery_action_execution_failure(self):
        """回復アクション実行失敗"""
        def failing_action(error_info):
            raise Exception("Action failed")

        action = RecoveryAction(
            strategy=RecoveryStrategy.RETRY,
            action_name="failing_action",
            description="Failing action",
            executable=failing_action
        )

        context = ErrorContext("test_component", "test_operation")
        error_info = ErrorInfo(
            error_id="test_id",
            error_type="TestError",
            error_message="Test",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.SYSTEM,
            context=context,
            timestamp=datetime.now()
        )

        result = action.execute(error_info)

        assert result is False


class TestErrorHandlers:
    """各種エラーハンドラーのテスト"""

    def test_validation_error_handler(self):
        """バリデーションエラーハンドラー"""
        handler = ValidationErrorHandler()
        context = ErrorContext("test_component", "validate_input")

        validation_error = ErrorInfo(
            error_id="test_id",
            error_type="ValidationError",
            error_message="Invalid input",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.VALIDATION,
            context=context,
            timestamp=datetime.now()
        )

        assert handler.can_handle(validation_error) is True
        assert handler.handle(validation_error) is False  # バリデーションエラーはリトライしない

        actions = handler.get_recovery_actions(validation_error)
        assert len(actions) == 1
        assert actions[0].strategy == RecoveryStrategy.USER_INTERVENTION

    def test_integration_error_handler(self):
        """統合エラーハンドラー"""
        handler = IntegrationErrorHandler()
        context = ErrorContext("api_client", "call_external_service")

        integration_error = ErrorInfo(
            error_id="test_id",
            error_type="ConnectionError",
            error_message="Service unavailable",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.INTEGRATION,
            context=context,
            timestamp=datetime.now(),
            retry_count=1,
            max_retries=3
        )

        assert handler.can_handle(integration_error) is True
        assert handler.handle(integration_error) is True  # リトライ可能

        actions = handler.get_recovery_actions(integration_error)
        assert len(actions) == 2
        assert actions[0].strategy == RecoveryStrategy.RETRY
        assert actions[1].strategy == RecoveryStrategy.FALLBACK

    def test_network_error_handler(self):
        """ネットワークエラーハンドラー"""
        handler = NetworkErrorHandler()
        context = ErrorContext("http_client", "send_request")

        network_error = ErrorInfo(
            error_id="test_id",
            error_type="TimeoutError",
            error_message="Request timeout",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.NETWORK,
            context=context,
            timestamp=datetime.now(),
            retry_count=0,
            max_retries=3
        )

        assert handler.can_handle(network_error) is True
        assert handler.handle(network_error) is True

        actions = handler.get_recovery_actions(network_error)
        assert len(actions) == 2
        assert actions[0].strategy == RecoveryStrategy.RETRY
        assert actions[1].strategy == RecoveryStrategy.CIRCUIT_BREAKER

    def test_system_error_handler(self):
        """システムエラーハンドラー"""
        handler = SystemErrorHandler()
        context = ErrorContext("database", "execute_query")

        # 致命的システムエラー
        fatal_error = ErrorInfo(
            error_id="test_id",
            error_type="SystemError",
            error_message="System failure",
            severity=ErrorSeverity.FATAL,
            category=ErrorCategory.SYSTEM,
            context=context,
            timestamp=datetime.now()
        )

        assert handler.can_handle(fatal_error) is True
        assert handler.handle(fatal_error) is False  # 致命的エラーは処理しない

        actions = handler.get_recovery_actions(fatal_error)
        assert len(actions) == 2
        assert actions[0].strategy == RecoveryStrategy.FAIL_FAST
        assert actions[1].strategy == RecoveryStrategy.GRACEFUL_DEGRADATION

        # 回復可能システムエラー
        recoverable_error = ErrorInfo(
            error_id="test_id_2",
            error_type="SystemError",
            error_message="Temporary system issue",
            severity=ErrorSeverity.MEDIUM,  # HIGH -> MEDIUM に変更
            category=ErrorCategory.SYSTEM,
            context=context,
            timestamp=datetime.now(),
            retry_count=1,
            max_retries=3
        )

        assert handler.handle(recoverable_error) is True


class TestErrorStatistics:
    """ErrorStatisticsのテスト"""

    def test_error_statistics_update(self):
        """エラー統計更新"""
        stats = ErrorStatistics()
        context = ErrorContext("test_component", "test_operation")

        error1 = ErrorInfo(
            error_id="error_1",
            error_type="ValueError",
            error_message="Error 1",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.VALIDATION,
            context=context,
            timestamp=datetime.now()
        )

        error2 = ErrorInfo(
            error_id="error_2",
            error_type="ConnectionError",
            error_message="Error 2",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.NETWORK,
            context=context,
            timestamp=datetime.now()
        )

        stats.update_from_error(error1)
        stats.update_from_error(error2)

        assert stats.total_errors == 2
        assert stats.errors_by_severity[ErrorSeverity.HIGH] == 1
        assert stats.errors_by_severity[ErrorSeverity.MEDIUM] == 1
        assert stats.errors_by_category[ErrorCategory.VALIDATION] == 1
        assert stats.errors_by_category[ErrorCategory.NETWORK] == 1
        assert stats.errors_by_component["test_component"] == 2
        assert stats.last_updated is not None

    def test_error_statistics_serialization(self):
        """エラー統計シリアライゼーション"""
        stats = ErrorStatistics()
        context = ErrorContext("test_component", "test_operation")

        error = ErrorInfo(
            error_id="error_1",
            error_type="TestError",
            error_message="Test error",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.SYSTEM,
            context=context,
            timestamp=datetime.now()
        )

        stats.update_from_error(error)
        serialized = stats.to_dict()

        assert serialized["total_errors"] == 1
        assert "errors_by_severity" in serialized
        assert "errors_by_category" in serialized
        assert "errors_by_component" in serialized


class TestErrorHandlingSystem:
    """ErrorHandlingSystemのテスト"""

    def setup_method(self):
        """テストセットアップ"""
        # 一時ディレクトリでテスト
        self.temp_dir = tempfile.mkdtemp()
        self.persistence_path = Path(self.temp_dir)

        # ロガーのモック
        self.logger = Mock(spec=logging.Logger)

        self.error_system = ErrorHandlingSystem(
            logger=self.logger,
            persistence_path=self.persistence_path
        )

    def test_handle_error_basic(self):
        """基本的なエラー処理"""
        exception = ValueError("Test error")
        context = ErrorContext("test_component", "test_operation")

        self.error_system.handle_error(
            exception=exception,
            context=context,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.VALIDATION
        )

        # エラーが記録されることを確認
        assert len(self.error_system.error_history) == 1
        assert len(self.error_system.error_cache) == 1
        assert self.error_system.statistics.total_errors == 1

        # ログが出力されることを確認
        self.logger.log.assert_called()

    def test_handle_error_with_fallback_success(self):
        """フォールバック付きエラー処理（成功）"""
        def successful_operation():
            return "success"

        def fallback_operation():
            return "fallback"

        context = ErrorContext("test_component", "test_operation")

        result = self.error_system.handle_error_with_fallback(
            operation=successful_operation,
            fallback=fallback_operation,
            context=context
        )

        assert result == "success"
        assert len(self.error_system.error_history) == 0  # エラーなし

    def test_handle_error_with_fallback_failure(self):
        """フォールバック付きエラー処理（失敗→フォールバック）"""
        def failing_operation():
            raise ValueError("Operation failed")

        def fallback_operation():
            return "fallback_result"

        context = ErrorContext("test_component", "test_operation")

        result = self.error_system.handle_error_with_fallback(
            operation=failing_operation,
            fallback=fallback_operation,
            context=context,
            max_retries=2
        )

        assert result == "fallback_result"
        assert len(self.error_system.error_history) == 1  # 1つのエラーが記録される

    def test_handle_error_with_fallback_complete_failure(self):
        """フォールバック付きエラー処理（完全失敗）"""
        def failing_operation():
            raise ValueError("Operation failed")

        def failing_fallback():
            raise RuntimeError("Fallback also failed")

        context = ErrorContext("test_component", "test_operation")

        with pytest.raises(RuntimeError, match="Fallback also failed"):
            self.error_system.handle_error_with_fallback(
                operation=failing_operation,
                fallback=failing_fallback,
                context=context,
                max_retries=1
            )

        assert len(self.error_system.error_history) == 2  # 2つのエラーが記録される

    def test_get_error_by_id(self):
        """エラーID検索"""
        exception = ValueError("Test error")
        context = ErrorContext("test_component", "test_operation")

        self.error_system.handle_error(exception, context)

        error_id = list(self.error_system.error_cache.keys())[0]
        retrieved_error = self.error_system.get_error_by_id(error_id)

        assert retrieved_error is not None
        assert retrieved_error.error_id == error_id
        assert retrieved_error.error_type == "ValueError"

    def test_get_recent_errors(self):
        """最近のエラー取得"""
        context = ErrorContext("test_component", "test_operation")

        # 複数のエラーを生成
        for i in range(5):
            exception = ValueError(f"Error {i}")
            self.error_system.handle_error(exception, context)

        recent_errors = self.error_system.get_recent_errors(limit=3)

        assert len(recent_errors) == 3
        assert recent_errors[-1].error_message == "Error 4"  # 最新

    def test_get_errors_by_component(self):
        """コンポーネント別エラー取得"""
        context1 = ErrorContext("component_1", "operation")
        context2 = ErrorContext("component_2", "operation")

        self.error_system.handle_error(ValueError("Error 1"), context1)
        self.error_system.handle_error(ValueError("Error 2"), context1)
        self.error_system.handle_error(ValueError("Error 3"), context2)

        component1_errors = self.error_system.get_errors_by_component("component_1")
        component2_errors = self.error_system.get_errors_by_component("component_2")

        assert len(component1_errors) == 2
        assert len(component2_errors) == 1
        assert component1_errors[0].context.component_name == "component_1"

    def test_clear_old_errors(self):
        """古いエラークリア"""
        context = ErrorContext("test_component", "test_operation")

        # 古いエラーを作成（タイムスタンプを手動設定）
        old_error = ErrorInfo(
            error_id="old_error",
            error_type="OldError",
            error_message="Old error",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.SYSTEM,
            context=context,
            timestamp=datetime.now() - timedelta(hours=25)  # 25時間前
        )

        # 新しいエラーを作成
        new_exception = ValueError("New error")
        self.error_system.handle_error(new_exception, context)

        # 古いエラーを手動で履歴に追加
        self.error_system.error_history.insert(0, old_error)
        self.error_system.error_cache[old_error.error_id] = old_error

        # クリア実行
        removed_count = self.error_system.clear_old_errors(older_than_hours=24)

        assert removed_count == 1
        assert len(self.error_system.error_history) == 1  # 新しいエラーのみ残る
        assert old_error.error_id not in self.error_system.error_cache

    def test_error_persistence(self):
        """エラー永続化"""
        exception = ValueError("Persistent error")
        context = ErrorContext("test_component", "test_operation")

        self.error_system.handle_error(exception, context)

        # 永続化ファイルが作成されることを確認
        error_files = list(self.persistence_path.glob("error_*.json"))
        assert len(error_files) == 1

        # ファイル内容を確認
        with open(error_files[0], encoding='utf-8') as f:
            saved_error = json.load(f)

        assert saved_error["error_type"] == "ValueError"
        assert saved_error["error_message"] == "Persistent error"

    def test_export_diagnostics(self):
        """診断情報エクスポート"""
        context = ErrorContext("test_component", "test_operation")

        # いくつかのエラーを生成
        self.error_system.handle_error(ValueError("Error 1"), context)
        self.error_system.handle_error(RuntimeError("Error 2"), context)

        diagnostics = self.error_system.export_diagnostics()

        assert "system_info" in diagnostics
        assert "current_state" in diagnostics
        assert "statistics" in diagnostics
        assert "recent_errors" in diagnostics

        assert diagnostics["current_state"]["errors_in_history"] == 2
        assert diagnostics["current_state"]["errors_in_cache"] == 2
        assert len(diagnostics["recent_errors"]) == 2

    def test_error_history_cleanup(self):
        """エラー履歴自動クリーンアップ"""
        # max_history_sizeを小さく設定
        self.error_system.max_history_size = 3

        context = ErrorContext("test_component", "test_operation")

        # 5つのエラーを生成（制限を超える）
        for i in range(5):
            exception = ValueError(f"Error {i}")
            self.error_system.handle_error(exception, context)

        # 履歴サイズが制限内に収まることを確認
        assert len(self.error_system.error_history) == 3
        assert len(self.error_system.error_cache) == 3

        # 最新のエラーが残ることを確認
        assert self.error_system.error_history[-1].error_message == "Error 4"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
