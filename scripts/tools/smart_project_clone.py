#!/usr/bin/env python3
"""
Smart Project Clone System
スマートプロジェクトクローンシステム - ベストプラクティス設計
ルート配置・設定ファイル競合解決・テンプレート初期化
"""

import argparse
import datetime
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List


class ProjectCloneManager:
    """プロジェクトクローン管理システム"""

    def __init__(self):
        self.config_files = [
            ".claude",
            ".cursorignore",
            ".gitignore",
            ".pre-commit-config.yaml",
        ]
        self.template_indicators = [
            ".claudetemplate",
            "TEMPLATE.md",
            "template-config.json",
        ]

    def smart_clone(
        self, repo_url: str, target_dir: str, clone_mode: str = "root_content"
    ) -> Dict[str, Any]:
        """スマートクローン実行"""
        result = {
            "success": False,
            "target_directory": target_dir,
            "clone_mode": clone_mode,
            "actions_taken": [],
            "conflicts_resolved": [],
            "template_initialized": False,
            "configuration_status": {},
            "warnings": [],
            "errors": [],
        }

        try:
            target_path = Path(target_dir).resolve()

            # 1. 既存ディレクトリチェック
            existing_conflicts = self._check_existing_conflicts(target_path)
            if existing_conflicts["has_conflicts"]:
                result["warnings"].extend(existing_conflicts["conflicts"])

                # ユーザー確認（バックアップ提案）
                backup_needed = self._suggest_backup(existing_conflicts)
                if backup_needed:
                    backup_result = self._create_backup(target_path, existing_conflicts)
                    result["actions_taken"].append(f"Backup created: {backup_result}")

            # 2. 一時ディレクトリでクローン
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_clone_path = Path(temp_dir) / "repo_clone"

                clone_result = self._execute_clone(repo_url, str(temp_clone_path))
                if not clone_result["success"]:
                    result["errors"].append(f"Clone failed: {clone_result['error']}")
                    return result

                result["actions_taken"].append(
                    "Repository cloned to temporary directory"
                )

                # 3. テンプレート検出・処理
                template_status = self._detect_and_process_template(
                    temp_clone_path, target_path
                )
                result["template_initialized"] = template_status["is_template"]
                if template_status["is_template"]:
                    result["actions_taken"].extend(
                        template_status["initialization_actions"]
                    )

                # 4. 設定ファイル競合解決
                config_resolution = self._resolve_config_conflicts(
                    temp_clone_path, target_path
                )
                result["conflicts_resolved"] = config_resolution["resolutions"]
                result["configuration_status"] = config_resolution["final_config"]

                # 5. ルートコンテンツ配置
                if clone_mode == "root_content":
                    placement_result = self._place_root_content(
                        temp_clone_path, target_path
                    )
                elif clone_mode == "folder":
                    placement_result = self._place_as_folder(
                        temp_clone_path, target_path, repo_url
                    )
                else:
                    raise ValueError(f"Unknown clone mode: {clone_mode}")

                result["actions_taken"].extend(placement_result["actions"])

                # 6. 後処理
                post_process_result = self._post_process_setup(
                    target_path, template_status
                )
                result["actions_taken"].extend(post_process_result["actions"])

            result["success"] = True

        except Exception as e:
            result["errors"].append(f"Clone operation failed: {str(e)}")
            result["success"] = False

        return result

    def _check_existing_conflicts(self, target_path: Path) -> Dict[str, Any]:
        """既存ファイル競合チェック"""
        conflicts = {
            "has_conflicts": False,
            "conflicts": [],
            "config_files": {},
            "important_files": [],
        }

        if not target_path.exists():
            return conflicts

        # 設定ファイル競合チェック
        for config_file in self.config_files:
            existing_config = target_path / config_file
            if existing_config.exists():
                conflicts["has_conflicts"] = True
                conflicts["config_files"][config_file] = {
                    "exists": True,
                    "size": existing_config.stat().st_size,
                    "modified": datetime.datetime.fromtimestamp(
                        existing_config.stat().st_mtime
                    ).isoformat(),
                }
                conflicts["conflicts"].append(
                    f"Configuration file conflict: {config_file}"
                )

        # 重要ファイル競合チェック
        important_files = [
            "README.md",
            "package.json",
            "requirements.txt",
            "Makefile",
            "CLAUDE.md",
        ]
        for important_file in important_files:
            existing_file = target_path / important_file
            if existing_file.exists():
                conflicts["important_files"].append(important_file)
                conflicts["conflicts"].append(
                    f"Important file exists: {important_file}"
                )

        return conflicts

    def _suggest_backup(self, conflicts: Dict[str, Any]) -> bool:
        """バックアップ提案"""
        if not conflicts["has_conflicts"]:
            return False

        # 重要な設定ファイルがある場合はバックアップ推奨
        critical_configs = [".claude", "CLAUDE.md", ".cursorignore"]
        has_critical = any(
            config in conflicts["config_files"] for config in critical_configs
        )

        return has_critical or len(conflicts["important_files"]) > 0

    def _create_backup(self, target_path: Path, conflicts: Dict[str, Any]) -> str:
        """設定ファイルバックアップ作成"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = target_path / f".backup_{timestamp}"
        backup_dir.mkdir(exist_ok=True)

        backed_up_files = []

        # 設定ファイルバックアップ
        for config_file in conflicts["config_files"]:
            source = target_path / config_file
            dest = backup_dir / config_file

            if source.exists():
                if source.is_dir():
                    shutil.copytree(source, dest)
                else:
                    shutil.copy2(source, dest)
                backed_up_files.append(config_file)

        # 重要ファイルバックアップ
        for important_file in conflicts["important_files"]:
            source = target_path / important_file
            dest = backup_dir / important_file

            if source.exists():
                shutil.copy2(source, dest)
                backed_up_files.append(important_file)

        return f"{backup_dir} (files: {', '.join(backed_up_files)})"

    def _execute_clone(self, repo_url: str, target_dir: str) -> Dict[str, Any]:
        """Git クローン実行"""
        try:
            # git clone コマンド実行
            result = subprocess.run(
                ["git", "clone", repo_url, target_dir],
                capture_output=True,
                text=True,
                check=True,
            )

            return {"success": True, "stdout": result.stdout, "stderr": result.stderr}

        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Git clone failed: {e.stderr}",
                "returncode": e.returncode,
            }
        except FileNotFoundError:
            return {
                "success": False,
                "error": "Git command not found. Please install Git.",
            }

    def _detect_and_process_template(
        self, source_path: Path, target_path: Path
    ) -> Dict[str, Any]:
        """テンプレート検出・処理"""
        template_status = {
            "is_template": False,
            "template_type": None,
            "initialization_actions": [],
            "template_config": {},
        }

        # テンプレートインジケーター検出
        for indicator in self.template_indicators:
            indicator_file = source_path / indicator
            if indicator_file.exists():
                template_status["is_template"] = True
                template_status["template_type"] = indicator

                if indicator == "template-config.json":
                    try:
                        with open(indicator_file, encoding="utf-8") as f:
                            template_status["template_config"] = json.load(f)
                    except Exception:
                        pass

                break

        if template_status["is_template"]:
            # テンプレート初期化処理
            init_result = self._initialize_template(
                source_path, target_path, template_status
            )
            template_status["initialization_actions"].extend(init_result["actions"])

        return template_status

    def _initialize_template(
        self, source_path: Path, target_path: Path, template_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """テンプレート初期化"""
        init_result = {"actions": [], "replacements": {}, "generated_files": []}

        # プロジェクト名の決定
        project_name = target_path.name if target_path.name != "." else "my-project"
        init_result["replacements"]["{{project_name}}"] = project_name

        # ミス数カウンターの初期化
        init_result["replacements"]["{{mistake_count}}"] = "0"
        init_result["actions"].append("Mistake counter initialized to 0")

        # テンプレート置換処理
        template_files = self._find_template_files(source_path)
        for template_file in template_files:
            self._process_template_file(template_file, init_result["replacements"])
            init_result["actions"].append(f"Template processed: {template_file.name}")

        # 動的設定ファイル生成
        self._generate_dynamic_configs(source_path, target_path, init_result)

        return init_result

    def _find_template_files(self, source_path: Path) -> List[Path]:
        """テンプレートファイル検索"""
        template_files = []

        # テンプレート変数を含むファイル検索
        for file_path in source_path.rglob("*"):
            if file_path.is_file() and not file_path.name.startswith(".git"):
                try:
                    with open(file_path, encoding="utf-8") as f:
                        content = f.read()
                        if "{{" in content and "}}" in content:
                            template_files.append(file_path)
                except (UnicodeDecodeError, PermissionError):
                    # バイナリファイルや権限エラーをスキップ
                    continue

        return template_files

    def _process_template_file(
        self, file_path: Path, replacements: Dict[str, str]
    ) -> None:
        """テンプレートファイル処理"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # 置換実行
            for placeholder, replacement in replacements.items():
                content = content.replace(placeholder, replacement)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

        except Exception as e:
            print(f"Warning: Failed to process template file {file_path}: {e}")

    def _generate_dynamic_configs(
        self, source_path: Path, target_path: Path, init_result: Dict[str, Any]
    ) -> None:
        """動的設定ファイル生成"""
        # プロジェクト固有の.claude設定生成
        claude_config = {
            "project_name": init_result["replacements"]["{{project_name}}"],
            "template_initialized": True,
            "initialization_date": datetime.datetime.now().isoformat(),
            "mistake_counter": 0,
            "template_source": "coding-rule2-template",
        }

        claude_config_file = source_path / ".claude" / "project-config.json"
        claude_config_file.parent.mkdir(exist_ok=True)

        with open(claude_config_file, "w", encoding="utf-8") as f:
            json.dump(claude_config, f, ensure_ascii=False, indent=2)

        init_result["generated_files"].append(".claude/project-config.json")
        init_result["actions"].append("Dynamic Claude configuration generated")

    def _resolve_config_conflicts(
        self, source_path: Path, target_path: Path
    ) -> Dict[str, Any]:
        """設定ファイル競合解決"""
        resolution_result = {
            "resolutions": [],
            "final_config": {},
            "merge_strategy": "smart_merge",
        }

        for config_file in self.config_files:
            source_config = source_path / config_file
            target_config = target_path / config_file

            if source_config.exists() and target_config.exists():
                # 競合解決
                merge_result = self._merge_config_files(
                    source_config, target_config, config_file
                )
                resolution_result["resolutions"].append(merge_result)
                resolution_result["final_config"][config_file] = merge_result[
                    "strategy"
                ]
            elif source_config.exists():
                resolution_result["final_config"][config_file] = "source_only"
            elif target_config.exists():
                resolution_result["final_config"][config_file] = "target_preserved"

        return resolution_result

    def _merge_config_files(
        self, source_config: Path, target_config: Path, config_name: str
    ) -> Dict[str, Any]:
        """設定ファイルマージ"""
        merge_result = {
            "file": config_name,
            "strategy": "merged",
            "actions": [],
            "backup_created": False,
        }

        # 設定ファイル別のマージ戦略
        if config_name == ".claude":
            # .claude ディレクトリは階層マージ
            merge_result = self._merge_claude_directory(source_config, target_config)
        elif config_name == ".gitignore":
            # .gitignore は内容マージ
            merge_result = self._merge_gitignore_files(source_config, target_config)
        elif config_name == ".cursorignore":
            # .cursorignore は上書き（プロジェクト固有）
            merge_result = self._replace_config_file(
                source_config, target_config, config_name
            )
        else:
            # その他は上書き
            merge_result = self._replace_config_file(
                source_config, target_config, config_name
            )

        return merge_result

    def _merge_claude_directory(
        self, source_dir: Path, target_dir: Path
    ) -> Dict[str, Any]:
        """Claude設定ディレクトリマージ"""
        merge_result = {
            "file": ".claude",
            "strategy": "hierarchical_merge",
            "actions": [],
            "backup_created": False,
        }

        if target_dir.exists():
            # バックアップ作成
            backup_name = (
                f".claude.backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            backup_path = target_dir.parent / backup_name
            shutil.copytree(target_dir, backup_path)
            merge_result["backup_created"] = True
            merge_result["actions"].append(f"Backup created: {backup_name}")

        # 階層マージ実行
        self._copy_with_merge(source_dir, target_dir)
        merge_result["actions"].append("Claude configuration merged hierarchically")

        return merge_result

    def _merge_gitignore_files(
        self, source_file: Path, target_file: Path
    ) -> Dict[str, Any]:
        """gitignoreファイルマージ"""
        merge_result = {
            "file": ".gitignore",
            "strategy": "content_merged",
            "actions": [],
            "backup_created": False,
        }

        # 既存内容読み込み
        try:
            with open(target_file, encoding="utf-8") as f:
                target_content = {
                    line.strip()
                    for line in f
                    if line.strip() and not line.startswith("#")
                }
        except Exception:
            target_content = set()

        try:
            with open(source_file, encoding="utf-8") as f:
                source_content = {
                    line.strip()
                    for line in f
                    if line.strip() and not line.startswith("#")
                }
        except Exception:
            source_content = set()

        # マージ実行
        merged_content = target_content.union(source_content)

        with open(target_file, "w", encoding="utf-8") as f:
            f.write("# Merged .gitignore\n")
            for item in sorted(merged_content):
                f.write(f"{item}\n")

        merge_result["actions"].append(
            f"Merged {len(source_content)} new ignore patterns"
        )

        return merge_result

    def _replace_config_file(
        self, source_file: Path, target_file: Path, config_name: str
    ) -> Dict[str, Any]:
        """設定ファイル置換"""
        merge_result = {
            "file": config_name,
            "strategy": "replaced",
            "actions": [],
            "backup_created": False,
        }

        # バックアップ作成
        backup_name = (
            f"{config_name}.backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        backup_path = target_file.parent / backup_name
        shutil.copy2(target_file, backup_path)
        merge_result["backup_created"] = True
        merge_result["actions"].append(f"Backup created: {backup_name}")

        # ファイル置換
        shutil.copy2(source_file, target_file)
        merge_result["actions"].append(
            "Configuration file replaced with template version"
        )

        return merge_result

    def _copy_with_merge(self, source_dir: Path, target_dir: Path) -> None:
        """マージ付きコピー"""
        target_dir.mkdir(exist_ok=True)

        for item in source_dir.iterdir():
            target_item = target_dir / item.name

            if item.is_dir():
                self._copy_with_merge(item, target_item)
            else:
                # ファイルは上書き（JSON設定は特別処理）
                if item.suffix == ".json" and target_item.exists():
                    self._merge_json_configs(item, target_item)
                else:
                    shutil.copy2(item, target_item)

    def _merge_json_configs(self, source_file: Path, target_file: Path) -> None:
        """JSON設定ファイルマージ"""
        try:
            with open(target_file, encoding="utf-8") as f:
                target_config = json.load(f)
        except Exception:
            target_config = {}

        try:
            with open(source_file, encoding="utf-8") as f:
                source_config = json.load(f)
        except Exception:
            source_config = {}

        # 深いマージ実行
        merged_config = self._deep_merge_dict(target_config, source_config)

        with open(target_file, "w", encoding="utf-8") as f:
            json.dump(merged_config, f, ensure_ascii=False, indent=2)

    def _deep_merge_dict(self, target: Dict, source: Dict) -> Dict:
        """辞書の深いマージ"""
        result = target.copy()

        for key, value in source.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._deep_merge_dict(result[key], value)
            else:
                result[key] = value

        return result

    def _place_root_content(
        self, source_path: Path, target_path: Path
    ) -> Dict[str, Any]:
        """ルートコンテンツ配置"""
        placement_result = {"actions": [], "files_copied": 0, "directories_created": 0}

        target_path.mkdir(parents=True, exist_ok=True)

        for item in source_path.iterdir():
            if item.name == ".git":
                continue  # .gitディレクトリはスキップ

            target_item = target_path / item.name

            try:
                if item.is_dir():
                    if target_item.exists():
                        # ディレクトリマージ
                        self._copy_with_merge(item, target_item)
                        placement_result["actions"].append(
                            f"Merged directory: {item.name}"
                        )
                    else:
                        shutil.copytree(item, target_item)
                        placement_result["actions"].append(
                            f"Copied directory: {item.name}"
                        )
                    placement_result["directories_created"] += 1
                else:
                    shutil.copy2(item, target_item)
                    placement_result["actions"].append(f"Copied file: {item.name}")
                    placement_result["files_copied"] += 1

            except Exception as e:
                placement_result["actions"].append(
                    f"Failed to copy {item.name}: {str(e)}"
                )

        return placement_result

    def _place_as_folder(
        self, source_path: Path, target_path: Path, repo_url: str
    ) -> Dict[str, Any]:
        """フォルダとして配置"""
        placement_result = {"actions": [], "folder_name": "", "files_copied": 0}

        # リポジトリ名から適切なフォルダ名を決定
        repo_name = repo_url.split("/")[-1].replace(".git", "")
        folder_name = repo_name

        target_folder = target_path / folder_name

        shutil.copytree(source_path, target_folder)
        placement_result["folder_name"] = folder_name
        placement_result["actions"].append(
            f"Repository placed in folder: {folder_name}"
        )

        return placement_result

    def _post_process_setup(
        self, target_path: Path, template_status: Dict[str, Any]
    ) -> Dict[str, Any]:
        """後処理セットアップ"""
        post_result = {
            "actions": [],
            "hooks_installed": False,
            "dependencies_checked": False,
        }

        # Makefileが存在する場合の初期化コマンド実行
        makefile = target_path / "Makefile"
        if makefile.exists():
            try:
                # 基本セットアップコマンド実行
                result = subprocess.run(
                    ["make", "help"],
                    cwd=target_path,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if result.returncode == 0:
                    post_result["actions"].append("Makefile help confirmed")
            except Exception:
                post_result["actions"].append("Makefile setup skipped (command failed)")

        # Git初期化（テンプレートの場合）
        if template_status["is_template"]:
            try:
                subprocess.run(["git", "init"], cwd=target_path, check=True)
                post_result["actions"].append("Git repository initialized")
            except Exception:
                post_result["actions"].append("Git initialization failed")

        return post_result


def main():
    """メイン実行"""
    parser = argparse.ArgumentParser(description="Smart Project Clone System")
    parser.add_argument("repo_url", help="Repository URL to clone")
    parser.add_argument("target_dir", help="Target directory")
    parser.add_argument(
        "--mode",
        choices=["root_content", "folder"],
        default="root_content",
        help="Clone mode",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be done"
    )

    args = parser.parse_args()

    clone_manager = ProjectCloneManager()

    if args.dry_run:
        print(
            f"🔍 Dry run: Would clone {args.repo_url} to {args.target_dir} in {args.mode} mode"
        )
        return

    print(f"🚀 Smart cloning {args.repo_url} to {args.target_dir}")

    result = clone_manager.smart_clone(args.repo_url, args.target_dir, args.mode)

    print("\n📊 Clone Result:")
    print(f"Success: {'✅' if result['success'] else '❌'}")
    print(f"Template: {'✅' if result['template_initialized'] else '❌'}")
    print(f"Conflicts resolved: {len(result['conflicts_resolved'])}")

    if result["actions_taken"]:
        print("\n🔧 Actions taken:")
        for action in result["actions_taken"]:
            print(f"  - {action}")

    if result["warnings"]:
        print("\n⚠️ Warnings:")
        for warning in result["warnings"]:
            print(f"  - {warning}")

    if result["errors"]:
        print("\n❌ Errors:")
        for error in result["errors"]:
            print(f"  - {error}")


if __name__ == "__main__":
    main()
