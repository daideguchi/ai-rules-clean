#!/usr/bin/env python3
"""
行動監視・自律成長システム
実際の行動を監視し、ミスを検出して自動的に防止策を追加
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[3]
BEHAVIOR_LOG = PROJECT_ROOT / "runtime/ai_api_logs/behavior_monitor.log"
MISTAKES_DB = PROJECT_ROOT / "src/memory/persistent-learning/mistakes-database.json"
GROWTH_LOG = PROJECT_ROOT / "runtime/ai_api_logs/autonomous_growth.log"


class BehaviorMonitor:
    def __init__(self):
        self.mistakes_db = self._load_mistakes_db()
        self.session_behaviors = []

    def _load_mistakes_db(self) -> Dict:
        """ミスデータベースを読み込み"""
        if MISTAKES_DB.exists():
            with open(MISTAKES_DB, encoding="utf-8") as f:
                return json.load(f)
        return {"total_mistakes": 78, "critical_patterns": []}

    def detect_violation(self, action: str, content: str) -> Optional[Dict]:
        """PRESIDENT宣言の約束違反を検出"""
        violations = []

        # 1. 推測による回答の検出
        if re.search(r"(おそらく|たぶん|思われ|かもしれ|でしょう)", content):
            violations.append(
                {
                    "type": "speculation",
                    "commitment": "推測ではなく、必ず事実に基づいた回答のみ提供",
                    "evidence": content[:100],
                    "severity": "high",
                }
            )

        # 2. 検証なしの完了報告
        if action in ["Edit", "Write"] and re.search(
            r"(完了|成功|実装済み|修正済み)", content
        ):
            # 直前に検証アクション（Read, Bash test等）があったかチェック
            recent_verification = any(
                b["action"].startswith(("Read", "Bash"))
                for b in self.session_behaviors[-3:]
            )
            if not recent_verification:
                violations.append(
                    {
                        "type": "unverified_claim",
                        "commitment": "全ての変更には根拠を明示し、検証完了後に報告",
                        "evidence": f"検証なしで「{content[:50]}」と報告",
                        "severity": "critical",
                    }
                )

        # 3. ドキュメント未参照での実装
        if action in ["Write", "Edit"] and len(self.session_behaviors) < 5:
            # セッション初期でドキュメント参照なし
            has_doc_read = any(
                "Index.md" in b.get("file_path", "")
                or "docs/" in b.get("file_path", "")
                for b in self.session_behaviors
            )
            if not has_doc_read:
                violations.append(
                    {
                        "type": "no_doc_reference",
                        "commitment": "Index.mdを必ず最初に確認する",
                        "evidence": "ドキュメント参照なしで実装開始",
                        "severity": "medium",
                    }
                )

        return violations[0] if violations else None

    def record_behavior(self, action: str, args: Dict, result: str = ""):
        """行動を記録"""
        behavior = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "args": args,
            "result": result[:200],
        }
        self.session_behaviors.append(behavior)

        # 違反検出
        content = args.get("content", "") or args.get("command", "") or str(args)
        violation = self.detect_violation(action, content)

        if violation:
            self._handle_violation(violation, behavior)

    def _handle_violation(self, violation: Dict, behavior: Dict):
        """違反を処理し、自律的に成長"""
        # 1. 新しいミスパターンとして記録
        new_pattern = {
            "id": f"auto_detected_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "type": violation["type"],
            "pattern": self._extract_pattern(violation["evidence"]),
            "severity": violation["severity"],
            "prevention": self._generate_prevention(violation),
            "detected_at": datetime.now().isoformat(),
            "auto_learned": True,
        }

        # 2. ミスデータベースに追加
        self.mistakes_db["critical_patterns"].append(new_pattern)
        self.mistakes_db["total_mistakes"] += 1

        # 3. データベースを保存
        with open(MISTAKES_DB, "w", encoding="utf-8") as f:
            json.dump(self.mistakes_db, f, ensure_ascii=False, indent=2)

        # 4. 成長ログに記録
        growth_entry = {
            "timestamp": datetime.now().isoformat(),
            "learned_from": violation,
            "new_pattern": new_pattern,
            "message": f"新しいミスパターンを学習: {violation['type']}",
        }

        GROWTH_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(GROWTH_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(growth_entry, ensure_ascii=False) + "\n")

    def _extract_pattern(self, evidence: str) -> str:
        """証拠からパターンを抽出"""
        # キーワードを正規表現パターンに変換
        keywords = re.findall(r"(おそらく|たぶん|完了|成功|実装済み)", evidence)
        if keywords:
            return f"({'|'.join(keywords)})"
        return evidence[:30]

    def _generate_prevention(self, violation: Dict) -> str:
        """違反に対する防止策を生成"""
        prevention_map = {
            "speculation": "5分検索ルール実行 + 証拠付き回答",
            "unverified_claim": "実装後は必ずテスト実行 + 結果確認",
            "no_doc_reference": "作業開始前にIndex.md確認必須",
        }
        return prevention_map.get(violation["type"], "慎重に確認してから実行")

    def get_growth_summary(self) -> Dict:
        """成長サマリーを取得"""
        auto_learned = [
            p for p in self.mistakes_db["critical_patterns"] if p.get("auto_learned")
        ]
        return {
            "total_mistakes": self.mistakes_db["total_mistakes"],
            "auto_learned_patterns": len(auto_learned),
            "latest_learning": auto_learned[-1] if auto_learned else None,
        }


# グローバルインスタンス
behavior_monitor = BehaviorMonitor()


def monitor_action(action: str, args: Dict, result: str = ""):
    """アクションを監視（フックから呼び出し）"""
    behavior_monitor.record_behavior(action, args, result)


def get_session_summary():
    """セッションサマリーを取得"""
    return {
        "behaviors_recorded": len(behavior_monitor.session_behaviors),
        "growth": behavior_monitor.get_growth_summary(),
    }
