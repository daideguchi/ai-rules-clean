"""
MonitoringSystem Tests
監視・可観測性システムのテスト
"""

import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock

import pytest

sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent / "src"))

from session_management.infrastructure.monitoring.monitoring_system import (
    Alert,
    AlertManager,
    AlertSeverity,
    AlertType,
    MetricCollector,
    MetricData,
    MetricType,
    MonitoringSystem,
    SystemHealthMonitor,
    ThresholdRule,
)


class TestMetricData:
    """MetricDataのテスト"""

    def test_metric_data_creation(self):
        """メトリクスデータ作成"""
        metric = MetricData(
            name="test_metric",
            metric_type=MetricType.GAUGE,
            value=42.0,
            timestamp=datetime.now(),
            labels={"component": "test"},
            description="Test metric"
        )

        assert metric.name == "test_metric"
        assert metric.metric_type == MetricType.GAUGE
        assert metric.value == 42.0
        assert metric.labels["component"] == "test"

    def test_metric_data_to_dict(self):
        """メトリクスデータ辞書変換"""
        timestamp = datetime.now()
        metric = MetricData(
            name="test_metric",
            metric_type=MetricType.COUNTER,
            value=100,
            timestamp=timestamp,
            labels={"env": "test"}
        )

        data = metric.to_dict()
        assert data["name"] == "test_metric"
        assert data["type"] == "COUNTER"
        assert data["value"] == 100
        assert data["timestamp"] == timestamp.isoformat()
        assert data["labels"]["env"] == "test"


class TestAlert:
    """Alertのテスト"""

    def test_alert_creation(self):
        """アラート作成"""
        alert = Alert(
            alert_id="test_alert_1",
            name="Test Alert",
            severity=AlertSeverity.WARNING,
            alert_type=AlertType.THRESHOLD_EXCEEDED,
            message="Test alert message",
            timestamp=datetime.now(),
            source_component="test_component"
        )

        assert alert.alert_id == "test_alert_1"
        assert alert.severity == AlertSeverity.WARNING
        assert not alert.is_resolved

    def test_alert_resolution(self):
        """アラート解決"""
        alert = Alert(
            alert_id="test_alert_2",
            name="Test Alert",
            severity=AlertSeverity.ERROR,
            alert_type=AlertType.SYSTEM_FAILURE,
            message="Test message",
            timestamp=datetime.now(),
            source_component="test"
        )

        assert not alert.is_resolved
        assert alert.resolved_at is None

        alert.resolve()

        assert alert.is_resolved
        assert alert.resolved_at is not None


class TestThresholdRule:
    """ThresholdRuleのテスト"""

    def test_threshold_evaluation_greater_than(self):
        """閾値評価（より大きい）"""
        rule = ThresholdRule(
            metric_name="cpu_usage",
            operator="gt",
            threshold=80.0,
            severity=AlertSeverity.WARNING,
            message_template="CPU usage high: {value}%"
        )

        # 閾値を超えている
        assert rule.evaluate([85.0, 90.0]) is True

        # 閾値を超えていない
        assert rule.evaluate([70.0, 75.0]) is False

        # 値が不足
        assert rule.evaluate([]) is False

    def test_threshold_evaluation_less_than(self):
        """閾値評価（より小さい）"""
        rule = ThresholdRule(
            metric_name="disk_free",
            operator="lt",
            threshold=10.0,
            severity=AlertSeverity.CRITICAL,
            message_template="Disk space low: {value}%",
            minimum_occurrences=2
        )

        # 閾値を下回っている（十分な出現回数）
        assert rule.evaluate([5.0, 8.0, 7.0]) is True

        # 閾値を下回っているが出現回数不足
        assert rule.evaluate([8.0]) is False

        # 閾値を下回っていない
        assert rule.evaluate([15.0, 20.0]) is False


class TestMetricCollector:
    """MetricCollectorのテスト"""

    def setup_method(self):
        """テストセットアップ"""
        self.collector = MetricCollector(max_history_size=100)

    def test_record_metric(self):
        """メトリクス記録"""
        metric = MetricData(
            name="test_metric",
            metric_type=MetricType.GAUGE,
            value=42.0,
            timestamp=datetime.now()
        )

        self.collector.record_metric(metric)

        # 現在値確認
        current_value = self.collector.get_current_value("test_metric")
        assert current_value == 42.0

        # 履歴確認
        history = self.collector.get_metric_history("test_metric")
        assert len(history) == 1
        assert history[0].value == 42.0

    def test_metric_with_labels(self):
        """ラベル付きメトリクス"""
        metric1 = MetricData(
            name="requests_total",
            metric_type=MetricType.COUNTER,
            value=100,
            timestamp=datetime.now(),
            labels={"method": "GET", "status": "200"}
        )

        metric2 = MetricData(
            name="requests_total",
            metric_type=MetricType.COUNTER,
            value=50,
            timestamp=datetime.now(),
            labels={"method": "POST", "status": "200"}
        )

        self.collector.record_metric(metric1)
        self.collector.record_metric(metric2)

        # 異なるラベルで区別される
        get_value = self.collector.get_current_value(
            "requests_total", {"method": "GET", "status": "200"}
        )
        post_value = self.collector.get_current_value(
            "requests_total", {"method": "POST", "status": "200"}
        )

        assert get_value == 100
        assert post_value == 50

    def test_metric_statistics(self):
        """メトリクス統計計算"""
        # 複数のメトリクスを記録
        for i, value in enumerate([10, 20, 30, 40, 50]):
            metric = MetricData(
                name="response_time",
                metric_type=MetricType.TIMING,
                value=value,
                timestamp=datetime.now() - timedelta(minutes=i)
            )
            self.collector.record_metric(metric)

        stats = self.collector.get_metric_statistics("response_time", window_minutes=60)

        assert stats["count"] == 5
        assert stats["min"] == 10
        assert stats["max"] == 50
        assert stats["mean"] == 30.0
        assert stats["median"] == 30.0

    def test_export_metrics(self):
        """メトリクスエクスポート"""
        # いくつかのメトリクスを記録
        for i in range(5):
            metric = MetricData(
                name=f"metric_{i}",
                metric_type=MetricType.GAUGE,
                value=i * 10,
                timestamp=datetime.now()
            )
            self.collector.record_metric(metric)

        export_data = self.collector.export_metrics()

        assert "current_values" in export_data
        assert "metrics_count" in export_data
        assert "unique_metrics" in export_data
        assert export_data["unique_metrics"] == 5


class TestAlertManager:
    """AlertManagerのテスト"""

    def setup_method(self):
        """テストセットアップ"""
        self.logger = Mock()
        self.alert_manager = AlertManager(self.logger)

    def test_create_alert(self):
        """アラート作成"""
        alert = self.alert_manager.create_alert(
            name="Test Alert",
            severity=AlertSeverity.WARNING,
            alert_type=AlertType.THRESHOLD_EXCEEDED,
            message="Test alert message",
            source_component="test_component"
        )

        assert alert.name == "Test Alert"
        assert alert.severity == AlertSeverity.WARNING
        assert len(self.alert_manager.active_alerts) == 1
        assert len(self.alert_manager.alert_history) == 1

    def test_resolve_alert(self):
        """アラート解決"""
        alert = self.alert_manager.create_alert(
            name="Test Alert",
            severity=AlertSeverity.ERROR,
            alert_type=AlertType.SYSTEM_FAILURE,
            message="Test message",
            source_component="test"
        )

        alert_id = alert.alert_id

        # アラート解決
        success = self.alert_manager.resolve_alert(alert_id)

        assert success is True
        assert len(self.alert_manager.active_alerts) == 0
        assert alert.is_resolved is True

    def test_threshold_evaluation(self):
        """閾値評価"""
        # 閾値ルール追加
        rule = ThresholdRule(
            metric_name="cpu_usage",
            operator="gt",
            threshold=80.0,
            severity=AlertSeverity.WARNING,
            message_template="CPU usage high: {value}%"
        )
        self.alert_manager.add_threshold_rule(rule)

        # メトリクスコレクター作成
        collector = MetricCollector()

        # 閾値を超えるメトリクス記録
        metric = MetricData(
            name="cpu_usage",
            metric_type=MetricType.GAUGE,
            value=90.0,
            timestamp=datetime.now()
        )
        collector.record_metric(metric)

        # 閾値評価実行
        new_alerts = self.alert_manager.evaluate_thresholds(collector)

        assert len(new_alerts) == 1
        assert new_alerts[0].severity == AlertSeverity.WARNING
        assert "CPU usage high" in new_alerts[0].message

    def test_alert_handler(self):
        """アラートハンドラー"""
        handler_calls = []

        def test_handler(alert):
            handler_calls.append(alert)

        self.alert_manager.add_alert_handler(test_handler)

        # アラート作成
        alert = self.alert_manager.create_alert(
            name="Handler Test",
            severity=AlertSeverity.INFO,
            alert_type=AlertType.ANOMALY_DETECTED,
            message="Test message",
            source_component="test"
        )

        # ハンドラーが呼ばれることを確認
        assert len(handler_calls) == 1
        assert handler_calls[0] == alert

    def test_get_alerts_by_severity(self):
        """重要度別アラート取得"""
        # 異なる重要度のアラートを作成
        self.alert_manager.create_alert(
            "Warning Alert", AlertSeverity.WARNING, AlertType.THRESHOLD_EXCEEDED, "msg", "comp"
        )
        self.alert_manager.create_alert(
            "Critical Alert", AlertSeverity.CRITICAL, AlertType.SYSTEM_FAILURE, "msg", "comp"
        )
        self.alert_manager.create_alert(
            "Info Alert", AlertSeverity.INFO, AlertType.ANOMALY_DETECTED, "msg", "comp"
        )

        # 重要度別取得
        warning_alerts = self.alert_manager.get_active_alerts(AlertSeverity.WARNING)
        critical_alerts = self.alert_manager.get_active_alerts(AlertSeverity.CRITICAL)

        assert len(warning_alerts) == 1
        assert len(critical_alerts) == 1
        assert warning_alerts[0].severity == AlertSeverity.WARNING
        assert critical_alerts[0].severity == AlertSeverity.CRITICAL


class TestSystemHealthMonitor:
    """SystemHealthMonitorのテスト"""

    def setup_method(self):
        """テストセットアップ"""
        self.collector = MetricCollector()
        self.alert_manager = AlertManager()
        self.logger = Mock()
        self.monitor = SystemHealthMonitor(
            self.collector, self.alert_manager, self.logger
        )

    def test_health_monitor_initialization(self):
        """ヘルス監視初期化"""
        assert self.monitor.system_health_score == 100.0
        assert not self.monitor.is_monitoring
        assert self.monitor.health_check_interval == 30

    def test_health_report(self):
        """ヘルスレポート"""
        report = self.monitor.get_health_report()

        assert "system_health_score" in report
        assert "component_healths" in report
        assert "last_health_check" in report
        assert "monitoring_active" in report
        assert "active_alerts_count" in report

        assert report["system_health_score"] == 100.0
        assert not report["monitoring_active"]

    def test_start_stop_monitoring(self):
        """監視開始・停止"""
        # 監視開始
        self.monitor.start_monitoring()
        assert self.monitor.is_monitoring is True
        assert self.monitor.monitor_thread is not None

        # 少し待機してヘルスチェックが実行されることを確認
        time.sleep(0.1)

        # 監視停止
        self.monitor.stop_monitoring()
        assert self.monitor.is_monitoring is False


class TestMonitoringSystem:
    """MonitoringSystemのテスト"""

    def setup_method(self):
        """テストセットアップ"""
        self.config = {
            "max_metric_history": 1000,
            "enable_log_alerts": True,
            "health_check_interval": 10
        }
        self.logger = Mock()
        self.monitoring = MonitoringSystem(self.config, self.logger)

    def test_monitoring_system_initialization(self):
        """監視システム初期化"""
        assert self.monitoring.metric_collector is not None
        assert self.monitoring.alert_manager is not None
        assert self.monitoring.health_monitor is not None
        assert self.monitoring.health_monitor.health_check_interval == 10

    def test_record_metric(self):
        """メトリクス記録"""
        self.monitoring.record_metric(
            name="test_metric",
            value=42.0,
            metric_type=MetricType.GAUGE,
            labels={"component": "test"},
            description="Test metric"
        )

        # メトリクスが記録されることを確認
        current_value = self.monitoring.metric_collector.get_current_value(
            "test_metric", {"component": "test"}
        )
        assert current_value == 42.0

    def test_start_stop_monitoring(self):
        """監視開始・停止"""
        # 監視開始
        self.monitoring.start_monitoring()
        assert self.monitoring.health_monitor.is_monitoring is True

        # 監視停止
        self.monitoring.stop_monitoring()
        assert self.monitoring.health_monitor.is_monitoring is False

    def test_system_overview(self):
        """システム概要"""
        # いくつかのメトリクスを記録
        self.monitoring.record_metric("test_metric_1", 10.0)
        self.monitoring.record_metric("test_metric_2", 20.0)

        overview = self.monitoring.get_system_overview()

        assert "health_report" in overview
        assert "metrics_summary" in overview
        assert "alerts_summary" in overview
        assert "monitoring_config" in overview

        # メトリクスが記録されていることを確認
        assert overview["metrics_summary"]["unique_metrics"] >= 2

    def test_export_diagnostics(self):
        """診断情報エクスポート"""
        # データ準備
        self.monitoring.record_metric("system_health_score", 85.0)
        self.monitoring.record_metric("error_count", 5)

        diagnostics = self.monitoring.export_diagnostics()

        assert "timestamp" in diagnostics
        assert "system_overview" in diagnostics
        assert "recent_metrics" in diagnostics
        assert "active_alerts" in diagnostics
        assert "component_health_trends" in diagnostics

    def test_integration_with_alerts(self):
        """アラート統合テスト"""
        # 閾値を超えるメトリクスを記録
        self.monitoring.record_metric("error_count_per_minute", 15.0)

        # 閾値評価実行
        alerts = self.monitoring.alert_manager.evaluate_thresholds(
            self.monitoring.metric_collector
        )

        # アラートが生成されることを確認
        assert len(alerts) > 0

        # アラートが適切な重要度であることを確認
        error_alerts = [a for a in alerts if a.severity == AlertSeverity.ERROR]
        assert len(error_alerts) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
