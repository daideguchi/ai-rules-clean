"""
ErrorHandlingSystem Implementation
包括的エラーハンドリング・回復システムの実装
O3・Gemini分析で特定された品質保証不足を解決
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Union, Type
import traceback
import logging
import hashlib
import json
from pathlib import Path
import threading
from abc import ABC, abstractmethod


class ErrorSeverity(Enum):
    """エラー重要度"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    FATAL = "FATAL"


class ErrorCategory(Enum):
    """エラーカテゴリ"""
    VALIDATION = "VALIDATION"
    INTEGRATION = "INTEGRATION"
    SYSTEM = "SYSTEM"
    DATA = "DATA"
    NETWORK = "NETWORK"
    PERMISSION = "PERMISSION"
    TIMEOUT = "TIMEOUT"
    RESOURCE = "RESOURCE"
    BUSINESS_LOGIC = "BUSINESS_LOGIC"
    CONFIGURATION = "CONFIGURATION"


class RecoveryStrategy(Enum):
    """回復戦略"""
    RETRY = "RETRY"
    FALLBACK = "FALLBACK"
    SKIP = "SKIP"
    FAIL_FAST = "FAIL_FAST"
    CIRCUIT_BREAKER = "CIRCUIT_BREAKER"
    GRACEFUL_DEGRADATION = "GRACEFUL_DEGRADATION"
    USER_INTERVENTION = "USER_INTERVENTION"


@dataclass(frozen=True)
class ErrorContext:
    """エラーコンテキスト"""
    component_name: str
    operation_name: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    correlation_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            "component_name": self.component_name,
            "operation_name": self.operation_name,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "correlation_id": self.correlation_id,
            "metadata": self.metadata or {}
        }


@dataclass
class ErrorInfo:
    """エラー情報"""
    error_id: str
    error_type: str
    error_message: str
    severity: ErrorSeverity
    category: ErrorCategory
    context: ErrorContext
    timestamp: datetime
    traceback_info: Optional[str] = None
    original_exception: Optional[Exception] = None
    retry_count: int = 0
    max_retries: int = 3
    recovery_attempted: bool = False
    recovery_successful: bool = False
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if not self.error_id:
            self.error_id = self.generate_error_id()
    
    def generate_error_id(self) -> str:
        """一意のエラーIDを生成"""
        data = f"{self.error_type}:{self.context.component_name}:{self.timestamp.isoformat()}"
        return hashlib.sha256(data.encode('utf-8')).hexdigest()[:16]
    
    def can_retry(self) -> bool:
        """リトライ可能かチェック"""
        return self.retry_count < self.max_retries and self.severity in [
            ErrorSeverity.LOW, ErrorSeverity.MEDIUM
        ]
    
    def should_fail_fast(self) -> bool:
        """即座に失敗すべきかチェック"""
        return self.severity in [ErrorSeverity.FATAL] or self.retry_count >= self.max_retries
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            "error_id": self.error_id,
            "error_type": self.error_type,
            "error_message": self.error_message,
            "severity": self.severity.value,
            "category": self.category.value,
            "context": self.context.to_dict(),
            "timestamp": self.timestamp.isoformat(),
            "traceback_info": self.traceback_info,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "recovery_attempted": self.recovery_attempted,
            "recovery_successful": self.recovery_successful,
            "metadata": self.metadata or {}
        }
    
    @classmethod
    def from_exception(cls,
                      exception: Exception,
                      context: ErrorContext,
                      severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                      category: ErrorCategory = ErrorCategory.SYSTEM) -> 'ErrorInfo':
        """例外からErrorInfoを作成"""
        return cls(
            error_id="",  # __post_init__で生成される
            error_type=type(exception).__name__,
            error_message=str(exception),
            severity=severity,
            category=category,
            context=context,
            timestamp=datetime.now(),
            traceback_info=traceback.format_exc(),
            original_exception=exception
        )


@dataclass
class RecoveryAction:
    """回復アクション"""
    strategy: RecoveryStrategy
    action_name: str
    description: str
    executable: Optional[Callable] = None
    fallback_data: Optional[Any] = None
    timeout_seconds: int = 30
    metadata: Optional[Dict[str, Any]] = None
    
    def execute(self, error_info: ErrorInfo) -> bool:
        """回復アクションを実行"""
        if not self.executable:
            return False
        
        try:
            result = self.executable(error_info)
            return bool(result)
        except Exception:
            return False


class ErrorHandler(ABC):
    """エラーハンドラー抽象基底クラス"""
    
    @abstractmethod
    def can_handle(self, error_info: ErrorInfo) -> bool:
        """このハンドラーがエラーを処理できるかチェック"""
        pass
    
    @abstractmethod
    def handle(self, error_info: ErrorInfo) -> bool:
        """エラーを処理"""
        pass
    
    @abstractmethod
    def get_recovery_actions(self, error_info: ErrorInfo) -> List[RecoveryAction]:
        """回復アクションを取得"""
        pass


class ValidationErrorHandler(ErrorHandler):
    """バリデーションエラーハンドラー"""
    
    def can_handle(self, error_info: ErrorInfo) -> bool:
        return error_info.category == ErrorCategory.VALIDATION
    
    def handle(self, error_info: ErrorInfo) -> bool:
        # バリデーションエラーは通常リトライしない
        return False
    
    def get_recovery_actions(self, error_info: ErrorInfo) -> List[RecoveryAction]:
        return [
            RecoveryAction(
                strategy=RecoveryStrategy.USER_INTERVENTION,
                action_name="request_valid_input",
                description="ユーザーに正しい入力を要求",
                fallback_data={"error_details": error_info.error_message}
            )
        ]


class IntegrationErrorHandler(ErrorHandler):
    """統合エラーハンドラー"""
    
    def can_handle(self, error_info: ErrorInfo) -> bool:
        return error_info.category == ErrorCategory.INTEGRATION
    
    def handle(self, error_info: ErrorInfo) -> bool:
        # 統合エラーはリトライ可能
        return error_info.can_retry()
    
    def get_recovery_actions(self, error_info: ErrorInfo) -> List[RecoveryAction]:
        actions = []
        
        if error_info.can_retry():
            actions.append(RecoveryAction(
                strategy=RecoveryStrategy.RETRY,
                action_name="exponential_backoff_retry",
                description="指数バックオフでリトライ"
            ))
        
        actions.append(RecoveryAction(
            strategy=RecoveryStrategy.FALLBACK,
            action_name="use_fallback_service",
            description="代替サービスを使用"
        ))
        
        return actions


class NetworkErrorHandler(ErrorHandler):
    """ネットワークエラーハンドラー"""
    
    def can_handle(self, error_info: ErrorInfo) -> bool:
        return error_info.category == ErrorCategory.NETWORK
    
    def handle(self, error_info: ErrorInfo) -> bool:
        return error_info.can_retry()
    
    def get_recovery_actions(self, error_info: ErrorInfo) -> List[RecoveryAction]:
        actions = []
        
        if error_info.can_retry():
            actions.append(RecoveryAction(
                strategy=RecoveryStrategy.RETRY,
                action_name="network_retry_with_backoff",
                description="ネットワーク接続をリトライ"
            ))
        
        actions.append(RecoveryAction(
            strategy=RecoveryStrategy.CIRCUIT_BREAKER,
            action_name="enable_circuit_breaker",
            description="サーキットブレーカーを有効化"
        ))
        
        return actions


class SystemErrorHandler(ErrorHandler):
    """システムエラーハンドラー"""
    
    def can_handle(self, error_info: ErrorInfo) -> bool:
        return error_info.category == ErrorCategory.SYSTEM
    
    def handle(self, error_info: ErrorInfo) -> bool:
        if error_info.severity == ErrorSeverity.FATAL:
            return False
        return error_info.can_retry() and error_info.severity in [ErrorSeverity.LOW, ErrorSeverity.MEDIUM]
    
    def get_recovery_actions(self, error_info: ErrorInfo) -> List[RecoveryAction]:
        actions = []
        
        if error_info.severity == ErrorSeverity.FATAL:
            actions.append(RecoveryAction(
                strategy=RecoveryStrategy.FAIL_FAST,
                action_name="system_shutdown",
                description="システムを安全にシャットダウン"
            ))
        elif error_info.can_retry():
            actions.append(RecoveryAction(
                strategy=RecoveryStrategy.RETRY,
                action_name="system_component_restart",
                description="システムコンポーネントを再起動"
            ))
        
        actions.append(RecoveryAction(
            strategy=RecoveryStrategy.GRACEFUL_DEGRADATION,
            action_name="enable_degraded_mode",
            description="機能制限モードで継続"
        ))
        
        return actions


@dataclass
class ErrorStatistics:
    """エラー統計"""
    total_errors: int = 0
    errors_by_severity: Dict[ErrorSeverity, int] = field(default_factory=dict)
    errors_by_category: Dict[ErrorCategory, int] = field(default_factory=dict)
    errors_by_component: Dict[str, int] = field(default_factory=dict)
    recovery_success_rate: float = 0.0
    retry_success_rate: float = 0.0
    last_updated: Optional[datetime] = None
    
    def update_from_error(self, error_info: ErrorInfo) -> None:
        """エラー情報から統計を更新"""
        self.total_errors += 1
        
        # 重要度別
        if error_info.severity not in self.errors_by_severity:
            self.errors_by_severity[error_info.severity] = 0
        self.errors_by_severity[error_info.severity] += 1
        
        # カテゴリ別
        if error_info.category not in self.errors_by_category:
            self.errors_by_category[error_info.category] = 0
        self.errors_by_category[error_info.category] += 1
        
        # コンポーネント別
        component = error_info.context.component_name
        if component not in self.errors_by_component:
            self.errors_by_component[component] = 0
        self.errors_by_component[component] += 1
        
        self.last_updated = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            "total_errors": self.total_errors,
            "errors_by_severity": {k.value: v for k, v in self.errors_by_severity.items()},
            "errors_by_category": {k.value: v for k, v in self.errors_by_category.items()},
            "errors_by_component": self.errors_by_component.copy(),
            "recovery_success_rate": self.recovery_success_rate,
            "retry_success_rate": self.retry_success_rate,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None
        }


class ErrorHandlingSystem:
    """包括的エラーハンドリングシステム"""
    
    def __init__(self, 
                 logger: Optional[logging.Logger] = None,
                 persistence_path: Optional[Path] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.persistence_path = persistence_path
        
        # エラーハンドラー登録
        self.handlers: List[ErrorHandler] = [
            ValidationErrorHandler(),
            IntegrationErrorHandler(),
            NetworkErrorHandler(),
            SystemErrorHandler()
        ]
        
        # エラー履歴とキャッシュ
        self.error_history: List[ErrorInfo] = []
        self.error_cache: Dict[str, ErrorInfo] = {}
        self.statistics = ErrorStatistics()
        
        # スレッドセーフティ
        self._lock = threading.RLock()
        
        # 設定
        self.max_history_size = 1000
        self.cache_ttl_minutes = 60
    
    def handle_error(self, 
                    exception: Exception,
                    context: ErrorContext,
                    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                    category: ErrorCategory = ErrorCategory.SYSTEM) -> Optional[Any]:
        """エラーを処理し、可能であれば回復を試行"""
        
        with self._lock:
            # ErrorInfo作成
            error_info = ErrorInfo.from_exception(
                exception=exception,
                context=context,
                severity=severity,
                category=category
            )
            
            # ログ記録
            self._log_error(error_info)
            
            # 統計更新
            self.statistics.update_from_error(error_info)
            
            # 履歴に追加
            self.error_history.append(error_info)
            self._cleanup_old_errors()
            
            # キャッシュに追加
            self.error_cache[error_info.error_id] = error_info
            
            # 適切なハンドラーを見つけて処理
            recovery_result = self._attempt_recovery(error_info)
            
            # 永続化
            if self.persistence_path:
                self._persist_error(error_info)
            
            return recovery_result
    
    def handle_error_with_fallback(self,
                                  operation: Callable,
                                  fallback: Callable,
                                  context: ErrorContext,
                                  max_retries: int = 3) -> Any:
        """操作を実行し、失敗時にフォールバックを使用"""
        
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                return operation()
            except Exception as e:
                last_exception = e
                
                if attempt < max_retries:
                    # リトライの場合はログのみ
                    self.logger.warning(f"Operation failed, retrying ({attempt + 1}/{max_retries}): {e}")
                    continue
                else:
                    # 最終試行失敗時はエラーハンドリング実行
                    self.handle_error(e, context, ErrorSeverity.HIGH, ErrorCategory.BUSINESS_LOGIC)
                    break
        
        # フォールバック実行
        try:
            self.logger.info("Executing fallback operation")
            return fallback()
        except Exception as fallback_error:
            # フォールバックも失敗
            self.handle_error(fallback_error, context, ErrorSeverity.CRITICAL, ErrorCategory.SYSTEM)
            raise fallback_error
    
    def get_error_by_id(self, error_id: str) -> Optional[ErrorInfo]:
        """エラーIDでエラー情報を取得"""
        with self._lock:
            return self.error_cache.get(error_id)
    
    def get_recent_errors(self, limit: int = 10) -> List[ErrorInfo]:
        """最近のエラーを取得"""
        with self._lock:
            return self.error_history[-limit:] if limit > 0 else self.error_history.copy()
    
    def get_errors_by_component(self, component_name: str) -> List[ErrorInfo]:
        """コンポーネント別エラーを取得"""
        with self._lock:
            return [
                error for error in self.error_history
                if error.context.component_name == component_name
            ]
    
    def get_statistics(self) -> ErrorStatistics:
        """エラー統計を取得"""
        with self._lock:
            return self.statistics
    
    def clear_old_errors(self, older_than_hours: int = 24) -> int:
        """古いエラーをクリア"""
        with self._lock:
            cutoff_time = datetime.now() - timedelta(hours=older_than_hours)
            
            # 履歴クリア
            original_count = len(self.error_history)
            self.error_history = [
                error for error in self.error_history
                if error.timestamp > cutoff_time
            ]
            
            # キャッシュクリア
            cache_keys_to_remove = [
                error_id for error_id, error_info in self.error_cache.items()
                if error_info.timestamp <= cutoff_time
            ]
            
            for error_id in cache_keys_to_remove:
                del self.error_cache[error_id]
            
            removed_count = original_count - len(self.error_history)
            self.logger.info(f"Cleared {removed_count} old errors")
            
            return removed_count
    
    def _attempt_recovery(self, error_info: ErrorInfo) -> Optional[Any]:
        """エラー回復を試行"""
        
        # 適切なハンドラーを見つける
        handler = None
        for h in self.handlers:
            if h.can_handle(error_info):
                handler = h
                break
        
        if not handler:
            self.logger.warning(f"No handler found for error: {error_info.error_type}")
            return None
        
        # ハンドラーで処理可能かチェック
        if not handler.handle(error_info):
            self.logger.info(f"Handler declined to process error: {error_info.error_id}")
            return None
        
        # 回復アクションを取得・実行
        recovery_actions = handler.get_recovery_actions(error_info)
        
        error_info.recovery_attempted = True
        
        for action in recovery_actions:
            try:
                self.logger.info(f"Attempting recovery action: {action.action_name}")
                
                if action.execute(error_info):
                    error_info.recovery_successful = True
                    self.logger.info(f"Recovery successful: {action.action_name}")
                    return action.fallback_data
                    
            except Exception as recovery_error:
                self.logger.error(f"Recovery action failed: {action.action_name}, Error: {recovery_error}")
                continue
        
        self.logger.warning(f"All recovery actions failed for error: {error_info.error_id}")
        return None
    
    def _log_error(self, error_info: ErrorInfo) -> None:
        """エラーをログ出力"""
        log_level = {
            ErrorSeverity.LOW: logging.INFO,
            ErrorSeverity.MEDIUM: logging.WARNING,
            ErrorSeverity.HIGH: logging.ERROR,
            ErrorSeverity.CRITICAL: logging.CRITICAL,
            ErrorSeverity.FATAL: logging.CRITICAL
        }.get(error_info.severity, logging.ERROR)
        
        message = (
            f"Error [{error_info.error_id}] in {error_info.context.component_name}:"
            f"{error_info.context.operation_name} - {error_info.error_message}"
        )
        
        self.logger.log(log_level, message)
        
        if error_info.traceback_info and error_info.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL, ErrorSeverity.FATAL]:
            self.logger.debug(f"Traceback for {error_info.error_id}:\n{error_info.traceback_info}")
    
    def _cleanup_old_errors(self) -> None:
        """古いエラーの自動クリーンアップ"""
        if len(self.error_history) > self.max_history_size:
            # 古いエラーから削除
            excess_count = len(self.error_history) - self.max_history_size
            removed_errors = self.error_history[:excess_count]
            self.error_history = self.error_history[excess_count:]
            
            # キャッシュからも削除
            for error in removed_errors:
                self.error_cache.pop(error.error_id, None)
    
    def _persist_error(self, error_info: ErrorInfo) -> None:
        """エラー情報を永続化"""
        if not self.persistence_path:
            return
        
        try:
            # エラー情報をJSONファイルに保存
            error_file = self.persistence_path / f"error_{error_info.error_id}.json"
            error_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(error_file, 'w', encoding='utf-8') as f:
                json.dump(error_info.to_dict(), f, ensure_ascii=False, indent=2)
                
        except Exception as persist_error:
            self.logger.error(f"Failed to persist error {error_info.error_id}: {persist_error}")
    
    def export_diagnostics(self) -> Dict[str, Any]:
        """診断情報をエクスポート"""
        with self._lock:
            return {
                "system_info": {
                    "total_handlers": len(self.handlers),
                    "max_history_size": self.max_history_size,
                    "cache_ttl_minutes": self.cache_ttl_minutes,
                    "persistence_enabled": self.persistence_path is not None
                },
                "current_state": {
                    "errors_in_history": len(self.error_history),
                    "errors_in_cache": len(self.error_cache),
                    "last_error_time": self.error_history[-1].timestamp.isoformat() if self.error_history else None
                },
                "statistics": self.statistics.to_dict(),
                "recent_errors": [
                    error.to_dict() for error in self.error_history[-5:]
                ]
            }