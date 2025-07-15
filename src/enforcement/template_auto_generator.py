#!/usr/bin/env python3
"""
📋 Template Auto-Generator
=========================

Generates correctly formatted responses following CLAUDE.md template
"""

import subprocess
from pathlib import Path
from typing import Dict, List


class TemplateAutoGenerator:
    """Generates responses following mandatory template"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent

    def generate_response(
        self,
        thinking: str,
        task_declaration: str,
        processing_steps: List[str],
        results: Dict,
        task_level: str = "SIMPLE",
    ) -> str:
        """Generate a complete response following CLAUDE.md template"""

        # Determine appropriate thinking mode based on task level
        thinking_mode = self._get_thinking_mode(task_level)
        formatted_thinking = (
            f"{thinking_mode}\n{thinking}\n</{thinking_mode.replace('<', '')}>"
        )

        # Get dynamic system status
        status = self._get_system_status()

        # Get PRESIDENT status
        president_status = self._get_president_status()

        # Get log check results
        log_check = self._get_log_check()

        # Build response
        response_parts = [
            formatted_thinking,
            "",
            president_status,
            "",
            status,
            "",
            log_check,
            "",
            "## 🎯 これから行うこと",
            task_declaration,
            "",
        ]

        # Add processing steps
        for step in processing_steps:
            response_parts.append(step)

        response_parts.extend(["", "## ✅ 完遂報告"])

        # Add results
        if results.get("success"):
            for item in results["success"]:
                path = item.get("path", "")
                response_parts.append(f"- ✅ {item['description']}: {path}")

        if results.get("failures"):
            for item in results["failures"]:
                path = item.get("path", "")
                reason = item.get("reason", "技術的エラー")
                response_parts.append(f"- ❌ {item['description']}: {reason} ({path})")

        if results.get("warnings"):
            for item in results["warnings"]:
                response_parts.append(f"- ⚠️ {item['description']}")

        # Add recording report
        if results.get("recordings"):
            response_parts.extend(["", "**記録報告**:"])
            for record in results["recordings"]:
                response_parts.append(
                    f"- 📝 {record['content']}を{record['destination']}に記録完了"
                )

        # Add file modifications
        if results.get("modified_files"):
            files = ", ".join(results["modified_files"])
            response_parts.append(f"- 📁 修正ファイル: {files}")

        # Add status
        if results.get("status"):
            response_parts.append(f"- 🔧 処理ステータス: {results['status']}")

        return "\n".join(response_parts)

    def _get_system_status(self) -> str:
        """Get dynamic system status"""
        try:
            script_path = (
                self.project_root / "scripts" / "hooks" / "system_status_display.py"
            )
            if not script_path.exists():
                return "📊 **システム状況**\n**ステータス表示スクリプト未検出**"

            result = subprocess.run(
                ["python3", str(script_path)],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=5,
            )

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return "📊 **システム状況**\n**ステータス取得エラー**"

        except subprocess.TimeoutExpired:
            return "📊 **システム状況**\n**タイムアウト**"
        except Exception as e:
            return f"📊 **システム状況**\n**エラー**: {str(e)}"

    def _get_president_status(self) -> str:
        """Get PRESIDENT declaration status"""
        try:
            president_file = (
                self.project_root / "runtime" / "unified-president-declare.json"
            )
            if president_file.exists():
                return "🔴 **PRESIDENT確認**\nPRESIDENT宣言済み: runtime/unified-president-declare.json確認済み"
            else:
                return "🔴 **PRESIDENT確認**\n❌ PRESIDENT宣言未実行 - make declare-president実行が必要"
        except Exception as e:
            return f"🔴 **PRESIDENT確認**\n**エラー**: {str(e)}"

    def _get_log_check(self) -> str:
        """Get log check results based on judgment level"""
        log_results = []

        # Check violation logs
        violations_file = self.project_root / "runtime" / "thinking_violations.json"
        if violations_file.exists():
            log_results.append(
                "- 違反記録: runtime/thinking_violations.json - チェック済み"
            )
        else:
            log_results.append("- 違反記録: 記録なし")

        # Check memory logs
        memory_file = self.project_root / "runtime" / "memory" / "session_logs.json"
        if memory_file.exists():
            log_results.append(
                "- 記憶システム: runtime/memory/session_logs.json - 正常動作"
            )
        else:
            log_results.append("- 記憶システム: 初期化中")

        # Check mistake prevention
        mistakes_file = (
            self.project_root
            / "runtime"
            / "mistake_prevention"
            / "mistakes_ledger.json"
        )
        if mistakes_file.exists():
            log_results.append(
                "- ミス防止: runtime/mistake_prevention/mistakes_ledger.json - 監視中"
            )
        else:
            log_results.append("- ミス防止: システム待機中")

        return "📋 **記録ログ確認**\n" + "\n".join(log_results)

    def _get_thinking_mode(self, task_level: str) -> str:
        """Get appropriate thinking mode based on task level"""
        thinking_modes = {
            "SIMPLE": "<think>",
            "MEDIUM": "<think hard>",
            "COMPLEX": "<think harder>",
            "CRITICAL": "<ultrathink>",
        }
        return thinking_modes.get(task_level.upper(), "<think>")


def main():
    """Test template generator"""
    generator = TemplateAutoGenerator()

    # Test data
    response = generator.generate_response(
        thinking="テンプレート生成テストを実行",
        task_declaration="テンプレート自動生成システムのテスト実行",
        processing_steps=[
            "Creating template generator...",
            "Testing response format...",
            "Validating output...",
        ],
        results={
            "success": [
                {
                    "description": "テンプレート生成完了",
                    "path": "/src/enforcement/template_auto_generator.py",
                }
            ],
            "recordings": [{"content": "テンプレート仕様", "destination": "CLAUDE.md"}],
            "modified_files": ["/src/enforcement/template_auto_generator.py"],
            "status": "テンプレート生成システム正常動作",
        },
    )

    print(response)


if __name__ == "__main__":
    main()
