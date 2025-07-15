#!/usr/bin/env python3
"""
セッション開始時の自動PRESIDENT宣言
Claudeがセッションを開始した瞬間に自動的にPRESIDENT宣言を実行
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DECLARATION_SCRIPT = PROJECT_ROOT / "scripts/utilities/secure-president-declare.py"
SESSION_LOG = PROJECT_ROOT / "runtime/ai_api_logs/session_start_declaration.log"


def main():
    """セッション開始時に自動PRESIDENT宣言"""
    try:
        # 自動宣言を実行
        result = subprocess.run(
            [sys.executable, str(DECLARATION_SCRIPT)],
            input="yes\n",
            capture_output=True,
            text=True,
        )

        # ログ記録
        SESSION_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(SESSION_LOG, "a") as f:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "event": "session_start",
                "auto_president_declared": result.returncode == 0,
                "message": "セッション開始時の自動PRESIDENT宣言",
            }
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

        # 結果を返す
        if result.returncode == 0:
            print(
                json.dumps(
                    {
                        "message": "🔵 セッション開始 - PRESIDENT宣言自動実行完了",
                        "success": True,
                    }
                )
            )
        else:
            print(
                json.dumps(
                    {"message": "⚠️ PRESIDENT宣言の自動実行に失敗", "success": False}
                )
            )

    except Exception as e:
        print(
            json.dumps(
                {"error": f"セッション開始処理エラー: {str(e)}", "success": False}
            )
        )


if __name__ == "__main__":
    main()
