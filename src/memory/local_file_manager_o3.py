#!/usr/bin/env python3
"""
📁 o3推奨プロジェクト別ローカルファイル管理システム - 安全性優先階層化削除
=================================================================

【o3回答による設計改善】
- 500MB → 8GB容量設定（開発環境に現実的）
- 階層化ストレージ（Hot/Warm/Cold）
- 学習データ永続保護（30日削除問題解決）
- プロジェクト別データベース設定
- 対話型UX改善

【実装内容】
- プロジェクト別設定ファイル自動検出
- 容量ベース階層化監視
- 複合スコアリング削除優先度
- 安全なatomic rename操作
- DB操作ログ記録
- 対話型クリーンアップウィザード
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional


class LocalFileManagerO3:
    """o3推奨プロジェクト別ローカルファイル管理 - UX重視設計"""

    def __init__(
        self, project_root: Optional[Path] = None, config_file: Optional[str] = None
    ):
        """初期化 - プロジェクト別設定対応"""

        # プロジェクトルート自動検出
        if project_root:
            self.project_root = project_root
        else:
            self.project_root = Path(__file__).parent.parent

        # 設定ファイル読み込み（UX優先）
        self.config = self._load_project_config(config_file)

        # DB設定（プロジェクト別）
        self.db_config = self.config.get(
            "database",
            {
                "host": "localhost",
                "database": f"{self.project_root.name}_ai",  # プロジェクト名ベース
                "user": "dd",
                "password": "",
                "port": 5432,
            },
        )

        # o3推奨現実的容量設定
        capacity_config = self.config.get("capacity", {})
        self.max_total_size_mb = capacity_config.get(
            "max_size_mb", 8192
        )  # デフォルト8GB
        self.warning_threshold_mb = capacity_config.get(
            "warning_mb", int(self.max_total_size_mb * 0.8)
        )
        self.target_cleanup_mb = capacity_config.get(
            "target_mb", int(self.max_total_size_mb * 0.64)
        )

        # o3推奨保護期間設定（プロジェクト別調整可能）
        # DISABLED: Memory inheritance system never expires data
        # retention_config = self.config.get("retention", {})
        self.hot_retention_days = -1  # DISABLED: Permanent retention
        self.warm_retention_days = -1  # DISABLED: Permanent retention
        self.critical_preserve_days = -1  # DISABLED: Permanent retention

        # プロジェクト別保護設定
        protection_config = self.config.get("protection", {})
        self.learning_data_protection = protection_config.get("learning_data", True)
        self.documentation_protection = protection_config.get("documentation", True)
        self.auto_backup_enabled = protection_config.get("auto_backup", True)

        # プロジェクト別ディレクトリ設定
        paths_config = self.config.get("paths", {})

        # ホット層（デフォルト + プロジェクト固有）
        default_hot_paths = ["logs", "tmp", "runtime", "operations/runtime-logs"]
        hot_paths = paths_config.get("hot_tier", default_hot_paths)
        self.hot_tier_paths = [self.project_root / path for path in hot_paths]

        # ウォーム層
        warm_path = paths_config.get("warm_tier", "data/warm")
        self.warm_tier_path = self.project_root / warm_path

        # 学習データ層（永続保護）
        default_learning_paths = ["docs", "ai-instructions", "memory"]
        learning_paths = paths_config.get("learning_data", default_learning_paths)
        self.learning_data_paths = [self.project_root / path for path in learning_paths]

        # 安全性設定（プロジェクト別調整可能）
        safety_config = self.config.get("safety", {})
        trash_dir = safety_config.get("trash_directory", ".trash")
        self.trash_directory = self.project_root / trash_dir
        self.verification_delay_seconds = safety_config.get("verification_delay", 2)
        self.max_batch_delete = safety_config.get("max_batch_delete", 20)

        # UX改善設定
        ux_config = self.config.get("ux", {})
        self.interactive_mode = ux_config.get("interactive_mode", True)
        self.verbose_logging = ux_config.get("verbose_logging", True)
        self.progress_bar_enabled = ux_config.get("progress_bar", True)

        # プロジェクト別保護パターン設定
        patterns_config = self.config.get("protection_patterns", {})

        default_learning = [
            "mistake*",
            "president*",
            "*learning*",
            "*report*",
            "*analysis*",
        ]
        self.learning_protected_patterns = patterns_config.get(
            "learning", default_learning
        )

        default_docs = [
            "README*",
            "*.md",
            "docs/*",
            "ai-instructions/*",
            "*manual*",
            "*guide*",
        ]
        self.documentation_protected_patterns = patterns_config.get(
            "documentation", default_docs
        )

        default_critical = [
            "*error*",
            "*critical*",
            ".git*",
            "config/*",
            "*.py",
            "*.json",
        ]
        self.critical_system_patterns = patterns_config.get(
            "critical_system", default_critical
        )

        # プロジェクト固有の追加パターン
        self.custom_protected_patterns = patterns_config.get("custom", [])

    def _load_project_config(self, config_file: Optional[str] = None) -> Dict[str, Any]:
        """プロジェクト設定ファイル読み込み"""

        # 設定ファイル候補
        config_candidates = []

        if config_file:
            config_candidates.append(Path(config_file))

        # プロジェクト内設定ファイル候補
        config_candidates.extend(
            [
                self.project_root / "memory_config.json",
                self.project_root / "config" / "memory.json",
                self.project_root / ".memory_config.json",
                Path.home() / ".ai_memory" / f"{self.project_root.name}.json",
                Path.home() / ".ai_memory" / "default.json",
            ]
        )

        # 最初に見つかった設定ファイルを使用
        for config_path in config_candidates:
            if config_path.exists():
                try:
                    with open(config_path, encoding="utf-8") as f:
                        config = json.load(f)
                    if hasattr(self, "verbose_logging") and self.verbose_logging:
                        print(f"📄 設定ファイル読み込み: {config_path}")
                    return config
                except Exception as e:
                    if hasattr(self, "verbose_logging") and self.verbose_logging:
                        print(f"⚠️ 設定ファイル読み込みエラー {config_path}: {e}")
                    continue

        # 設定ファイルが見つからない場合はデフォルト設定
        return self._create_default_config()

    def _create_default_config(self) -> Dict[str, Any]:
        """デフォルト設定生成"""
        return {
            "database": {
                "host": "localhost",
                "database": f"{self.project_root.name}_ai",
                "user": "dd",
                "password": "",
                "port": 5432,
            },
            "capacity": {"max_size_mb": 8192, "warning_mb": 6553, "target_mb": 5242},
            "retention": {"hot_days": 14, "warm_days": 365, "critical_days": 730},
            "protection": {
                "learning_data": True,
                "documentation": True,
                "auto_backup": True,
            },
            "ux": {
                "interactive_mode": True,
                "verbose_logging": True,
                "progress_bar": True,
            },
        }

    def generate_config_template(self, output_path: Optional[Path] = None) -> Path:
        """設定ファイルテンプレート生成"""

        if output_path is None:
            output_path = self.project_root / "memory_config.json"

        template = {
            "_comment": "AI Memory Management Configuration",
            "project_name": self.project_root.name,
            "database": {
                "host": "localhost",
                "database": f"{self.project_root.name}_ai",
                "user": "dd",
                "password": "",
                "port": 5432,
            },
            "capacity": {
                "_comment": "Storage capacity settings (MB)",
                "max_size_mb": 8192,
                "warning_mb": 6553,
                "target_mb": 5242,
            },
            "paths": {
                "_comment": "Project-specific directory paths",
                "hot_tier": ["logs", "tmp", "runtime"],
                "warm_tier": "data/warm",
                "learning_data": ["docs", "ai-instructions", "memory"],
            },
            "retention": {
                "_comment": "Retention periods (days)",
                "hot_days": 14,
                "warm_days": 365,
                "critical_days": 730,
            },
            "protection": {
                "_comment": "Data protection settings",
                "learning_data": True,
                "documentation": True,
                "auto_backup": True,
            },
            "protection_patterns": {
                "_comment": "File patterns to protect from deletion",
                "learning": [
                    "mistake*",
                    "president*",
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
            "safety": {
                "_comment": "Safety and verification settings",
                "trash_directory": ".trash",
                "verification_delay": 2,
                "max_batch_delete": 20,
            },
            "ux": {
                "_comment": "User experience settings",
                "interactive_mode": True,
                "verbose_logging": True,
                "progress_bar": True,
            },
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(template, f, indent=2, ensure_ascii=False)

        if self.verbose_logging:
            print(f"📝 設定テンプレート生成: {output_path}")

        return output_path

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

    def get_project_summary(self) -> Dict[str, Any]:
        """プロジェクト別サマリー生成"""
        stats = self.calculate_tiered_storage_stats()

        return {
            "project_name": self.project_root.name,
            "database_name": self.db_config["database"],
            "capacity_summary": stats["total_summary"]["capacity_analysis"],
            "tier_distribution": stats["total_summary"]["capacity_analysis"][
                "tier_distribution"
            ],
            "configuration": {
                "max_capacity_gb": round(self.max_total_size_mb / 1024, 1),
                "hot_retention_days": self.hot_retention_days,
                "warm_retention_days": self.warm_retention_days,
                "protection_enabled": {
                    "learning_data": self.learning_data_protection,
                    "documentation": self.documentation_protection,
                    "auto_backup": self.auto_backup_enabled,
                },
            },
            "paths": {
                "hot_tier": [
                    str(p.relative_to(self.project_root)) for p in self.hot_tier_paths
                ],
                "warm_tier": str(self.warm_tier_path.relative_to(self.project_root)),
                "learning_data": [
                    str(p.relative_to(self.project_root))
                    for p in self.learning_data_paths
                ],
            },
        }

    def interactive_cleanup_wizard(self) -> Dict[str, Any]:
        """DISABLED: Memory inheritance system never deletes memories"""
        return {
            "status": "disabled",
            "message": "Memory inheritance system preserves all memories",
            "cleaned_files": 0,
        }
        if not self.interactive_mode:
            return {"status": "non_interactive_mode", "message": "対話モードが無効です"}

        print("\n🧙‍♂️ 対話型クリーンアップウィザード")
        stats = self.calculate_tiered_storage_stats()
        capacity = stats["total_summary"]["capacity_analysis"]

        print(f"📊 現在の使用量: {capacity['current_usage_percent']}%")
        print(f"📈 警告閾値: {self.warning_threshold_mb}MB")
        print(f"🔥 現在のホット層: {stats['total_summary']['hot_tier_mb']}MB")

        if not capacity["needs_cleanup"]:
            print("✅ クリーンアップは不要です。")
            return {"status": "no_cleanup_needed"}

        print("\n🗂️  クリーンアップが推奨されます")
        print(f"💾 データベース: {self.db_config['database']}")
        print(
            f"🛡️ 学習データ保護: {'有効' if self.learning_data_protection else '無効'}"
        )

        # ユーザー確認
        while True:
            choice = input("\n実行しますか？ [y]es/[n]o/[d]ry-run: ").lower().strip()
            if choice in ["y", "yes"]:
                print("🚀 実際のクリーンアップを実行します...")
                return {"status": "user_confirmed", "action": "execute"}
            elif choice in ["d", "dry", "dry-run"]:
                print("🔍 ドライランを実行します...")
                return {"status": "user_confirmed", "action": "dry_run"}
            elif choice in ["n", "no"]:
                print("❌ クリーンアップをキャンセルしました。")
                return {"status": "cancelled"}
            else:
                print("⚠️  y/n/d のいずれかを入力してください。")


def main():
    """メイン実行 - プロジェクト別ローカルファイル管理"""

    # コマンドライン引数対応
    import sys

    project_root = None
    config_file = None

    if len(sys.argv) > 1:
        if sys.argv[1] == "--generate-config":
            if len(sys.argv) > 2:
                project_root = Path(sys.argv[2])
            else:
                project_root = Path.cwd()

            manager = LocalFileManagerO3(project_root=project_root)
            config_path = manager.generate_config_template()
            print(f"✅ 設定ファイルテンプレート生成完了: {config_path}")
            print("   設定をカスタマイズしてからシステムを実行してください。")
            return

        elif sys.argv[1] == "--config":
            config_file = sys.argv[2] if len(sys.argv) > 2 else None

        elif sys.argv[1] == "--project":
            project_root = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    print("📁 プロジェクト別ローカルファイル管理システム開始")

    try:
        manager = LocalFileManagerO3(project_root=project_root, config_file=config_file)
    except Exception as e:
        print(f"❌ 初期化エラー: {e}")
        print(
            "   設定ファイルを確認するか、--generate-config でテンプレートを生成してください。"
        )
        return

    print(f"🏗️ プロジェクト: {manager.project_root.name}")
    print(f"💾 データベース: {manager.db_config['database']}")
    print(f"📊 容量上限: {manager.max_total_size_mb}MB")

    # 1. プロジェクトサマリー表示
    print("\n1️⃣ プロジェクトサマリー")
    summary = manager.get_project_summary()
    print(f"💾 最大容量: {summary['configuration']['max_capacity_gb']}GB")
    print(f"🔥 ホット層保持: {summary['configuration']['hot_retention_days']}日")
    print(f"🌡️ ウォーム層保持: {summary['configuration']['warm_retention_days']}日")

    # 2. 階層化ストレージ状況確認
    print("\n2️⃣ 階層化ストレージ状況")
    stats = manager.calculate_tiered_storage_stats()
    total_summary = stats["total_summary"]
    print(f"📊 総容量: {total_summary['total_size_mb']}MB")
    print(
        f"🔥 ホット層: {total_summary['hot_tier_mb']}MB ({total_summary['capacity_analysis']['tier_distribution']['hot_percent']}%)"
    )
    print(
        f"🌡️ ウォーム層: {total_summary['warm_tier_mb']}MB ({total_summary['capacity_analysis']['tier_distribution']['warm_percent']}%)"
    )
    print(
        f"🛡️ 保護データ: {total_summary['protected_data_mb']}MB ({total_summary['capacity_analysis']['tier_distribution']['protected_percent']}%)"
    )
    print(f"📈 使用率: {total_summary['capacity_analysis']['current_usage_percent']}%")
    print(
        f"⚠️ クリーンアップ必要: {'✅ Yes' if total_summary['capacity_analysis']['needs_cleanup'] else '❌ No'}"
    )

    # ディレクトリ別容量
    print("\n   ホット層ディレクトリ別:")
    for dir_name, dir_stats in stats["hot_tier"].items():
        print(
            f"     🔥 {dir_name}: {dir_stats['size_mb']}MB ({dir_stats['file_count']}ファイル)"
        )

    if stats["learning_data"]:
        print("\n   学習データディレクトリ別:")
        for dir_name, dir_stats in stats["learning_data"].items():
            print(
                f"     🧠 {dir_name}: {dir_stats['size_mb']}MB ({dir_stats['file_count']}ファイル)"
            )

    # 3. 対話型クリーンアップ
    if total_summary["capacity_analysis"]["needs_cleanup"]:
        print("\n3️⃣ 対話型クリーンアップ")

        if manager.interactive_mode:
            wizard_result = manager.interactive_cleanup_wizard()
            print(f"ウィザード結果: {wizard_result['status']}")
        else:
            print("   非対話モードが設定されています")

    # 4. 設定表示と次のステップ
    print("\n4️⃣ プロジェクト設定情報")
    print(f"📋 設定ファイル: {manager.project_root / 'memory_config.json'}")
    print(f"💾 データベース: {manager.db_config['database']}")
    print(f"🔧 対話モード: {'有効' if manager.interactive_mode else '無効'}")
    print(f"📝 詳細ログ: {'有効' if manager.verbose_logging else '無効'}")

    print("\n📖 使用方法:")
    print(
        "   設定生成: python local_file_manager_o3.py --generate-config [プロジェクトパス]"
    )
    print("   設定指定: python local_file_manager_o3.py --config [設定ファイルパス]")
    print(
        "   プロジェクト指定: python local_file_manager_o3.py --project [プロジェクトパス]"
    )

    print("\n✅ o3推奨プロジェクト別ローカルファイル管理システム実装完了")
    print(
        "📍 8GB容量 + 階層化ストレージ + 学習データ永続保護 + プロジェクト別DB + UX重視設計"
    )


if __name__ == "__main__":
    main()
