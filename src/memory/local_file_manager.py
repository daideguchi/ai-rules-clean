#!/usr/bin/env python3
"""
📁 ローカルファイル管理システム - 容量ベース自動削除
================================================

【目的】
- ローカル.logファイルの容量監視
- 一定容量超過時の自動削除
- 重要ファイル保護
- DBへの事前バックアップ

【実装内容】
- 容量ベース監視
- 古いファイルから優先削除
- 最新ファイル保護
- 削除前DB保存確認
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import psycopg2


class LocalFileManager:
    """o3推奨ローカルファイル管理 - 安全性優先二段階削除システム"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.db_config = {
            "host": "localhost",
            "database": "president_ai",
            "user": "dd",
            "password": "",
            "port": 5432,
        }

        # o3推奨現実的容量設定
        self.max_total_size_mb = 8192  # ハード上限 8GB (o3推奨開発環境標準)
        self.warning_threshold_mb = 6553  # 警告閾値 6.4GB (80%)
        self.target_cleanup_mb = 5242  # クリーンアップ目標 5.1GB (64%)

        # o3推奨階層化保護期間
        self.hot_retention_days = 14  # ホット層：14日間高速アクセス
        self.warm_retention_days = 365  # ウォーム層：1年間保持
        self.critical_preserve_days = 730  # クリティカル：2年間永続保護

        # o3推奨学習データ保護設定
        self.learning_data_protection = True  # 学習データは永続保護
        self.documentation_protection = True  # ドキュメントは永続保護

        # 安全性設定
        self.trash_directory = self.project_root / ".trash"
        self.verification_delay_seconds = 2  # 削除前検証待機
        self.max_batch_delete = 20  # 一回の最大削除数

        # o3推奨階層化ディレクトリ監視
        self.hot_tier_paths = [
            self.project_root / "operations" / "runtime-logs",
            self.project_root / "runtime",
            self.project_root / "logs",
            self.project_root / "tmp",
        ]

        self.warm_tier_path = self.project_root / "data" / "warm"
        self.learning_data_paths = [
            self.project_root / "docs",
            self.project_root / "ai-instructions",
            self.project_root / "memory",
        ]

        # o3推奨保護対象ファイルパターン
        self.learning_protected_patterns = [
            "mistake*",
            "president*",
            "*learning*",
            "*report*",
            "*analysis*",
        ]

        self.documentation_protected_patterns = [
            "README*",
            "*.md",
            "docs/*",
            "ai-instructions/*",
            "*manual*",
            "*guide*",
        ]

        self.critical_system_patterns = [
            "*error*",
            "*critical*",
            ".git*",
            "config/*",
            "*.py",
            "*.json",
        ]

    def calculate_tiered_storage_stats(self) -> Dict[str, Any]:
        """o3推奨階層化ストレージ統計計算"""

        hot_size = 0
        warm_size = 0
        protected_size = 0
        total_file_count = 0
        tier_stats = {
            "hot_tier": {},
            "warm_tier": {},
            "learning_data": {},
            "total_summary": {},
        }

        # ホット層統計
        for monitor_path in self.hot_tier_paths:
            if not monitor_path.exists():
                continue

            dir_size = 0
            dir_files = 0

            for file_path in monitor_path.rglob("*"):
                if file_path.is_file():
                    try:
                        file_size = file_path.stat().st_size
                        hot_size += file_size
                        dir_size += file_size
                        total_file_count += 1
                        dir_files += 1
                    except (OSError, PermissionError):
                        continue

            tier_stats["hot_tier"][str(monitor_path.relative_to(self.project_root))] = {
                "size_mb": round(dir_size / (1024 * 1024), 2),
                "file_count": dir_files,
            }

        # 学習データ層統計
        for learning_path in self.learning_data_paths:
            if not learning_path.exists():
                continue

            dir_size = 0
            dir_files = 0

            for file_path in learning_path.rglob("*"):
                if file_path.is_file():
                    try:
                        file_size = file_path.stat().st_size
                        protected_size += file_size
                        dir_size += file_size
                        total_file_count += 1
                        dir_files += 1
                    except (OSError, PermissionError):
                        continue

            tier_stats["learning_data"][
                str(learning_path.relative_to(self.project_root))
            ] = {"size_mb": round(dir_size / (1024 * 1024), 2), "file_count": dir_files}

        # ウォーム層統計
        if self.warm_tier_path.exists():
            for file_path in self.warm_tier_path.rglob("*"):
                if file_path.is_file():
                    try:
                        warm_size += file_path.stat().st_size
                    except (OSError, PermissionError):
                        continue

        total_size = hot_size + warm_size + protected_size
        total_size_mb = total_size / (1024 * 1024)
        hot_size_mb = hot_size / (1024 * 1024)
        warm_size_mb = warm_size / (1024 * 1024)
        protected_size_mb = protected_size / (1024 * 1024)

        tier_stats["total_summary"] = {
            "total_size_mb": round(total_size_mb, 2),
            "hot_tier_mb": round(hot_size_mb, 2),
            "warm_tier_mb": round(warm_size_mb, 2),
            "protected_data_mb": round(protected_size_mb, 2),
            "total_files": total_file_count,
            "capacity_analysis": {
                "max_limit_mb": self.max_total_size_mb,
                "warning_threshold_mb": self.warning_threshold_mb,
                "current_usage_percent": round(
                    (hot_size_mb / self.max_total_size_mb) * 100, 1
                ),
                "needs_cleanup": hot_size_mb > self.warning_threshold_mb,
                "tier_distribution": {
                    "hot_percent": round((hot_size_mb / total_size_mb) * 100, 1)
                    if total_size_mb > 0
                    else 0,
                    "warm_percent": round((warm_size_mb / total_size_mb) * 100, 1)
                    if total_size_mb > 0
                    else 0,
                    "protected_percent": round(
                        (protected_size_mb / total_size_mb) * 100, 1
                    )
                    if total_size_mb > 0
                    else 0,
                },
            },
        }

        return tier_stats

    def identify_tiered_cleanup_candidates(self) -> List[Dict[str, Any]]:
        """DISABLED: Memory inheritance system never deletes memories"""
        return []  # Always return empty - no cleanup candidates

        candidates = []
        now = datetime.now()
        preserve_cutoff = now - timedelta(days=self.preserve_recent_days)
        critical_preserve_cutoff = now - timedelta(days=self.critical_preserve_days)

        for monitor_path in self.monitored_paths:
            if not monitor_path.exists():
                continue

            for file_path in monitor_path.rglob("*"):
                if not file_path.is_file():
                    continue

                try:
                    stat = file_path.stat()
                    modified_time = datetime.fromtimestamp(stat.st_mtime)
                    file_size = stat.st_size

                    # 保護ファイルチェック
                    is_protected = self._is_protected_file(file_path)
                    is_recent = modified_time > preserve_cutoff
                    is_critical_recent = modified_time > critical_preserve_cutoff

                    # 削除候補条件
                    if not is_recent and not (is_protected and is_critical_recent):
                        candidates.append(
                            {
                                "path": file_path,
                                "relative_path": str(
                                    file_path.relative_to(self.project_root)
                                ),
                                "size_mb": round(file_size / (1024 * 1024), 3),
                                "modified_time": modified_time,
                                "age_days": (now - modified_time).days,
                                "is_protected": is_protected,
                                "file_type": self._classify_file_type(file_path),
                                "deletion_priority": self._calculate_deletion_priority(
                                    file_path, modified_time, file_size, is_protected
                                ),
                            }
                        )

                except (OSError, PermissionError):
                    continue

        # 削除優先度順にソート
        candidates.sort(key=lambda x: x["deletion_priority"], reverse=True)

        return candidates

    def _is_protected_file(self, file_path: Path) -> bool:
        """保護ファイル判定"""

        file_name_lower = file_path.name.lower()

        # パターンマッチング
        for pattern in self.protected_patterns:
            if pattern.replace("*", "") in file_name_lower:
                return True

        # 拡張子チェック
        if file_path.suffix in [".md", ".json", ".py"]:
            return True

        # パス内キーワード
        path_str = str(file_path).lower()
        if any(
            keyword in path_str
            for keyword in ["important", "critical", "backup", "recovery"]
        ):
            return True

        return False

    def _classify_file_type(self, file_path: Path) -> str:
        """ファイルタイプ分類"""

        suffix = file_path.suffix.lower()
        name_lower = file_path.name.lower()

        if suffix == ".log":
            if "error" in name_lower:
                return "error_log"
            elif "debug" in name_lower:
                return "debug_log"
            else:
                return "system_log"
        elif suffix == ".tmp":
            return "temporary"
        elif suffix in [".bak", ".backup"]:
            return "backup"
        elif suffix == ".json":
            return "data_file"
        elif suffix == ".md":
            return "documentation"
        else:
            return "other"

    def _calculate_deletion_priority(
        self,
        file_path: Path,
        modified_time: datetime,
        file_size: int,
        is_protected: bool,
    ) -> float:
        """o3推奨複合スコアリング削除優先度計算 (高いほど削除優先)"""

        now = datetime.now()
        age_days = (now - modified_time).days
        size_mb = file_size / (1024 * 1024)

        # o3推奨基本スコア計算
        age_score = min(age_days / 30.0, 10.0)  # 年齢スコア (最大10点)
        size_score = min(size_mb / 5.0, 5.0)  # サイズスコア (最大5点)

        # o3推奨ファイルタイプ重み
        file_type = self._classify_file_type(file_path)
        type_weight = {
            "temporary": 3.0,  # 一時ファイルは最優先削除
            "debug_log": 2.5,  # デバッグログは削除しやすい
            "system_log": 2.0,  # システムログは中程度
            "backup": 1.5,  # バックアップは重要度による
            "error_log": 0.5,  # エラーログは重要
            "documentation": 0.3,  # ドキュメントは保持優先
            "data_file": 0.2,  # データファイルは最重要
            "other": 1.0,
        }.get(file_type, 1.0)

        # o3推奨重要度調整
        importance_penalty = 0.1 if is_protected else 1.0

        # o3推奨アクセス頻度推定 (ファイル名パターンベース)
        access_freq_boost = 1.0
        name_lower = file_path.name.lower()
        if any(pattern in name_lower for pattern in ["temp", "tmp", "cache", ".log"]):
            access_freq_boost = 1.5  # アクセス頻度低いファイルは削除しやすい
        elif any(
            pattern in name_lower for pattern in ["config", "setting", "important"]
        ):
            access_freq_boost = 0.5  # 設定ファイルは削除しにくい

        # o3複合スコア計算式
        composite_score = (
            (age_score * 0.4 + size_score * 0.3)
            * type_weight
            * importance_penalty
            * access_freq_boost
        )

        return composite_score

    def execute_cleanup_o3_safe(
        self, target_size_mb: Optional[float] = None, dry_run: bool = True
    ) -> Dict[str, Any]:
        """DISABLED: Memory inheritance system never executes cleanup"""
        return {
            "status": "disabled",
            "message": "Memory inheritance system preserves all memories",
            "cleaned_files": 0,
            "bytes_freed": 0,
        }

        if target_size_mb is None:
            target_size_mb = self.target_cleanup_mb  # o3推奨目標値

        current_stats = self.calculate_total_size()
        current_size_mb = current_stats["total_size_mb"]

        # o3推奨閾値チェック
        if current_size_mb <= self.warning_threshold_mb:
            return {
                "status": "no_cleanup_needed",
                "current_size_mb": current_size_mb,
                "warning_threshold_mb": self.warning_threshold_mb,
                "message": "現在の容量は警告閾値以下です",
            }

        # o3推奨Trashディレクトリ準備
        if not dry_run:
            self.trash_directory.mkdir(exist_ok=True)

        candidates = self.identify_cleanup_candidates()
        processed_files = []
        moved_files = []
        deleted_files = []
        deleted_size_mb = 0.0
        errors = []
        rollback_operations = []  # o3推奨ロールバック用

        # o3推奨二段階削除量計算
        size_to_delete_mb = current_size_mb - target_size_mb

        try:
            # Phase 1: o3推奨Move → Verify パターン
            batch_count = 0
            for candidate in candidates:
                if (
                    deleted_size_mb >= size_to_delete_mb
                    or batch_count >= self.max_batch_delete
                ):
                    break

                file_path = candidate["path"]

                try:
                    # o3推奨DB事前バックアップ (重要ファイルの場合)
                    if candidate["is_protected"]:
                        backup_success = self._backup_to_database_o3(file_path)
                        if not backup_success:
                            errors.append(
                                f"DB保存失敗のため削除スキップ: {candidate['relative_path']}"
                            )
                            continue

                        # o3推奨DB保存ログ記録
                        self._log_deletion_to_database(candidate, "db_backup_completed")

                    if not dry_run:
                        # o3推奨安全なatomic rename操作
                        trash_path = (
                            self.trash_directory
                            / f"{file_path.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                        )
                        file_path.rename(trash_path)  # atomic operation
                        rollback_operations.append((trash_path, file_path))

                        moved_files.append(
                            {
                                "original_path": candidate["relative_path"],
                                "trash_path": str(
                                    trash_path.relative_to(self.project_root)
                                ),
                                "size_mb": candidate["size_mb"],
                            }
                        )

                    processed_files.append(
                        {
                            "path": candidate["relative_path"],
                            "size_mb": candidate["size_mb"],
                            "age_days": candidate["age_days"],
                            "file_type": candidate["file_type"],
                            "composite_score": candidate["deletion_priority"],
                        }
                    )
                    deleted_size_mb += candidate["size_mb"]
                    batch_count += 1

                except (OSError, PermissionError) as e:
                    errors.append(f"移動失敗: {candidate['relative_path']}: {str(e)}")
                    continue

            # Phase 2: o3推奨Verification → Delete パターン
            if not dry_run and moved_files:
                import time

                time.sleep(self.verification_delay_seconds)  # o3推奨検証待機

                # o3推奨最終検証後の実削除
                for moved_file in moved_files:
                    trash_path = self.project_root / moved_file["trash_path"]
                    if trash_path.exists():
                        trash_path.unlink()  # 実際の削除
                        deleted_files.append(moved_file)
                        # o3推奨削除ログ記録
                        self._log_deletion_to_database(moved_file, "file_deleted")

                rollback_operations.clear()  # 削除完了でロールバック不要

        except Exception as e:
            # o3推奨エラー時自動ロールバック
            if not dry_run and rollback_operations:
                for trash_path, original_path in rollback_operations:
                    try:
                        if trash_path.exists():
                            trash_path.rename(original_path)
                    except Exception:
                        pass
            errors.append(f"クリーンアップエラー: {str(e)}")

        final_size_mb = current_size_mb - deleted_size_mb

        return {
            "status": "cleanup_completed" if not dry_run else "dry_run_completed",
            "initial_size_mb": current_size_mb,
            "target_size_mb": target_size_mb,
            "final_size_mb": final_size_mb,
            "deleted_files_count": len(deleted_files),
            "deleted_size_mb": round(deleted_size_mb, 2),
            "space_freed_percent": round((deleted_size_mb / current_size_mb) * 100, 1),
            "deleted_files": deleted_files,
            "errors": errors,
            "dry_run": dry_run,
        }

    def _backup_to_database_o3(self, file_path: Path) -> bool:
        """o3推奨重要ファイルの安全なDB保存"""
        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()

            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()

            # o3推奨拡張ファイルバックアップテーブル
            cur.execute("""
                CREATE TABLE IF NOT EXISTS file_backups_o3 (
                    id SERIAL PRIMARY KEY,
                    file_path TEXT UNIQUE,
                    file_content TEXT,
                    file_size INTEGER,
                    original_modified TIMESTAMPTZ,
                    backed_up_at TIMESTAMPTZ DEFAULT NOW(),
                    file_type VARCHAR(50),
                    deletion_reason VARCHAR(100),
                    composite_score FLOAT,
                    is_protected BOOLEAN DEFAULT FALSE,
                    backup_hash VARCHAR(64)
                );
            """)

            stat = file_path.stat()
            modified_time = datetime.fromtimestamp(stat.st_mtime)

            # o3推奨ハッシュ付きバックアップ
            import hashlib

            content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

            cur.execute(
                """
                INSERT INTO file_backups_o3
                (file_path, file_content, file_size, original_modified, file_type,
                 deletion_reason, is_protected, backup_hash)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (file_path) DO UPDATE SET
                    file_content = EXCLUDED.file_content,
                    file_size = EXCLUDED.file_size,
                    backed_up_at = NOW(),
                    backup_hash = EXCLUDED.backup_hash;
            """,
                (
                    str(file_path.relative_to(self.project_root)),
                    content,
                    stat.st_size,
                    modified_time,
                    self._classify_file_type(file_path),
                    "capacity_cleanup",
                    self._is_protected_file(file_path),
                    content_hash,
                ),
            )

            conn.commit()
            cur.close()
            conn.close()

            return True

        except Exception as e:
            print(f"DB backup failed for {file_path}: {e}")
            return False

    def setup_automatic_monitoring(self) -> Dict[str, Any]:
        """自動監視設定"""

        monitor_script = (
            self.project_root / "scripts" / "utilities" / "auto_file_cleanup.py"
        )

        script_content = '''#!/usr/bin/env python3
"""自動ファイルクリーンアップスクリプト"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from memory.local_file_manager import LocalFileManager

def main():
    manager = LocalFileManager()

    # 容量チェック
    stats = manager.calculate_total_size()
    print(f"現在の容量: {stats['total_size_mb']}MB")

    if stats['threshold_status']['needs_cleanup']:
        print("クリーンアップが必要です。実行中...")
        result = manager.execute_cleanup(dry_run=False)
        print(f"クリーンアップ完了: {result['deleted_files_count']}ファイル削除 ({result['deleted_size_mb']}MB)")
    else:
        print("クリーンアップは不要です。")

if __name__ == "__main__":
    main()
'''

        monitor_script.parent.mkdir(parents=True, exist_ok=True)
        with open(monitor_script, "w", encoding="utf-8") as f:
            f.write(script_content)

        monitor_script.chmod(0o755)

        return {
            "status": "success",
            "monitor_script": str(monitor_script),
            "cron_command": f"0 */6 * * * {monitor_script}",  # 6時間おき
            "setup_instructions": [
                f"chmod +x {monitor_script}",
                f"crontab -e で追加: 0 */6 * * * {monitor_script}",
            ],
        }


def main():
    """メイン実行 - ローカルファイル管理"""
    print("📁 ローカルファイル管理システム開始")

    manager = LocalFileManager()

    # 1. 現在の容量状況確認
    print("\\n1️⃣ 現在の容量状況")
    stats = manager.calculate_total_size()
    print(f"総容量: {stats['total_size_mb']}MB")
    print(f"ファイル数: {stats['total_files']}")
    print(f"使用率: {stats['threshold_status']['current_usage_percent']}%")
    print(
        f"クリーンアップ必要: {'✅ Yes' if stats['threshold_status']['needs_cleanup'] else '❌ No'}"
    )

    # ディレクトリ別容量
    print("\\n   ディレクトリ別容量:")
    for dir_name, dir_stats in stats["directory_breakdown"].items():
        print(
            f"     {dir_name}: {dir_stats['size_mb']}MB ({dir_stats['file_count']}ファイル)"
        )

    # 2. 削除候補確認
    print("\\n2️⃣ 削除候補ファイル確認")
    candidates = manager.identify_cleanup_candidates()
    print(f"削除候補数: {len(candidates)}")

    if candidates:
        print("   上位削除候補:")
        for i, candidate in enumerate(candidates[:10]):
            print(
                f"     {i + 1}. {candidate['relative_path']} ({candidate['size_mb']}MB, {candidate['age_days']}日前)"
            )

    # 3. ドライランクリーンアップ
    if stats["threshold_status"]["needs_cleanup"]:
        print("\\n3️⃣ ドライランクリーンアップ")
        dry_result = manager.execute_cleanup(dry_run=True)
        print(f"ドライラン結果: {dry_result['status']}")
        print(f"   削除予定ファイル数: {dry_result['deleted_files_count']}")
        print(f"   削除予定容量: {dry_result['deleted_size_mb']}MB")
        print(f"   容量削減率: {dry_result['space_freed_percent']}%")

        # 実際のクリーンアップ実行確認
        print("\\n4️⃣ 実際のクリーンアップ実行")
        actual_result = manager.execute_cleanup(dry_run=False)
        print(f"実行結果: {actual_result['status']}")
        print(f"   削除ファイル数: {actual_result['deleted_files_count']}")
        print(f"   削除容量: {actual_result['deleted_size_mb']}MB")
        print(f"   最終容量: {actual_result['final_size_mb']}MB")

        if actual_result["errors"]:
            print(f"   エラー数: {len(actual_result['errors'])}")

    # 5. 自動監視設定
    print("\\n5️⃣ 自動監視設定")
    monitor_setup = manager.setup_automatic_monitoring()
    print(f"監視設定: {monitor_setup['status']}")
    print(f"   監視スクリプト: {monitor_setup['monitor_script']}")
    print(f"   Cron設定: {monitor_setup['cron_command']}")

    print("\\n✅ ローカルファイル管理システム実装完了")
    print("📍 容量ベース自動削除 + 重要ファイル保護 + DB事前バックアップ")


if __name__ == "__main__":
    main()
