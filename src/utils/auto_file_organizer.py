#!/usr/bin/env python3
"""
📁 Auto File Organizer
======================
自動ファイル整理システム
新規ファイルの適切な配置を強制
"""

import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


class AutoFileOrganizer:
    def __init__(self, project_root: str = "/Users/dd/Desktop/1_dev/coding-rule2"):
        self.project_root = Path(project_root)

        # ファイル分類ルール
        self.organization_rules = {
            # ドキュメント
            ".md": "docs/",
            ".rst": "docs/",
            ".txt": "docs/",
            # 設定ファイル
            ".json": "config/",
            ".yaml": "config/",
            ".yml": "config/",
            ".toml": "config/",
            ".cfg": "config/",
            ".conf": "config/",
            ".ini": "config/",
            # ログファイル
            ".log": "logs/",
            ".out": "logs/",
            # スクリプト
            ".sh": "scripts/",
            ".bat": "scripts/",
            ".ps1": "scripts/",
            # テンプレート
            ".template": "templates/",
            ".sample": "templates/",
            ".example": "templates/",
            # データ
            ".csv": "data/",
            ".pkl": "data/",
            ".dat": "data/",
            # 一時ファイル
            ".tmp": "tmp/",
            ".temp": "tmp/",
            ".cache": "tmp/",
            ".backup": "tmp/backup/",
            # Python関連
            ".py": "src/",
            ".pyi": "src/",
            ".pyc": "tmp/cache/",
            "__pycache__": "tmp/cache/",
        }

        # 重要ファイル（移動しない）
        self.protected_files = {
            "README.md",
            "LICENSE",
            "CLAUDE.md",
            "requirements.txt",
            "setup.py",
            "pyproject.toml",
            "Makefile",
            ".gitignore",
            ".env",
            ".env.example",
        }

        # 保護ディレクトリ（移動しない）
        self.protected_dirs = {
            ".git",
            ".github",
            "venv",
            ".venv",
            "node_modules",
            "__pycache__",
            ".pytest_cache",
        }

    def should_organize_file(self, file_path: Path) -> bool:
        """ファイルを整理すべきかチェック"""

        # 保護ファイルチェック
        if file_path.name in self.protected_files:
            return False

        # 保護ディレクトリチェック
        for part in file_path.parts:
            if part in self.protected_dirs:
                return False

        # 既に適切な場所にあるかチェック
        suffix = file_path.suffix.lower()
        if suffix in self.organization_rules:
            target_dir = self.organization_rules[suffix]
            if str(file_path.parent).endswith(target_dir.rstrip("/")):
                return False

        return True

    def get_target_directory(self, file_path: Path) -> Path:
        """ファイルの適切な配置先を取得"""

        suffix = file_path.suffix.lower()

        # 拡張子ベースの分類
        if suffix in self.organization_rules:
            target_dir = self.organization_rules[suffix]
            return self.project_root / target_dir

        # 特殊ケース
        if file_path.name.startswith("."):
            return self.project_root / "config/"

        # デフォルト
        return self.project_root / "misc/"

    def organize_file(self, file_path: Path, dry_run: bool = True) -> Tuple[bool, str]:
        """ファイルを適切な場所に移動"""

        try:
            if not self.should_organize_file(file_path):
                return False, f"保護ファイル: {file_path.name}"

            target_dir = self.get_target_directory(file_path)
            target_path = target_dir / file_path.name

            # 同名ファイルの処理
            if target_path.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                name_parts = file_path.name.split(".")
                if len(name_parts) > 1:
                    new_name = f"{name_parts[0]}_{timestamp}.{name_parts[1]}"
                else:
                    new_name = f"{file_path.name}_{timestamp}"
                target_path = target_dir / new_name

            if dry_run:
                return True, f"移動予定: {file_path} → {target_path}"

            # 実際の移動
            target_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(file_path), str(target_path))

            return True, f"移動完了: {file_path} → {target_path}"

        except Exception as e:
            return False, f"エラー: {file_path} - {str(e)}"

    def organize_root_directory(self, dry_run: bool = True) -> Dict:
        """ルートディレクトリを整理"""

        results = {"organized": [], "skipped": [], "errors": []}

        # ルートディレクトリのファイルを処理
        for file_path in self.project_root.iterdir():
            if file_path.is_file():
                success, message = self.organize_file(file_path, dry_run)

                if success:
                    if "移動" in message:
                        results["organized"].append(message)
                    else:
                        results["skipped"].append(message)
                else:
                    results["errors"].append(message)

        return results

    def cleanup_logs(self, days: int = 7, dry_run: bool = True) -> List[str]:
        """古いログファイルをクリーンアップ"""

        cleaned = []
        log_dirs = [
            self.project_root / "logs",
            self.project_root / "runtime" / "logs",
            self.project_root / "src" / "conductor" / "runtime" / "logs",
        ]

        for log_dir in log_dirs:
            if log_dir.exists():
                for log_file in log_dir.rglob("*.log"):
                    # ファイルの更新日をチェック
                    file_age = (
                        datetime.now()
                        - datetime.fromtimestamp(log_file.stat().st_mtime)
                    ).days

                    if file_age > days:
                        if dry_run:
                            cleaned.append(f"削除予定: {log_file}")
                        else:
                            log_file.unlink()
                            cleaned.append(f"削除完了: {log_file}")

        return cleaned

    def generate_organization_report(self, dry_run: bool = True) -> str:
        """整理レポート生成"""

        print("📁 ファイル整理システム開始")
        print("=" * 50)

        # ルートディレクトリ整理
        org_results = self.organize_root_directory(dry_run)

        # ログクリーンアップ
        log_results = self.cleanup_logs(dry_run=dry_run)

        # レポート生成
        report = f"""
# 📁 ファイル整理レポート

## 実行モード
{"🔍 ドライラン（実際の変更なし）" if dry_run else "🔧 実行モード（実際に変更）"}

## ルートディレクトリ整理結果

### 整理されたファイル ({len(org_results["organized"])}件)
"""

        for item in org_results["organized"]:
            report += f"- {item}\n"

        report += f"""
### スキップされたファイル ({len(org_results["skipped"])}件)
"""

        for item in org_results["skipped"]:
            report += f"- {item}\n"

        if org_results["errors"]:
            report += f"""
### エラー ({len(org_results["errors"])}件)
"""
            for item in org_results["errors"]:
                report += f"- {item}\n"

        report += f"""
## ログクリーンアップ結果 ({len(log_results)}件)
"""

        for item in log_results:
            report += f"- {item}\n"

        report += f"""
## 総合結果
- 整理対象: {len(org_results["organized"])}件
- 保護ファイル: {len(org_results["skipped"])}件
- クリーンアップ: {len(log_results)}件
- エラー: {len(org_results["errors"])}件

## 推奨次回アクション
1. ドライランで結果を確認
2. 実行モードで実際に整理
3. 定期的なクリーンアップの自動化
"""

        return report


def main():
    """メイン実行"""

    organizer = AutoFileOrganizer()

    # ドライラン実行
    report = organizer.generate_organization_report(dry_run=True)
    print(report)

    # レポート保存
    report_path = organizer.project_root / "logs" / "file_organization_report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n📊 詳細レポート: {report_path}")


if __name__ == "__main__":
    main()
