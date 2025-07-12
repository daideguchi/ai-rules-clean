#!/usr/bin/env python3
"""
ルール重複分析スクリプト
docs/とcode内のルール・ナレッジの重複を検出し統合提案を生成
"""

import hashlib
import json
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple


class RuleDuplicateAnalyzer:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.rule_files = []
        self.content_hashes = {}
        self.duplicates = []

    def find_rule_files(self) -> List[Path]:
        """ルール関連ファイルを検索"""
        patterns = [
            "**/*.mdc",
            "**/CLAUDE.md",
            "**/README.md",
            "**/*rules*",
            "**/*guideline*",
            "**/*standard*",
        ]

        rule_files = []
        for pattern in patterns:
            rule_files.extend(self.project_root.glob(pattern))

        # 除外パターン
        excludes = {".git", "node_modules", "__pycache__", ".pytest_cache"}

        return [f for f in rule_files if not any(exc in str(f) for exc in excludes)]

    def extract_rules(self, file_path: Path) -> List[str]:
        """ファイルからルール記述を抽出"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"❌ Error reading {file_path}: {e}")
            return []

        # ルール記述パターンを抽出
        rule_patterns = [
            r"[#*-] .{10,}",  # リスト項目
            r"```[^`]+```",  # コードブロック
            r"> .{10,}",  # 引用
            r"## .{5,}",  # セクションヘッダー
        ]

        rules = []
        for pattern in rule_patterns:
            matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
            rules.extend(matches)

        return [self.normalize_rule(rule) for rule in rules if len(rule.strip()) > 10]

    def normalize_rule(self, rule: str) -> str:
        """ルールテキストを正規化"""
        # 記号・空白の正規化
        normalized = re.sub(r"[#*-] ", "", rule)
        normalized = re.sub(r"\s+", " ", normalized.strip())
        normalized = normalized.lower()

        # コードブロック内の変数を統一
        normalized = re.sub(r"\$\{[^}]+\}", "${VAR}", normalized)
        normalized = re.sub(r"\w+\.\w+", "file.ext", normalized)

        return normalized

    def calculate_similarity(self, rule1: str, rule2: str) -> float:
        """2つのルール間の類似度を計算"""
        from difflib import SequenceMatcher

        return SequenceMatcher(None, rule1, rule2).ratio()

    def find_duplicates(self, threshold: float = 0.8) -> List[Tuple]:
        """重複ルールを検出（効率化版）"""
        all_rules = {}

        # 全ファイルからルールを収集（サイズ制限）
        total_rules = 0
        for file_path in self.rule_files:
            if total_rules > 1000:  # 処理制限
                print("⚠️ ルール数制限到達、処理を制限します")
                break

            rules = self.extract_rules(file_path)
            # 長すぎるルールは除外
            rules = [r for r in rules if len(r) < 500]
            all_rules[file_path] = rules[:20]  # ファイルあたり最大20ルール
            total_rules += len(rules)

            print(f"📄 {file_path.name}: {len(rules)}ルール")

        duplicates = []

        # ハッシュベース事前フィルタリング
        rule_hashes = {}
        for file_path, rules in all_rules.items():
            for rule in rules:
                rule_hash = hashlib.md5(rule.encode()).hexdigest()[:8]
                if rule_hash not in rule_hashes:
                    rule_hashes[rule_hash] = []
                rule_hashes[rule_hash].append((file_path, rule))

        # 同一ハッシュグループのみ詳細比較
        processed_pairs = set()

        for _hash_val, rule_list in rule_hashes.items():
            if len(rule_list) < 2:
                continue

            # グループ内比較
            for i in range(len(rule_list)):
                for j in range(i + 1, len(rule_list)):
                    file1, rule1 = rule_list[i]
                    file2, rule2 = rule_list[j]

                    # 同一ファイルは除外
                    if file1 == file2:
                        continue

                    pair_key = tuple(
                        sorted([str(file1), str(file2), rule1[:50], rule2[:50]])
                    )
                    if pair_key in processed_pairs:
                        continue
                    processed_pairs.add(pair_key)

                    similarity = self.calculate_similarity(rule1, rule2)

                    if similarity >= threshold:
                        duplicates.append(
                            {
                                "similarity": similarity,
                                "file1": str(file1),
                                "file2": str(file2),
                                "rule1": rule1[:100] + "..."
                                if len(rule1) > 100
                                else rule1,
                                "rule2": rule2[:100] + "..."
                                if len(rule2) > 100
                                else rule2,
                            }
                        )

        return duplicates

    def generate_consolidation_plan(self) -> Dict:
        """統合計画を生成"""
        plan = {
            "current_files": len(self.rule_files),
            "duplicates_found": len(self.duplicates),
            "recommendations": [],
        }

        # 重複度の高いファイルペアを特定
        file_pairs = {}
        for dup in self.duplicates:
            pair = tuple(sorted([dup["file1"], dup["file2"]]))
            if pair not in file_pairs:
                file_pairs[pair] = []
            file_pairs[pair].append(dup["similarity"])

        # 統合推奨
        for (file1, file2), similarities in file_pairs.items():
            avg_similarity = sum(similarities) / len(similarities)
            if avg_similarity > 0.7:
                plan["recommendations"].append(
                    {
                        "action": "merge",
                        "files": [file1, file2],
                        "avg_similarity": avg_similarity,
                        "duplicate_count": len(similarities),
                    }
                )

        return plan

    def run_analysis(self) -> Dict:
        """全体分析を実行"""
        print("🔍 ルール重複分析開始...")

        # ファイル検索
        self.rule_files = self.find_rule_files()
        print(f"📁 発見ファイル: {len(self.rule_files)}")

        # 重複検出
        self.duplicates = self.find_duplicates()
        print(f"🔍 重複検出: {len(self.duplicates)}件")

        # 統合計画生成
        plan = self.generate_consolidation_plan()

        return {
            "files_analyzed": [str(f) for f in self.rule_files],
            "duplicates": self.duplicates,
            "consolidation_plan": plan,
        }


def main():
    analyzer = RuleDuplicateAnalyzer()
    results = analyzer.run_analysis()

    # 結果をJSONで保存
    output_file = "runtime/rule-analysis-results.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"📊 分析結果を保存: {output_file}")

    # 重要な発見をサマリー表示
    duplicates = results["duplicates"]
    plan = results["consolidation_plan"]

    print("\n📋 分析サマリー:")
    print(f"  対象ファイル: {len(results['files_analyzed'])}")
    print(f"  重複検出: {len(duplicates)}件")
    print(f"  統合推奨: {len(plan['recommendations'])}ペア")

    if duplicates:
        print("\n🔍 主要な重複:")
        for dup in sorted(duplicates, key=lambda x: x["similarity"], reverse=True)[:5]:
            print(
                f"  {dup['similarity']:.2f}: {Path(dup['file1']).name} ↔ {Path(dup['file2']).name}"
            )

    if plan["recommendations"]:
        print("\n💡 統合推奨:")
        for rec in plan["recommendations"]:
            files = [Path(f).name for f in rec["files"]]
            print(f"  {files[0]} + {files[1]} (類似度: {rec['avg_similarity']:.2f})")


if __name__ == "__main__":
    main()
