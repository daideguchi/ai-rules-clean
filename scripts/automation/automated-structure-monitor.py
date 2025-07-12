#!/usr/bin/env python3
"""
自動化された継続的整理システム
プロジェクトファイル構造の8個制限を自動監視・維持
"""

import argparse
import json
import logging
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("runtime/logs/structure-monitor.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class ProjectStructureMonitor:
    """プロジェクト構造監視・自動整理システム"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.max_root_dirs = 8
        self.allowed_roots = {
            "src",
            "docs",
            "config",
            "runtime",
            "ops",
            "assets",
            "scripts",
            "tests",
        }
        self.system_dirs = {".git", ".dev", "node_modules", "__pycache__"}
        self.config_file = self.project_root / "config" / "structure-monitor.json"

        # 自動分類ルール
        self.auto_categorization_rules = {
            "src": {
                "extensions": [".py", ".js", ".sh", ".ts", ".jsx", ".tsx"],
                "patterns": ["ai/", "hooks/", "integrations/", "memory/"],
                "keywords": ["algorithm", "logic", "processing", "core"],
            },
            "docs": {
                "extensions": [".md", ".rst", ".txt"],
                "patterns": ["README", "documentation", "guide", "manual"],
                "keywords": ["document", "guide", "instruction", "help"],
            },
            "config": {
                "extensions": [".json", ".yaml", ".yml", ".toml", ".conf", ".cfg"],
                "patterns": ["config", "settings", "env"],
                "keywords": ["configuration", "settings", "environment"],
            },
            "runtime": {
                "extensions": [".log", ".pid", ".lock"],
                "patterns": ["logs/", "temp/", "cache/", "session"],
                "keywords": ["runtime", "temporary", "cache", "session"],
            },
            "ops": {
                "extensions": [".tf", ".yaml", ".yml"],
                "patterns": ["kubernetes/", "terraform/", "docker", "k8s/"],
                "keywords": ["infrastructure", "deployment", "kubernetes", "terraform"],
            },
            "assets": {
                "extensions": [
                    ".png",
                    ".jpg",
                    ".jpeg",
                    ".gif",
                    ".svg",
                    ".css",
                    ".html",
                ],
                "patterns": ["assets/", "static/", "public/", "media/"],
                "keywords": ["asset", "media", "static", "resource"],
            },
            "scripts": {
                "extensions": [".sh", ".py", ".js"],
                "patterns": ["scripts/", "bin/", "tools/"],
                "keywords": ["script", "automation", "tool", "utility"],
            },
            "tests": {
                "extensions": [".py", ".js", ".sh"],
                "patterns": ["test", "spec", "check"],
                "keywords": ["test", "spec", "validation", "check"],
            },
        }

    def load_config(self) -> Dict:
        """設定ファイルの読み込み"""
        try:
            if self.config_file.exists():
                with open(self.config_file) as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Config loading error: {e}")
            return {}

    def save_config(self, config: Dict):
        """設定ファイルの保存"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            logger.error(f"Config saving error: {e}")

    def get_root_directories(self) -> Set[str]:
        """ルートディレクトリの取得"""
        root_dirs = set()
        for item in self.project_root.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                root_dirs.add(item.name)
        return root_dirs - self.system_dirs

    def validate_structure(self) -> Dict:
        """構造検証"""
        root_dirs = self.get_root_directories()

        validation_result = {
            "valid": True,
            "total_dirs": len(root_dirs),
            "max_dirs": self.max_root_dirs,
            "directories": sorted(root_dirs),
            "violations": [],
            "warnings": [],
        }

        # 8個制限チェック
        if len(root_dirs) > self.max_root_dirs:
            validation_result["valid"] = False
            validation_result["violations"].append(
                f"Too many root directories: {len(root_dirs)}/{self.max_root_dirs}"
            )

        # 許可されたディレクトリチェック
        invalid_dirs = root_dirs - self.allowed_roots
        if invalid_dirs:
            validation_result["warnings"].append(
                f"Non-standard directories found: {sorted(invalid_dirs)}"
            )

        return validation_result

    def categorize_file(self, file_path: Path) -> str:
        """ファイルの自動分類"""
        file_path_str = str(file_path).lower()
        file_ext = file_path.suffix.lower()

        scores = {}

        for category, rules in self.auto_categorization_rules.items():
            score = 0

            # 拡張子チェック
            if file_ext in rules["extensions"]:
                score += 10

            # パターンチェック
            for pattern in rules["patterns"]:
                if pattern.lower() in file_path_str:
                    score += 5

            # キーワードチェック
            for keyword in rules["keywords"]:
                if keyword.lower() in file_path_str:
                    score += 3

            if score > 0:
                scores[category] = score

        # 最高スコアのカテゴリを返す
        if scores:
            return max(scores, key=scores.get)

        # デフォルトはsrc
        return "src"

    def suggest_moves(self) -> List[Dict]:
        """移動提案の生成"""
        suggestions = []
        root_dirs = self.get_root_directories()

        # 8個制限を超えた場合の移動提案
        if len(root_dirs) > self.max_root_dirs:
            excess_dirs = root_dirs - self.allowed_roots

            for dir_name in excess_dirs:
                dir_path = self.project_root / dir_name
                if not dir_path.exists():
                    continue

                # ディレクトリ内容を分析
                files = list(dir_path.rglob("*"))
                if not files:
                    continue

                # 最も適切なカテゴリを決定
                category_votes = {}
                for file_path in files:
                    if file_path.is_file():
                        category = self.categorize_file(file_path)
                        category_votes[category] = category_votes.get(category, 0) + 1

                if category_votes:
                    best_category = max(category_votes, key=category_votes.get)
                    suggestions.append(
                        {
                            "source": str(dir_path),
                            "target": str(self.project_root / best_category / dir_name),
                            "reason": f"Auto-categorized as {best_category}",
                            "confidence": category_votes[best_category] / len(files),
                        }
                    )

        return suggestions

    def execute_move(self, suggestion: Dict, dry_run: bool = True) -> bool:
        """移動の実行"""
        source = Path(suggestion["source"])
        target = Path(suggestion["target"])

        if dry_run:
            logger.info(f"DRY RUN: Would move {source} → {target}")
            return True

        try:
            # Git移動を使用（履歴保持）
            target.parent.mkdir(parents=True, exist_ok=True)

            # Gitが管理しているかチェック
            result = subprocess.run(
                ["git", "ls-files", str(source)],
                capture_output=True,
                cwd=self.project_root,
            )

            if result.returncode == 0 and result.stdout.strip():
                # Git管理下の場合はgit mv使用
                subprocess.run(
                    ["git", "mv", str(source), str(target)],
                    cwd=self.project_root,
                    check=True,
                )
                logger.info(f"Git moved: {source} → {target}")
            else:
                # 通常の移動
                shutil.move(str(source), str(target))
                logger.info(f"Moved: {source} → {target}")

            return True

        except Exception as e:
            logger.error(f"Move failed: {source} → {target}, Error: {e}")
            return False

    def generate_report(self, validation: Dict, suggestions: List[Dict]) -> str:
        """レポート生成"""
        report = f"""# 構造監視レポート

## 実行日時
{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 現在の構造
- ルートディレクトリ数: {validation["total_dirs"]}/{validation["max_dirs"]}
- ディレクトリ: {", ".join(validation["directories"])}
- 状態: {"✓ OK" if validation["valid"] else "✗ VIOLATION"}

## 検出された問題
"""

        if validation["violations"]:
            for violation in validation["violations"]:
                report += f"- ❌ {violation}\n"

        if validation["warnings"]:
            for warning in validation["warnings"]:
                report += f"- ⚠️ {warning}\n"

        if not validation["violations"] and not validation["warnings"]:
            report += "- なし\n"

        report += "\n## 移動提案\n"

        if suggestions:
            for i, suggestion in enumerate(suggestions, 1):
                report += f"""
### 提案 {i}
- **移動元**: {suggestion["source"]}
- **移動先**: {suggestion["target"]}
- **理由**: {suggestion["reason"]}
- **信頼度**: {suggestion["confidence"]:.2f}
"""
        else:
            report += "- 移動提案なし\n"

        return report

    def run_monitoring_cycle(self, auto_fix: bool = False, dry_run: bool = True):
        """監視サイクルの実行"""
        logger.info("Starting structure monitoring cycle...")

        # 構造検証
        validation = self.validate_structure()

        # 移動提案生成
        suggestions = self.suggest_moves()

        # レポート生成
        report = self.generate_report(validation, suggestions)

        # レポート保存
        report_file = (
            self.project_root
            / "runtime"
            / "reports"
            / f"structure-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
        )
        report_file.parent.mkdir(parents=True, exist_ok=True)

        with open(report_file, "w") as f:
            f.write(report)

        logger.info(f"Report saved: {report_file}")

        # 自動修正の実行
        if auto_fix and suggestions:
            logger.info("Executing auto-fix...")

            for suggestion in suggestions:
                if suggestion["confidence"] > 0.7:  # 高信頼度のみ実行
                    success = self.execute_move(suggestion, dry_run=dry_run)
                    if success and not dry_run:
                        # Git commit
                        subprocess.run(["git", "add", "-A"], cwd=self.project_root)

                        subprocess.run(
                            [
                                "git",
                                "commit",
                                "-m",
                                f"refactor: auto-organize {suggestion['source']} → {suggestion['target']}",
                            ],
                            cwd=self.project_root,
                        )

        # 結果返却
        return {
            "validation": validation,
            "suggestions": suggestions,
            "report_file": str(report_file),
        }


def main():
    """メイン実行"""
    parser = argparse.ArgumentParser(description="Project Structure Monitor")
    parser.add_argument(
        "--auto-fix", action="store_true", help="Auto-fix structure violations"
    )
    parser.add_argument(
        "--dry-run", action="store_true", default=True, help="Dry run mode"
    )
    parser.add_argument(
        "--no-dry-run",
        dest="dry_run",
        action="store_false",
        help="Execute actual changes",
    )
    parser.add_argument("--project-root", default=".", help="Project root directory")

    args = parser.parse_args()

    # 監視システム初期化
    monitor = ProjectStructureMonitor(args.project_root)

    # 監視サイクル実行
    result = monitor.run_monitoring_cycle(auto_fix=args.auto_fix, dry_run=args.dry_run)

    # 結果表示
    if result["validation"]["valid"]:
        print("✓ Project structure is valid")
        sys.exit(0)
    else:
        print("✗ Project structure violations detected")
        print(f"Report: {result['report_file']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
