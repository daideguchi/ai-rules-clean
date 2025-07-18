"""
SessionState Entity Unit Tests
セッション状態エンティティのテスト
"""

import sys
from datetime import datetime
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent / "src"))

from session_management.domain.entities.check_result import CheckResult
from session_management.domain.entities.session_state import (
    ComponentState,
    SessionState,
    StateVersion,
)


class TestSessionState:
    """SessionStateエンティティのテスト"""

    def test_create_empty_session_state(self):
        """空のセッション状態作成"""
        state = SessionState.create_empty()

        assert state.session_id is not None
        assert len(state.session_id) > 0
        assert state.created_at is not None
        assert state.updated_at is not None
        assert state.version.value == 1
        assert len(state.component_states) == 0
        assert len(state.check_history) == 0

    def test_create_session_state_with_id(self):
        """指定IDでのセッション状態作成"""
        session_id = "test-session-123"
        state = SessionState.create_with_id(session_id)

        assert state.session_id == session_id
        assert state.version.value == 1

    def test_add_component_state(self):
        """コンポーネント状態追加"""
        state = SessionState.create_empty()

        component_state = ComponentState(
            component_name="president_status",
            status="active",
            last_checked=datetime.now(),
            state_hash="abc123",
            dependencies_hash="def456"
        )

        updated_state = state.add_component_state(component_state)

        assert len(updated_state.component_states) == 1
        assert updated_state.component_states["president_status"] == component_state
        assert updated_state.version.value == 2
        assert updated_state.updated_at > state.updated_at

    def test_update_component_state(self):
        """コンポーネント状態更新"""
        state = SessionState.create_empty()

        # 初期状態追加
        initial_component = ComponentState(
            component_name="president_status",
            status="inactive",
            last_checked=datetime.now(),
            state_hash="abc123"
        )
        state = state.add_component_state(initial_component)

        # 状態更新
        updated_component = ComponentState(
            component_name="president_status",
            status="active",
            last_checked=datetime.now(),
            state_hash="xyz789"
        )

        updated_state = state.update_component_state("president_status", updated_component)

        assert updated_state.component_states["president_status"].status == "active"
        assert updated_state.component_states["president_status"].state_hash == "xyz789"
        assert updated_state.version.value == 3

    def test_add_check_result(self):
        """確認結果追加"""
        state = SessionState.create_empty()

        check_result = CheckResult.success(
            check_name="president_status",
            message="PRESIDENT宣言済み"
        )

        updated_state = state.add_check_result(check_result)

        assert len(updated_state.check_history) == 1
        assert updated_state.check_history[0] == check_result
        assert updated_state.version.value == 2

    def test_get_component_state(self):
        """コンポーネント状態取得"""
        state = SessionState.create_empty()

        component_state = ComponentState(
            component_name="cursor_rules",
            status="valid",
            last_checked=datetime.now()
        )

        state = state.add_component_state(component_state)

        retrieved = state.get_component_state("cursor_rules")
        assert retrieved == component_state

        not_found = state.get_component_state("nonexistent")
        assert not_found is None

    def test_get_latest_check_result(self):
        """最新確認結果取得"""
        state = SessionState.create_empty()

        # 複数の確認結果を追加
        old_result = CheckResult.success("test1", "old")
        new_result = CheckResult.success("test2", "new")

        state = state.add_check_result(old_result)
        state = state.add_check_result(new_result)

        latest = state.get_latest_check_result("test2")
        assert latest == new_result

        not_found = state.get_latest_check_result("nonexistent")
        assert not_found is None

    def test_calculate_state_hash(self):
        """状態ハッシュ計算"""
        state = SessionState.create_empty()

        component1 = ComponentState(
            component_name="comp1",
            status="active",
            last_checked=datetime.now()
        )
        component2 = ComponentState(
            component_name="comp2",
            status="inactive",
            last_checked=datetime.now()
        )

        state = state.add_component_state(component1)
        state = state.add_component_state(component2)

        state_hash = state.calculate_state_hash()
        assert isinstance(state_hash, str)
        assert len(state_hash) > 0

        # 同じ状態なら同じハッシュ
        state_hash2 = state.calculate_state_hash()
        assert state_hash == state_hash2

    def test_has_violations(self):
        """違反有無判定"""
        state = SessionState.create_empty()

        # 違反なし
        success_result = CheckResult.success("test", "success")
        state = state.add_check_result(success_result)
        assert state.has_violations() is False

        # 違反あり
        failure_result = CheckResult.failure("test", "failure")
        state = state.add_check_result(failure_result)
        assert state.has_violations() is True

    def test_get_violation_count(self):
        """違反数取得"""
        state = SessionState.create_empty()

        # 成功・警告・失敗結果を追加
        state = state.add_check_result(CheckResult.success("test1", "success"))
        state = state.add_check_result(CheckResult.warning("test2", "warning"))
        state = state.add_check_result(CheckResult.failure("test3", "failure"))
        state = state.add_check_result(CheckResult.failure("test4", "failure2"))

        assert state.get_violation_count() == 2  # 失敗のみカウント

    def test_session_state_serialization(self):
        """SessionStateシリアライゼーション"""
        state = SessionState.create_with_id("test-session")

        component = ComponentState(
            component_name="test_component",
            status="active",
            last_checked=datetime.now()
        )
        state = state.add_component_state(component)

        check_result = CheckResult.success("test_check", "success")
        state = state.add_check_result(check_result)

        serialized = state.to_dict()

        assert serialized["session_id"] == "test-session"
        assert serialized["version"] == state.version.value
        assert len(serialized["component_states"]) == 1
        assert len(serialized["check_history"]) == 1

    def test_session_state_deserialization(self):
        """SessionStateデシリアライゼーション"""
        original_state = SessionState.create_with_id("test-session")

        component = ComponentState(
            component_name="test_component",
            status="active",
            last_checked=datetime.now()
        )
        original_state = original_state.add_component_state(component)

        # シリアライズしてからデシリアライズ
        serialized = original_state.to_dict()
        restored_state = SessionState.from_dict(serialized)

        assert restored_state.session_id == original_state.session_id
        assert restored_state.version.value == original_state.version.value
        assert len(restored_state.component_states) == len(original_state.component_states)

    def test_state_version_increment(self):
        """状態バージョン増分"""
        state = SessionState.create_empty()
        initial_version = state.version.value

        # コンポーネント追加でバージョン増分
        component = ComponentState("test", "active", datetime.now())
        state = state.add_component_state(component)
        assert state.version.value == initial_version + 1

        # 確認結果追加でバージョン増分
        check_result = CheckResult.success("test", "success")
        state = state.add_check_result(check_result)
        assert state.version.value == initial_version + 2


class TestComponentState:
    """ComponentStateのテスト"""

    def test_create_component_state(self):
        """コンポーネント状態作成"""
        timestamp = datetime.now()
        component = ComponentState(
            component_name="president_status",
            status="active",
            last_checked=timestamp,
            state_hash="abc123",
            dependencies_hash="def456",
            metadata={"file": "president_session.json"}
        )

        assert component.component_name == "president_status"
        assert component.status == "active"
        assert component.last_checked == timestamp
        assert component.state_hash == "abc123"
        assert component.dependencies_hash == "def456"
        assert component.metadata["file"] == "president_session.json"

    def test_component_state_equality(self):
        """ComponentState同等性"""
        timestamp = datetime.now()

        comp1 = ComponentState("test", "active", timestamp, "hash1")
        comp2 = ComponentState("test", "active", timestamp, "hash1")
        comp3 = ComponentState("test", "active", timestamp, "hash2")

        assert comp1 == comp2
        assert comp1 != comp3

    def test_component_state_serialization(self):
        """ComponentStateシリアライゼーション"""
        timestamp = datetime.now()
        component = ComponentState(
            component_name="test",
            status="active",
            last_checked=timestamp,
            state_hash="hash123"
        )

        serialized = component.to_dict()

        assert serialized["component_name"] == "test"
        assert serialized["status"] == "active"
        assert serialized["last_checked"] == timestamp.isoformat()
        assert serialized["state_hash"] == "hash123"


class TestStateVersion:
    """StateVersionのテスト"""

    def test_create_state_version(self):
        """状態バージョン作成"""
        version = StateVersion(5)
        assert version.value == 5

    def test_increment_version(self):
        """バージョン増分"""
        version = StateVersion(1)
        incremented = version.increment()

        assert version.value == 1  # 元は変更されない
        assert incremented.value == 2

    def test_version_comparison(self):
        """バージョン比較"""
        v1 = StateVersion(1)
        v2 = StateVersion(2)
        v3 = StateVersion(1)

        assert v1 < v2
        assert v2 > v1
        assert v1 == v3
        assert v1 != v2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
