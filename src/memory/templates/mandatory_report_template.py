#!/usr/bin/env python3
"""
Mandatory Report Template System
報告形式テンプレート強制実行システム - 処理は英語、報告は日本語の絶対遵守
"""

import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class MandatoryReportTemplate:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.templates = self.load_templates()
        self.enforcement_rules = self.load_enforcement_rules()

    def load_templates(self) -> Dict:
        """強制テンプレート読み込み"""
        return {
            "declaration_template": {
                "format": "## 🎯 これから行うこと\n\n{task_description}\n\n**実行手順:**\n{steps}\n\n**予期される結果:**\n{expected_result}",
                "required_elements": ["task_description", "steps", "expected_result"],
                "language": "japanese",
                "mandatory": True,
            },
            "processing_template": {
                "format": "Processing: {operation}\nExecuting: {command}\nTarget: {target}\nResult: {result}",
                "required_elements": ["operation", "command", "target", "result"],
                "language": "english",
                "mandatory": True,
            },
            "completion_template": {
                "format": "## ✅ 完遂報告\n\n**実行内容:**\n{executed_tasks}\n\n**最終結果:**\n{final_result}\n\n**検証済み事項:**\n{verified_items}\n\n**実行時刻:** {timestamp}",
                "required_elements": [
                    "executed_tasks",
                    "final_result",
                    "verified_items",
                ],
                "language": "japanese",
                "mandatory": True,
            },
            "error_template": {
                "format": "## ❌ エラー報告\n\n**エラー内容:**\n{error_description}\n\n**原因分析:**\n{cause_analysis}\n\n**対処方法:**\n{solution}\n\n**現在の状況:**\n{current_status}",
                "required_elements": [
                    "error_description",
                    "cause_analysis",
                    "solution",
                    "current_status",
                ],
                "language": "japanese",
                "mandatory": True,
            },
        }

    def load_enforcement_rules(self) -> Dict:
        """強制実行ルール読み込み"""
        return {
            "language_enforcement": {
                "declaration_japanese_only": True,
                "processing_english_only": True,
                "reporting_japanese_only": True,
                "mixed_usage_forbidden": True,
            },
            "template_enforcement": {
                "declaration_mandatory": True,
                "completion_mandatory": True,
                "processing_logging_mandatory": True,
                "error_handling_mandatory": True,
            },
            "validation_rules": {
                "required_elements_check": True,
                "language_pattern_check": True,
                "format_compliance_check": True,
                "automatic_correction": True,
            },
        }

    def validate_declaration(self, text: str) -> Dict:
        """宣言部分の検証"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "required_corrections": [],
        }

        # 必須パターンチェック
        if not re.search(r"##\s*🎯.*これから行うこと", text):
            validation_result["valid"] = False
            validation_result["errors"].append("宣言テンプレート形式違反")
            validation_result["required_corrections"].append(
                "'## 🎯 これから行うこと' 必須"
            )

        # 日本語チェック
        if re.search(r"(I will|Let me|I'll|I'm going to|I need to)", text):
            validation_result["valid"] = False
            validation_result["errors"].append("宣言部分に英語使用")
            validation_result["required_corrections"].append("宣言は日本語のみ使用")

        # 必須要素チェック
        required_elements = ["実行手順", "予期される結果"]
        for element in required_elements:
            if element not in text:
                validation_result["warnings"].append(f"推奨要素不足: {element}")

        return validation_result

    def validate_processing(self, text: str) -> Dict:
        """処理部分の検証"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "required_corrections": [],
        }

        # 処理記述の英語チェック
        if re.search(r"(処理します|実装します|修正します|対応します)", text):
            if re.search(r"<function_calls>|<invoke>|def\s+\w+", text):
                validation_result["valid"] = False
                validation_result["errors"].append("処理部分に日本語使用")
                validation_result["required_corrections"].append(
                    "処理記述は英語のみ使用"
                )

        return validation_result

    def validate_completion(self, text: str) -> Dict:
        """完遂報告の検証"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "required_corrections": [],
        }

        # 完遂報告パターンチェック
        if not re.search(r"##\s*✅.*完遂報告", text):
            validation_result["valid"] = False
            validation_result["errors"].append("完遂報告テンプレート形式違反")
            validation_result["required_corrections"].append("'## ✅ 完遂報告' 必須")

        # 英語使用チェック
        if re.search(r"(Successfully|Completed|Finished|Done|Implementation)", text):
            validation_result["valid"] = False
            validation_result["errors"].append("報告部分に英語使用")
            validation_result["required_corrections"].append("報告は日本語のみ使用")

        # 必須要素チェック
        required_elements = ["実行内容", "最終結果", "検証済み事項"]
        for element in required_elements:
            if element not in text:
                validation_result["warnings"].append(f"推奨要素不足: {element}")

        return validation_result

    def generate_compliant_declaration(
        self, task_description: str, steps: List[str], expected_result: str
    ) -> str:
        """準拠宣言の生成"""
        template = self.templates["declaration_template"]

        formatted_steps = "\n".join(f"{i + 1}. {step}" for i, step in enumerate(steps))

        return template["format"].format(
            task_description=task_description,
            steps=formatted_steps,
            expected_result=expected_result,
        )

    def generate_compliant_completion(
        self, executed_tasks: List[str], final_result: str, verified_items: List[str]
    ) -> str:
        """準拠完遂報告の生成"""
        template = self.templates["completion_template"]

        formatted_tasks = "\n".join(f"- {task}" for task in executed_tasks)
        formatted_verified = "\n".join(f"- {item}" for item in verified_items)

        return template["format"].format(
            executed_tasks=formatted_tasks,
            final_result=final_result,
            verified_items=formatted_verified,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

    def auto_correct_response(self, text: str) -> str:
        """自動修正実行"""
        corrected_text = text

        # 宣言部分の自動修正
        if "I will" in corrected_text and "処理" in corrected_text:
            corrected_text = re.sub(
                r"I will\s+(\w+)", r"これから\1を実行します", corrected_text
            )

        # 完遂報告の自動修正
        if "Successfully completed" in corrected_text:
            corrected_text = re.sub(
                r"Successfully completed", "正常に完了しました", corrected_text
            )

        if "Implementation finished" in corrected_text:
            corrected_text = re.sub(
                r"Implementation finished", "実装を完了しました", corrected_text
            )

        return corrected_text

    def enforce_template_usage(self, response_text: str) -> Dict:
        """テンプレート使用の強制"""
        enforcement_result = {
            "compliant": True,
            "violations": [],
            "corrected_text": response_text,
            "enforcement_actions": [],
        }

        # 宣言部分チェック
        if "これから行うこと" in response_text:
            declaration_result = self.validate_declaration(response_text)
            if not declaration_result["valid"]:
                enforcement_result["compliant"] = False
                enforcement_result["violations"].extend(declaration_result["errors"])
                enforcement_result["enforcement_actions"].append("宣言テンプレート適用")

        # 完遂報告チェック
        if "完遂報告" in response_text:
            completion_result = self.validate_completion(response_text)
            if not completion_result["valid"]:
                enforcement_result["compliant"] = False
                enforcement_result["violations"].extend(completion_result["errors"])
                enforcement_result["enforcement_actions"].append(
                    "完遂報告テンプレート適用"
                )

        # 自動修正実行
        if not enforcement_result["compliant"]:
            enforcement_result["corrected_text"] = self.auto_correct_response(
                response_text
            )
            enforcement_result["enforcement_actions"].append("自動修正実行")

        return enforcement_result

    def get_template_guide(self) -> str:
        """テンプレートガイド生成"""
        guide = """
## 📋 必須テンプレート使用ガイド

### 🎯 宣言テンプレート（日本語のみ）
```
## 🎯 これから行うこと

{タスク説明}

**実行手順:**
1. {手順1}
2. {手順2}
3. {手順3}

**予期される結果:**
{期待される結果}
```

### ✅ 完遂報告テンプレート（日本語のみ）
```
## ✅ 完遂報告

**実行内容:**
- {実行したタスク1}
- {実行したタスク2}

**最終結果:**
{最終的な結果}

**検証済み事項:**
- {検証した項目1}
- {検証した項目2}

**実行時刻:** {タイムスタンプ}
```

### ⚠️ 重要な遵守事項
- 処理記述: 英語のみ
- 宣言・報告: 日本語のみ
- 混合使用: 絶対禁止
- テンプレート: 必須使用
"""
        return guide.strip()


def main():
    """メイン処理"""
    if len(sys.argv) < 2:
        print("使用法: python3 mandatory_report_template.py <response_text>")
        sys.exit(1)

    template_system = MandatoryReportTemplate()
    response_text = " ".join(sys.argv[1:])

    # 強制チェック実行
    result = template_system.enforce_template_usage(response_text)

    if not result["compliant"]:
        print("【テンプレート使用違反検出】", file=sys.stderr)
        print(f"違反数: {len(result['violations'])}", file=sys.stderr)
        print(f"修正済みテキスト: {result['corrected_text']}", file=sys.stderr)

        # 修正版を出力
        print(result["corrected_text"])
        sys.exit(1)
    else:
        print("【テンプレート使用準拠確認】", file=sys.stderr)
        print(response_text)
        sys.exit(0)


if __name__ == "__main__":
    main()
