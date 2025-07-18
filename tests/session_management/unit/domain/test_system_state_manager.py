"""
SystemStateManager Unit Tests
状態同期・管理システムのテスト
"""

import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent / "src"))

from session_management.domain.entities.check_result import CheckResult
from session_management.domain.entities.session_state import (
    ComponentState,
)
from session_management.domain.services.system_state_manager import (
    DependencyTracker,
    StateChangeEvent,
    StateChangeType,
    StateHashCalculator,
    SystemStateManager,
)
from session_management.infrastructure.cache.event_driven_cache import (
    StateAwareCacheKey,
)


class TestSystemStateManager:
    """SystemStateManagerのテスト"""

    def setup_method(self):
        """テストセットアップ"""
        self.event_publisher = Mock()
        self.cache_manager = Mock()
        self.dependency_tracker = Mock()
        self.state_hash_calculator = Mock()

        self.state_manager = SystemStateManager(
            event_publisher=self.event_publisher,
            cache_manager=self.cache_manager,
            dependency_tracker=self.dependency_tracker,
            state_hash_calculator=self.state_hash_calculator
        )

    def test_initialize_session_state(self):
        """セッション状態初期化"""
        session_id = "test-session-123"

        session_state = self.state_manager.initialize_session_state(session_id)

        assert session_state.session_id == session_id
        assert session_state.version.value == 1
        assert len(session_state.component_states) == 0
        assert len(session_state.check_history) == 0

    def test_update_component_state(self):
        """コンポーネント状態更新"""
        session_state = self.state_manager.initialize_session_state("test-session")

        # セッション初期化後にイベント発行者のモックをリセット
        self.event_publisher.reset_mock()

        # 依存関係トラッカーのモック設定
        self.dependency_tracker.get_affected_checks.return_value = ["dependent_check"]

        # 状態ハッシュ計算のモック設定
        self.state_hash_calculator.calculate_state_hash.return_value = "new_hash_123"
        self.state_hash_calculator.calculate_dependencies_hash.return_value = "dep_hash_456"

        # コンポーネント状態更新
        component_state = ComponentState(
            component_name="president_status",
            status="active",
            last_checked=datetime.now(),
            state_hash="abc123"
        )

        updated_state = self.state_manager.update_component_state(
            session_state, component_state
        )

        # 状態が更新されることを確認
        assert len(updated_state.component_states) == 1
        assert updated_state.component_states["president_status"] == component_state
        assert updated_state.version.value == 2

        # イベント発行の確認
        self.event_publisher.publish.assert_called_once()
        published_event = self.event_publisher.publish.call_args[0][0]
        assert published_event.change_type == StateChangeType.COMPONENT_UPDATED
        assert published_event.component_name == "president_status"

    def test_add_check_result(self):
        """確認結果追加"""
        session_state = self.state_manager.initialize_session_state("test-session")

        # セッション初期化後にイベント発行者のモックをリセット
        self.event_publisher.reset_mock()

        check_result = CheckResult.success(
            check_name="cursor_rules",
            message="Cursor Rules確認成功"
        )

        updated_state = self.state_manager.add_check_result(session_state, check_result)

        # 確認結果が追加されることを確認
        assert len(updated_state.check_history) == 1
        assert updated_state.check_history[0] == check_result
        assert updated_state.version.value == 2

        # イベント発行の確認
        self.event_publisher.publish.assert_called_once()
        published_event = self.event_publisher.publish.call_args[0][0]
        assert published_event.change_type == StateChangeType.CHECK_RESULT_ADDED
        assert published_event.check_name == "cursor_rules"

    def test_handle_file_change(self):
        """ファイル変更処理"""
        file_path = "runtime/secure_state/president_session.json"

        # 依存関係トラッカーのモック設定
        self.dependency_tracker.get_affected_checks.return_value = ["president_status", "system_status"]

        # ファイル変更処理
        self.state_manager.handle_file_change(file_path)

        # 依存関係確認の呼び出し
        self.dependency_tracker.get_affected_checks.assert_called_once_with(file_path)

        # キャッシュ無効化の呼び出し
        self.cache_manager.invalidate_by_dependency.assert_called_once_with(
            ["president_status", "system_status"]
        )

        # イベント発行の確認
        self.event_publisher.publish.assert_called_once()
        published_event = self.event_publisher.publish.call_args[0][0]
        assert published_event.change_type == StateChangeType.FILE_CHANGED
        assert published_event.file_path == file_path

    def test_handle_command_execution(self):
        """コマンド実行処理"""
        command = "make declare-president"

        # 依存関係トラッカーのモック設定
        self.dependency_tracker.get_affected_checks_by_command.return_value = ["president_status"]

        # コマンド実行処理
        self.state_manager.handle_command_execution(command)

        # 依存関係確認の呼び出し
        self.dependency_tracker.get_affected_checks_by_command.assert_called_once_with(command)

        # キャッシュ無効化の呼び出し
        self.cache_manager.invalidate_by_dependency.assert_called_once_with(["president_status"])

        # イベント発行の確認
        self.event_publisher.publish.assert_called_once()
        published_event = self.event_publisher.publish.call_args[0][0]
        assert published_event.change_type == StateChangeType.COMMAND_EXECUTED
        assert published_event.command == command

    def test_generate_cache_key(self):
        """キャッシュキー生成"""
        check_name = "president_status"

        # 状態ハッシュ計算のモック設定
        self.state_hash_calculator.calculate_state_hash.return_value = "state_abc123"
        self.state_hash_calculator.calculate_dependencies_hash.return_value = "dep_def456"

        cache_key = self.state_manager.generate_cache_key(check_name)

        assert isinstance(cache_key, StateAwareCacheKey)
        assert cache_key.check_name == check_name
        assert cache_key.state_hash == "state_abc123"
        assert cache_key.dependencies_hash == "dep_def456"
        assert cache_key.version == "1.0.0"  # デフォルトバージョン

    def test_get_state_hash(self):
        """状態ハッシュ取得"""
        check_name = "cursor_rules"
        expected_hash = "cursor_hash_789"

        # 状態ハッシュ計算のモック設定
        self.state_hash_calculator.calculate_state_hash.return_value = expected_hash

        state_hash = self.state_manager.get_state_hash(check_name)

        assert state_hash == expected_hash
        self.state_hash_calculator.calculate_state_hash.assert_called_once_with(check_name)

    def test_get_dependencies_hash(self):
        """依存関係ハッシュ取得"""
        check_name = "system_status"
        expected_hash = "deps_hash_321"

        # 依存関係ハッシュ計算のモック設定
        self.state_hash_calculator.calculate_dependencies_hash.return_value = expected_hash

        deps_hash = self.state_manager.get_dependencies_hash(check_name)

        assert deps_hash == expected_hash
        self.state_hash_calculator.calculate_dependencies_hash.assert_called_once_with(check_name)

    def test_get_system_overview(self):
        """システム概要取得"""
        session_state = self.state_manager.initialize_session_state("test-session")

        # テストデータ追加
        component1 = ComponentState("comp1", "active", datetime.now())
        component2 = ComponentState("comp2", "inactive", datetime.now())
        session_state = session_state.add_component_state(component1)
        session_state = session_state.add_component_state(component2)

        success_result = CheckResult.success("test1", "success")
        failure_result = CheckResult.failure("test2", "failure")
        session_state = session_state.add_check_result(success_result)
        session_state = session_state.add_check_result(failure_result)

        overview = self.state_manager.get_system_overview(session_state)

        assert overview["session_id"] == "test-session"
        assert overview["version"] == session_state.version.value
        assert overview["component_count"] == 2
        assert overview["check_count"] == 2
        assert overview["violation_count"] == 1
        assert overview["last_updated"] == session_state.updated_at.isoformat()


class TestStateChangeEvent:
    """StateChangeEventのテスト"""

    def test_create_component_updated_event(self):
        """コンポーネント更新イベント作成"""
        timestamp = datetime.now()
        event = StateChangeEvent.component_updated(
            component_name="president_status",
            new_status="active",
            timestamp=timestamp
        )

        assert event.change_type == StateChangeType.COMPONENT_UPDATED
        assert event.component_name == "president_status"
        assert event.new_status == "active"
        assert event.timestamp == timestamp
        assert event.file_path is None
        assert event.command is None

    def test_create_file_changed_event(self):
        """ファイル変更イベント作成"""
        file_path = "test/file.json"
        affected_checks = ["check1", "check2"]

        event = StateChangeEvent.file_changed(
            file_path=file_path,
            affected_checks=affected_checks
        )

        assert event.change_type == StateChangeType.FILE_CHANGED
        assert event.file_path == file_path
        assert event.affected_checks == affected_checks
        assert event.component_name is None
        assert event.command is None

    def test_create_command_executed_event(self):
        """コマンド実行イベント作成"""
        command = "make declare-president"
        affected_checks = ["president_status"]

        event = StateChangeEvent.command_executed(
            command=command,
            affected_checks=affected_checks
        )

        assert event.change_type == StateChangeType.COMMAND_EXECUTED
        assert event.command == command
        assert event.affected_checks == affected_checks
        assert event.component_name is None
        assert event.file_path is None

    def test_state_change_event_serialization(self):
        """StateChangeEventシリアライゼーション"""
        event = StateChangeEvent.component_updated(
            component_name="test_component",
            new_status="updated"
        )

        serialized = event.to_dict()
        restored = StateChangeEvent.from_dict(serialized)

        assert restored.change_type == event.change_type
        assert restored.component_name == event.component_name
        assert restored.new_status == event.new_status
        assert restored.timestamp == event.timestamp


class TestDependencyTracker:
    """DependencyTrackerのテスト"""

    def test_get_affected_checks_by_file(self):
        """ファイル変更による影響確認取得"""
        tracker = DependencyTracker()

        # PRESIDENT関連ファイル
        affected = tracker.get_affected_checks("runtime/secure_state/president_session.json")
        assert "president_status" in affected

        # Cursor Rules関連ファイル
        affected = tracker.get_affected_checks("src/cursor-rules/globals.mdc")
        assert "cursor_rules" in affected

        # 関係ないファイル
        affected = tracker.get_affected_checks("some/random/file.txt")
        assert len(affected) == 0

    def test_get_affected_checks_by_command(self):
        """コマンド実行による影響確認取得"""
        tracker = DependencyTracker()

        # PRESIDENT宣言コマンド
        affected = tracker.get_affected_checks_by_command("make declare-president")
        assert "president_status" in affected

        # システム状態表示コマンド
        affected = tracker.get_affected_checks_by_command("python3 scripts/hooks/system_status_display.py")
        assert "system_status" in affected

        # 関係ないコマンド
        affected = tracker.get_affected_checks_by_command("ls -la")
        assert len(affected) == 0

    def test_register_dependency(self):
        """依存関係登録"""
        tracker = DependencyTracker()

        # 新しい依存関係を登録
        tracker.register_dependency(
            check_name="new_check",
            file_dependencies=["new/file.json"],
            command_dependencies=["new-command"]
        )

        # 登録された依存関係が反映されることを確認
        affected = tracker.get_affected_checks("new/file.json")
        assert "new_check" in affected

        affected = tracker.get_affected_checks_by_command("new-command")
        assert "new_check" in affected


class TestStateHashCalculator:
    """StateHashCalculatorのテスト"""

    def test_calculate_state_hash(self):
        """状態ハッシュ計算"""
        calculator = StateHashCalculator()

        # 同じ入力には同じハッシュ
        hash1 = calculator.calculate_state_hash("president_status")
        hash2 = calculator.calculate_state_hash("president_status")
        assert hash1 == hash2

        # 異なる入力には異なるハッシュ
        hash3 = calculator.calculate_state_hash("cursor_rules")
        assert hash1 != hash3

    def test_calculate_dependencies_hash(self):
        """依存関係ハッシュ計算"""
        calculator = StateHashCalculator()

        # 同じ依存関係には同じハッシュ
        hash1 = calculator.calculate_dependencies_hash("president_status")
        hash2 = calculator.calculate_dependencies_hash("president_status")
        assert hash1 == hash2

        # 異なる依存関係には異なるハッシュ
        hash3 = calculator.calculate_dependencies_hash("cursor_rules")
        assert hash1 != hash3

    def test_calculate_file_hash(self):
        """ファイルハッシュ計算"""
        calculator = StateHashCalculator()

        with patch('pathlib.Path.exists') as mock_exists, \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('pathlib.Path.read_text') as mock_read:

            # ファイル存在のモック
            mock_exists.return_value = True

            # ファイル統計のモック
            mock_stat.return_value.st_mtime = 1234567890.0
            mock_stat.return_value.st_size = 1024

            # ファイル内容のモック
            mock_read.return_value = "test file content"

            file_hash = calculator.calculate_file_hash("test/file.txt")

            assert isinstance(file_hash, str)
            assert len(file_hash) > 0

    def test_calculate_file_hash_nonexistent(self):
        """存在しないファイルのハッシュ計算"""
        calculator = StateHashCalculator()

        with patch('pathlib.Path.exists') as mock_exists:
            mock_exists.return_value = False

            file_hash = calculator.calculate_file_hash("nonexistent/file.txt")

            assert file_hash == "file_not_found"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
