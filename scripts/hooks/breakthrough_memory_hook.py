#!/usr/bin/env python3
"""
🧠 Breakthrough Memory Hook - 記憶継承強制実行
"""

import sys
from pathlib import Path

# プロジェクトパス追加
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root / "src"))

try:
    from memory.breakthrough_memory_system import BreakthroughMemorySystem

    # 記憶システム初期化
    memory = BreakthroughMemorySystem()

    # 永続記憶の強制表示
    print("🧠 BREAKTHROUGH MEMORY ACTIVE")
    print("=" * 40)

    forever_instructions = memory.ledger_fetch_all()
    for i, instruction in enumerate(forever_instructions[:5], 1):
        print(f"{i}. {instruction}")

    print("=" * 40)
    print("⚠️ THESE INSTRUCTIONS ARE PERMANENT")

except Exception as e:
    print(f"🚨 Memory system error: {e}")
    print("🚨 CRITICAL: Memory inheritance failed!")
