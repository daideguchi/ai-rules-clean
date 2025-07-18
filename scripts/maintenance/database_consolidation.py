#!/usr/bin/env python3
"""
データベース統合・整理システム
o3ベストプラクティスに基づく3DB統一アーキテクチャ
"""

import json
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path


class DatabaseConsolidation:
    def __init__(self):
        self.project_root = Path("/Users/dd/Desktop/1_dev/coding-rule2")
        self.backup_dir = (
            self.project_root
            / "runtime"
            / "db_backups"
            / datetime.now().strftime("%Y%m%d_%H%M%S")
        )
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # 新しい統合DB設計
        self.target_dbs = {
            "core.db": {
                "description": "コアシステム - メモリ、セッション、ユーザー記録",
                "source_dbs": [
                    "runtime/memory/forever_ledger.db",
                    "runtime/memory/user_prompts.db",
                    "runtime/memory/autonomous_growth.db",
                    "runtime/memory/ai_growth.db",
                ],
            },
            "ai_organization.db": {
                "description": "AI組織システム - tmux協調、役割管理",
                "source_dbs": [
                    "runtime/databases/ai_organization_bridge.db",
                    "runtime/ai_organization_bridge.db",  # 重複確認
                ],
            },
            "enforcement.db": {
                "description": "ガバナンス・エンフォースメント - ポリシー、違反記録",
                "source_dbs": [
                    "runtime/enforcement/policy_decisions.db",
                    "runtime/databases/ultra_correction.db",
                ],
            },
        }

    def backup_existing_dbs(self):
        """既存DB全バックアップ"""
        print("📁 既存データベースバックアップ開始...")

        backed_up = set()

        for db_pattern in ["**/*.db"]:
            for db_file in self.project_root.glob(db_pattern):
                if db_file.exists() and db_file.name not in backed_up:
                    backup_path = self.backup_dir / db_file.name
                    shutil.copy2(db_file, backup_path)
                    backed_up.add(db_file.name)
                    print(f"  ✅ {db_file.name} → {backup_path}")

        print(f"📦 バックアップ完了: {self.backup_dir} ({len(backed_up)}ファイル)")

    def analyze_table_schemas(self, db_path):
        """テーブルスキーマ分析"""
        tables = {}

        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
                table_names = [row[0] for row in cursor.fetchall()]

                for table_name in table_names:
                    cursor = conn.execute(f"PRAGMA table_info({table_name})")
                    columns = cursor.fetchall()

                    cursor = conn.execute(f"SELECT COUNT(*) FROM {table_name}")
                    row_count = cursor.fetchone()[0]

                    tables[table_name] = {
                        "columns": len(columns),
                        "rows": row_count,
                        "schema": columns,
                    }
        except Exception as e:
            print(f"❌ {db_path} 分析エラー: {e}")

        return tables

    def create_consolidated_db(self, target_name, config):
        """統合データベース作成"""
        target_path = self.project_root / "runtime" / "databases" / target_name
        target_path.parent.mkdir(parents=True, exist_ok=True)

        print(f"\n🔨 {target_name} 統合開始...")
        print(f"目的: {config['description']}")

        # 新しい統合DBを作成
        with sqlite3.connect(target_path) as target_conn:
            # メタデータテーブル作成
            target_conn.execute(
                """
                CREATE TABLE IF NOT EXISTS _consolidation_metadata (
                    id INTEGER PRIMARY KEY,
                    source_db TEXT NOT NULL,
                    source_table TEXT NOT NULL,
                    target_table TEXT NOT NULL,
                    migration_time TEXT NOT NULL,
                    row_count INTEGER DEFAULT 0
                )
            """
            )

            # 各ソースDBからデータ移行
            for source_db_path in config["source_dbs"]:
                full_source_path = self.project_root / source_db_path

                if not full_source_path.exists():
                    print(f"  ⚠️ スキップ: {source_db_path} (存在しない)")
                    continue

                print(f"  📊 {source_db_path} から移行中...")

                # ソースDB解析
                tables = self.analyze_table_schemas(full_source_path)

                if not tables:
                    print("    ❌ テーブルなし")
                    continue

                # ソースDBをアタッチ
                target_conn.execute(
                    f"ATTACH DATABASE '{full_source_path}' AS source_db"
                )

                try:
                    # 各テーブルを移行
                    for table_name, table_info in tables.items():
                        if table_name.startswith("sqlite_"):
                            continue

                        # テーブル作成（存在確認）
                        target_conn.execute(
                            f"CREATE TABLE IF NOT EXISTS {table_name} AS SELECT * FROM source_db.{table_name} WHERE 1=0"
                        )

                        # データ挿入（重複回避）
                        target_conn.execute(
                            f"INSERT OR IGNORE INTO {table_name} SELECT * FROM source_db.{table_name}"
                        )

                        # メタデータ記録
                        target_conn.execute(
                            """
                            INSERT INTO _consolidation_metadata
                            (source_db, source_table, target_table, migration_time, row_count)
                            VALUES (?, ?, ?, ?, ?)
                        """,
                            (
                                source_db_path,
                                table_name,
                                table_name,
                                datetime.now().isoformat(),
                                table_info["rows"],
                            ),
                        )

                        print(f"    ✅ {table_name}: {table_info['rows']}行")

                finally:
                    target_conn.execute("DETACH DATABASE source_db")

        print(f"  🎯 {target_name} 統合完了")
        return target_path

    def generate_architecture_report(self):
        """DBアーキテクチャレポート生成"""
        report = {
            "consolidation_timestamp": datetime.now().isoformat(),
            "architecture": "3-Database Unified Design (o3 Best Practices)",
            "databases": {},
            "backup_location": str(self.backup_dir),
        }

        for db_name, config in self.target_dbs.items():
            db_path = self.project_root / "runtime" / "databases" / db_name

            if db_path.exists():
                tables = self.analyze_table_schemas(db_path)
                total_rows = sum(table["rows"] for table in tables.values())

                report["databases"][db_name] = {
                    "description": config["description"],
                    "tables": len(tables),
                    "total_rows": total_rows,
                    "file_size_kb": round(db_path.stat().st_size / 1024, 1),
                    "table_details": {
                        name: {"rows": info["rows"], "columns": info["columns"]}
                        for name, info in tables.items()
                    },
                }

        return report

    def consolidate_all(self):
        """全DB統合実行"""
        print("🚀 データベース統合開始")
        print("=" * 60)

        # バックアップ
        self.backup_existing_dbs()

        # 統合実行
        created_dbs = []
        for db_name, config in self.target_dbs.items():
            target_path = self.create_consolidated_db(db_name, config)
            created_dbs.append(target_path)

        # レポート生成
        report = self.generate_architecture_report()

        report_path = self.project_root / "runtime" / "db_consolidation_report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n📊 統合レポート: {report_path}")

        # 統計表示
        print("\n🎯 統合結果:")
        for db_name, info in report["databases"].items():
            print(
                f"  - {db_name}: {info['tables']}テーブル, {info['total_rows']}行, {info['file_size_kb']}KB"
            )

        return report


def main():
    consolidation = DatabaseConsolidation()
    consolidation.consolidate_all()

    print("\n✅ データベース統合完了！")
    print("o3ベストプラクティスに基づく3DB統一アーキテクチャを実現")


if __name__ == "__main__":
    main()
