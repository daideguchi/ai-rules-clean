#!/usr/bin/env python3
"""
ドキュメント自動同期システム
コード変更時にドキュメントの同期状態をチェック・自動更新
"""

import hashlib
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

PROJECT_ROOT = Path(__file__).parent.parent.parent
SYNC_STATE_FILE = PROJECT_ROOT / "runtime" / "doc_sync_state.json"
DOCS_ROOT = PROJECT_ROOT / "docs"


class DocumentationSyncer:
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.sync_state = self._load_sync_state()

    def _load_sync_state(self) -> Dict:
        """同期状態ファイルの読み込み"""
        if SYNC_STATE_FILE.exists():
            with open(SYNC_STATE_FILE, encoding="utf-8") as f:
                return json.load(f)
        return {
            "version": "1.0",
            "last_sync": None,
            "file_hashes": {},
            "doc_mappings": {},
            "auto_sync_enabled": True,
        }

    def _save_sync_state(self):
        """同期状態ファイルの保存"""
        SYNC_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(SYNC_STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(self.sync_state, f, indent=2, ensure_ascii=False)

    def _get_file_hash(self, file_path: Path) -> str:
        """ファイルのハッシュ値計算"""
        try:
            with open(file_path, "rb") as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return ""

    def _get_git_changed_files(self) -> List[str]:
        """Git変更ファイル一覧取得"""
        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )
            return result.stdout.strip().split("\n") if result.stdout.strip() else []
        except Exception:
            return []

    def _find_related_docs(self, source_file: str) -> List[Path]:
        """ソースファイルに関連するドキュメント発見"""
        related_docs = []
        file_stem = Path(source_file).stem

        # 1. 直接命名関連ドキュメント
        for doc_file in DOCS_ROOT.rglob("*.md"):
            if file_stem.lower() in doc_file.stem.lower():
                related_docs.append(doc_file)

        # 2. 内容参照関連ドキュメント
        try:
            result = subprocess.run(
                ["grep", "-r", "-l", file_stem, str(DOCS_ROOT)],
                capture_output=True,
                text=True,
            )
            for line in result.stdout.strip().split("\n"):
                if line and line.endswith(".md"):
                    related_docs.append(Path(line))
        except Exception:
            pass

        return list(set(related_docs))

    def _check_doc_staleness(self, doc_path: Path) -> Tuple[bool, str]:
        """ドキュメントの陳腐化チェック"""
        if not doc_path.exists():
            return True, "ドキュメントが存在しません"

        # 最終更新日チェック
        doc_mtime = doc_path.stat().st_mtime
        week_ago = datetime.now().timestamp() - (7 * 24 * 3600)

        if doc_mtime < week_ago:
            return (
                True,
                f"7日以上更新されていません ({datetime.fromtimestamp(doc_mtime).strftime('%Y-%m-%d')})",
            )

        # ハッシュ変更チェック
        current_hash = self._get_file_hash(doc_path)
        stored_hash = self.sync_state["file_hashes"].get(str(doc_path), "")

        if current_hash != stored_hash:
            return False, "ドキュメントは最新です"

        return True, "関連コードが変更されましたが、ドキュメントは未更新です"

    def _auto_update_doc_header(self, doc_path: Path):
        """ドキュメントヘッダーの自動更新"""
        try:
            with open(doc_path, encoding="utf-8") as f:
                content = f.read()

            # 更新日時ヘッダーの追加・更新
            current_date = datetime.now().strftime("%Y-%m-%d")

            if "**最終更新**:" in content:
                # 既存の更新日を置換
                import re

                content = re.sub(
                    r"\*\*最終更新\*\*: \d{4}-\d{2}-\d{2}",
                    f"**最終更新**: {current_date}",
                    content,
                )
            else:
                # ヘッダーを追加
                lines = content.split("\n")
                if lines and lines[0].startswith("#"):
                    lines.insert(1, f"\n**最終更新**: {current_date}")
                    content = "\n".join(lines)

            with open(doc_path, "w", encoding="utf-8") as f:
                f.write(content)

            print(
                f"✅ ドキュメントヘッダー更新: {doc_path.relative_to(self.project_root)}"
            )

        except Exception as e:
            print(
                f"❌ ドキュメント更新失敗: {doc_path.relative_to(self.project_root)} - {e}"
            )

    def check_and_sync(self) -> bool:
        """変更ファイルのドキュメント同期チェック"""
        if not self.sync_state["auto_sync_enabled"]:
            return True

        changed_files = self._get_git_changed_files()
        if not changed_files:
            return True

        issues_found = False
        sync_needed = []

        for file_path in changed_files:
            if not file_path.endswith((".py", ".sh", ".js", ".ts")):
                continue

            # 関連ドキュメント発見
            related_docs = self._find_related_docs(file_path)

            for doc_path in related_docs:
                is_stale, reason = self._check_doc_staleness(doc_path)

                if is_stale:
                    issues_found = True
                    sync_needed.append((file_path, doc_path, reason))
                    print(
                        f"⚠️  同期必要: {file_path} → {doc_path.relative_to(self.project_root)}"
                    )
                    print(f"   理由: {reason}")

        # 自動同期実行
        if sync_needed:
            print(f"\n🔄 {len(sync_needed)}件のドキュメント自動同期中...")

            for _source_file, doc_path, _reason in sync_needed:
                self._auto_update_doc_header(doc_path)

                # ハッシュ状態更新
                self.sync_state["file_hashes"][str(doc_path)] = self._get_file_hash(
                    doc_path
                )

        # 同期状態保存
        self.sync_state["last_sync"] = datetime.now().isoformat()
        self._save_sync_state()

        if issues_found:
            print("\n📝 ドキュメント同期を実行しました")
            print(f"   変更されたファイル: {len(changed_files)}件")
            print(f"   同期されたドキュメント: {len(sync_needed)}件")

        return True


def main():
    """メイン処理"""
    try:
        syncer = DocumentationSyncer()
        success = syncer.check_and_sync()

        if not success:
            print("❌ ドキュメント同期チェックに失敗しました")
            sys.exit(1)

        print("✅ ドキュメント同期チェック完了")

    except Exception as e:
        print(f"❌ ドキュメント同期システムエラー: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
