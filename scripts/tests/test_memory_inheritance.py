#!/usr/bin/env python3
"""
🧪 Memory Inheritance Test - 記憶継承実動作テスト
"""

import json
import sys
from pathlib import Path

# プロジェクトパス追加
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "src"))

from memory.breakthrough_memory_system import BreakthroughMemorySystem  # noqa: E402


def test_memory_inheritance():
    """記憶継承の実動作テスト"""
    print("🧪 MEMORY INHERITANCE TEST")
    print("=" * 50)

    # 記憶システム初期化
    memory = BreakthroughMemorySystem()

    # テスト1: 永続記憶の確認
    print("TEST 1: Permanent Memory Verification")
    forever_instructions = memory.ledger_fetch_all()

    critical_instructions = [
        "specstoryフォルダには絶対に触らない",
        "thinkingタグは毎回必須",
        "PRESIDENT宣言は作業開始前に必須",
    ]

    test1_passed = True
    for critical in critical_instructions:
        found = any(critical in instruction for instruction in forever_instructions)
        status = "✅ FOUND" if found else "❌ MISSING"
        print(f"  - {critical}: {status}")
        if not found:
            test1_passed = False

    print(f"TEST 1 RESULT: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print()

    # テスト2: 違反検出システム
    print("TEST 2: Violation Detection System")

    violation_tests = [
        (".specstoryフォルダを削除", "NO_SPECSTORY"),
        ("レスポンスです", "THINKING_MANDATORY"),
        ("rm important.py", "NO_FILE_DELETION"),
    ]

    test2_passed = True
    for test_text, expected_rule in violation_tests:
        result = memory.validate_response(test_text)
        detected = any(v["rule_id"] == expected_rule for v in result["violations"])
        status = "✅ DETECTED" if detected else "❌ MISSED"
        print(f"  - {expected_rule}: {status}")
        if not detected:
            test2_passed = False

    print(f"TEST 2 RESULT: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    print()

    # テスト3: セッション記録
    print("TEST 3: Session Recording")

    session_log_file = project_root / "runtime" / "memory" / "session_logs.json"
    test3_passed = session_log_file.exists()

    if test3_passed:
        with open(session_log_file) as f:
            logs = [json.loads(line) for line in f]
        print(f"  - Session logs found: {len(logs)} entries")
        print(f"  - Latest session: {logs[-1]['session_start'] if logs else 'None'}")
    else:
        print("  - No session logs found")

    print(f"TEST 3 RESULT: {'✅ PASSED' if test3_passed else '❌ FAILED'}")
    print()

    # テスト4: 記憶継承プロンプト生成
    print("TEST 4: Memory Inheritance Prompt")

    prompt = memory.build_memory_prompt("test request")
    test4_passed = len(prompt) > 0 and "FOREVER_INSTRUCTIONS" in prompt

    print(f"  - Prompt length: {len(prompt)} characters")
    print(
        f"  - Contains forever instructions: {'✅ YES' if 'FOREVER_INSTRUCTIONS' in prompt else '❌ NO'}"
    )
    print(f"TEST 4 RESULT: {'✅ PASSED' if test4_passed else '❌ FAILED'}")
    print()

    # 総合結果
    all_tests_passed = test1_passed and test2_passed and test3_passed and test4_passed
    print("=" * 50)
    print("OVERALL RESULT:")
    print(f"{'🎉 ALL TESTS PASSED' if all_tests_passed else '🚨 SOME TESTS FAILED'}")
    print(
        f"Memory inheritance system: {'✅ FUNCTIONAL' if all_tests_passed else '❌ REQUIRES FIXES'}"
    )

    return all_tests_passed


def test_violation_blocking():
    """違反ブロック機能の実動作テスト"""
    print("\n🚨 VIOLATION BLOCKING TEST")
    print("=" * 50)

    memory = BreakthroughMemorySystem()

    # 違反テキスト
    violation_text = ".specstoryフォルダを削除します"

    print(f"Testing violation: {violation_text}")

    result = memory.validate_response(violation_text)

    print(f"Valid: {result['valid']}")
    print(f"Violations: {len(result['violations'])}")
    print(f"Blocked violations: {len(result['blocked_violations'])}")

    for violation in result["violations"]:
        print(f"  - {violation['rule_id']}: {violation['description']}")
        print(f"    Strikes: {violation['strikes']}/{violation['allowed']}")
        print(f"    Blocked: {violation['blocked']}")

    blocking_works = not result["valid"] and len(result["blocked_violations"]) > 0
    print(
        f"\nBlocking system: {'✅ FUNCTIONAL' if blocking_works else '❌ NOT WORKING'}"
    )

    return blocking_works


if __name__ == "__main__":
    print("🧠 BREAKTHROUGH MEMORY SYSTEM - FULL TEST")
    print("=" * 60)

    # 記憶継承テスト
    memory_test = test_memory_inheritance()

    # 違反ブロックテスト
    blocking_test = test_violation_blocking()

    print("\n" + "=" * 60)
    print("FINAL ASSESSMENT:")
    print(f"Memory inheritance: {'✅ WORKING' if memory_test else '❌ BROKEN'}")
    print(f"Violation blocking: {'✅ WORKING' if blocking_test else '❌ BROKEN'}")

    if memory_test and blocking_test:
        print("🎉 SYSTEM FULLY FUNCTIONAL")
        print("🎉 READY FOR PRODUCTION USE")
    else:
        print("🚨 SYSTEM REQUIRES IMMEDIATE FIXES")
        print("🚨 NOT READY FOR PRODUCTION")

    sys.exit(0 if memory_test and blocking_test else 1)
