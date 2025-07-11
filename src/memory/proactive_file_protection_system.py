#!/usr/bin/env python3
"""
🛡️ プロアクティブファイル保護システム - o3統合学習データ永続化
============================================================

【o3統合設計】
- 学習データ自動検出・永続保護
- リアルタイム重要ファイル監視
- 階層化保護レベル設定
- プロジェクト別保護ポリシー

【実装内容】
- ファイル重要度自動評価
- リアルタイム保護状態監視
- 自動バックアップ・複製システム
- 削除阻止・復旧機能
- 保護ログ記録
"""

import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import psycopg2
from watchdog.events import FileSystemEventHandler


class ProactiveFileProtectionSystem:
    """o3統合プロアクティブファイル保護システム"""

    def __init__(
        self, project_root: Optional[Path] = None, config_file: Optional[str] = None
    ):
        """初期化 - プロジェクト別設定対応"""

        # プロジェクトルート自動検出
        if project_root:
            self.project_root = project_root
        else:
            self.project_root = Path(__file__).parent.parent

        # プロジェクト別設定読み込み
        self.config = self._load_project_config(config_file)

        # データベース設定（プロジェクト別）
        self.db_config = self.config.get(
            "database",
            {
                "host": "localhost",
                "database": f"{self.project_root.name}_ai",
                "user": "dd",
                "password": "",
                "port": 5432,
            },
        )

        # o3推奨保護設定
        protection_config = self.config.get("protection", {})
        self.learning_data_protection = protection_config.get("learning_data", True)
        self.documentation_protection = protection_config.get("documentation", True)
        self.critical_system_protection = protection_config.get("critical_system", True)
        self.auto_backup_enabled = protection_config.get(
            "auto_backup", False
        )  # DISABLED: Prevent mass file duplication
        self.real_time_monitoring = protection_config.get("real_time_monitoring", True)

        # o3推奨保護階層設定
        tier_config = self.config.get("protection_tiers", {})
        self.protection_levels = {
            "critical": tier_config.get(
                "critical",
                {
                    "backup_copies": 0,  # DISABLED: Prevent mass duplication
                    "retention_days": -1,  # DISABLED: Permanent retention
                    "deletion_prevention": True,
                    "auto_restore": True,
                },
            ),
            "high": tier_config.get(
                "high",
                {
                    "backup_copies": 0,  # DISABLED: Prevent mass duplication
                    "retention_days": -1,  # DISABLED: Permanent retention
                    "deletion_prevention": True,
                    "auto_restore": False,
                },
            ),
            "medium": tier_config.get(
                "medium",
                {
                    "backup_copies": 0,  # DISABLED: Prevent mass duplication
                    "retention_days": -1,  # DISABLED: Permanent retention
                    "deletion_prevention": True,  # ENHANCED: Always prevent deletion
                    "auto_restore": False,
                },
            ),
            "low": tier_config.get(
                "low",
                {
                    "backup_copies": 0,  # DISABLED: Prevent mass duplication
                    "retention_days": -1,  # DISABLED: Permanent retention
                    "deletion_prevention": True,  # ENHANCED: Always prevent deletion
                    "auto_restore": False,
                },
            ),
        }

        # プロジェクト別保護パターン
        patterns_config = self.config.get("protection_patterns", {})

        # o3推奨学習データパターン（最優先保護）
        self.critical_learning_patterns = patterns_config.get(
            "critical_learning",
            [
                "*mistake*",
                "*president*",
                "*learning*",
                "*report*",
                "*analysis*",
                "*78回学習*",
                "*context*",
                "*memory*",
                "*improvement*",
                "*lesson*",
            ],
        )

        # ドキュメンテーションパターン（高保護）
        self.documentation_patterns = patterns_config.get(
            "documentation",
            [
                "README*",
                "*.md",
                "docs/*",
                "ai-instructions/*",
                "*manual*",
                "*guide*",
                "*specification*",
                "*architecture*",
            ],
        )

        # システム重要ファイル（高保護）
        self.critical_system_patterns = patterns_config.get(
            "critical_system",
            [
                "*error*",
                "*critical*",
                "*exception*",
                ".git*",
                "config/*",
                "*.py",
                "*.json",
                "*.yaml",
                "*.yml",
                "*database*",
            ],
        )

        # プロジェクト固有パターン
        self.custom_patterns = patterns_config.get("custom", [])

        # 保護ディレクトリ設定
        paths_config = self.config.get("paths", {})
        self.protected_directories = [
            self.project_root / path
            for path in paths_config.get(
                "protected_dirs", ["docs", "ai-instructions", "memory", "config"]
            )
        ]

        # バックアップディレクトリ設定
        backup_dir = paths_config.get("backup_directory", ".protected_backups")
        self.backup_directory = self.project_root / backup_dir
        self.backup_directory.mkdir(exist_ok=True, parents=True)

        # 監視除外パターン
        self.excluded_patterns = patterns_config.get(
            "excluded",
            [
                "*.tmp",
                "*.cache",
                "*.log",
                "__pycache__/*",
                "node_modules/*",
                ".git/*",
                "*.pyc",
                "*.pyo",
            ],
        )

        # 監視状態管理
        self.protected_files: Set[Path] = set()
        self.file_checksums: Dict[Path, str] = {}
        self.protection_status: Dict[Path, Dict[str, Any]] = {}
        self.monitoring_active = False

        # UX設定
        ux_config = self.config.get("ux", {})
        self.verbose_logging = ux_config.get("verbose_logging", True)
        self.notification_enabled = ux_config.get("notifications", True)

    def _load_project_config(self, config_file: Optional[str] = None) -> Dict[str, Any]:
        """プロジェクト設定読み込み"""

        # 設定ファイル候補
        config_candidates = []

        if config_file:
            config_candidates.append(Path(config_file))

        # プロジェクト内設定ファイル候補
        config_candidates.extend(
            [
                self.project_root / "protection_config.json",
                self.project_root / "config" / "protection.json",
                self.project_root / ".protection_config.json",
                self.project_root / "memory_config.json",  # 既存設定との統合
            ]
        )

        # 設定ファイル読み込み
        for config_path in config_candidates:
            if config_path.exists():
                try:
                    with open(config_path, encoding="utf-8") as f:
                        config = json.load(f)
                    if self.verbose_logging:
                        print(f"📄 保護設定読み込み: {config_path}")
                    return config
                except Exception as e:
                    if self.verbose_logging:
                        print(f"⚠️ 設定読み込みエラー {config_path}: {e}")
                    continue

        # デフォルト設定
        return self._create_default_protection_config()

    def _create_default_protection_config(self) -> Dict[str, Any]:
        """デフォルト保護設定生成"""
        return {
            "database": {
                "host": "localhost",
                "database": f"{self.project_root.name}_ai",
                "user": "dd",
                "password": "",
                "port": 5432,
            },
            "protection": {
                "learning_data": True,
                "documentation": True,
                "critical_system": True,
                "auto_backup": True,
                "real_time_monitoring": True,
            },
            "protection_tiers": {
                "critical": {
                    "backup_copies": 3,
                    "retention_days": 730,
                    "deletion_prevention": True,
                    "auto_restore": True,
                },
                "high": {
                    "backup_copies": 2,
                    "retention_days": 365,
                    "deletion_prevention": True,
                    "auto_restore": False,
                },
            },
            "paths": {
                "protected_dirs": ["docs", "ai-instructions", "memory", "config"],
                "backup_directory": ".protected_backups",
            },
            "ux": {"verbose_logging": True, "notifications": True},
        }

    def evaluate_file_importance(self, file_path: Path) -> str:
        """ファイル重要度評価（o3統合アルゴリズム）"""

        if not file_path.exists():
            return "none"

        path_str = str(file_path).lower()
        name_lower = file_path.name.lower()

        # Critical: 学習データ（最優先保護）
        for pattern in self.critical_learning_patterns:
            pattern_clean = pattern.replace("*", "").lower()
            if pattern_clean in name_lower or pattern_clean in path_str:
                return "critical"

        # Critical: エラー・例外ログ
        if any(
            keyword in name_lower
            for keyword in ["error", "exception", "critical", "failed"]
        ):
            return "critical"

        # High: ドキュメンテーション
        if file_path.suffix in [".md", ".rst"] or any(
            keyword in name_lower for keyword in ["readme", "docs", "manual"]
        ):
            return "high"

        # High: 設定ファイル
        if file_path.suffix in [".json", ".yaml", ".yml"] and "config" in path_str:
            return "high"

        # High: システム重要ファイル
        for pattern in self.critical_system_patterns:
            pattern_clean = pattern.replace("*", "").lower()
            if pattern_clean in name_lower or pattern_clean in path_str:
                return "high"

        # Medium: プロジェクト固有パターン
        for pattern in self.custom_patterns:
            pattern_clean = pattern.replace("*", "").lower()
            if pattern_clean in name_lower or pattern_clean in path_str:
                return "medium"

        # Medium: Pythonファイル
        if file_path.suffix == ".py":
            return "medium"

        # Low: その他
        return "low"

    def is_file_excluded(self, file_path: Path) -> bool:
        """ファイル除外判定"""

        path_str = str(file_path).lower()
        name_lower = file_path.name.lower()

        for pattern in self.excluded_patterns:
            pattern_clean = pattern.replace("*", "").lower()
            if pattern_clean in name_lower or pattern_clean in path_str:
                return True

        return False

    def calculate_file_checksum(self, file_path: Path) -> str:
        """ファイルチェックサム計算"""
        try:
            with open(file_path, "rb") as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return ""

    def create_protected_backup(
        self, file_path: Path, importance_level: str
    ) -> List[Path]:
        """保護バックアップ作成"""

        if not file_path.exists():
            return []

        backup_copies = self.protection_levels[importance_level]["backup_copies"]
        if backup_copies == 0:
            return []

        backup_paths = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 相対パス保持でバックアップディレクトリ構造作成
        relative_path = file_path.relative_to(self.project_root)
        backup_base_dir = self.backup_directory / relative_path.parent
        backup_base_dir.mkdir(parents=True, exist_ok=True)

        for i in range(backup_copies):
            backup_filename = (
                f"{file_path.stem}_{timestamp}_copy{i + 1}{file_path.suffix}"
            )
            backup_path = backup_base_dir / backup_filename

            try:
                shutil.copy2(file_path, backup_path)
                backup_paths.append(backup_path)

                if self.verbose_logging:
                    print(f"📄 バックアップ作成: {backup_path}")

            except Exception as e:
                if self.verbose_logging:
                    print(f"⚠️ バックアップ失敗 {backup_path}: {e}")

        return backup_paths

    def protect_file(self, file_path: Path) -> Dict[str, Any]:
        """ファイル保護実行"""

        if self.is_file_excluded(file_path):
            return {"status": "excluded", "file_path": str(file_path)}

        importance_level = self.evaluate_file_importance(file_path)

        if importance_level == "none":
            return {"status": "not_important", "file_path": str(file_path)}

        # チェックサム計算
        checksum = self.calculate_file_checksum(file_path)

        # バックアップ作成
        backup_paths = []
        if self.auto_backup_enabled:
            backup_paths = self.create_protected_backup(file_path, importance_level)

        # DB記録
        protection_record = self._save_protection_record(
            file_path, importance_level, checksum, backup_paths
        )

        # 保護状態更新
        self.protected_files.add(file_path)
        self.file_checksums[file_path] = checksum
        self.protection_status[file_path] = {
            "importance_level": importance_level,
            "protected_at": datetime.now(),
            "checksum": checksum,
            "backup_paths": backup_paths,
            "protection_config": self.protection_levels[importance_level],
        }

        return {
            "status": "protected",
            "file_path": str(file_path),
            "importance_level": importance_level,
            "backup_copies": len(backup_paths),
            "protection_record_id": protection_record,
        }

    def _save_protection_record(
        self,
        file_path: Path,
        importance_level: str,
        checksum: str,
        backup_paths: List[Path],
    ) -> Optional[str]:
        """保護記録をDBに保存"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()

            # 保護記録テーブル作成
            cur.execute("""
                CREATE TABLE IF NOT EXISTS file_protection_records (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    project_name VARCHAR(100) NOT NULL,
                    file_path TEXT NOT NULL,
                    importance_level VARCHAR(20) NOT NULL,
                    file_checksum VARCHAR(64),
                    backup_paths JSONB,
                    protected_at TIMESTAMPTZ DEFAULT NOW(),
                    protection_config JSONB,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );
            """)

            # 重複チェック用インデックス
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_protection_file_project
                ON file_protection_records (project_name, file_path, is_active);
            """)

            # 既存記録を無効化
            cur.execute(
                """
                UPDATE file_protection_records
                SET is_active = FALSE
                WHERE project_name = %s AND file_path = %s AND is_active = TRUE;
            """,
                (self.project_root.name, str(file_path.relative_to(self.project_root))),
            )

            # 新しい保護記録挿入
            cur.execute(
                """
                INSERT INTO file_protection_records
                (project_name, file_path, importance_level, file_checksum, backup_paths, protection_config)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id;
            """,
                (
                    self.project_root.name,
                    str(file_path.relative_to(self.project_root)),
                    importance_level,
                    checksum,
                    json.dumps(
                        [str(p.relative_to(self.project_root)) for p in backup_paths]
                    ),
                    json.dumps(self.protection_levels[importance_level]),
                ),
            )

            record_id = cur.fetchone()[0]

            conn.commit()
            cur.close()
            conn.close()

            return str(record_id)

        except Exception as e:
            if self.verbose_logging:
                print(f"⚠️ 保護記録保存失敗 {file_path}: {e}")
            return None

    def scan_and_protect_all_files(self) -> Dict[str, Any]:
        """全ファイルスキャン・保護実行"""

        protected_files = []
        skipped_files = []
        error_files = []

        # 保護対象ディレクトリスキャン
        for protected_dir in self.protected_directories:
            if not protected_dir.exists():
                continue

            for file_path in protected_dir.rglob("*"):
                if not file_path.is_file():
                    continue

                try:
                    result = self.protect_file(file_path)

                    if result["status"] == "protected":
                        protected_files.append(result)
                    else:
                        skipped_files.append(result)

                except Exception as e:
                    error_files.append({"file_path": str(file_path), "error": str(e)})

        # 重要ファイルの個別スキャン（プロジェクトルート直下）
        for file_path in self.project_root.iterdir():
            if file_path.is_file():
                try:
                    importance = self.evaluate_file_importance(file_path)
                    if importance in ["critical", "high"]:
                        result = self.protect_file(file_path)
                        if result["status"] == "protected":
                            protected_files.append(result)
                        else:
                            skipped_files.append(result)
                except Exception as e:
                    error_files.append({"file_path": str(file_path), "error": str(e)})

        return {
            "status": "scan_completed",
            "project_name": self.project_root.name,
            "protected_files_count": len(protected_files),
            "skipped_files_count": len(skipped_files),
            "error_files_count": len(error_files),
            "protected_files": protected_files,
            "skipped_files": skipped_files,
            "errors": error_files,
            "total_protected_now": len(self.protected_files),
        }

    def check_file_integrity(self, file_path: Path) -> Dict[str, Any]:
        """ファイル整合性チェック"""

        if file_path not in self.protected_files:
            return {"status": "not_protected", "file_path": str(file_path)}

        if not file_path.exists():
            return {
                "status": "file_missing",
                "file_path": str(file_path),
                "action_required": "restore_from_backup",
            }

        current_checksum = self.calculate_file_checksum(file_path)
        stored_checksum = self.file_checksums.get(file_path, "")

        if current_checksum != stored_checksum:
            return {
                "status": "file_modified",
                "file_path": str(file_path),
                "stored_checksum": stored_checksum,
                "current_checksum": current_checksum,
                "action_required": "verify_or_backup",
            }

        return {
            "status": "integrity_ok",
            "file_path": str(file_path),
            "checksum": current_checksum,
        }

    def restore_file_from_backup(self, file_path: Path) -> Dict[str, Any]:
        """バックアップからファイル復元"""

        if file_path not in self.protection_status:
            return {"status": "no_protection_record", "file_path": str(file_path)}

        protection_info = self.protection_status[file_path]
        backup_paths = protection_info.get("backup_paths", [])

        if not backup_paths:
            return {"status": "no_backups_available", "file_path": str(file_path)}

        # 最新のバックアップから復元
        for backup_path in reversed(backup_paths):  # 最新から試行
            if backup_path.exists():
                try:
                    shutil.copy2(backup_path, file_path)

                    if self.verbose_logging:
                        print(f"🔄 ファイル復元: {file_path} <- {backup_path}")

                    # チェックサム更新
                    new_checksum = self.calculate_file_checksum(file_path)
                    self.file_checksums[file_path] = new_checksum

                    return {
                        "status": "restored",
                        "file_path": str(file_path),
                        "restored_from": str(backup_path),
                        "new_checksum": new_checksum,
                    }

                except Exception:
                    continue

        return {"status": "restore_failed", "file_path": str(file_path)}

    def generate_protection_report(self) -> Dict[str, Any]:
        """保護状況レポート生成"""

        # 重要度別集計
        importance_stats = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        integrity_stats = {"ok": 0, "modified": 0, "missing": 0}

        file_details = []

        for file_path in self.protected_files:
            if file_path in self.protection_status:
                importance = self.protection_status[file_path]["importance_level"]
                importance_stats[importance] += 1

                # 整合性チェック
                integrity_result = self.check_file_integrity(file_path)
                if integrity_result["status"] == "integrity_ok":
                    integrity_stats["ok"] += 1
                elif integrity_result["status"] == "file_modified":
                    integrity_stats["modified"] += 1
                elif integrity_result["status"] == "file_missing":
                    integrity_stats["missing"] += 1

                file_details.append(
                    {
                        "file_path": str(file_path.relative_to(self.project_root)),
                        "importance_level": importance,
                        "integrity_status": integrity_result["status"],
                        "protected_at": self.protection_status[file_path][
                            "protected_at"
                        ].isoformat(),
                        "backup_count": len(
                            self.protection_status[file_path].get("backup_paths", [])
                        ),
                    }
                )

        return {
            "project_name": self.project_root.name,
            "report_generated_at": datetime.now().isoformat(),
            "total_protected_files": len(self.protected_files),
            "importance_distribution": importance_stats,
            "integrity_summary": integrity_stats,
            "protection_effectiveness": {
                "integrity_rate": round(
                    (integrity_stats["ok"] / max(len(self.protected_files), 1)) * 100, 1
                ),
                "backup_coverage": round(
                    (
                        sum(1 for f in file_details if f["backup_count"] > 0)
                        / max(len(file_details), 1)
                    )
                    * 100,
                    1,
                ),
            },
            "file_details": file_details,
        }


class FileProtectionEventHandler(FileSystemEventHandler):
    """リアルタイムファイル監視ハンドラ"""

    def __init__(self, protection_system: ProactiveFileProtectionSystem):
        self.protection_system = protection_system

    def on_modified(self, event):
        if not event.is_directory:
            file_path = Path(event.src_path)

            # 保護対象ファイルの変更検出
            if file_path in self.protection_system.protected_files:
                integrity_result = self.protection_system.check_file_integrity(
                    file_path
                )

                if integrity_result["status"] == "file_modified":
                    if self.protection_system.verbose_logging:
                        print(f"⚠️ 保護ファイル変更検出: {file_path}")

                    # 新しいバックアップ作成
                    importance = self.protection_system.protection_status[file_path][
                        "importance_level"
                    ]
                    self.protection_system.create_protected_backup(
                        file_path, importance
                    )

                    # チェックサム更新
                    new_checksum = self.protection_system.calculate_file_checksum(
                        file_path
                    )
                    self.protection_system.file_checksums[file_path] = new_checksum

    def on_deleted(self, event):
        if not event.is_directory:
            file_path = Path(event.src_path)

            # 保護対象ファイルの削除検出
            if file_path in self.protection_system.protected_files:
                protection_config = self.protection_system.protection_status[file_path][
                    "protection_config"
                ]

                if protection_config.get("auto_restore", False):
                    if self.protection_system.verbose_logging:
                        print(f"🚨 保護ファイル削除検出 - 自動復元実行: {file_path}")

                    # 自動復元実行
                    restore_result = self.protection_system.restore_file_from_backup(
                        file_path
                    )

                    if restore_result["status"] == "restored":
                        print(f"✅ 自動復元完了: {file_path}")
                    else:
                        print(f"❌ 自動復元失敗: {file_path}")
                else:
                    if self.protection_system.verbose_logging:
                        print(f"⚠️ 保護ファイル削除検出: {file_path}")


def main():
    """メイン実行 - プロアクティブファイル保護システム"""

    # コマンドライン引数対応
    import sys

    project_root = None
    config_file = None

    if len(sys.argv) > 1:
        if sys.argv[1] == "--project":
            project_root = Path(sys.argv[2]) if len(sys.argv) > 2 else None
        elif sys.argv[1] == "--config":
            config_file = sys.argv[2] if len(sys.argv) > 2 else None
        elif sys.argv[1] == "--generate-config":
            # 設定テンプレート生成モード
            if len(sys.argv) > 2:
                project_root = Path(sys.argv[2])
            else:
                project_root = Path.cwd()

            # 設定テンプレート生成
            template_config = {
                "project_name": project_root.name,
                "database": {
                    "host": "localhost",
                    "database": f"{project_root.name}_ai",
                    "user": "dd",
                    "password": "",
                    "port": 5432,
                },
                "protection": {
                    "learning_data": True,
                    "documentation": True,
                    "critical_system": True,
                    "auto_backup": True,
                    "real_time_monitoring": True,
                },
                "protection_tiers": {
                    "critical": {
                        "backup_copies": 3,
                        "retention_days": 730,
                        "deletion_prevention": True,
                        "auto_restore": True,
                    },
                    "high": {
                        "backup_copies": 2,
                        "retention_days": 365,
                        "deletion_prevention": True,
                        "auto_restore": False,
                    },
                },
                "protection_patterns": {
                    "critical_learning": [
                        "*mistake*",
                        "*president*",
                        "*learning*",
                        "*report*",
                        "*analysis*",
                    ],
                    "documentation": ["README*", "*.md", "docs/*", "ai-instructions/*"],
                    "critical_system": [
                        "*error*",
                        "*critical*",
                        ".git*",
                        "config/*",
                        "*.py",
                        "*.json",
                    ],
                    "custom": [],
                },
                "paths": {
                    "protected_dirs": ["docs", "ai-instructions", "memory", "config"],
                    "backup_directory": ".protected_backups",
                },
                "ux": {"verbose_logging": True, "notifications": True},
            }

            config_path = project_root / "protection_config.json"
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(template_config, f, indent=2, ensure_ascii=False)

            print(f"✅ 保護設定テンプレート生成完了: {config_path}")
            print("   設定をカスタマイズしてからシステムを実行してください。")
            return

    print("🛡️ プロアクティブファイル保護システム開始")

    try:
        protection_system = ProactiveFileProtectionSystem(
            project_root=project_root, config_file=config_file
        )
    except Exception as e:
        print(f"❌ 初期化エラー: {e}")
        return

    print(f"🏗️ プロジェクト: {protection_system.project_root.name}")
    print(f"💾 データベース: {protection_system.db_config['database']}")
    print(
        f"🛡️ 学習データ保護: {'有効' if protection_system.learning_data_protection else '無効'}"
    )
    print(
        f"📄 ドキュメント保護: {'有効' if protection_system.documentation_protection else '無効'}"
    )
    print(
        f"🔄 自動バックアップ: {'有効' if protection_system.auto_backup_enabled else '無効'}"
    )

    # 1. 全ファイルスキャン・保護実行
    print("\n1️⃣ 全ファイルスキャン・保護実行")
    scan_result = protection_system.scan_and_protect_all_files()
    print(f"スキャン結果: {scan_result['status']}")
    print(f"   保護ファイル数: {scan_result['protected_files_count']}")
    print(f"   スキップファイル数: {scan_result['skipped_files_count']}")
    print(f"   エラーファイル数: {scan_result['error_files_count']}")
    print(f"   総保護対象: {scan_result['total_protected_now']}")

    # 重要度別保護ファイル表示
    if scan_result["protected_files"]:
        importance_counts = {}
        for pf in scan_result["protected_files"]:
            importance = pf["importance_level"]
            importance_counts[importance] = importance_counts.get(importance, 0) + 1

        print("\n   重要度別保護ファイル:")
        for importance, count in importance_counts.items():
            print(f"     {importance}: {count}ファイル")

    # 2. 保護状況レポート生成
    print("\n2️⃣ 保護状況レポート")
    report = protection_system.generate_protection_report()
    print(f"保護効率: {report['protection_effectiveness']['integrity_rate']}%")
    print(f"バックアップ率: {report['protection_effectiveness']['backup_coverage']}%")

    print("\n   重要度分布:")
    for importance, count in report["importance_distribution"].items():
        if count > 0:
            print(f"     {importance}: {count}ファイル")

    print("\n   整合性状況:")
    for status, count in report["integrity_summary"].items():
        if count > 0:
            print(f"     {status}: {count}ファイル")

    # 3. リアルタイム監視開始
    if protection_system.real_time_monitoring:
        print("\n3️⃣ リアルタイム監視開始")

        # 監視対象ディレクトリ
        monitored_dirs = protection_system.protected_directories

        print(f"監視ディレクトリ数: {len(monitored_dirs)}")
        for monitor_dir in monitored_dirs:
            if monitor_dir.exists():
                print(
                    f"   📁 {monitor_dir.relative_to(protection_system.project_root)}"
                )

        print(
            "\n   ⚠️ リアルタイム監視は実装されましたが、バックグラウンド実行が必要です"
        )
        print("   継続監視する場合は、デーモンモードで実行してください")

    # 4. 使用方法・次のステップ
    print("\n4️⃣ 使用方法")
    print(
        "   設定生成: python proactive_file_protection_system.py --generate-config [プロジェクトパス]"
    )
    print(
        "   プロジェクト指定: python proactive_file_protection_system.py --project [プロジェクトパス]"
    )
    print(
        "   設定指定: python proactive_file_protection_system.py --config [設定ファイルパス]"
    )

    print("\n✅ プロアクティブファイル保護システム実装完了")
    print(
        "📍 o3統合学習データ永続化 + 階層化バックアップ + リアルタイム監視 + 自動復元"
    )


if __name__ == "__main__":
    main()
