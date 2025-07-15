#!/usr/bin/env python3
"""
Role-Based Access Control (RBAC) システム
- 階層的役割管理
- 権限ベースのアクセス制御
- 監査ログ機能
"""

import hashlib
import json
import logging
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Permission(Enum):
    """権限定義"""

    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    EXECUTE = "execute"
    ADMIN = "admin"

    # AI特有の権限
    AI_CREATE_MODEL = "ai_create_model"
    AI_TRAIN_MODEL = "ai_train_model"
    AI_DEPLOY_MODEL = "ai_deploy_model"
    AI_ACCESS_MEMORY = "ai_access_memory"
    AI_MODIFY_SYSTEM = "ai_modify_system"

    # President特有の権限
    PRESIDENT_DECLARE = "president_declare"
    PRESIDENT_MODIFY_RULES = "president_modify_rules"
    PRESIDENT_OVERRIDE = "president_override"

    # システム権限
    SYSTEM_CONFIG = "system_config"
    SYSTEM_BACKUP = "system_backup"
    SYSTEM_RESTORE = "system_restore"
    SYSTEM_MONITORING = "system_monitoring"


class Role(Enum):
    """役割定義"""

    GUEST = "guest"
    USER = "user"
    DEVELOPER = "developer"
    AI_WORKER = "ai_worker"
    AI_PRESIDENT = "ai_president"
    SYSTEM_ADMIN = "system_admin"
    SECURITY_ADMIN = "security_admin"


class RBACSystem:
    """RBAC管理システム"""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).resolve().parents[2]
        self.config_dir = self.project_root / "config" / "security"
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # 設定ファイル
        self.rbac_config_file = self.config_dir / "rbac_config.json"
        self.access_log_file = self.config_dir / "rbac_access.log"

        # RBAC設定の読み込み
        self.rbac_config = self._load_rbac_config()

        # デフォルト権限マトリックスの初期化
        self._initialize_default_permissions()

    def _load_rbac_config(self) -> Dict:
        """RBAC設定の読み込み"""
        if self.rbac_config_file.exists():
            try:
                with open(self.rbac_config_file) as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load RBAC config: {e}")
                return {}

        return {
            "version": "1.0.0",
            "role_permissions": {},
            "user_roles": {},
            "role_hierarchy": {},
            "access_policies": {},
            "created_at": datetime.now().isoformat(),
        }

    def _save_rbac_config(self):
        """RBAC設定の保存"""
        with open(self.rbac_config_file, "w") as f:
            json.dump(self.rbac_config, f, indent=2)

        # セキュアな権限設定
        import os

        os.chmod(self.rbac_config_file, 0o600)

    def _initialize_default_permissions(self):
        """デフォルト権限マトリックスの初期化"""
        default_permissions = {
            Role.GUEST.value: [Permission.READ.value],
            Role.USER.value: [Permission.READ.value, Permission.WRITE.value],
            Role.DEVELOPER.value: [
                Permission.READ.value,
                Permission.WRITE.value,
                Permission.DELETE.value,
                Permission.EXECUTE.value,
            ],
            Role.AI_WORKER.value: [
                Permission.READ.value,
                Permission.WRITE.value,
                Permission.EXECUTE.value,
                Permission.AI_CREATE_MODEL.value,
                Permission.AI_TRAIN_MODEL.value,
                Permission.AI_ACCESS_MEMORY.value,
            ],
            Role.AI_PRESIDENT.value: [
                Permission.READ.value,
                Permission.WRITE.value,
                Permission.DELETE.value,
                Permission.EXECUTE.value,
                Permission.AI_CREATE_MODEL.value,
                Permission.AI_TRAIN_MODEL.value,
                Permission.AI_DEPLOY_MODEL.value,
                Permission.AI_ACCESS_MEMORY.value,
                Permission.AI_MODIFY_SYSTEM.value,
                Permission.PRESIDENT_DECLARE.value,
                Permission.PRESIDENT_MODIFY_RULES.value,
                Permission.PRESIDENT_OVERRIDE.value,
            ],
            Role.SYSTEM_ADMIN.value: [
                Permission.READ.value,
                Permission.WRITE.value,
                Permission.DELETE.value,
                Permission.EXECUTE.value,
                Permission.ADMIN.value,
                Permission.SYSTEM_CONFIG.value,
                Permission.SYSTEM_BACKUP.value,
                Permission.SYSTEM_RESTORE.value,
                Permission.SYSTEM_MONITORING.value,
            ],
            Role.SECURITY_ADMIN.value: [
                Permission.READ.value,
                Permission.WRITE.value,
                Permission.DELETE.value,
                Permission.EXECUTE.value,
                Permission.ADMIN.value,
                Permission.SYSTEM_CONFIG.value,
                Permission.SYSTEM_MONITORING.value,
            ],
        }

        # 設定されていない場合のみデフォルト値を設定
        for role, permissions in default_permissions.items():
            if role not in self.rbac_config["role_permissions"]:
                self.rbac_config["role_permissions"][role] = permissions

        # 役割階層の設定
        if not self.rbac_config["role_hierarchy"]:
            self.rbac_config["role_hierarchy"] = {
                Role.GUEST.value: [],
                Role.USER.value: [Role.GUEST.value],
                Role.DEVELOPER.value: [Role.USER.value],
                Role.AI_WORKER.value: [Role.USER.value],
                Role.AI_PRESIDENT.value: [Role.AI_WORKER.value, Role.DEVELOPER.value],
                Role.SYSTEM_ADMIN.value: [Role.DEVELOPER.value],
                Role.SECURITY_ADMIN.value: [Role.SYSTEM_ADMIN.value],
            }

        self._save_rbac_config()

    def assign_role(
        self, user_id: str, role: Role, assigned_by: str = "system"
    ) -> bool:
        """ユーザーに役割を割り当て"""
        try:
            if user_id not in self.rbac_config["user_roles"]:
                self.rbac_config["user_roles"][user_id] = []

            if role.value not in self.rbac_config["user_roles"][user_id]:
                self.rbac_config["user_roles"][user_id].append(role.value)

                # 監査ログ記録
                self._log_access(
                    user_id,
                    f"ROLE_ASSIGNED:{role.value}",
                    "SUCCESS",
                    f"Assigned by {assigned_by}",
                )

                self._save_rbac_config()
                logger.info(f"Role {role.value} assigned to user {user_id}")
                return True

            return False  # 既に割り当て済み

        except Exception as e:
            logger.error(f"Failed to assign role: {e}")
            self._log_access(user_id, f"ROLE_ASSIGNED:{role.value}", "FAILED", str(e))
            return False

    def revoke_role(self, user_id: str, role: Role, revoked_by: str = "system") -> bool:
        """ユーザーから役割を取り消し"""
        try:
            if (
                user_id in self.rbac_config["user_roles"]
                and role.value in self.rbac_config["user_roles"][user_id]
            ):
                self.rbac_config["user_roles"][user_id].remove(role.value)

                # 監査ログ記録
                self._log_access(
                    user_id,
                    f"ROLE_REVOKED:{role.value}",
                    "SUCCESS",
                    f"Revoked by {revoked_by}",
                )

                self._save_rbac_config()
                logger.info(f"Role {role.value} revoked from user {user_id}")
                return True

            return False  # 役割が割り当てられていない

        except Exception as e:
            logger.error(f"Failed to revoke role: {e}")
            self._log_access(user_id, f"ROLE_REVOKED:{role.value}", "FAILED", str(e))
            return False

    def get_user_permissions(self, user_id: str) -> Set[str]:
        """ユーザーの全権限を取得（継承含む）"""
        permissions = set()

        # ユーザーの役割を取得
        user_roles = self.rbac_config["user_roles"].get(user_id, [])

        for role in user_roles:
            # 直接の権限を追加
            role_permissions = self.rbac_config["role_permissions"].get(role, [])
            permissions.update(role_permissions)

            # 継承された権限を追加
            inherited_permissions = self._get_inherited_permissions(role)
            permissions.update(inherited_permissions)

        return permissions

    def _get_inherited_permissions(self, role: str) -> Set[str]:
        """役割の継承権限を取得"""
        permissions = set()

        # 親役割を取得
        parent_roles = self.rbac_config["role_hierarchy"].get(role, [])

        for parent_role in parent_roles:
            # 親役割の権限を追加
            parent_permissions = self.rbac_config["role_permissions"].get(
                parent_role, []
            )
            permissions.update(parent_permissions)

            # 再帰的に継承権限を取得
            inherited = self._get_inherited_permissions(parent_role)
            permissions.update(inherited)

        return permissions

    def has_permission(
        self, user_id: str, permission: Permission, resource: Optional[str] = None
    ) -> bool:
        """ユーザーが特定の権限を持っているかチェック"""
        try:
            user_permissions = self.get_user_permissions(user_id)

            # 権限チェック
            has_perm = permission.value in user_permissions

            # 監査ログ記録
            self._log_access(
                user_id,
                f"PERMISSION_CHECK:{permission.value}",
                "SUCCESS" if has_perm else "DENIED",
                f"Resource: {resource}" if resource else "",
            )

            return has_perm

        except Exception as e:
            logger.error(f"Failed to check permission: {e}")
            self._log_access(
                user_id, f"PERMISSION_CHECK:{permission.value}", "ERROR", str(e)
            )
            return False

    def check_access(self, user_id: str, operation: str, resource: str = "") -> bool:
        """アクセス権限の総合チェック"""
        # 操作に基づく権限マッピング
        operation_permissions = {
            "read": Permission.READ,
            "write": Permission.WRITE,
            "delete": Permission.DELETE,
            "execute": Permission.EXECUTE,
            "admin": Permission.ADMIN,
            "ai_create_model": Permission.AI_CREATE_MODEL,
            "ai_train_model": Permission.AI_TRAIN_MODEL,
            "ai_deploy_model": Permission.AI_DEPLOY_MODEL,
            "ai_access_memory": Permission.AI_ACCESS_MEMORY,
            "ai_modify_system": Permission.AI_MODIFY_SYSTEM,
            "president_declare": Permission.PRESIDENT_DECLARE,
            "president_modify_rules": Permission.PRESIDENT_MODIFY_RULES,
            "president_override": Permission.PRESIDENT_OVERRIDE,
            "system_config": Permission.SYSTEM_CONFIG,
            "system_backup": Permission.SYSTEM_BACKUP,
            "system_restore": Permission.SYSTEM_RESTORE,
            "system_monitoring": Permission.SYSTEM_MONITORING,
        }

        required_permission = operation_permissions.get(operation)
        if not required_permission:
            logger.warning(f"Unknown operation: {operation}")
            return False

        return self.has_permission(user_id, required_permission, resource)

    def _log_access(self, user_id: str, operation: str, status: str, details: str = ""):
        """アクセス監査ログ記録"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "operation": operation,
            "status": status,
            "details": details,
            "session_hash": hashlib.sha256(
                f"{user_id}{datetime.now().date()}".encode()
            ).hexdigest()[:8],
        }

        with open(self.access_log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

    def get_user_roles(self, user_id: str) -> List[str]:
        """ユーザーの役割一覧を取得"""
        return self.rbac_config["user_roles"].get(user_id, [])

    def get_role_permissions(self, role: Role) -> List[str]:
        """役割の権限一覧を取得"""
        return self.rbac_config["role_permissions"].get(role.value, [])

    def list_all_users(self) -> Dict[str, List[str]]:
        """全ユーザーと役割の一覧"""
        return self.rbac_config["user_roles"]

    def get_access_statistics(self) -> Dict:
        """アクセス統計情報を取得"""
        try:
            access_count = {}
            permission_usage = {}

            if self.access_log_file.exists():
                with open(self.access_log_file) as f:
                    for line in f:
                        try:
                            log_entry = json.loads(line.strip())
                            user_id = log_entry["user_id"]
                            operation = log_entry["operation"]

                            access_count[user_id] = access_count.get(user_id, 0) + 1
                            permission_usage[operation] = (
                                permission_usage.get(operation, 0) + 1
                            )

                        except json.JSONDecodeError:
                            continue

            return {
                "total_users": len(self.rbac_config["user_roles"]),
                "access_count": access_count,
                "permission_usage": permission_usage,
                "last_updated": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to get access statistics: {e}")
            return {}


# グローバルインスタンス
_rbac_system = None


def get_rbac_system() -> RBACSystem:
    """RBACシステムのシングルトン取得"""
    global _rbac_system
    if _rbac_system is None:
        _rbac_system = RBACSystem()
    return _rbac_system


def has_permission(user_id: str, permission: Permission, resource: str = "") -> bool:
    """権限チェックの便利関数"""
    return get_rbac_system().has_permission(user_id, permission, resource)


def check_access(user_id: str, operation: str, resource: str = "") -> bool:
    """アクセスチェックの便利関数"""
    return get_rbac_system().check_access(user_id, operation, resource)


def assign_role(user_id: str, role: Role, assigned_by: str = "system") -> bool:
    """役割割り当ての便利関数"""
    return get_rbac_system().assign_role(user_id, role, assigned_by)


def main():
    """テスト実行"""
    rbac = RBACSystem()

    # AI Presidentの役割を割り当て
    success = rbac.assign_role("ai_president_001", Role.AI_PRESIDENT, "system")
    print(f"AI President role assignment: {'SUCCESS' if success else 'FAILED'}")

    # 権限チェック
    can_declare = rbac.has_permission("ai_president_001", Permission.PRESIDENT_DECLARE)
    print(f"Can declare as President: {can_declare}")

    # アクセスチェック
    can_modify_system = rbac.check_access("ai_president_001", "ai_modify_system")
    print(f"Can modify system: {can_modify_system}")

    # 統計情報
    stats = rbac.get_access_statistics()
    print(f"Access statistics: {stats}")


if __name__ == "__main__":
    main()
