#!/usr/bin/env python3
"""
🔧 Auto Corrector - 自動軌道修正システム
=====================================
失敗を検出して自動的に修正案を生成し、実行を継続する
「止める」ではなく「修正して続行」する現実的なメカニズム
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


class CorrectionStrategy:
    """修正戦略の基底クラス"""

    def can_handle(self, error_context: Dict[str, Any]) -> bool:
        raise NotImplementedError

    def generate_correction(self, error_context: Dict[str, Any]) -> Optional[str]:
        raise NotImplementedError


class GeminiCLIStrategy(CorrectionStrategy):
    """Gemini CLI対話エラーの修正戦略"""

    def can_handle(self, error_context: Dict[str, Any]) -> bool:
        command = error_context.get("command", "")
        stderr = error_context.get("stderr", "")

        return "gemini" in command.lower() and (
            "unknown" in stderr.lower() or "error" in stderr.lower()
        )

    def generate_correction(self, error_context: Dict[str, Any]) -> Optional[str]:
        command = error_context["command"]
        stderr = error_context["stderr"]

        # 一般的なGeminiコマンドエラーパターンを修正
        if "unknown" in stderr.lower() and not command.startswith("gemini -p"):
            # gemini "text" -> gemini -p "text" に修正
            if command.startswith("gemini ") and '"' in command:
                text = command[7:].strip()
                return f"gemini -p {text}"

        if "api key" in stderr.lower():
            return "echo '⚠️ Gemini API Key未設定 - 環境変数GEMINI_API_KEYを設定してください'"

        return None


class MCPIntegrationStrategy(CorrectionStrategy):
    """MCP統合エラーの修正戦略"""

    def can_handle(self, error_context: Dict[str, Any]) -> bool:
        command = error_context.get("command", "")
        return "mcp" in command.lower()

    def generate_correction(self, error_context: Dict[str, Any]) -> Optional[str]:
        stderr = error_context["stderr"]

        if "not found" in stderr.lower():
            return "echo '⚠️ MCPコマンドが見つかりません - インストールが必要です'"

        return None


class FileOperationStrategy(CorrectionStrategy):
    """ファイル操作エラーの修正戦略"""

    def can_handle(self, error_context: Dict[str, Any]) -> bool:
        stderr = error_context.get("stderr", "")
        return any(
            keyword in stderr.lower()
            for keyword in ["no such file", "permission denied", "directory not empty"]
        )

    def generate_correction(self, error_context: Dict[str, Any]) -> Optional[str]:
        command = error_context["command"]
        stderr = error_context["stderr"]

        if "no such file" in stderr.lower():
            # ファイルが存在しない場合、親ディレクトリを作成を提案
            if "mkdir" not in command:
                return f"mkdir -p $(dirname {command.split()[-1]}) && {command}"

        if "permission denied" in stderr.lower():
            # 権限エラーの場合、chmod/sudoを提案
            if "chmod" not in command and "sudo" not in command:
                return f"chmod +x {command.split()[-1]} && {command}"

        return None


class CorrectionHandler:
    """修正処理のメインハンドラー"""

    def __init__(self, max_retries: int = 3, log_file: Optional[Path] = None):
        self.max_retries = max_retries
        self.log_file = log_file or Path("runtime/logs/correction.log")

        # 修正戦略を登録
        self.strategies = [
            GeminiCLIStrategy(),
            MCPIntegrationStrategy(),
            FileOperationStrategy(),
        ]

        # ログディレクトリ確保
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def analyze_and_correct(
        self, command: str, stderr: str, stdout: str, exit_code: int, attempt: int
    ) -> Optional[str]:
        """エラーを分析して修正コマンドを生成"""

        if attempt >= self.max_retries:
            self._log_correction(
                {
                    "status": "max_retries_reached",
                    "command": command,
                    "attempt": attempt,
                    "stderr": stderr[:200],
                }
            )
            return None

        error_context = {
            "command": command,
            "stderr": stderr,
            "stdout": stdout,
            "exit_code": exit_code,
            "attempt": attempt,
        }

        # 各戦略を試行
        for strategy in self.strategies:
            if strategy.can_handle(error_context):
                correction = strategy.generate_correction(error_context)
                if correction:
                    self._log_correction(
                        {
                            "status": "correction_generated",
                            "strategy": strategy.__class__.__name__,
                            "original_command": command,
                            "corrected_command": correction,
                            "attempt": attempt,
                            "error": stderr[:200],
                        }
                    )
                    return correction

        # 修正不可能
        self._log_correction(
            {
                "status": "no_correction_available",
                "command": command,
                "attempt": attempt,
                "stderr": stderr[:200],
            }
        )
        return None

    def execute_with_correction(self, command: str) -> Tuple[bool, str, str]:
        """修正ループ付きでコマンドを実行"""

        attempt = 0
        current_command = command

        while attempt < self.max_retries:
            try:
                result = subprocess.run(
                    current_command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=120,
                )

                if result.returncode == 0:
                    self._log_correction(
                        {
                            "status": "success",
                            "command": current_command,
                            "attempt": attempt,
                            "stdout": result.stdout[:200],
                        }
                    )
                    return True, result.stdout, ""

                # エラーの場合、修正を試行
                attempt += 1
                corrected_command = self.analyze_and_correct(
                    current_command,
                    result.stderr,
                    result.stdout,
                    result.returncode,
                    attempt,
                )

                if corrected_command:
                    print(f"🔧 コマンド修正 (試行{attempt}): {corrected_command}")
                    current_command = corrected_command
                else:
                    return False, "", result.stderr

            except subprocess.TimeoutExpired:
                self._log_correction(
                    {
                        "status": "timeout",
                        "command": current_command,
                        "attempt": attempt,
                    }
                )
                return False, "", "Command timeout"
            except Exception as e:
                self._log_correction(
                    {
                        "status": "exception",
                        "command": current_command,
                        "attempt": attempt,
                        "error": str(e),
                    }
                )
                return False, "", str(e)

        return False, "", f"Failed after {self.max_retries} attempts"

    def _log_correction(self, log_entry: Dict[str, Any]):
        """修正ログを記録"""
        log_entry["timestamp"] = datetime.now().isoformat()

        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"⚠️ 修正ログ記録エラー: {e}")


def main():
    """テスト実行"""
    corrector = CorrectionHandler()

    # テストケース
    test_commands = [
        'gemini "テストメッセージ"',  # 構文エラーテスト
        "ls /nonexistent/path",  # ファイル不存在テスト
        'echo "修正システムテスト完了"',  # 正常実行テスト
    ]

    for cmd in test_commands:
        print(f"\n🧪 テスト: {cmd}")
        success, stdout, stderr = corrector.execute_with_correction(cmd)
        print(f"結果: {'✅ 成功' if success else '❌ 失敗'}")
        if stdout:
            print(f"出力: {stdout.strip()}")
        if stderr:
            print(f"エラー: {stderr.strip()}")


if __name__ == "__main__":
    main()
