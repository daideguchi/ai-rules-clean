#!/usr/bin/env python3
"""
📝 Conversation Logger - 会話ログシステム
======================================
ユーザー要求の「読み上げ用詳細記録」会話ログシステム
user発言→AI応答形式での完全記録・TTS対応
"""

import json
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class ConversationEntry:
    """会話エントリ"""

    timestamp: str
    entry_type: str  # user_message, ai_response, system_action
    content: str
    metadata: Dict[str, Any]
    tts_formatted: Optional[str] = None


class ConversationLogger:
    """会話ログシステム"""

    def __init__(self):
        self.project_root = Path("/Users/dd/Desktop/1_dev/coding-rule2")
        self.logs_dir = self.project_root / "runtime" / "conversation_logs"
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        # 現在の会話ログファイル
        self.current_log_file = (
            self.logs_dir
            / f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        self.entries: List[ConversationEntry] = []

        # TTS設定
        self.tts_enabled = False
        self.tts_format = "user発言→AI応答"

        # セッション情報読み込み
        self._load_session_info()

    def _load_session_info(self):
        """セッション情報の読み込み"""
        try:
            session_file = (
                self.project_root
                / "src"
                / "memory"
                / "core"
                / "session-records"
                / "current-session.json"
            )
            if session_file.exists():
                with open(session_file, encoding="utf-8") as f:
                    session_data = json.load(f)

                conv_log = session_data.get("conversation_log", {})
                self.tts_enabled = conv_log.get("tts_enabled", False)

                # 既存の会話IDがあれば引き継ぎ
                existing_conv_id = conv_log.get("current_conversation_id")
                if existing_conv_id:
                    # 既存ログファイルを探す
                    existing_log = self.logs_dir / f"{existing_conv_id}.json"
                    if existing_log.exists():
                        self.current_log_file = existing_log
                        self._load_existing_entries()
        except Exception:
            pass

    def _load_existing_entries(self):
        """既存エントリの読み込み"""
        try:
            if self.current_log_file.exists():
                with open(self.current_log_file, encoding="utf-8") as f:
                    data = json.load(f)

                self.entries = [
                    ConversationEntry(**entry) for entry in data.get("entries", [])
                ]
        except Exception:
            self.entries = []

    def log_user_message(self, message: str, metadata: Dict[str, Any] = None):
        """ユーザーメッセージのログ"""
        entry = ConversationEntry(
            timestamp=datetime.now().isoformat(),
            entry_type="user_message",
            content=message,
            metadata=metadata or {},
            tts_formatted=self._format_for_tts(message, "user"),
        )

        self.entries.append(entry)
        self._save_log()
        self._update_session_info()

    def log_ai_response(self, response: str, metadata: Dict[str, Any] = None):
        """AI応答のログ"""
        entry = ConversationEntry(
            timestamp=datetime.now().isoformat(),
            entry_type="ai_response",
            content=response,
            metadata=metadata or {},
            tts_formatted=self._format_for_tts(response, "ai"),
        )

        self.entries.append(entry)
        self._save_log()
        self._update_session_info()

    def log_system_action(self, action: str, details: Dict[str, Any] = None):
        """システムアクションのログ"""
        entry = ConversationEntry(
            timestamp=datetime.now().isoformat(),
            entry_type="system_action",
            content=action,
            metadata=details or {},
            tts_formatted=self._format_for_tts(action, "system"),
        )

        self.entries.append(entry)
        self._save_log()

    def _format_for_tts(self, content: str, speaker_type: str) -> str:
        """TTS用フォーマット"""
        if not self.tts_enabled:
            return None

        # 基本的なTTSフォーマット
        if speaker_type == "user":
            return f"ユーザー発言: {content}"
        elif speaker_type == "ai":
            return f"AI応答: {content}"
        elif speaker_type == "system":
            return f"システム: {content}"

        return content

    def _save_log(self):
        """ログの保存"""
        log_data = {
            "conversation_id": self.current_log_file.stem,
            "created_at": self.entries[0].timestamp
            if self.entries
            else datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "entry_count": len(self.entries),
            "tts_enabled": self.tts_enabled,
            "format": self.tts_format,
            "entries": [asdict(entry) for entry in self.entries],
        }

        try:
            with open(self.current_log_file, "w", encoding="utf-8") as f:
                json.dump(log_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"会話ログ保存エラー: {e}", file=sys.stderr)

    def _update_session_info(self):
        """セッション情報の更新"""
        try:
            session_file = (
                self.project_root
                / "src"
                / "memory"
                / "core"
                / "session-records"
                / "current-session.json"
            )
            if session_file.exists():
                with open(session_file, encoding="utf-8") as f:
                    session_data = json.load(f)

                # 会話ログ情報を更新
                session_data["conversation_log"]["current_conversation_id"] = (
                    self.current_log_file.stem
                )
                session_data["conversation_log"]["message_count"] = len(self.entries)
                session_data["session_quality"]["conversation_logging_active"] = True
                session_data["last_updated"] = datetime.now().isoformat()

                with open(session_file, "w", encoding="utf-8") as f:
                    json.dump(session_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"セッション情報更新エラー: {e}", file=sys.stderr)

    def generate_tts_summary(self) -> str:
        """TTS用サマリー生成"""
        if not self.entries:
            return "会話記録がありません。"

        summary_parts = []

        # 基本統計
        user_messages = len([e for e in self.entries if e.entry_type == "user_message"])
        ai_responses = len([e for e in self.entries if e.entry_type == "ai_response"])
        system_actions = len(
            [e for e in self.entries if e.entry_type == "system_action"]
        )

        summary_parts.append(
            f"会話統計: ユーザー発言{user_messages}件、AI応答{ai_responses}件、システムアクション{system_actions}件"
        )

        # 最近の重要な交流
        recent_entries = self.entries[-10:]  # 最新10エントリ

        summary_parts.append("最近の会話:")
        for entry in recent_entries:
            if entry.tts_formatted:
                summary_parts.append(f"- {entry.tts_formatted}")

        return "\n".join(summary_parts)

    def get_conversation_context(self, last_n: int = 5) -> List[Dict[str, str]]:
        """会話コンテキストの取得"""
        recent_entries = self.entries[-last_n * 2 :]  # user+ai ペアでlast_n個

        context = []
        for entry in recent_entries:
            if entry.entry_type in ["user_message", "ai_response"]:
                context.append(
                    {
                        "type": entry.entry_type,
                        "content": entry.content,
                        "timestamp": entry.timestamp,
                    }
                )

        return context

    def search_conversation(self, query: str) -> List[ConversationEntry]:
        """会話検索"""
        results = []
        query_lower = query.lower()

        for entry in self.entries:
            if query_lower in entry.content.lower():
                results.append(entry)

        return results


def main():
    """会話ログシステムのテスト"""
    logger = ConversationLogger()

    print("📝 会話ログシステム初期化完了")
    print(f"ログファイル: {logger.current_log_file}")
    print(f"TTS有効: {logger.tts_enabled}")

    # テストログ
    logger.log_user_message(
        "{{mistake_count}}回ミス防止システムのテストメッセージです", {"test": True}
    )
    logger.log_ai_response(
        "承知いたしました。{{mistake_count}}回ミス防止システムが正常に動作しています。",
        {"system_status": "operational"},
    )
    logger.log_system_action(
        "conversation_logger.py テスト実行完了", {"test_result": "success"}
    )

    print(f"\n📊 ログエントリ数: {len(logger.entries)}")

    # TTS用サマリー
    if logger.tts_enabled:
        print(f"\n🔊 TTS用サマリー:\n{logger.generate_tts_summary()}")

    # 会話コンテキスト
    context = logger.get_conversation_context(2)
    print(f"\n💬 会話コンテキスト: {len(context)}エントリ")
    for ctx in context:
        print(f"  {ctx['type']}: {ctx['content'][:50]}...")


if __name__ == "__main__":
    main()
