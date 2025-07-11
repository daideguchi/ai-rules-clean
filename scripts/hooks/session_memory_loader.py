#!/usr/bin/env python3
"""
🧠 Session Memory Loader - セッション開始時記憶強制ロード
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# プロジェクトパス追加
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root / "src"))

try:
    from memory.breakthrough_memory_system import BreakthroughMemorySystem

    # 記憶システム初期化
    memory = BreakthroughMemorySystem()

    # セッション開始ログ
    session_start_time = datetime.now().isoformat()
    print(f"🧠 SESSION STARTED: {session_start_time}")
    print("=" * 60)

    # 永続記憶の強制表示
    print("📋 PERMANENT MEMORY INHERITANCE:")
    forever_instructions = memory.ledger_fetch_all()

    for i, instruction in enumerate(forever_instructions, 1):
        print(f"{i:2d}. {instruction}")

    print("=" * 60)

    # 違反履歴確認
    conversation_id = datetime.now().strftime("%Y%m%d")
    strikes = memory.get_strikes(conversation_id)

    if strikes:
        print("⚠️  VIOLATION HISTORY:")
        for rule_id, count in strikes.items():
            print(f"   {rule_id}: {count} strikes")
    else:
        print("✅ NO VIOLATIONS TODAY")

    print("=" * 60)
    print("🚨 MEMORY INHERITANCE ACTIVE")
    print("🚨 VIOLATIONS WILL BE BLOCKED")

    # 記憶継承状況をログファイルに記録
    log_file = project_root / "runtime" / "memory" / "session_logs.json"
    log_file.parent.mkdir(parents=True, exist_ok=True)

    session_log = {
        "session_start": session_start_time,
        "memory_count": len(forever_instructions),
        "strikes": strikes,
        "status": "memory_loaded",
    }

    # 既存ログを読み込み
    logs = []
    if log_file.exists():
        with open(log_file) as f:
            logs = [json.loads(line) for line in f]

    # 新しいログを追加
    logs.append(session_log)

    # ログを保存
    with open(log_file, "w") as f:
        for log in logs:
            f.write(json.dumps(log, ensure_ascii=False) + "\n")

except Exception as e:
    print(f"🚨 Memory loader error: {e}")
    print("🚨 CRITICAL: Memory inheritance failed!")
    sys.exit(1)
