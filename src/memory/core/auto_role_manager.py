#!/usr/bin/env python3
"""
Auto Role Manager
役職が4個を超えた場合の自動整理システム
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


class AutoRoleManager:
    """役職自動管理システム"""

    MAX_ROLES = 4

    def __init__(self, organization_state_path: str):
        self.state_path = Path(organization_state_path)
        self.logger = self._setup_logger()

    def _setup_logger(self):
        """ログ設定"""
        logger = logging.getLogger('auto_role_manager')
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def load_organization_state(self) -> Dict[str, Any]:
        """組織状態を読み込み"""
        try:
            with open(self.state_path, encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load organization state: {e}")
            return {}

    def save_organization_state(self, data: Dict[str, Any]) -> bool:
        """組織状態を保存"""
        try:
            with open(self.state_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Failed to save organization state: {e}")
            return False

    def prioritize_roles(self, roles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """役職を優先度順にソート"""
        # 優先度マッピング（高い順）
        priority_mapping = {
            'PRESIDENT': 100,
            'REQUIREMENTS_ANALYST': 90,
            'SECURITY_SPECIALIST': 85,
            'COORDINATOR': 80,
            'SYSTEM_ARCHITECT': 75,
            'BACKEND_DEVELOPER': 70,
            'FRONTEND_DEVELOPER': 65,
            'DEVOPS_ENGINEER': 60,
            'QA_ENGINEER': 55,
            'UI_DESIGNER': 50,
            'PROJECT_MANAGER': 45
        }

        def get_priority(role):
            name = role.get('name', 'UNKNOWN')
            base_priority = priority_mapping.get(name, 0)

            # authority_levelも考慮
            authority_bonus = role.get('authority_level', 0) * 2

            # responsibilitiesの数も考慮
            responsibility_bonus = len(role.get('responsibilities', [])) * 1

            return base_priority + authority_bonus + responsibility_bonus

        return sorted(roles, key=get_priority, reverse=True)

    def auto_manage_roles(self) -> bool:
        """役職の自動管理を実行"""
        self.logger.info("Starting automatic role management")

        # 組織状態を読み込み
        data = self.load_organization_state()
        if not data:
            return False

        roles = data.get('active_roles', [])
        current_count = len(roles)

        self.logger.info(f"Current role count: {current_count}")

        # 4個以下の場合は何もしない
        if current_count <= self.MAX_ROLES:
            self.logger.info(f"Role count is within limit ({current_count} <= {self.MAX_ROLES})")
            return True

        # 自動整理が必要
        self.logger.warning(f"Role count exceeds limit ({current_count} > {self.MAX_ROLES}). Auto-organizing...")

        # バックアップ作成
        backup_path = self.state_path.with_suffix('.auto_backup')
        try:
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.logger.info(f"Backup created: {backup_path}")
        except Exception as e:
            self.logger.error(f"Failed to create backup: {e}")
            return False

        # 優先度順にソート
        prioritized_roles = self.prioritize_roles(roles)

        # 上位4個を選択
        selected_roles = prioritized_roles[:self.MAX_ROLES]
        excluded_roles = prioritized_roles[self.MAX_ROLES:]

        self.logger.info("Selected roles (top 4):")
        for i, role in enumerate(selected_roles, 1):
            name = role.get('name', 'UNKNOWN')
            authority = role.get('authority_level', 0)
            self.logger.info(f"  {i}. {name} (authority: {authority})")

        self.logger.info("Excluded roles:")
        for role in excluded_roles:
            name = role.get('name', 'UNKNOWN')
            authority = role.get('authority_level', 0)
            self.logger.info(f"  - {name} (authority: {authority})")

        # 組織状態を更新
        data['active_roles'] = selected_roles
        data['last_updated'] = datetime.now().isoformat()
        data['current_context'] = f"Auto-managed: {current_count} -> {len(selected_roles)} roles"

        # 自動管理履歴を記録
        if 'role_generation_history' not in data:
            data['role_generation_history'] = []

        history_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': 'auto_role_limit_enforcement',
            'original_count': current_count,
            'final_count': len(selected_roles),
            'excluded_roles': [role.get('name', 'UNKNOWN') for role in excluded_roles]
        }
        data['role_generation_history'].append(history_entry)

        # 保存
        if self.save_organization_state(data):
            self.logger.info(f"✅ Auto role management completed: {current_count} -> {len(selected_roles)} roles")
            return True
        else:
            self.logger.error("❌ Failed to save updated organization state")
            return False

    def get_role_status(self) -> Dict[str, Any]:
        """現在の役職状況を取得"""
        data = self.load_organization_state()
        if not data:
            return {}

        roles = data.get('active_roles', [])

        return {
            'current_count': len(roles),
            'max_allowed': self.MAX_ROLES,
            'within_limit': len(roles) <= self.MAX_ROLES,
            'roles': [
                {
                    'name': role.get('name', 'UNKNOWN'),
                    'authority_level': role.get('authority_level', 0),
                    'responsibilities_count': len(role.get('responsibilities', []))
                }
                for role in roles
            ]
        }


def main():
    """メイン実行関数"""
    import sys

    # 設定
    org_state_path = "src/memory/core/organization_state.json"

    if len(sys.argv) > 1:
        command = sys.argv[1]

        manager = AutoRoleManager(org_state_path)

        if command == "manage":
            success = manager.auto_manage_roles()
            sys.exit(0 if success else 1)

        elif command == "status":
            status = manager.get_role_status()
            print(json.dumps(status, ensure_ascii=False, indent=2))

        elif command == "check":
            status = manager.get_role_status()
            if status.get('within_limit', True):
                print("✅ Role count is within limit")
                sys.exit(0)
            else:
                print(f"⚠️ Role count exceeds limit: {status.get('current_count', 0)} > {manager.MAX_ROLES}")
                sys.exit(1)

        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
    else:
        print("Usage:")
        print("  python auto_role_manager.py manage   # Auto-manage roles")
        print("  python auto_role_manager.py status   # Show role status")
        print("  python auto_role_manager.py check    # Check if within limit")


if __name__ == "__main__":
    main()