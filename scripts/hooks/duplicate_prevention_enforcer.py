#!/usr/bin/env python3
"""🚫 複製ファイル防止強制システム"""

import os
import re
import sys
from pathlib import Path


class DuplicatePreventionEnforcer:
    def __init__(self):
        self.project_root = Path.cwd()
        self.duplicate_patterns = [
            r".*\s2\..*",  # " 2."パターン
            r".*-2\..*",  # "-2."パターン
            r".*_2\..*",  # "_2."パターン
            r".*\s2$",  # " 2"で終わる
            r".*-2$",  # "-2"で終わる
            r".*_2$",  # "_2"で終わる
        ]

        self.exclude_patterns = [
            r".*test.*2.*",  # テストファイル
            r".*python3\.13.*",  # Python関連
            r".*\.dist-info.*",  # パッケージ情報
            r".*numpy.*2.*",  # numpy関連
            r".*pydantic.*2.*",  # pydantic関連
        ]

    def scan_for_duplicates(self):
        duplicates = []
        for root, dirs, files in os.walk(self.project_root):
            for name in dirs + files:
                if any(re.match(p, name) for p in self.duplicate_patterns):
                    full_path = os.path.join(root, name)
                    if not any(re.match(e, full_path) for e in self.exclude_patterns):
                        duplicates.append(full_path)
        return duplicates

    def auto_clean_duplicates(self):
        duplicates = self.scan_for_duplicates()
        cleaned = {"files_removed": 0, "dirs_removed": 0, "total_removed": 0}

        for dup in duplicates:
            try:
                if os.path.isfile(dup):
                    os.remove(dup)
                    cleaned["files_removed"] += 1
                    print(f"🗑️  ファイル削除: {dup}")
                elif os.path.isdir(dup):
                    import shutil

                    shutil.rmtree(dup)
                    cleaned["dirs_removed"] += 1
                    print(f"🗑️  ディレクトリ削除: {dup}")
                cleaned["total_removed"] += 1
            except Exception as e:
                print(f"⚠️  削除失敗 {dup}: {e}")

        return cleaned


def main():
    enforcer = DuplicatePreventionEnforcer()

    if len(sys.argv) > 1 and sys.argv[1] == "--clean":
        result = enforcer.auto_clean_duplicates()
        print("\n✅ 複製除去完了:")
        print(f"   📁 ディレクトリ: {result['dirs_removed']}個")
        print(f"   📄 ファイル: {result['files_removed']}個")
        print(f"   🗑️  総計: {result['total_removed']}個")
    else:
        duplicates = enforcer.scan_for_duplicates()
        if duplicates:
            print(f"🚫 {len(duplicates)}個の複製ファイルを検出:")
            for dup in duplicates[:10]:  # 最初の10個のみ表示
                print(f"   ❌ {dup}")
            if len(duplicates) > 10:
                print(f"   ... および{len(duplicates) - 10}個")
            print("\n💡 --clean で自動除去可能")
        else:
            print("✅ 複製ファイルは検出されませんでした")


if __name__ == "__main__":
    main()
