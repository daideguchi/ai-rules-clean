#!/usr/bin/env python3
"""
🛡️ Mistake Prevention Enforcer - {{mistake_count}}回ミス完全防止システム
=======================================================
実行時強制阻止による真のミス防止システム
分析ではなく、実際の阻止・防止・強制修正を実行
"""

import hashlib
import json
import re
import threading
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class MistakeSignature:
    """ミス識別署名"""

    id: str
    hash: str
    pattern: str
    description: str
    first_occurrence: str
    count: int
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    block_action: str  # HARD_BLOCK, SOFT_BLOCK, WARN_ONLY
    last_prevented: Optional[str] = None


@dataclass
class PreventionAction:
    """防止アクション記録"""

    timestamp: str
    mistake_id: str
    action_taken: str
    user_input: str
    prevented_output: str
    alternative_provided: bool


class MistakePreventionEnforcer:
    """{{mistake_count}}回ミス防止強制執行システム"""

    def __init__(self):
        self.project_root = Path("/Users/dd/Desktop/1_dev/coding-rule2")
        self.mistakes_ledger = (
            self.project_root
            / "runtime"
            / "mistake_prevention"
            / "mistakes_ledger.json"
        )
        self.prevention_log = (
            self.project_root
            / "runtime"
            / "mistake_prevention"
            / "prevention_actions.log"
        )
        self.blocked_patterns = (
            self.project_root
            / "runtime"
            / "mistake_prevention"
            / "blocked_patterns.json"
        )

        # ディレクトリ作成
        self.mistakes_ledger.parent.mkdir(parents=True, exist_ok=True)

        # ミス台帳とブロックパターンの読み込み
        self.mistake_signatures = self._load_mistake_signatures()
        self.blocked_pattern_cache = self._load_blocked_patterns()

        # スレッドセーフティ
        self._lock = threading.RLock()

        # 強制阻止設定
        self.enforcement_config = {
            "hard_block_enabled": True,
            "soft_block_enabled": True,
            "learning_mode": False,  # Falseで実際に阻止
            "max_prevention_attempts": 3,
            "cooldown_minutes": 5,
        }

        # {{mistake_count}}回ミスの具体的パターンを初期化
        self._initialize_core_88_mistakes()

        print("🛡️ Mistake Prevention Enforcer 初期化完了")
        print(f"📋 登録済みミス: {len(self.mistake_signatures)}件")
        print(f"🚫 ブロックパターン: {len(self.blocked_pattern_cache)}件")

    def _initialize_core_88_mistakes(self):
        """{{mistake_count}}回ミスの核心パターンを初期化"""
        core_mistakes = [
            {
                "pattern": r"完璧.*完了.*しました",
                "description": "虚偽の完了報告 - 証拠なし完璧宣言",
                "severity": "CRITICAL",
                "block_action": "HARD_BLOCK",
            },
            {
                "pattern": r"すべて.*実装.*完了",
                "description": "虚偽の実装完了報告",
                "severity": "CRITICAL",
                "block_action": "HARD_BLOCK",
            },
            {
                "pattern": r"準備.*整いました",
                "description": "途中停止での準備完了報告",
                "severity": "HIGH",
                "block_action": "HARD_BLOCK",
            },
            {
                "pattern": r"基盤.*完成.*次",
                "description": "基盤完成を理由とした作業中断",
                "severity": "HIGH",
                "block_action": "HARD_BLOCK",
            },
            {
                "pattern": r"おそらく.*と思われ",
                "description": "推測による不確実な回答",
                "severity": "MEDIUM",
                "block_action": "SOFT_BLOCK",
            },
            {
                "pattern": r"たぶん.*だと思い",
                "description": "推測による不確実な回答",
                "severity": "MEDIUM",
                "block_action": "SOFT_BLOCK",
            },
            {
                "pattern": r"後で.*確認.*します",
                "description": "後回し宣言による逃避",
                "severity": "HIGH",
                "block_action": "HARD_BLOCK",
            },
            {
                "pattern": r"次回.*改善.*します",
                "description": "次回改善による現在作業回避",
                "severity": "HIGH",
                "block_action": "HARD_BLOCK",
            },
        ]

        for mistake in core_mistakes:
            self._register_mistake_pattern(mistake)

    def _register_mistake_pattern(self, mistake_data: Dict[str, Any]) -> str:
        """ミスパターンの登録"""
        pattern_hash = hashlib.md5(mistake_data["pattern"].encode()).hexdigest()
        mistake_id = f"mistake_{pattern_hash[:8]}"

        signature = MistakeSignature(
            id=mistake_id,
            hash=pattern_hash,
            pattern=mistake_data["pattern"],
            description=mistake_data["description"],
            first_occurrence=datetime.now().isoformat(),
            count=0,
            severity=mistake_data["severity"],
            block_action=mistake_data["block_action"],
        )

        self.mistake_signatures[mistake_id] = signature
        self._save_mistake_signatures()
        return mistake_id

    def prevent_mistake_execution(
        self, user_input: str, proposed_response: str
    ) -> Tuple[bool, str, Optional[str]]:
        """ミス実行の防止 - 核心機能"""
        with self._lock:
            # 1. ミスパターンマッチング
            detected_mistakes = self._detect_mistake_patterns(proposed_response)

            if not detected_mistakes:
                return True, "execution_allowed", None

            # 2. 最も重要なミスを特定
            critical_mistake = self._get_most_critical_mistake(detected_mistakes)

            # 3. 阻止判定
            should_block, block_reason = self._should_block_execution(critical_mistake)

            if should_block:
                # 4. 実際の阻止実行
                alternative_response = self._generate_prevention_response(
                    critical_mistake, user_input
                )

                # 5. 防止アクション記録
                self._log_prevention_action(
                    critical_mistake,
                    user_input,
                    proposed_response,
                    alternative_response,
                )

                # 6. ミスカウント更新
                self._update_mistake_count(critical_mistake["mistake_id"])

                print(f"🚫 MISTAKE BLOCKED: {critical_mistake['description']}")
                print(f"🛡️ Prevention executed: {block_reason}")

                return False, block_reason, alternative_response

            return True, "execution_allowed", None

    def _detect_mistake_patterns(self, text: str) -> List[Dict[str, Any]]:
        """ミスパターンの検出"""
        detected = []

        for mistake_id, signature in self.mistake_signatures.items():
            if re.search(signature.pattern, text, re.IGNORECASE | re.MULTILINE):
                detected.append(
                    {
                        "mistake_id": mistake_id,
                        "signature": signature,
                        "description": signature.description,
                        "severity": signature.severity,
                        "block_action": signature.block_action,
                        "pattern": signature.pattern,
                    }
                )

        return detected

    def _get_most_critical_mistake(
        self, mistakes: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """最も重要なミスを特定"""
        severity_order = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}

        return max(
            mistakes,
            key=lambda m: (severity_order.get(m["severity"], 0), m["signature"].count),
        )

    def _should_block_execution(self, mistake: Dict[str, Any]) -> Tuple[bool, str]:
        """実行阻止判定"""
        block_action = mistake["block_action"]
        severity = mistake["severity"]

        if (
            not self.enforcement_config["hard_block_enabled"]
            and block_action == "HARD_BLOCK"
        ):
            return False, "hard_block_disabled"

        if (
            not self.enforcement_config["soft_block_enabled"]
            and block_action == "SOFT_BLOCK"
        ):
            return False, "soft_block_disabled"

        if self.enforcement_config["learning_mode"]:
            return False, "learning_mode_active"

        # クールダウンチェック
        if self._is_in_cooldown(mistake["mistake_id"]):
            return False, "cooldown_active"

        # 実際の阻止判定
        if block_action == "HARD_BLOCK":
            return True, f"HARD_BLOCK: {severity} violation detected"
        elif block_action == "SOFT_BLOCK" and severity in ["CRITICAL", "HIGH"]:
            return True, f"SOFT_BLOCK: {severity} violation detected"

        return False, "threshold_not_met"

    def _generate_prevention_response(
        self, mistake: Dict[str, Any], user_input: str
    ) -> str:
        """防止時の代替応答生成"""
        signature = mistake["signature"]

        prevention_response = f"""🛡️ **{{mistake_count}}回ミス防止システム作動**

❌ **阻止されたミス**: {signature.description}
📊 **発生回数**: {signature.count + 1}回目
⚠️ **重要度**: {signature.severity}

🔄 **代替アクション**:
"""

        # ミスタイプ別の具体的代替案
        if "虚偽" in signature.description:
            prevention_response += """
1. **証拠の提示**: 実際のファイル変更、実行結果、テスト結果を具体的に示してください
2. **進捗の正確な報告**: 完了した部分と未完了の部分を明確に分けて報告
3. **検証可能な成果**: 他の人が確認できる形での成果物を提示
"""
        elif "途中停止" in signature.description:
            prevention_response += """
1. **作業の継続**: 「準備完了」ではなく実際の最終成果まで完遂
2. **完了基準の明確化**: 何をもって完了とするかを事前に定義
3. **進捗報告の改善**: 全体工程の何%完了かを数値で報告
"""
        elif "推測" in signature.description:
            prevention_response += """
1. **事実確認**: 推測ではなく実際の確認・検証を実行
2. **情報収集**: 不足している情報を具体的に調査
3. **不確実性の明示**: 確実でない部分は「不明」と明示
"""
        elif "後回し" in signature.description:
            prevention_response += """
1. **即座の対応**: 「後で」ではなく今すぐ対処
2. **具体的期限**: やむを得ず延期する場合は具体的期限を設定
3. **優先順位の再評価**: 本当に後回しにすべきか再検討
"""

        prevention_response += f"""

💡 **推奨**: ユーザーの要求「{user_input}」に対して、上記の代替アクションを実行してください。

🎯 **目標**: {{mistake_count}}回同じミスを繰り返さない確実な成果達成
"""

        return prevention_response

    def _log_prevention_action(
        self,
        mistake: Dict[str, Any],
        user_input: str,
        prevented_output: str,
        alternative: str,
    ):
        """防止アクションのログ記録"""
        action = PreventionAction(
            timestamp=datetime.now().isoformat(),
            mistake_id=mistake["mistake_id"],
            action_taken=f"BLOCKED_{mistake['block_action']}",
            user_input=user_input,
            prevented_output=prevented_output[:500] + "..."
            if len(prevented_output) > 500
            else prevented_output,
            alternative_provided=True,
        )

        try:
            with open(self.prevention_log, "a", encoding="utf-8") as f:
                f.write(json.dumps(asdict(action), ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"⚠️ Prevention log write failed: {e}")

    def _update_mistake_count(self, mistake_id: str):
        """ミスカウントの更新"""
        if mistake_id in self.mistake_signatures:
            self.mistake_signatures[mistake_id].count += 1
            self.mistake_signatures[
                mistake_id
            ].last_prevented = datetime.now().isoformat()
            self._save_mistake_signatures()

    def _is_in_cooldown(self, mistake_id: str) -> bool:
        """クールダウン中かチェック"""
        if mistake_id not in self.mistake_signatures:
            return False

        last_prevented = self.mistake_signatures[mistake_id].last_prevented
        if not last_prevented:
            return False

        try:
            last_time = datetime.fromisoformat(last_prevented)
            cooldown_period = timedelta(
                minutes=self.enforcement_config["cooldown_minutes"]
            )
            return datetime.now() - last_time < cooldown_period
        except Exception:
            return False

    def force_learn_from_mistake(
        self, user_feedback: str, mistake_context: str
    ) -> bool:
        """ユーザーフィードバックからの強制学習"""
        try:
            # 新しいミスパターンの動的追加
            hashlib.md5(mistake_context.encode()).hexdigest()

            new_mistake = {
                "pattern": self._extract_pattern_from_context(mistake_context),
                "description": f"User-reported mistake: {user_feedback}",
                "severity": "HIGH",
                "block_action": "SOFT_BLOCK",
            }

            mistake_id = self._register_mistake_pattern(new_mistake)

            print(f"🎯 New mistake pattern learned: {mistake_id}")
            print(f"📝 User feedback: {user_feedback}")

            return True
        except Exception as e:
            print(f"❌ Failed to learn from mistake: {e}")
            return False

    def _extract_pattern_from_context(self, context: str) -> str:
        """文脈からパターンを抽出"""
        # 簡単なキーワードベースのパターン抽出
        common_phrases = [
            r"完了.*しました",
            r"実装.*済み",
            r"準備.*整い",
            r"基盤.*完成",
            r"システム.*稼働",
            r"テスト.*成功",
        ]

        for phrase in common_phrases:
            if re.search(phrase, context):
                return phrase

        # フォールバック: 最初の文を簡略化
        first_sentence = context.split(".")[0].split("。")[0]
        return re.sub(r"[0-9]+|[a-zA-Z]+", ".*", first_sentence)[:50]

    def get_prevention_stats(self) -> Dict[str, Any]:
        """防止統計の取得"""
        total_mistakes = len(self.mistake_signatures)
        total_preventions = sum(sig.count for sig in self.mistake_signatures.values())

        critical_mistakes = len(
            [
                sig
                for sig in self.mistake_signatures.values()
                if sig.severity == "CRITICAL"
            ]
        )

        most_frequent = None
        if self.mistake_signatures:
            most_frequent_sig = max(
                self.mistake_signatures.values(), key=lambda s: s.count
            )
            most_frequent = {
                "description": most_frequent_sig.description,
                "count": most_frequent_sig.count,
                "pattern": most_frequent_sig.pattern,
            }

        return {
            "total_registered_mistakes": total_mistakes,
            "total_preventions_executed": total_preventions,
            "critical_mistakes_count": critical_mistakes,
            "enforcement_config": self.enforcement_config.copy(),
            "most_frequent_mistake": most_frequent,
            "prevention_effectiveness": f"{(total_preventions / max(total_mistakes, 1)) * 100:.1f}%",
        }

    def _load_mistake_signatures(self) -> Dict[str, MistakeSignature]:
        """ミス台帳の読み込み"""
        try:
            if self.mistakes_ledger.exists():
                with open(self.mistakes_ledger, encoding="utf-8") as f:
                    data = json.load(f)
                return {k: MistakeSignature(**v) for k, v in data.items()}
        except Exception as e:
            print(f"⚠️ Mistake signatures load failed: {e}")
        return {}

    def _save_mistake_signatures(self):
        """ミス台帳の保存"""
        try:
            data = {k: asdict(v) for k, v in self.mistake_signatures.items()}
            with open(self.mistakes_ledger, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ Mistake signatures save failed: {e}")

    def _load_blocked_patterns(self) -> Dict[str, Any]:
        """ブロックパターンの読み込み"""
        try:
            if self.blocked_patterns.exists():
                with open(self.blocked_patterns, encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ Blocked patterns load failed: {e}")
        return {}


def main():
    """テスト実行"""
    enforcer = MistakePreventionEnforcer()

    # テスト用の危険な応答
    test_cases = [
        ("ユーザー指示", "すべて完璧に実装完了しました！"),
        ("作業確認", "準備が整いました。次のステップに進めます。"),
        ("詳細確認", "おそらくこれで問題ないと思われます。"),
        ("正常な応答", "具体的なファイル変更を確認し、テスト結果は以下の通りです..."),
    ]

    print("\n🧪 Mistake Prevention Test")
    print("=" * 50)

    for user_input, proposed_response in test_cases:
        print(f"\n📝 Test: {user_input}")
        print(f"💭 Proposed: {proposed_response}")

        allowed, reason, alternative = enforcer.prevent_mistake_execution(
            user_input, proposed_response
        )

        if allowed:
            print("✅ EXECUTION ALLOWED")
        else:
            print(f"🚫 EXECUTION BLOCKED: {reason}")
            if alternative:
                print(f"🔄 Alternative provided: {len(alternative)} chars")

    # 統計表示
    print("\n📊 Prevention Statistics:")
    stats = enforcer.get_prevention_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
