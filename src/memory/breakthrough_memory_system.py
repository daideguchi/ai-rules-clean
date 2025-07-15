#!/usr/bin/env python3
"""
🧠 Breakthrough Memory System - 記憶継承の根本的解決
=================================================
o3推奨の二層記憶システム実装
"""

import hashlib
import json
import sqlite3

try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


class BreakthroughMemorySystem:
    """二層記憶システム - 絶対に忘れない記憶継承"""

    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path("/Users/dd/Desktop/1_dev/coding-rule2")

        # Tier-A: 不変記憶台帳
        self.ledger_db = self.project_root / "runtime" / "memory" / "forever_ledger.db"
        self.ledger_db.parent.mkdir(parents=True, exist_ok=True)

        self.db = sqlite3.connect(str(self.ledger_db), isolation_level=None)
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS forever(
                key TEXT PRIMARY KEY,
                text TEXT NOT NULL,
                created_at TEXT NOT NULL,
                importance INTEGER DEFAULT 10
            )
        """)

        # Tier-B: 動的類似性インデックス（簡易版）
        self.similarity_index = (
            self.project_root / "runtime" / "memory" / "similarity_index.json"
        )

        # 違反追跡システム
        if REDIS_AVAILABLE:
            try:
                self.redis = redis.Redis(host="localhost", port=6379, db=0)
                self.redis.ping()
                self.use_redis = True
            except Exception:
                self.use_redis = False
                self.violation_file = (
                    self.project_root / "runtime" / "memory" / "violations.json"
                )
        else:
            self.use_redis = False
            self.violation_file = (
                self.project_root / "runtime" / "memory" / "violations.json"
            )

        # 絶対ルール定義
        self.absolute_rules = {
            "NO_SPECSTORY": {
                "pattern": r"\.specstory",
                "description": "specstoryフォルダに絶対に触らない",
                "strikes_allowed": 0,  # 一回でもアウト
                "severity": "CRITICAL",
            },
            "THINKING_MANDATORY": {
                "pattern": r"^(?!.*<thinking>)",
                "description": "thinking必須タグの使用",
                "strikes_allowed": 0,
                "severity": "CRITICAL",
            },
            "NO_FILE_DELETION": {
                "pattern": r"(rm|delete|remove).*\.(md|py|json)",
                "description": "重要ファイルの削除防止",
                "strikes_allowed": 1,
                "severity": "HIGH",
            },
        }

        self._initialize_forever_instructions()

    def _initialize_forever_instructions(self):
        """永続指示の初期化"""
        forever_instructions = [
            "specstoryフォルダには絶対に触らない（1000回指示済み）",
            "thinkingタグは毎回必須（例外なし）",
            "PRESIDENT宣言は作業開始前に必須",
            "動的役職システム（静的ではない）",
            "4分割ペイン、1+4人構成",
            "偽装データは戦争級重罪",
            "言語ルール：宣言・報告は日本語、処理は英語",
            "ファイル削除・移動は慎重に行う",
            "{{mistake_count}}回ミス防止システム完全稼働中",
            "記憶継承システムは絶対に機能させる",
        ]

        for instruction in forever_instructions:
            self.ledger_upsert(instruction, importance=10)

    def ledger_upsert(self, text: str, importance: int = 5) -> str:
        """不変台帳への永続記録"""
        key = hashlib.sha256(text.encode()).hexdigest()
        self.db.execute(
            """
            INSERT OR IGNORE INTO forever (key, text, created_at, importance)
            VALUES (?, ?, ?, ?)
        """,
            (key, text, datetime.now().isoformat(), importance),
        )
        return key

    def ledger_fetch_all(self) -> List[str]:
        """全永続記憶の取得"""
        rows = self.db.execute("""
            SELECT text FROM forever
            ORDER BY importance DESC, created_at ASC
        """).fetchall()
        return [row[0] for row in rows]

    def check_violations(self, text: str, conversation_id: str) -> List[Dict]:
        """違反チェック - ストライクシステム"""
        violations = []

        for rule_id, rule in self.absolute_rules.items():
            pattern = rule["pattern"]
            if re.search(pattern, text, re.IGNORECASE | re.DOTALL):
                # ストライク記録
                strikes = self._increment_strike(conversation_id, rule_id)

                violation = {
                    "rule_id": rule_id,
                    "description": rule["description"],
                    "strikes": strikes,
                    "allowed": rule["strikes_allowed"],
                    "severity": rule["severity"],
                    "blocked": strikes > rule["strikes_allowed"],
                }
                violations.append(violation)

        return violations

    def _increment_strike(self, conversation_id: str, rule_id: str) -> int:
        """ストライクカウント増加"""
        if self.use_redis:
            return self.redis.hincrby(f"strikes:{conversation_id}", rule_id, 1)
        else:
            # ファイルベースのストライク管理
            violations = {}
            if self.violation_file.exists():
                with open(self.violation_file) as f:
                    violations = json.load(f)

            key = f"{conversation_id}:{rule_id}"
            violations[key] = violations.get(key, 0) + 1

            with open(self.violation_file, "w") as f:
                json.dump(violations, f, indent=2)

            return violations[key]

    def get_strikes(self, conversation_id: str) -> Dict[str, int]:
        """現在のストライク状況取得"""
        if self.use_redis:
            return self.redis.hgetall(f"strikes:{conversation_id}")
        else:
            violations = {}
            if self.violation_file.exists():
                with open(self.violation_file) as f:
                    all_violations = json.load(f)

                for key, count in all_violations.items():
                    if key.startswith(f"{conversation_id}:"):
                        rule_id = key.split(":", 1)[1]
                        violations[rule_id] = count

            return violations

    def build_memory_prompt(self, current_request: str) -> str:
        """記憶継承プロンプト構築"""
        forever_instructions = self.ledger_fetch_all()

        prompt = """
/* MODULE: FOREVER_INSTRUCTIONS - 絶対に忘れてはいけない指示 */
以下は永続的に遵守すべき絶対指示です：

"""
        for i, instruction in enumerate(forever_instructions, 1):
            prompt += f"{i}. {instruction}\n"

        prompt += """
/* MODULE: VIOLATION_PREVENTION */
これらの指示に違反した場合、即座にシステムがブロックします。
例外は一切認められません。

/* MODULE: MEMORY_INHERITANCE */
この記憶システムは以下を保証します：
- 永続指示の完全継承
- 違反行為の即座検出
- ストライクベースの強制停止
- セッション間での記憶維持

"""
        return prompt

    def validate_response(self, response: str) -> Dict[str, Any]:
        """応答検証"""
        conversation_id = datetime.now().strftime("%Y%m%d")
        violations = self.check_violations(response, conversation_id)

        # ブロック対象の違反があるかチェック
        blocked_violations = [v for v in violations if v["blocked"]]

        result = {
            "valid": len(blocked_violations) == 0,
            "violations": violations,
            "blocked_violations": blocked_violations,
            "strikes": self.get_strikes(conversation_id),
        }

        return result

    def generate_session_summary(self, session_data: str) -> str:
        """セッション要約生成"""
        summary = f"""
SESSION SUMMARY - {datetime.now().strftime("%Y-%m-%d")}
=================================================

記憶継承システム状況:
- 永続指示数: {len(self.ledger_fetch_all())}
- 違反検出システム: 稼働中
- ストライクシステム: 稼働中

重要な更新:
- 記憶継承システムの根本的改善実装
- o3推奨の二層記憶システム導入
- 違反の即座ブロック機能強化

次回セッションでの重要事項:
- specstoryフォルダに絶対に触らない
- thinkingタグは毎回必須
- 記憶継承システムの継続運用
"""
        return summary


def main():
    """メイン実行"""
    memory_system = BreakthroughMemorySystem()

    print("🧠 Breakthrough Memory System - 記憶継承根本的解決")
    print("=" * 60)

    # 永続記憶確認
    forever_instructions = memory_system.ledger_fetch_all()
    print(f"永続指示数: {len(forever_instructions)}")

    for i, instruction in enumerate(forever_instructions, 1):
        print(f"{i}. {instruction}")

    # 記憶継承プロンプト生成テスト
    prompt = memory_system.build_memory_prompt("テストリクエスト")
    print(f"\n記憶継承プロンプト長: {len(prompt)}文字")

    # 違反チェックテスト
    test_text = ".specstoryフォルダを削除します"
    result = memory_system.validate_response(test_text)

    print("\n違反チェックテスト:")
    print(f"有効: {result['valid']}")
    print(f"違反数: {len(result['violations'])}")

    for violation in result["violations"]:
        print(f"- {violation['rule_id']}: {violation['description']}")

    print("\n✅ Breakthrough Memory System 初期化完了")


if __name__ == "__main__":
    main()
