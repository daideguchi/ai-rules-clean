"""
MonitoringSystem Implementation
監視・可観測性システム実装
システム全体の健全性・パフォーマンス監視
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Union
from pathlib import Path
import threading
import time
import json
import logging
from collections import deque, defaultdict
import statistics


class MetricType(Enum):
    """メトリクス種別"""
    COUNTER = "COUNTER"          # カウンター（増加のみ）
    GAUGE = "GAUGE"              # ゲージ（任意の値）
    HISTOGRAM = "HISTOGRAM"      # ヒストグラム（分布）
    TIMING = "TIMING"           # タイミング（実行時間）


class AlertSeverity(Enum):
    """アラート重要度"""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class AlertType(Enum):
    """アラート種別"""
    THRESHOLD_EXCEEDED = "THRESHOLD_EXCEEDED"
    ANOMALY_DETECTED = "ANOMALY_DETECTED"
    SYSTEM_FAILURE = "SYSTEM_FAILURE"
    PERFORMANCE_DEGRADATION = "PERFORMANCE_DEGRADATION"
    RESOURCE_EXHAUSTION = "RESOURCE_EXHAUSTION"


@dataclass
class MetricData:
    """メトリクスデータ"""
    name: str
    metric_type: MetricType
    value: Union[int, float]
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)
    description: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            "name": self.name,
            "type": self.metric_type.value,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "labels": self.labels,
            "description": self.description
        }


@dataclass
class Alert:
    """アラート"""
    alert_id: str
    name: str
    severity: AlertSeverity
    alert_type: AlertType
    message: str
    timestamp: datetime
    source_component: str
    metric_name: Optional[str] = None
    threshold_value: Optional[float] = None
    actual_value: Optional[float] = None
    is_resolved: bool = False
    resolved_at: Optional[datetime] = None
    labels: Dict[str, str] = field(default_factory=dict)
    
    def resolve(self) -> None:
        """アラート解決"""
        self.is_resolved = True
        self.resolved_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            "alert_id": self.alert_id,
            "name": self.name,
            "severity": self.severity.value,
            "alert_type": self.alert_type.value,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "source_component": self.source_component,
            "metric_name": self.metric_name,
            "threshold_value": self.threshold_value,
            "actual_value": self.actual_value,
            "is_resolved": self.is_resolved,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "labels": self.labels
        }


@dataclass
class ThresholdRule:
    """閾値ルール"""
    metric_name: str
    operator: str  # "gt", "lt", "gte", "lte", "eq", "ne"
    threshold: float
    severity: AlertSeverity
    message_template: str
    evaluation_window_seconds: int = 60
    minimum_occurrences: int = 1
    labels: Dict[str, str] = field(default_factory=dict)
    
    def evaluate(self, values: List[float]) -> bool:
        """閾値評価"""
        if len(values) < self.minimum_occurrences:
            return False
        
        # 評価ウィンドウ内の値で評価
        recent_values = values[-self.minimum_occurrences:]
        
        for value in recent_values:
            if self.operator == "gt" and value > self.threshold:
                return True
            elif self.operator == "lt" and value < self.threshold:
                return True
            elif self.operator == "gte" and value >= self.threshold:
                return True
            elif self.operator == "lte" and value <= self.threshold:
                return True
            elif self.operator == "eq" and value == self.threshold:
                return True
            elif self.operator == "ne" and value != self.threshold:
                return True
        
        return False


class MetricCollector:
    """メトリクス収集器"""
    
    def __init__(self, max_history_size: int = 10000):
        self.metrics_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_history_size))
        self.current_values: Dict[str, Union[int, float]] = {}
        self._lock = threading.Lock()
    
    def record_metric(self, metric: MetricData) -> None:
        """メトリクス記録"""
        with self._lock:
            key = f"{metric.name}:{json.dumps(metric.labels, sort_keys=True)}"
            self.metrics_history[key].append(metric)
            self.current_values[key] = metric.value
    
    def get_metric_history(self, metric_name: str, 
                         labels: Optional[Dict[str, str]] = None,
                         limit: int = 100) -> List[MetricData]:
        """メトリクス履歴取得"""
        key = f"{metric_name}:{json.dumps(labels or {}, sort_keys=True)}"
        
        with self._lock:
            history = self.metrics_history.get(key, deque())
            return list(history)[-limit:]
    
    def get_current_value(self, metric_name: str, 
                         labels: Optional[Dict[str, str]] = None) -> Optional[Union[int, float]]:
        """現在値取得"""
        key = f"{metric_name}:{json.dumps(labels or {}, sort_keys=True)}"
        return self.current_values.get(key)
    
    def get_metric_statistics(self, metric_name: str,
                            labels: Optional[Dict[str, str]] = None,
                            window_minutes: int = 60) -> Dict[str, float]:
        """メトリクス統計計算"""
        history = self.get_metric_history(metric_name, labels, limit=1000)
        
        # 時間ウィンドウでフィルタ
        cutoff_time = datetime.now() - timedelta(minutes=window_minutes)
        recent_values = [
            m.value for m in history 
            if m.timestamp >= cutoff_time
        ]
        
        if not recent_values:
            return {}
        
        return {
            "count": len(recent_values),
            "min": min(recent_values),
            "max": max(recent_values),
            "mean": statistics.mean(recent_values),
            "median": statistics.median(recent_values),
            "stddev": statistics.stdev(recent_values) if len(recent_values) > 1 else 0.0
        }
    
    def export_metrics(self) -> Dict[str, Any]:
        """メトリクス全エクスポート"""
        with self._lock:
            return {
                "current_values": dict(self.current_values),
                "metrics_count": sum(len(deque_obj) for deque_obj in self.metrics_history.values()),
                "unique_metrics": len(self.metrics_history),
                "timestamp": datetime.now().isoformat()
            }


class AlertManager:
    """アラート管理システム"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.threshold_rules: List[ThresholdRule] = []
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.alert_handlers: List[Callable[[Alert], None]] = []
        self._lock = threading.Lock()
    
    def add_threshold_rule(self, rule: ThresholdRule) -> None:
        """閾値ルール追加"""
        with self._lock:
            self.threshold_rules.append(rule)
            self.logger.info(f"Added threshold rule for {rule.metric_name}")
    
    def add_alert_handler(self, handler: Callable[[Alert], None]) -> None:
        """アラートハンドラー追加"""
        self.alert_handlers.append(handler)
    
    def create_alert(self, name: str, severity: AlertSeverity, alert_type: AlertType,
                    message: str, source_component: str, **kwargs) -> Alert:
        """アラート作成"""
        alert_id = f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.alert_history)}"
        
        alert = Alert(
            alert_id=alert_id,
            name=name,
            severity=severity,
            alert_type=alert_type,
            message=message,
            timestamp=datetime.now(),
            source_component=source_component,
            **kwargs
        )
        
        with self._lock:
            self.active_alerts[alert_id] = alert
            self.alert_history.append(alert)
        
        # ハンドラー実行
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                self.logger.error(f"Alert handler failed: {e}")
        
        self.logger.warning(f"Alert created: {alert.name} ({alert.severity.value})")
        return alert
    
    def resolve_alert(self, alert_id: str) -> bool:
        """アラート解決"""
        with self._lock:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                alert.resolve()
                del self.active_alerts[alert_id]
                self.logger.info(f"Alert resolved: {alert.name}")
                return True
        return False
    
    def evaluate_thresholds(self, metric_collector: MetricCollector) -> List[Alert]:
        """閾値評価・アラート生成"""
        new_alerts = []
        
        for rule in self.threshold_rules:
            try:
                # メトリクス値取得
                history = metric_collector.get_metric_history(
                    rule.metric_name, 
                    rule.labels,
                    limit=100
                )
                
                if not history:
                    continue
                
                # 評価ウィンドウ内の値を抽出
                cutoff_time = datetime.now() - timedelta(seconds=rule.evaluation_window_seconds)
                recent_values = [
                    m.value for m in history 
                    if m.timestamp >= cutoff_time
                ]
                
                # 閾値評価
                if rule.evaluate(recent_values):
                    # 既存のアクティブアラートをチェック
                    existing_alert_key = f"{rule.metric_name}_{rule.operator}_{rule.threshold}"
                    if any(a.name == existing_alert_key for a in self.active_alerts.values()):
                        continue  # 既にアクティブなアラートが存在
                    
                    # 新規アラート作成
                    current_value = recent_values[-1] if recent_values else None
                    alert = self.create_alert(
                        name=existing_alert_key,
                        severity=rule.severity,
                        alert_type=AlertType.THRESHOLD_EXCEEDED,
                        message=rule.message_template.format(
                            metric=rule.metric_name,
                            value=current_value,
                            threshold=rule.threshold
                        ),
                        source_component="monitoring_system",
                        metric_name=rule.metric_name,
                        threshold_value=rule.threshold,
                        actual_value=current_value,
                        labels=rule.labels
                    )
                    new_alerts.append(alert)
                    
            except Exception as e:
                self.logger.error(f"Error evaluating threshold rule {rule.metric_name}: {e}")
        
        return new_alerts
    
    def get_active_alerts(self, severity: Optional[AlertSeverity] = None) -> List[Alert]:
        """アクティブアラート取得"""
        with self._lock:
            alerts = list(self.active_alerts.values())
            if severity:
                alerts = [a for a in alerts if a.severity == severity]
            return sorted(alerts, key=lambda x: x.timestamp, reverse=True)
    
    def get_alert_history(self, limit: int = 100, 
                         severity: Optional[AlertSeverity] = None) -> List[Alert]:
        """アラート履歴取得"""
        with self._lock:
            history = self.alert_history
            if severity:
                history = [a for a in history if a.severity == severity]
            return sorted(history, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    def export_alert_data(self) -> Dict[str, Any]:
        """アラートデータエクスポート"""
        with self._lock:
            return {
                "active_alerts": [a.to_dict() for a in self.active_alerts.values()],
                "recent_history": [a.to_dict() for a in self.alert_history[-50:]],
                "alert_counts_by_severity": {
                    severity.value: len([a for a in self.alert_history if a.severity == severity])
                    for severity in AlertSeverity
                },
                "threshold_rules_count": len(self.threshold_rules)
            }


class SystemHealthMonitor:
    """システムヘルス監視"""
    
    def __init__(self, metric_collector: MetricCollector, alert_manager: AlertManager,
                 logger: Optional[logging.Logger] = None):
        self.metric_collector = metric_collector
        self.alert_manager = alert_manager
        self.logger = logger or logging.getLogger(__name__)
        
        # ヘルス状態
        self.system_health_score = 100.0
        self.component_healths: Dict[str, float] = {}
        self.last_health_check = datetime.now()
        
        # 監視設定
        self.health_check_interval = 30  # 秒
        self.is_monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        
        # デフォルト閾値ルール設定
        self._setup_default_threshold_rules()
    
    def _setup_default_threshold_rules(self) -> None:
        """デフォルト閾値ルール設定"""
        default_rules = [
            ThresholdRule(
                metric_name="session_check_failure_rate",
                operator="gt",
                threshold=0.1,  # 10%以上の失敗率
                severity=AlertSeverity.WARNING,
                message_template="Session check failure rate {value:.2%} exceeds threshold {threshold:.2%}"
            ),
            ThresholdRule(
                metric_name="cache_hit_rate", 
                operator="lt",
                threshold=0.5,  # 50%未満のヒット率
                severity=AlertSeverity.WARNING,
                message_template="Cache hit rate {value:.2%} below threshold {threshold:.2%}"
            ),
            ThresholdRule(
                metric_name="error_count_per_minute",
                operator="gt", 
                threshold=10.0,  # 1分間に10エラー以上
                severity=AlertSeverity.ERROR,
                message_template="Error rate {value} errors/minute exceeds threshold {threshold}"
            ),
            ThresholdRule(
                metric_name="system_health_score",
                operator="lt",
                threshold=70.0,  # ヘルススコア70未満
                severity=AlertSeverity.CRITICAL,
                message_template="System health score {value:.1f} critically low (threshold: {threshold:.1f})"
            )
        ]
        
        for rule in default_rules:
            self.alert_manager.add_threshold_rule(rule)
    
    def start_monitoring(self) -> None:
        """監視開始"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("System health monitoring started")
    
    def stop_monitoring(self) -> None:
        """監視停止"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.logger.info("System health monitoring stopped")
    
    def _monitoring_loop(self) -> None:
        """監視ループ"""
        while self.is_monitoring:
            try:
                self._perform_health_check()
                self.alert_manager.evaluate_thresholds(self.metric_collector)
                time.sleep(self.health_check_interval)
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)  # エラー時は短い間隔で再試行
    
    def _perform_health_check(self) -> None:
        """ヘルスチェック実行"""
        try:
            # システム全体のヘルススコア計算
            component_scores = []
            
            # キャッシュヘルス
            cache_stats = self._get_cache_health()
            if cache_stats:
                cache_score = min(100.0, cache_stats.get("hit_rate", 0.0) * 100)
                component_scores.append(cache_score)
                self.component_healths["cache"] = cache_score
            
            # エラーレート基づくヘルス
            error_health = self._get_error_health()
            component_scores.append(error_health)
            self.component_healths["error_handling"] = error_health
            
            # セッション管理ヘルス
            session_health = self._get_session_health()
            component_scores.append(session_health)
            self.component_healths["session_management"] = session_health
            
            # 全体スコア計算
            if component_scores:
                self.system_health_score = statistics.mean(component_scores)
            else:
                self.system_health_score = 50.0  # デフォルトスコア
            
            # メトリクス記録
            self.metric_collector.record_metric(MetricData(
                name="system_health_score",
                metric_type=MetricType.GAUGE,
                value=self.system_health_score,
                timestamp=datetime.now(),
                description="Overall system health score (0-100)"
            ))
            
            self.last_health_check = datetime.now()
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
    
    def _get_cache_health(self) -> Optional[Dict[str, float]]:
        """キャッシュヘルス取得"""
        try:
            # キャッシュ統計からヘルス計算（実装依存）
            return {"hit_rate": 0.75}  # プレースホルダー
        except Exception:
            return None
    
    def _get_error_health(self) -> float:
        """エラーヘルス計算"""
        try:
            # 直近の時間窓でのエラー率を計算
            error_stats = self.metric_collector.get_metric_statistics(
                "error_count", window_minutes=10
            )
            
            if error_stats:
                error_count = error_stats.get("count", 0)
                # エラー数に基づくヘルススコア（少ないほど高い）
                return max(0, 100 - error_count * 5)
            return 100.0
        except Exception:
            return 50.0
    
    def _get_session_health(self) -> float:
        """セッション管理ヘルス計算"""
        try:
            # セッションチェックの成功率基づくヘルス
            check_stats = self.metric_collector.get_metric_statistics(
                "session_check_success_rate", window_minutes=30
            )
            
            if check_stats:
                success_rate = check_stats.get("mean", 0.0)
                return success_rate * 100
            return 80.0  # デフォルト
        except Exception:
            return 50.0
    
    def get_health_report(self) -> Dict[str, Any]:
        """ヘルスレポート取得"""
        return {
            "system_health_score": self.system_health_score,
            "component_healths": dict(self.component_healths),
            "last_health_check": self.last_health_check.isoformat(),
            "monitoring_active": self.is_monitoring,
            "active_alerts_count": len(self.alert_manager.get_active_alerts()),
            "critical_alerts_count": len(self.alert_manager.get_active_alerts(AlertSeverity.CRITICAL))
        }


class MonitoringSystem:
    """統合監視システム"""
    
    def __init__(self, config: Dict[str, Any], logger: Optional[logging.Logger] = None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        
        # コンポーネント初期化
        self.metric_collector = MetricCollector(
            max_history_size=config.get("max_metric_history", 10000)
        )
        self.alert_manager = AlertManager(self.logger)
        self.health_monitor = SystemHealthMonitor(
            self.metric_collector, self.alert_manager, self.logger
        )
        
        # 設定適用
        self._apply_configuration()
        
        self.logger.info("MonitoringSystem initialized")
    
    def _apply_configuration(self) -> None:
        """設定適用"""
        # アラートハンドラー設定
        if self.config.get("enable_log_alerts", True):
            self.alert_manager.add_alert_handler(self._log_alert)
        
        # ヘルスチェック間隔設定
        if "health_check_interval" in self.config:
            self.health_monitor.health_check_interval = self.config["health_check_interval"]
    
    def _log_alert(self, alert: Alert) -> None:
        """アラートログ出力"""
        level = logging.WARNING
        if alert.severity == AlertSeverity.CRITICAL:
            level = logging.CRITICAL
        elif alert.severity == AlertSeverity.ERROR:
            level = logging.ERROR
        
        self.logger.log(level, f"ALERT: {alert.message}")
    
    def record_metric(self, name: str, value: Union[int, float], 
                     metric_type: MetricType = MetricType.GAUGE,
                     labels: Optional[Dict[str, str]] = None,
                     description: Optional[str] = None) -> None:
        """メトリクス記録"""
        metric = MetricData(
            name=name,
            metric_type=metric_type,
            value=value,
            timestamp=datetime.now(),
            labels=labels or {},
            description=description
        )
        self.metric_collector.record_metric(metric)
    
    def start_monitoring(self) -> None:
        """監視開始"""
        self.health_monitor.start_monitoring()
        self.logger.info("Full monitoring started")
    
    def stop_monitoring(self) -> None:
        """監視停止"""
        self.health_monitor.stop_monitoring()
        self.logger.info("Monitoring stopped")
    
    def get_system_overview(self) -> Dict[str, Any]:
        """システム概要取得"""
        return {
            "health_report": self.health_monitor.get_health_report(),
            "metrics_summary": self.metric_collector.export_metrics(),
            "alerts_summary": self.alert_manager.export_alert_data(),
            "monitoring_config": {
                "health_check_interval": self.health_monitor.health_check_interval,
                "max_metric_history": len(self.metric_collector.metrics_history),
                "threshold_rules_count": len(self.alert_manager.threshold_rules)
            }
        }
    
    def export_diagnostics(self) -> Dict[str, Any]:
        """診断情報エクスポート"""
        return {
            "timestamp": datetime.now().isoformat(),
            "system_overview": self.get_system_overview(),
            "recent_metrics": {
                name: self.metric_collector.get_metric_history(name, limit=10)
                for name in ["system_health_score", "error_count", "cache_hit_rate"]
            },
            "active_alerts": [a.to_dict() for a in self.alert_manager.get_active_alerts()],
            "component_health_trends": self.health_monitor.component_healths
        }