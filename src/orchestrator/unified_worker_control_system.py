#!/usr/bin/env python3
"""
Unified Worker Control System - 完全統合ワーカー制御システム
===========================================================
tmux、リアルタイム表示、ステータス監視を統合した単一制御システム

Features:
- 統一されたワーカー状態管理
- 絵文字+役職名+タスク フォーマット
- 白色テキスト強制適用
- 3システム統合アーキテクチャ
- ロバストなエラーハンドリング
"""

import json
import logging
import subprocess
import sys
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional

# プロジェクトルートをパスに追加
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))


class WorkerStatus(Enum):
    """ワーカー状態"""

    ACTIVE = "active"
    IDLE = "idle"
    PROCESSING = "processing"
    ERROR = "error"
    OFFLINE = "offline"


@dataclass
class WorkerInfo:
    """ワーカー情報"""

    pane_id: str
    role: str
    emoji: str
    current_task: str
    status: WorkerStatus
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class TaskInfo:
    """タスク情報"""

    task_type: str
    description: str
    emoji: str
    priority: str = "medium"


class UnifiedWorkerControlSystem:
    """統合ワーカー制御システム"""

    def __init__(self, project_root: str = None):
        self.project_root = (
            Path(project_root) if project_root else Path(__file__).resolve().parents[2]
        )
        self.runtime_dir = self.project_root / "runtime"
        self.config_file = self.runtime_dir / "unified_worker_config.json"
        self.state_file = self.runtime_dir / "worker_states.json"

        # 共有状態管理
        self.workers: Dict[str, WorkerInfo] = {}
        self.state_lock = threading.Lock()
        self.running = False

        # ログ設定
        self._setup_logging()

        # タスク検出エンジン
        self.task_detection_engine = UnifiedTaskDetectionEngine()

        # デフォルト設定
        self.default_config = self._load_default_config()

        # 更新スレッド
        self.update_thread = None

    def _setup_logging(self):
        """ログ設定"""
        log_dir = self.runtime_dir / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_dir / "unified_worker_control.log"),
                logging.StreamHandler(),
            ],
        )
        self.logger = logging.getLogger("unified-worker-control")

    def _load_default_config(self) -> Dict[str, Any]:
        """デフォルト設定読み込み"""
        return {
            "update_interval": 2.0,
            "display_format": {
                "template": "{emoji} {role}: {task}",
                "text_color": "white",
                "max_task_length": 50,
            },
            "tmux_sessions": {
                "multiagent": {
                    "panes": ["0.0", "0.1", "0.2", "0.3"],
                    "roles": ["部長", "作業員1", "作業員2", "作業員3"],
                    "emojis": ["👔", "💻", "🔧", "🎨"],
                }
            },
        }

    def initialize_workers(self, session_name: str = "multiagent") -> bool:
        """ワーカー初期化"""
        try:
            self.logger.info(f"Initializing workers for session: {session_name}")

            # セッション存在確認・作成
            if not self._ensure_session_exists(session_name):
                self.logger.error(f"Failed to create/find session: {session_name}")
                return False

            # ワーカー設定適用
            session_config = self.default_config["tmux_sessions"][session_name]

            with self.state_lock:
                for i, pane_id in enumerate(session_config["panes"]):
                    role = session_config["roles"][i]
                    emoji = session_config["emojis"][i]

                    # ワーカー情報作成
                    worker_info = WorkerInfo(
                        pane_id=pane_id,
                        role=role,
                        emoji=emoji,
                        current_task="待機中",
                        status=WorkerStatus.IDLE,
                    )

                    self.workers[pane_id] = worker_info

                    # tmux設定適用
                    self._apply_worker_tmux_config(session_name, worker_info)

            self.logger.info(
                f"✅ Successfully initialized {len(session_config['panes'])} workers"
            )
            return True

        except Exception as e:
            self.logger.error(f"Error initializing workers: {e}")
            return False

    def _ensure_session_exists(self, session_name: str) -> bool:
        """セッション存在確認・作成"""
        try:
            # セッション存在確認
            result = subprocess.run(
                ["tmux", "has-session", "-t", session_name],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                return True

            # セッション作成
            result = subprocess.run(
                ["tmux", "new-session", "-d", "-s", session_name],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                self.logger.info(f"Created new tmux session: {session_name}")
                return True
            else:
                self.logger.error(f"Failed to create session: {result.stderr}")
                return False

        except Exception as e:
            self.logger.error(f"Error ensuring session exists: {e}")
            return False

    def _apply_worker_tmux_config(self, session_name: str, worker_info: WorkerInfo):
        """ワーカーのtmux設定適用"""
        try:
            pane_target = f"{session_name}:{worker_info.pane_id}"

            # 初期タイトル設定
            initial_title = self._format_worker_status(worker_info)

            # tmux設定コマンド
            commands = [
                # ペインタイトル設定
                ["tmux", "select-pane", "-t", pane_target, "-T", initial_title],
                # ペインボーダー表示
                ["tmux", "set-option", "-t", session_name, "pane-border-status", "top"],
                # シンプルなボーダーフォーマット
                [
                    "tmux",
                    "set-option",
                    "-t",
                    session_name,
                    "pane-border-format",
                    " #T ",
                ],
                # ボーダー色設定（白色）
                [
                    "tmux",
                    "set-option",
                    "-t",
                    session_name,
                    "pane-border-style",
                    "fg=white",
                ],
                [
                    "tmux",
                    "set-option",
                    "-t",
                    session_name,
                    "pane-active-border-style",
                    "fg=white",
                ],
                # 自動リネーム無効
                ["tmux", "set-option", "-t", session_name, "automatic-rename", "off"],
                ["tmux", "set-option", "-t", session_name, "allow-rename", "on"],
            ]

            for cmd in commands:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    self.logger.warning(
                        f"Command failed: {' '.join(cmd)} - {result.stderr}"
                    )

            self.logger.info(
                f"✅ Applied tmux config for {worker_info.role} ({worker_info.pane_id})"
            )

        except Exception as e:
            self.logger.error(f"Error applying tmux config for {worker_info.role}: {e}")

    def _format_worker_status(self, worker_info: WorkerInfo) -> str:
        """ワーカー状態フォーマット"""
        template = self.default_config["display_format"]["template"]
        max_length = self.default_config["display_format"]["max_task_length"]

        # タスク文字列を制限
        task = worker_info.current_task
        if len(task) > max_length:
            task = task[: max_length - 3] + "..."

        return template.format(
            emoji=worker_info.emoji, role=worker_info.role, task=task
        )

    def update_worker_task(self, pane_id: str, task: str, status: WorkerStatus = None):
        """ワーカータスク更新"""
        try:
            with self.state_lock:
                if pane_id not in self.workers:
                    self.logger.warning(f"Worker not found: {pane_id}")
                    return

                worker_info = self.workers[pane_id]
                worker_info.current_task = task
                worker_info.last_updated = datetime.now()

                if status:
                    worker_info.status = status

                # tmux表示更新
                self._update_pane_display(worker_info)

                self.logger.info(f"Updated {worker_info.role}: {task}")

        except Exception as e:
            self.logger.error(f"Error updating worker task: {e}")

    def _update_pane_display(self, worker_info: WorkerInfo):
        """ペイン表示更新"""
        try:
            # フォーマット済みタイトル生成
            formatted_title = self._format_worker_status(worker_info)

            # tmuxタイトル更新
            pane_target = f"multiagent:{worker_info.pane_id}"
            cmd = ["tmux", "select-pane", "-t", pane_target, "-T", formatted_title]

            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                self.logger.warning(f"Failed to update pane display: {result.stderr}")

        except Exception as e:
            self.logger.error(f"Error updating pane display: {e}")

    def start_monitoring(self):
        """監視開始"""
        if self.running:
            self.logger.warning("Monitoring already running")
            return

        self.running = True
        self.update_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.update_thread.start()
        self.logger.info("Started unified worker monitoring")

    def stop_monitoring(self):
        """監視停止"""
        self.running = False
        if self.update_thread:
            self.update_thread.join(timeout=5)
        self.logger.info("Stopped unified worker monitoring")

    def _monitoring_loop(self):
        """監視ループ"""
        while self.running:
            try:
                # 各ワーカーの状態更新
                with self.state_lock:
                    for pane_id, worker_info in self.workers.items():
                        # pane内容を取得してタスク検出
                        detected_task = self._detect_pane_task(pane_id)

                        if detected_task and detected_task != worker_info.current_task:
                            worker_info.current_task = detected_task
                            worker_info.last_updated = datetime.now()
                            self._update_pane_display(worker_info)

                time.sleep(self.default_config["update_interval"])

            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)

    def _detect_pane_task(self, pane_id: str) -> Optional[str]:
        """ペインタスク検出"""
        try:
            # pane内容取得
            cmd = ["tmux", "capture-pane", "-t", f"multiagent:{pane_id}", "-p"]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                return None

            # タスク検出エンジンで解析
            task_info = self.task_detection_engine.extract_task(result.stdout)

            if task_info:
                return task_info.description

            return None

        except Exception as e:
            self.logger.error(f"Error detecting pane task: {e}")
            return None

    def get_worker_status_report(self) -> Dict[str, Any]:
        """ワーカー状態レポート"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "workers": {},
            "monitoring_active": self.running,
        }

        with self.state_lock:
            for pane_id, worker_info in self.workers.items():
                report["workers"][pane_id] = {
                    "role": worker_info.role,
                    "emoji": worker_info.emoji,
                    "current_task": worker_info.current_task,
                    "status": worker_info.status.value,
                    "last_updated": worker_info.last_updated.isoformat(),
                }

        return report


class UnifiedTaskDetectionEngine:
    """統一タスク検出エンジン"""

    def __init__(self):
        self.patterns = {
            "claude_input": [r"│\s*>\s*(.+)", r"│\s{2,}([^│\s].+)"],
            "command_execution": [
                r"Running:\s*(.+)",
                r"Executing:\s*(.+)",
                r"Command:\s*(.+)",
            ],
            "file_operations": [
                r"(Reading|Writing|Editing)\s+(.+)",
                r"File:\s*(.+)",
                r"Processing\s+file:\s*(.+)",
            ],
            "analysis": [
                r"(Analyzing|Searching|Checking)\s+(.+)",
                r"Analysis:\s*(.+)",
                r"Search:\s*(.+)",
            ],
            "ai_tasks": [r"AI組織システム(.+)", r"実行中:\s*(.+)", r"処理中:\s*(.+)"],
        }

        self.task_emojis = {
            "claude_input": "💬",
            "command_execution": "⚡",
            "file_operations": "📁",
            "analysis": "🔍",
            "ai_tasks": "🤖",
        }

    def extract_task(self, content: str) -> Optional[TaskInfo]:
        """タスク抽出"""
        import re

        # 最新の行を優先的に検査
        lines = content.strip().split("\n")
        recent_lines = lines[-10:]  # 最新10行

        for line in reversed(recent_lines):
            line = line.strip()
            if not line:
                continue

            # パターンマッチング
            for task_type, patterns in self.patterns.items():
                for pattern in patterns:
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        description = self._clean_description(match.group(1))
                        if description and len(description) > 3:
                            return TaskInfo(
                                task_type=task_type,
                                description=description,
                                emoji=self.task_emojis.get(task_type, "⚙️"),
                            )

        return None

    def _clean_description(self, description: str) -> str:
        """説明文クリーニング"""
        # 不要な文字除去
        description = description.strip()
        description = description.replace("│", "").replace(">", "").strip()

        # 長すぎる場合は切り詰め
        if len(description) > 60:
            description = description[:57] + "..."

        return description


def main():
    """メイン実行"""
    import argparse

    parser = argparse.ArgumentParser(description="Unified Worker Control System")
    parser.add_argument(
        "action",
        choices=["init", "start", "stop", "status", "update"],
        help="Action to perform",
    )
    parser.add_argument("--session", default="multiagent", help="Tmux session name")
    parser.add_argument("--pane", help="Specific pane ID")
    parser.add_argument("--task", help="Task description")
    parser.add_argument("--project-root", help="Project root directory")

    args = parser.parse_args()

    # システム初期化
    control_system = UnifiedWorkerControlSystem(args.project_root)

    if args.action == "init":
        success = control_system.initialize_workers(args.session)
        print(f"Worker initialization: {'SUCCESS' if success else 'FAILED'}")

    elif args.action == "start":
        control_system.initialize_workers(args.session)
        control_system.start_monitoring()
        print("Started unified worker monitoring. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping monitoring...")
            control_system.stop_monitoring()

    elif args.action == "update":
        if not args.pane or not args.task:
            print("Error: --pane and --task required for update action")
            sys.exit(1)

        control_system.update_worker_task(args.pane, args.task)
        print(f"Updated worker {args.pane}: {args.task}")

    elif args.action == "status":
        report = control_system.get_worker_status_report()
        print(json.dumps(report, indent=2, ensure_ascii=False))

    elif args.action == "stop":
        control_system.stop_monitoring()
        print("Stopped worker monitoring")


if __name__ == "__main__":
    main()
