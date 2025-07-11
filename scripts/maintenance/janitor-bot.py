#!/usr/bin/env python3
"""
Janitor Bot - 自律的プロジェクト整理システム
o3とGemini戦略に基づく継続的クリーニング
"""

import json
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


class JanitorBot:
    """自律的プロジェクト整理Bot"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.max_root_dirs = 8
        self.rules_file = self.project_root / "docs" / "rules" / "janitor-rules.yaml"
        self.log_file = self.project_root / "runtime" / "logs" / "janitor-bot.log"

        # ログディレクトリ作成
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def log(self, message: str, level: str = "INFO"):
        """ログメッセージ出力"""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] {level}: {message}"
        print(log_entry)

        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")

    def check_root_directory_count(self) -> Dict[str, Any]:
        """ルートディレクトリ数チェック（o3戦略）"""
        dirs = [
            d
            for d in self.project_root.iterdir()
            if d.is_dir() and not d.name.startswith(".")
        ]

        count = len(dirs)
        violation = count > self.max_root_dirs

        result = {
            "check": "root_directory_count",
            "count": count,
            "max_allowed": self.max_root_dirs,
            "violation": violation,
            "directories": [d.name for d in dirs],
        }

        if violation:
            self.log(
                f"❌ ルートディレクトリ違反: {count}個 (上限{self.max_root_dirs})",
                "WARNING",
            )
        else:
            self.log(f"✅ ルートディレクトリ数OK: {count}個", "INFO")

        return result

    def detect_stray_files(self) -> List[Dict[str, Any]]:
        """不適切な場所にあるファイル検出（Gemini戦略）"""
        stray_files = []

        # ルートレベルのファイルをチェック
        for item in self.project_root.iterdir():
            if item.is_file() and not self._is_allowed_root_file(item.name):
                stray_files.append(
                    {
                        "type": "misplaced_file",
                        "path": str(item),
                        "suggested_location": self._suggest_location(item),
                        "reason": "ルートレベルに配置すべきでないファイル",
                    }
                )

        # 一時ファイル検出
        temp_patterns = ["*.tmp", "*.bak", "*.backup", "*~", ".DS_Store", "nohup.out"]
        for pattern in temp_patterns:
            for temp_file in self.project_root.rglob(pattern):
                if self._should_cleanup_temp(temp_file):
                    stray_files.append(
                        {
                            "type": "temp_file",
                            "path": str(temp_file),
                            "suggested_action": "delete",
                            "reason": f"一時ファイル（パターン: {pattern}）",
                        }
                    )

        self.log(f"🔍 不適切ファイル検出: {len(stray_files)}個")
        return stray_files

    def _is_allowed_root_file(self, filename: str) -> bool:
        """ルートレベル許可ファイル判定"""
        allowed_patterns = [
            "README.md",
            "LICENSE",
            "CHANGELOG.md",
            ".gitignore",
            ".mcp.json",
            ".claude-project",
            "pyproject.toml",
            "package.json",
            "Dockerfile",
            "docker-compose.yml",
            ".shell_integration.zsh",
            ".cursorindexingignore",
        ]

        return any(
            filename == pattern or filename.startswith(pattern.replace("*", ""))
            for pattern in allowed_patterns
        )

    def _suggest_location(self, file_path: Path) -> str:
        """ファイルの適切な配置場所を提案"""
        name = file_path.name.lower()

        if name.endswith(".log"):
            return "runtime/logs/"
        elif name.endswith(".md") and "report" in name:
            return "docs/reports/"
        elif name.endswith(".md"):
            return "docs/"
        elif name.endswith(".json") and "config" in name:
            return "config/"
        elif name.endswith(".py"):
            return "src/"
        elif name.endswith(".sh"):
            return "scripts/"
        else:
            return "runtime/tmp/"

    def _should_cleanup_temp(self, file_path: Path) -> bool:
        """一時ファイルのクリーンアップ判定"""
        # node_modules内は除外
        if "node_modules" in str(file_path):
            return False

        # .git内は除外
        if ".git" in str(file_path):
            return False

        # 最終更新から24時間以上経過した一時ファイルのみ
        try:
            age_hours = (time.time() - file_path.stat().st_mtime) / 3600
            return age_hours > 24
        except Exception:
            return False

    def auto_fix_violations(self, stray_files: List[Dict[str, Any]]) -> int:
        """自動修正実行（o3のpath-shim戦略）"""
        fixed_count = 0

        for item in stray_files:
            try:
                if item["type"] == "temp_file" and item["suggested_action"] == "delete":
                    # 一時ファイル削除
                    Path(item["path"]).unlink()
                    self.log(f"🗑️ 削除: {item['path']}")
                    fixed_count += 1

                elif item["type"] == "misplaced_file":
                    # ファイル移動
                    src_path = Path(item["path"])
                    dst_dir = Path(item["suggested_location"])
                    dst_dir.mkdir(parents=True, exist_ok=True)
                    dst_path = dst_dir / src_path.name

                    # Git管理下なら git mv、そうでなければ通常移動
                    if self._is_git_tracked(src_path):
                        subprocess.run(
                            ["git", "mv", str(src_path), str(dst_path)],
                            check=True,
                            cwd=self.project_root,
                        )
                        self.log(f"📦 Git移動: {src_path} → {dst_path}")
                    else:
                        src_path.rename(dst_path)
                        self.log(f"📦 移動: {src_path} → {dst_path}")

                    fixed_count += 1

            except Exception as e:
                self.log(f"❌ 修正失敗 {item['path']}: {str(e)}", "ERROR")

        return fixed_count

    def _is_git_tracked(self, file_path: Path) -> bool:
        """Gitトラッキング状態確認"""
        try:
            result = subprocess.run(
                ["git", "ls-files", "--error-unmatch", str(file_path)],
                cwd=self.project_root,
                capture_output=True,
                check=False,
            )
            return result.returncode == 0
        except Exception:
            return False

    def generate_report(self) -> Dict[str, Any]:
        """整理結果レポート生成（Gemini戦略）"""
        root_check = self.check_root_directory_count()
        stray_files = self.detect_stray_files()

        report = {
            "timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "checks": {
                "root_directory_count": root_check,
                "stray_files": {"count": len(stray_files), "items": stray_files},
            },
            "overall_health": "healthy"
            if not root_check["violation"] and len(stray_files) == 0
            else "needs_attention",
        }

        # レポート保存
        report_file = (
            self.project_root
            / "runtime"
            / "logs"
            / f"janitor-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        )
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        self.log(f"📊 レポート生成: {report_file}")
        return report

    def run_cleaning_cycle(self, auto_fix: bool = True) -> Dict[str, Any]:
        """完全なクリーニングサイクル実行"""
        self.log("🧹 Janitor Bot クリーニングサイクル開始")

        # 1. 分析フェーズ
        report = self.generate_report()

        # 2. 自動修正フェーズ
        if auto_fix and report["checks"]["stray_files"]["count"] > 0:
            self.log("🔧 自動修正開始")
            fixed_count = self.auto_fix_violations(
                report["checks"]["stray_files"]["items"]
            )
            report["auto_fixes_applied"] = fixed_count
            self.log(f"✅ 自動修正完了: {fixed_count}件")

        # 3. 最終状態確認
        final_root_check = self.check_root_directory_count()
        report["final_state"] = {
            "root_directory_count": final_root_check["count"],
            "health_status": "healthy"
            if final_root_check["count"] <= self.max_root_dirs
            else "violated",
        }

        self.log("🏁 Janitor Bot クリーニングサイクル完了")
        return report


def main():
    """メイン実行"""
    import argparse

    parser = argparse.ArgumentParser(description="Janitor Bot - 自律的プロジェクト整理")
    parser.add_argument(
        "--project-root", default=".", help="プロジェクトルートディレクトリ"
    )
    parser.add_argument("--no-auto-fix", action="store_true", help="自動修正を無効化")
    parser.add_argument("--report-only", action="store_true", help="レポート生成のみ")

    args = parser.parse_args()

    bot = JanitorBot(args.project_root)

    if args.report_only:
        report = bot.generate_report()
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        report = bot.run_cleaning_cycle(auto_fix=not args.no_auto_fix)

        # サマリー表示
        print("\n" + "=" * 60)
        print("🤖 JANITOR BOT - 実行結果サマリー")
        print("=" * 60)
        print(
            f"📂 ルートディレクトリ数: {report['final_state']['root_directory_count']}/8"
        )
        print(f"🏥 プロジェクト健全性: {report['final_state']['health_status']}")
        if "auto_fixes_applied" in report:
            print(f"🔧 自動修正実行: {report['auto_fixes_applied']}件")
        print("=" * 60)


if __name__ == "__main__":
    main()
