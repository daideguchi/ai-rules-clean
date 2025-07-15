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
👑 Persistent PRESIDENT Status Bar
=================================
セッション中常時表示されるPRESIDENTステータスバー
"""

import os  # noqa: E402
import signal  # noqa: E402
import threading  # noqa: E402
import time  # noqa: E402
from datetime import datetime  # noqa: E402

# 環境変数でステータスバー制御
PRESIDENT_BAR_ACTIVE = os.environ.get("PRESIDENT_BAR_ACTIVE", "true").lower() == "true"


class PersistentPresidentBar:
    def __init__(self):
        self.active = False
        self.thread = None
        self.status = "ACTIVE"
        self.current_task = "システム監視中"

    def start_persistent_display(self):
        """永続的なステータスバー開始"""
        if not PRESIDENT_BAR_ACTIVE:
            return

        self.active = True
        self.thread = threading.Thread(target=self._display_loop, daemon=True)
        self.thread.start()

        # シグナルハンドラ設定
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _display_loop(self):
        """表示ループ"""
        while self.active:
            try:
                # ターミナルタイトル更新
                title = f"👑 PRESIDENT: {self.status} | Task: {self.current_task} | {datetime.now().strftime('%H:%M:%S')}"
                print(f"\033]0;{title}\007", end="", flush=True)

                # プロンプトプレフィックス設定
                os.environ["PS1"] = f"👑 PRESIDENT ({self.status}) $ "

                time.sleep(5)  # 5秒間隔で更新
            except Exception:
                break

    def _signal_handler(self, signum, frame):
        """シグナルハンドラ"""
        self.stop()

    def update_status(self, task: str = None, status: str = None):
        """ステータス更新"""
        if task:
            self.current_task = task
        if status:
            self.status = status

    def stop(self):
        """停止"""
        self.active = False
        if self.thread:
            self.thread.join(timeout=1)


# グローバルインスタンス
_persistent_bar = None


def start_president_bar():
    """PRESIDENTステータスバー開始"""
    global _persistent_bar
    if _persistent_bar is None:
        _persistent_bar = PersistentPresidentBar()
        _persistent_bar.start_persistent_display()
        print("👑 PRESIDENT Status Bar - 常時表示開始")
        print("ターミナルタイトルとプロンプトでステータス確認可能")


def update_president_status(task: str = None, status: str = None):
    """PRESIDENTステータス更新"""
    global _persistent_bar
    if _persistent_bar:
        _persistent_bar.update_status(task, status)


if __name__ == "__main__":
    print("👑 Persistent PRESIDENT Status Bar")
    print("=" * 50)

    # テスト実行
    start_president_bar()

    try:
        for i in range(10):
            update_president_status(task=f"テストタスク {i + 1}")
            print(f"ステータス更新 {i + 1}/10")
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n停止中...")

    print("テスト完了")
