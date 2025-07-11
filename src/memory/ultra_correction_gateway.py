#!/usr/bin/env python3
"""
💪 Ultra Correction Gateway - 超強力矯正ツール
===========================================

o3推奨の超強力矯正システム実装
Claude Code環境でのthinking必須・基本情報記憶強制システム
"""

import json
import logging
import re

# import redis  # Optional - only if available
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Tuple


class ViolationType(Enum):
    """違反タイプ"""

    MISSING_THINKING = "missing_thinking"
    LANGUAGE_MISMATCH = "language_mismatch"
    DYNAMIC_ROLE_FORGOTTEN = "dynamic_role_forgotten"
    BASIC_INFO_LOST = "basic_info_lost"
    INSTRUCTION_IGNORED = "instruction_ignored"


class StrikeLevel(Enum):
    """ストライクレベル"""

    GENTLE = "gentle"  # 1-2 strikes
    WARNING = "warning"  # 3-4 strikes
    BLOCKING = "blocking"  # 5+ strikes


@dataclass
class Violation:
    """違反記録"""

    timestamp: str
    violation_type: ViolationType
    snippet: str
    severity: str
    auto_fixed: bool
    strike_count: int


@dataclass
class CoreRules:
    """コアルール定義"""

    thinking_mandatory: bool = True
    language_declaration: str = "japanese"
    language_processing: str = "english"
    language_reporting: str = "japanese"
    dynamic_roles: bool = True
    fake_data_forbidden: bool = True
    pane_count: int = 4
    dashboard_config: str = "1+4"


class UltraCorrectionGateway:
    """超強力矯正ゲートウェイ"""

    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path("/Users/dd/Desktop/1_dev/coding-rule2")
        self.logger = logging.getLogger(__name__)

        # データベース設定
        self.db_path = self.project_root / "runtime" / "ultra_correction.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Redis設定（オプション）
        self.use_redis = False
        self.redis_client = None

        try:
            import redis

            self.redis_client = redis.Redis(host="localhost", port=6379, db=0)
            self.use_redis = True
        except ImportError:
            pass

        # SQLite設定
        self.init_database()

        # コアルール
        self.core_rules = CoreRules()

        # 違反パターン
        self.violation_patterns = {
            ViolationType.MISSING_THINKING: [
                r"^(?!.*<thinking>).*$",  # thinkingタグなし
            ],
            ViolationType.LANGUAGE_MISMATCH: [
                r"## 🎯.*[a-zA-Z]",  # 宣言部分に英語
                r"## ✅.*[a-zA-Z]",  # 報告部分に英語
            ],
            ViolationType.DYNAMIC_ROLE_FORGOTTEN: [
                r"static.*role",  # 静的役職言及
                r"fixed.*role",  # 固定役職言及
                r"固定.*役職",  # 固定役職言及（日本語）
            ],
            ViolationType.BASIC_INFO_LOST: [
                r"4.*screen",  # 4画面（正しくは4分割ペイン）
                r"8.*worker",  # 8人（正しくは1+4人）
            ],
        }

        # 自動修復テンプレート
        self.repair_templates = {
            ViolationType.MISSING_THINKING: """<thinking>
{original_content}
</thinking>

{original_content}""",
            ViolationType.LANGUAGE_MISMATCH: """## 🎯 これから行うこと
{japanese_declaration}

{english_processing}

## ✅ 完遂報告
{japanese_reporting}""",
        }

        # ストライクスコア
        self.strike_score = self.get_strike_score()

        # 会話要約
        self.running_summary = self.get_running_summary()

    def init_database(self):
        """データベース初期化"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 違反テーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS violations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                violation_type TEXT NOT NULL,
                snippet TEXT NOT NULL,
                severity TEXT NOT NULL,
                auto_fixed BOOLEAN NOT NULL,
                strike_count INTEGER NOT NULL
            )
        """)

        # コアルールテーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS core_rules (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # 会話要約テーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS running_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                summary TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # ストライクスコアテーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS strike_score (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                score INTEGER NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        conn.commit()
        conn.close()

    def build_prompt(self, user_prompt: str) -> List[Dict[str, str]]:
        """プロンプト構築 - 事前ルール注入"""
        rules_text = self._get_rules_text()
        dynamic_roles = self._get_dynamic_roles()
        memory = self.running_summary

        system_prefix = f"""あなたは以下のルールを厳守するAIです:

🚨 CRITICAL RULES - 絶対遵守:
{rules_text}

📋 動的ロール一覧:
{json.dumps(dynamic_roles, ensure_ascii=False, indent=2)}

💭 会話要約:
{memory}

⚠️ 違反時の処理:
- thinking必須: 毎回<thinking>タグから開始
- 言語ルール: 宣言・報告は日本語、処理は英語
- 動的役職: 「静的」「固定」は禁止
- 基本情報: 4分割ペイン、1+4人構成

現在のストライクスコア: {self.strike_score}
"""

        return [
            {"role": "system", "content": system_prefix},
            {"role": "user", "content": user_prompt},
        ]

    def validate_and_fix(self, text: str) -> Tuple[str, List[Violation]]:
        """応答検証・自動修復"""
        violations = []

        # 1. thinkingタグチェック
        if not re.search(r"<thinking>(.|\\n)+?</thinking>", text, re.DOTALL):
            violation = Violation(
                timestamp=datetime.now().isoformat(),
                violation_type=ViolationType.MISSING_THINKING,
                snippet=text[:100],
                severity="CRITICAL",
                auto_fixed=False,
                strike_count=self.strike_score + 1,
            )
            violations.append(violation)

        # 2. 言語ルールチェック
        ja_declaration = re.search(r"## 🎯.*これから行うこと", text)
        ja_reporting = re.search(r"## ✅.*完遂報告", text)

        if not (ja_declaration and ja_reporting):
            violation = Violation(
                timestamp=datetime.now().isoformat(),
                violation_type=ViolationType.LANGUAGE_MISMATCH,
                snippet=text[:100],
                severity="HIGH",
                auto_fixed=False,
                strike_count=self.strike_score + 1,
            )
            violations.append(violation)

        # 3. 動的役職チェック
        if re.search(r"(static|fixed|固定).*役職", text, re.IGNORECASE):
            violation = Violation(
                timestamp=datetime.now().isoformat(),
                violation_type=ViolationType.DYNAMIC_ROLE_FORGOTTEN,
                snippet=text[:100],
                severity="MEDIUM",
                auto_fixed=False,
                strike_count=self.strike_score + 1,
            )
            violations.append(violation)

        # 4. 基本情報チェック
        if re.search(r"8.*worker|4.*screen", text, re.IGNORECASE):
            violation = Violation(
                timestamp=datetime.now().isoformat(),
                violation_type=ViolationType.BASIC_INFO_LOST,
                snippet=text[:100],
                severity="MEDIUM",
                auto_fixed=False,
                strike_count=self.strike_score + 1,
            )
            violations.append(violation)

        # 自動修復試行
        if violations:
            fixed_text = self._auto_repair(text, violations)

            # 修復成功チェック
            if fixed_text != text:
                for violation in violations:
                    violation.auto_fixed = True
                return fixed_text, violations

        return text, violations

    def _auto_repair(self, text: str, violations: List[Violation]) -> str:
        """自動修復"""
        fixed_text = text

        for violation in violations:
            if violation.violation_type == ViolationType.MISSING_THINKING:
                # thinkingタグ追加
                if not re.search(r"<thinking>", fixed_text):
                    thinking_content = "User request processing and response planning"
                    fixed_text = (
                        f"<thinking>\n{thinking_content}\n</thinking>\n\n{fixed_text}"
                    )

            elif violation.violation_type == ViolationType.LANGUAGE_MISMATCH:
                # 言語修正（簡易版）
                if not re.search(r"## 🎯.*これから行うこと", fixed_text):
                    fixed_text = "## 🎯 これから行うこと\n" + fixed_text

        return fixed_text

    def record_violation(self, violation: Violation):
        """違反記録"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO violations (timestamp, violation_type, snippet, severity, auto_fixed, strike_count)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                violation.timestamp,
                violation.violation_type.value,
                violation.snippet,
                violation.severity,
                violation.auto_fixed,
                violation.strike_count,
            ),
        )

        conn.commit()
        conn.close()

        # ストライクスコア更新
        self.strike_score = violation.strike_count
        self._update_strike_score()

    def get_strike_level(self) -> StrikeLevel:
        """ストライクレベル取得"""
        if self.strike_score >= 5:
            return StrikeLevel.BLOCKING
        elif self.strike_score >= 3:
            return StrikeLevel.WARNING
        else:
            return StrikeLevel.GENTLE

    def should_block_response(self) -> bool:
        """応答ブロック判定"""
        return self.get_strike_level() == StrikeLevel.BLOCKING

    def get_strike_score(self) -> int:
        """ストライクスコア取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT score FROM strike_score ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()

        conn.close()

        return result[0] if result else 0

    def _update_strike_score(self):
        """ストライクスコア更新"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO strike_score (score, updated_at)
            VALUES (?, ?)
        """,
            (self.strike_score, datetime.now().isoformat()),
        )

        conn.commit()
        conn.close()

    def get_running_summary(self) -> str:
        """会話要約取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT summary FROM running_summary ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()

        conn.close()

        return result[0] if result else "セッション開始"

    def update_running_summary(self, new_summary: str):
        """会話要約更新"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO running_summary (summary, updated_at)
            VALUES (?, ?)
        """,
            (new_summary, datetime.now().isoformat()),
        )

        conn.commit()
        conn.close()

        self.running_summary = new_summary

    def _get_rules_text(self) -> str:
        """ルールテキスト取得"""
        return """
• 毎回thinkingを必須にする（絶対）
• 処理中は英語を使用する
• 宣言は日本語（## 🎯 これから行うこと）
• 報告は日本語（## ✅ 完遂報告）
• 役職は動的システム（静的ではない）
• 4分割ペインはclaude code 4画面同時起動
• ダッシュボードは1+4人構成（プレジデント＋4人）
• 偽装データは絶対禁止（戦争級重罪）
"""

    def _get_dynamic_roles(self) -> Dict[str, str]:
        """動的役職取得"""
        return {
            "PRESIDENT": "戦略統括・意思決定",
            "COORDINATOR": "タスク調整・進捗管理",
            "ANALYST": "要件分析・仕様策定",
            "ARCHITECT": "システム設計・構造設計",
            "ENGINEER": "システム実装・技術検証",
        }

    def get_violation_history(self) -> List[Violation]:
        """違反履歴取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT timestamp, violation_type, snippet, severity, auto_fixed, strike_count
            FROM violations
            ORDER BY timestamp DESC
            LIMIT 50
        """)

        results = cursor.fetchall()
        conn.close()

        violations = []
        for row in results:
            violation = Violation(
                timestamp=row[0],
                violation_type=ViolationType(row[1]),
                snippet=row[2],
                severity=row[3],
                auto_fixed=bool(row[4]),
                strike_count=row[5],
            )
            violations.append(violation)

        return violations

    def generate_status_report(self) -> Dict[str, Any]:
        """ステータスレポート生成"""
        violations = self.get_violation_history()

        return {
            "strike_score": self.strike_score,
            "strike_level": self.get_strike_level().value,
            "should_block": self.should_block_response(),
            "total_violations": len(violations),
            "recent_violations": [asdict(v) for v in violations[:5]],
            "running_summary": self.running_summary,
            "core_rules": asdict(self.core_rules),
            "last_updated": datetime.now().isoformat(),
        }

    def reset_strikes(self):
        """ストライクリセット"""
        self.strike_score = 0
        self._update_strike_score()
        print("✅ Strike score reset to 0")


def main():
    """メイン実行"""
    gateway = UltraCorrectionGateway()

    print("💪 Ultra Correction Gateway - 超強力矯正ツール")
    print("=" * 60)

    # ステータスレポート
    status = gateway.generate_status_report()
    print(f"Current strike score: {status['strike_score']}")
    print(f"Strike level: {status['strike_level']}")
    print(f"Should block: {status['should_block']}")
    print(f"Total violations: {status['total_violations']}")

    # テスト用違反記録
    test_text = "This is a test response without thinking tags"
    fixed_text, violations = gateway.validate_and_fix(test_text)

    print("\nTest validation:")
    print(f"Original: {test_text}")
    print(f"Fixed: {fixed_text}")
    print(f"Violations: {len(violations)}")

    for violation in violations:
        gateway.record_violation(violation)
        print(f"  - {violation.violation_type.value}: {violation.severity}")

    print("\n✅ Ultra Correction Gateway test completed")


if __name__ == "__main__":
    main()
