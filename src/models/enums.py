#!/usr/bin/env python3
"""
🎯 System Enums - システム列挙型定義
====================================

偽装データ防止のための厳格な列挙型システム
o3・Geminiフィードバック反映実装
"""

from enum import Enum, IntEnum
from typing import Any, Dict, List


class TaskStatus(str, Enum):
    """タスクステータス - 偽装データ防止"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"
    REVIEW = "review"
    APPROVED = "approved"
    DEPLOYED = "deployed"


class WorkerStatus(str, Enum):
    """ワーカーステータス"""

    ACTIVE = "active"
    IDLE = "idle"
    PROCESSING = "processing"
    ERROR = "error"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    INITIALIZING = "initializing"
    SHUTTING_DOWN = "shutting_down"


class PriorityLevel(str, Enum):
    """優先度レベル"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"


class AlertSeverity(str, Enum):
    """アラート重要度"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class SystemComponent(str, Enum):
    """システムコンポーネント"""

    DASHBOARD = "dashboard"
    WORKER = "worker"
    COORDINATOR = "coordinator"
    MEMORY = "memory"
    MONITOR = "monitor"
    DATABASE = "database"
    API = "api"
    UI = "ui"


class RoleType(str, Enum):
    """役職タイプ（動的システム）"""

    PRESIDENT = "president"
    COORDINATOR = "coordinator"
    ANALYST = "analyst"
    ENGINEER = "engineer"
    SPECIALIST = "specialist"
    MANAGER = "manager"
    ARCHITECT = "architect"
    DEVELOPER = "developer"
    TESTER = "tester"
    OPERATOR = "operator"


class AuthorityLevel(IntEnum):
    """権限レベル"""

    MINIMAL = 1
    BASIC = 2
    STANDARD = 3
    ELEVATED = 4
    ADVANCED = 5
    SENIOR = 6
    LEAD = 7
    MANAGER = 8
    EXECUTIVE = 9
    PRESIDENT = 10


class EnvironmentType(str, Enum):
    """環境タイプ"""

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
    LOCAL = "local"
    VIRTUAL = "virtual"


class DatabaseState(str, Enum):
    """データベース状態"""

    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    INITIALIZING = "initializing"
    ERROR = "error"
    MIGRATING = "migrating"
    BACKUP = "backup"
    MAINTENANCE = "maintenance"


class APIStatus(str, Enum):
    """API状態"""

    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    RATE_LIMITED = "rate_limited"
    AUTHENTICATION_FAILED = "authentication_failed"
    TIMEOUT = "timeout"
    ERROR = "error"


class FileType(str, Enum):
    """ファイルタイプ"""

    PYTHON = "python"
    MARKDOWN = "markdown"
    JSON = "json"
    YAML = "yaml"
    CONFIG = "config"
    LOG = "log"
    SCRIPT = "script"
    DOCUMENT = "document"
    DATA = "data"
    TEMPORARY = "temporary"


class ValidationResult(str, Enum):
    """検証結果"""

    VALID = "valid"
    INVALID = "invalid"
    WARNING = "warning"
    ERROR = "error"
    PENDING = "pending"
    UNKNOWN = "unknown"


class OperationMode(str, Enum):
    """動作モード"""

    NORMAL = "normal"
    DEBUG = "debug"
    MAINTENANCE = "maintenance"
    EMERGENCY = "emergency"
    SAFE = "safe"
    DEVELOPMENT = "development"


class UIMode(str, Enum):
    """UIモード"""

    DASHBOARD = "dashboard"
    COMMAND = "command"
    WORKER = "worker"
    METRICS = "metrics"
    ADMIN = "admin"
    MONITOR = "monitor"


class ExecutionPhase(str, Enum):
    """実行フェーズ"""

    INITIALIZATION = "initialization"
    PLANNING = "planning"
    EXECUTION = "execution"
    MONITORING = "monitoring"
    COMPLETION = "completion"
    CLEANUP = "cleanup"
    EVALUATION = "evaluation"


class Quality(str, Enum):
    """品質レベル"""

    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    CRITICAL = "critical"


class Language(str, Enum):
    """言語設定"""

    JAPANESE = "japanese"
    ENGLISH = "english"
    MIXED = "mixed"


class ResponseType(str, Enum):
    """レスポンスタイプ"""

    DECLARATION = "declaration"  # 宣言（日本語）
    PROCESSING = "processing"  # 処理（英語）
    REPORTING = "reporting"  # 報告（日本語）
    THINKING = "thinking"  # 思考（必須）


# 偽装データ検出用パターン
BANNED_FAKE_PATTERNS = [
    "待機中",
    "処理中",
    "完了",
    "エラー",
    "テスト",
    "サンプル",
    "ダミー",
    "仮データ",
    "適当",
    "とりあえず",
    "temp",
    "dummy",
    "fake",
    "mock",
    "test",
    "sample",
    "placeholder",
    "lorem",
    "ipsum",
    "example",
    "demo",
    "random",
    "TBD",
    "TODO",
]


def validate_enum_value(value: Any, enum_class: Enum) -> bool:
    """列挙型値の検証"""
    try:
        return value in [item.value for item in enum_class]
    except Exception:
        return False


def get_enum_values(enum_class: Enum) -> List[str]:
    """列挙型の全値を取得"""
    return [item.value for item in enum_class]


def is_fake_data(value: str) -> bool:
    """偽装データかどうかを判定"""
    if not isinstance(value, str):
        return False

    value_lower = value.lower()
    for pattern in BANNED_FAKE_PATTERNS:
        if pattern.lower() in value_lower:
            return True

    return False


def enforce_enum_integrity(
    data: Dict[str, Any], field_definitions: Dict[str, Enum]
) -> Dict[str, Any]:
    """列挙型整合性を強制"""
    validated_data = {}

    for field_name, expected_enum in field_definitions.items():
        if field_name in data:
            value = data[field_name]
            if validate_enum_value(value, expected_enum):
                validated_data[field_name] = value
            else:
                raise ValueError(f"Invalid enum value for {field_name}: {value}")
        else:
            # デフォルト値を設定
            if expected_enum == TaskStatus:
                validated_data[field_name] = TaskStatus.PENDING.value
            elif expected_enum == WorkerStatus:
                validated_data[field_name] = WorkerStatus.IDLE.value
            elif expected_enum == PriorityLevel:
                validated_data[field_name] = PriorityLevel.MEDIUM.value

    return validated_data


# エクスポート用辞書
ENUM_REGISTRY = {
    "TaskStatus": TaskStatus,
    "WorkerStatus": WorkerStatus,
    "PriorityLevel": PriorityLevel,
    "AlertSeverity": AlertSeverity,
    "SystemComponent": SystemComponent,
    "RoleType": RoleType,
    "AuthorityLevel": AuthorityLevel,
    "EnvironmentType": EnvironmentType,
    "DatabaseState": DatabaseState,
    "APIStatus": APIStatus,
    "FileType": FileType,
    "ValidationResult": ValidationResult,
    "OperationMode": OperationMode,
    "UIMode": UIMode,
    "ExecutionPhase": ExecutionPhase,
    "Quality": Quality,
    "Language": Language,
    "ResponseType": ResponseType,
}

if __name__ == "__main__":
    print("🎯 System Enums - Validation Test")
    print("=" * 40)

    # 偽装データテスト
    test_values = ["pending", "待機中", "processing", "処理中", "dummy", "test"]

    for value in test_values:
        is_fake = is_fake_data(value)
        is_valid_task = validate_enum_value(value, TaskStatus)
        print(f"'{value}': fake={is_fake}, valid_task={is_valid_task}")

    # 列挙型整合性テスト
    test_data = {"status": "pending", "priority": "high", "worker_state": "active"}

    field_defs = {
        "status": TaskStatus,
        "priority": PriorityLevel,
        "worker_state": WorkerStatus,
    }

    validated = enforce_enum_integrity(test_data, field_defs)
    print(f"\nValidated data: {validated}")

    print("\n✅ Enum validation system operational")
