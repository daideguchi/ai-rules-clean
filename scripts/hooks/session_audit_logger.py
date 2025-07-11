#!/opt/homebrew/bin/python3
"""
Session Audit Logger with Audio Hooks Integration
セッション終了時の監査・音響効果・音声読み上げ統合システム
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Audio Hooks System を利用可能な場合は統合
try:
    sys.path.append(str(Path(__file__).resolve().parents[2] / "src"))
    from hooks.audio_hooks_system import AudioHooksSystem, EventType

    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False


def emit_session_end_audio(session_summary: str):
    """セッション終了時の音響・音声効果"""
    if not AUDIO_AVAILABLE:
        return

    try:
        audio_system = AudioHooksSystem()

        # セッション終了イベント発行
        audio_system.emit_event(
            EventType.SYSTEM_ACTION,
            "session_completed",
            {"type": "session_audit", "summary": session_summary},
            "セッション完了",
        )

        # 短縮サマリーでTTS（設定に応じて）
        if audio_system.tts_enabled:
            clean_summary = session_summary.replace("📊", "").replace("✅", "").strip()
            short_summary = clean_summary.split("\n")[0]  # 最初の行のみ
            if len(short_summary) > 30:
                short_summary = short_summary[:27] + "..."

            audio_system._text_to_speech(f"セッション完了。{short_summary}")

    except Exception as e:
        print(f"⚠️ Audio integration failed: {e}", file=sys.stderr)


def main():
    """Stop Hook メイン処理"""
    try:
        # フックからの入力を取得（通常空のJSONまたは基本情報）
        sys.stdin.read().strip()

        # 基本的なセッションサマリー
        session_summary = f"📊 Session ended at {datetime.now().strftime('%H:%M:%S')}"

        # 音響・音声効果（設定に応じて）
        if AUDIO_AVAILABLE:
            emit_session_end_audio(session_summary)

        # ログ出力（非表示設定）
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "event": "session_stop_hook",
            "summary": session_summary,
            "audio_integration": AUDIO_AVAILABLE,
        }

        # Claude Code hookの正常終了レスポンス
        hook_response = {
            "continue": True,
            "suppressOutput": True,  # 出力を抑制
            "audit": audit_entry,
        }

        print(json.dumps(hook_response))
        sys.exit(0)

    except Exception as e:
        # エラー時も正常終了扱い（Claude Codeをブロックしない）
        error_response = {"continue": True, "suppressOutput": True, "error": str(e)}
        print(json.dumps(error_response))
        sys.exit(0)


if __name__ == "__main__":
    main()
