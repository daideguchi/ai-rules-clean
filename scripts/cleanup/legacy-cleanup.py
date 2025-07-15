#!/usr/bin/env python3
"""
レガシーファイル・ディレクトリのクリーンアップスクリプト
0-ROOT.ymlで非推奨とされた項目を整理
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class LegacyCleanup:
    """レガシーファイルのクリーンアップ"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.cleanup_log = []

        # 0-ROOT.ymlで非推奨とされた項目
        self.deprecated_items = {
            "directories": [
                "logs",  # runtime/に統合済み
                "bin",  # scripts/に移動済み
                "archive",  # git履歴で代替
                "cache",  # システムキャッシュ使用
                "tmp",  # システムtmp使用
                "temp",  # システムtmp使用
            ],
            "file_patterns": [
                "*backup*",
                "*old*",
                "*copy*",
                "*temp*",
                "*tmp*",
                "*.bak",
                "*.orig",
            ],
            "specific_paths": [".cursor.backup-*", ".vscode.backup-*", "docs-backup-*"],
        }

        # セーフティチェック: 重要ファイルは除外
        self.protected_items = {
            "runtime",  # 現在使用中
            "scripts",  # 重要スクリプト
            "src",  # ソースコード
            "docs",  # ドキュメント
            ".dev",  # IDE設定
            ".git",  # Git履歴
            "data",  # データ
            "models",  # モデル
            "api",  # API定義
            "compliance",  # コンプライアンス
        }

    def scan_deprecated_items(self) -> Dict:
        """非推奨項目をスキャン"""
        found_items = {"directories": [], "files": [], "backup_dirs": []}

        # ルートレベルディレクトリをスキャン
        for item in self.project_root.iterdir():
            if item.name.startswith(".") and item.name not in [".dev", ".git"]:
                continue

            if item.is_dir():
                # 非推奨ディレクトリ
                if item.name in self.deprecated_items["directories"]:
                    if item.name not in self.protected_items:
                        found_items["directories"].append(str(item))

                # バックアップディレクトリ
                if any(
                    pattern.replace("*", "") in item.name.lower()
                    for pattern in ["*backup*", "*old*"]
                ):
                    found_items["backup_dirs"].append(str(item))

            elif item.is_file():
                # 非推奨ファイル
                if any(
                    self._match_pattern(item.name, pattern)
                    for pattern in self.deprecated_items["file_patterns"]
                ):
                    found_items["files"].append(str(item))

        return found_items

    def _match_pattern(self, filename: str, pattern: str) -> bool:
        """パターンマッチング"""
        import fnmatch

        return fnmatch.fnmatch(filename.lower(), pattern.lower())

    def analyze_safety(self, items: Dict) -> Dict:
        """削除の安全性を分析"""
        analysis = {
            "safe_to_delete": {"directories": [], "files": [], "backup_dirs": []},
            "needs_review": {"directories": [], "files": [], "backup_dirs": []},
            "total_size": 0,
        }

        for category, item_list in items.items():
            for item_str in item_list:
                item = Path(item_str)
                size = self._get_size(item)
                analysis["total_size"] += size

                # 安全性判定
                if self._is_safe_to_delete(item):
                    analysis["safe_to_delete"][category].append(
                        {
                            "path": str(item),
                            "size": size,
                            "reason": self._get_deletion_reason(item),
                        }
                    )
                else:
                    analysis["needs_review"][category].append(
                        {"path": str(item), "size": size, "reason": "要手動確認"}
                    )

        return analysis

    def _get_size(self, path: Path) -> int:
        """サイズ計算"""
        if path.is_file():
            return path.stat().st_size
        elif path.is_dir():
            return sum(f.stat().st_size for f in path.rglob("*") if f.is_file())
        return 0

    def _is_safe_to_delete(self, item: Path) -> bool:
        """削除安全性判定"""
        # 保護対象チェック
        if item.name in self.protected_items:
            return False

        # バックアップファイル/ディレクトリは比較的安全
        if any(
            keyword in item.name.lower()
            for keyword in ["backup", "old", "copy", "temp", "tmp"]
        ):
            return True

        # 空ディレクトリは安全
        if item.is_dir():
            try:
                return not any(item.iterdir())
            except Exception:
                return False

        # 小さなファイルは比較的安全
        if item.is_file() and item.stat().st_size < 1024:  # 1KB未満
            return True

        return False

    def _get_deletion_reason(self, item: Path) -> str:
        """削除理由"""
        if "backup" in item.name.lower():
            return "バックアップファイル/ディレクトリ"
        elif "old" in item.name.lower():
            return "旧版ファイル"
        elif "temp" in item.name.lower() or "tmp" in item.name.lower():
            return "一時ファイル"
        elif item.name in self.deprecated_items["directories"]:
            return "0-ROOT.ymlで非推奨指定"
        else:
            return "レガシーファイル"

    def create_cleanup_plan(self) -> Dict:
        """クリーンアップ計画作成"""
        deprecated_items = self.scan_deprecated_items()
        safety_analysis = self.analyze_safety(deprecated_items)

        plan = {
            "scan_date": datetime.now().isoformat(),
            "total_items": sum(len(items) for items in deprecated_items.values()),
            "total_size_mb": safety_analysis["total_size"] / 1024 / 1024,
            "safe_items": sum(
                len(items) for items in safety_analysis["safe_to_delete"].values()
            ),
            "review_items": sum(
                len(items) for items in safety_analysis["needs_review"].values()
            ),
            "deprecated_items": deprecated_items,
            "safety_analysis": safety_analysis,
        }

        return plan

    def execute_safe_cleanup(self, plan: Dict, dry_run: bool = True) -> Dict:
        """安全なクリーンアップ実行"""
        results = {"deleted": [], "errors": [], "total_freed_mb": 0, "dry_run": dry_run}

        if not dry_run:
            # バックアップディレクトリ作成
            backup_dir = (
                self.project_root / f"cleanup-backup-{int(datetime.now().timestamp())}"
            )
            backup_dir.mkdir(exist_ok=True)
            print(f"📦 バックアップディレクトリ作成: {backup_dir}")

        safe_items = plan["safety_analysis"]["safe_to_delete"]

        for _category, items in safe_items.items():
            for item_info in items:
                item_path = Path(item_info["path"])

                try:
                    if dry_run:
                        print(
                            f"🔍 [DRY RUN] 削除予定: {item_path} ({item_info['size'] / 1024:.1f}KB)"
                        )
                        results["deleted"].append(item_info)
                        results["total_freed_mb"] += item_info["size"] / 1024 / 1024
                    else:
                        # 実際の削除前にバックアップ
                        if item_path.exists():
                            backup_target = backup_dir / item_path.name
                            if item_path.is_dir():
                                shutil.copytree(item_path, backup_target)
                                shutil.rmtree(item_path)
                            else:
                                shutil.copy2(item_path, backup_target)
                                item_path.unlink()

                            print(f"🗑️ 削除完了: {item_path}")
                            results["deleted"].append(item_info)
                            results["total_freed_mb"] += item_info["size"] / 1024 / 1024

                except Exception as e:
                    error_msg = f"❌ 削除エラー {item_path}: {e}"
                    print(error_msg)
                    results["errors"].append(error_msg)

        return results

    def generate_report(self, plan: Dict, results: Dict = None):
        """レポート生成"""
        report_path = self.project_root / "runtime" / "legacy-cleanup-report.json"

        report = {
            "cleanup_plan": plan,
            "execution_results": results,
            "recommendations": self._generate_recommendations(plan),
        }

        # runtime/ディレクトリ確保
        report_path.parent.mkdir(exist_ok=True)

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"📋 レポート保存: {report_path}")
        return report

    def _generate_recommendations(self, plan: Dict) -> List[str]:
        """改善推奨事項生成"""
        recommendations = []

        if plan["review_items"] > 0:
            recommendations.append(
                f"手動確認が必要な項目が{plan['review_items']}個あります。"
                "各項目を個別に確認してください。"
            )

        if plan["total_size_mb"] > 100:
            recommendations.append(
                f"合計{plan['total_size_mb']:.1f}MBのスペースを解放できます。"
            )

        recommendations.extend(
            [
                "定期的なクリーンアップスケジュールの設定を検討してください。",
                ".gitignoreの更新でtempファイル生成を防止してください。",
                "CI/CDパイプラインにクリーンアップステップの追加を検討してください。",
            ]
        )

        return recommendations


def main():
    """メイン実行"""
    cleanup = LegacyCleanup()

    print("🧹 レガシーファイルクリーンアップ開始")
    print("=" * 50)

    # クリーンアップ計画作成
    plan = cleanup.create_cleanup_plan()

    print("📊 スキャン結果:")
    print(f"  発見項目: {plan['total_items']}個")
    print(f"  合計サイズ: {plan['total_size_mb']:.1f}MB")
    print(f"  安全削除可能: {plan['safe_items']}個")
    print(f"  要確認: {plan['review_items']}個")

    # ドライラン実行
    print("\n🔍 ドライラン実行...")
    dry_results = cleanup.execute_safe_cleanup(plan, dry_run=True)

    print(f"\n💾 削除により解放されるスペース: {dry_results['total_freed_mb']:.1f}MB")

    # レポート生成
    cleanup.generate_report(plan, dry_results)

    print("\n📝 次のステップ:")
    print("1. レポートを確認: runtime/legacy-cleanup-report.json")
    print("2. 実際のクリーンアップ: python3 scripts/legacy-cleanup.py --execute")
    print("3. 手動確認項目の個別チェック")

    print("\n✅ レガシーファイル分析完了")


if __name__ == "__main__":
    import sys

    if "--execute" in sys.argv:
        print("⚠️ 実際のクリーンアップは安全性確認のため段階的に実装予定")
    else:
        main()
