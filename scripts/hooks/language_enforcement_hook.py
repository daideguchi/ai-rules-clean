#!/usr/bin/env python3
"""
Language Enforcement Hook
言語使用ルール強制実行システム - 処理は英語、報告は日本語
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path


class LanguageEnforcementHook:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.mistakes_db_path = (
            self.project_root / "src/memory/persistent-learning/mistakes-database.json"
        )
        self.language_violation_patterns = {
            "mixed_processing": r"(I will|Let me|I'll|I'm going to|I need to).*?(処理|実装|修正|対応)",
            "japanese_processing": r"(処理します|実装します|修正します|対応します).*?(using|with|by|through)",
            "english_reporting": r"(Successfully|Completed|Finished|Done).*?(完了|成功|終了)",
            "forbidden_mixing": r"(する|した|します|でした).*(will|shall|would|should|can|could|must|may|might)",
        }

        self.report_template = {
            "processing_phase": "english_only",
            "reporting_phase": "japanese_only",
            "status_format": "【{status}】{details}",
            "result_format": "実行結果: {result}",
            "error_format": "エラー: {error_details}",
        }

    def check_language_violations(self, text: str) -> list:
        """Check for language usage violations"""
        violations = []

        for violation_type, pattern in self.language_violation_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                violations.append(
                    {
                        "type": violation_type,
                        "pattern": pattern,
                        "matches": matches,
                        "severity": "critical",
                        "auto_fix": True,
                    }
                )

        return violations

    def enforce_language_rules(self, text: str) -> str:
        """Automatically enforce language rules"""
        # Phase 1: Processing descriptions (English only)
        processing_patterns = [
            (r"処理します", "processing"),
            (r"実装します", "implementing"),
            (r"修正します", "fixing"),
            (r"対応します", "handling"),
            (r"作成します", "creating"),
            (r"更新します", "updating"),
        ]

        fixed_text = text
        for jp_pattern, en_replacement in processing_patterns:
            if re.search(r"(I will|Let me|I'll).*?" + jp_pattern, fixed_text):
                fixed_text = re.sub(jp_pattern, en_replacement, fixed_text)

        # Phase 2: Reporting descriptions (Japanese only)
        reporting_patterns = [
            (r"Successfully (completed|finished|done)", "正常に完了しました"),
            (r"Implementation (completed|finished|done)", "実装が完了しました"),
            (r"File (created|updated|modified)", "ファイルを更新しました"),
            (r"System (activated|enabled|started)", "システムを起動しました"),
        ]

        for en_pattern, jp_replacement in reporting_patterns:
            fixed_text = re.sub(
                en_pattern, jp_replacement, fixed_text, flags=re.IGNORECASE
            )

        return fixed_text

    def generate_compliant_report(
        self, operation: str, details: str, result: str
    ) -> str:
        """Generate language-compliant report"""
        template = f"""
【{operation}】

処理内容: {details}
実行結果: {result}
実行時刻: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

言語使用ルール準拠済み
"""
        return template.strip()

    def log_violation(self, violation_data: dict):
        """Log language violation to mistakes database"""
        try:
            if self.mistakes_db_path.exists():
                with open(self.mistakes_db_path, encoding="utf-8") as f:
                    db = json.load(f)

                # Update mistake_008 statistics
                for mistake in db.get("critical_patterns", []):
                    if mistake["id"] == "mistake_008":
                        mistake["incident_count"] += 1
                        mistake["last_occurrence"] = datetime.now().isoformat()
                        break

                with open(self.mistakes_db_path, "w", encoding="utf-8") as f:
                    json.dump(db, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"Error logging language violation: {e}")

    def process_input(self, input_text: str) -> dict:
        """Process input text for language compliance"""
        violations = self.check_language_violations(input_text)

        if violations:
            # Log violations
            for violation in violations:
                self.log_violation(violation)

            # Auto-fix if possible
            fixed_text = self.enforce_language_rules(input_text)

            return {
                "compliant": False,
                "violations": violations,
                "original_text": input_text,
                "fixed_text": fixed_text,
                "action": "auto_enforcement_applied",
            }

        return {
            "compliant": True,
            "violations": [],
            "original_text": input_text,
            "fixed_text": input_text,
            "action": "no_action_needed",
        }


def main():
    """Main execution for hook integration"""
    if len(sys.argv) < 2:
        print("Usage: language_enforcement_hook.py <text_to_check>", file=sys.stderr)
        sys.exit(1)

    hook = LanguageEnforcementHook()
    input_text = " ".join(sys.argv[1:])

    result = hook.process_input(input_text)

    if not result["compliant"]:
        print("【言語使用ルール違反検出】", file=sys.stderr)
        print(f"違反数: {len(result['violations'])}", file=sys.stderr)
        print(f"修正済みテキスト: {result['fixed_text']}", file=sys.stderr)

        # Return fixed text for automatic application
        print(result["fixed_text"])
        sys.exit(1)
    else:
        print("【言語使用ルール準拠確認】", file=sys.stderr)
        print(result["original_text"])
        sys.exit(0)


if __name__ == "__main__":
    main()
