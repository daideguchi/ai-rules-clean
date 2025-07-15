#!/usr/bin/env python3
"""
組織ルール違反自動修正スクリプト
11個のルートディレクトリを9個以下に削減し、散在ファイルを適切な場所に移動

実行方法:
1. python scripts/automated-cleanup.py              # DRY-RUN（実行プレビュー）
2. python scripts/automated-cleanup.py --apply     # 実際に修正実行
"""

from __future__ import annotations

import argparse
import logging
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG = logging.getLogger("cleanup")

# 統合戦略: 11個 → 7個のルートディレクトリに削減
TARGET_STRUCTURE = {
    "config": "Configuration files and rules",
    "docs": "Documentation, reports, compliance",
    "models": "ML models and experiments",
    "ops": "Operations, deployment, monitoring",
    "runtime": "Runtime data, logs, temporary files",
    "scripts": "Utility scripts and automation",
    "src": "Source code including API and tests",
}

# 移動ルール定義（O3推奨の安全版）
MOVE_RULES = [
    # 散在ファイルの整理（安全）
    ("runtime/logs/**/*.md", "docs/reports/logs"),
    ("src/ai/agents/**/*.md", "docs/reports/ai-agents"),
    # ルートディレクトリ統合（衝突チェック付き）
    ("compliance/**", "docs/compliance"),
    ("data/**", "runtime/data"),
    # ルールファイル統合（制限付き）
    ("docs/*rules*.md", "docs/rules"),
    ("*RULES*.md", "docs/rules"),
    (".cursor/**", "config/cursor"),
    # トップレベルのみの安全な移動
    ("README.md", "docs/misc/ROOT_README.md"),
]

# 危険なルール（O3により無効化）
DISABLED_RULES = [
    # ("src/ai/agents/**/*.sh", "scripts/ai-agents"),  # パス参照破綻の可能性
    # ("api/**", "src/api"),                           # 既存ディレクトリとの衝突
    # ("tests/**", "src/tests"),                       # 既存ディレクトリとの衝突
    # ("**/.editorconfig", "config"),                  # IDE設定破綻
    # ("**/README.md", "docs/misc"),                   # node_modules等の大量README
]

# 除外パターン（サードパーティコード保護）
EXCLUDE_PATTERNS = [
    "node_modules/**",
    "vendor/**",
    "external/**",
    ".git/**",
    "__pycache__/**",
    "*.pyc",
    ".DS_Store",
]

# 禁止されたディレクトリ
FORBIDDEN_DIRS = {
    "logs",  # runtime/logs を使用
    "tmp",  # system temp を使用
    "temp",  # system temp を使用
    "cache",  # system cache を使用
    "backup",  # git history を使用
    "bin",  # scripts/ を使用
    "archive",  # git history を使用
}


class CleanupEngine:
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.moves_planned = []
        self.renames_planned = []

    def log_action(self, action: str, src: Path, dst: Path = None):
        if self.dry_run:
            if dst:
                LOG.info(f"DRY-RUN {action}: {src} -> {dst}")
            else:
                LOG.info(f"DRY-RUN {action}: {src}")
        else:
            if dst:
                LOG.info(f"EXECUTING {action}: {src} -> {dst}")
            else:
                LOG.info(f"EXECUTING {action}: {src}")

    def git_mv(self, src: Path, dst: Path):
        """Git mvを使用してファイルを移動（履歴保持）"""
        self.log_action("MOVE", src, dst)

        if self.dry_run:
            self.moves_planned.append((src, dst))
            return

        # 移動先ディレクトリ作成
        dst.parent.mkdir(parents=True, exist_ok=True)

        # Git管理下かチェック
        if (ROOT / ".git").exists():
            try:
                subprocess.run(
                    ["git", "mv", str(src), str(dst)],
                    check=True,
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                )
            except subprocess.CalledProcessError as e:
                # Git mvが失敗した場合は通常の移動
                LOG.warning(f"Git mv failed: {e.stderr.strip()}")
                shutil.move(src, dst)
        else:
            shutil.move(src, dst)

    def to_kebab_case(self, name: str) -> str:
        """ファイル名をkebab-caseに変換"""
        if name.startswith("_") or name.startswith("."):
            return name  # 隠しファイルは変更しない

        # 特殊文字を除去してケバブケースに変換
        words = re.split(r"[_ ]", name)
        clean_name = "-".join(filter(None, words)).lower()
        clean_name = re.sub(r"[^a-z0-9\-\.]", "-", clean_name)

        # 重複ハイフンを削除
        clean_name = re.sub(r"-+", "-", clean_name)
        clean_name = clean_name.strip("-")

        return clean_name

    def should_exclude(self, path: Path) -> bool:
        """除外パターンにマッチするかチェック"""
        path_str = str(path)
        for pattern in EXCLUDE_PATTERNS:
            if path.match(pattern) or pattern.removesuffix("/**") in path_str:
                return True
        return False

    def apply_file_moves(self):
        """ファイル移動ルールを適用（安全版）"""
        LOG.info("=== ファイル移動ルール適用開始（安全版） ===")

        for pattern, dest_dir in MOVE_RULES:
            matches = list(ROOT.glob(pattern))

            for src_path in matches:
                # 除外パターンチェック
                if self.should_exclude(src_path):
                    LOG.debug(f"EXCLUDED: {src_path}")
                    continue

                if src_path.is_file():
                    src_path.relative_to(ROOT)
                    dest_path = ROOT / dest_dir / src_path.name

                    # 移動先に既に存在する場合はスキップ
                    if dest_path.exists():
                        LOG.warning(f"SKIP: {dest_path} already exists")
                        continue

                    self.git_mv(src_path, dest_path)

    def apply_kebab_case_naming(self):
        """ケバブケース命名規則を適用（安全版）"""
        LOG.info("=== ケバブケース命名規則適用開始（プロジェクトファイルのみ） ===")

        # プロジェクトのディレクトリとファイルのみを対象
        project_dirs = [
            "docs",
            "scripts",
            "src/ai",
            "runtime",
            "config",
            "ops",
            "models",
            "data",
            "compliance",
        ]

        for project_dir in project_dirs:
            project_path = ROOT / project_dir
            if not project_path.exists():
                continue

            # プロジェクトディレクトリ内のファイルを処理
            all_paths = sorted(
                project_path.rglob("*"), key=lambda p: len(p.parts), reverse=True
            )

            for path in all_paths:
                # 除外パターンチェック
                if self.should_exclude(path):
                    continue

                if path.name in (".git", "__pycache__") or path.is_symlink():
                    continue

                new_name = self.to_kebab_case(path.name)
                if new_name != path.name:
                    new_path = path.with_name(new_name)
                    self.log_action("RENAME", path, new_path)

                    if not self.dry_run:
                        try:
                            path.rename(new_path)
                            self.renames_planned.append((path, new_path))
                        except OSError as e:
                            LOG.error(f"RENAME FAILED: {path} -> {new_path}: {e}")

    def remove_forbidden_dirs(self):
        """禁止されたディレクトリを削除"""
        LOG.info("=== 禁止ディレクトリ削除開始 ===")

        for forbidden in FORBIDDEN_DIRS:
            forbidden_path = ROOT / forbidden
            if forbidden_path.exists():
                self.log_action("REMOVE FORBIDDEN DIR", forbidden_path)

                if not self.dry_run:
                    try:
                        shutil.rmtree(forbidden_path)
                        LOG.info(f"REMOVED: {forbidden_path}")
                    except OSError as e:
                        LOG.error(f"REMOVE FAILED: {forbidden_path}: {e}")

    def validate_target_structure(self):
        """目標構造の検証"""
        LOG.info("=== 目標構造検証 ===")

        current_roots = [
            d for d in ROOT.iterdir() if d.is_dir() and not d.name.startswith(".")
        ]

        LOG.info(f"現在のルートディレクトリ数: {len(current_roots)}")
        LOG.info(f"目標ルートディレクトリ数: {len(TARGET_STRUCTURE)}")

        for root_dir in current_roots:
            if root_dir.name in TARGET_STRUCTURE:
                LOG.info(f"✅ 適合: {root_dir.name}")
            else:
                LOG.warning(f"❌ 未適合: {root_dir.name}")

    def generate_report(self):
        """実行レポート生成"""
        LOG.info("=== 実行レポート ===")
        LOG.info(f"計画されたファイル移動: {len(self.moves_planned)}")
        LOG.info(f"計画されたリネーム: {len(self.renames_planned)}")

        if self.dry_run:
            LOG.info(
                "⚠️  DRY-RUN モードで実行されました。実際の変更は行われていません。"
            )
            LOG.info("実際に実行するには --apply フラグを使用してください。")
        else:
            LOG.info("✅ 実際の変更が適用されました。")

    def run_cleanup(self):
        """クリーンアップ実行"""
        LOG.info("🧹 プロジェクト組織構造クリーンアップ開始")
        LOG.info(f"実行モード: {'DRY-RUN' if self.dry_run else 'APPLY'}")

        try:
            # 1. ファイル移動
            self.apply_file_moves()

            # 2. ケバブケース適用
            self.apply_kebab_case_naming()

            # 3. 禁止ディレクトリ削除
            self.remove_forbidden_dirs()

            # 4. 構造検証
            self.validate_target_structure()

            # 5. レポート生成
            self.generate_report()

            LOG.info("✅ クリーンアップ完了")

        except Exception as e:
            LOG.error(f"❌ クリーンアップ中にエラーが発生しました: {e}")
            raise


def main():
    parser = argparse.ArgumentParser(
        description="プロジェクト組織構造自動クリーンアップ",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python scripts/automated-cleanup.py                # DRY-RUN
  python scripts/automated-cleanup.py --apply        # 実際に実行
  python scripts/automated-cleanup.py --apply -v     # 詳細ログ付き実行
        """,
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help="実際に変更を適用する（デフォルトはDRY-RUN）",
    )

    parser.add_argument("-v", "--verbose", action="store_true", help="詳細ログを表示")

    args = parser.parse_args()

    # ログ設定
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%H:%M:%S",
    )

    # クリーンアップエンジン初期化
    cleanup = CleanupEngine(dry_run=not args.apply)

    # 実行
    cleanup.run_cleanup()


if __name__ == "__main__":
    main()
