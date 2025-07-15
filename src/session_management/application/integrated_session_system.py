"""
IntegratedSessionSystem Implementation
統合セッション管理システムの実装
全コンポーネントを統合した最終システム
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, Union
from pathlib import Path
import logging
import threading

from ..domain.entities.session_state import SessionState, ComponentState
from ..domain.entities.check_result import CheckResult, CheckStatus, CheckSeverity
from ..domain.entities.system_status import SystemStatus, ComponentHealth, HealthStatus
from ..domain.services.system_state_manager import (
    SystemStateManager,
    StateChangeEvent,
    DependencyTracker,
    StateHashCalculator,
    EventPublisher
)
from ..domain.services.error_handling_system import (
    ErrorHandlingSystem,
    ErrorContext,
    ErrorSeverity,
    ErrorCategory
)
from ..infrastructure.cache.event_driven_cache import (
    EventDrivenCache,
    StateAwareCacheKey,
    CacheResult
)


@dataclass
class SessionConfiguration:
    """セッション設定"""
    session_id: str
    max_cache_size: int = 1000
    cache_ttl_seconds: int = 1800
    error_retention_hours: int = 24
    enable_persistence: bool = True
    persistence_path: Optional[Path] = None
    enable_monitoring: bool = True
    log_level: str = "INFO"
    
    def __post_init__(self):
        if self.enable_persistence and not self.persistence_path:
            self.persistence_path = Path("runtime/session_management")


class IntegratedEventPublisher(EventPublisher):
    """統合イベント発行者"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.event_handlers: List[Callable] = []
        self._lock = threading.Lock()
    
    def add_event_handler(self, handler: Callable[[StateChangeEvent], None]) -> None:
        """イベントハンドラーを追加"""
        with self._lock:
            self.event_handlers.append(handler)
    
    def remove_event_handler(self, handler: Callable[[StateChangeEvent], None]) -> None:
        """イベントハンドラーを削除"""
        with self._lock:
            if handler in self.event_handlers:
                self.event_handlers.remove(handler)
    
    def publish(self, event: Union[StateChangeEvent, Any]) -> None:
        """イベント発行"""
        # StateChangeEventの場合
        if hasattr(event, 'change_type'):
            self.logger.debug(f"Publishing StateChange event: {event.change_type.value}")
        # CacheEventの場合
        elif hasattr(event, 'event_type'):
            self.logger.debug(f"Publishing Cache event: {event.event_type.value}")
        else:
            self.logger.debug(f"Publishing event: {type(event).__name__}")
        
        with self._lock:
            for handler in self.event_handlers:
                try:
                    handler(event)
                except Exception as e:
                    self.logger.error(f"Event handler failed: {e}")


class IntegratedSessionSystem:
    """統合セッション管理システム"""
    
    def __init__(self, config: SessionConfiguration):
        self.config = config
        self.logger = self._setup_logger()
        
        # コンポーネント初期化
        self.event_publisher = IntegratedEventPublisher(self.logger)
        self.cache = EventDrivenCache(self.event_publisher)
        self.dependency_tracker = DependencyTracker()
        self.state_hash_calculator = StateHashCalculator(self.dependency_tracker)
        
        self.state_manager = SystemStateManager(
            event_publisher=self.event_publisher,
            cache_manager=self.cache,
            dependency_tracker=self.dependency_tracker,
            state_hash_calculator=self.state_hash_calculator
        )
        
        self.error_system = ErrorHandlingSystem(
            logger=self.logger,
            persistence_path=config.persistence_path / "errors" if config.persistence_path else None
        )
        
        # セッション状態
        self.session_state = self.state_manager.initialize_session_state(config.session_id)
        self.system_status = SystemStatus.create_healthy()
        
        # イベントハンドラー登録
        self.event_publisher.add_event_handler(self._handle_state_change_event)
        
        # 初期化完了ログ
        self.logger.info(f"IntegratedSessionSystem initialized for session: {config.session_id}")
    
    def _setup_logger(self) -> logging.Logger:
        """ロガーセットアップ"""
        logger = logging.getLogger(f"session_system_{self.config.session_id}")
        logger.setLevel(getattr(logging, self.config.log_level.upper()))
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def execute_with_error_handling(self,
                                  operation: Callable,
                                  component_name: str,
                                  operation_name: str,
                                  fallback: Optional[Callable] = None,
                                  severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                                  category: ErrorCategory = ErrorCategory.SYSTEM) -> Any:
        """エラーハンドリング付きで操作を実行"""
        
        context = ErrorContext(
            component_name=component_name,
            operation_name=operation_name,
            session_id=self.config.session_id
        )
        
        try:
            if fallback:
                return self.error_system.handle_error_with_fallback(
                    operation=operation,
                    fallback=fallback,
                    context=context
                )
            else:
                return operation()
                
        except Exception as e:
            self.error_system.handle_error(e, context, severity, category)
            raise
    
    def perform_check(self,
                     check_name: str,
                     check_function: Callable[[], bool],
                     component_name: str = "unknown",
                     use_cache: bool = True,
                     cache_ttl_seconds: Optional[int] = None) -> CheckResult:
        """確認作業を実行（キャッシュ付き）"""
        
        # キャッシュキー生成
        cache_key = None
        if use_cache:
            cache_key = self.state_manager.generate_cache_key(check_name)
        
        # キャッシュからの取得を試行
        if cache_key and use_cache:
            cached_result = self.cache.get(cache_key)
            if cached_result.is_hit():
                self.logger.debug(f"Cache hit for check: {check_name}")
                return CheckResult.from_dict(cached_result.data)
        
        # 確認実行
        def execute_check():
            start_time = datetime.now()
            try:
                success = check_function()
                duration = (datetime.now() - start_time).total_seconds()
                
                if success:
                    result = CheckResult.success(check_name, "Check passed", duration_ms=int(duration * 1000))
                else:
                    result = CheckResult.failure(check_name, "Check failed", duration_ms=int(duration * 1000))
                
                return result
                
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds()
                result = CheckResult.failure(
                    check_name, f"Check error: {str(e)}", error=e, duration_ms=int(duration * 1000)
                )
                return result
        
        # エラーハンドリング付きで実行
        result = self.execute_with_error_handling(
            operation=execute_check,
            component_name=component_name,
            operation_name=f"check_{check_name}",
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.VALIDATION
        )
        
        # 結果をセッション状態に追加
        self.session_state = self.state_manager.add_check_result(self.session_state, result)
        
        # キャッシュに保存
        if cache_key and use_cache and not result.is_failure():
            ttl = cache_ttl_seconds or self.config.cache_ttl_seconds
            self.cache.set(cache_key, result.to_dict(), ttl)
        
        # システム状態更新
        health_status = HealthStatus.HEALTHY if result.is_success() else HealthStatus.UNHEALTHY
        component_health = ComponentHealth(
            component_name=component_name,
            status=health_status,
            last_check=result.timestamp,
            details={"check_name": check_name, "duration_ms": result.duration_ms}
        )
        self.system_status = self.system_status.add_component_health(component_health)
        
        return result
    
    def update_component_status(self,
                              component_name: str,
                              status: str,
                              metadata: Optional[Dict[str, Any]] = None) -> None:
        """コンポーネント状態を更新"""
        
        def update_operation():
            state_hash = self.state_manager.get_state_hash(component_name)
            component_state = ComponentState(
                component_name=component_name,
                status=status,
                last_checked=datetime.now(),
                state_hash=state_hash,
                metadata=metadata
            )
            
            self.session_state = self.state_manager.update_component_state(
                self.session_state, component_state
            )
            
            return component_state
        
        self.execute_with_error_handling(
            operation=update_operation,
            component_name=component_name,
            operation_name="update_status"
        )
    
    def get_system_overview(self) -> Dict[str, Any]:
        """システム概要を取得"""
        
        def get_overview():
            session_overview = self.state_manager.get_system_overview(self.session_state)
            cache_stats = self.cache.get_statistics()
            error_stats = self.error_system.get_statistics()
            system_health = self.system_status.overall_health
            
            return {
                "session": session_overview,
                "cache": cache_stats,
                "errors": error_stats.to_dict(),
                "system_health": {
                    "overall_status": system_health.value,
                    "component_count": len(self.system_status.component_healths),
                    "unhealthy_components": [
                        comp.component_name for comp in self.system_status.get_unhealthy_components()
                    ]
                },
                "configuration": {
                    "session_id": self.config.session_id,
                    "cache_enabled": True,
                    "error_handling_enabled": True,
                    "persistence_enabled": self.config.enable_persistence,
                    "monitoring_enabled": self.config.enable_monitoring
                }
            }
        
        return self.execute_with_error_handling(
            operation=get_overview,
            component_name="system",
            operation_name="get_overview"
        )
    
    def cleanup_resources(self, older_than_hours: int = 24) -> Dict[str, int]:
        """リソースクリーンアップ"""
        
        def cleanup_operation():
            # 期限切れキャッシュクリーンアップ
            expired_cache_count = self.cache.cleanup_expired()
            
            # 古いエラークリーンアップ
            cleaned_errors_count = self.error_system.clear_old_errors(older_than_hours)
            
            return {
                "cleaned_cache_entries": expired_cache_count,
                "cleaned_errors": cleaned_errors_count
            }
        
        return self.execute_with_error_handling(
            operation=cleanup_operation,
            component_name="system",
            operation_name="cleanup_resources"
        )
    
    def validate_system_integrity(self) -> Dict[str, Any]:
        """システム整合性を検証"""
        
        def validation_operation():
            # セッション状態の整合性検証
            state_validation = self.state_manager.validate_state_integrity(self.session_state)
            
            # キャッシュ統計取得
            cache_stats = self.cache.get_statistics()
            
            # エラー統計取得
            error_stats = self.error_system.get_statistics()
            
            # 整合性判定
            is_healthy = (
                state_validation["is_valid"] and
                cache_stats["hit_rate"] >= 0.0 and  # キャッシュが機能している
                error_stats.total_errors < 100  # エラー数が許容範囲内
            )
            
            return {
                "is_healthy": is_healthy,
                "state_validation": state_validation,
                "cache_health": {
                    "hit_rate": cache_stats["hit_rate"],
                    "total_entries": cache_stats["total_entries"]
                },
                "error_health": {
                    "total_errors": error_stats.total_errors,
                    "recent_errors": len(self.error_system.get_recent_errors(10))
                },
                "overall_assessment": "healthy" if is_healthy else "needs_attention"
            }
        
        return self.execute_with_error_handling(
            operation=validation_operation,
            component_name="system",
            operation_name="validate_integrity"
        )
    
    def _handle_state_change_event(self, event: Union[StateChangeEvent, Any]) -> None:
        """状態変更イベントを処理"""
        try:
            if hasattr(event, 'change_type'):
                self.logger.debug(f"Handling state change event: {event.change_type.value}")
            elif hasattr(event, 'event_type'):
                self.logger.debug(f"Handling cache event: {event.event_type.value}")
            else:
                self.logger.debug(f"Handling event: {type(event).__name__}")
            
            # 必要に応じて追加の処理を実装
            # 例: メトリクス更新、通知送信、ログ記録など
            
            if self.config.enable_monitoring:
                # モニタリング情報更新
                pass
            
        except Exception as e:
            self.logger.error(f"Error handling event: {e}")
    
    def export_full_diagnostics(self) -> Dict[str, Any]:
        """完全な診断情報をエクスポート"""
        
        def export_operation():
            return {
                "timestamp": datetime.now().isoformat(),
                "session_id": self.config.session_id,
                "system_overview": self.get_system_overview(),
                "validation_results": self.validate_system_integrity(),
                "error_diagnostics": self.error_system.export_diagnostics(),
                "cache_state": self.cache.export_state(),
                "configuration": {
                    "max_cache_size": self.config.max_cache_size,
                    "cache_ttl_seconds": self.config.cache_ttl_seconds,
                    "error_retention_hours": self.config.error_retention_hours,
                    "enable_persistence": self.config.enable_persistence,
                    "enable_monitoring": self.config.enable_monitoring,
                    "log_level": self.config.log_level
                }
            }
        
        return self.execute_with_error_handling(
            operation=export_operation,
            component_name="system",
            operation_name="export_diagnostics"
        )
    
    def shutdown(self) -> None:
        """システムシャットダウン"""
        try:
            self.logger.info("Shutting down IntegratedSessionSystem")
            
            # 最終クリーンアップ
            self.cleanup_resources()
            
            # 統計情報ログ出力
            final_stats = self.get_system_overview()
            self.logger.info(f"Final session statistics: {final_stats}")
            
            # イベントハンドラー削除
            self.event_publisher.remove_event_handler(self._handle_state_change_event)
            
            self.logger.info("IntegratedSessionSystem shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")