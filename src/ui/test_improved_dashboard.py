#!/usr/bin/env python3
"""
🧪 Test Improved Dashboard
========================
テスト用改良ダッシュボード
"""

import time

from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

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


def create_detailed_worker_panel(worker_data):
    """詳細ワーカーパネル作成"""

    # Status colors
    status_colors = {
        "ACTIVE": "green",
        "PROCESSING": "blue",
        "IDLE": "yellow",
        "ERROR": "red",
    }

    # Priority colors
    priority_colors = {
        "CRITICAL": "bold red",
        "HIGH": "red",
        "MEDIUM": "yellow",
        "LOW": "dim",
    }

    status_color = status_colors.get(worker_data["status"], "white")
    priority_color = priority_colors.get(worker_data["priority"], "dim")

    # Progress bar
    progress = worker_data["progress"]
    progress_bar = "█" * int(progress / 10) + "░" * (10 - int(progress / 10))

    # Create content
    content = Text()
    content.append(f"{worker_data['icon']} {worker_data['name']}\n", style="bold")
    content.append(f"役割: {worker_data['role']}\n", style="dim")
    content.append("状態: ", style="dim")
    content.append(f"{worker_data['status']}", style=status_color)
    content.append(" | 優先度: ", style="dim")
    content.append(f"{worker_data['priority']}\n", style=priority_color)
    content.append(
        f"\n🎯 現在タスク: {worker_data['current_task']}\n", style="bold yellow"
    )
    content.append(f"📋 具体TODO: {worker_data['todo']}\n", style="bold cyan")
    content.append(f"🔄 今の作業: {worker_data['action']}\n", style="bold green")
    content.append(f"🏁 次目標: {worker_data['milestone']}\n", style="bold white")
    content.append(f"⏰ 期限: {worker_data['deadline']}\n", style="bold red")
    content.append(f"\n進捗: [{progress}%] {progress_bar}\n", style="green")

    return Panel(
        content,
        title=f"[{status_color}]{worker_data['icon']} {worker_data['name']}[/]",
        border_style=status_color,
        height=12,
    )


def create_mission_panel():
    """プロジェクト目標パネル"""

    content = Text()
    content.append("🎯 PROJECT MISSION\n", style="bold yellow")
    content.append(
        "目標: {{mistake_count}}回ミス防止AIエージェントシステムの完全稼働\n",
        style="bold cyan",
    )
    content.append("現在: 最終品質確認・運用準備\n", style="bold green")
    content.append("完了予定: 2025-07-09 15:00\n", style="bold white")
    content.append("優先度: CRITICAL\n", style="bold red")
    content.append("\n全体進捗: [87%] ████████████████████\n", style="green")

    return Panel(
        content, title="🎯 MISSION CONTROL", border_style="bold blue", height=8
    )


def main():
    """メイン実行"""

    console = Console()

    # サンプルワーカーデータ
    workers = [
        {
            "name": "PRESIDENT",
            "icon": "👑",
            "role": "全体統括・意思決定",
            "status": "ACTIVE",
            "priority": "CRITICAL",
            "current_task": "システム最終確認",
            "todo": "ダッシュボード品質向上",
            "action": "ユーザー要求対応中",
            "milestone": "運用開始承認",
            "deadline": "14:50",
            "progress": 85,
        },
        {
            "name": "COORDINATOR",
            "icon": "🔄",
            "role": "タスク調整・リソース管理",
            "status": "PROCESSING",
            "priority": "HIGH",
            "current_task": "ワーカー間協調制御",
            "todo": "8ワーカー負荷分散",
            "action": "タスクキュー最適化",
            "milestone": "完全同期達成",
            "deadline": "14:55",
            "progress": 72,
        },
        {
            "name": "DATA_ENGINEER",
            "icon": "📊",
            "role": "データ処理・DB管理",
            "status": "PROCESSING",
            "priority": "HIGH",
            "current_task": "リアルタイムデータ処理",
            "todo": "ワーカー状態データ管理",
            "action": "PostgreSQL最適化実行",
            "milestone": "データ同期完了",
            "deadline": "14:50",
            "progress": 91,
        },
        {
            "name": "SECURITY_SPECIALIST",
            "icon": "🔒",
            "role": "セキュリティ監査・保護",
            "status": "ACTIVE",
            "priority": "HIGH",
            "current_task": "システム安全性確認",
            "todo": "表示データ機密性チェック",
            "action": "セキュリティスキャン実行",
            "milestone": "セキュリティ承認",
            "deadline": "14:55",
            "progress": 82,
        },
    ]

    print("📊 Test Improved Dashboard")
    print("=" * 60)
    print("🎯 TODO・作業内容・全体目標を完全可視化")
    print("=" * 60)

    for i in range(3):
        console.clear()

        # Mission control panel
        mission_panel = create_mission_panel()

        # Worker panels
        worker_panels = []
        for worker in workers:
            # Update progress for demo
            worker["progress"] = min(95, worker["progress"] + i)
            panel = create_detailed_worker_panel(worker)
            worker_panels.append(panel)

        # Display mission
        console.print(mission_panel)

        # Display workers in 2x2 grid
        top_row = Columns(worker_panels[:2], equal=True)
        bottom_row = Columns(worker_panels[2:], equal=True)

        console.print(top_row)
        console.print(bottom_row)

        console.print(f"\n⏱️  更新 {i + 1}/3 | 次回更新: 3秒後")
        time.sleep(3)

    print("\n✅ 改良ダッシュボードテスト完了!")
    print("各ワーカーの詳細なTODO・作業内容・全体目標が表示されました。")


if __name__ == "__main__":
    main()
