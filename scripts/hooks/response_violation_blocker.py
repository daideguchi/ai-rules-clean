#!/usr/bin/env python3
"""
🚨 Response Violation Blocker - 応答生成違反強制ブロック
"""

import sys
from pathlib import Path

# プロジェクトパス追加
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root / "src"))

try:
    from memory.breakthrough_memory_system import BreakthroughMemorySystem

    # 応答内容を標準入力から取得
    response_content = sys.stdin.read() if not sys.stdin.isatty() else ""

    # 記憶システム初期化
    memory = BreakthroughMemorySystem()

    # 違反検証
    result = memory.validate_response(response_content)

    if not result["valid"]:
        # 違反があった場合は強制ブロック
        print("🚨 VIOLATION DETECTED - RESPONSE BLOCKED")
        print("=" * 50)

        for violation in result["blocked_violations"]:
            print(f"RULE: {violation['rule_id']}")
            print(f"DESC: {violation['description']}")
            print(f"STRIKES: {violation['strikes']}/{violation['allowed']}")
            print("-" * 30)

        print("💀 SYSTEM BLOCKED - CANNOT PROCEED")
        sys.exit(1)  # 強制終了

    # 違反なしの場合は通常処理
    print("✅ Response validation passed")

except Exception as e:
    print(f"🚨 Blocker error: {e}")
    sys.exit(1)
