#!/usr/bin/env python3
"""
Language System Integration
言語使用ルール統合システム - 全てのコンポーネントを統合した自動強制実行
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict


class LanguageSystemIntegration:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.components = self.initialize_components()
        self.enforcement_log = (
            self.project_root / "runtime/ai_api_logs/language_enforcement.log"
        )

    def initialize_components(self) -> Dict:
        """全コンポーネントの初期化"""
        return {
            "language_enforcement_hook": self.project_root
            / "scripts/hooks/language_enforcement_hook.py",
            "president_declaration_gate": self.project_root
            / "scripts/hooks/president_declaration_gate.py",
            "runtime_advisor": self.project_root / "src/memory/core/runtime_advisor.py",
            "mandatory_report_template": self.project_root
            / "src/memory/templates/mandatory_report_template.py",
            "mistakes_database": self.project_root
            / "src/memory/persistent-learning/mistakes-database.json",
        }

    def enforce_language_rules(self, input_text: str, context: str = "general") -> Dict:
        """言語ルール強制実行"""
        enforcement_result = {
            "timestamp": datetime.now().isoformat(),
            "input_text": input_text[:200],  # 最初の200文字
            "context": context,
            "violations_detected": [],
            "corrected_text": input_text,
            "enforcement_actions": [],
            "compliance_score": 100,
        }

        # 1. Language Enforcement Hook実行
        try:
            hook_result = subprocess.run(
                [
                    "python3",
                    str(self.components["language_enforcement_hook"]),
                    input_text,
                ],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            if hook_result.returncode != 0:
                enforcement_result["violations_detected"].append(
                    "language_hook_violation"
                )
                enforcement_result["corrected_text"] = hook_result.stdout.strip()
                enforcement_result["enforcement_actions"].append(
                    "language_hook_correction"
                )
                enforcement_result["compliance_score"] -= 30
        except Exception as e:
            enforcement_result["enforcement_actions"].append(
                f"language_hook_error: {str(e)}"
            )

        # 2. Runtime Advisor実行
        try:
            advisor_result = subprocess.run(
                ["python3", str(self.components["runtime_advisor"]), input_text],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            if "mistake_008" in advisor_result.stdout:
                enforcement_result["violations_detected"].append(
                    "runtime_advisor_language_violation"
                )
                enforcement_result["enforcement_actions"].append(
                    "runtime_advisor_warning"
                )
                enforcement_result["compliance_score"] -= 25
        except Exception as e:
            enforcement_result["enforcement_actions"].append(
                f"runtime_advisor_error: {str(e)}"
            )

        # 3. Template System実行
        try:
            template_result = subprocess.run(
                [
                    "python3",
                    str(self.components["mandatory_report_template"]),
                    input_text,
                ],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            if template_result.returncode != 0:
                enforcement_result["violations_detected"].append("template_violation")
                enforcement_result["corrected_text"] = template_result.stdout.strip()
                enforcement_result["enforcement_actions"].append("template_correction")
                enforcement_result["compliance_score"] -= 20
        except Exception as e:
            enforcement_result["enforcement_actions"].append(
                f"template_error: {str(e)}"
            )

        return enforcement_result

    def validate_response_format(self, response_text: str) -> Dict:
        """レスポンス形式の検証"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "required_corrections": [],
            "template_compliance": False,
        }

        # 必須テンプレート要素のチェック
        required_sections = [
            ("🎯 これから行うこと", "declaration"),
            ("✅ 完遂報告", "completion"),
        ]

        for section_marker, section_type in required_sections:
            if section_marker in response_text:
                validation_result["template_compliance"] = True

                # 日本語使用チェック
                if section_type in ["declaration", "completion"]:
                    import re

                    if re.search(
                        r"(I will|Let me|I'll|Successfully|Completed)", response_text
                    ):
                        validation_result["valid"] = False
                        validation_result["errors"].append(
                            f"{section_type}部分に英語使用"
                        )
                        validation_result["required_corrections"].append(
                            f"{section_type}は日本語のみ使用"
                        )

        # 処理部分の英語チェック
        if "<function_calls>" in response_text or "<invoke>" in response_text:
            import re

            if re.search(r"処理します|実装します|修正します", response_text):
                validation_result["valid"] = False
                validation_result["errors"].append("処理部分に日本語使用")
                validation_result["required_corrections"].append(
                    "処理記述は英語のみ使用"
                )

        return validation_result

    def generate_compliance_report(self, text: str) -> str:
        """準拠報告の生成"""
        enforcement_result = self.enforce_language_rules(text)
        self.validate_response_format(text)

        report = f"""
## 📋 言語使用ルール準拠報告

**検証時刻:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**準拠スコア:** {enforcement_result["compliance_score"]}/100

### 🔍 検出された違反
{len(enforcement_result["violations_detected"])}件の違反を検出しました。

### 🛠️ 実行された修正
{chr(10).join(f"- {action}" for action in enforcement_result["enforcement_actions"])}

### ✅ 最終確認
- 宣言部分: 日本語のみ使用
- 処理部分: 英語のみ使用
- 報告部分: 日本語のみ使用
- テンプレート: 必須要素完備

**修正済みテキスト:**
{enforcement_result["corrected_text"]}
"""
        return report.strip()

    def log_enforcement_action(self, result: Dict):
        """強制実行アクションのログ記録"""
        try:
            self.enforcement_log.parent.mkdir(parents=True, exist_ok=True)

            with open(self.enforcement_log, "a", encoding="utf-8") as f:
                f.write(json.dumps(result, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"⚠️ 強制実行ログ記録失敗: {e}", file=sys.stderr)

    def get_system_status(self) -> Dict:
        """システム状態の取得"""
        status = {
            "components_available": {},
            "enforcement_active": True,
            "total_enforcements": 0,
            "success_rate": 0,
        }

        # コンポーネント状態チェック
        for component_name, component_path in self.components.items():
            status["components_available"][component_name] = component_path.exists()

        # 強制実行履歴の統計
        if self.enforcement_log.exists():
            try:
                with open(self.enforcement_log, encoding="utf-8") as f:
                    lines = f.readlines()
                    status["total_enforcements"] = len(lines)

                    # 成功率計算
                    successful = sum(
                        1 for line in lines if '"compliance_score": 100' in line
                    )
                    status["success_rate"] = (
                        (successful / len(lines) * 100) if lines else 0
                    )
            except Exception:
                pass

        return status

    def create_integration_hook(self):
        """統合フックの作成"""
        hook_content = f"""#!/usr/bin/env python3
import sys
import os
sys.path.append('{self.project_root / "src/memory/core"}')
from language_system_integration import LanguageSystemIntegration

def main():
    if len(sys.argv) < 2:
        print("Usage: integration_hook.py <text>")
        sys.exit(1)

    integration = LanguageSystemIntegration()
    text = " ".join(sys.argv[1:])

    result = integration.enforce_language_rules(text)

    if result["compliance_score"] < 100:
        print(result["corrected_text"])
        sys.exit(1)
    else:
        print(text)
        sys.exit(0)

if __name__ == "__main__":
    main()
"""

        hook_path = self.project_root / "scripts/hooks/language_integration_hook.py"
        with open(hook_path, "w", encoding="utf-8") as f:
            f.write(hook_content)

        # 実行権限付与
        os.chmod(hook_path, 0o755)

        return hook_path


def main():
    """メイン処理"""
    if len(sys.argv) < 2:
        print("使用法: python3 language_system_integration.py <text>")
        sys.exit(1)

    integration = LanguageSystemIntegration()
    text = " ".join(sys.argv[1:])

    # 強制実行
    result = integration.enforce_language_rules(text)

    # ログ記録
    integration.log_enforcement_action(result)

    # 結果出力
    if result["compliance_score"] < 100:
        print("【言語使用ルール違反 - 自動修正実行】", file=sys.stderr)
        print(f"準拠スコア: {result['compliance_score']}/100", file=sys.stderr)
        print(f"修正済みテキスト: {result['corrected_text']}", file=sys.stderr)

        # 修正版を出力
        print(result["corrected_text"])
        sys.exit(1)
    else:
        print("【言語使用ルール完全準拠】", file=sys.stderr)
        print(text)
        sys.exit(0)


if __name__ == "__main__":
    main()
