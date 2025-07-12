#!/usr/bin/env python3
"""
[LEGACY WRAPPER] Smart Log Manager

このスクリプトは unified-monitoring-tool.py に統合されました。
Phase 4 統合完了 - レガシー互換性のためのwrapperスクリプト

新しい使用方法:
  scripts/tools/unified-monitoring-tool.py rotate     # ローテーション
  scripts/tools/unified-monitoring-tool.py cleanup   # クリーンアップ
  scripts/tools/unified-monitoring-tool.py health    # ヘルスレポート
"""

import gzip
import json
import logging
import os
import shutil
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

print("⚠️  [LEGACY] smart-log-manager.py は統合されました")
print("📦 unified-monitoring-tool.py に移行してください")
print("")
print("🔄 自動転送中...")

# 統合ツールの実行
script_dir = Path(__file__).parent
unified_tool = script_dir.parent / "unified-monitoring-tool.py"

# 引数変換 (action based)
args = sys.argv[1:] if len(sys.argv) > 1 else ["health"]
action_mapping = {
    "rotate": "rotate",
    "compress": "rotate",
    "cleanup": "cleanup",
    "analyze": "analyze",
    "health": "health",
}

action = args[0] if args else "health"
new_command = action_mapping.get(action, "health")
new_args = [new_command] + args[1:]

os.execv(sys.executable, [sys.executable, str(unified_tool)] + new_args)


class SmartLogManager:
    """o3+Gemini統合スマートログ管理システム"""

    def __init__(self, log_root: str = "runtime/logs"):
        self.log_root = Path(log_root)
        self.log_root.mkdir(parents=True, exist_ok=True)

        # o3戦略: ログ設定（標準ライブラリ版）
        logging.basicConfig(
            level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        self.logger = logging.getLogger("smart-log-manager")

        # 設定
        self.max_file_size = 100 * 1024 * 1024  # 100MB (o3推奨)
        # DISABLED: Memory inheritance system never expires data
        self.retention_days = {
            "hot": 7,  # ローカルSSD
            "warm": 30,  # 標準ストレージ
            "cold": 90,  # アーカイブストレージ
        }

        self.logger.info(
            f"SmartLogManager初期化完了 - log_root: {self.log_root}, max_size_mb: {self.max_file_size // (1024 * 1024)}"
        )

    def rotate_logs(self) -> Dict[str, Any]:
        """o3戦略: ログローテーション実行"""
        self.logger.info("ログローテーション開始")

        rotated_files = []
        total_size_before = 0
        total_size_after = 0

        # 全ログファイルをスキャン
        for log_file in self.log_root.rglob("*.log"):
            if not log_file.is_file():
                continue

            file_size = log_file.stat().st_size
            total_size_before += file_size

            # サイズまたは日付でローテーション判定
            if self._should_rotate(log_file, file_size):
                rotated_path = self._rotate_single_file(log_file)
                if rotated_path:
                    rotated_files.append(
                        {
                            "original": str(log_file),
                            "rotated": str(rotated_path),
                            "size_mb": file_size / (1024 * 1024),
                        }
                    )

        # JSONファイルも同様にローテーション
        for json_file in self.log_root.rglob("*.json"):
            if not json_file.is_file() or "current-session" in json_file.name:
                continue

            file_size = json_file.stat().st_size
            total_size_before += file_size

            if self._should_rotate(json_file, file_size):
                rotated_path = self._rotate_single_file(json_file)
                if rotated_path:
                    rotated_files.append(
                        {
                            "original": str(json_file),
                            "rotated": str(rotated_path),
                            "size_mb": file_size / (1024 * 1024),
                        }
                    )

        # ローテーション後のサイズ計算
        for file_path in self.log_root.rglob("*"):
            if file_path.is_file():
                total_size_after += file_path.stat().st_size

        result = {
            "rotated_files": len(rotated_files),
            "files_details": rotated_files,
            "size_reduction_mb": (total_size_before - total_size_after) / (1024 * 1024),
            "timestamp": datetime.now().isoformat(),
        }

        self.logger.info("ログローテーション完了", **result)
        return result

    def _should_rotate(self, file_path: Path, file_size: int) -> bool:
        """ローテーション判定"""
        # サイズベース
        if file_size > self.max_file_size:
            return True

        # 時間ベース（24時間以上経過）
        try:
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            if datetime.now() - mtime > timedelta(hours=24):
                return True
        except OSError:
            pass

        return False

    def _rotate_single_file(self, file_path: Path) -> Optional[Path]:
        """単一ファイルのローテーション"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            rotated_name = f"{file_path.stem}-{timestamp}{file_path.suffix}.gz"
            rotated_path = file_path.parent / rotated_name

            # gzip圧縮してローテーション
            with open(file_path, "rb") as f_in:
                with gzip.open(rotated_path, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)

            # 元ファイルをクリア（完全削除ではなく空にする）
            file_path.write_text("")

            self.logger.debug(
                "ファイルローテーション完了",
                original=str(file_path),
                rotated=str(rotated_path),
            )
            return rotated_path

        except Exception as e:
            self.logger.error("ローテーション失敗", file=str(file_path), error=str(e))
            return None

    def compress_old_logs(self) -> Dict[str, Any]:
        """o3戦略: 古いログの圧縮"""
        self.logger.info("古いログ圧縮開始")

        compressed_files = []
        total_saved_bytes = 0

        # 7日以上経過した未圧縮ログを圧縮
        cutoff_date = datetime.now() - timedelta(days=7)

        for log_file in self.log_root.rglob("*.log"):
            if not log_file.is_file():
                continue

            try:
                mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                if mtime < cutoff_date:
                    original_size = log_file.stat().st_size
                    compressed_path = self._compress_file(log_file)

                    if compressed_path:
                        compressed_size = compressed_path.stat().st_size
                        saved_bytes = original_size - compressed_size
                        total_saved_bytes += saved_bytes

                        compressed_files.append(
                            {
                                "file": str(log_file),
                                "compressed": str(compressed_path),
                                "original_size_mb": original_size / (1024 * 1024),
                                "compressed_size_mb": compressed_size / (1024 * 1024),
                                "compression_ratio": compressed_size / original_size
                                if original_size > 0
                                else 0,
                            }
                        )

                        # 元ファイル削除
                        log_file.unlink()

            except OSError as e:
                self.logger.error("圧縮処理失敗", file=str(log_file), error=str(e))

        result = {
            "compressed_files": len(compressed_files),
            "files_details": compressed_files,
            "total_saved_mb": total_saved_bytes / (1024 * 1024),
            "timestamp": datetime.now().isoformat(),
        }

        self.logger.info("古いログ圧縮完了", **result)
        return result

    def _compress_file(self, file_path: Path) -> Optional[Path]:
        """ファイル圧縮（zstd使用、fallbackでgzip）"""
        compressed_path = file_path.with_suffix(file_path.suffix + ".zst")

        # zstd圧縮を試行
        try:
            subprocess.run(
                ["zstd", "-19", str(file_path), "-o", str(compressed_path)],
                capture_output=True,
                check=True,
            )

            if compressed_path.exists():
                return compressed_path

        except (subprocess.CalledProcessError, FileNotFoundError):
            # zstdが失敗した場合はgzipにフォールバック
            self.logger.warning(
                "zstd圧縮失敗、gzipにフォールバック", file=str(file_path)
            )

        # gzip圧縮
        try:
            compressed_path = file_path.with_suffix(file_path.suffix + ".gz")
            with open(file_path, "rb") as f_in:
                with gzip.open(compressed_path, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)
            return compressed_path

        except Exception as e:
            self.logger.error("gzip圧縮も失敗", file=str(file_path), error=str(e))
            return None

    def cleanup_old_archives(self) -> Dict[str, Any]:
        """DISABLED: Memory inheritance system never deletes archives"""
        return {
            "status": "disabled",
            "message": "Memory inheritance system preserves all archives",
            "deleted_files": 0,
            "files_details": [],
            "bytes_freed": 0,
        }
        self.logger.info("古いアーカイブクリーンアップ開始")

        deleted_files = []
        total_freed_bytes = 0

        # 設定された保持期間を超えたファイルを削除
        cutoff_date = datetime.now() - timedelta(days=self.retention_days["cold"])

        for archive_file in self.log_root.rglob("*.gz"):
            if not archive_file.is_file():
                continue

            try:
                mtime = datetime.fromtimestamp(archive_file.stat().st_mtime)
                if mtime < cutoff_date:
                    file_size = archive_file.stat().st_size
                    total_freed_bytes += file_size

                    deleted_files.append(
                        {
                            "file": str(archive_file),
                            "size_mb": file_size / (1024 * 1024),
                            "age_days": (datetime.now() - mtime).days,
                        }
                    )

                    archive_file.unlink()

            except OSError as e:
                self.logger.error("削除失敗", file=str(archive_file), error=str(e))

        # .zstファイルも同様に処理
        for archive_file in self.log_root.rglob("*.zst"):
            if not archive_file.is_file():
                continue

            try:
                mtime = datetime.fromtimestamp(archive_file.stat().st_mtime)
                if mtime < cutoff_date:
                    file_size = archive_file.stat().st_size
                    total_freed_bytes += file_size

                    deleted_files.append(
                        {
                            "file": str(archive_file),
                            "size_mb": file_size / (1024 * 1024),
                            "age_days": (datetime.now() - mtime).days,
                        }
                    )

                    archive_file.unlink()

            except OSError as e:
                self.logger.error("削除失敗", file=str(archive_file), error=str(e))

        result = {
            "deleted_files": len(deleted_files),
            "files_details": deleted_files,
            "freed_space_mb": total_freed_bytes / (1024 * 1024),
            "retention_days": self.retention_days["cold"],
            "timestamp": datetime.now().isoformat(),
        }

        self.logger.info("古いアーカイブクリーンアップ完了", **result)
        return result

    def analyze_log_patterns(self) -> Dict[str, Any]:
        """Gemini戦略: ログパターン分析"""
        self.logger.info("ログパターン分析開始")

        patterns = {
            "error_frequency": {},
            "warning_patterns": {},
            "performance_issues": [],
            "security_events": [],
            "size_distribution": {},
        }

        total_lines = 0
        total_files = 0

        # 全ログファイルを分析
        for log_file in self.log_root.rglob("*.log"):
            if not log_file.is_file():
                continue

            total_files += 1
            file_lines = 0

            try:
                with open(log_file, encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        total_lines += 1
                        file_lines += 1

                        # エラーパターン検出
                        if "ERROR" in line or "FATAL" in line:
                            error_type = self._extract_error_type(line)
                            patterns["error_frequency"][error_type] = (
                                patterns["error_frequency"].get(error_type, 0) + 1
                            )

                        # 警告パターン検出
                        elif "WARNING" in line or "WARN" in line:
                            warning_type = self._extract_warning_type(line)
                            patterns["warning_patterns"][warning_type] = (
                                patterns["warning_patterns"].get(warning_type, 0) + 1
                            )

                        # パフォーマンス問題検出
                        elif "timeout" in line.lower() or "slow" in line.lower():
                            patterns["performance_issues"].append(
                                {
                                    "file": str(log_file),
                                    "line": line.strip(),
                                    "timestamp": self._extract_timestamp(line),
                                }
                            )

                        # セキュリティイベント検出
                        elif any(
                            keyword in line.lower()
                            for keyword in ["auth", "login", "permission", "security"]
                        ):
                            patterns["security_events"].append(
                                {
                                    "file": str(log_file),
                                    "line": line.strip(),
                                    "timestamp": self._extract_timestamp(line),
                                }
                            )

                # ファイルサイズ分布
                file_size_mb = log_file.stat().st_size / (1024 * 1024)
                size_category = self._categorize_file_size(file_size_mb)
                patterns["size_distribution"][size_category] = (
                    patterns["size_distribution"].get(size_category, 0) + 1
                )

            except Exception as e:
                self.logger.error("ログ分析失敗", file=str(log_file), error=str(e))

        # 分析結果の要約
        result = {
            "total_files": total_files,
            "total_lines": total_lines,
            "analysis_patterns": patterns,
            "insights": self._generate_insights(patterns),
            "timestamp": datetime.now().isoformat(),
        }

        self.logger.info(
            "ログパターン分析完了",
            files=total_files,
            lines=total_lines,
            errors=len(patterns["error_frequency"]),
            warnings=len(patterns["warning_patterns"]),
        )

        return result

    def _extract_error_type(self, line: str) -> str:
        """エラータイプ抽出"""
        common_errors = [
            "connection",
            "timeout",
            "permission",
            "not found",
            "invalid",
            "failed",
        ]
        for error_type in common_errors:
            if error_type in line.lower():
                return error_type
        return "other"

    def _extract_warning_type(self, line: str) -> str:
        """警告タイプ抽出"""
        common_warnings = [
            "deprecated",
            "limit",
            "capacity",
            "memory",
            "disk",
            "performance",
        ]
        for warning_type in common_warnings:
            if warning_type in line.lower():
                return warning_type
        return "other"

    def _extract_timestamp(self, line: str) -> Optional[str]:
        """タイムスタンプ抽出（簡易版）"""
        import re

        # ISO形式の日時を検索
        iso_pattern = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"
        match = re.search(iso_pattern, line)
        return match.group(0) if match else None

    def _categorize_file_size(self, size_mb: float) -> str:
        """ファイルサイズカテゴリ分類"""
        if size_mb < 1:
            return "small (<1MB)"
        elif size_mb < 10:
            return "medium (1-10MB)"
        elif size_mb < 100:
            return "large (10-100MB)"
        else:
            return "very_large (>100MB)"

    def _generate_insights(self, patterns: Dict[str, Any]) -> List[str]:
        """Gemini戦略: インサイト生成"""
        insights = []

        # エラー頻度分析
        if patterns["error_frequency"]:
            most_common_error = max(
                patterns["error_frequency"].items(), key=lambda x: x[1]
            )
            insights.append(
                f"最頻出エラー: {most_common_error[0]} ({most_common_error[1]}回)"
            )

        # パフォーマンス問題
        if len(patterns["performance_issues"]) > 10:
            insights.append(
                f"パフォーマンス問題検出: {len(patterns['performance_issues'])}件 - 調査推奨"
            )

        # セキュリティイベント
        if len(patterns["security_events"]) > 5:
            insights.append(
                f"セキュリティ関連イベント: {len(patterns['security_events'])}件 - 要確認"
            )

        # ファイルサイズ分布
        large_files = patterns["size_distribution"].get("very_large (>100MB)", 0)
        if large_files > 0:
            insights.append(f"大容量ログファイル {large_files}個 - ローテーション推奨")

        return insights

    def generate_health_report(self) -> Dict[str, Any]:
        """総合ヘルスレポート生成"""
        self.logger.info("ログヘルスレポート生成開始")

        # 各種分析実行
        rotation_result = self.rotate_logs()
        compression_result = self.compress_old_logs()
        cleanup_result = self.cleanup_old_archives()
        pattern_analysis = self.analyze_log_patterns()

        # 総合評価
        health_score = self._calculate_health_score(pattern_analysis)

        report = {
            "report_timestamp": datetime.now().isoformat(),
            "log_root": str(self.log_root),
            "health_score": health_score,
            "operations": {
                "rotation": rotation_result,
                "compression": compression_result,
                "cleanup": cleanup_result,
            },
            "analysis": pattern_analysis,
            "recommendations": self._generate_recommendations(
                pattern_analysis, health_score
            ),
            "next_maintenance": (datetime.now() + timedelta(days=1)).isoformat(),
        }

        # レポート保存
        report_file = (
            self.log_root
            / f"health-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        )
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        self.logger.info(
            "ログヘルスレポート生成完了",
            report_file=str(report_file),
            health_score=health_score,
        )

        return report

    def _calculate_health_score(self, analysis: Dict[str, Any]) -> float:
        """ヘルススコア計算（0-100）"""
        score = 100.0

        # エラー率でスコア減算
        total_lines = analysis.get("total_lines", 1)
        error_count = sum(analysis["analysis_patterns"]["error_frequency"].values())
        error_rate = error_count / total_lines if total_lines > 0 else 0
        score -= min(error_rate * 1000, 30)  # 最大30点減点

        # パフォーマンス問題でスコア減算
        perf_issues = len(analysis["analysis_patterns"]["performance_issues"])
        score -= min(perf_issues * 2, 20)  # 最大20点減点

        # 大容量ファイルでスコア減算
        large_files = analysis["analysis_patterns"]["size_distribution"].get(
            "very_large (>100MB)", 0
        )
        score -= min(large_files * 5, 15)  # 最大15点減点

        return max(score, 0.0)

    def _generate_recommendations(
        self, analysis: Dict[str, Any], health_score: float
    ) -> List[str]:
        """改善推奨事項生成"""
        recommendations = []

        if health_score < 70:
            recommendations.append(
                "🚨 ログ健全性が低下しています。緊急対応が必要です。"
            )

        error_count = sum(analysis["analysis_patterns"]["error_frequency"].values())
        if error_count > 100:
            recommendations.append(
                f"🔥 エラー数が多すぎます ({error_count}件)。根本原因の調査を推奨します。"
            )

        perf_issues = len(analysis["analysis_patterns"]["performance_issues"])
        if perf_issues > 10:
            recommendations.append(
                f"⚡ パフォーマンス問題が多発しています ({perf_issues}件)。最適化を検討してください。"
            )

        large_files = analysis["analysis_patterns"]["size_distribution"].get(
            "very_large (>100MB)", 0
        )
        if large_files > 0:
            recommendations.append(
                f"📁 大容量ログファイルが {large_files}個あります。ローテーション設定を見直してください。"
            )

        if not recommendations:
            recommendations.append("✅ ログシステムは健全に動作しています。")

        return recommendations


def main():
    """メイン実行"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Smart Log Manager - o3+Gemini統合ログ管理"
    )
    parser.add_argument(
        "action",
        choices=["rotate", "compress", "cleanup", "analyze", "health"],
        help="実行するアクション",
    )
    parser.add_argument(
        "--log-root", default="runtime/logs", help="ログルートディレクトリ"
    )
    parser.add_argument("--log-level", default="INFO", help="ログレベル")

    args = parser.parse_args()

    # 環境変数設定
    os.environ["LOG_LEVEL"] = args.log_level

    manager = SmartLogManager(args.log_root)

    if args.action == "rotate":
        result = manager.rotate_logs()
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.action == "compress":
        result = manager.compress_old_logs()
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.action == "cleanup":
        result = manager.cleanup_old_archives()
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.action == "analyze":
        result = manager.analyze_log_patterns()
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.action == "health":
        result = manager.generate_health_report()
        print("\n" + "=" * 60)
        print("🏥 SMART LOG MANAGER - ヘルスレポート")
        print("=" * 60)
        print(f"📊 健全性スコア: {result['health_score']:.1f}/100")
        print(f"📁 ログルート: {result['log_root']}")
        print(f"📈 分析ファイル数: {result['analysis']['total_files']}")
        print(f"📝 総ログ行数: {result['analysis']['total_lines']:,}")
        print("\n🎯 推奨事項:")
        for rec in result["recommendations"]:
            print(f"  {rec}")
        print("=" * 60)


if __name__ == "__main__":
    main()
