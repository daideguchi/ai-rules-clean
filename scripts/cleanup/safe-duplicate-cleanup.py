#!/usr/bin/env python3
"""
O3推奨の安全措置を実装した重複ファイルクリーンアップ
SHA-256検証 + 参照スキャン + 段階的隔離
"""

import hashlib
import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class SafeDuplicateCleanup:
    """O3推奨の安全措置を実装した重複クリーンアップ"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.quarantine_dir = (
            self.project_root
            / ".archive"
            / "duplicates"
            / f"{datetime.now().strftime('%Y%m%d')}"
        )

        # 保護対象ディレクトリ
        self.protected_dirs = {
            "src",
            "docs",
            ".git",
            "runtime",
            "data",
            "models",
            "api",
            "compliance",
            ".dev",
            "tests",
            "scripts",
            # ENHANCED: Memory inheritance system protection
            "src/memory",
            "runtime/ai_api_logs",
            "runtime/secure_state",
            "runtime/backups",
            "runtime/wal_archives",
            ".claude",
        }

        # 検索対象拡張子（参照スキャン用）
        self.code_extensions = {
            "*.py",
            "*.sh",
            "*.js",
            "*.ts",
            "*.json",
            "*.yaml",
            "*.yml",
            "*.md",
            "*.toml",
            "*.cfg",
            "*.ini",
        }

    def calculate_file_hash(self, file_path: Path) -> str:
        """SHA-256ハッシュ計算"""
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except Exception as e:
            print(f"⚠️ ハッシュ計算エラー {file_path}: {e}")
            return ""

    def find_true_duplicates(self) -> Dict[str, List[str]]:
        """SHA-256ベースの真の重複検出"""
        print("🔍 SHA-256ベース重複スキャン開始...")

        hash_groups = {}
        total_files = 0

        # 全ファイルをスキャン
        for file_path in self.project_root.rglob("*"):
            if not file_path.is_file():
                continue

            # 保護対象ディレクトリはスキップ
            if any(protected in file_path.parts for protected in self.protected_dirs):
                continue

            # 隠しファイル・システムファイルはスキップ
            if file_path.name.startswith(".") and file_path.name not in [
                ".gitignore",
                ".editorconfig",
            ]:
                continue

            file_hash = self.calculate_file_hash(file_path)
            if file_hash:
                if file_hash not in hash_groups:
                    hash_groups[file_hash] = []
                hash_groups[file_hash].append(str(file_path))
                total_files += 1

        # 重複のみ抽出
        true_duplicates = {
            hash_val: paths for hash_val, paths in hash_groups.items() if len(paths) > 1
        }

        print(
            f"📊 スキャン結果: {total_files}ファイル, {len(true_duplicates)}個のハッシュグループで重複"
        )
        return true_duplicates

    def scan_code_references(self, file_paths: List[str]) -> Dict[str, List[Dict]]:
        """コード内の参照スキャン"""
        print("🔍 コード参照スキャン開始...")

        references = {}

        for file_path in file_paths:
            file_name = Path(file_path).name
            str(Path(file_path).relative_to(self.project_root))

            # ripgrepで参照を検索
            try:
                # ファイル名での検索
                result = subprocess.run(
                    [
                        "rg",
                        "--json",
                        "--type-add",
                        "code:*.{py,sh,js,ts,json,yaml,yml,md,toml,cfg,ini}",
                        "--type",
                        "code",
                        file_name,
                    ],
                    capture_output=True,
                    text=True,
                    cwd=self.project_root,
                )

                if result.returncode == 0:
                    refs = []
                    for line in result.stdout.strip().split("\n"):
                        if line:
                            try:
                                data = json.loads(line)
                                if data.get("type") == "match":
                                    refs.append(
                                        {
                                            "file": data["data"]["path"]["text"],
                                            "line": data["data"]["line_number"],
                                            "content": data["data"]["lines"][
                                                "text"
                                            ].strip(),
                                        }
                                    )
                            except Exception:
                                continue

                    if refs:
                        references[file_path] = refs

            except Exception as e:
                print(f"⚠️ 参照スキャンエラー {file_path}: {e}")

        return references

    def select_canonical_files(
        self, duplicates: Dict[str, List[str]]
    ) -> Dict[str, Dict]:
        """重複グループから保持すべきファイルを選択"""
        cleanup_plan = {}

        for hash_val, file_paths in duplicates.items():
            if len(file_paths) < 2:
                continue

            # 優先順位ルール
            def priority_score(path: str) -> int:
                path_obj = Path(path)
                score = 0

                # 1. より浅い階層を優先
                score += 100 - len(path_obj.parts)

                # 2. 特定ディレクトリを優先
                if "docs/" in path:
                    score += 50
                elif "src/" in path:
                    score += 40
                elif "scripts/" in path:
                    score += 30

                # 3. READMEは親ディレクトリを優先
                if path_obj.name == "README.md":
                    score += 20

                # 4. バックアップ・古いファイルを除外
                if any(
                    keyword in path.lower()
                    for keyword in ["backup", "old", "copy", "temp"]
                ):
                    score -= 100

                return score

            # 最高スコアのファイルを正規版として選択
            sorted_paths = sorted(file_paths, key=priority_score, reverse=True)
            canonical = sorted_paths[0]
            duplicates_to_remove = sorted_paths[1:]

            cleanup_plan[hash_val] = {
                "canonical": canonical,
                "duplicates": duplicates_to_remove,
                "file_count": len(file_paths),
                "size_bytes": Path(canonical).stat().st_size
                if Path(canonical).exists()
                else 0,
            }

        return cleanup_plan

    def create_quarantine_plan(self) -> Dict:
        """隔離計画作成"""
        print("📋 安全な隔離計画作成中...")

        # 1. 真の重複検出
        true_duplicates = self.find_true_duplicates()

        # 2. 正規ファイル選択
        cleanup_plan = self.select_canonical_files(true_duplicates)

        # 3. 削除予定ファイルリスト作成
        files_to_quarantine = []
        for group in cleanup_plan.values():
            files_to_quarantine.extend(group["duplicates"])

        # 4. 参照スキャン
        references = self.scan_code_references(files_to_quarantine)

        # 5. 最終計画
        plan = {
            "created": datetime.now().isoformat(),
            "total_duplicate_groups": len(cleanup_plan),
            "total_files_to_quarantine": len(files_to_quarantine),
            "total_size_mb": sum(group["size_bytes"] for group in cleanup_plan.values())
            / 1024
            / 1024,
            "cleanup_plan": cleanup_plan,
            "code_references": references,
            "quarantine_directory": str(self.quarantine_dir),
            "safety_status": self._assess_safety(references),
        }

        return plan

    def _assess_safety(self, references: Dict) -> Dict:
        """安全性評価"""
        total_refs = sum(len(refs) for refs in references.values())

        if total_refs == 0:
            status = "SAFE"
            risk_level = "LOW"
        elif total_refs < 5:
            status = "CAUTION"
            risk_level = "MEDIUM"
        else:
            status = "REVIEW_REQUIRED"
            risk_level = "HIGH"

        return {
            "status": status,
            "risk_level": risk_level,
            "total_references": total_refs,
            "referenced_files": len(references),
            "recommendation": self._get_safety_recommendation(status),
        }

    def _get_safety_recommendation(self, status: str) -> str:
        """安全性推奨"""
        recommendations = {
            "SAFE": "隔離実行可能。参照なしで安全です。",
            "CAUTION": "少数の参照あり。手動確認後に隔離実行。",
            "REVIEW_REQUIRED": "多数の参照あり。各参照を詳細確認後に段階的実行。",
        }
        return recommendations.get(status, "要詳細分析")

    def execute_quarantine(self, plan: Dict, dry_run: bool = True) -> Dict:
        """隔離実行"""
        if dry_run:
            print("🔍 [DRY RUN] 隔離シミュレーション")
        else:
            print("📦 隔離実行開始")
            self.quarantine_dir.mkdir(parents=True, exist_ok=True)

        results = {
            "quarantined_files": [],
            "errors": [],
            "total_freed_mb": 0,
            "dry_run": dry_run,
        }

        for _hash_val, group in plan["cleanup_plan"].items():
            for duplicate_path in group["duplicates"]:
                try:
                    source = Path(duplicate_path)
                    if not source.exists():
                        continue

                    if dry_run:
                        print(f"🔍 [DRY RUN] 隔離予定: {duplicate_path}")
                        results["quarantined_files"].append(duplicate_path)
                        results["total_freed_mb"] += group["size_bytes"] / 1024 / 1024
                    else:
                        # 隔離先パス計算
                        relative_path = source.relative_to(self.project_root)
                        quarantine_target = self.quarantine_dir / relative_path

                        # ディレクトリ作成
                        quarantine_target.parent.mkdir(parents=True, exist_ok=True)

                        # ファイル移動
                        shutil.move(str(source), str(quarantine_target))
                        print(f"📦 隔離完了: {duplicate_path}")

                        results["quarantined_files"].append(duplicate_path)
                        results["total_freed_mb"] += group["size_bytes"] / 1024 / 1024

                except Exception as e:
                    error_msg = f"❌ 隔離エラー {duplicate_path}: {e}"
                    print(error_msg)
                    results["errors"].append(error_msg)

        return results

    def save_plan(self, plan: Dict, results: Dict = None):
        """計画保存"""
        runtime_dir = self.project_root / "runtime"
        runtime_dir.mkdir(exist_ok=True)

        plan_file = (
            runtime_dir
            / f"duplicate-cleanup-plan-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        )

        full_report = {
            "plan": plan,
            "execution_results": results,
            "o3_recommendations_implemented": [
                "SHA-256 hash verification",
                "Code reference scanning",
                "Quarantine phase implementation",
                "Protected directory exclusion",
                "Safety assessment",
            ],
        }

        with open(plan_file, "w", encoding="utf-8") as f:
            json.dump(full_report, f, indent=2, ensure_ascii=False)

        print(f"📋 計画保存: {plan_file}")
        return plan_file


def main():
    """メイン実行"""
    cleanup = SafeDuplicateCleanup()

    print("🛡️ O3推奨安全措置付き重複クリーンアップ")
    print("=" * 60)

    # 隔離計画作成
    plan = cleanup.create_quarantine_plan()

    # 結果表示
    print("\n📊 隔離計画:")
    print(f"  重複グループ: {plan['total_duplicate_groups']}")
    print(f"  隔離対象ファイル: {plan['total_files_to_quarantine']}")
    print(f"  解放予定容量: {plan['total_size_mb']:.2f}MB")
    print(f"  コード参照: {plan['safety_status']['total_references']}件")
    print(
        f"  安全性: {plan['safety_status']['status']} ({plan['safety_status']['risk_level']})"
    )
    print(f"  推奨: {plan['safety_status']['recommendation']}")

    # ドライラン
    print("\n🔍 ドライラン実行...")
    dry_results = cleanup.execute_quarantine(plan, dry_run=True)

    # 計画保存
    plan_file = cleanup.save_plan(plan, dry_results)

    # 実行判定
    if plan["safety_status"]["status"] == "SAFE":
        print("\n✅ 安全性確認: 隔離実行可能")
        print(f"実行コマンド: python3 {__file__} --execute")
    else:
        print(f"\n⚠️ 要確認: {plan['safety_status']['recommendation']}")
        print(f"詳細確認: {plan_file}")

    print("\n🎯 O3推奨措置完了:")
    print("  ✅ SHA-256ハッシュ検証")
    print("  ✅ コード参照スキャン")
    print("  ✅ 段階的隔離計画")
    print("  ✅ 安全性評価")


if __name__ == "__main__":
    import sys

    if "--execute" in sys.argv:
        cleanup = SafeDuplicateCleanup()
        plan = cleanup.create_quarantine_plan()

        if plan["safety_status"]["status"] == "SAFE":
            print("🚀 隔離実行開始...")
            results = cleanup.execute_quarantine(plan, dry_run=False)
            cleanup.save_plan(plan, results)
            print("✅ 隔離完了")
        else:
            print("❌ 安全性確認が必要です。手動確認後に実行してください。")
    else:
        main()
