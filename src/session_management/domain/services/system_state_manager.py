"""
SystemStateManager Implementation
状態同期・管理システムの実装
O3・Gemini分析で特定された「状態同期の完全欠如」を解決
"""

import fnmatch
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol

from ...infrastructure.cache.event_driven_cache import StateAwareCacheKey
from ..entities.check_result import CheckResult
from ..entities.session_state import ComponentState, SessionState


class StateChangeType(Enum):
    """状態変更タイプ"""

    COMPONENT_UPDATED = "COMPONENT_UPDATED"
    CHECK_RESULT_ADDED = "CHECK_RESULT_ADDED"
    FILE_CHANGED = "FILE_CHANGED"
    COMMAND_EXECUTED = "COMMAND_EXECUTED"
    SESSION_INITIALIZED = "SESSION_INITIALIZED"


@dataclass
class StateChangeEvent:
    """状態変更イベント"""

    change_type: StateChangeType
    timestamp: datetime
    session_id: Optional[str] = None
    component_name: Optional[str] = None
    check_name: Optional[str] = None
    file_path: Optional[str] = None
    command: Optional[str] = None
    new_status: Optional[str] = None
    affected_checks: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

    @classmethod
    def component_updated(
        cls,
        component_name: str,
        new_status: str,
        session_id: Optional[str] = None,
        timestamp: Optional[datetime] = None,
    ) -> "StateChangeEvent":
        """コンポーネント更新イベント作成"""
        return cls(
            change_type=StateChangeType.COMPONENT_UPDATED,
            timestamp=timestamp or datetime.now(),
            session_id=session_id,
            component_name=component_name,
            new_status=new_status,
        )

    @classmethod
    def check_result_added(
        cls,
        check_name: str,
        session_id: Optional[str] = None,
        timestamp: Optional[datetime] = None,
    ) -> "StateChangeEvent":
        """確認結果追加イベント作成"""
        return cls(
            change_type=StateChangeType.CHECK_RESULT_ADDED,
            timestamp=timestamp or datetime.now(),
            session_id=session_id,
            check_name=check_name,
        )

    @classmethod
    def file_changed(
        cls,
        file_path: str,
        affected_checks: List[str],
        timestamp: Optional[datetime] = None,
    ) -> "StateChangeEvent":
        """ファイル変更イベント作成"""
        return cls(
            change_type=StateChangeType.FILE_CHANGED,
            timestamp=timestamp or datetime.now(),
            file_path=file_path,
            affected_checks=affected_checks,
        )

    @classmethod
    def command_executed(
        cls,
        command: str,
        affected_checks: List[str],
        timestamp: Optional[datetime] = None,
    ) -> "StateChangeEvent":
        """コマンド実行イベント作成"""
        return cls(
            change_type=StateChangeType.COMMAND_EXECUTED,
            timestamp=timestamp or datetime.now(),
            command=command,
            affected_checks=affected_checks,
        )

    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            "change_type": self.change_type.value,
            "timestamp": self.timestamp.isoformat(),
            "session_id": self.session_id,
            "component_name": self.component_name,
            "check_name": self.check_name,
            "file_path": self.file_path,
            "command": self.command,
            "new_status": self.new_status,
            "affected_checks": self.affected_checks,
            "metadata": self.metadata or {},
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StateChangeEvent":
        """辞書から復元"""
        return cls(
            change_type=StateChangeType(data["change_type"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            session_id=data.get("session_id"),
            component_name=data.get("component_name"),
            check_name=data.get("check_name"),
            file_path=data.get("file_path"),
            command=data.get("command"),
            new_status=data.get("new_status"),
            affected_checks=data.get("affected_checks"),
            metadata=data.get("metadata"),
        )


class EventPublisher(Protocol):
    """イベント発行者プロトコル"""

    def publish(self, event: StateChangeEvent) -> None:
        """イベント発行"""
        ...


class CacheManager(Protocol):
    """キャッシュ管理者プロトコル"""

    def invalidate_by_dependency(self, affected_checks: List[str]) -> int:
        """依存関係による無効化"""
        ...

    def invalidate_by_pattern(self, pattern: str) -> int:
        """パターン指定無効化"""
        ...


class DependencyTracker:
    """依存関係追跡システム"""

    def __init__(self):
        # 各確認項目の依存ファイル
        self.file_dependencies = {
            "president_status": [
                "runtime/secure_state/president_session.json",
                "scripts/tools/unified-president-tool.py",
                "Makefile",
            ],
            "cursor_rules": ["src/cursor-rules/globals.mdc", ".cursor/rules/*"],
            "system_status": [
                "scripts/hooks/system_status_display.py",
                "runtime/thinking_violations.json",
                "runtime/memory/session_logs.json",
            ],
        }

        # 各確認項目の依存コマンド
        self.command_dependencies = {
            "president_status": [
                "make declare-president",
                "python3 scripts/tools/unified-president-tool.py",
            ],
            "system_status": ["python3 scripts/hooks/system_status_display.py"],
            "cursor_rules": [
                # Cursor Rulesは通常コマンドでは変更されない
            ],
        }

    def get_affected_checks(self, file_path: str) -> List[str]:
        """ファイル変更時に影響を受ける確認項目を返す"""
        affected = []

        for check_name, files in self.file_dependencies.items():
            for dep_file in files:
                # ワイルドカードマッチング対応
                if fnmatch.fnmatch(file_path, dep_file) or file_path.endswith(dep_file):
                    affected.append(check_name)
                    break

        return affected

    def get_affected_checks_by_command(self, command: str) -> List[str]:
        """コマンド実行時に影響を受ける確認項目を返す"""
        affected = []

        for check_name, commands in self.command_dependencies.items():
            for dep_command in commands:
                if command.startswith(dep_command) or dep_command in command:
                    affected.append(check_name)
                    break

        return affected

    def register_dependency(
        self,
        check_name: str,
        file_dependencies: Optional[List[str]] = None,
        command_dependencies: Optional[List[str]] = None,
    ) -> None:
        """新しい依存関係を登録"""
        if file_dependencies:
            self.file_dependencies[check_name] = file_dependencies

        if command_dependencies:
            self.command_dependencies[check_name] = command_dependencies

    def get_all_dependencies(self, check_name: str) -> Dict[str, List[str]]:
        """指定確認項目の全依存関係を取得"""
        return {
            "files": self.file_dependencies.get(check_name, []),
            "commands": self.command_dependencies.get(check_name, []),
        }


class StateHashCalculator:
    """状態ハッシュ計算システム"""

    def __init__(self, dependency_tracker: Optional[DependencyTracker] = None):
        self.dependency_tracker = dependency_tracker or DependencyTracker()

    def calculate_state_hash(self, check_name: str) -> str:
        """指定確認項目の状態ハッシュを計算"""
        dependencies = self.dependency_tracker.get_all_dependencies(check_name)

        # ファイル依存関係のハッシュ
        file_hashes = []
        for file_path in dependencies["files"]:
            file_hash = self.calculate_file_hash(file_path)
            file_hashes.append(f"{file_path}:{file_hash}")

        # コマンド依存関係のハッシュ（コマンド文字列そのもの）
        command_hashes = []
        for command in dependencies["commands"]:
            command_hash = hashlib.md5(command.encode("utf-8")).hexdigest()[:8]
            command_hashes.append(f"{command}:{command_hash}")

        # 統合ハッシュ計算
        combined_data = {
            "check_name": check_name,
            "files": sorted(file_hashes),
            "commands": sorted(command_hashes),
            "timestamp": datetime.now().strftime("%Y%m%d"),  # 日付レベルでの変更検出
        }

        json_str = json.dumps(combined_data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(json_str.encode("utf-8")).hexdigest()[:16]

    def calculate_dependencies_hash(self, check_name: str) -> str:
        """依存関係構造のハッシュを計算"""
        dependencies = self.dependency_tracker.get_all_dependencies(check_name)

        # 依存関係の構造のみのハッシュ（ファイル内容は含まない）
        structure_data = {
            "check_name": check_name,
            "file_dependencies": sorted(dependencies["files"]),
            "command_dependencies": sorted(dependencies["commands"]),
        }

        json_str = json.dumps(structure_data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(json_str.encode("utf-8")).hexdigest()[:16]

    def calculate_file_hash(self, file_path: str) -> str:
        """ファイルのハッシュを計算"""
        try:
            path = Path(file_path)

            if not path.exists():
                return "file_not_found"

            # ファイル情報の取得
            stat = path.stat()
            file_info = {"mtime": stat.st_mtime, "size": stat.st_size}

            # 小さなファイルは内容も含める
            if stat.st_size < 10240:  # 10KB未満
                try:
                    content = path.read_text(encoding="utf-8")
                    file_info["content_preview"] = content[:500]  # 最初の500文字
                except (UnicodeDecodeError, PermissionError):
                    # バイナリファイルや権限エラーの場合はスキップ
                    pass

            json_str = json.dumps(file_info, sort_keys=True, ensure_ascii=False)
            return hashlib.md5(json_str.encode("utf-8")).hexdigest()[:12]

        except (OSError, PermissionError) as e:
            return f"error_{hashlib.md5(str(e).encode()).hexdigest()[:8]}"


class SystemStateManager:
    """システム状態管理システム"""

    def __init__(
        self,
        event_publisher: Optional[EventPublisher] = None,
        cache_manager: Optional[CacheManager] = None,
        dependency_tracker: Optional[DependencyTracker] = None,
        state_hash_calculator: Optional[StateHashCalculator] = None,
    ):
        self.event_publisher = event_publisher
        self.cache_manager = cache_manager
        self.dependency_tracker = dependency_tracker or DependencyTracker()
        self.state_hash_calculator = state_hash_calculator or StateHashCalculator(
            self.dependency_tracker
        )

        # デフォルトバージョン
        self.default_version = "1.0.0"

    def initialize_session_state(self, session_id: str) -> SessionState:
        """セッション状態初期化"""
        session_state = SessionState.create_with_id(session_id)

        if self.event_publisher:
            event = StateChangeEvent(
                change_type=StateChangeType.SESSION_INITIALIZED,
                timestamp=datetime.now(),
                session_id=session_id,
            )
            self.event_publisher.publish(event)

        return session_state

    def update_component_state(
        self, session_state: SessionState, component_state: ComponentState
    ) -> SessionState:
        """コンポーネント状態更新"""
        updated_state = session_state.add_component_state(component_state)

        # 依存関係による影響チェック
        affected_checks = self.dependency_tracker.get_affected_checks(
            f"component:{component_state.component_name}"
        )

        # キャッシュ無効化
        if self.cache_manager and affected_checks:
            self.cache_manager.invalidate_by_dependency(affected_checks)

        # イベント発行
        if self.event_publisher:
            event = StateChangeEvent.component_updated(
                component_name=component_state.component_name,
                new_status=component_state.status,
                session_id=session_state.session_id,
            )
            self.event_publisher.publish(event)

        return updated_state

    def add_check_result(
        self, session_state: SessionState, check_result: CheckResult
    ) -> SessionState:
        """確認結果追加"""
        updated_state = session_state.add_check_result(check_result)

        # イベント発行
        if self.event_publisher:
            event = StateChangeEvent.check_result_added(
                check_name=check_result.check_name, session_id=session_state.session_id
            )
            self.event_publisher.publish(event)

        return updated_state

    def handle_file_change(self, file_path: str) -> None:
        """ファイル変更処理"""
        affected_checks = self.dependency_tracker.get_affected_checks(file_path)

        if not affected_checks:
            return

        # キャッシュ無効化
        if self.cache_manager:
            self.cache_manager.invalidate_by_dependency(affected_checks)

        # イベント発行
        if self.event_publisher:
            event = StateChangeEvent.file_changed(
                file_path=file_path, affected_checks=affected_checks
            )
            self.event_publisher.publish(event)

    def handle_command_execution(self, command: str) -> None:
        """コマンド実行処理"""
        affected_checks = self.dependency_tracker.get_affected_checks_by_command(
            command
        )

        if not affected_checks:
            return

        # キャッシュ無効化
        if self.cache_manager:
            self.cache_manager.invalidate_by_dependency(affected_checks)

        # イベント発行
        if self.event_publisher:
            event = StateChangeEvent.command_executed(
                command=command, affected_checks=affected_checks
            )
            self.event_publisher.publish(event)

    def generate_cache_key(self, check_name: str) -> StateAwareCacheKey:
        """キャッシュキー生成"""
        state_hash = self.state_hash_calculator.calculate_state_hash(check_name)
        dependencies_hash = self.state_hash_calculator.calculate_dependencies_hash(
            check_name
        )

        return StateAwareCacheKey(
            check_name=check_name,
            state_hash=state_hash,
            dependencies_hash=dependencies_hash,
            version=self.default_version,
        )

    def get_state_hash(self, check_name: str) -> str:
        """状態ハッシュ取得"""
        return self.state_hash_calculator.calculate_state_hash(check_name)

    def get_dependencies_hash(self, check_name: str) -> str:
        """依存関係ハッシュ取得"""
        return self.state_hash_calculator.calculate_dependencies_hash(check_name)

    def get_system_overview(self, session_state: SessionState) -> Dict[str, Any]:
        """システム概要取得"""
        return {
            "session_id": session_state.session_id,
            "version": session_state.version.value,
            "created_at": session_state.created_at.isoformat(),
            "last_updated": session_state.updated_at.isoformat(),
            "component_count": len(session_state.component_states),
            "check_count": len(session_state.check_history),
            "violation_count": session_state.get_violation_count(),
            "has_violations": session_state.has_violations(),
            "state_hash": session_state.calculate_state_hash(),
        }

    def validate_state_integrity(self, session_state: SessionState) -> Dict[str, Any]:
        """状態整合性検証"""
        validation_results = {"is_valid": True, "issues": [], "warnings": []}

        # バージョン整合性チェック
        if session_state.version.value < 1:
            validation_results["is_valid"] = False
            validation_results["issues"].append("Invalid version number")

        # コンポーネント状態整合性チェック
        for name, component in session_state.component_states.items():
            if component.component_name != name:
                validation_results["is_valid"] = False
                validation_results["issues"].append(
                    f"Component name mismatch: {name} vs {component.component_name}"
                )

        # 確認結果の整合性チェック
        recent_failures = [
            result
            for result in session_state.check_history[-10:]  # 最新10件
            if result.is_failure()
        ]

        if len(recent_failures) > 5:
            validation_results["warnings"].append("High failure rate in recent checks")

        return validation_results
