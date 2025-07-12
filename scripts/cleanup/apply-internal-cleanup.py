#!/usr/bin/env python3
"""
内部構造クリーンアップ実行
散在ドキュメント・命名違反・重複ファイルの自動修正
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class InternalCleanupEngine:
    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        self.moves = []
        self.renames = []
        self.deletions = []

    def run_cleanup(self):
        print("🧹 内部構造クリーンアップ開始")
        print(f"モード: {'DRY-RUN' if self.dry_run else 'EXECUTE'}")

        # 最新の分析結果を読み込み
        analysis_file = self.get_latest_analysis()
        if not analysis_file:
            print("❌ 分析結果ファイルが見つかりません")
            print(
                "先に python3 scripts/analyze-internal-structure.py を実行してください"
            )
            return

        with open(analysis_file, encoding="utf-8") as f:
            analysis = json.load(f)

        # 1. 散在ドキュメント整理
        self.fix_scattered_documents(analysis["problems"]["scattered_documents"])

        # 2. 命名規則違反修正
        self.fix_naming_violations(analysis["problems"]["naming_violations"])

        # 3. 重複ファイル処理
        self.handle_duplicates(analysis["problems"]["duplicates"])

        # 4. 空ディレクトリ削除
        self.remove_empty_directories()

        # 5. レポート生成
        self.generate_cleanup_report()

    def get_latest_analysis(self):
        """最新の分析結果ファイルを取得"""
        analysis_files = list(
            (ROOT / "runtime").glob("internal-structure-analysis-*.json")
        )
        if not analysis_files:
            return None
        return max(analysis_files, key=lambda f: f.stat().st_mtime)

    def fix_scattered_documents(self, scattered_docs):
        """散在ドキュメントを適切な場所に移動"""
        print(f"\n📄 散在ドキュメント修正: {len(scattered_docs)}個")

        for doc in scattered_docs:
            src = ROOT / doc["current_location"] / doc["file"]
            dst = ROOT / doc["should_be"]

            if not src.exists():
                continue

            self.log_action("MOVE DOC", src, dst)

            if not self.dry_run:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), str(dst))

            self.moves.append({"src": str(src), "dst": str(dst), "type": "document"})

    def fix_naming_violations(self, naming_violations):
        """命名規則違反を修正"""
        print(f"\n🏷️  命名規則違反修正: {len(naming_violations)}個")

        # ディレクトリ名から処理（深い階層から）
        dirs_to_rename = [v for v in naming_violations if v["type"] == "directory"]
        dirs_to_rename.sort(key=lambda x: len(x["path"].split("/")), reverse=True)

        for violation in dirs_to_rename:
            old_path = ROOT / violation["path"]
            parent = old_path.parent
            new_name = violation["suggested"]
            new_path = parent / new_name

            if not old_path.exists() or old_path == new_path:
                continue

            self.log_action("RENAME DIR", old_path, new_path)

            if not self.dry_run:
                old_path.rename(new_path)

            self.renames.append(
                {"old": str(old_path), "new": str(new_path), "type": "directory"}
            )

        # ファイル名を処理
        files_to_rename = [v for v in naming_violations if v["type"] == "file"]

        for violation in files_to_rename:
            old_path = ROOT / violation["path"]
            parent = old_path.parent
            new_name = violation["suggested"]
            new_path = parent / new_name

            if not old_path.exists() or old_path == new_path:
                continue

            self.log_action("RENAME FILE", old_path, new_path)

            if not self.dry_run:
                old_path.rename(new_path)

            self.renames.append(
                {"old": str(old_path), "new": str(new_path), "type": "file"}
            )

    def handle_duplicates(self, duplicates):
        """重複ファイルを処理"""
        print(f"\n🔄 重複ファイル処理: {len(duplicates)}組")

        for dup_group in duplicates:
            files = dup_group["files"]
            if len(files) < 2:
                continue

            # 最も適切な場所にあるファイルを残し、他を削除
            keep_file = self.select_file_to_keep(files)

            for file_path in files:
                if file_path != keep_file:
                    full_path = ROOT / file_path
                    self.log_action("DELETE DUP", full_path)

                    if not self.dry_run and full_path.exists():
                        full_path.unlink()

                    self.deletions.append(
                        {"path": str(full_path), "reason": "duplicate"}
                    )

    def select_file_to_keep(self, files):
        """重複ファイルの中で残すべきファイルを選択"""
        # 優先順位: docs/ > scripts/ > config/ > src/ > runtime/
        priority_order = ["docs/", "scripts/", "config/", "src/", "runtime/"]

        for prefix in priority_order:
            for file_path in files:
                if file_path.startswith(prefix):
                    return file_path

        # 優先順位に該当しない場合は最初のファイルを残す
        return files[0]

    def remove_empty_directories(self):
        """空ディレクトリを削除"""
        print("\n📁 空ディレクトリ削除中...")

        # 深い階層から処理
        for root, _dirs, _files in os.walk(ROOT, topdown=False):
            if ".git" in root or "node_modules" in root:
                continue

            current_dir = Path(root)
            rel_path = current_dir.relative_to(ROOT)

            # ディレクトリが空かチェック
            try:
                if not any(current_dir.iterdir()):
                    self.log_action("DELETE EMPTY", current_dir)

                    if not self.dry_run:
                        current_dir.rmdir()

                    self.deletions.append(
                        {"path": str(rel_path), "reason": "empty_directory"}
                    )
            except OSError:
                continue

    def log_action(self, action, src, dst=None):
        """アクション内容をログ出力"""
        if self.dry_run:
            prefix = "DRY-RUN"
        else:
            prefix = "EXECUTE"

        if dst:
            print(f"   {prefix} {action}: {src} → {dst}")
        else:
            print(f"   {prefix} {action}: {src}")

    def generate_cleanup_report(self):
        """クリーンアップレポート生成"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "dry_run": self.dry_run,
            "summary": {
                "moves": len(self.moves),
                "renames": len(self.renames),
                "deletions": len(self.deletions),
            },
            "actions": {
                "moves": self.moves,
                "renames": self.renames,
                "deletions": self.deletions,
            },
        }

        report_path = (
            ROOT
            / "runtime"
            / f"internal-cleanup-{'dry-run' if self.dry_run else 'executed'}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        )

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print("\n📊 クリーンアップ結果:")
        print(f"   📁 ファイル移動: {len(self.moves)}個")
        print(f"   🏷️  リネーム: {len(self.renames)}個")
        print(f"   🗑️  削除: {len(self.deletions)}個")
        print(f"\n📋 詳細レポート: {report_path}")

        if self.dry_run:
            print("\n⚠️  DRY-RUN モードで実行されました")
            print("実際に適用するには --apply フラグを使用してください")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="内部構造クリーンアップ実行")
    parser.add_argument("--apply", action="store_true", help="実際に変更を適用する")
    args = parser.parse_args()

    cleanup = InternalCleanupEngine(dry_run=not args.apply)
    cleanup.run_cleanup()


if __name__ == "__main__":
    main()
