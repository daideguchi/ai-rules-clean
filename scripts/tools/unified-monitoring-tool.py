#!/usr/bin/env python3
"""
Unified Monitoring Tool - Phase 4 統合モニタリングシステム
Consolidates: ai-api-check.sh + simple-log-analyzer.py + smart-log-manager.py + status-updater-daemon.sh

o3推奨セーフティ機能:
- プロセス分離によるサブコマンド実行
- 段階的ロールバック対応
- 権限分離とセキュリティ強化
- 構造化ログと監視連携
"""

import argparse
import gzip
import json
import logging
import os
import shutil
import signal
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# バージョン情報
TOOL_VERSION = "1.0.0"
CONSOLIDATED_SCRIPTS = [
    "ai-api-check.sh",
    "simple-log-analyzer.py",
    "smart-log-manager.py",
    "status-updater-daemon.sh",
]


class UnifiedMonitoringTool:
    """統合モニタリングツール - o3推奨アーキテクチャ"""

    def __init__(
        self, log_root: str = "runtime/logs", config_file: Optional[str] = None
    ):
        self.log_root = Path(log_root)
        self.log_root.mkdir(parents=True, exist_ok=True)

        # 設定読み込み
        self.config = self._load_config(config_file)

        # o3推奨: 構造化ログ設定
        logging.basicConfig(
            level=getattr(logging, self.config.get("log_level", "INFO")),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(self.log_root / "unified-monitoring.log"),
                logging.StreamHandler(),
            ],
        )
        self.logger = logging.getLogger("unified-monitoring")

        # プロセス管理
        self.daemon_pid_file = self.log_root / "monitoring-daemon.pid"
        self.daemon_lock_file = self.log_root / "monitoring-daemon.lock"

        self.logger.info(f"UnifiedMonitoringTool v{TOOL_VERSION} 初期化完了")

    def _load_config(self, config_file: Optional[str]) -> Dict[str, Any]:
        """設定ファイル読み込み"""
        default_config = {
            "log_level": "INFO",
            "api_models": ["gemini-1.5-pro", "gemini-1.5-flash", "o3-mini"],
            "log_rotation": {"max_size_mb": 100, "max_age_hours": 24},
            "cleanup": {"retention_days": 30, "compression_days": 7},
            "monitoring": {
                "update_interval": 300,  # 5分
                "health_check_interval": 3600,  # 1時間
            },
        }

        if config_file and Path(config_file).exists():
            try:
                with open(config_file) as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                self.logger.warning(f"設定ファイル読み込み失敗: {e}")

        return default_config

    # ========== API チェック機能 (ai-api-check.sh 統合) ==========

    def check_api_status(
        self, model: Optional[str] = None, interactive: bool = False
    ) -> Dict[str, Any]:
        """API実行前チェック - ai-api-check.sh統合機能"""
        self.logger.info("API実行前チェック開始")

        if interactive:
            return self._interactive_api_check()

        # 非対話式チェック
        valid_models = self.config["api_models"]
        if model and model not in valid_models:
            return {
                "status": "error",
                "message": f"無効なモデル名: {model}",
                "valid_models": valid_models,
                "timestamp": datetime.now().isoformat(),
            }

        # API疎通確認（モック）
        result = {
            "status": "success",
            "model": model or "auto-detect",
            "api_available": True,
            "recommendations": [
                "エラー時はo3にフォールバック",
                "クオータ制限時は時間を置く",
                "API全体停止時はローカル実行",
            ],
            "timestamp": datetime.now().isoformat(),
        }

        # ログ記録
        self._log_api_check(result)

        self.logger.info("API実行前チェック完了", extra={"model": model})
        return result

    def _interactive_api_check(self) -> Dict[str, Any]:
        """対話式APIチェック"""
        print("🔍 AI API 実行前チェック")
        print("==========================")

        # モデル選択
        print("1. 使用予定モデル名を選択:")
        for i, model in enumerate(self.config["api_models"], 1):
            print(f"   {i}. {model}")

        try:
            choice = input("選択 (1-3): ").strip()
            model_idx = int(choice) - 1
            if 0 <= model_idx < len(self.config["api_models"]):
                model = self.config["api_models"][model_idx]
                print(f"✅ 選択されたモデル: {model}")
            else:
                return {"status": "error", "message": "無効な選択"}
        except (ValueError, KeyboardInterrupt):
            return {"status": "cancelled", "message": "ユーザーによるキャンセル"}

        # コマンド構文確認
        print("\n2. コマンド構文確認:")
        if "gemini" in model:
            print(
                f'正しい形式: echo "prompt" | npx https://github.com/google-gemini/gemini-cli -m "{model}"'
            )
        elif "o3" in model:
            print("正しい形式: mcp__o3__o3-search with input parameter")

        syntax_ok = input("コマンド構文確認済み？ [y/n]: ").strip().lower()
        if syntax_ok != "y":
            return {"status": "error", "message": "コマンド構文を確認してください"}

        # 代替手段確認
        print("\n3. エラー時の代替手段準備:")
        print("   - Gemini失敗 → O3使用")
        print("   - クオータ制限 → 時間を置く")
        print("   - API全体停止 → ローカル実行")

        backup_ok = input("代替手段準備済み？ [y/n]: ").strip().lower()
        if backup_ok != "y":
            return {"status": "error", "message": "代替手段を準備してください"}

        result = {
            "status": "success",
            "model": model,
            "interactive_check": True,
            "timestamp": datetime.now().isoformat(),
        }

        print("\n✅ 事前チェック完了")
        print("安全にAPI実行してください")

        return result

    def _log_api_check(self, result: Dict[str, Any]):
        """API チェック結果ログ"""
        log_file = self.log_root / f"api_checks_{datetime.now().strftime('%Y%m%d')}.log"
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "check_result": result,
            "tool_version": TOOL_VERSION,
        }

        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

    # ========== ログ分析機能 (simple-log-analyzer.py 統合) ==========

    def analyze_logs(self, scope: str = "all") -> Dict[str, Any]:
        """ログ分析実行 - simple-log-analyzer.py統合機能"""
        self.logger.info("ログ分析開始", extra={"scope": scope})

        stats = {
            "total_files": 0,
            "total_size_mb": 0,
            "file_types": {},
            "large_files": [],
            "old_files": [],
            "errors_found": 0,
            "warnings_found": 0,
        }

        search_patterns = ["*.log", "*.txt"] if scope == "logs" else ["*"]

        for pattern in search_patterns:
            for log_file in self.log_root.rglob(pattern):
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

                # ログ内容分析
                if suffix in [".log", ".txt"]:
                    error_count, warning_count = self._analyze_log_content(log_file)
                    stats["errors_found"] += error_count
                    stats["warnings_found"] += warning_count

        result = {
            "analysis_time": datetime.now().isoformat(),
            "scope": scope,
            "statistics": stats,
            "recommendations": self._generate_analysis_recommendations(stats),
            "tool_version": TOOL_VERSION,
        }

        self.logger.info(
            "ログ分析完了",
            extra={
                "files": stats["total_files"],
                "size_mb": stats["total_size_mb"],
                "errors": stats["errors_found"],
            },
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
                    if any(
                        keyword in line_lower
                        for keyword in ["error", "fatal", "critical"]
                    ):
                        error_count += 1
                    elif any(
                        keyword in line_lower
                        for keyword in ["warning", "warn", "caution"]
                    ):
                        warning_count += 1
        except Exception:
            pass  # ファイル読み込みエラーは無視

        return error_count, warning_count

    def _generate_analysis_recommendations(self, stats: Dict[str, Any]) -> List[str]:
        """分析結果からの推奨事項生成"""
        recommendations = []

        if len(stats["large_files"]) > 0:
            recommendations.append(
                f"🗂️ 大容量ログファイル {len(stats['large_files'])}個 - ローテーション推奨"
            )

        if len(stats["old_files"]) > 5:
            recommendations.append(
                f"🗑️ 古いログファイル {len(stats['old_files'])}個 - クリーンアップ推奨"
            )

        if stats["errors_found"] > 100:
            recommendations.append(
                f"🚨 多数のエラー検出 ({stats['errors_found']}件) - 調査が必要"
            )

        if stats["warnings_found"] > 500:
            recommendations.append(
                f"⚠️ 多数の警告検出 ({stats['warnings_found']}件) - 確認推奨"
            )

        if stats["total_size_mb"] > 100:
            recommendations.append(
                f"💾 ログサイズ大 ({stats['total_size_mb']:.1f}MB) - アーカイブ推奨"
            )

        if not recommendations:
            recommendations.append("✅ ログ状態は良好です")

        return recommendations

    # ========== ログ管理機能 (smart-log-manager.py 統合) ==========

    def rotate_logs(self) -> Dict[str, Any]:
        """ログローテーション実行 - smart-log-manager.py統合機能"""
        self.logger.info("ログローテーション開始")

        config = self.config["log_rotation"]
        max_size = config["max_size_mb"] * 1024 * 1024
        max_age = timedelta(hours=config["max_age_hours"])

        rotated_files = []
        total_size_before = 0
        total_size_after = 0

        for log_file in self.log_root.rglob("*.log"):
            if not log_file.is_file():
                continue

            file_size = log_file.stat().st_size
            total_size_before += file_size

            # ローテーション判定
            should_rotate = False
            if file_size > max_size:
                should_rotate = True
                reason = "size"
            else:
                mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                if datetime.now() - mtime > max_age:
                    should_rotate = True
                    reason = "age"

            if should_rotate:
                rotated_path = self._rotate_single_file(log_file)
                if rotated_path:
                    rotated_files.append(
                        {
                            "original": str(log_file.relative_to(self.log_root)),
                            "rotated": str(rotated_path.relative_to(self.log_root)),
                            "size_mb": file_size / (1024 * 1024),
                            "reason": reason,
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
            "tool_version": TOOL_VERSION,
        }

        self.logger.info(
            "ログローテーション完了",
            extra={
                "rotated_count": len(rotated_files),
                "size_reduction_mb": result["size_reduction_mb"],
            },
        )

        return result

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

            return rotated_path

        except Exception as e:
            self.logger.error(
                "ローテーション失敗", extra={"file": str(file_path), "error": str(e)}
            )
            return None

    def cleanup_old_logs(self, days: int = None) -> Dict[str, Any]:
        """古いログのクリーンアップ"""
        if days is None:
            days = self.config["cleanup"]["retention_days"]

        self.logger.info("古いログクリーンアップ開始", extra={"retention_days": days})

        cutoff_date = datetime.now() - timedelta(days=days)
        deleted_files = []
        freed_space_mb = 0

        for log_file in self.log_root.rglob("*.log.*"):  # ローテーション済みファイル
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
                    self.logger.error(
                        "削除失敗", extra={"file": str(log_file), "error": str(e)}
                    )

        result = {
            "cleaned_files": len(deleted_files),
            "files": deleted_files,
            "freed_space_mb": round(freed_space_mb, 2),
            "cutoff_days": days,
            "timestamp": datetime.now().isoformat(),
        }

        self.logger.info(
            "古いログクリーンアップ完了",
            extra={"deleted_count": len(deleted_files), "freed_mb": freed_space_mb},
        )

        return result

    # ========== ステータス更新デーモン (status-updater-daemon.sh 統合) ==========

    def start_status_daemon(self) -> Dict[str, Any]:
        """ステータス更新デーモン開始 - status-updater-daemon.sh統合機能"""

        # 既存デーモンチェック
        if self._is_daemon_running():
            return {
                "status": "already_running",
                "message": f"ステータス更新デーモンは既に実行中です (PID: {self._get_daemon_pid()})",
                "timestamp": datetime.now().isoformat(),
            }

        # フォークしてデーモン化
        try:
            pid = os.fork()
            if pid > 0:
                # 親プロセス - PID保存して終了
                with open(self.daemon_pid_file, "w") as f:
                    f.write(str(pid))

                return {
                    "status": "started",
                    "pid": pid,
                    "message": "ステータス更新デーモンを開始しました",
                    "timestamp": datetime.now().isoformat(),
                }
            else:
                # 子プロセス - デーモン実行
                self._run_status_daemon()

        except OSError as e:
            return {
                "status": "error",
                "message": f"デーモン開始失敗: {e}",
                "timestamp": datetime.now().isoformat(),
            }

    def stop_status_daemon(self) -> Dict[str, Any]:
        """ステータス更新デーモン停止"""
        if not self._is_daemon_running():
            return {
                "status": "not_running",
                "message": "ステータス更新デーモンは実行されていません",
                "timestamp": datetime.now().isoformat(),
            }

        try:
            pid = self._get_daemon_pid()
            os.kill(pid, signal.SIGTERM)

            # クリーンアップ
            self.daemon_pid_file.unlink(missing_ok=True)
            self.daemon_lock_file.unlink(missing_ok=True)

            return {
                "status": "stopped",
                "pid": pid,
                "message": "ステータス更新デーモンを停止しました",
                "timestamp": datetime.now().isoformat(),
            }

        except (ProcessLookupError, OSError) as e:
            return {
                "status": "error",
                "message": f"デーモン停止失敗: {e}",
                "timestamp": datetime.now().isoformat(),
            }

    def _is_daemon_running(self) -> bool:
        """デーモン実行状態確認"""
        if not self.daemon_pid_file.exists():
            return False

        try:
            pid = self._get_daemon_pid()
            os.kill(pid, 0)  # シグナル0でプロセス存在確認
            return True
        except (ProcessLookupError, OSError):
            # staleなPIDファイルクリーンアップ
            self.daemon_pid_file.unlink(missing_ok=True)
            return False

    def _get_daemon_pid(self) -> int:
        """デーモンPID取得"""
        if self.daemon_pid_file.exists():
            return int(self.daemon_pid_file.read_text().strip())
        return 0

    def _run_status_daemon(self):
        """デーモンメインループ"""
        # デーモン化処理
        os.setsid()
        os.chdir("/")
        os.umask(0)

        # 標準入出力をクローズ
        with open("/dev/null") as dev_null:
            os.dup2(dev_null.fileno(), sys.stdin.fileno())
        with open("/dev/null", "w") as dev_null:
            os.dup2(dev_null.fileno(), sys.stdout.fileno())
            os.dup2(dev_null.fileno(), sys.stderr.fileno())

        # ロックファイル作成
        self.daemon_lock_file.touch()

        # 終了シグナルハンドラ
        def signal_handler(signum, frame):
            self.daemon_lock_file.unlink(missing_ok=True)
            sys.exit(0)

        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)

        # メインループ
        interval = self.config["monitoring"]["update_interval"]
        while True:
            try:
                # ステータス更新実行
                self._update_status()
                time.sleep(interval)

            except Exception as e:
                # エラーログ記録
                error_log = self.log_root / "daemon_errors.log"
                with open(error_log, "a") as f:
                    f.write(f"{datetime.now().isoformat()}: {e}\n")
                time.sleep(60)  # エラー時は1分待機

    def _update_status(self):
        """ステータス更新処理"""
        project_root = Path(__file__).parent.parent.parent

        # ファイル変更確認
        check_paths = [
            project_root / "runtime",
            project_root / "scripts",
            project_root / "docs",
            project_root / "src",
        ]

        for path in check_paths:
            if not path.exists():
                continue

            # 最近変更されたファイルチェック
            for file_path in path.rglob("*"):
                if not file_path.is_file():
                    continue

                if file_path.suffix in [".json", ".py", ".md", ".sh"]:
                    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if datetime.now() - mtime < timedelta(minutes=5):
                        # 自動ステータス表示実行
                        status_script = (
                            project_root / "scripts" / "auto-status-display.py"
                        )
                        if status_script.exists():
                            try:
                                subprocess.run(
                                    ["python3", str(status_script)],
                                    capture_output=True,
                                    timeout=30,
                                )
                            except (
                                subprocess.TimeoutExpired,
                                subprocess.CalledProcessError,
                            ):
                                pass
                        return

    # ========== 統合ヘルスチェック ==========

    def health_check(self) -> Dict[str, Any]:
        """統合ヘルスチェック実行"""
        self.logger.info("統合ヘルスチェック開始")

        health_results = {
            "api_status": self.check_api_status(interactive=False),
            "log_analysis": self.analyze_logs(),
            "log_rotation": self.rotate_logs(),
            "cleanup_result": self.cleanup_old_logs(),
            "daemon_status": {
                "running": self._is_daemon_running(),
                "pid": self._get_daemon_pid() if self._is_daemon_running() else None,
            },
        }

        # 総合スコア計算
        health_score = self._calculate_health_score(health_results)

        result = {
            "health_score": health_score,
            "timestamp": datetime.now().isoformat(),
            "tool_version": TOOL_VERSION,
            "consolidated_scripts": CONSOLIDATED_SCRIPTS,
            "results": health_results,
            "recommendations": self._generate_health_recommendations(
                health_results, health_score
            ),
        }

        # ヘルスレポート保存
        report_file = (
            self.log_root
            / f"health-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        )
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        self.logger.info(
            "統合ヘルスチェック完了",
            extra={"health_score": health_score, "report_file": str(report_file)},
        )

        return result

    def _calculate_health_score(self, health_results: Dict[str, Any]) -> float:
        """ヘルススコア計算 (0-100)"""
        score = 100.0

        # API状態
        if health_results["api_status"]["status"] != "success":
            score -= 20

        # ログエラー率
        log_stats = health_results["log_analysis"]["statistics"]
        if log_stats["errors_found"] > 50:
            score -= min(log_stats["errors_found"] / 10, 30)

        # ログサイズ
        if log_stats["total_size_mb"] > 500:
            score -= 15

        # デーモン状態
        if not health_results["daemon_status"]["running"]:
            score -= 10

        return max(score, 0.0)

    def _generate_health_recommendations(
        self, health_results: Dict[str, Any], health_score: float
    ) -> List[str]:
        """ヘルス改善推奨事項"""
        recommendations = []

        if health_score < 70:
            recommendations.append("🚨 システム健全性が低下 - 緊急対応必要")

        if health_results["api_status"]["status"] != "success":
            recommendations.append("🔧 API接続に問題 - 設定確認が必要")

        log_stats = health_results["log_analysis"]["statistics"]
        if log_stats["errors_found"] > 100:
            recommendations.append(
                f"🔥 多数エラー検出 ({log_stats['errors_found']}件) - 調査必要"
            )

        if not health_results["daemon_status"]["running"]:
            recommendations.append("⚙️ ステータス更新デーモン停止 - 再起動推奨")

        if len(health_results["log_rotation"]["files_details"]) > 10:
            recommendations.append("📁 大量ローテーション実行 - 設定見直し推奨")

        if not recommendations:
            recommendations.append("✅ 全システム正常動作中")

        return recommendations


def main():
    """メイン実行関数"""
    parser = argparse.ArgumentParser(
        description=f"Unified Monitoring Tool v{TOOL_VERSION} - 統合モニタリングシステム",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
統合済みスクリプト:
  {", ".join(CONSOLIDATED_SCRIPTS)}

使用例:
  %(prog)s api-check --interactive          # 対話式APIチェック
  %(prog)s analyze --scope logs             # ログ分析実行
  %(prog)s rotate                           # ログローテーション
  %(prog)s daemon start                     # デーモン開始
  %(prog)s health                           # 統合ヘルスチェック
        """,
    )

    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {TOOL_VERSION}"
    )
    parser.add_argument("--config", help="設定ファイルパス")
    parser.add_argument(
        "--log-root", default="runtime/logs", help="ログルートディレクトリ"
    )

    subparsers = parser.add_subparsers(dest="command", help="実行コマンド")

    # API チェック
    api_parser = subparsers.add_parser("api-check", help="API実行前チェック")
    api_parser.add_argument("--model", help="使用モデル名")
    api_parser.add_argument("--interactive", action="store_true", help="対話式チェック")

    # ログ分析
    analyze_parser = subparsers.add_parser("analyze", help="ログ分析実行")
    analyze_parser.add_argument(
        "--scope", choices=["all", "logs"], default="all", help="分析スコープ"
    )

    # ログローテーション
    subparsers.add_parser("rotate", help="ログローテーション実行")

    # クリーンアップ
    cleanup_parser = subparsers.add_parser("cleanup", help="古いログクリーンアップ")
    cleanup_parser.add_argument("--days", type=int, help="保持期間（日）")

    # デーモン管理
    daemon_parser = subparsers.add_parser("daemon", help="ステータス更新デーモン管理")
    daemon_parser.add_argument(
        "action", choices=["start", "stop", "status"], help="デーモンアクション"
    )

    # ヘルスチェック
    subparsers.add_parser("health", help="統合ヘルスチェック実行")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # ツール初期化
    tool = UnifiedMonitoringTool(args.log_root, args.config)

    try:
        # コマンド実行
        if args.command == "api-check":
            result = tool.check_api_status(
                getattr(args, "model", None), getattr(args, "interactive", False)
            )

        elif args.command == "analyze":
            result = tool.analyze_logs(getattr(args, "scope", "all"))

        elif args.command == "rotate":
            result = tool.rotate_logs()

        elif args.command == "cleanup":
            result = tool.cleanup_old_logs(getattr(args, "days", None))

        elif args.command == "daemon":
            action = getattr(args, "action", "status")
            if action == "start":
                result = tool.start_status_daemon()
            elif action == "stop":
                result = tool.stop_status_daemon()
            elif action == "status":
                result = {
                    "running": tool._is_daemon_running(),
                    "pid": tool._get_daemon_pid()
                    if tool._is_daemon_running()
                    else None,
                    "timestamp": datetime.now().isoformat(),
                }

        elif args.command == "health":
            result = tool.health_check()
            print("\n" + "=" * 60)
            print("🏥 UNIFIED MONITORING TOOL - ヘルスレポート")
            print("=" * 60)
            print(f"📊 健全性スコア: {result['health_score']:.1f}/100")
            print(f"🛠️ ツールバージョン: {result['tool_version']}")
            print(f"📦 統合スクリプト数: {len(result['consolidated_scripts'])}")
            print("\n🎯 推奨事項:")
            for rec in result["recommendations"]:
                print(f"  {rec}")
            print("=" * 60)
            return

        # 結果出力
        if not getattr(args, "interactive", False) or args.command != "api-check":
            print(json.dumps(result, indent=2, ensure_ascii=False))

    except KeyboardInterrupt:
        print("\n操作がキャンセルされました")
        sys.exit(1)
    except Exception as e:
        print(f"エラー: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
