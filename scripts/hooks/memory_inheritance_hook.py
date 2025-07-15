#!/usr/bin/env python3
"""
Memory Inheritance Hook - 記憶継承システムとフックの統合
Runtime Advisorを呼び出してミスパターンをリアルタイムで検出
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# プロジェクトルートを設定
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from src.memory.core.runtime_advisor import RuntimeAdvisor  # noqa: E402


class MemoryInheritanceHook:
    def __init__(self):
        self.advisor = RuntimeAdvisor()
        self.hook_log = PROJECT_ROOT / "runtime/ai_api_logs/memory_inheritance_hook.log"

    def analyze_tool_input(self, tool_name: str, tool_args: dict) -> dict:
        """ツール入力を分析してミスパターンを検出"""
        # 入力テキストの抽出
        input_text = ""
        if tool_name in ["Edit", "Write", "MultiEdit"]:
            input_text = tool_args.get("new_string", "") or tool_args.get("content", "")
        elif tool_name == "Bash":
            input_text = tool_args.get("command", "")
        elif tool_name == "Task":
            input_text = tool_args.get("prompt", "")

        # Runtime Advisorで分析
        analysis = self.advisor.analyze_input(input_text, context=f"Tool: {tool_name}")

        # 危険度判定
        is_dangerous = analysis["risk_score"] >= 50

        # 結果をログに記録
        result = {
            "timestamp": datetime.now().isoformat(),
            "tool_name": tool_name,
            "risk_score": analysis["risk_score"],
            "detected_patterns": analysis["detected_patterns"],
            "is_dangerous": is_dangerous,
            "recommendations": analysis["recommendations"],
        }

        self._log_result(result)

        return result

    def _log_result(self, result: dict):
        """結果をログファイルに記録"""
        try:
            self.hook_log.parent.mkdir(parents=True, exist_ok=True)
            with open(self.hook_log, "a", encoding="utf-8") as f:
                f.write(json.dumps(result, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"⚠️ ログ記録失敗: {e}", file=sys.stderr)

    def generate_warning_message(self, result: dict) -> str:
        """警告メッセージの生成"""
        if not result["is_dangerous"]:
            return ""

        msg = ["🚨 記憶継承システム - ミスパターン検出"]
        msg.append(f"リスクスコア: {result['risk_score']}")
        msg.append("")

        for pattern in result["detected_patterns"]:
            msg.append(f"- {pattern['mistake_type']} (重要度: {pattern['severity']})")
            msg.append(f"  防止策: {pattern['prevention']}")

        msg.append("")
        msg.append("推奨アクション:")
        for rec in result["recommendations"]:
            msg.append(f"- {rec}")

        return "\n".join(msg)


def main():
    """フックのメイン処理"""
    # 標準入力からフックデータを読み取り
    try:
        hook_data = json.loads(sys.stdin.read())
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON input: {e}", "allow": True}))
        return

    # ツール情報の取得
    tool_name = hook_data.get("tool_name", "")
    tool_args = hook_data.get("arguments", {})

    # 記憶継承システムで分析
    hook = MemoryInheritanceHook()
    result = hook.analyze_tool_input(tool_name, tool_args)

    # 応答の生成
    response = {
        "allow": not result["is_dangerous"],
        "message": hook.generate_warning_message(result)
        if result["is_dangerous"]
        else "",
    }

    # 危険でない場合でも、推奨事項があれば通知
    if not result["is_dangerous"] and result["recommendations"]:
        response["info"] = f"💡 推奨: {', '.join(result['recommendations'])}"

    print(json.dumps(response, ensure_ascii=False))


if __name__ == "__main__":
    main()
