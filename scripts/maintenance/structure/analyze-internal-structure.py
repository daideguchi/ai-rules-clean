#!/usr/bin/env python3
"""
内部構造分析 - 散在スクリプト・ドキュメント調査
ディレクトリ内部の整理状況と問題点を洗い出し
"""

import json
import os
from collections import defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class InternalStructureAnalyzer:
    def __init__(self):
        self.problems = []
        self.duplicates = []
        self.scattered_scripts = []
        self.scattered_docs = []
        self.naming_violations = []
        self.structure_violations = []

    def analyze_all(self):
        print("🔍 内部構造分析開始...")

        # 1. スクリプトファイル分析
        self.analyze_scripts()

        # 2. ドキュメントファイル分析
        self.analyze_documents()

        # 3. 命名規則違反
        self.analyze_naming_conventions()

        # 4. 構造違反
        self.analyze_structure_violations()

        # 5. 重複ファイル検出
        self.detect_duplicates()

        # 6. レポート生成
        self.generate_report()

    def analyze_scripts(self):
        """スクリプトファイルの散在分析"""
        print("📜 スクリプトファイル分析中...")

        script_extensions = {".sh", ".py", ".js", ".mjs", ".ts"}
        script_locations = defaultdict(list)

        for root, dirs, files in os.walk(ROOT):
            # .git, node_modules等は除外
            dirs[:] = [d for d in dirs if not d.startswith(".") and d != "node_modules"]

            for file in files:
                if any(file.endswith(ext) for ext in script_extensions):
                    rel_path = Path(root).relative_to(ROOT)
                    script_locations[str(rel_path)].append(file)

        # 問題のあるスクリプト配置を特定
        for location, scripts in script_locations.items():
            if location == "scripts":
                continue  # 正しい配置

            # src/以外にあるスクリプト（実行可能ファイル）
            if not location.startswith("src") and len(scripts) > 0:
                for script in scripts:
                    script_path = Path(ROOT) / location / script
                    if script_path.suffix in {
                        ".sh",
                        ".py",
                    } and self.is_executable_script(script_path):
                        self.scattered_scripts.append(
                            {
                                "file": script,
                                "current_location": location,
                                "should_be": "scripts/",
                                "type": "executable_script",
                            }
                        )

    def analyze_documents(self):
        """ドキュメントファイルの散在分析"""
        print("📚 ドキュメントファイル分析中...")

        doc_extensions = {".md", ".txt", ".rst"}
        doc_locations = defaultdict(list)

        for root, dirs, files in os.walk(ROOT):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d != "node_modules"]

            for file in files:
                if any(file.endswith(ext) for ext in doc_extensions):
                    rel_path = Path(root).relative_to(ROOT)
                    doc_locations[str(rel_path)].append(file)

        # ドキュメント散在問題を特定
        for location, docs in doc_locations.items():
            if location.startswith("docs"):
                continue  # 正しい配置

            for doc in docs:
                if doc not in ["README.md"]:  # ルートのREADMEは除外
                    self.scattered_docs.append(
                        {
                            "file": doc,
                            "current_location": location,
                            "should_be": self.determine_doc_destination(doc, location),
                            "type": "scattered_document",
                        }
                    )

    def analyze_naming_conventions(self):
        """命名規則違反分析"""
        print("🏷️  命名規則分析中...")

        for root, dirs, files in os.walk(ROOT):
            if ".git" in root or "node_modules" in root:
                continue

            rel_path = Path(root).relative_to(ROOT)

            # ディレクトリ命名チェック
            for dir_name in dirs:
                if not self.is_kebab_case(dir_name) and not dir_name.startswith("."):
                    self.naming_violations.append(
                        {
                            "path": str(rel_path / dir_name),
                            "type": "directory",
                            "violation": "not_kebab_case",
                            "suggested": self.to_kebab_case(dir_name),
                        }
                    )

            # ファイル命名チェック
            for file_name in files:
                if not self.is_valid_filename(file_name):
                    self.naming_violations.append(
                        {
                            "path": str(rel_path / file_name),
                            "type": "file",
                            "violation": "invalid_naming",
                            "suggested": self.suggest_filename(file_name),
                        }
                    )

    def analyze_structure_violations(self):
        """構造規則違反分析"""
        print("🏗️  構造規則分析中...")

        # 深すぎる階層
        for root, _dirs, _files in os.walk(ROOT):
            if ".git" in root or "node_modules" in root:
                continue

            depth = len(Path(root).relative_to(ROOT).parts)
            if depth > 5:  # 5階層を超える
                self.structure_violations.append(
                    {
                        "path": str(Path(root).relative_to(ROOT)),
                        "type": "excessive_depth",
                        "depth": depth,
                        "max_allowed": 5,
                    }
                )

        # 空ディレクトリ
        for root, dirs, files in os.walk(ROOT):
            if ".git" in root or "node_modules" in root:
                continue

            if not dirs and not files:
                self.structure_violations.append(
                    {
                        "path": str(Path(root).relative_to(ROOT)),
                        "type": "empty_directory",
                    }
                )

    def detect_duplicates(self):
        """重複ファイル検出"""
        print("🔄 重複ファイル検出中...")

        file_contents = defaultdict(list)

        for root, _dirs, files in os.walk(ROOT):
            if ".git" in root or "node_modules" in root:
                continue

            for file in files:
                file_path = Path(root) / file
                if file_path.suffix in {".md", ".sh", ".py", ".js"}:
                    try:
                        with open(file_path, encoding="utf-8", errors="ignore") as f:
                            content_hash = hash(f.read())
                            file_contents[content_hash].append(
                                str(file_path.relative_to(ROOT))
                            )
                    except Exception:
                        continue

        # 重複を特定
        for _content_hash, paths in file_contents.items():
            if len(paths) > 1:
                self.duplicates.append({"files": paths, "count": len(paths)})

    def is_executable_script(self, path):
        """実行可能スクリプトかチェック"""
        try:
            with open(path, encoding="utf-8", errors="ignore") as f:
                first_line = f.readline()
                return first_line.startswith("#!") or "main" in f.read()
        except Exception:
            return False

    def determine_doc_destination(self, doc_name, current_location):
        """ドキュメントの適切な配置先を決定"""
        if "README" in doc_name.upper():
            return f"docs/misc/{doc_name}"
        elif any(word in doc_name.upper() for word in ["RULE", "POLICY", "GOVERNANCE"]):
            return f"docs/rules/{doc_name}"
        elif any(word in doc_name.upper() for word in ["REPORT", "LOG", "ANALYSIS"]):
            return f"docs/reports/{doc_name}"
        elif any(
            word in doc_name.upper() for word in ["SPEC", "DESIGN", "ARCHITECTURE"]
        ):
            return f"docs/developer/{doc_name}"
        else:
            return f"docs/misc/{doc_name}"

    def is_kebab_case(self, name):
        """ケバブケースかチェック"""
        return (
            name.replace("-", "").replace("_", "").replace(".", "").isalnum()
            and name.islower()
        )

    def to_kebab_case(self, name):
        """ケバブケースに変換"""
        import re

        return re.sub(r"[^a-z0-9\-\.]", "-", name.lower()).strip("-")

    def is_valid_filename(self, filename):
        """有効なファイル名かチェック"""
        if filename.startswith("."):
            return True  # 隠しファイルは除外
        base_name = filename.split(".")[0]
        return self.is_kebab_case(base_name)

    def suggest_filename(self, filename):
        """適切なファイル名を提案"""
        parts = filename.split(".")
        base_name = self.to_kebab_case(parts[0])
        if len(parts) > 1:
            return f"{base_name}.{'.'.join(parts[1:])}"
        return base_name

    def generate_report(self):
        """分析レポート生成"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "scattered_scripts": len(self.scattered_scripts),
                "scattered_documents": len(self.scattered_docs),
                "naming_violations": len(self.naming_violations),
                "structure_violations": len(self.structure_violations),
                "duplicate_groups": len(self.duplicates),
            },
            "problems": {
                "scattered_scripts": self.scattered_scripts,
                "scattered_documents": self.scattered_docs,
                "naming_violations": self.naming_violations,
                "structure_violations": self.structure_violations,
                "duplicates": self.duplicates,
            },
        }

        # JSONレポート保存
        report_path = (
            ROOT
            / "runtime"
            / f"internal-structure-analysis-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        )
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        # 結果表示
        print("\n📊 内部構造分析結果:")
        print(f"   🔀 散在スクリプト: {len(self.scattered_scripts)}個")
        print(f"   📄 散在ドキュメント: {len(self.scattered_docs)}個")
        print(f"   🏷️  命名規則違反: {len(self.naming_violations)}個")
        print(f"   🏗️  構造規則違反: {len(self.structure_violations)}個")
        print(f"   🔄 重複ファイル群: {len(self.duplicates)}組")

        print(f"\n📋 詳細レポート: {report_path}")

        # 重要な問題を強調表示
        if self.scattered_scripts:
            print("\n⚠️  散在スクリプト例:")
            for script in self.scattered_scripts[:3]:
                print(
                    f"   📜 {script['current_location']}/{script['file']} → {script['should_be']}"
                )

        if self.scattered_docs:
            print("\n⚠️  散在ドキュメント例:")
            for doc in self.scattered_docs[:3]:
                print(
                    f"   📄 {doc['current_location']}/{doc['file']} → {doc['should_be']}"
                )

        return report_path


def main():
    analyzer = InternalStructureAnalyzer()
    analyzer.analyze_all()


if __name__ == "__main__":
    main()
