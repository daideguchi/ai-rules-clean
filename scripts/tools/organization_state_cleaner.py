#!/usr/bin/env python3
"""
Organization State Data Cleaner
重複した役職データを整理し、正規化されたAI組織状態を作成
"""

import json
import sys
from datetime import datetime
from pathlib import Path


class OrganizationStateCleaner:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.backup_path = self.file_path.with_suffix('.backup')
        self.data = None

    def load_data(self):
        """データを読み込み"""
        try:
            with open(self.file_path, encoding='utf-8') as f:
                self.data = json.load(f)
            print(f"✅ Loaded data from {self.file_path}")
            return True
        except Exception as e:
            print(f"❌ Failed to load data: {e}")
            return False

    def create_backup(self):
        """バックアップを作成"""
        try:
            with open(self.backup_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            print(f"✅ Backup created: {self.backup_path}")
            return True
        except Exception as e:
            print(f"❌ Failed to create backup: {e}")
            return False

    def analyze_duplicates(self):
        """重複データを分析"""
        if not self.data or 'active_roles' not in self.data:
            print("❌ No active_roles data found")
            return

        roles = self.data['active_roles']
        print(f"📊 Total roles: {len(roles)}")

        # 役職名別のカウント
        role_counts = {}
        for role in roles:
            name = role.get('name', 'UNKNOWN')
            role_counts[name] = role_counts.get(name, 0) + 1

        print("\n🔍 Role counts:")
        for name, count in role_counts.items():
            if count > 1:
                print(f"  🔴 {name}: {count} instances (DUPLICATE)")
            else:
                print(f"  ✅ {name}: {count} instance")

        return role_counts

    def deduplicate_roles(self):
        """重複役職を除去"""
        if not self.data or 'active_roles' not in self.data:
            return False

        roles = self.data['active_roles']
        unique_roles = {}

        print("\n🧹 Deduplicating roles...")

        for role in roles:
            name = role.get('name', 'UNKNOWN')

            # より詳細な役職定義を保持（responsibilities が多いものを優先）
            if name not in unique_roles:
                unique_roles[name] = role
                print(f"  ✅ Added {name}")
            else:
                # より詳細な定義がある場合は置き換え
                existing_resp_count = len(unique_roles[name].get('responsibilities', []))
                new_resp_count = len(role.get('responsibilities', []))

                if new_resp_count > existing_resp_count:
                    unique_roles[name] = role
                    print(f"  🔄 Updated {name} (more detailed)")
                else:
                    print(f"  ⏭️  Skipped duplicate {name}")

        # 重複除去された役職リストを設定
        self.data['active_roles'] = list(unique_roles.values())

        print(f"\n✅ Deduplication complete: {len(roles)} → {len(unique_roles)} roles")
        return True

    def normalize_data(self):
        """データを正規化"""
        print("\n🔧 Normalizing organization data...")

        # タイムスタンプを更新
        self.data['last_updated'] = datetime.now().isoformat()

        # 各役職のauthority_levelが重複しないように調整
        roles = self.data['active_roles']
        authority_levels = {}

        for role in roles:
            name = role['name']
            current_level = role.get('authority_level', 5)

            # 役職に応じた適切な権限レベルを設定
            if name == 'PRESIDENT':
                role['authority_level'] = 10
            elif name == 'REQUIREMENTS_ANALYST':
                role['authority_level'] = 9
            elif name == 'SECURITY_SPECIALIST':
                role['authority_level'] = 9
            elif name == 'COORDINATOR':
                role['authority_level'] = 8
            else:
                role['authority_level'] = current_level

            authority_levels[name] = role['authority_level']

        print("  ✅ Authority levels normalized:")
        for name, level in authority_levels.items():
            print(f"    {name}: {level}")

        # コンテキストを更新
        self.data['current_context'] = "Clean and optimized AI organization state"

        print("  ✅ Data normalization complete")
        return True

    def save_cleaned_data(self):
        """整理されたデータを保存"""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            print(f"✅ Cleaned data saved to {self.file_path}")
            return True
        except Exception as e:
            print(f"❌ Failed to save cleaned data: {e}")
            return False

    def clean_organization_state(self):
        """組織状態データの完全クリーニング"""
        print("🚀 Organization State Cleaner - Starting")
        print("=" * 50)

        # Step 1: データ読み込み
        if not self.load_data():
            return False

        # Step 2: バックアップ作成
        if not self.create_backup():
            return False

        # Step 3: 重複分析
        self.analyze_duplicates()

        # Step 4: 重複除去
        if not self.deduplicate_roles():
            return False

        # Step 5: データ正規化
        if not self.normalize_data():
            return False

        # Step 6: 保存
        if not self.save_cleaned_data():
            return False

        print("\n🎉 Organization state cleaning completed successfully!")
        print(f"📁 Backup saved: {self.backup_path}")
        print(f"📁 Cleaned data: {self.file_path}")

        return True


def main():
    if len(sys.argv) != 2:
        print("Usage: python organization_state_cleaner.py <json_file_path>")
        sys.exit(1)

    file_path = sys.argv[1]

    if not Path(file_path).exists():
        print(f"❌ File not found: {file_path}")
        sys.exit(1)

    cleaner = OrganizationStateCleaner(file_path)
    success = cleaner.clean_organization_state()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
