#!/usr/bin/env python3
"""
[LEGACY WRAPPER] タスク検証システム

このスクリプトは unified-validation-tool.py に統合されました。
Phase 6 統合完了 - レガシー互換性のためのwrapperスクリプト

新しい使用方法:
  scripts/tools/unified-validation-tool.py task-verify "<task>" [--context "<context>"]
"""

import os
import sys
from pathlib import Path

print("⚠️  [LEGACY] task-verification-system.py は統合されました")
print("📦 unified-validation-tool.py task-verify に移行してください")
print("")
print("🔄 自動転送中...")

# 統合ツールの実行
script_dir = Path(__file__).parent
unified_tool = script_dir.parent / "unified-validation-tool.py"

# 引数変換
if len(sys.argv) < 2:
    args = ["task-verify", "デフォルトタスク"]
else:
    args = ["task-verify", sys.argv[1]]
    if len(sys.argv) > 2:
        args.extend(["--context", sys.argv[2]])

os.execv(sys.executable, [sys.executable, str(unified_tool)] + args)

import json
import os
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
VERIFICATION_LOG = PROJECT_ROOT / "runtime" / "ai_api_logs" / "task_verification.log"

class TaskVerificationSystem:
    def __init__(self):
        self.verification_failed = False
        self.critical_keywords = [
            "スペルチェック", "リンター", "エラー修正", "spell", "lint", "error",
            "修正", "改善", "fix", "correct", "resolve"
        ]

    def verify_task_understanding(self, task_description, user_context=""):
        """タスク理解の検証"""
        print("🔍 タスク検証システム起動")
        print("=" * 40)

        # 1. 重要キーワード検出
        detected_keywords = []
        for keyword in self.critical_keywords:
            if keyword in task_description.lower() or keyword in user_context.lower():
                detected_keywords.append(keyword)

        if detected_keywords:
            print(f"⚠️  重要キーワード検出: {', '.join(detected_keywords)}")
            print("以下を確認してください：")

            # 2. 具体的な確認項目
            if any(k in detected_keywords for k in ["スペルチェック", "spell"]):
                print("□ スペルチェックエラーの具体的なリストを確認しましたか？")
                print("□ 修正対象のファイルパスを特定しましたか？")
                print("□ エラーの種類（タイポ、辞書追加、設定変更）を判別しましたか？")

            if any(k in detected_keywords for k in ["リンター", "lint"]):
                print("□ リンターの種類（Python、JS、spell等）を特定しましたか？")
                print("□ エラー出力の実際の内容を確認しましたか？")

            if any(k in detected_keywords for k in ["エラー修正", "error", "fix"]):
                print("□ エラーの根本原因を特定しましたか？")
                print("□ 修正すべき具体的な箇所を明確にしましたか？")

            # 3. 強制確認
            try:
                response = input("\n上記すべてを確認しましたか？ (yes/no): ").strip().lower()
                if response != 'yes':
                    print("❌ タスク検証失敗 - 作業を中止してください")
                    self.verification_failed = True
                    return False
            except EOFError:
                print("⚠️  非対話環境 - 自動検証モード")

        # 4. ログ記録
        self._log_verification(task_description, detected_keywords, user_context)

        print("✅ タスク検証完了")
        return True

    def _log_verification(self, task_description, keywords, context):
        """検証ログの記録"""
        try:
            VERIFICATION_LOG.parent.mkdir(parents=True, exist_ok=True)

            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "task_description": task_description,
                "detected_keywords": keywords,
                "user_context": context,
                "verification_status": "passed" if not self.verification_failed else "failed"
            }

            with open(VERIFICATION_LOG, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')

        except Exception as e:
            print(f"⚠️  検証ログ記録失敗: {e}")

def main():
    """メイン処理"""
    if len(sys.argv) < 2:
        print("使用法: python3 task-verification-system.py 'タスク説明' ['ユーザーコンテキスト']")
        return False

    task_description = sys.argv[1]
    user_context = sys.argv[2] if len(sys.argv) > 2 else ""

    verifier = TaskVerificationSystem()
    return verifier.verify_task_understanding(task_description, user_context)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
