#!/usr/bin/env python3
"""
[LEGACY WRAPPER] Simple Log Analyzer

このスクリプトは unified-monitoring-tool.py に統合されました。
Phase 4 統合完了 - レガシー互換性のためのwrapperスクリプト

新しい使用方法:
  scripts/tools/unified-monitoring-tool.py analyze
"""

import gzip
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Tuple

print("⚠️  [LEGACY] simple-log-analyzer.py は統合されました")
print("📦 unified-monitoring-tool.py analyze に移行してください")
print("")
print("🔄 自動転送中...")

# 統合ツールの実行
script_dir = Path(__file__).parent
unified_tool = script_dir.parent / "unified-monitoring-tool.py"

# 引数変換
args = sys.argv[1:] if len(sys.argv) > 1 else ["analyze"]
if args[0] in ["analyze", "cleanup", "rotate", "all"]:
    new_args = ["analyze"] + args[1:]
else:
    new_args = ["analyze"] + args

os.execv(sys.executable, [sys.executable, str(unified_tool)] + new_args)


class SimpleLogAnalyzer:
    """シンプルログ分析システム"""

    def __init__(self, log_root: str = "runtime/logs"):
        self.log_root = Path(log_root)
        if not self.log_root.exists():
            self.log_root.mkdir(parents=True, exist_ok=True)

        print(f"🔍 SimpleLogAnalyzer初期化完了 - ログルート: {self.log_root}")

    def analyze_logs(self) -> Dict[str, Any]:
        """ログ分析実行"""
        print("📊 ログ分析開始...")

        stats = {
            "total_files": 0,
            "total_size_mb": 0,
            "file_types": {},
            "large_files": [],
            "old_files": [],
            "errors_found": 0,
            "warnings_found": 0,
        }

        for log_file in self.log_root.rglob("*"):
            if not log_file.is_file():
                continue

            stats["total_files"] += 1
            file_size = log_file.stat().st_size
            stats["total_size_mb"] += file_size / (1024 * 1024)

            # ファイルタイプ統計
            suffix = log_file.suffix.lower()
            stats["file_types"][suffix] = stats["file_types"].get(suffix, 0) + 1

            # 大きなファイル検出
            if file_size > 10 * 1024 * 1024:  # 10MB以上
                stats["large_files"].append(
                    {
                        "file": str(log_file.relative_to(self.log_root)),
                        "size_mb": round(file_size / (1024 * 1024), 2),
                    }
                )

            # 古いファイル検出
            mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
            if datetime.now() - mtime > timedelta(days=30):
                stats["old_files"].append(
                    {
                        "file": str(log_file.relative_to(self.log_root)),
                        "age_days": (datetime.now() - mtime).days,
                    }
                )

            # ログ内容分析（テキストファイルのみ）
            if suffix in [".log", ".txt"]:
                error_count, warning_count = self._analyze_log_content(log_file)
                stats["errors_found"] += error_count
                stats["warnings_found"] += warning_count

        # 分析結果
        result = {
            "analysis_time": datetime.now().isoformat(),
            "statistics": stats,
            "recommendations": self._generate_recommendations(stats),
        }

        print(
            f"✅ ログ分析完了 - {stats['total_files']}ファイル, {stats['total_size_mb']:.1f}MB"
        )
        return result

    def _analyze_log_content(self, log_file: Path) -> Tuple[int, int]:
        """ログ内容の分析"""
        error_count = 0
        warning_count = 0

        try:
            with open(log_file, encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line_lower = line.lower()
                    if "error" in line_lower or "fatal" in line_lower:
                        error_count += 1
                    elif "warning" in line_lower or "warn" in line_lower:
                        warning_count += 1
        except Exception:
            pass  # ファイル読み込みエラーは無視

        return error_count, warning_count

    def _generate_recommendations(self, stats: Dict[str, Any]) -> List[str]:
        """推奨事項生成"""
        recommendations = []

        # 大容量ファイル
        if len(stats["large_files"]) > 0:
            recommendations.append(
                f"🗂️ 大容量ログファイル {len(stats['large_files'])}個 - ローテーション推奨"
            )

        # 古いファイル
        if len(stats["old_files"]) > 5:
            recommendations.append(
                f"🗑️ 古いログファイル {len(stats['old_files'])}個 - クリーンアップ推奨"
            )

        # エラー数
        if stats["errors_found"] > 100:
            recommendations.append(
                f"🚨 多数のエラー検出 ({stats['errors_found']}件) - 調査が必要"
            )

        # 警告数
        if stats["warnings_found"] > 500:
            recommendations.append(
                f"⚠️ 多数の警告検出 ({stats['warnings_found']}件) - 確認推奨"
            )

        # 総サイズ
        if stats["total_size_mb"] > 100:
            recommendations.append(
                f"💾 ログサイズ大 ({stats['total_size_mb']:.1f}MB) - アーカイブ推奨"
            )

        if not recommendations:
            recommendations.append("✅ ログ状態は良好です")

        return recommendations

    def cleanup_old_logs(self, days: int = 30) -> Dict[str, Any]:
        """古いログのクリーンアップ"""
        print(f"🧹 {days}日以上経過したログをクリーンアップ中...")

        cutoff_date = datetime.now() - timedelta(days=days)
        deleted_files = []
        freed_space_mb = 0

        for log_file in self.log_root.rglob("*.log"):
            if not log_file.is_file():
                continue

            mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
            if mtime < cutoff_date:
                file_size = log_file.stat().st_size
                freed_space_mb += file_size / (1024 * 1024)
                deleted_files.append(str(log_file.relative_to(self.log_root)))

                try:
                    log_file.unlink()
                except Exception as e:
                    print(f"❌ 削除失敗: {log_file} - {e}")

        result = {
            "cleaned_files": len(deleted_files),
            "files": deleted_files,
            "freed_space_mb": round(freed_space_mb, 2),
            "cutoff_days": days,
        }

        print(
            f"✅ クリーンアップ完了 - {len(deleted_files)}ファイル削除, {freed_space_mb:.1f}MB解放"
        )
        return result

    def rotate_large_logs(self, max_size_mb: int = 10) -> Dict[str, Any]:
        """大容量ログのローテーション"""
        print(f"🔄 {max_size_mb}MB以上のログをローテーション中...")

        rotated_files = []
        max_size_bytes = max_size_mb * 1024 * 1024

        for log_file in self.log_root.rglob("*.log"):
            if not log_file.is_file():
                continue

            if log_file.stat().st_size > max_size_bytes:
                rotated_path = self._rotate_file(log_file)
                if rotated_path:
                    rotated_files.append(
                        {
                            "original": str(log_file.relative_to(self.log_root)),
                            "rotated": str(rotated_path.relative_to(self.log_root)),
                        }
                    )

        result = {
            "rotated_files": len(rotated_files),
            "files": rotated_files,
            "max_size_mb": max_size_mb,
        }

        print(f"✅ ローテーション完了 - {len(rotated_files)}ファイル")
        return result

    def _rotate_file(self, log_file: Path) -> Path:
        """単一ファイルのローテーション"""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        rotated_name = f"{log_file.stem}-{timestamp}.log.gz"
        rotated_path = log_file.parent / rotated_name

        try:
            # gzip圧縮
            with open(log_file, "rb") as f_in:
                with gzip.open(rotated_path, "wb") as f_out:
                    f_out.writelines(f_in)

            # 元ファイルをクリア
            log_file.write_text("")
            return rotated_path

        except Exception as e:
            print(f"❌ ローテーション失敗: {log_file} - {e}")
            return None


def main():
    """メイン実行"""
    import argparse

    parser = argparse.ArgumentParser(description="Simple Log Analyzer")
    parser.add_argument(
        "action",
        choices=["analyze", "cleanup", "rotate", "all"],
        help="実行するアクション",
    )
    parser.add_argument(
        "--log-root", default="runtime/logs", help="ログルートディレクトリ"
    )
    parser.add_argument("--days", type=int, default=30, help="クリーンアップ日数")
    parser.add_argument(
        "--max-size", type=int, default=10, help="ローテーションサイズ(MB)"
    )

    args = parser.parse_args()

    analyzer = SimpleLogAnalyzer(args.log_root)

    if args.action == "analyze" or args.action == "all":
        result = analyzer.analyze_logs()
        print("\n" + "=" * 60)
        print("📊 ログ分析結果")
        print("=" * 60)
        print(f"📁 総ファイル数: {result['statistics']['total_files']}")
        print(f"💾 総サイズ: {result['statistics']['total_size_mb']:.1f} MB")
        print(f"🚨 エラー数: {result['statistics']['errors_found']}")
        print(f"⚠️ 警告数: {result['statistics']['warnings_found']}")
        print(f"📈 大容量ファイル: {len(result['statistics']['large_files'])}")
        print(f"🗓️ 古いファイル: {len(result['statistics']['old_files'])}")
        print("\n🎯 推奨事項:")
        for rec in result["recommendations"]:
            print(f"  {rec}")
        print("=" * 60)

    if args.action == "cleanup" or args.action == "all":
        cleanup_result = analyzer.cleanup_old_logs(args.days)
        print(f"\n🧹 クリーンアップ完了: {cleanup_result['cleaned_files']}ファイル削除")

    if args.action == "rotate" or args.action == "all":
        rotate_result = analyzer.rotate_large_logs(args.max_size)
        print(f"\n🔄 ローテーション完了: {rotate_result['rotated_files']}ファイル")


if __name__ == "__main__":
    main()
