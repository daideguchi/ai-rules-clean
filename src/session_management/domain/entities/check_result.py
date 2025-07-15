"""
CheckResult Entity
セッション確認結果を表現するドメインエンティティ
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, Union
import json


class CheckStatus(Enum):
    """確認ステータス"""
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    WARNING = "WARNING"
    UNKNOWN = "UNKNOWN"


class CheckSeverity(Enum):
    """確認重要度"""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class CheckResult:
    """確認結果エンティティ"""
    
    check_name: str
    status: CheckStatus
    severity: CheckSeverity
    message: str
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None
    error: Optional[Exception] = None
    duration_ms: Optional[int] = None
    
    def __post_init__(self):
        """バリデーション"""
        if not self.check_name.strip():
            raise ValueError("check_name cannot be empty")
        if not self.message.strip():
            raise ValueError("message cannot be empty")
    
    @classmethod
    def success(
        cls,
        check_name: str,
        message: str,
        timestamp: Optional[datetime] = None,
        details: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[int] = None
    ) -> 'CheckResult':
        """成功結果の作成"""
        return cls(
            check_name=check_name,
            status=CheckStatus.SUCCESS,
            severity=CheckSeverity.INFO,
            message=message,
            timestamp=timestamp or datetime.now(),
            details=details or {},
            duration_ms=duration_ms
        )
    
    @classmethod
    def failure(
        cls,
        check_name: str,
        message: str,
        error: Optional[Exception] = None,
        timestamp: Optional[datetime] = None,
        severity: CheckSeverity = CheckSeverity.ERROR,
        details: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[int] = None
    ) -> 'CheckResult':
        """失敗結果の作成"""
        return cls(
            check_name=check_name,
            status=CheckStatus.FAILURE,
            severity=severity,
            message=message,
            timestamp=timestamp or datetime.now(),
            details=details or {},
            error=error,
            duration_ms=duration_ms
        )
    
    @classmethod
    def warning(
        cls,
        check_name: str,
        message: str,
        timestamp: Optional[datetime] = None,
        details: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[int] = None
    ) -> 'CheckResult':
        """警告結果の作成"""
        return cls(
            check_name=check_name,
            status=CheckStatus.WARNING,
            severity=CheckSeverity.WARNING,
            message=message,
            timestamp=timestamp or datetime.now(),
            details=details or {},
            duration_ms=duration_ms
        )
    
    @classmethod
    def unknown(
        cls,
        check_name: str,
        message: str,
        timestamp: Optional[datetime] = None,
        details: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[int] = None
    ) -> 'CheckResult':
        """不明結果の作成"""
        return cls(
            check_name=check_name,
            status=CheckStatus.UNKNOWN,
            severity=CheckSeverity.WARNING,
            message=message,
            timestamp=timestamp or datetime.now(),
            details=details or {},
            duration_ms=duration_ms
        )
    
    def is_success(self) -> bool:
        """成功判定"""
        return self.status == CheckStatus.SUCCESS
    
    def is_failure(self) -> bool:
        """失敗判定"""
        return self.status == CheckStatus.FAILURE
    
    def is_warning(self) -> bool:
        """警告判定"""
        return self.status == CheckStatus.WARNING
    
    def is_unknown(self) -> bool:
        """不明判定"""
        return self.status == CheckStatus.UNKNOWN
    
    def __str__(self) -> str:
        """文字列表現"""
        error_info = f" (Error: {self.error})" if self.error else ""
        duration_info = f" ({self.duration_ms}ms)" if self.duration_ms else ""
        return f"CheckResult[{self.check_name}: {self.status.value} - {self.message}{duration_info}{error_info}]"
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            "check_name": self.check_name,
            "status": self.status.value,
            "severity": self.severity.value,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details,
            "error": str(self.error) if self.error else None,
            "duration_ms": self.duration_ms
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CheckResult':
        """辞書から復元"""
        timestamp = datetime.fromisoformat(data["timestamp"])
        
        # エラーの復元（文字列から）
        error = None
        if data.get("error"):
            error = Exception(data["error"])
        
        return cls(
            check_name=data["check_name"],
            status=CheckStatus(data["status"]),
            severity=CheckSeverity(data["severity"]),
            message=data["message"],
            timestamp=timestamp,
            details=data.get("details") or {},
            error=error,
            duration_ms=data.get("duration_ms")
        )
    
    def generate_cache_key(self) -> str:
        """キャッシュキー生成"""
        state_hash = self.details.get("state_hash", "unknown") if self.details else "unknown"
        dependencies_hash = self.details.get("dependencies_hash", "unknown") if self.details else "unknown"
        
        return f"{self.check_name}:{state_hash}:{dependencies_hash}"
    
    def to_json(self) -> str:
        """JSON文字列に変換"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'CheckResult':
        """JSON文字列から復元"""
        data = json.loads(json_str)
        return cls.from_dict(data)