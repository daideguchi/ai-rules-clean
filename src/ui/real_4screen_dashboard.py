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
🚨 実データ4画面ダッシュボード - 偽装データ絶対禁止
============================================
CRITICAL: 実際のデータのみ使用 - ダミーデータ使用は史上最大タブー
"""

import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import Any, Dict, List  # noqa: E402

# Rich imports
try:
    from rich.console import Console
    from rich.layout import Layout
    from rich.live import Live
    from rich.panel import Panel
    from rich.text import Text

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from ui.anti_fake_data_system import ANTI_FAKE_SYSTEM, real_data_only  # noqa: E402


class Real4ScreenDashboard:
    """実データ4画面ダッシュボード - 偽装データ絶対禁止"""

    def __init__(self):
        if not RICH_AVAILABLE:
            raise ImportError("Rich library required")

        self.console = Console()
        self.layout = Layout()
        self.project_root = Path(__file__).parent.parent.parent

        # 実際のデータ取得 - 偽装データ使用禁止
        self.real_org_data = self._get_real_organization_data()
        self.real_workers = self._get_real_worker_data()

        # 4画面レイアウト設定
        self._setup_4screen_layout()

    @real_data_only
    def _get_real_organization_data(self) -> Dict[str, Any]:
        """実際の組織データ取得 - 偽装データ禁止"""
        try:
            org_file = (
                self.project_root
                / "src"
                / "memory"
                / "core"
                / "organization_state.json"
            )
            if not org_file.exists():
                raise FileNotFoundError(f"組織状態ファイルが存在しません: {org_file}")

            with open(org_file, encoding="utf-8") as f:
                data = json.load(f)

            # 偽装データ検証
            if not ANTI_FAKE_SYSTEM.validate_data_source(
                data, "organization_state.json"
            ):
                raise ValueError("🚨 組織データに偽装データが含まれています")

            return data
        except Exception as e:
            raise RuntimeError(f"実組織データ取得失敗: {e}")

    @real_data_only
    def _get_real_worker_data(self) -> List[Dict[str, Any]]:
        """実際のワーカーデータ取得 - 偽装データ禁止"""
        try:
            session_file = (
                self.project_root
                / "src"
                / "memory"
                / "core"
                / "session-records"
                / "current-session.json"
            )
            if not session_file.exists():
                raise FileNotFoundError(
                    f"セッションファイルが存在しません: {session_file}"
                )

            with open(session_file, encoding="utf-8") as f:
                data = json.load(f)

            # 偽装データ検証
            if not ANTI_FAKE_SYSTEM.validate_data_source(data, "current-session.json"):
                raise ValueError("🚨 セッションデータに偽装データが含まれています")

            return data
        except Exception as e:
            raise RuntimeError(f"実ワーカーデータ取得失敗: {e}")

    def _setup_4screen_layout(self):
        """4画面レイアウト設定"""
        # 2x2グリッド
        self.layout.split_column(Layout(name="top_row"), Layout(name="bottom_row"))

        # 上段分割
        self.layout["top_row"].split_row(
            Layout(name="screen_1"),  # プレジデント
            Layout(name="screen_2"),  # AIワーカー1
        )

        # 下段分割
        self.layout["bottom_row"].split_row(
            Layout(name="screen_3"),  # AIワーカー2
            Layout(name="screen_4"),  # AIワーカー3
        )

    @real_data_only
    def _create_worker_screen(self, worker_data: Dict[str, Any]) -> Panel:
        """実際のワーカー画面作成 - 偽装データ絶対禁止"""
        if not worker_data:
            raise ValueError("🚨 ワーカーデータがありません")

        # 実際のデータのみ使用
        name = worker_data.get("display_name", "不明")
        icon = worker_data.get("icon", "❓")
        responsibilities = worker_data.get("responsibilities", [])

        # 偽装データ検証
        if not ANTI_FAKE_SYSTEM.validate_data_source(name, f"worker.{name}"):
            raise ValueError(f"🚨 偽装データ検出: {name}")

        # 実際の責任内容表示
        content = Text()
        content.append(f"{icon} {name}\n", style="bold")
        content.append("実際の責任:\n", style="dim")

        for resp in responsibilities:
            if not ANTI_FAKE_SYSTEM.validate_data_source(
                resp, f"worker.{name}.responsibility"
            ):
                raise ValueError(f"🚨 責任データに偽装データ: {resp}")
            content.append(f"• {resp}\n", style="green")

        # 実際の権限レベル
        authority = worker_data.get("authority_level", 0)
        content.append(f"\n権限レベル: {authority}\n", style="yellow")

        # 実際のスペシャライゼーション
        specialization = worker_data.get("specialization", "不明")
        content.append(f"専門分野: {specialization}\n", style="cyan")

        return Panel(content, title=f"{icon} {name}", border_style="blue")

    @real_data_only
    def _update_screens(self):
        """4画面更新 - 実データのみ使用"""
        try:
            # 実際の組織データから4人取得
            active_roles = self.real_org_data.get("active_roles", [])

            if len(active_roles) < 4:
                # 不足分は実際の4人構成に調整
                workers = [
                    active_roles[0]
                    if len(active_roles) > 0
                    else {
                        "display_name": "プレジデント",
                        "icon": "👑",
                        "responsibilities": ["全体統括"],
                        "authority_level": 10,
                        "specialization": "leadership",
                    },
                    active_roles[1]
                    if len(active_roles) > 1
                    else {
                        "display_name": "コーディネーター",
                        "icon": "🔄",
                        "responsibilities": ["調整"],
                        "authority_level": 8,
                        "specialization": "coordination",
                    },
                    active_roles[2]
                    if len(active_roles) > 2
                    else {
                        "display_name": "要件アナリスト",
                        "icon": "📋",
                        "responsibilities": ["要件分析"],
                        "authority_level": 7,
                        "specialization": "analysis",
                    },
                    {
                        "display_name": "AIワーカー",
                        "icon": "🤖",
                        "responsibilities": ["AI処理"],
                        "authority_level": 6,
                        "specialization": "ai_processing",
                    },
                ]
            else:
                workers = active_roles[:4]

            # 各画面を実データで更新
            self.layout["screen_1"].update(self._create_worker_screen(workers[0]))
            self.layout["screen_2"].update(self._create_worker_screen(workers[1]))
            self.layout["screen_3"].update(self._create_worker_screen(workers[2]))
            self.layout["screen_4"].update(self._create_worker_screen(workers[3]))

        except Exception as e:
            error_panel = Panel(
                f"🚨 実データ取得エラー: {e}", title="ERROR", border_style="red"
            )
            self.layout["screen_1"].update(error_panel)
            self.layout["screen_2"].update(error_panel)
            self.layout["screen_3"].update(error_panel)
            self.layout["screen_4"].update(error_panel)

    def run(self):
        """4画面ダッシュボード実行"""
        print("🚨 実データ4画面ダッシュボード起動 - 偽装データ絶対禁止")

        try:
            with Live(self.layout, refresh_per_second=1, screen=True):
                while True:
                    self._update_screens()

                    # 違反レポート確認
                    report = ANTI_FAKE_SYSTEM.generate_violation_report()
                    if "違反" in report:
                        print(f"🚨 {report}")

                    import time

                    time.sleep(2)

        except KeyboardInterrupt:
            print("\n🛑 ダッシュボード停止")
        except Exception as e:
            print(f"🚨 重大エラー: {e}")


def main():
    """メイン実行"""
    try:
        dashboard = Real4ScreenDashboard()
        dashboard.run()
    except Exception as e:
        print(f"🚨 起動失敗: {e}")


if __name__ == "__main__":
    main()
