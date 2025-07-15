"""
SessionState Entity
セッション状態を管理するドメインエンティティ
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
import hashlib
import json
import uuid

from .check_result import CheckResult


@dataclass(frozen=True)
class StateVersion:
    """状態バージョン"""
    value: int
    
    def increment(self) -> 'StateVersion':
        """バージョン増分"""
        return StateVersion(self.value + 1)
    
    def __lt__(self, other: 'StateVersion') -> bool:
        return self.value < other.value
    
    def __gt__(self, other: 'StateVersion') -> bool:
        return self.value > other.value
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, StateVersion):
            return False
        return self.value == other.value


@dataclass(frozen=True)
class ComponentState:
    """コンポーネント状態"""
    component_name: str
    status: str
    last_checked: datetime
    state_hash: Optional[str] = None
    dependencies_hash: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            "component_name": self.component_name,
            "status": self.status,
            "last_checked": self.last_checked.isoformat(),
            "state_hash": self.state_hash,
            "dependencies_hash": self.dependencies_hash,
            "metadata": self.metadata or {}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ComponentState':
        """辞書から復元"""
        return cls(
            component_name=data["component_name"],
            status=data["status"],
            last_checked=datetime.fromisoformat(data["last_checked"]),
            state_hash=data.get("state_hash"),
            dependencies_hash=data.get("dependencies_hash"),
            metadata=data.get("metadata") or {}
        )


@dataclass(frozen=True)
class SessionState:
    """セッション状態エンティティ"""
    session_id: str
    created_at: datetime
    updated_at: datetime
    version: StateVersion
    component_states: Dict[str, ComponentState] = field(default_factory=dict)
    check_history: List[CheckResult] = field(default_factory=list)
    
    @classmethod
    def create_empty(cls) -> 'SessionState':
        """空のセッション状態作成"""
        now = datetime.now()
        session_id = str(uuid.uuid4())
        
        return cls(
            session_id=session_id,
            created_at=now,
            updated_at=now,
            version=StateVersion(1),
            component_states={},
            check_history=[]
        )
    
    @classmethod
    def create_with_id(cls, session_id: str) -> 'SessionState':
        """指定IDでセッション状態作成"""
        now = datetime.now()
        
        return cls(
            session_id=session_id,
            created_at=now,
            updated_at=now,
            version=StateVersion(1),
            component_states={},
            check_history=[]
        )
    
    def add_component_state(self, component_state: ComponentState) -> 'SessionState':
        """コンポーネント状態追加"""
        new_components = self.component_states.copy()
        new_components[component_state.component_name] = component_state
        
        return SessionState(
            session_id=self.session_id,
            created_at=self.created_at,
            updated_at=datetime.now(),
            version=self.version.increment(),
            component_states=new_components,
            check_history=self.check_history
        )
    
    def update_component_state(self, component_name: str, new_state: ComponentState) -> 'SessionState':
        """コンポーネント状態更新"""
        if component_name not in self.component_states:
            raise ValueError(f"Component {component_name} not found")
        
        new_components = self.component_states.copy()
        new_components[component_name] = new_state
        
        return SessionState(
            session_id=self.session_id,
            created_at=self.created_at,
            updated_at=datetime.now(),
            version=self.version.increment(),
            component_states=new_components,
            check_history=self.check_history
        )
    
    def add_check_result(self, check_result: CheckResult) -> 'SessionState':
        """確認結果追加"""
        new_history = self.check_history.copy()
        new_history.append(check_result)
        
        return SessionState(
            session_id=self.session_id,
            created_at=self.created_at,
            updated_at=datetime.now(),
            version=self.version.increment(),
            component_states=self.component_states,
            check_history=new_history
        )
    
    def get_component_state(self, component_name: str) -> Optional[ComponentState]:
        """コンポーネント状態取得"""
        return self.component_states.get(component_name)
    
    def get_latest_check_result(self, check_name: str) -> Optional[CheckResult]:
        """指定名の最新確認結果取得"""
        for result in reversed(self.check_history):
            if result.check_name == check_name:
                return result
        return None
    
    def has_violations(self) -> bool:
        """違反有無判定"""
        return any(result.is_failure() for result in self.check_history)
    
    def get_violation_count(self) -> int:
        """違反数取得"""
        return sum(1 for result in self.check_history if result.is_failure())
    
    def calculate_state_hash(self) -> str:
        """全体状態ハッシュ計算"""
        # コンポーネント状態をソートして一意性保証
        sorted_components = dict(sorted(self.component_states.items()))
        
        hash_data = {
            "version": self.version.value,
            "components": {
                name: {
                    "status": comp.status,
                    "state_hash": comp.state_hash,
                    "dependencies_hash": comp.dependencies_hash
                }
                for name, comp in sorted_components.items()
            }
        }
        
        json_str = json.dumps(hash_data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(json_str.encode('utf-8')).hexdigest()[:16]
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "version": self.version.value,
            "component_states": {
                name: component.to_dict()
                for name, component in self.component_states.items()
            },
            "check_history": [
                result.to_dict() for result in self.check_history
            ]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionState':
        """辞書から復元"""
        component_states = {}
        for name, comp_data in data.get("component_states", {}).items():
            component_states[name] = ComponentState.from_dict(comp_data)
        
        check_history = []
        for result_data in data.get("check_history", []):
            check_history.append(CheckResult.from_dict(result_data))
        
        return cls(
            session_id=data["session_id"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            version=StateVersion(data["version"]),
            component_states=component_states,
            check_history=check_history
        )
    
    def to_json(self) -> str:
        """JSON文字列に変換"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'SessionState':
        """JSON文字列から復元"""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def __str__(self) -> str:
        """文字列表現"""
        component_count = len(self.component_states)
        history_count = len(self.check_history)
        violation_count = self.get_violation_count()
        
        return (f"SessionState[{self.session_id[:8]}...] "
                f"v{self.version.value} "
                f"components:{component_count} "
                f"history:{history_count} "
                f"violations:{violation_count}")