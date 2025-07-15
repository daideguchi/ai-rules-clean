# 🏗️ 新システムアーキテクチャ設計 - Enterprise Grade

**設計日時**: 2025-07-15T12:XX:XX  
**設計原則**: O3 + Gemini分析準拠・関心事分離・依存性注入・状態管理  
**品質目標**: 99.9%精度・テストカバレッジ90%・1秒応答時間

## 🎯 設計原則（SOLID + DDD + Clean Architecture）

### 1. 単一責任原則（Single Responsibility Principle）
```python
# ❌ 現在：1クラスが全責任（廃止済み）
class SmartSessionChecker:  # 確認・キャッシュ・テンプレート・エラー処理

# ✅ 新設計：責任分離
class SessionCheckOrchestrator:     # 確認プロセス統括
class SystemStateManager:          # 状態管理専門
class CacheManager:                # キャッシュ専門
class TemplateRenderer:            # テンプレート生成専門
class ErrorHandler:                # エラー処理専門
```

### 2. 依存性注入（Dependency Injection）
```python
# ✅ 新設計：テスト可能・拡張可能・設定外部化
class SessionCheckOrchestrator:
    def __init__(
        self,
        state_manager: SystemStateManager,
        cache_manager: CacheManager,
        template_renderer: TemplateRenderer,
        error_handler: ErrorHandler,
        logger: Logger
    ):
        self.state_manager = state_manager
        self.cache_manager = cache_manager
        self.template_renderer = template_renderer
        self.error_handler = error_handler
        self.logger = logger
```

### 3. インターフェース分離（Interface Segregation）
```python
# ✅ 細分化されたインターフェース
class StateChecker(Protocol):
    def check_president_status(self) -> CheckResult: ...
    def check_cursor_rules(self) -> CheckResult: ...

class CacheProvider(Protocol):
    def get(self, key: str, validator: Callable) -> CacheResult: ...
    def set(self, key: str, value: Any, ttl: int) -> None: ...
    def invalidate(self, key: str) -> None: ...

class EventPublisher(Protocol):
    def publish(self, event: Event) -> None: ...
```

## 🏛️ アーキテクチャ構造（Hexagonal Architecture）

### Core Domain（ビジネスロジック）
```
src/session_management/
├── domain/
│   ├── entities/
│   │   ├── check_result.py        # 確認結果エンティティ
│   │   ├── session_state.py       # セッション状態エンティティ
│   │   └── system_status.py       # システム状態エンティティ
│   ├── value_objects/
│   │   ├── check_level.py         # 確認レベル（SIMPLE/MEDIUM/COMPLEX/CRITICAL）
│   │   ├── cache_key.py           # キャッシュキー（状態ハッシュ含む）
│   │   └── template_context.py    # テンプレートコンテキスト
│   ├── services/
│   │   ├── session_check_service.py    # セッション確認サービス
│   │   ├── state_sync_service.py       # 状態同期サービス
│   │   └── template_generation_service.py # テンプレート生成サービス
│   └── repositories/
│       ├── state_repository.py         # 状態永続化
│       └── cache_repository.py         # キャッシュ永続化
```

### Infrastructure（技術詳細）
```
src/session_management/
├── infrastructure/
│   ├── state_checkers/
│   │   ├── president_status_checker.py    # PRESIDENT状態確認
│   │   ├── cursor_rules_checker.py        # Cursor Rules確認
│   │   └── system_status_checker.py       # システム状態確認
│   ├── cache/
│   │   ├── event_driven_cache.py          # イベント駆動キャッシュ
│   │   ├── file_watcher.py                # ファイル変更監視
│   │   └── cache_invalidator.py           # キャッシュ無効化
│   ├── templates/
│   │   ├── jinja_renderer.py              # Jinjaテンプレート
│   │   └── template_registry.py           # テンプレート管理
│   └── persistence/
│       ├── json_state_repository.py       # JSON状態永続化
│       └── sqlite_cache_repository.py     # SQLiteキャッシュ永続化
```

### Application（アプリケーションロジック）
```
src/session_management/
├── application/
│   ├── use_cases/
│   │   ├── perform_session_check.py       # セッション確認実行
│   │   ├── generate_response_template.py  # 応答テンプレート生成
│   │   └── invalidate_cache_on_change.py  # 変更時キャッシュ無効化
│   ├── dto/
│   │   ├── check_request.py               # 確認リクエスト
│   │   └── check_response.py              # 確認レスポンス
│   └── events/
│       ├── file_changed_event.py          # ファイル変更イベント
│       └── state_updated_event.py         # 状態更新イベント
```

## 🔄 イベント駆動アーキテクチャ

### Event Flow
```python
# ✅ イベント駆動による状態同期
class EventDrivenSessionManagement:
    def handle_file_change(self, file_path: str):
        """ファイル変更時の処理"""
        event = FileChangedEvent(
            file_path=file_path,
            timestamp=datetime.now(),
            affected_checks=self.dependency_tracker.get_affected_checks(file_path)
        )
        
        # 関連キャッシュ無効化
        self.cache_invalidator.invalidate_by_dependency(event.affected_checks)
        
        # イベント発行
        self.event_publisher.publish(event)
    
    def handle_command_execution(self, command: str):
        """コマンド実行時の処理"""
        if command == "make declare-president":
            event = StateUpdatedEvent(
                component="president_status",
                new_state="active",
                timestamp=datetime.now()
            )
            
            # 即座キャッシュ無効化
            self.cache_invalidator.invalidate("president_status")
            self.event_publisher.publish(event)
```

### Dependency Tracking
```python
class DependencyTracker:
    """コンポーネント間依存関係追跡"""
    
    dependencies = {
        "president_status": [
            "runtime/secure_state/president_session.json",
            "scripts/tools/unified-president-tool.py"
        ],
        "cursor_rules": [
            "src/cursor-rules/globals.mdc",
            ".cursor/rules/"
        ],
        "system_status": [
            "scripts/hooks/system_status_display.py",
            "runtime/thinking_violations.json"
        ]
    }
    
    def get_affected_checks(self, file_path: str) -> List[str]:
        """ファイル変更時に影響を受ける確認項目を返す"""
        affected = []
        for check_name, files in self.dependencies.items():
            if any(file_path.endswith(dep_file) for dep_file in files):
                affected.append(check_name)
        return affected
```

## 💾 新キャッシュシステム設計

### State-Aware Cache
```python
class StateAwareCacheKey:
    """状態を考慮したキャッシュキー"""
    
    def __init__(self, check_name: str, state_manager: SystemStateManager):
        self.check_name = check_name
        self.state_hash = state_manager.get_state_hash(check_name)
        self.dependencies_hash = state_manager.get_dependencies_hash(check_name)
        self.version = "1.0.0"
    
    def __str__(self) -> str:
        return f"{self.check_name}:{self.state_hash}:{self.dependencies_hash}:{self.version}"

class EventDrivenCache:
    """イベント駆動キャッシュシステム"""
    
    def get(self, key: CacheKey, validator: Callable = None) -> CacheResult:
        """キャッシュ取得（検証付き）"""
        entry = self.storage.get(str(key))
        
        if not entry:
            return CacheResult.miss()
        
        # TTL確認
        if self.is_expired(entry):
            self.storage.delete(str(key))
            return CacheResult.expired()
        
        # データ整合性確認
        if validator and not validator(entry.data):
            self.storage.delete(str(key))
            return CacheResult.invalid()
        
        return CacheResult.hit(entry.data)
    
    def invalidate_by_dependency(self, affected_checks: List[str]):
        """依存関係による無効化"""
        for check_name in affected_checks:
            pattern = f"{check_name}:*"
            keys = self.storage.keys_matching(pattern)
            for key in keys:
                self.storage.delete(key)
                self.logger.info(f"Cache invalidated: {key}")
```

## 🚨 包括的エラーハンドリング

### Error Classification
```python
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any

class ErrorSeverity(Enum):
    INFO = "info"           # 情報レベル
    WARNING = "warning"     # 警告レベル
    ERROR = "error"         # エラーレベル
    CRITICAL = "critical"   # 重大エラー

class ErrorCategory(Enum):
    FILE_ACCESS = "file_access"         # ファイルアクセスエラー
    PERMISSION = "permission"           # 権限エラー
    CONFIGURATION = "configuration"     # 設定エラー
    NETWORK = "network"                # ネットワークエラー
    DEPENDENCY = "dependency"          # 依存関係エラー
    VALIDATION = "validation"          # バリデーションエラー

@dataclass
class ErrorDetail:
    severity: ErrorSeverity
    category: ErrorCategory
    message: str
    technical_details: Optional[str] = None
    user_action: Optional[str] = None
    auto_recoverable: bool = False
    retry_strategy: Optional[Dict[str, Any]] = None

class StructuredErrorHandler:
    """構造化エラーハンドリング"""
    
    def handle_error(self, exception: Exception, context: str) -> ErrorDetail:
        """例外を構造化エラーに変換"""
        
        if isinstance(exception, FileNotFoundError):
            return ErrorDetail(
                severity=ErrorSeverity.ERROR,
                category=ErrorCategory.FILE_ACCESS,
                message=f"Required file not found: {exception.filename}",
                technical_details=str(exception),
                user_action=f"Please run 'make declare-president' to generate required files",
                auto_recoverable=True,
                retry_strategy={"max_retries": 3, "backoff": "exponential"}
            )
        
        elif isinstance(exception, PermissionError):
            return ErrorDetail(
                severity=ErrorSeverity.CRITICAL,
                category=ErrorCategory.PERMISSION,
                message="Insufficient permissions",
                technical_details=str(exception),
                user_action="Check file permissions and user access rights",
                auto_recoverable=False
            )
        
        elif isinstance(exception, json.JSONDecodeError):
            return ErrorDetail(
                severity=ErrorSeverity.ERROR,
                category=ErrorCategory.VALIDATION,
                message="Invalid JSON format in configuration file",
                technical_details=f"Line {exception.lineno}, Column {exception.colno}: {exception.msg}",
                user_action="Validate and fix JSON syntax",
                auto_recoverable=True,
                retry_strategy={"max_retries": 1, "backoff": "immediate"}
            )
        
        # 未知のエラー
        return ErrorDetail(
            severity=ErrorSeverity.CRITICAL,
            category=ErrorCategory.DEPENDENCY,
            message="Unexpected system error",
            technical_details=str(exception),
            user_action="Contact system administrator",
            auto_recoverable=False
        )
```

### Auto-Recovery System
```python
class AutoRecoverySystem:
    """自動回復システム"""
    
    def attempt_recovery(self, error: ErrorDetail, context: str) -> bool:
        """自動回復試行"""
        
        if not error.auto_recoverable:
            return False
        
        if error.category == ErrorCategory.FILE_ACCESS:
            return self.recover_missing_files(error)
        
        elif error.category == ErrorCategory.VALIDATION:
            return self.recover_validation_error(error)
        
        return False
    
    def recover_missing_files(self, error: ErrorDetail) -> bool:
        """ファイル不足の自動回復"""
        try:
            # PRESIDENT宣言実行で必要ファイル生成
            result = subprocess.run(
                ["make", "declare-president"],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            return False
    
    def recover_validation_error(self, error: ErrorDetail) -> bool:
        """バリデーションエラーの自動回復"""
        # バックアップから復元など
        return False
```

## 📊 監視・メトリクス設計

### Metrics Collection
```python
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional

@dataclass
class CheckMetrics:
    check_name: str
    level: str
    start_time: datetime
    end_time: datetime
    duration_ms: int
    cache_hit: bool
    cache_source: Optional[str]
    error_count: int
    error_details: Optional[Dict]
    dependencies_checked: List[str]
    
class MetricsCollector:
    """メトリクス収集システム"""
    
    def record_check_execution(self, metrics: CheckMetrics):
        """確認実行のメトリクス記録"""
        
        # 実行時間記録
        self.prometheus.histogram('session_check_duration_ms').observe(
            metrics.duration_ms,
            labels={'check_name': metrics.check_name, 'level': metrics.level}
        )
        
        # キャッシュヒット率記録
        self.prometheus.counter('session_check_cache_hits').inc(
            labels={'check_name': metrics.check_name, 'hit': str(metrics.cache_hit)}
        )
        
        # エラー発生率記録
        if metrics.error_count > 0:
            self.prometheus.counter('session_check_errors').inc(
                labels={'check_name': metrics.check_name}
            )
    
    def record_cache_performance(self, cache_metrics: CacheMetrics):
        """キャッシュパフォーマンス記録"""
        pass
    
    def record_state_synchronization(self, sync_metrics: StateSyncMetrics):
        """状態同期パフォーマンス記録"""
        pass
```

## 🧪 テスト戦略

### Test Pyramid
```python
# Unit Tests（高速・大量）
class TestPresidentStatusChecker:
    def test_active_status_detection(self):
        """PRESIDENT宣言済み状態の正確検出"""
    
    def test_inactive_status_detection(self):
        """PRESIDENT未宣言状態の正確検出"""
    
    def test_corrupted_file_handling(self):
        """破損ファイルの適切処理"""

# Integration Tests（中速・中量）
class TestSessionCheckOrchestration:
    def test_end_to_end_check_flow(self):
        """エンドツーエンドの確認フロー"""
    
    def test_cache_invalidation_on_file_change(self):
        """ファイル変更時のキャッシュ無効化"""
    
    def test_error_recovery_workflow(self):
        """エラー回復ワークフロー"""

# E2E Tests（低速・少量）  
class TestCompleteSystem:
    def test_claude_md_integration(self):
        """CLAUDE.md統合テスト"""
    
    def test_makefile_integration(self):
        """Makefile統合テスト"""
    
    def test_mcp_collaboration(self):
        """MCP協業統合テスト"""
```

## 🔧 設定外部化

### Configuration Schema
```python
from pydantic import BaseModel, Field
from typing import Dict, List

class CacheConfig(BaseModel):
    enabled: bool = True
    default_ttl_minutes: int = 30
    max_entries: int = 1000
    cleanup_interval_minutes: int = 10

class CheckConfig(BaseModel):
    name: str
    enabled: bool = True
    timeout_seconds: int = 10
    retry_count: int = 3
    dependencies: List[str] = []

class SessionManagementConfig(BaseModel):
    cache: CacheConfig = CacheConfig()
    checks: Dict[str, CheckConfig] = Field(default_factory=dict)
    log_level: str = "INFO"
    metrics_enabled: bool = True
    auto_recovery_enabled: bool = True
    
    class Config:
        schema_extra = {
            "example": {
                "cache": {
                    "enabled": True,
                    "default_ttl_minutes": 30
                },
                "checks": {
                    "president_status": {
                        "enabled": True,
                        "timeout_seconds": 5,
                        "dependencies": ["runtime/secure_state/president_session.json"]
                    }
                }
            }
        }
```

## 🎯 実装優先順位

### Phase 1: Core Foundation
1. **Domain Entities** - CheckResult, SessionState, SystemStatus
2. **Basic Services** - SessionCheckService, StateManager  
3. **Simple Repository** - JsonStateRepository
4. **Basic Error Handling** - StructuredErrorHandler

### Phase 2: Advanced Features  
1. **Event-Driven Cache** - EventDrivenCache, FileWatcher
2. **Dependency Tracking** - DependencyTracker, CacheInvalidator
3. **Template System** - JinjaRenderer, TemplateRegistry
4. **Metrics Collection** - MetricsCollector

### Phase 3: Quality & Integration
1. **Comprehensive Tests** - Unit, Integration, E2E
2. **Auto-Recovery** - AutoRecoverySystem
3. **CLAUDE.md Integration** - New template system
4. **MCP Collaboration** - External validation integration

---

**次のアクション**: Phase 1 Core Foundation実装開始