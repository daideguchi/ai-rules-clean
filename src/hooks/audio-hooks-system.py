#!/usr/bin/env python3
"""
Audio Hooks System - ファイル操作時の音響効果・音声読み上げ・記録
優しい音での操作フィードバックと活動記録システム
"""

import json
import os
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, Optional


class EventType(Enum):
    """イベント種別"""

    FILE_CREATED = "file_created"
    FILE_MODIFIED = "file_modified"
    FILE_DELETED = "file_deleted"
    FOLDER_CREATED = "folder_created"
    FOLDER_DELETED = "folder_deleted"
    VALIDATION_PASSED = "validation_passed"
    VALIDATION_FAILED = "validation_failed"
    SYSTEM_ACTION = "system_action"


@dataclass
class HookEvent:
    """フックイベント構造"""

    event_type: EventType
    path: str
    actor: str
    timestamp: str
    details: Dict
    message: str


class AudioHooksSystem:
    """音響・音声・記録統合システム"""

    def __init__(self, config_path: str = None):
        self.root = Path(__file__).resolve().parents[2]
        self.config = self._load_config(config_path)
        self.sound_enabled = self.config.get("sound_enabled", False)  # デフォルトはオフ
        self.tts_enabled = self.config.get("tts_enabled", False)  # デフォルトはオフ
        self.logging_enabled = self.config.get("logging_enabled", True)

        # 記録ファイルパス
        self.activity_log = self.root / "FILE_OPERATIONS_LOG.md"
        self.interaction_log = self.root / "AI_INTERACTIONS_LOG.md"

        # 音響効果ファイル
        self.sounds = {
            EventType.FILE_CREATED: self.config.get("sounds", {}).get(
                "create", "gentle_create.wav"
            ),
            EventType.FILE_MODIFIED: self.config.get("sounds", {}).get(
                "modify", "soft_modify.wav"
            ),
            EventType.FILE_DELETED: self.config.get("sounds", {}).get(
                "delete", "gentle_delete.wav"
            ),
            EventType.VALIDATION_PASSED: self.config.get("sounds", {}).get(
                "success", "success_chime.wav"
            ),
            EventType.VALIDATION_FAILED: self.config.get("sounds", {}).get(
                "error", "gentle_error.wav"
            ),
        }

        # TTS設定
        self.tts_command = self._detect_tts_command()
        self.tts_rate_limit = 10  # 1分間に最大10回
        self.tts_history = []

    def _load_config(self, config_path: str) -> Dict:
        """設定ファイル読み込み"""
        if config_path and Path(config_path).exists():
            with open(config_path) as f:
                return json.load(f)

        # デフォルト設定
        return {
            "sound_enabled": False,
            "tts_enabled": False,
            "logging_enabled": True,
            "sounds": {
                "create": "gentle_create.wav",
                "modify": "soft_modify.wav",
                "delete": "gentle_delete.wav",
                "success": "success_chime.wav",
                "error": "gentle_error.wav",
            },
        }

    def _detect_tts_command(self) -> Optional[str]:
        """TTS コマンド自動検出"""
        commands = [
            "say",  # macOS
            "espeak-ng",  # Linux
            "pico2wave",  # Linux (Pico TTS)
            "spd-say",  # Linux (Speech Dispatcher)
        ]

        for cmd in commands:
            if subprocess.run(["which", cmd], capture_output=True).returncode == 0:
                return cmd
        return None

    def emit_event(
        self,
        event_type: EventType,
        path: str,
        details: Dict = None,
        custom_message: str = None,
    ):
        """イベント発行"""
        if details is None:
            details = {}

        # メッセージ生成
        message = custom_message or self._generate_message(event_type, path, details)

        event = HookEvent(
            event_type=event_type,
            path=path,
            actor=os.environ.get("USER", "system"),
            timestamp=datetime.now().isoformat(),
            details=details,
            message=message,
        )

        # 非同期処理で各ハンドラー実行
        threading.Thread(target=self._process_event, args=(event,), daemon=True).start()

    def _process_event(self, event: HookEvent):
        """イベント処理（非同期）"""
        try:
            # 1. 音響効果
            if self.sound_enabled:
                self._play_sound(event)

            # 2. 音声読み上げ
            if self.tts_enabled and self._should_announce(event):
                self._text_to_speech(event.message)

            # 3. ログ記録
            if self.logging_enabled:
                self._log_activity(event)

        except Exception as e:
            print(f"Hook処理エラー: {e}", file=sys.stderr)

    def _generate_message(self, event_type: EventType, path: str, details: Dict) -> str:
        """イベントメッセージ生成"""
        file_name = Path(path).name

        messages = {
            EventType.FILE_CREATED: f"📄 新規ファイル作成: {file_name}",
            EventType.FILE_MODIFIED: f"✏️  ファイル更新: {file_name}",
            EventType.FILE_DELETED: f"🗑️  ファイル削除: {file_name}",
            EventType.FOLDER_CREATED: f"📁 新規フォルダ作成: {file_name}",
            EventType.FOLDER_DELETED: f"📁 フォルダ削除: {file_name}",
            EventType.VALIDATION_PASSED: f"✅ 検証成功: {file_name}",
            EventType.VALIDATION_FAILED: f"❌ 検証失敗: {file_name}",
        }

        base_message = messages.get(event_type, f"操作: {file_name}")

        # 詳細情報追加
        if details.get("size"):
            base_message += f" ({details['size']} bytes)"
        if details.get("error"):
            base_message += f" - エラー: {details['error']}"

        return base_message

    def _play_sound(self, event: HookEvent):
        """音響効果再生"""
        sound_file = self.sounds.get(event.event_type)
        if not sound_file:
            return

        sound_path = self.root / "assets" / "sounds" / sound_file

        # サウンドファイルが存在しない場合は生成
        if not sound_path.exists():
            self._generate_default_sound(sound_path, event.event_type)

        # プラットフォーム別再生
        try:
            if sys.platform == "darwin":  # macOS
                subprocess.run(
                    ["afplay", str(sound_path)], check=True, capture_output=True
                )
            elif sys.platform.startswith("linux"):  # Linux
                # 複数のコマンドを試行
                for cmd in ["aplay", "paplay", "play"]:
                    if (
                        subprocess.run(["which", cmd], capture_output=True).returncode
                        == 0
                    ):
                        subprocess.run(
                            [cmd, str(sound_path)], check=True, capture_output=True
                        )
                        break
        except subprocess.CalledProcessError:
            pass  # 音再生失敗は無視

    def _generate_default_sound(self, sound_path: Path, event_type: EventType):
        """デフォルト音響効果生成（SoX使用）"""
        sound_path.parent.mkdir(parents=True, exist_ok=True)

        # SoXコマンド生成（優しい音）
        sox_commands = {
            EventType.FILE_CREATED: "sox -n {} synth 0.3 sine 800 fade 0.1 0.3 0.1",
            EventType.FILE_MODIFIED: "sox -n {} synth 0.2 sine 600 fade 0.05 0.2 0.05",
            EventType.FILE_DELETED: "sox -n {} synth 0.4 sine 400 fade 0.1 0.4 0.2",
            EventType.VALIDATION_PASSED: "sox -n {} synth 0.3 sine 1000:1200 fade 0.1 0.3 0.1",
            EventType.VALIDATION_FAILED: "sox -n {} synth 0.5 sine 300:200 fade 0.1 0.5 0.2",
        }

        command = sox_commands.get(event_type)
        if (
            command
            and subprocess.run(["which", "sox"], capture_output=True).returncode == 0
        ):
            try:
                subprocess.run(
                    command.format(sound_path).split(), check=True, capture_output=True
                )
            except subprocess.CalledProcessError:
                pass

    def _should_announce(self, event: HookEvent) -> bool:
        """音声読み上げ必要性判定"""
        # レート制限チェック
        now = time.time()
        self.tts_history = [
            t for t in self.tts_history if now - t < 60
        ]  # 1分以内のみ保持

        if len(self.tts_history) >= self.tts_rate_limit:
            return False

        # 重要なイベントのみ読み上げ
        important_events = {
            EventType.VALIDATION_FAILED,
            EventType.FILE_DELETED,
            EventType.SYSTEM_ACTION,
        }

        return event.event_type in important_events

    def _text_to_speech(self, message: str):
        """音声読み上げ"""
        if not self.tts_command:
            return

        # 記号除去・短縮
        clean_message = (
            message.replace("📄", "")
            .replace("✏️", "")
            .replace("🗑️", "")
            .replace("📁", "")
        )
        clean_message = clean_message.replace("✅", "").replace("❌", "").strip()

        # 長すぎる場合は短縮
        if len(clean_message) > 50:
            clean_message = clean_message[:47] + "..."

        try:
            if self.tts_command == "say":  # macOS
                subprocess.run(
                    ["say", "-r", "200", clean_message], check=True, capture_output=True
                )
            elif self.tts_command == "espeak-ng":  # Linux
                subprocess.run(
                    ["espeak-ng", "-s", "150", clean_message],
                    check=True,
                    capture_output=True,
                )
            elif self.tts_command == "spd-say":  # Linux
                subprocess.run(
                    ["spd-say", clean_message], check=True, capture_output=True
                )

            # レート制限記録更新
            self.tts_history.append(time.time())

        except subprocess.CalledProcessError:
            pass  # TTS失敗は無視

    def _log_activity(self, event: HookEvent):
        """活動ログ記録"""
        # ファイル操作ログ（最上位）
        if event.event_type in [
            EventType.FILE_CREATED,
            EventType.FILE_MODIFIED,
            EventType.FILE_DELETED,
            EventType.FOLDER_CREATED,
            EventType.FOLDER_DELETED,
        ]:
            self._append_to_log(self.activity_log, event, "ファイル操作")

        # AI相互作用ログ（最上位）
        elif event.event_type in [
            EventType.VALIDATION_PASSED,
            EventType.VALIDATION_FAILED,
            EventType.SYSTEM_ACTION,
        ]:
            self._append_to_log(self.interaction_log, event, "AI相互作用")

    def _append_to_log(self, log_file: Path, event: HookEvent, category: str):
        """ログファイル追記"""
        # ファイルが存在しない場合はヘッダー作成
        if not log_file.exists():
            with open(log_file, "w", encoding="utf-8") as f:
                f.write(f"# {category}記録\n\n")
                f.write("**最終更新**: 自動生成  \n")
                f.write("**記録形式**: タイムスタンプ - メッセージ - 詳細\n\n")

        # エントリ追加
        with open(log_file, "a", encoding="utf-8") as f:
            timestamp = datetime.fromisoformat(event.timestamp).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            f.write(f"- **{timestamp}** - {event.message}")

            if event.details:
                details_str = " | ".join(
                    [f"{k}: {v}" for k, v in event.details.items()]
                )
                f.write(f" | {details_str}")

            f.write(f" | by: {event.actor}\n")


# グローバルインスタンス
_hooks_system = None


def get_hooks_system() -> AudioHooksSystem:
    """シングルトンパターンでhooksシステム取得"""
    global _hooks_system
    if _hooks_system is None:
        _hooks_system = AudioHooksSystem()
    return _hooks_system


def emit_file_created(path: str, details: Dict = None):
    """ファイル作成イベント発行"""
    get_hooks_system().emit_event(EventType.FILE_CREATED, path, details)


def emit_file_modified(path: str, details: Dict = None):
    """ファイル変更イベント発行"""
    get_hooks_system().emit_event(EventType.FILE_MODIFIED, path, details)


def emit_file_deleted(path: str, details: Dict = None):
    """ファイル削除イベント発行"""
    get_hooks_system().emit_event(EventType.FILE_DELETED, path, details)


def emit_validation_result(path: str, passed: bool, details: Dict = None):
    """検証結果イベント発行"""
    event_type = EventType.VALIDATION_PASSED if passed else EventType.VALIDATION_FAILED
    get_hooks_system().emit_event(event_type, path, details)


def main():
    """テスト実行"""
    hooks = AudioHooksSystem()

    # テストイベント
    print("🧪 Audio Hooks System テスト開始")

    hooks.emit_event(EventType.FILE_CREATED, "test-file.py", {"size": 1024})
    time.sleep(1)

    hooks.emit_event(EventType.VALIDATION_PASSED, "test-file.py")
    time.sleep(1)

    hooks.emit_event(EventType.FILE_MODIFIED, "test-file.py", {"size": 2048})

    print("✅ テスト完了 - ログファイルを確認してください")


if __name__ == "__main__":
    main()
