"""
IntegratedSessionSystem Integration Tests
統合セッション管理システムの統合テスト
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from pathlib import Path
import tempfile
import time

import sys
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "src"))

from session_management.application.integrated_session_system import (
    IntegratedSessionSystem,
    SessionConfiguration,
    IntegratedEventPublisher
)
from session_management.domain.entities.check_result import CheckResult
from session_management.domain.services.system_state_manager import StateChangeEvent, StateChangeType
from session_management.domain.services.error_handling_system import ErrorSeverity, ErrorCategory


class TestIntegratedEventPublisher:
    """IntegratedEventPublisherのテスト"""

    def test_event_publisher_basic(self):
        """基本的なイベント発行"""
        publisher = IntegratedEventPublisher()

        events_received = []

        def test_handler(event):
            events_received.append(event)

        publisher.add_event_handler(test_handler)

        # イベント発行
        event = StateChangeEvent(
            change_type=StateChangeType.SESSION_INITIALIZED,
            timestamp=datetime.now(),
            session_id="test_session"
        )

        publisher.publish(event)

        assert len(events_received) == 1
        assert events_received[0] == event

    def test_multiple_event_handlers(self):
        """複数イベントハンドラー"""
        publisher = IntegratedEventPublisher()

        handler1_calls = []
        handler2_calls = []

        def handler1(event):
            handler1_calls.append(event)

        def handler2(event):
            handler2_calls.append(event)

        publisher.add_event_handler(handler1)
        publisher.add_event_handler(handler2)

        event = StateChangeEvent(
            change_type=StateChangeType.COMPONENT_UPDATED,
            timestamp=datetime.now(),
            component_name="test_component"
        )

        publisher.publish(event)

        assert len(handler1_calls) == 1
        assert len(handler2_calls) == 1

    def test_event_handler_removal(self):
        """イベントハンドラー削除"""
        publisher = IntegratedEventPublisher()

        calls = []

        def test_handler(event):
            calls.append(event)

        publisher.add_event_handler(test_handler)
        publisher.remove_event_handler(test_handler)

        event = StateChangeEvent(
            change_type=StateChangeType.SESSION_INITIALIZED,
            timestamp=datetime.now()
        )

        publisher.publish(event)

        assert len(calls) == 0


class TestSessionConfiguration:
    """SessionConfigurationのテスト"""

    def test_default_configuration(self):
        """デフォルト設定"""
        config = SessionConfiguration(session_id="test_session")

        assert config.session_id == "test_session"
        assert config.max_cache_size == 1000
        assert config.cache_ttl_seconds == 1800
        assert config.error_retention_hours == 24
        assert config.enable_persistence is True
        assert config.enable_monitoring is True
        assert config.log_level == "INFO"
        assert config.persistence_path == Path("runtime/session_management")

    def test_custom_configuration(self):
        """カスタム設定"""
        custom_path = Path("/tmp/custom_session")

        config = SessionConfiguration(
            session_id="custom_session",
            max_cache_size=500,
            cache_ttl_seconds=900,
            error_retention_hours=12,
            enable_persistence=False,
            persistence_path=custom_path,
            enable_monitoring=False,
            log_level="DEBUG"
        )

        assert config.session_id == "custom_session"
        assert config.max_cache_size == 500
        assert config.cache_ttl_seconds == 900
        assert config.error_retention_hours == 12
        assert config.enable_persistence is False
        assert config.persistence_path == custom_path
        assert config.enable_monitoring is False
        assert config.log_level == "DEBUG"


class TestIntegratedSessionSystem:
    """IntegratedSessionSystemの統合テスト"""

    def setup_method(self):
        """テストセットアップ"""
        self.temp_dir = tempfile.mkdtemp()
        self.config = SessionConfiguration(
            session_id="test_session_123",
            persistence_path=Path(self.temp_dir),
            log_level="WARNING"  # テスト中はログを抑制
        )

        self.system = IntegratedSessionSystem(self.config)

    def test_system_initialization(self):
        """システム初期化"""
        assert self.system.config.session_id == "test_session_123"
        assert self.system.session_state.session_id == "test_session_123"
        assert self.system.logger is not None
        assert self.system.event_publisher is not None
        assert self.system.cache is not None
        assert self.system.state_manager is not None
        assert self.system.error_system is not None

    def test_execute_with_error_handling_success(self):
        """エラーハンドリング付き実行（成功）"""
        def successful_operation():
            return "success_result"

        result = self.system.execute_with_error_handling(
            operation=successful_operation,
            component_name="test_component",
            operation_name="test_operation"
        )

        assert result == "success_result"

    def test_execute_with_error_handling_with_fallback(self):
        """エラーハンドリング付き実行（フォールバック使用）"""
        def failing_operation():
            raise ValueError("Operation failed")

        def fallback_operation():
            return "fallback_result"

        result = self.system.execute_with_error_handling(
            operation=failing_operation,
            component_name="test_component",
            operation_name="test_operation",
            fallback=fallback_operation
        )

        assert result == "fallback_result"

        # エラーが記録されることを確認
        assert len(self.system.error_system.error_history) > 0

    def test_perform_check_success(self):
        """確認作業実行（成功）"""
        def successful_check():
            return True

        result = self.system.perform_check(
            check_name="test_check",
            check_function=successful_check,
            component_name="test_component"
        )

        assert result.is_success()
        assert result.check_name == "test_check"
        assert result.duration_ms is not None and result.duration_ms >= 0

        # セッション状態に記録されることを確認
        assert len(self.system.session_state.check_history) == 1
        assert self.system.session_state.check_history[0] == result

    def test_perform_check_failure(self):
        """確認作業実行（失敗）"""
        def failing_check():
            return False

        result = self.system.perform_check(
            check_name="failing_check",
            check_function=failing_check,
            component_name="test_component"
        )

        assert result.is_failure()
        assert result.check_name == "failing_check"
        assert "Check failed" in result.message

    def test_perform_check_with_exception(self):
        """確認作業実行（例外発生）"""
        def exception_check():
            raise RuntimeError("Check exception")

        result = self.system.perform_check(
            check_name="exception_check",
            check_function=exception_check,
            component_name="test_component"
        )

        assert result.is_failure()
        assert "Check error" in result.message
        assert "Check exception" in result.message

    def test_perform_check_with_cache(self):
        """確認作業実行（キャッシュ使用）"""
        call_count = 0

        def cached_check():
            nonlocal call_count
            call_count += 1
            return True

        # 1回目実行（キャッシュミス）
        result1 = self.system.perform_check(
            check_name="cached_check",
            check_function=cached_check,
            component_name="test_component",
            use_cache=True
        )

        # 2回目実行（キャッシュヒット）
        result2 = self.system.perform_check(
            check_name="cached_check",
            check_function=cached_check,
            component_name="test_component",
            use_cache=True
        )

        assert result1.is_success()
        assert result2.is_success()
        assert call_count == 1  # 1回だけ実行される

    def test_update_component_status(self):
        """コンポーネント状態更新"""
        self.system.update_component_status(
            component_name="test_component",
            status="active",
            metadata={"version": "1.0.0"}
        )

        # セッション状態に反映されることを確認
        component_state = self.system.session_state.get_component_state("test_component")
        assert component_state is not None
        assert component_state.status == "active"
        assert component_state.metadata["version"] == "1.0.0"

    def test_get_system_overview(self):
        """システム概要取得"""
        # いくつかの操作を実行してデータを生成
        self.system.perform_check("test_check", lambda: True, "test_component")
        self.system.update_component_status("test_component", "active")

        overview = self.system.get_system_overview()

        assert "session" in overview
        assert "cache" in overview
        assert "errors" in overview
        assert "system_health" in overview
        assert "configuration" in overview

        assert overview["session"]["session_id"] == "test_session_123"
        assert overview["configuration"]["session_id"] == "test_session_123"

    def test_cleanup_resources(self):
        """リソースクリーンアップ"""
        # いくつかのエラーとキャッシュエントリを生成
        try:
            raise ValueError("Test error")
        except ValueError as e:
            from session_management.domain.services.error_handling_system import ErrorContext
            context = ErrorContext("test_component", "test_operation")
            self.system.error_system.handle_error(e, context)

        # キャッシュエントリ作成
        self.system.perform_check("test_check", lambda: True, "test_component")

        # クリーンアップ実行
        cleanup_result = self.system.cleanup_resources()

        assert "cleaned_cache_entries" in cleanup_result
        assert "cleaned_errors" in cleanup_result
        assert isinstance(cleanup_result["cleaned_cache_entries"], int)
        assert isinstance(cleanup_result["cleaned_errors"], int)

    def test_validate_system_integrity(self):
        """システム整合性検証"""
        # システムの動作を実行
        self.system.perform_check("integrity_check", lambda: True, "test_component")

        validation = self.system.validate_system_integrity()

        assert "is_healthy" in validation
        assert "state_validation" in validation
        assert "cache_health" in validation
        assert "error_health" in validation
        assert "overall_assessment" in validation

        assert isinstance(validation["is_healthy"], bool)
        assert validation["overall_assessment"] in ["healthy", "needs_attention"]

    def test_export_full_diagnostics(self):
        """完全診断情報エクスポート"""
        # データ生成のため操作実行
        self.system.perform_check("diagnostic_check", lambda: True, "test_component")
        self.system.update_component_status("test_component", "active")

        diagnostics = self.system.export_full_diagnostics()

        assert "timestamp" in diagnostics
        assert "session_id" in diagnostics
        assert "system_overview" in diagnostics
        assert "validation_results" in diagnostics
        assert "error_diagnostics" in diagnostics
        assert "cache_state" in diagnostics
        assert "configuration" in diagnostics

        assert diagnostics["session_id"] == "test_session_123"

    def test_event_handling_integration(self):
        """イベント処理統合テスト"""
        events_received = []

        def test_event_handler(event):
            events_received.append(event)

        self.system.event_publisher.add_event_handler(test_event_handler)

        # コンポーネント状態更新（イベント発生）
        self.system.update_component_status("event_test_component", "active")

        # イベントが発行されることを確認
        assert len(events_received) > 0

        # 最後のイベントがCOMPONENT_UPDATEDであることを確認
        last_event = events_received[-1]
        assert last_event.change_type == StateChangeType.COMPONENT_UPDATED
        assert last_event.component_name == "event_test_component"

    def test_error_recovery_integration(self):
        """エラー回復統合テスト"""
        call_count = 0

        def always_failing_operation():
            nonlocal call_count
            call_count += 1
            raise ValueError(f"Failing operation {call_count}")

        def fallback_operation():
            return "fallback_success"

        result = self.system.execute_with_error_handling(
            operation=always_failing_operation,
            component_name="retry_component",
            operation_name="retry_test",
            fallback=fallback_operation
        )

        # フォールバックが実行される
        assert result == "fallback_success"

        # エラーが記録される（最終試行失敗時）
        assert len(self.system.error_system.error_history) > 0

        # エラー統計が更新される
        stats = self.system.error_system.get_statistics()
        assert stats.total_errors > 0

    def test_cache_integration(self):
        """キャッシュ統合テスト"""
        # キャッシュ可能な確認を複数回実行
        def consistent_check():
            return True

        # 1回目（キャッシュミス）
        result1 = self.system.perform_check(
            "cache_integration_check",
            consistent_check,
            "cache_component",
            use_cache=True
        )

        # キャッシュ統計確認
        cache_stats = self.system.cache.get_statistics()
        initial_hits = cache_stats["total_hits"]
        initial_misses = cache_stats["total_misses"]

        # 2回目（キャッシュヒット予期）
        result2 = self.system.perform_check(
            "cache_integration_check",
            consistent_check,
            "cache_component",
            use_cache=True
        )

        # キャッシュ統計再確認
        cache_stats_after = self.system.cache.get_statistics()

        assert result1.is_success()
        assert result2.is_success()

        # キャッシュヒット数が増加していることを確認
        assert cache_stats_after["total_hits"] > initial_hits

    def test_system_shutdown(self):
        """システムシャットダウン"""
        # システムで作業実行
        self.system.perform_check("shutdown_test", lambda: True, "test_component")

        # シャットダウン実行
        self.system.shutdown()

        # イベントハンドラーがクリアされることを確認
        assert len(self.system.event_publisher.event_handlers) == 0

    def test_concurrent_operations(self):
        """並行操作テスト"""
        import threading

        results = []
        errors = []

        def concurrent_check(check_id):
            try:
                result = self.system.perform_check(
                    f"concurrent_check_{check_id}",
                    lambda: True,
                    "concurrent_component"
                )
                results.append(result)
            except Exception as e:
                errors.append(e)

        # 複数スレッドで並行実行
        threads = []
        for i in range(5):
            thread = threading.Thread(target=concurrent_check, args=(i,))
            threads.append(thread)
            thread.start()

        # 全スレッド完了待ち
        for thread in threads:
            thread.join()

        # エラーなしで全て成功することを確認
        assert len(errors) == 0
        assert len(results) == 5
        assert all(result.is_success() for result in results)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])