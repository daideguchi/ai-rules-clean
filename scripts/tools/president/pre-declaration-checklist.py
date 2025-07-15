#!/usr/bin/env python3
"""
[LEGACY WRAPPER] Pre-Declaration Checklist

このスクリプトは unified-president-tool.py に統合されました。
Phase 5 統合完了 - レガシー互換性のためのwrapperスクリプト

新しい使用方法:
  scripts/tools/unified-president-tool.py checklist <task_description>
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict

print("⚠️  [LEGACY] pre-declaration-checklist.py は統合されました")
print("📦 unified-president-tool.py checklist に移行してください")
print("")
print("🔄 自動転送中...")

# 統合ツールの実行
script_dir = Path(__file__).parent
unified_tool = script_dir.parent / "unified-president-tool.py"

# 引数変換
if len(sys.argv) < 2:
    args = ["checklist", "デフォルトタスク"]
elif sys.argv[1] == "stats":
    args = ["stats"]
else:
    args = ["checklist"] + sys.argv[1:]

os.execv(sys.executable, [sys.executable, str(unified_tool)] + args)


class PreDeclarationChecker:
    """Enforces mandatory checks before making any commitment"""

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.checklist_template = {
            "requirement_analysis": {
                "question": "具体的要件を文書化済み？",
                "required": True,
                "validation": self._validate_requirements,
            },
            "feasibility_assessment": {
                "question": "実現可能性60%以上で査定済み？",
                "required": True,
                "validation": self._validate_feasibility,
            },
            "time_estimation": {
                "question": "所要時間を30-120分で見積り済み？",
                "required": True,
                "validation": self._validate_time_estimate,
            },
            "dependency_mapping": {
                "question": "依存関係を特定済み？",
                "required": True,
                "validation": self._validate_dependencies,
            },
            "completion_criteria": {
                "question": "完了条件を明確化済み？",
                "required": True,
                "validation": self._validate_completion_criteria,
            },
        }

    def _validate_requirements(self, response: str) -> Dict:
        """Validate requirements documentation"""
        if len(response.strip()) < 50:
            return {"valid": False, "error": "要件が不十分です（最低50文字必要）"}

        # Check for specific patterns
        required_patterns = [
            r"(実装|作成|修正|削除|追加)",  # Action verbs
            r"(ファイル|機能|システム|スクリプト)",  # Objects
            r"(により|ため|目的|理由)",  # Purpose indicators
        ]

        missing_patterns = []
        for pattern in required_patterns:
            if not re.search(pattern, response):
                missing_patterns.append(pattern)

        if missing_patterns:
            return {"valid": False, "error": f"要件に不足要素: {missing_patterns}"}

        return {"valid": True}

    def _validate_feasibility(self, response: str) -> Dict:
        """Validate feasibility assessment"""
        # Look for confidence indicators
        confidence_patterns = [
            r"(\d+)%",  # Percentage
            r"(可能|困難|実現可能|実装可能)",  # Feasibility terms
            r"(リスク|問題|障害|制約)",  # Risk assessment
        ]

        found_patterns = []
        for pattern in confidence_patterns:
            if re.search(pattern, response):
                found_patterns.append(pattern)

        if len(found_patterns) < 2:
            return {
                "valid": False,
                "error": "実現可能性の詳細分析が不足（確信度、リスク評価が必要）",
            }

        return {"valid": True}

    def _validate_time_estimate(self, response: str) -> Dict:
        """Validate time estimation"""
        # Extract time estimates
        time_patterns = [
            r"(\d+)\s*分",  # Minutes
            r"(\d+)\s*時間",  # Hours
            r"(\d+)\s*h",  # Hours (short)
            r"(\d+)\s*min",  # Minutes (short)
        ]

        total_minutes = 0
        for pattern in time_patterns:
            matches = re.findall(pattern, response)
            for match in matches:
                if "分" in pattern or "min" in pattern:
                    total_minutes += int(match)
                else:  # Hours
                    total_minutes += int(match) * 60

        if total_minutes < 30:
            return {"valid": False, "error": "見積り時間が短すぎます（最低30分必要）"}

        if total_minutes > 120:
            return {
                "valid": False,
                "error": "見積り時間が長すぎます（最大120分、分割が必要）",
            }

        return {"valid": True, "estimated_minutes": total_minutes}

    def _validate_dependencies(self, response: str) -> Dict:
        """Validate dependency mapping"""
        dependency_indicators = [
            r"(依存|必要|前提|条件)",  # Dependency terms
            r"(ファイル|ツール|ライブラリ|システム)",  # Resource types
            r"(完了|実装|存在|利用可能)",  # Status indicators
        ]

        found_indicators = 0
        for pattern in dependency_indicators:
            if re.search(pattern, response):
                found_indicators += 1

        if found_indicators < 2:
            return {
                "valid": False,
                "error": "依存関係の分析が不十分（必要リソース、前提条件を明記）",
            }

        return {"valid": True}

    def _validate_completion_criteria(self, response: str) -> Dict:
        """Validate completion criteria"""
        criteria_patterns = [
            r"(完了|終了|完成|成功)",  # Completion terms
            r"(確認|検証|テスト|動作)",  # Verification terms
            r"(条件|基準|要件|状態)",  # Criteria terms
        ]

        found_criteria = 0
        for pattern in criteria_patterns:
            if re.search(pattern, response):
                found_criteria += 1

        if found_criteria < 2:
            return {"valid": False, "error": "完了条件が不明確（検証可能な基準を設定）"}

        return {"valid": True}

    def run_checklist(self, task_description: str) -> Dict:
        """Run the complete pre-declaration checklist"""

        print("🔍 宣言前チェックリスト開始")
        print(f"📋 対象タスク: {task_description}")
        print("=" * 60)

        results = {}
        all_passed = True

        for check_id, check_config in self.checklist_template.items():
            print(f"\n❓ {check_config['question']}")

            if check_config["required"]:
                print("   (必須項目)")

            # Get user input
            response = input("回答: ").strip()

            if not response:
                results[check_id] = {"passed": False, "error": "回答が空です"}
                all_passed = False
                print("❌ 回答が必要です")
                continue

            # Validate response
            validation_result = check_config["validation"](response)

            if validation_result["valid"]:
                results[check_id] = {
                    "passed": True,
                    "response": response,
                    "metadata": validation_result.get("metadata", {}),
                }
                print("✅ 合格")
            else:
                results[check_id] = {
                    "passed": False,
                    "response": response,
                    "error": validation_result["error"],
                }
                all_passed = False
                print(f"❌ {validation_result['error']}")

        print("\n" + "=" * 60)

        if all_passed:
            print("✅ 全チェック合格 - 宣言許可")
            self._save_checklist_result(task_description, results, "APPROVED")
            return {"approved": True, "results": results}
        else:
            print("❌ チェック不合格 - 宣言禁止")
            print("\n🚫 許可される表現:")
            print("   - 「調査します」")
            print("   - 「検討します」")
            print("   - 「実現可能性を査定してから回答します」")

            self._save_checklist_result(task_description, results, "REJECTED")
            return {"approved": False, "results": results}

    def _save_checklist_result(self, task_description: str, results: Dict, status: str):
        """Save checklist results for audit trail"""

        runtime_dir = self.repo_path / "runtime"
        runtime_dir.mkdir(exist_ok=True)

        checklist_log = runtime_dir / "pre-declaration-log.json"

        # Load existing log
        if checklist_log.exists():
            with open(checklist_log) as f:
                log_data = json.load(f)
        else:
            log_data = {"entries": []}

        # Add new entry
        entry = {
            "timestamp": datetime.now().isoformat(),
            "task_description": task_description,
            "status": status,
            "results": results,
        }

        log_data["entries"].append(entry)

        # Save updated log
        with open(checklist_log, "w") as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)

        print(f"📝 チェックリスト結果を保存: {checklist_log}")

    def get_checklist_stats(self) -> Dict:
        """Get statistics about checklist usage"""

        checklist_log = self.repo_path / "runtime" / "pre-declaration-log.json"

        if not checklist_log.exists():
            return {"total_checks": 0, "approved": 0, "rejected": 0, "approval_rate": 0}

        with open(checklist_log) as f:
            log_data = json.load(f)

        entries = log_data.get("entries", [])
        approved = sum(1 for entry in entries if entry["status"] == "APPROVED")
        rejected = sum(1 for entry in entries if entry["status"] == "REJECTED")

        return {
            "total_checks": len(entries),
            "approved": approved,
            "rejected": rejected,
            "approval_rate": approved / len(entries) if entries else 0,
        }


def main():
    """CLI interface for pre-declaration checklist"""

    if len(sys.argv) < 2:
        print("Usage: python pre-declaration-checklist.py <command> [args...]")
        print("Commands: check, stats")
        return

    checker = PreDeclarationChecker()
    command = sys.argv[1]

    if command == "check":
        if len(sys.argv) < 3:
            print("Usage: check <task_description>")
            return

        task_description = " ".join(sys.argv[2:])
        result = checker.run_checklist(task_description)

        if result["approved"]:
            print("\n🎯 宣言可能です。次のステップに進んでください。")
        else:
            print("\n🚫 宣言は許可されません。要件を再検討してください。")

    elif command == "stats":
        stats = checker.get_checklist_stats()
        print("📊 チェックリスト統計:")
        print(f"   総チェック数: {stats['total_checks']}")
        print(f"   承認: {stats['approved']}")
        print(f"   却下: {stats['rejected']}")
        print(f"   承認率: {stats['approval_rate']:.1%}")

    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
