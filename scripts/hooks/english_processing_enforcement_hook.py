#!/usr/bin/env python3
"""
🔤 English Processing Enforcement Hook - 英語処理強制フック
=========================================================
技術処理の英語強制を実行するフック
PreToolUse event で実行され、言語使用ルールを強制する
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# プロジェクトルートを追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.ai.english_processing_enforcement import EnglishProcessingEnforcement
except ImportError as e:
    print(f"インポートエラー: {e}")
    sys.exit(1)


class EnglishProcessingEnforcementHook:
    """英語処理強制フック"""

    def __init__(self):
        self.project_root = project_root
        self.hook_log_file = (
            self.project_root / "runtime" / "logs" / "english_enforcement_hook.log"
        )
        self.enforcer = EnglishProcessingEnforcement()

        # ログファイル準備
        self.hook_log_file.parent.mkdir(parents=True, exist_ok=True)

        # 監視対象のツール
        self.monitored_tools = [
            "Edit",
            "Write",
            "MultiEdit",
            "Bash",
            "Task",
            "Read",
            "Grep",
            "Glob",
        ]

    def execute_pre_tool_use_hook(self, hook_data: dict = None) -> dict:
        """PreToolUse フック実行"""
        try:
            # フック情報の取得
            tool_name = os.environ.get("TOOL_NAME", "unknown")
            tool_args = os.environ.get("TOOL_ARGS", "{}")

            if tool_name not in self.monitored_tools:
                return {
                    "status": "skipped",
                    "reason": f"Tool {tool_name} not monitored",
                }

            self._log(f"🔤 英語処理強制フック実行: {tool_name}")

            # ツール引数の解析
            try:
                args = json.loads(tool_args)
            except json.JSONDecodeError:
                args = {}

            # 言語チェック対象のコンテンツを抽出
            content = self._extract_content_from_args(tool_name, args)

            if not content:
                return {"status": "skipped", "reason": "No content to check"}

            # 言語ルール強制チェック
            context = self.enforcer.enforce_language_rules(content)

            # 違反がある場合の処理
            if context.violations:
                self._log(f"❌ 言語ルール違反検出: {', '.join(context.violations)}")

                # 修正提案の表示
                if context.corrections:
                    print("\n🔤 言語使用ルール違反が検出されました:")
                    print(f"検出言語: {context.detected_language.value}")
                    print(f"期待言語: {context.expected_language.value}")
                    print(f"処理タイプ: {context.processing_type.value}")
                    print("\n修正提案:")
                    for correction in context.corrections[:3]:  # 最大3つの提案
                        print(f"  - {correction}")
                    print("")

                # 強制ではなく警告として処理（実行は継続）
                return {
                    "status": "warning",
                    "violations": context.violations,
                    "corrections": context.corrections,
                    "detected_language": context.detected_language.value,
                    "expected_language": context.expected_language.value,
                }
            else:
                self._log(f"✅ 言語ルール準拠: {context.processing_type.value}")
                return {
                    "status": "compliant",
                    "detected_language": context.detected_language.value,
                    "processing_type": context.processing_type.value,
                }

        except Exception as e:
            self._log(f"❌ 英語処理強制フック実行エラー: {e}")
            return {"status": "error", "error": str(e)}

    def _extract_content_from_args(self, tool_name: str, args: dict) -> str:
        """ツール引数からコンテンツを抽出"""
        content = ""

        if tool_name in ["Edit", "Write", "MultiEdit"]:
            # ファイル編集系ツール
            if "new_string" in args:
                content += args["new_string"]
            if "content" in args:
                content += args["content"]
            if "edits" in args:
                # MultiEditの場合
                for edit in args["edits"]:
                    if "new_string" in edit:
                        content += edit["new_string"]

        elif tool_name == "Bash":
            # Bashコマンド
            if "command" in args:
                content = args["command"]

        elif tool_name == "Task":
            # Taskの場合
            if "prompt" in args:
                content = args["prompt"]

        elif tool_name in ["Read", "Grep", "Glob"]:
            # 読み込み系ツールの場合、パターンやパスをチェック
            if "pattern" in args:
                content = args["pattern"]
            if "file_path" in args:
                content += args["file_path"]

        return content

    def generate_enforcement_summary(self) -> dict:
        """強制実行サマリーの生成"""
        try:
            report = self.enforcer.generate_enforcement_report()
            return {
                "enforcement_status": report["status"],
                "total_violations": report["total_violations"],
                "compliance_rate": report["compliance_rate"],
                "recommendations": report["recommendations"],
                "summary": report["enforcement_summary"],
            }
        except Exception as e:
            return {"enforcement_status": "error", "error": str(e)}

    def _log(self, message: str):
        """ログ出力"""
        log_entry = f"[{datetime.now().isoformat()}] {message}"
        print(log_entry)

        try:
            with open(self.hook_log_file, "a", encoding="utf-8") as f:
                f.write(log_entry + "\n")
        except Exception:
            pass


def main():
    """メイン実行（フック呼び出し）"""
    hook = EnglishProcessingEnforcementHook()

    # 引数からフックタイプを取得
    hook_type = sys.argv[1] if len(sys.argv) > 1 else "PreToolUse"

    if hook_type == "PreToolUse":
        result = hook.execute_pre_tool_use_hook()

        if result["status"] == "warning":
            print(f"⚠️ 言語使用ルール違反警告: {len(result['violations'])}件")
        elif result["status"] == "compliant":
            print(f"✅ 言語使用ルール準拠: {result['processing_type']}")
        elif result["status"] == "error":
            print(f"❌ 英語処理強制フックエラー: {result['error']}")

    elif hook_type == "Summary":
        # サマリーレポートの生成
        summary = hook.generate_enforcement_summary()
        print("🔤 英語処理強制サマリー:")
        print(f"  ステータス: {summary['enforcement_status']}")
        print(f"  違反数: {summary.get('total_violations', 0)}")
        print(f"  コンプライアンス率: {summary.get('compliance_rate', 1.0):.2f}")
        print(f"  {summary.get('summary', '状況不明')}")

    else:
        print(f"🔤 English Enforcement Hook: {hook_type} event - No action required")


if __name__ == "__main__":
    main()
