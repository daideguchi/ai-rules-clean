#!/usr/bin/env python3
"""
AI Worker Status Monitor - リアルタイムワーカー状態監視システム
===========================================================
AIワーカーの実際の動作状態をリアルタイムで監視・表示

Features:
- Claude Code接続状態監視
- タスク実行状況追跡
- エラー・警告検出
- パフォーマンスメトリクス
- 自動ステータス更新
"""

import json
import logging
import re
import subprocess
import sys
import threading
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))


class WorkerStatus(Enum):
    """ワーカー状態"""

    INITIALIZING = "initializing"
    READY = "ready"
    WORKING = "working"
    WAITING = "waiting"
    ERROR = "error"
    DISCONNECTED = "disconnected"


@dataclass
class WorkerState:
    """ワーカー状態情報"""

    pane_id: str
    role: str
    title: str
    status: WorkerStatus
    current_task: Optional[str]
    last_activity: datetime
    error_count: int
    performance_score: float
    connection_health: str
    memory_usage: Optional[Dict] = None


@dataclass
class StatusMetrics:
    """ステータスメトリクス"""

    total_workers: int
    active_workers: int
    idle_workers: int
    error_workers: int
    average_performance: float
    system_health: str
    uptime: str


class AIWorkerStatusMonitor:
    """AIワーカーリアルタイムステータス監視システム"""

    def __init__(self, project_root: str = None):
        self.project_root = (
            Path(project_root) if project_root else Path(__file__).resolve().parents[2]
        )
        self.runtime_dir = self.project_root / "runtime"
        self.status_file = self.runtime_dir / "worker_status.json"
        self.running = False

        # ログ設定
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(self.runtime_dir / "logs" / "worker_status.log"),
                logging.StreamHandler(),
            ],
        )
        self.logger = logging.getLogger("worker-status")

        # ワーカー状態管理
        self.worker_states: Dict[str, WorkerState] = {}
        self.session_configs = {
            "multiagent": [
                {"pane_id": "0.0", "role": "BOSS1", "title": "👔：BOSS1：統括管理"},
                {"pane_id": "0.1", "role": "WORKER1", "title": "💻：WORKER1：開発実装"},
                {"pane_id": "0.2", "role": "WORKER2", "title": "🔧：WORKER2：品質管理"},
                {"pane_id": "0.3", "role": "WORKER3", "title": "🎨：WORKER3：設計文書"},
            ],
            "president": [
                {"pane_id": "0", "role": "PRESIDENT", "title": "👑 PRESIDENT"}
            ],
        }

        # 監視スレッド
        self.monitor_thread = None
        self.status_update_thread = None

    def start_monitoring(self):
        """監視開始"""
        if self.running:
            self.logger.warning("Monitoring already running")
            return

        self.running = True

        # 監視スレッド開始
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

        # ステータス更新スレッド開始
        self.status_update_thread = threading.Thread(
            target=self._status_update_loop, daemon=True
        )
        self.status_update_thread.start()

        self.logger.info("✅ AI Worker Status Monitoring started")

    def stop_monitoring(self):
        """監視停止"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        if self.status_update_thread:
            self.status_update_thread.join(timeout=5)
        self.logger.info("AI Worker Status Monitoring stopped")

    def _monitor_loop(self):
        """メイン監視ループ"""
        while self.running:
            try:
                # 全ワーカー状態更新
                self._update_all_worker_states()

                # ステータスバー更新
                self._update_statusbar_display()

                time.sleep(3)  # 3秒間隔で監視

            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)

    def _status_update_loop(self):
        """ステータス更新ループ"""
        while self.running:
            try:
                # ステータス永続化
                self._save_status_report()

                # ヘルスチェック
                self._perform_health_check()

                time.sleep(10)  # 10秒間隔でレポート更新

            except Exception as e:
                self.logger.error(f"Error in status update loop: {e}")
                time.sleep(10)

    def _update_all_worker_states(self):
        """全ワーカー状態更新"""
        for session_name, workers in self.session_configs.items():
            if self._session_exists(session_name):
                for worker_config in workers:
                    pane_target = f"{session_name}:{worker_config['pane_id']}"
                    worker_state = self._analyze_worker_state(
                        pane_target, worker_config
                    )
                    self.worker_states[pane_target] = worker_state

    def _analyze_worker_state(self, pane_target: str, config: Dict) -> WorkerState:
        """個別ワーカー状態分析"""
        try:
            # ペイン内容取得
            content = self._get_pane_content(pane_target)

            # 状態判定
            status = self._determine_worker_status(content)
            current_task = self._extract_current_task(content)
            connection_health = self._check_connection_health(content)
            error_count = self._count_errors(content)
            performance_score = self._calculate_performance_score(content, status)

            return WorkerState(
                pane_id=pane_target,
                role=config["role"],
                title=config["title"],
                status=status,
                current_task=current_task,
                last_activity=datetime.now(),
                error_count=error_count,
                performance_score=performance_score,
                connection_health=connection_health,
            )

        except Exception as e:
            self.logger.error(f"Error analyzing worker {pane_target}: {e}")
            return WorkerState(
                pane_id=pane_target,
                role=config["role"],
                title=config["title"],
                status=WorkerStatus.ERROR,
                current_task=None,
                last_activity=datetime.now(),
                error_count=1,
                performance_score=0.0,
                connection_health="error",
            )

    def _determine_worker_status(self, content: str) -> WorkerStatus:
        """ワーカー状態判定"""
        if not content:
            return WorkerStatus.DISCONNECTED

        # Claude Code接続状態確認
        if "How can I help" in content:
            return WorkerStatus.READY
        elif "Working on" in content or "Processing" in content:
            return WorkerStatus.WORKING
        elif "Error" in content or "Failed" in content:
            return WorkerStatus.ERROR
        elif "Login" in content or "Welcome to Claude Code" in content:
            return WorkerStatus.INITIALIZING
        elif "Approaching usage limit" in content:
            return WorkerStatus.WAITING
        else:
            return WorkerStatus.READY

    def _extract_current_task(self, content: str) -> Optional[str]:
        """現在のタスク抽出"""
        task_patterns = [
            r"Working on: (.+)",
            r"Processing: (.+)",
            r"Task: (.+)",
            r"> Try \"(.+)\"",
            r"> (.+)",
        ]

        for pattern in task_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1).strip()[:50]  # 50文字制限

        return None

    def _check_connection_health(self, content: str) -> str:
        """接続ヘルス確認"""
        if "How can I help" in content:
            return "excellent"
        elif "Bypassing Permissions" in content:
            return "good"
        elif "Approaching usage limit" in content:
            return "limited"
        elif "Error" in content or "Failed" in content:
            return "poor"
        else:
            return "unknown"

    def _count_errors(self, content: str) -> int:
        """エラー数カウント"""
        error_patterns = ["Error", "Failed", "Exception", "Timeout"]
        count = 0
        for pattern in error_patterns:
            count += content.count(pattern)
        return count

    def _calculate_performance_score(self, content: str, status: WorkerStatus) -> float:
        """パフォーマンススコア計算"""
        base_score = 0.5

        # ステータスによるスコア
        status_scores = {
            WorkerStatus.READY: 1.0,
            WorkerStatus.WORKING: 0.9,
            WorkerStatus.WAITING: 0.7,
            WorkerStatus.INITIALIZING: 0.5,
            WorkerStatus.ERROR: 0.1,
            WorkerStatus.DISCONNECTED: 0.0,
        }

        base_score = status_scores.get(status, 0.5)

        # 追加要素
        if "How can I help" in content:
            base_score += 0.1
        if "Bypassing Permissions" in content:
            base_score += 0.05
        if "Error" in content:
            base_score -= 0.2

        return max(0.0, min(1.0, base_score))

    def _update_statusbar_display(self):
        """ステータスバー表示更新"""
        try:
            for pane_target, worker_state in self.worker_states.items():
                # ステータスインジケーター作成
                status_indicator = self._create_status_indicator(worker_state)

                # tmuxペインタイトル更新
                session, pane_id = pane_target.split(":", 1)
                updated_title = f"{worker_state.title} {status_indicator}"

                subprocess.run(
                    ["tmux", "select-pane", "-t", pane_target, "-T", updated_title],
                    capture_output=True,
                    text=True,
                    check=False,
                )

        except Exception as e:
            self.logger.error(f"Error updating statusbar display: {e}")

    def _create_status_indicator(self, worker_state: WorkerState) -> str:
        """ステータスインジケーター作成"""
        status_icons = {
            WorkerStatus.READY: "✅",
            WorkerStatus.WORKING: "⚡",
            WorkerStatus.WAITING: "⏳",
            WorkerStatus.INITIALIZING: "🔄",
            WorkerStatus.ERROR: "❌",
            WorkerStatus.DISCONNECTED: "🔌",
        }

        icon = status_icons.get(worker_state.status, "❓")

        # パフォーマンススコアによる追加インジケーター
        if worker_state.performance_score >= 0.9:
            performance_icon = "🔥"
        elif worker_state.performance_score >= 0.7:
            performance_icon = "💪"
        elif worker_state.performance_score >= 0.5:
            performance_icon = "👍"
        else:
            performance_icon = "⚠️"

        return f"{icon}{performance_icon}"

    def _get_pane_content(self, pane_target: str) -> str:
        """ペイン内容取得"""
        try:
            result = subprocess.run(
                ["tmux", "capture-pane", "-t", pane_target, "-p"],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout
        except Exception:
            return ""

    def _session_exists(self, session_name: str) -> bool:
        """セッション存在確認"""
        try:
            result = subprocess.run(
                ["tmux", "has-session", "-t", session_name],
                capture_output=True,
                text=True,
            )
            return result.returncode == 0
        except Exception:
            return False

    def _save_status_report(self):
        """ステータスレポート保存"""
        try:
            report = {
                "timestamp": datetime.now().isoformat(),
                "workers": {k: asdict(v) for k, v in self.worker_states.items()},
                "metrics": asdict(self._calculate_metrics()),
                "monitoring_active": self.running,
            }

            self.status_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.status_file, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)

        except Exception as e:
            self.logger.error(f"Error saving status report: {e}")

    def _calculate_metrics(self) -> StatusMetrics:
        """メトリクス計算"""
        if not self.worker_states:
            return StatusMetrics(0, 0, 0, 0, 0.0, "unknown", "0s")

        total = len(self.worker_states)
        active = sum(
            1
            for w in self.worker_states.values()
            if w.status in [WorkerStatus.READY, WorkerStatus.WORKING]
        )
        idle = sum(
            1 for w in self.worker_states.values() if w.status == WorkerStatus.WAITING
        )
        error = sum(
            1 for w in self.worker_states.values() if w.status == WorkerStatus.ERROR
        )

        avg_performance = (
            sum(w.performance_score for w in self.worker_states.values()) / total
        )

        # システムヘルス判定
        if avg_performance >= 0.8:
            system_health = "excellent"
        elif avg_performance >= 0.6:
            system_health = "good"
        elif avg_performance >= 0.4:
            system_health = "fair"
        else:
            system_health = "poor"

        return StatusMetrics(
            total_workers=total,
            active_workers=active,
            idle_workers=idle,
            error_workers=error,
            average_performance=avg_performance,
            system_health=system_health,
            uptime="active",
        )

    def _perform_health_check(self):
        """ヘルスチェック実行"""
        try:
            metrics = self._calculate_metrics()

            if metrics.error_workers > 0:
                self.logger.warning(f"⚠️ {metrics.error_workers} workers in error state")

            if metrics.average_performance < 0.5:
                self.logger.warning(
                    f"⚠️ Low system performance: {metrics.average_performance:.2f}"
                )

            if metrics.active_workers == 0:
                self.logger.error("❌ No active workers detected")

        except Exception as e:
            self.logger.error(f"Error in health check: {e}")

    def get_status_summary(self) -> Dict[str, Any]:
        """ステータス概要取得"""
        metrics = self._calculate_metrics()

        return {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_workers": metrics.total_workers,
                "active_workers": metrics.active_workers,
                "system_health": metrics.system_health,
                "average_performance": f"{metrics.average_performance:.2f}",
            },
            "workers": {
                worker_state.role: {
                    "status": worker_state.status.value,
                    "performance": f"{worker_state.performance_score:.2f}",
                    "current_task": worker_state.current_task,
                    "connection": worker_state.connection_health,
                }
                for worker_state in self.worker_states.values()
            },
            "monitoring_active": self.running,
        }


def main():
    """メイン実行"""
    import argparse

    parser = argparse.ArgumentParser(description="AI Worker Status Monitor")
    parser.add_argument(
        "action", choices=["start", "status", "stop"], help="Action to perform"
    )
    parser.add_argument("--project-root", help="Project root directory")

    args = parser.parse_args()

    monitor = AIWorkerStatusMonitor(args.project_root)

    if args.action == "start":
        print("Starting AI Worker Status Monitoring...")
        monitor.start_monitoring()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping monitoring...")
            monitor.stop_monitoring()

    elif args.action == "status":
        summary = monitor.get_status_summary()
        print(json.dumps(summary, indent=2, ensure_ascii=False))

    elif args.action == "stop":
        monitor.stop_monitoring()
        print("Monitoring stopped")


if __name__ == "__main__":
    main()
