"""
EventDrivenCache Unit Tests
イベント駆動キャッシュシステムのテスト
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent / "src"))

from session_management.infrastructure.cache.event_driven_cache import (
    EventDrivenCache,
    CacheEntry,
    CacheResult,
    CacheEventType,
    CacheEvent,
    StateAwareCacheKey
)
from session_management.domain.entities.check_result import CheckResult


class TestStateAwareCacheKey:
    """StateAwareCacheKeyのテスト"""

    def test_create_cache_key(self):
        """キャッシュキー作成"""
        key = StateAwareCacheKey(
            check_name="president_status",
            state_hash="abc123",
            dependencies_hash="def456",
            version="1.0.0"
        )

        expected = "president_status:abc123:def456:1.0.0"
        assert str(key) == expected
        assert key.check_name == "president_status"
        assert key.state_hash == "abc123"
        assert key.dependencies_hash == "def456"
        assert key.version == "1.0.0"

    def test_cache_key_equality(self):
        """キャッシュキー同等性"""
        key1 = StateAwareCacheKey("test", "hash1", "dep1", "1.0")
        key2 = StateAwareCacheKey("test", "hash1", "dep1", "1.0")
        key3 = StateAwareCacheKey("test", "hash2", "dep1", "1.0")

        assert key1 == key2
        assert key1 != key3

    def test_cache_key_pattern_matching(self):
        """キャッシュキーパターンマッチング"""
        key = StateAwareCacheKey("president_status", "abc123", "def456", "1.0.0")

        assert key.matches_pattern("president_status:*")
        assert key.matches_pattern("president_status:abc123:*")
        assert key.matches_pattern("*:abc123:*")
        assert not key.matches_pattern("cursor_rules:*")


class TestCacheEntry:
    """CacheEntryのテスト"""

    def test_create_cache_entry(self):
        """キャッシュエントリ作成"""
        timestamp = datetime.now()
        data = {"status": "success", "message": "test"}

        entry = CacheEntry(
            data=data,
            created_at=timestamp,
            ttl_seconds=300,
            metadata={"source": "test"}
        )

        assert entry.data == data
        assert entry.created_at == timestamp
        assert entry.ttl_seconds == 300
        assert entry.metadata["source"] == "test"

    def test_cache_entry_expiry(self):
        """キャッシュエントリ有効期限"""
        # 期限内
        recent_entry = CacheEntry(
            data={"test": "data"},
            created_at=datetime.now() - timedelta(seconds=100),
            ttl_seconds=300
        )
        assert not recent_entry.is_expired()

        # 期限切れ
        old_entry = CacheEntry(
            data={"test": "data"},
            created_at=datetime.now() - timedelta(seconds=400),
            ttl_seconds=300
        )
        assert old_entry.is_expired()

    def test_cache_entry_serialization(self):
        """キャッシュエントリシリアライゼーション"""
        timestamp = datetime.now()
        entry = CacheEntry(
            data={"status": "success"},
            created_at=timestamp,
            ttl_seconds=300
        )

        serialized = entry.to_dict()
        restored = CacheEntry.from_dict(serialized)

        assert restored.data == entry.data
        assert restored.created_at == entry.created_at
        assert restored.ttl_seconds == entry.ttl_seconds


class TestCacheResult:
    """CacheResultのテスト"""

    def test_cache_hit(self):
        """キャッシュヒット"""
        data = {"test": "value"}
        result = CacheResult.hit(data)

        assert result.is_hit() is True
        assert result.is_miss() is False
        assert result.is_expired() is False
        assert result.is_invalid() is False
        assert result.data == data

    def test_cache_miss(self):
        """キャッシュミス"""
        result = CacheResult.miss()

        assert result.is_hit() is False
        assert result.is_miss() is True
        assert result.is_expired() is False
        assert result.is_invalid() is False
        assert result.data is None

    def test_cache_expired(self):
        """キャッシュ期限切れ"""
        result = CacheResult.expired()

        assert result.is_hit() is False
        assert result.is_miss() is False
        assert result.is_expired() is True
        assert result.is_invalid() is False

    def test_cache_invalid(self):
        """キャッシュ無効"""
        result = CacheResult.invalid("validation failed")

        assert result.is_hit() is False
        assert result.is_miss() is False
        assert result.is_expired() is False
        assert result.is_invalid() is True
        assert result.reason == "validation failed"


class TestEventDrivenCache:
    """EventDrivenCacheのテスト"""

    def setup_method(self):
        """テストセットアップ"""
        self.cache = EventDrivenCache()
        self.event_publisher = Mock()
        self.cache.event_publisher = self.event_publisher

    def test_cache_set_and_get(self):
        """キャッシュ設定・取得"""
        key = StateAwareCacheKey("test", "hash1", "dep1", "1.0")
        data = {"result": "success"}

        # データ設定
        self.cache.set(key, data, ttl_seconds=300)

        # データ取得
        result = self.cache.get(key)

        assert result.is_hit() is True
        assert result.data == data

    def test_cache_get_miss(self):
        """キャッシュミス"""
        key = StateAwareCacheKey("nonexistent", "hash", "dep", "1.0")

        result = self.cache.get(key)

        assert result.is_miss() is True
        assert result.data is None

    def test_cache_expiry(self):
        """キャッシュ有効期限"""
        key = StateAwareCacheKey("test", "hash", "dep", "1.0")
        data = {"test": "data"}

        # 短い有効期限で設定
        self.cache.set(key, data, ttl_seconds=1)

        # 即座には取得可能
        result = self.cache.get(key)
        assert result.is_hit() is True

        # 有効期限切れ後
        with patch('session_management.infrastructure.cache.event_driven_cache.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime.now() + timedelta(seconds=2)
            result = self.cache.get(key)
            assert result.is_expired() is True

    def test_cache_validation(self):
        """キャッシュバリデーション"""
        key = StateAwareCacheKey("test", "hash", "dep", "1.0")
        data = {"status": "active"}

        self.cache.set(key, data)

        # バリデーション成功
        def valid_validator(cached_data):
            return cached_data.get("status") == "active"

        result = self.cache.get(key, validator=valid_validator)
        assert result.is_hit() is True

        # バリデーション失敗
        def invalid_validator(cached_data):
            return cached_data.get("status") == "inactive"

        result = self.cache.get(key, validator=invalid_validator)
        assert result.is_invalid() is True

    def test_cache_invalidate_by_key(self):
        """キー指定キャッシュ無効化"""
        key = StateAwareCacheKey("test", "hash", "dep", "1.0")
        data = {"test": "data"}

        self.cache.set(key, data)

        # 無効化前は取得可能
        result = self.cache.get(key)
        assert result.is_hit() is True

        # 無効化
        self.cache.invalidate(key)

        # 無効化後は取得不可
        result = self.cache.get(key)
        assert result.is_miss() is True

    def test_cache_invalidate_by_pattern(self):
        """パターン指定キャッシュ無効化"""
        # 複数のキーでデータ設定
        keys = [
            StateAwareCacheKey("president_status", "hash1", "dep1", "1.0"),
            StateAwareCacheKey("president_status", "hash2", "dep2", "1.0"),
            StateAwareCacheKey("cursor_rules", "hash3", "dep3", "1.0")
        ]

        for key in keys:
            self.cache.set(key, {"data": f"test_{key.check_name}"})

        # パターンで無効化
        invalidated_count = self.cache.invalidate_by_pattern("president_status:*")

        assert invalidated_count == 2

        # president_statusは削除済み
        assert self.cache.get(keys[0]).is_miss()
        assert self.cache.get(keys[1]).is_miss()

        # cursor_rulesは残存
        assert self.cache.get(keys[2]).is_hit()

    def test_cache_invalidate_by_dependency(self):
        """依存関係による無効化"""
        # 異なる依存関係のキーを設定
        keys = [
            StateAwareCacheKey("check1", "hash1", "file1_hash", "1.0"),
            StateAwareCacheKey("check2", "hash2", "file1_hash", "1.0"),  # 同じ依存関係
            StateAwareCacheKey("check3", "hash3", "file2_hash", "1.0")   # 異なる依存関係
        ]

        for key in keys:
            self.cache.set(key, {"data": f"test_{key.check_name}"})

        # 依存関係による無効化
        affected_checks = ["check1", "check2"]
        invalidated_count = self.cache.invalidate_by_dependency(affected_checks)

        assert invalidated_count == 2

        # 影響を受けるキーは削除
        assert self.cache.get(keys[0]).is_miss()
        assert self.cache.get(keys[1]).is_miss()

        # 影響を受けないキーは残存
        assert self.cache.get(keys[2]).is_hit()

    def test_cache_event_publishing(self):
        """キャッシュイベント発行"""
        key = StateAwareCacheKey("test", "hash", "dep", "1.0")
        data = {"test": "data"}

        # 設定時のイベント
        self.cache.set(key, data)

        self.event_publisher.publish.assert_called()
        published_event = self.event_publisher.publish.call_args[0][0]
        assert published_event.event_type == CacheEventType.SET
        assert published_event.cache_key == str(key)

    def test_cache_statistics(self):
        """キャッシュ統計"""
        key1 = StateAwareCacheKey("test1", "hash1", "dep1", "1.0")
        key2 = StateAwareCacheKey("test2", "hash2", "dep2", "1.0")

        # データ設定
        self.cache.set(key1, {"data": "test1"})
        self.cache.set(key2, {"data": "test2"})

        # ヒット・ミス発生
        self.cache.get(key1)  # ヒット
        self.cache.get(key1)  # ヒット
        self.cache.get(StateAwareCacheKey("nonexistent", "hash", "dep", "1.0"))  # ミス

        stats = self.cache.get_statistics()

        assert stats["total_entries"] == 2
        assert stats["total_hits"] == 2
        assert stats["total_misses"] == 1
        assert stats["hit_rate"] == 2/3

    def test_cache_cleanup_expired_entries(self):
        """期限切れエントリの自動削除"""
        key1 = StateAwareCacheKey("test1", "hash1", "dep1", "1.0")
        key2 = StateAwareCacheKey("test2", "hash2", "dep2", "1.0")

        # 短い有効期限で設定
        self.cache.set(key1, {"data": "test1"}, ttl_seconds=1)
        self.cache.set(key2, {"data": "test2"}, ttl_seconds=1000)

        # 時間経過をシミュレート
        with patch('session_management.infrastructure.cache.event_driven_cache.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime.now() + timedelta(seconds=2)

            # 期限切れエントリの削除
            removed_count = self.cache.cleanup_expired()

            assert removed_count == 1

            # 期限切れエントリは削除済み
            assert self.cache.get(key1).is_miss()

            # 有効なエントリは残存
            assert self.cache.get(key2).is_hit()


class TestCacheEvent:
    """CacheEventのテスト"""

    def test_create_cache_event(self):
        """キャッシュイベント作成"""
        timestamp = datetime.now()
        event = CacheEvent(
            event_type=CacheEventType.SET,
            cache_key="test:key",
            timestamp=timestamp,
            metadata={"source": "test"}
        )

        assert event.event_type == CacheEventType.SET
        assert event.cache_key == "test:key"
        assert event.timestamp == timestamp
        assert event.metadata["source"] == "test"

    def test_cache_event_serialization(self):
        """キャッシュイベントシリアライゼーション"""
        event = CacheEvent(
            event_type=CacheEventType.INVALIDATE,
            cache_key="test:key",
            timestamp=datetime.now()
        )

        serialized = event.to_dict()
        restored = CacheEvent.from_dict(serialized)

        assert restored.event_type == event.event_type
        assert restored.cache_key == event.cache_key
        assert restored.timestamp == event.timestamp


if __name__ == "__main__":
    pytest.main([__file__, "-v"])