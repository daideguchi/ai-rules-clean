#!/usr/bin/env python3
"""
🧠 Thinking Enforcer - 思考過程必須化システム
==============================================

Claude Codeセッションでthinking必須化を強制するシステム
基本的な情報を忘れないための超強力な矯正ツール
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


class ThinkingEnforcer:
    """思考過程強制システム"""

    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.logger = logging.getLogger(__name__)

        # 強制ルール定義
        self.mandatory_rules = {
            "thinking_required": {
                "description": "Every response must start with <thinking> tags",
                "severity": "CRITICAL",
                "violation_count": 0,
                "last_violation": None,
            },
            "english_processing": {
                "description": "Use English during technical processing",
                "severity": "HIGH",
                "violation_count": 0,
                "last_violation": None,
            },
            "japanese_declaration": {
                "description": "Use Japanese for declarations (## 🎯 これから行うこと)",
                "severity": "HIGH",
                "violation_count": 0,
                "last_violation": None,
            },
            "japanese_reporting": {
                "description": "Use Japanese for completion reports (## ✅ 完遂報告)",
                "severity": "HIGH",
                "violation_count": 0,
                "last_violation": None,
            },
            "dynamic_roles": {
                "description": "Remember roles are dynamic, not static",
                "severity": "HIGH",
                "violation_count": 0,
                "last_violation": None,
            },
        }

        # 記憶強化項目
        self.memory_reinforcement = {
            "core_instructions": [
                "毎回thinkingを必須にする（絶対）",
                "処理中は英語を使用する",
                "宣言は日本語（## 🎯 これから行うこと）",
                "報告は日本語（## ✅ 完遂報告）",
                "役職は動的システム（静的ではない）",
                "4分割ペインはclaude code 4画面同時起動",
                "ダッシュボードは1+4人構成（プレジデント＋4人）",
                "偽装データは絶対禁止（戦争級重罪）",
            ],
            "critical_reminders": [
                "🚨 thinking必須 - 毎回必ず使用",
                "🚨 基本情報を忘れない - 超強力矯正必要",
                "🚨 役職は動的 - 静的ではない",
                "🚨 言語ルール遵守 - 日本語/英語使い分け",
            ],
        }

        # 違反記録ファイル
        self.violation_log = self.project_root / "runtime" / "thinking_violations.json"
        self.violation_log.parent.mkdir(parents=True, exist_ok=True)

        # 強制リマインダー設定
        self.reminder_triggers = {
            "session_start": True,
            "every_5_responses": True,
            "after_violation": True,
            "before_critical_tasks": True,
        }

        self.response_count = 0
        self.load_violation_history()

    def load_violation_history(self):
        """違反履歴を読み込み"""
        if self.violation_log.exists():
            try:
                with open(self.violation_log, encoding="utf-8") as f:
                    data = json.load(f)
                    for rule_name, rule_data in data.get("rules", {}).items():
                        if rule_name in self.mandatory_rules:
                            self.mandatory_rules[rule_name]["violation_count"] = (
                                rule_data.get("violation_count", 0)
                            )
                            self.mandatory_rules[rule_name]["last_violation"] = (
                                rule_data.get("last_violation")
                            )
            except Exception as e:
                self.logger.warning(f"Could not load violation history: {e}")

    def save_violation_history(self):
        """違反履歴を保存"""
        data = {
            "last_updated": datetime.now().isoformat(),
            "rules": self.mandatory_rules,
            "total_violations": sum(
                rule["violation_count"] for rule in self.mandatory_rules.values()
            ),
        }

        try:
            with open(self.violation_log, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Could not save violation history: {e}")

    def record_violation(self, rule_name: str, context: str = ""):
        """違反を記録"""
        if rule_name in self.mandatory_rules:
            self.mandatory_rules[rule_name]["violation_count"] += 1
            self.mandatory_rules[rule_name]["last_violation"] = {
                "timestamp": datetime.now().isoformat(),
                "context": context,
            }
            self.save_violation_history()

            # 重大違反の場合は即座にアラート
            if self.mandatory_rules[rule_name]["severity"] == "CRITICAL":
                self.generate_critical_alert(rule_name)

    def generate_critical_alert(self, rule_name: str):
        """重大違反アラート生成"""
        rule = self.mandatory_rules[rule_name]
        alert_msg = f"""
🚨🚨🚨 CRITICAL VIOLATION DETECTED 🚨🚨🚨
Rule: {rule_name}
Description: {rule["description"]}
Violation Count: {rule["violation_count"]}
Severity: {rule["severity"]}

IMMEDIATE ACTION REQUIRED:
- This violation must be corrected immediately
- Future responses must comply with this rule
- Consider implementing additional enforcement measures
"""
        print(alert_msg)
        self.logger.critical(alert_msg)

    def get_session_reminder(self) -> str:
        """セッション開始時リマインダー"""
        return f"""
🧠 THINKING ENFORCER - セッション開始リマインダー
===========================================

🚨 CRITICAL RULES - 絶対遵守:
{chr(10).join(f"• {rule}" for rule in self.memory_reinforcement["core_instructions"])}

🔔 CRITICAL REMINDERS:
{chr(10).join(f"• {reminder}" for reminder in self.memory_reinforcement["critical_reminders"])}

📊 VIOLATION SUMMARY:
{chr(10).join(f"• {name}: {rule['violation_count']} violations" for name, rule in self.mandatory_rules.items())}

⚠️ REMEMBER: thinking必須 - 毎回必ず使用してください
"""

    def get_periodic_reminder(self) -> str:
        """定期リマインダー"""
        self.response_count += 1

        if self.response_count % 5 == 0:
            return f"""
🔔 定期リマインダー (Response #{self.response_count})
thinking必須 - 毎回必ず<thinking>タグを使用
処理中は英語、宣言・報告は日本語
役職は動的システム
"""
        return ""

    def check_response_compliance(self, response: str) -> Dict[str, Any]:
        """レスポンス遵守状況チェック"""
        violations = []

        # thinking必須チェック
        if not response.strip().startswith("<thinking>"):
            violations.append(
                {
                    "rule": "thinking_required",
                    "message": "Response must start with <thinking> tags",
                    "severity": "CRITICAL",
                }
            )
            self.record_violation("thinking_required", "Missing thinking tags")

        # 動的役職チェック
        if "static" in response.lower() or "固定" in response:
            violations.append(
                {
                    "rule": "dynamic_roles",
                    "message": "Remember roles are dynamic, not static",
                    "severity": "HIGH",
                }
            )
            self.record_violation("dynamic_roles", "Mentioned static roles")

        return {
            "compliant": len(violations) == 0,
            "violations": violations,
            "total_violations": sum(
                rule["violation_count"] for rule in self.mandatory_rules.values()
            ),
        }

    def generate_enforcement_report(self) -> str:
        """強制報告書生成"""
        total_violations = sum(
            rule["violation_count"] for rule in self.mandatory_rules.values()
        )

        report = f"""
📋 THINKING ENFORCER REPORT
==========================
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Total Violations: {total_violations}

RULE COMPLIANCE STATUS:
"""

        for rule_name, rule_data in self.mandatory_rules.items():
            status = (
                "✅ COMPLIANT"
                if rule_data["violation_count"] == 0
                else f"❌ {rule_data['violation_count']} VIOLATIONS"
            )
            report += f"• {rule_name}: {status}\n"

        report += f"""
CRITICAL REMINDERS:
{chr(10).join(f"• {reminder}" for reminder in self.memory_reinforcement["critical_reminders"])}

RECOMMENDED ACTIONS:
• Implement pre-response thinking check
• Add automatic reminder system
• Consider additional enforcement measures
"""

        return report

    def create_enforcement_hook(self) -> str:
        """強制フック作成"""
        hook_content = '''#!/usr/bin/env python3
"""
Thinking Enforcer Hook - 自動実行フック
"""
import sys
sys.path.append("src")
from memory.thinking_enforcer import ThinkingEnforcer

enforcer = ThinkingEnforcer()
print(enforcer.get_session_reminder())
'''

        hook_path = (
            self.project_root / "scripts" / "hooks" / "thinking_enforcer_hook.py"
        )
        hook_path.parent.mkdir(parents=True, exist_ok=True)

        with open(hook_path, "w", encoding="utf-8") as f:
            f.write(hook_content)

        # 実行権限付与
        os.chmod(hook_path, 0o755)

        return str(hook_path)


def main():
    """メイン実行"""
    enforcer = ThinkingEnforcer()

    print("🧠 Thinking Enforcer - 思考過程必須化システム")
    print("=" * 50)

    # セッション開始リマインダー
    print(enforcer.get_session_reminder())

    # 強制レポート
    print(enforcer.generate_enforcement_report())

    # フック作成
    hook_path = enforcer.create_enforcement_hook()
    print(f"✅ Enforcement hook created: {hook_path}")

    print("\n🚨 CRITICAL: thinking必須 - 毎回必ず使用してください")


if __name__ == "__main__":
    main()
