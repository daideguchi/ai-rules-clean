#!/usr/bin/env python3
"""
O3推奨 インテリジェント・ファイルロケーター
AI assistantの「ファイル位置記憶喪失」問題を根本解決
"""

import json
import os
import subprocess
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class IntelligentFileLocator:
    """O3推奨のファイル位置管理システム"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.session_start = datetime.now()

        # O3推奨: セッションレベル ファイルマップ
        self.file_map: Dict[str, List[str]] = {}
        self.dir_map: Dict[str, List[str]] = {}

        # O3推奨: LRUキャッシュ（最近使用ファイル）
        self.lru_cache = deque(maxlen=20)

        # O3推奨: 名前付きハンドル（高頻度ファイル）
        self.named_handles = {
            "CURSOR_RULES": ".cursor/rules/globals.mdc",
            "DEV_RULES": ".cursor/rules/dev-rules",
            "CLAUDE_RULES": "docs/instructions/CLAUDE.md",
            "ROOT_RULES": "docs/rules/0-ROOT.yml",
            "STATUS": "STATUS.md",
            "MAKEFILE": "Makefile",
            "PYPROJECT": "pyproject.toml",
            "GITIGNORE": ".gitignore",
        }

        # 無視するディレクトリ（O3推奨: 低シグナル領域の除外）
        self.ignore_patterns = {
            ".git",
            "node_modules",
            "dist",
            "__pycache__",
            ".pytest_cache",
            "coverage",
            ".coverage",
            "htmlcov",
            ".mypy_cache",
            ".ruff_cache",
        }

        # 初期化: 一回だけのディスカバリー実行
        self._build_initial_map()

    def _build_initial_map(self):
        """O3推奨: セッション開始時の一回限りディスカバリー"""
        print("🔍 O3推奨ファイルマップ構築中...")

        try:
            # 効率的なfind実行（一回限り）
            cmd = [
                "find",
                str(self.project_root),
                "-type",
                "f",
                "!",
                "-path",
                "*/.*/*",  # 大部分の隠しディレクトリ除外
                "!",
                "-name",
                "*.pyc",
                "!",
                "-name",
                "*.log",
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                files = result.stdout.strip().split("\n")
                files = [f for f in files if f]  # 空行除外

                # O(1)検索用辞書構築
                for file_path in files:
                    if self._should_ignore(file_path):
                        continue

                    rel_path = os.path.relpath(file_path, self.project_root)
                    basename = os.path.basename(file_path)

                    if basename not in self.file_map:
                        self.file_map[basename] = []
                    self.file_map[basename].append(rel_path)

                # ディレクトリマップも構築
                for file_path in files:
                    if self._should_ignore(file_path):
                        continue

                    rel_path = os.path.relpath(file_path, self.project_root)
                    dirname = os.path.dirname(rel_path)

                    if dirname and dirname != ".":
                        if dirname not in self.dir_map:
                            self.dir_map[dirname] = []
                        self.dir_map[dirname].append(os.path.basename(rel_path))

                print(
                    f"✅ ファイルマップ構築完了: {len(self.file_map)}ファイル, {len(self.dir_map)}ディレクトリ"
                )

            else:
                print(f"⚠️ find実行エラー: {result.stderr}")

        except Exception as e:
            print(f"⚠️ ファイルマップ構築エラー: {e}")

    def _should_ignore(self, file_path: str) -> bool:
        """低シグナル領域の除外判定"""
        path_parts = Path(file_path).parts
        return any(
            ignore_pattern in path_parts for ignore_pattern in self.ignore_patterns
        )

    def locate(self, filename: str, within: Optional[str] = None) -> Optional[str]:
        """O3推奨: O(1)ファイル位置検索"""

        # 1. 名前付きハンドル確認
        if filename.upper() in self.named_handles:
            handle_path = self.named_handles[filename.upper()]
            if (self.project_root / handle_path).exists():
                self._update_lru(handle_path)
                return handle_path

        # 2. LRUキャッシュ確認
        for cached_path in self.lru_cache:
            if os.path.basename(cached_path) == filename:
                if within is None or cached_path.startswith(within):
                    return cached_path

        # 3. ファイルマップ検索
        if filename in self.file_map:
            candidates = self.file_map[filename]

            if within:
                # スコープ検索
                filtered = [p for p in candidates if p.startswith(within)]
                if filtered:
                    self._update_lru(filtered[0])
                    return filtered[0]
            else:
                # 最初の候補を返す
                if candidates:
                    self._update_lru(candidates[0])
                    return candidates[0]

        # 4. 見つからない場合は対象リフレッシュ
        print(f"⚠️ {filename} が見つかりません。ターゲットリフレッシュ実行...")
        self._targeted_refresh(within or ".")

        # 5. リフレッシュ後に再検索
        if filename in self.file_map:
            candidates = self.file_map[filename]
            if candidates:
                self._update_lru(candidates[0])
                return candidates[0]

        return None

    def _update_lru(self, file_path: str):
        """LRUキャッシュ更新"""
        # 既存エントリを削除してから先頭に追加
        if file_path in self.lru_cache:
            self.lru_cache.remove(file_path)
        self.lru_cache.appendleft(file_path)

    def _targeted_refresh(self, directory: str):
        """O3推奨: 対象ディレクトリのみリフレッシュ"""
        try:
            target_dir = self.project_root / directory
            if not target_dir.exists():
                return

            cmd = ["find", str(target_dir), "-type", "f"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                files = result.stdout.strip().split("\n")

                # 該当ディレクトリのマップ更新
                for file_path in files:
                    if file_path and not self._should_ignore(file_path):
                        rel_path = os.path.relpath(file_path, self.project_root)
                        basename = os.path.basename(file_path)

                        if basename not in self.file_map:
                            self.file_map[basename] = []

                        if rel_path not in self.file_map[basename]:
                            self.file_map[basename].append(rel_path)

                print(f"✅ {directory}ディレクトリリフレッシュ完了")

        except Exception as e:
            print(f"⚠️ ターゲットリフレッシュエラー: {e}")

    def notify_file_created(self, file_path: str):
        """ファイル作成通知（マップ更新）"""
        rel_path = os.path.relpath(file_path, self.project_root)
        basename = os.path.basename(file_path)

        if basename not in self.file_map:
            self.file_map[basename] = []

        if rel_path not in self.file_map[basename]:
            self.file_map[basename].append(rel_path)

        self._update_lru(rel_path)
        print(f"📝 ファイルマップ更新: {basename} → {rel_path}")

    def notify_file_deleted(self, file_path: str):
        """ファイル削除通知（マップ更新）"""
        rel_path = os.path.relpath(file_path, self.project_root)
        basename = os.path.basename(file_path)

        if basename in self.file_map:
            if rel_path in self.file_map[basename]:
                self.file_map[basename].remove(rel_path)
                if not self.file_map[basename]:
                    del self.file_map[basename]

        if rel_path in self.lru_cache:
            self.lru_cache.remove(rel_path)

        print(f"🗑️ ファイルマップ更新: {basename} 削除")

    def list_files_in_dir(self, directory: str) -> List[str]:
        """ディレクトリ内ファイル一覧（マップから取得）"""
        if directory in self.dir_map:
            return self.dir_map[directory]

        # マップにない場合はリフレッシュ
        self._targeted_refresh(directory)
        return self.dir_map.get(directory, [])

    def find_by_extension(self, extension: str) -> List[str]:
        """拡張子によるファイル検索"""
        matches = []
        for basename, paths in self.file_map.items():
            if basename.endswith(extension):
                matches.extend(paths)
        return matches

    def get_project_overview(self) -> Dict:
        """プロジェクト概要（メンタルモデル構築用）"""
        overview = {
            "total_files": sum(len(paths) for paths in self.file_map.values()),
            "file_types": {},
            "top_directories": {},
            "key_files": {},
        }

        # ファイルタイプ分析
        for basename in self.file_map.keys():
            ext = os.path.splitext(basename)[1] or "no_extension"
            overview["file_types"][ext] = overview["file_types"].get(ext, 0) + 1

        # トップディレクトリ分析
        for paths in self.file_map.values():
            for path in paths:
                top_dir = path.split("/")[0] if "/" in path else "root"
                overview["top_directories"][top_dir] = (
                    overview["top_directories"].get(top_dir, 0) + 1
                )

        # キーファイル確認
        for handle, path in self.named_handles.items():
            overview["key_files"][handle] = (
                "✅" if (self.project_root / path).exists() else "❌"
            )

        return overview

    def save_session_cache(self):
        """セッションキャッシュ保存"""
        cache_data = {
            "session_start": self.session_start.isoformat(),
            "lru_cache": list(self.lru_cache),
            "file_map_size": len(self.file_map),
            "project_overview": self.get_project_overview(),
        }

        cache_file = self.project_root / "runtime" / "file-locator-cache.json"
        cache_file.parent.mkdir(exist_ok=True)

        with open(cache_file, "w") as f:
            json.dump(cache_data, f, indent=2)

        print(f"💾 セッションキャッシュ保存: {cache_file}")


# グローバルインスタンス（セッション間で再利用）
_global_locator: Optional[IntelligentFileLocator] = None


def get_file_locator() -> IntelligentFileLocator:
    """グローバルファイルロケーター取得"""
    global _global_locator
    if _global_locator is None:
        _global_locator = IntelligentFileLocator()
    return _global_locator


def locate_file(filename: str, within: Optional[str] = None) -> Optional[str]:
    """O3推奨: ファイル位置取得（シンプルインターフェース）"""
    return get_file_locator().locate(filename, within)


def main():
    """テスト実行"""
    locator = IntelligentFileLocator()

    print("🎯 インテリジェント・ファイルロケーター テスト")
    print("=" * 60)

    # テストケース
    test_files = ["globals.mdc", "STATUS.md", "Makefile", "pyproject.toml", "CLAUDE.md"]

    for test_file in test_files:
        location = locator.locate(test_file)
        if location:
            print(f"✅ {test_file} → {location}")
        else:
            print(f"❌ {test_file} → 見つかりません")

    # プロジェクト概要表示
    overview = locator.get_project_overview()
    print("\n📊 プロジェクト概要:")
    print(f"  総ファイル数: {overview['total_files']}")
    print(f"  ファイルタイプ: {len(overview['file_types'])}")
    print(f"  トップディレクトリ: {len(overview['top_directories'])}")

    # セッションキャッシュ保存
    locator.save_session_cache()


if __name__ == "__main__":
    main()
