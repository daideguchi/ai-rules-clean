#!/usr/bin/env python3
"""
AI API Interceptor Hook
AI API実行を自動検出し、事前チェックを強制実行
"""

import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# プロジェクトルート設定
PROJECT_ROOT = Path(__file__).parent.parent.parent
LOG_DIR = PROJECT_ROOT / "runtime" / "ai_api_logs"


class AIAPIInterceptor:
    def __init__(self):
        self.dangerous_patterns = [
            r"npx.*gemini-cli.*-c",  # 間違ったconfig指定
            r"gemini-2\.0-flash-latest",  # 存在しないモデル
            r"gemini.*--model-file",  # 存在しないオプション
            r"claude.*--api-key.*[^=]",  # APIキー直接指定
        ]

        self.api_patterns = [
            r"npx.*gemini-cli",
            r"mcp__o3__o3-search",
            r"claude.*api",
        ]

    def detect_ai_api_command(self, command):
        """AI API使用コマンドを検出"""
        for pattern in self.api_patterns:
            if re.search(pattern, command):
                return True
        return False

    def detect_dangerous_pattern(self, command):
        """危険なパターンを検出"""
        dangerous = []
        for pattern in self.dangerous_patterns:
            if re.search(pattern, command):
                dangerous.append(pattern)
        return dangerous

    def run_pre_check(self):
        """事前チェックスクリプト実行"""
        check_script = PROJECT_ROOT / "scripts" / "utilities" / "ai-api-check.sh"

        if not check_script.exists():
            print("❌ AI APIチェックスクリプトが見つかりません")
            return False

        try:
            result = subprocess.run(
                [str(check_script)], capture_output=True, text=True, timeout=60
            )
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            print("❌ チェックタイムアウト")
            return False
        except Exception as e:
            print(f"❌ チェック実行エラー: {e}")
            return False

    def log_attempt(self, command, result):
        """API使用試行をログ記録"""
        LOG_DIR.mkdir(parents=True, exist_ok=True)

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "command": command,
            "result": result,
            "dangerous_patterns": self.detect_dangerous_pattern(command),
        }

        log_file = LOG_DIR / "api_usage.jsonl"
        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

    def intercept(self, command):
        """メインインターセプト処理"""
        print(f"🔍 AI APIコマンド検出: {command[:50]}...")

        # 危険パターンチェック
        dangerous = self.detect_dangerous_pattern(command)
        if dangerous:
            print("🚨 危険なパターンを検出:")
            for pattern in dangerous:
                print(f"   - {pattern}")

            # 過去の失敗例を表示
            self.show_historical_failures(dangerous)

            choice = input("このまま実行しますか？ [y/N]: ").lower()
            if choice != "y":
                print("❌ 実行をキャンセルしました")
                self.log_attempt(command, "BLOCKED_DANGEROUS")
                return False

        # 事前チェック実行
        print("📋 事前チェックを実行中...")
        if not self.run_pre_check():
            print("❌ 事前チェックに失敗しました")
            self.log_attempt(command, "BLOCKED_PRECHECK")
            return False

        print("✅ 事前チェック完了")
        self.log_attempt(command, "APPROVED")
        return True

    def show_historical_failures(self, patterns):
        """過去の失敗例を表示"""
        tracker_file = LOG_DIR / "mistake_prevention_tracker.md"
        if tracker_file.exists():
            print("\n📚 過去の類似失敗:")
            with open(tracker_file) as f:
                content = f.read()
                if "CLI引数" in content:
                    print("   - 2025-07-07: CLI引数誤用")
                if "モデル名" in content:
                    print("   - 2025-07-07: 存在しないモデル名")
            print()


def main():
    if len(sys.argv) < 2:
        print("使用法: ai_api_interceptor.py <command>")
        sys.exit(1)

    command = " ".join(sys.argv[1:])
    interceptor = AIAPIInterceptor()

    # AI APIコマンドかチェック
    if not interceptor.detect_ai_api_command(command):
        # AI APIではない場合はそのまま実行
        sys.exit(0)

    # インターセプト実行
    if interceptor.intercept(command):
        print("🎯 安全にAPI実行してください")
        sys.exit(0)
    else:
        print("🛑 API実行がブロックされました")
        sys.exit(1)


if __name__ == "__main__":
    main()
