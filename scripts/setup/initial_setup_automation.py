#!/usr/bin/env python3
"""
🚀 Initial Setup Automation - 初期設定自動化システム
=================================================

0からプレジデント立ち上げ時の初期設定自動化
APIキー、DB設定、環境構築をスムーズに進行
"""

import getpass
import json
import subprocess
import sys
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


class InitialSetupAutomation:
    """初期設定自動化システム"""

    def __init__(self):
        self.project_root = Path("/Users/dd/Desktop/1_dev/coding-rule2")
        self.config_dir = self.project_root / "config"
        self.runtime_dir = self.project_root / "runtime"
        self.venv_path = self.project_root / ".venv"

        # 設定ファイルパス
        self.env_file = self.project_root / ".env"
        self.db_config_file = self.config_dir / "database.json"
        self.api_config_file = self.config_dir / "api_keys.json"
        self.system_config_file = self.config_dir / "system_config.json"

        # 設定テンプレート
        self.setup_templates = {
            "database": {
                "host": "localhost",
                "port": 5432,
                "database": "coding_rule2",
                "username": "postgres",
                "password": "",
                "ssl_mode": "prefer",
                "connection_timeout": 30,
            },
            "api_keys": {
                "gemini_api_key": "",
                "openai_api_key": "",
                "anthropic_api_key": "",
                "github_token": "",
                "slack_webhook": "",
            },
            "system_config": {
                "president_mode": True,
                "auto_role_assignment": True,
                "thinking_enforcer": True,
                "fake_data_prevention": True,
                "language_enforcement": True,
                "dashboard_mode": "dynamic",
                "worker_count": 4,
                "max_authority_level": 10,
                "session_persistence": True,
            },
        }

        # 必須ディレクトリ
        self.required_dirs = [
            "config",
            "runtime/logs",
            "runtime/sessions",
            "runtime/backups",
            "runtime/temp",
            "src/memory/core",
            "src/memory/core/session-records",
            "scripts/hooks",
        ]

        # 必須ファイル
        self.required_files = [
            "requirements.txt",
            "CLAUDE.md",
            "startup_checklist.md",
            "Index.md",
            "src/agents/executive/roles/president.md",
        ]

        self.setup_progress = {
            "directory_structure": False,
            "virtual_environment": False,
            "dependencies": False,
            "database_setup": False,
            "api_configuration": False,
            "system_configuration": False,
            "president_initialization": False,
            "validation": False,
        }

    def run_interactive_setup(self) -> bool:
        """インタラクティブセットアップ実行"""
        print("🚀 Initial Setup Automation - 初期設定自動化")
        print("=" * 50)
        print("プレジデント立ち上げのための初期設定を開始します。")
        print("以下の手順で進行します：")
        print()

        # セットアップステップ一覧表示
        steps = [
            "1. ディレクトリ構造作成",
            "2. 仮想環境構築",
            "3. 依存関係インストール",
            "4. データベース設定",
            "5. API設定",
            "6. システム設定",
            "7. プレジデント初期化",
            "8. 設定検証",
        ]

        for step in steps:
            print(f"  {step}")

        print()
        confirm = input("セットアップを開始しますか？ (y/n): ").lower().strip()
        if confirm != "y":
            print("セットアップをキャンセルしました。")
            return False

        print()

        # セットアップ実行
        try:
            self._setup_directory_structure()
            self._setup_virtual_environment()
            self._install_dependencies()
            self._setup_database_configuration()
            self._setup_api_configuration()
            self._setup_system_configuration()
            self._initialize_president()
            self._validate_setup()

            print("\n🎉 初期設定が完了しました！")
            print("プレジデントシステムの準備が整いました。")
            print("\n次の手順:")
            print("  1. make declare-president  # プレジデント宣言")
            print("  2. make run-president      # プレジデント起動")
            print("  3. make ui-dashboard       # ダッシュボード起動")

            return True

        except Exception as e:
            print(f"\n❌ セットアップエラー: {e}")
            print("エラーが発生しました。手動で設定を確認してください。")
            return False

    def _setup_directory_structure(self):
        """ディレクトリ構造作成"""
        print("📁 ディレクトリ構造作成中...")

        for dir_path in self.required_dirs:
            full_path = self.project_root / dir_path
            full_path.mkdir(parents=True, exist_ok=True)

            # .gitkeep作成
            gitkeep_path = full_path / ".gitkeep"
            if not gitkeep_path.exists():
                gitkeep_path.touch()

        self.setup_progress["directory_structure"] = True
        print("✅ ディレクトリ構造作成完了")

    def _setup_virtual_environment(self):
        """仮想環境構築"""
        print("🐍 仮想環境構築中...")

        if not self.venv_path.exists():
            result = subprocess.run(
                [sys.executable, "-m", "venv", str(self.venv_path)],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                raise Exception(f"仮想環境作成エラー: {result.stderr}")

        self.setup_progress["virtual_environment"] = True
        print("✅ 仮想環境構築完了")

    def _install_dependencies(self):
        """依存関係インストール"""
        print("📦 依存関係インストール中...")

        pip_path = self.venv_path / "bin" / "pip"
        if not pip_path.exists():
            pip_path = self.venv_path / "Scripts" / "pip.exe"  # Windows対応

        if self.project_root.joinpath("requirements.txt").exists():
            result = subprocess.run(
                [str(pip_path), "install", "-r", "requirements.txt"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                raise Exception(f"依存関係インストールエラー: {result.stderr}")

        self.setup_progress["dependencies"] = True
        print("✅ 依存関係インストール完了")

    def _setup_database_configuration(self):
        """データベース設定"""
        print("🗄️  データベース設定中...")

        # データベース設定入力
        print("\nデータベース設定を入力してください:")
        db_config = self.setup_templates["database"].copy()

        # 対話式入力
        db_config["host"] = (
            input(f"ホスト [{db_config['host']}]: ") or db_config["host"]
        )
        db_config["port"] = int(
            input(f"ポート [{db_config['port']}]: ") or db_config["port"]
        )
        db_config["database"] = (
            input(f"データベース名 [{db_config['database']}]: ")
            or db_config["database"]
        )
        db_config["username"] = (
            input(f"ユーザー名 [{db_config['username']}]: ") or db_config["username"]
        )
        db_config["password"] = getpass.getpass("パスワード: ") or ""

        # 設定ファイル保存
        with open(self.db_config_file, "w", encoding="utf-8") as f:
            json.dump(db_config, f, indent=2, ensure_ascii=False)

        # 接続文字列作成
        connection_string = self._create_connection_string(db_config)

        # 環境変数設定
        self._update_env_file("DATABASE_URL", connection_string)

        self.setup_progress["database_setup"] = True
        print("✅ データベース設定完了")

    def _setup_api_configuration(self):
        """API設定"""
        print("🔑 API設定中...")

        print("\nAPI設定を入力してください（空白でスキップ可能）:")
        api_config = self.setup_templates["api_keys"].copy()

        # 対話式入力
        api_config["gemini_api_key"] = input("Gemini API Key: ").strip() or ""
        api_config["openai_api_key"] = input("OpenAI API Key: ").strip() or ""
        api_config["anthropic_api_key"] = input("Anthropic API Key: ").strip() or ""
        api_config["github_token"] = input("GitHub Token: ").strip() or ""
        api_config["slack_webhook"] = input("Slack Webhook URL: ").strip() or ""

        # 設定ファイル保存
        with open(self.api_config_file, "w", encoding="utf-8") as f:
            json.dump(api_config, f, indent=2, ensure_ascii=False)

        # 環境変数設定
        for key, value in api_config.items():
            if value:
                env_key = key.upper()
                self._update_env_file(env_key, value)

        self.setup_progress["api_configuration"] = True
        print("✅ API設定完了")

    def _setup_system_configuration(self):
        """システム設定"""
        print("⚙️  システム設定中...")

        system_config = self.setup_templates["system_config"].copy()

        # 基本設定確認
        print("\nシステム設定を確認してください:")
        print(f"プレジデントモード: {system_config['president_mode']}")
        print(f"自動役職配置: {system_config['auto_role_assignment']}")
        print(f"思考強制システム: {system_config['thinking_enforcer']}")
        print(f"偽装データ防止: {system_config['fake_data_prevention']}")
        print(f"言語強制: {system_config['language_enforcement']}")
        print(f"ワーカー数: {system_config['worker_count']}")

        # 設定ファイル保存
        with open(self.system_config_file, "w", encoding="utf-8") as f:
            json.dump(system_config, f, indent=2, ensure_ascii=False)

        self.setup_progress["system_configuration"] = True
        print("✅ システム設定完了")

    def _initialize_president(self):
        """プレジデント初期化"""
        print("👑 プレジデント初期化中...")

        # 必須ファイル確認・作成
        for file_path in self.required_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                print(f"  作成中: {file_path}")
                self._create_required_file(full_path)

        # セッション記録初期化
        session_file = self.runtime_dir / "sessions" / "initial_session.json"
        session_data = {
            "session_id": f"setup_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "created_at": datetime.now().isoformat(),
            "setup_completed": True,
            "president_initialized": True,
            "system_status": "ready",
        }

        with open(session_file, "w", encoding="utf-8") as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)

        self.setup_progress["president_initialization"] = True
        print("✅ プレジデント初期化完了")

    def _validate_setup(self):
        """設定検証"""
        print("🔍 設定検証中...")

        validation_results = {
            "directories": all(
                (self.project_root / dir_path).exists()
                for dir_path in self.required_dirs
            ),
            "virtual_environment": self.venv_path.exists(),
            "config_files": all(
                [
                    self.db_config_file.exists(),
                    self.api_config_file.exists(),
                    self.system_config_file.exists(),
                ]
            ),
            "environment_file": self.env_file.exists(),
            "required_files": all(
                (self.project_root / file_path).exists()
                for file_path in self.required_files
            ),
        }

        all_valid = all(validation_results.values())

        if all_valid:
            print("✅ 設定検証完了 - すべて正常")
        else:
            print("⚠️  設定検証で問題が検出されました:")
            for check, result in validation_results.items():
                status = "✅" if result else "❌"
                print(f"  {status} {check}")

        self.setup_progress["validation"] = all_valid

        if not all_valid:
            raise Exception("設定検証に失敗しました")

    def _create_connection_string(self, config: Dict[str, Any]) -> str:
        """データベース接続文字列作成"""
        password = urllib.parse.quote(config["password"]) if config["password"] else ""
        user_part = f"{config['username']}:{password}@" if config["username"] else ""

        return f"postgresql://{user_part}{config['host']}:{config['port']}/{config['database']}"

    def _update_env_file(self, key: str, value: str):
        """環境変数ファイル更新"""
        env_vars = {}

        # 既存の環境変数読み込み
        if self.env_file.exists():
            with open(self.env_file, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        if "=" in line:
                            k, v = line.split("=", 1)
                            env_vars[k.strip()] = v.strip()

        # 新しい値設定
        env_vars[key] = value

        # ファイル書き込み
        with open(self.env_file, "w", encoding="utf-8") as f:
            f.write("# Environment variables for coding-rule2\n")
            f.write(f"# Generated: {datetime.now().isoformat()}\n\n")

            for k, v in env_vars.items():
                f.write(f"{k}={v}\n")

    def _create_required_file(self, file_path: Path):
        """必須ファイル作成"""
        file_path.parent.mkdir(parents=True, exist_ok=True)

        if file_path.name == "startup_checklist.md":
            content = """# Startup Checklist

## 必須確認事項
- [ ] PRESIDENT宣言完了
- [ ] 仮想環境アクティベート
- [ ] データベース接続確認
- [ ] API設定確認
- [ ] ダッシュボード起動可能

## 初期化完了
✅ 自動セットアップ完了
"""
        elif file_path.name == "Index.md":
            content = """# Project Index

## 初期設定完了
自動セットアップシステムにより初期化完了

## 次のステップ
1. make declare-president
2. make run-president
3. make ui-dashboard
"""
        else:
            content = f"# {file_path.name}\n\n初期設定時に自動生成されました。\n"

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

    def get_setup_status(self) -> Dict[str, Any]:
        """セットアップ状況取得"""
        return {
            "progress": self.setup_progress,
            "completion_rate": sum(self.setup_progress.values())
            / len(self.setup_progress)
            * 100,
            "next_steps": self._get_next_steps(),
        }

    def _get_next_steps(self) -> List[str]:
        """次のステップ取得"""
        if all(self.setup_progress.values()):
            return ["make declare-president", "make run-president", "make ui-dashboard"]
        else:
            incomplete = [
                step for step, completed in self.setup_progress.items() if not completed
            ]
            return [f"完了が必要: {step}" for step in incomplete]


def main():
    """メイン実行"""
    setup = InitialSetupAutomation()

    if len(sys.argv) > 1 and sys.argv[1] == "status":
        # 状況確認
        status = setup.get_setup_status()
        print(f"Setup completion: {status['completion_rate']:.1f}%")
        print("Next steps:")
        for step in status["next_steps"]:
            print(f"  - {step}")
    else:
        # インタラクティブセットアップ
        setup.run_interactive_setup()


if __name__ == "__main__":
    main()
