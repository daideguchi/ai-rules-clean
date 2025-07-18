"""
SystemStatus Entity Unit Tests
システム状態エンティティのテスト
"""

import pytest
from datetime import datetime
from typing import Dict, List

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent / "src"))

from session_management.domain.entities.system_status import (
    SystemStatus,
    HealthStatus,
    ComponentHealth,
    SystemMetrics
)


class TestSystemStatus:
    """SystemStatusエンティティのテスト"""

    def test_create_healthy_system_status(self):
        """健全なシステム状態作成"""
        status = SystemStatus.create_healthy()

        assert status.overall_health == HealthStatus.HEALTHY
        assert status.timestamp is not None
        assert len(status.component_healths) == 0
        assert status.metrics is not None
        assert status.is_healthy() is True
        assert status.is_degraded() is False
        assert status.is_unhealthy() is False

    def test_create_system_status_with_components(self):
        """コンポーネント付きシステム状態作成"""
        president_health = ComponentHealth(
            component_name="president_status",
            status=HealthStatus.HEALTHY,
            last_check=datetime.now(),
            details={"declared": True}
        )

        cache_health = ComponentHealth(
            component_name="cache_system",
            status=HealthStatus.DEGRADED,
            last_check=datetime.now(),
            details={"hit_rate": 0.7}
        )

        metrics = SystemMetrics(
            total_checks=10,
            successful_checks=8,
            failed_checks=2,
            average_response_time_ms=150
        )

        status = SystemStatus.create_with_components(
            [president_health, cache_health],
            metrics
        )

        assert len(status.component_healths) == 2
        assert status.get_component_health("president_status") == president_health
        assert status.get_component_health("cache_system") == cache_health
        assert status.metrics == metrics

    def test_add_component_health(self):
        """コンポーネントヘルス追加"""
        status = SystemStatus.create_healthy()

        component_health = ComponentHealth(
            component_name="cursor_rules",
            status=HealthStatus.HEALTHY,
            last_check=datetime.now()
        )

        updated_status = status.add_component_health(component_health)

        assert len(updated_status.component_healths) == 1
        assert updated_status.get_component_health("cursor_rules") == component_health
        assert updated_status.timestamp > status.timestamp

    def test_update_component_health(self):
        """コンポーネントヘルス更新"""
        initial_health = ComponentHealth(
            component_name="test_component",
            status=HealthStatus.HEALTHY,
            last_check=datetime.now()
        )

        status = SystemStatus.create_healthy().add_component_health(initial_health)

        updated_health = ComponentHealth(
            component_name="test_component",
            status=HealthStatus.DEGRADED,
            last_check=datetime.now(),
            details={"error_count": 2}
        )

        updated_status = status.update_component_health("test_component", updated_health)

        assert updated_status.get_component_health("test_component").status == HealthStatus.DEGRADED
        assert updated_status.get_component_health("test_component").details["error_count"] == 2

    def test_calculate_overall_health(self):
        """全体ヘルス計算"""
        # 全て健全
        healthy_components = [
            ComponentHealth("comp1", HealthStatus.HEALTHY, datetime.now()),
            ComponentHealth("comp2", HealthStatus.HEALTHY, datetime.now())
        ]
        status = SystemStatus.create_with_components(healthy_components)
        assert status.overall_health == HealthStatus.HEALTHY

        # 一部劣化
        mixed_components = [
            ComponentHealth("comp1", HealthStatus.HEALTHY, datetime.now()),
            ComponentHealth("comp2", HealthStatus.DEGRADED, datetime.now())
        ]
        status = SystemStatus.create_with_components(mixed_components)
        assert status.overall_health == HealthStatus.DEGRADED

        # 一部不健全
        unhealthy_components = [
            ComponentHealth("comp1", HealthStatus.HEALTHY, datetime.now()),
            ComponentHealth("comp2", HealthStatus.UNHEALTHY, datetime.now())
        ]
        status = SystemStatus.create_with_components(unhealthy_components)
        assert status.overall_health == HealthStatus.UNHEALTHY

    def test_get_unhealthy_components(self):
        """不健全コンポーネント取得"""
        components = [
            ComponentHealth("healthy1", HealthStatus.HEALTHY, datetime.now()),
            ComponentHealth("degraded1", HealthStatus.DEGRADED, datetime.now()),
            ComponentHealth("unhealthy1", HealthStatus.UNHEALTHY, datetime.now()),
            ComponentHealth("healthy2", HealthStatus.HEALTHY, datetime.now())
        ]

        status = SystemStatus.create_with_components(components)

        unhealthy = status.get_unhealthy_components()
        assert len(unhealthy) == 2
        assert any(comp.component_name == "degraded1" for comp in unhealthy)
        assert any(comp.component_name == "unhealthy1" for comp in unhealthy)

    def test_system_status_serialization(self):
        """SystemStatusシリアライゼーション"""
        component = ComponentHealth(
            component_name="test_component",
            status=HealthStatus.HEALTHY,
            last_check=datetime.now(),
            details={"test": "value"}
        )

        metrics = SystemMetrics(
            total_checks=100,
            successful_checks=95,
            failed_checks=5,
            average_response_time_ms=200
        )

        status = SystemStatus.create_with_components([component], metrics)

        serialized = status.to_dict()

        assert serialized["overall_health"] == "HEALTHY"
        assert len(serialized["component_healths"]) == 1
        assert serialized["metrics"]["total_checks"] == 100

    def test_system_status_deserialization(self):
        """SystemStatusデシリアライゼーション"""
        original_status = SystemStatus.create_with_components([
            ComponentHealth("test", HealthStatus.HEALTHY, datetime.now())
        ])

        serialized = original_status.to_dict()
        restored_status = SystemStatus.from_dict(serialized)

        assert restored_status.overall_health == original_status.overall_health
        assert len(restored_status.component_healths) == len(original_status.component_healths)
        assert restored_status.timestamp == original_status.timestamp


class TestComponentHealth:
    """ComponentHealthのテスト"""

    def test_create_component_health(self):
        """コンポーネントヘルス作成"""
        timestamp = datetime.now()
        health = ComponentHealth(
            component_name="president_status",
            status=HealthStatus.HEALTHY,
            last_check=timestamp,
            details={"session_file": "president_session.json"},
            error_message=None
        )

        assert health.component_name == "president_status"
        assert health.status == HealthStatus.HEALTHY
        assert health.last_check == timestamp
        assert health.details["session_file"] == "president_session.json"
        assert health.error_message is None
        assert health.is_healthy() is True
        assert health.is_degraded() is False
        assert health.is_unhealthy() is False

    def test_create_unhealthy_component_health(self):
        """不健全コンポーネントヘルス作成"""
        health = ComponentHealth(
            component_name="cache_system",
            status=HealthStatus.UNHEALTHY,
            last_check=datetime.now(),
            error_message="Cache connection failed"
        )

        assert health.is_healthy() is False
        assert health.is_degraded() is False
        assert health.is_unhealthy() is True
        assert health.error_message == "Cache connection failed"

    def test_component_health_serialization(self):
        """ComponentHealthシリアライゼーション"""
        timestamp = datetime.now()
        health = ComponentHealth(
            component_name="test",
            status=HealthStatus.DEGRADED,
            last_check=timestamp,
            details={"performance": "slow"}
        )

        serialized = health.to_dict()

        assert serialized["component_name"] == "test"
        assert serialized["status"] == "DEGRADED"
        assert serialized["last_check"] == timestamp.isoformat()
        assert serialized["details"]["performance"] == "slow"


class TestSystemMetrics:
    """SystemMetricsのテスト"""

    def test_create_system_metrics(self):
        """システムメトリクス作成"""
        metrics = SystemMetrics(
            total_checks=1000,
            successful_checks=950,
            failed_checks=50,
            average_response_time_ms=125,
            cache_hit_rate=0.85,
            error_rate=0.05
        )

        assert metrics.total_checks == 1000
        assert metrics.successful_checks == 950
        assert metrics.failed_checks == 50
        assert metrics.average_response_time_ms == 125
        assert metrics.cache_hit_rate == 0.85
        assert metrics.error_rate == 0.05

    def test_calculate_success_rate(self):
        """成功率計算"""
        metrics = SystemMetrics(
            total_checks=100,
            successful_checks=95,
            failed_checks=5
        )

        success_rate = metrics.calculate_success_rate()
        assert success_rate == 0.95

    def test_calculate_error_rate(self):
        """エラー率計算"""
        metrics = SystemMetrics(
            total_checks=200,
            successful_checks=190,
            failed_checks=10
        )

        error_rate = metrics.calculate_error_rate()
        assert error_rate == 0.05

    def test_is_performance_acceptable(self):
        """パフォーマンス許容判定"""
        # 良好なパフォーマンス
        good_metrics = SystemMetrics(
            total_checks=100,
            successful_checks=98,
            failed_checks=2,
            average_response_time_ms=100
        )
        assert good_metrics.is_performance_acceptable() is True

        # 悪いパフォーマンス（エラー率高）
        bad_error_metrics = SystemMetrics(
            total_checks=100,
            successful_checks=80,
            failed_checks=20,
            average_response_time_ms=100
        )
        assert bad_error_metrics.is_performance_acceptable() is False

        # 悪いパフォーマンス（応答時間遅い）
        slow_metrics = SystemMetrics(
            total_checks=100,
            successful_checks=98,
            failed_checks=2,
            average_response_time_ms=2000
        )
        assert slow_metrics.is_performance_acceptable() is False

    def test_system_metrics_serialization(self):
        """SystemMetricsシリアライゼーション"""
        metrics = SystemMetrics(
            total_checks=500,
            successful_checks=475,
            failed_checks=25,
            average_response_time_ms=150
        )

        serialized = metrics.to_dict()

        assert serialized["total_checks"] == 500
        assert serialized["successful_checks"] == 475
        assert serialized["failed_checks"] == 25
        assert serialized["average_response_time_ms"] == 150


class TestHealthStatus:
    """HealthStatusのテスト"""

    def test_health_status_ordering(self):
        """ヘルスステータス順序"""
        assert HealthStatus.HEALTHY > HealthStatus.DEGRADED
        assert HealthStatus.DEGRADED > HealthStatus.UNHEALTHY
        assert HealthStatus.HEALTHY > HealthStatus.UNHEALTHY

    def test_health_status_values(self):
        """ヘルスステータス値"""
        assert HealthStatus.HEALTHY.value == 3
        assert HealthStatus.DEGRADED.value == 2
        assert HealthStatus.UNHEALTHY.value == 1

        # 名前での確認
        assert HealthStatus.HEALTHY.name == "HEALTHY"
        assert HealthStatus.DEGRADED.name == "DEGRADED"
        assert HealthStatus.UNHEALTHY.name == "UNHEALTHY"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])