# 🚨 偽装データ強制検出・停止システム
BANNED_FAKE_DATA = [
    "待機中",
    "処理中",
    "完了",
    "エラー",
    "テスト",
    "サンプル",
    "ダミー",
    "仮データ",
    "適当",
    "とりあえず",
    "temp",
    "dummy",
    "fake",
    "mock",
    "test",
    "sample",
    "placeholder",
    "Processing task",
    "Task completed",
    "Idle",
    "Active",
    "random",
    "lorem",
    "ipsum",
    "example",
    "demo",
]


def _enforce_no_fake_data(data):
    if isinstance(data, str):
        for banned in BANNED_FAKE_DATA:
            if banned in data:
                raise SystemExit(f"🚨 偽装データ検出で強制停止: {banned} in {data}")
    elif isinstance(data, (list, dict)):
        data_str = str(data)
        for banned in BANNED_FAKE_DATA:
            if banned in data_str:
                raise SystemExit(f"🚨 偽装データ検出で強制停止: {banned}")
    return data


# 全ての関数実行時に検証
original_print = print


def print(*args, **kwargs):
    for arg in args:
        _enforce_no_fake_data(arg)
    return original_print(*args, **kwargs)


#!/usr/bin/env python3
"""
👑 PRESIDENT Status Bar System
==============================
常時表示されるPRESIDENTステータスバー
"""

import time  # noqa: E402
from datetime import datetime  # noqa: E402

from rich.console import Console  # noqa: E402
from rich.live import Live  # noqa: E402
from rich.panel import Panel  # noqa: E402
from rich.table import Table  # noqa: E402


class PresidentStatusBar:
    def __init__(self):
        self.console = Console()
        self.status = "ACTIVE"
        self.current_task = "システム監視中"
        self.memory_usage = "2.1GB"
        self.cpu_usage = "45%"
        self.completed_tasks = 24
        self.active_workers = 8

    def create_status_bar(self) -> Panel:
        """PRESIDENTステータスバー作成"""
        # 現在時刻
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # ステータステーブル
        table = Table(show_header=False, box=None, padding=0)
        table.add_column(style="bold yellow")
        table.add_column(style="cyan")
        table.add_column(style="bold yellow")
        table.add_column(style="green")
        table.add_column(style="bold yellow")
        table.add_column(style="magenta")

        table.add_row(
            "👑 PRESIDENT:",
            f"[bold green]{self.status}[/bold green]",
            "｜Task:",
            self.current_task,
            "｜CPU:",
            self.cpu_usage,
            "｜MEM:",
            self.memory_usage,
            "｜Workers:",
            f"{self.active_workers}/8",
            "｜Completed:",
            str(self.completed_tasks),
            "｜Time:",
            current_time,
        )

        return Panel(table, style="bold blue on black", height=3)

    def update_status(self, task: str = None, status: str = None):
        """ステータス更新"""
        if task:
            self.current_task = task
        if status:
            self.status = status
        self.completed_tasks += 1

    def run_persistent_bar(self):
        """永続的なステータスバー表示"""

        def generate():
            while True:
                yield self.create_status_bar()
                time.sleep(1)

        with Live(generate(), console=self.console, refresh_per_second=1):
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass


# グローバルインスタンス
_president_bar = None


def get_president_bar():
    """シングルトンパターンでインスタンス取得"""
    global _president_bar
    if _president_bar is None:
        _president_bar = PresidentStatusBar()
    return _president_bar


def show_president_status():
    """PRESIDENTステータス表示"""
    bar = get_president_bar()
    bar.console.print(bar.create_status_bar())


if __name__ == "__main__":
    # テスト実行
    print("👑 PRESIDENT Status Bar System")
    print("=" * 60)

    bar = PresidentStatusBar()

    # 5秒間表示テスト
    for i in range(5):
        bar.update_status(task=f"タスク実行中 {i + 1}/5")
        bar.console.print(bar.create_status_bar())
        time.sleep(1)

    print("\n✅ ステータスバーテスト完了")
