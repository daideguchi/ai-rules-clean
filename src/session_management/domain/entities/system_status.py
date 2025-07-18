"""
SystemStatus Entity
システム全体の状態を表現するドメインエンティティ
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum
from typing import Any, Dict, List, Optional


class HealthStatus(IntEnum):
    """ヘルスステータス（順序付き）"""

    UNHEALTHY = 1
    DEGRADED = 2
    HEALTHY = 3

    def __str__(self) -> str:
        return self.name


@dataclass(frozen=True)
class SystemMetrics:
    """システムメトリクス"""

    total_checks: int
    successful_checks: int
    failed_checks: int
    average_response_time_ms: int = 0
    cache_hit_rate: Optional[float] = None
    error_rate: Optional[float] = None

    def calculate_success_rate(self) -> float:
        """成功率計算"""
        if self.total_checks == 0:
            return 0.0
        return self.successful_checks / self.total_checks

    def calculate_error_rate(self) -> float:
        """エラー率計算"""
        if self.total_checks == 0:
            return 0.0
        return self.failed_checks / self.total_checks

    def is_performance_acceptable(
        self, max_error_rate: float = 0.1, max_response_time_ms: int = 1000
    ) -> bool:
        """パフォーマンス許容判定"""
        error_rate = self.calculate_error_rate()

        if error_rate > max_error_rate:
            return False

        if self.average_response_time_ms > max_response_time_ms:
            return False

        return True

    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            "total_checks": self.total_checks,
            "successful_checks": self.successful_checks,
            "failed_checks": self.failed_checks,
            "average_response_time_ms": self.average_response_time_ms,
            "cache_hit_rate": self.cache_hit_rate,
            "error_rate": self.error_rate,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SystemMetrics":
        """辞書から復元"""
        return cls(
            total_checks=data["total_checks"],
            successful_checks=data["successful_checks"],
            failed_checks=data["failed_checks"],
            average_response_time_ms=data.get("average_response_time_ms", 0),
            cache_hit_rate=data.get("cache_hit_rate"),
            error_rate=data.get("error_rate"),
        )


@dataclass(frozen=True)
class ComponentHealth:
    """コンポーネントヘルス"""

    component_name: str
    status: HealthStatus
    last_check: datetime
    details: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

    def is_healthy(self) -> bool:
        """健全判定"""
        return self.status == HealthStatus.HEALTHY

    def is_degraded(self) -> bool:
        """劣化判定"""
        return self.status == HealthStatus.DEGRADED

    def is_unhealthy(self) -> bool:
        """不健全判定"""
        return self.status == HealthStatus.UNHEALTHY

    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            "component_name": self.component_name,
            "status": self.status.name,
            "last_check": self.last_check.isoformat(),
            "details": self.details or {},
            "error_message": self.error_message,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ComponentHealth":
        """辞書から復元"""
        return cls(
            component_name=data["component_name"],
            status=HealthStatus[data["status"]],
            last_check=datetime.fromisoformat(data["last_check"]),
            details=data.get("details"),
            error_message=data.get("error_message"),
        )

    def __str__(self) -> str:
        """文字列表現"""
        error_info = f" (Error: {self.error_message})" if self.error_message else ""
        return f"ComponentHealth[{self.component_name}: {self.status.name}{error_info}]"


@dataclass(frozen=True)
class SystemStatus:
    """システム状態エンティティ"""

    overall_health: HealthStatus
    timestamp: datetime
    component_healths: Dict[str, ComponentHealth] = field(default_factory=dict)
    metrics: Optional[SystemMetrics] = None

    @classmethod
    def create_healthy(cls) -> "SystemStatus":
        """健全なシステム状態作成"""
        return cls(
            overall_health=HealthStatus.HEALTHY,
            timestamp=datetime.now(),
            component_healths={},
            metrics=SystemMetrics(0, 0, 0),
        )

    @classmethod
    def create_with_components(
        cls,
        component_healths: List[ComponentHealth],
        metrics: Optional[SystemMetrics] = None,
    ) -> "SystemStatus":
        """コンポーネント付きシステム状態作成"""
        components_dict = {comp.component_name: comp for comp in component_healths}

        # 全体ヘルスを計算
        overall_health = cls._calculate_overall_health(component_healths)

        return cls(
            overall_health=overall_health,
            timestamp=datetime.now(),
            component_healths=components_dict,
            metrics=metrics or SystemMetrics(0, 0, 0),
        )

    @staticmethod
    def _calculate_overall_health(
        component_healths: List[ComponentHealth],
    ) -> HealthStatus:
        """全体ヘルス計算"""
        if not component_healths:
            return HealthStatus.HEALTHY

        # 最も悪い状態を全体状態とする
        min_health = min(comp.status for comp in component_healths)
        return min_health

    def add_component_health(self, component_health: ComponentHealth) -> "SystemStatus":
        """コンポーネントヘルス追加"""
        new_components = self.component_healths.copy()
        new_components[component_health.component_name] = component_health

        # 全体ヘルス再計算
        all_healths = list(new_components.values())
        new_overall_health = self._calculate_overall_health(all_healths)

        return SystemStatus(
            overall_health=new_overall_health,
            timestamp=datetime.now(),
            component_healths=new_components,
            metrics=self.metrics,
        )

    def update_component_health(
        self, component_name: str, new_health: ComponentHealth
    ) -> "SystemStatus":
        """コンポーネントヘルス更新"""
        if component_name not in self.component_healths:
            raise ValueError(f"Component {component_name} not found")

        new_components = self.component_healths.copy()
        new_components[component_name] = new_health

        # 全体ヘルス再計算
        all_healths = list(new_components.values())
        new_overall_health = self._calculate_overall_health(all_healths)

        return SystemStatus(
            overall_health=new_overall_health,
            timestamp=datetime.now(),
            component_healths=new_components,
            metrics=self.metrics,
        )

    def get_component_health(self, component_name: str) -> Optional[ComponentHealth]:
        """コンポーネントヘルス取得"""
        return self.component_healths.get(component_name)

    def get_unhealthy_components(self) -> List[ComponentHealth]:
        """不健全コンポーネント取得"""
        return [
            comp
            for comp in self.component_healths.values()
            if comp.status != HealthStatus.HEALTHY
        ]

    def is_healthy(self) -> bool:
        """健全判定"""
        return self.overall_health == HealthStatus.HEALTHY

    def is_degraded(self) -> bool:
        """劣化判定"""
        return self.overall_health == HealthStatus.DEGRADED

    def is_unhealthy(self) -> bool:
        """不健全判定"""
        return self.overall_health == HealthStatus.UNHEALTHY

    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            "overall_health": self.overall_health.name,
            "timestamp": self.timestamp.isoformat(),
            "component_healths": {
                name: comp.to_dict() for name, comp in self.component_healths.items()
            },
            "metrics": self.metrics.to_dict() if self.metrics else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SystemStatus":
        """辞書から復元"""
        component_healths = {}
        for name, comp_data in data.get("component_healths", {}).items():
            component_healths[name] = ComponentHealth.from_dict(comp_data)

        metrics = None
        if data.get("metrics"):
            metrics = SystemMetrics.from_dict(data["metrics"])

        return cls(
            overall_health=HealthStatus[data["overall_health"]],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            component_healths=component_healths,
            metrics=metrics,
        )

    def __str__(self) -> str:
        """文字列表現"""
        component_count = len(self.component_healths)
        unhealthy_count = len(self.get_unhealthy_components())

        return (
            f"SystemStatus[{self.overall_health.name}] "
            f"components:{component_count} "
            f"unhealthy:{unhealthy_count} "
            f"@{self.timestamp.strftime('%H:%M:%S')}"
        )
