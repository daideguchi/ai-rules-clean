#!/usr/bin/env python3
"""
🎼 Conductor Core - 指揮者システム中核
=====================================
自動軌道修正機能を持つ指揮者システムのメイン実装
「止める」ではなく「修正して続行」する現実的なアプローチ
"""

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .corrector import CorrectionHandler


@dataclass
class Task:
    """実行タスクの定義"""

    id: str
    command: str
    description: str
    priority: str = "normal"
    max_retries: int = 3
    timeout: int = 120
    required_outputs: List[str] = None


@dataclass
class TaskResult:
    """タスク実行結果"""

    task_id: str
    success: bool
    stdout: str
    stderr: str
    attempts: int
    corrections_applied: List[str]
    execution_time: float
    timestamp: str


class ConductorCore:
    """指揮者システムの中核実装"""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path.cwd()
        self.correction_handler = CorrectionHandler(max_retries=3)
        self.task_queue: List[Task] = []
        self.completed_tasks: List[TaskResult] = []
        self.log_file = self.project_root / "runtime" / "logs" / "conductor.log"

        # ログディレクトリ確保
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def add_task(self, task: Task):
        """タスクをキューに追加"""
        self.task_queue.append(task)
        self._log(f"Task added: {task.id} - {task.description}")

    def execute_task(self, task: Task) -> TaskResult:
        """単一タスクの実行（自動修正付き）"""
        start_time = datetime.now()
        self._log(f"Executing task: {task.id}")

        # Correctorを使用して修正付き実行
        success, stdout, stderr = self.correction_handler.execute_with_correction(
            task.command
        )

        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()

        # 修正ログから適用された修正を取得
        corrections_applied = self._get_applied_corrections(task.id)

        result = TaskResult(
            task_id=task.id,
            success=success,
            stdout=stdout,
            stderr=stderr,
            attempts=len(corrections_applied) + 1,
            corrections_applied=corrections_applied,
            execution_time=execution_time,
            timestamp=end_time.isoformat(),
        )

        self.completed_tasks.append(result)
        self._log(f"Task completed: {task.id} - {'SUCCESS' if success else 'FAILED'}")

        return result

    def execute_queue(self) -> List[TaskResult]:
        """キュー内の全タスクを実行"""
        results = []

        while self.task_queue:
            task = self.task_queue.pop(0)
            result = self.execute_task(task)
            results.append(result)

            # 失敗した重要タスクの処理
            if not result.success and task.priority == "critical":
                self._log(f"CRITICAL task failed: {task.id}")
                self._handle_critical_failure(task, result)

        return results

    def create_mcp_gemini_task(
        self, message: str, task_id: Optional[str] = None
    ) -> Task:
        """MCP Gemini CLI対話タスクを作成"""
        task_id = task_id or f"gemini_{datetime.now().strftime('%H%M%S')}"

        return Task(
            id=task_id,
            command=f'gemini -p "{message}"',
            description=f"Gemini CLI対話: {message[:50]}...",
            priority="mandatory",
            max_retries=3,
        )

    def execute_mcp_gemini(self, message: str) -> TaskResult:
        """MCP Gemini CLI対話の直接実行"""
        task = self.create_mcp_gemini_task(message)
        return self.execute_task(task)

    def validate_instruction_compliance(
        self, instruction: str, executed_tasks: List[TaskResult]
    ) -> Dict[str, Any]:
        """指示遵守の検証"""
        compliance_check = {
            "instruction": instruction,
            "timestamp": datetime.now().isoformat(),
            "tasks_executed": len(executed_tasks),
            "success_rate": sum(1 for t in executed_tasks if t.success)
            / len(executed_tasks)
            if executed_tasks
            else 0,
            "violations": [],
            "compliance_score": 0.0,
        }

        # MCP CLI指示の検証
        if "gemini" in instruction.lower() and "cli" in instruction.lower():
            gemini_tasks = [t for t in executed_tasks if "gemini" in t.task_id]
            if not gemini_tasks:
                compliance_check["violations"].append(
                    "MCP Gemini CLI指示が実行されていません"
                )
            elif not any(t.success for t in gemini_tasks):
                compliance_check["violations"].append(
                    "Gemini CLI対話が全て失敗しています"
                )

        # 指揮者概念の言及チェック
        if "指揮者" in instruction or "conductor" in instruction.lower():
            if not any("conductor" in t.stdout.lower() for t in executed_tasks):
                compliance_check["violations"].append(
                    "指揮者概念への言及が不足しています"
                )

        # コンプライアンススコア計算
        violation_penalty = len(compliance_check["violations"]) * 0.2
        compliance_check["compliance_score"] = max(
            0.0, compliance_check["success_rate"] - violation_penalty
        )

        return compliance_check

    def generate_execution_report(self, results: List[TaskResult]) -> str:
        """実行レポートの生成（虚偽報告防止）"""
        if not results:
            return "⚠️ 実行されたタスクがありません"

        report = ["# 指揮者システム実行レポート", ""]
        report.append(f"実行時刻: {datetime.now().isoformat()}")
        report.append(f"総タスク数: {len(results)}")

        success_count = sum(1 for r in results if r.success)
        report.append(f"成功: {success_count}, 失敗: {len(results) - success_count}")
        report.append("")

        # 詳細結果
        report.append("## 詳細結果")
        for result in results:
            status = "✅" if result.success else "❌"
            report.append(f"{status} {result.task_id}: {result.attempts}回試行")

            if result.corrections_applied:
                report.append(f"   修正適用: {', '.join(result.corrections_applied)}")

            if result.success and result.stdout:
                report.append(f"   出力: {result.stdout[:100]}...")
            elif not result.success:
                report.append(f"   エラー: {result.stderr[:100]}...")

        report.append("")
        report.append("## 実行証跡")
        report.append(f"ログファイル: {self.log_file}")
        report.append(f"修正ログ: {self.correction_handler.log_file}")

        return "\n".join(report)

    def _get_applied_corrections(self, task_id: str) -> List[str]:
        """適用された修正の一覧を取得"""
        corrections = []
        try:
            if self.correction_handler.log_file.exists():
                with open(self.correction_handler.log_file) as f:
                    for line in f:
                        log_entry = json.loads(line)
                        if log_entry.get(
                            "status"
                        ) == "correction_generated" and task_id in log_entry.get(
                            "original_command", ""
                        ):
                            corrections.append(log_entry.get("strategy", "unknown"))
        except Exception:
            pass
        return corrections

    def _handle_critical_failure(self, task: Task, result: TaskResult):
        """重要タスク失敗時の処理"""
        self._log(f"CRITICAL FAILURE - Task: {task.id}, Error: {result.stderr}")

        # 重要な失敗は即座にレポート
        failure_report = {
            "type": "critical_failure",
            "task_id": task.id,
            "command": task.command,
            "error": result.stderr,
            "attempts": result.attempts,
            "timestamp": result.timestamp,
        }

        # 失敗レポートをファイルに保存
        failure_file = (
            self.project_root / "runtime" / "logs" / f"critical_failure_{task.id}.json"
        )
        with open(failure_file, "w") as f:
            json.dump(failure_report, f, indent=2)

    def _log(self, message: str):
        """ログ出力"""
        log_entry = f"[{datetime.now().isoformat()}] {message}"
        print(log_entry)

        try:
            with open(self.log_file, "a") as f:
                f.write(log_entry + "\n")
        except Exception:
            pass


def main():
    """テスト実行"""
    conductor = ConductorCore()

    # テストタスク作成
    test_tasks = [
        Task(
            id="test_gemini",
            command='gemini -p "指揮者システムのテストメッセージです"',
            description="Gemini CLI対話テスト",
            priority="mandatory",
        ),
        Task(
            id="test_ls",
            command="ls -la /Users/dd/Desktop/1_dev/coding-rule2/src/conductor/",
            description="指揮者ディレクトリ確認",
            priority="normal",
        ),
    ]

    # タスク実行
    for task in test_tasks:
        conductor.add_task(task)

    results = conductor.execute_queue()

    # レポート生成
    report = conductor.generate_execution_report(results)
    print("\n" + "=" * 60)
    print(report)


if __name__ == "__main__":
    main()
